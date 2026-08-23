// T1.3.6 验收测试：限速计数器逻辑。用一个内存 Map 模拟 KV binding 的 get/put 接口
// （真实 KV 是最终一致的分布式存储，这里只测计数逻辑本身，不测 KV 的一致性行为）。

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { checkAndIncrement, MAX_ATTEMPTS } from './rate-limit.js';

function makeFakeKv() {
	const store = new Map();
	return {
		async get(key) {
			return store.has(key) ? store.get(key) : null;
		},
		async put(key, value) {
			store.set(key, value);
		},
	};
}

test('checkAndIncrement: 前 MAX_ATTEMPTS 次都允许', async () => {
	const kv = makeFakeKv();
	for (let i = 0; i < MAX_ATTEMPTS; i++) {
		const { allowed } = await checkAndIncrement(kv, '1.2.3.4');
		assert.equal(allowed, true, `第 ${i + 1} 次应该允许`);
	}
});

test('checkAndIncrement: 超过 MAX_ATTEMPTS 次之后拒绝', async () => {
	const kv = makeFakeKv();
	for (let i = 0; i < MAX_ATTEMPTS; i++) {
		await checkAndIncrement(kv, '1.2.3.4');
	}
	const { allowed, remaining } = await checkAndIncrement(kv, '1.2.3.4');
	assert.equal(allowed, false);
	assert.equal(remaining, 0);
});

test('checkAndIncrement: 不同 IP 互不影响', async () => {
	const kv = makeFakeKv();
	for (let i = 0; i < MAX_ATTEMPTS; i++) {
		await checkAndIncrement(kv, '1.1.1.1');
	}
	const blocked = await checkAndIncrement(kv, '1.1.1.1');
	assert.equal(blocked.allowed, false);

	const otherIp = await checkAndIncrement(kv, '2.2.2.2');
	assert.equal(otherIp.allowed, true, '另一个 IP 不应该被前一个 IP 的计数影响');
});

test('checkAndIncrement: remaining 计数正确递减', async () => {
	const kv = makeFakeKv();
	const first = await checkAndIncrement(kv, '9.9.9.9');
	assert.equal(first.remaining, MAX_ATTEMPTS - 1);
	const second = await checkAndIncrement(kv, '9.9.9.9');
	assert.equal(second.remaining, MAX_ATTEMPTS - 2);
});

// T1.3.3 新增：/api/search 复用这个计数器，但要一套不同的前缀/窗口/次数配置
test('checkAndIncrement: 自定义 prefix/windowSeconds/maxAttempts 生效', async () => {
	const kv = makeFakeKv();
	const opts = { prefix: 'searchlimit:', windowSeconds: 60, maxAttempts: 2 };
	const first = await checkAndIncrement(kv, '5.5.5.5', opts);
	assert.equal(first.allowed, true);
	assert.equal(first.remaining, 1);
	const second = await checkAndIncrement(kv, '5.5.5.5', opts);
	assert.equal(second.allowed, true);
	assert.equal(second.remaining, 0);
	const third = await checkAndIncrement(kv, '5.5.5.5', opts);
	assert.equal(third.allowed, false);
});

test('checkAndIncrement: 不同 prefix 即使同一个 id 也不共享计数（登录限速跟搜索限速互不影响）', async () => {
	const kv = makeFakeKv();
	for (let i = 0; i < MAX_ATTEMPTS; i++) {
		await checkAndIncrement(kv, '3.3.3.3'); // 默认 prefix "ratelimit:"，登录场景
	}
	const loginBlocked = await checkAndIncrement(kv, '3.3.3.3');
	assert.equal(loginBlocked.allowed, false);

	const searchStillAllowed = await checkAndIncrement(kv, '3.3.3.3', { prefix: 'searchlimit:' });
	assert.equal(searchStillAllowed.allowed, true, '同一个 IP 登录限速用满，不应该影响它的搜索限速额度');
});

// 回归测试（FU-19）：KV get/put 抛异常时 fail-closed，不裸抛异常传染给调用方
test('checkAndIncrement: kv.get() 抛异常时 fail-closed 返回 { allowed: false }，不裸抛异常', async () => {
	const brokenKv = {
		async get() {
			throw new Error('KV quota exceeded');
		},
		async put() {},
	};
	const result = await checkAndIncrement(brokenKv, '4.4.4.4');
	assert.equal(result.allowed, false);
	assert.equal(result.remaining, 0);
});

test('checkAndIncrement: kv.put() 抛异常时同样 fail-closed', async () => {
	const brokenKv = {
		async get() {
			return null;
		},
		async put() {
			throw new Error('KV write failed');
		},
	};
	const result = await checkAndIncrement(brokenKv, '6.6.6.6');
	assert.equal(result.allowed, false);
	assert.equal(result.remaining, 0);
});

// 回归测试（round 2 review 用 M6 威胁模型实测证实的真实 bug）：原来 key 不带时间桶，
// 每次成功请求都把 TTL 重设成整窗口长度，只要请求间隔小于窗口长度，计数就永远不会真正
// 归零——一个持续、低速的正常用户反而更容易撞上限速。改成 key 带固定时间桶后，跨桶边界
// 应该拿到一个全新的、独立的计数额度，不管前一个桶里用掉了多少。
test('checkAndIncrement: 跨时间桶边界后计数独立重置，不因为持续活跃就被无限期顺延', async () => {
	const kv = makeFakeKv();
	const opts = { prefix: 'searchlimit:', windowSeconds: 300, maxAttempts: 2 };
	const realNow = Date.now;
	try {
		// 桶 0：用满这个桶的额度
		Date.now = () => 0;
		const a1 = await checkAndIncrement(kv, '7.7.7.7', opts);
		assert.equal(a1.allowed, true);
		const a2 = await checkAndIncrement(kv, '7.7.7.7', opts);
		assert.equal(a2.allowed, true);
		const a3 = await checkAndIncrement(kv, '7.7.7.7', opts);
		assert.equal(a3.allowed, false, '同一个桶内第 3 次应该被挡住');

		// 跨到下一个桶（300 秒之后）：不应该继续沿用桶 0 已经用满的计数
		Date.now = () => 300_000; // 300 秒 = 300000 毫秒，跨过一个 300 秒窗口
		const b1 = await checkAndIncrement(kv, '7.7.7.7', opts);
		assert.equal(b1.allowed, true, '跨桶之后应该拿到全新的额度，不应该因为上一桶用满了就继续被挡');
	} finally {
		Date.now = realNow;
	}
});
