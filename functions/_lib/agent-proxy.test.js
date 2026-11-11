import assert from 'node:assert/strict';
import { test } from 'node:test';
import { handleAgentProxy } from './agent-proxy.js';

test('agent-proxy: redirects /agent without trailing slash to /agent/', async () => {
	const req = new Request('https://blog.mushroom.cv/agent');
	const res = await handleAgentProxy({ request: req });
	assert.equal(res.status, 301);
	assert.equal(res.headers.get('location'), '/agent/');
});

test('agent-proxy: preserves search parameters on trailing slash redirect', async () => {
	const req = new Request('https://blog.mushroom.cv/agent?day=2026-11-11');
	const res = await handleAgentProxy({ request: req });
	assert.equal(res.status, 301);
	assert.equal(res.headers.get('location'), '/agent/?day=2026-11-11');
});

test('agent-proxy: rewrites relative redirect location from upstream', async () => {
	const originalFetch = globalThis.fetch;
	try {
		globalThis.fetch = async (url) => {
			assert.equal(url, 'https://agent-research-bot.pages.dev/days/2026-11-11');
			return new Response(null, {
				status: 308,
				headers: {
					location: '/days/2026-11-11/',
				},
			});
		};

		const req = new Request('https://blog.mushroom.cv/agent/days/2026-11-11');
		const res = await handleAgentProxy({ request: req });
		assert.equal(res.status, 308);
		assert.equal(res.headers.get('location'), '/agent/days/2026-11-11/');
	} finally {
		globalThis.fetch = originalFetch;
	}
});

test('agent-proxy: rewrites absolute redirect location pointing to target origin', async () => {
	const originalFetch = globalThis.fetch;
	try {
		globalThis.fetch = async () => {
			return new Response(null, {
				status: 302,
				headers: {
					location: 'https://agent-research-bot.pages.dev/archive/',
				},
			});
		};

		const req = new Request('https://blog.mushroom.cv/agent/archive');
		const res = await handleAgentProxy({ request: req });
		assert.equal(res.status, 302);
		assert.equal(res.headers.get('location'), '/agent/archive/');
	} finally {
		globalThis.fetch = originalFetch;
	}
});

test('agent-proxy: live proxy test against target domain', async () => {
	const req = new Request('https://blog.mushroom.cv/agent/');
	const res = await handleAgentProxy({ request: req });
	assert.equal(res.status, 200);
	const text = await res.text();
	assert.match(text, /Agent 开发日报/);
});
