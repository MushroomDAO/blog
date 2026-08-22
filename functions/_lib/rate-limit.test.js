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
