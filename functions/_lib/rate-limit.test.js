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
