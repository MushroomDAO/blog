import assert from 'node:assert/strict';
import { test } from 'node:test';
import { handleEthereumProxy } from './ethereum-proxy.js';

test('ethereum-proxy: redirects /ethereum without trailing slash to /ethereum/', async () => {
	const req = new Request('https://blog.mushroom.cv/ethereum');
	const res = await handleEthereumProxy({ request: req });
	assert.equal(res.status, 301);
	assert.equal(res.headers.get('location'), '/ethereum/');
});

test('ethereum-proxy: preserves search parameters on trailing slash redirect', async () => {
	const req = new Request('https://blog.mushroom.cv/ethereum?day=2026-11-11');
	const res = await handleEthereumProxy({ request: req });
	assert.equal(res.status, 301);
	assert.equal(res.headers.get('location'), '/ethereum/?day=2026-11-11');
});

test('ethereum-proxy: rewrites relative redirect location from upstream', async () => {
	const originalFetch = globalThis.fetch;
	try {
		globalThis.fetch = async (url) => {
			assert.equal(url, 'https://ethereum-research-bot.pages.dev/days/2026-11-11');
			return new Response(null, {
				status: 301,
				headers: {
					location: '/days/2026-11-11/',
				},
			});
		};

		const req = new Request('https://blog.mushroom.cv/ethereum/days/2026-11-11');
		const res = await handleEthereumProxy({ request: req });
		assert.equal(res.status, 301);
		assert.equal(res.headers.get('location'), '/ethereum/days/2026-11-11/');
	} finally {
		globalThis.fetch = originalFetch;
	}
});

test('ethereum-proxy: rewrites absolute redirect location pointing to target origin', async () => {
	const originalFetch = globalThis.fetch;
	try {
		globalThis.fetch = async () => {
			return new Response(null, {
				status: 302,
				headers: {
					location: 'https://ethereum-research-bot.pages.dev/days/2026-11-11/',
				},
			});
		};

		const req = new Request('https://blog.mushroom.cv/ethereum/days/2026-11-11');
		const res = await handleEthereumProxy({ request: req });
		assert.equal(res.status, 302);
		assert.equal(res.headers.get('location'), '/ethereum/days/2026-11-11/');
	} finally {
		globalThis.fetch = originalFetch;
	}
});

test('ethereum-proxy: preserves third-party redirects untouched', async () => {
	const originalFetch = globalThis.fetch;
	try {
		globalThis.fetch = async () => {
			return new Response(null, {
				status: 302,
				headers: {
					location: 'https://example.com/other',
				},
			});
		};

		const req = new Request('https://blog.mushroom.cv/ethereum/external');
		const res = await handleEthereumProxy({ request: req });
		assert.equal(res.status, 302);
		assert.equal(res.headers.get('location'), 'https://example.com/other');
	} finally {
		globalThis.fetch = originalFetch;
	}
});

test('ethereum-proxy: returns 502 on upstream fetch failure', async () => {
	const originalFetch = globalThis.fetch;
	try {
		globalThis.fetch = async () => {
			throw new Error('Connection refused');
		};

		const req = new Request('https://blog.mushroom.cv/ethereum/');
		const res = await handleEthereumProxy({ request: req });
		assert.equal(res.status, 502);
		const text = await res.text();
		assert.match(text, /Bad Gateway/);
	} finally {
		globalThis.fetch = originalFetch;
	}
});

test('ethereum-proxy: live proxy test against target domain', async () => {
	const req = new Request('https://blog.mushroom.cv/ethereum/');
	const res = await handleEthereumProxy({ request: req });
	assert.equal(res.status, 200);
	const text = await res.text();
	assert.match(text, /以太坊研究日报/);
});
