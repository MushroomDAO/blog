import assert from 'node:assert/strict';
import { test } from 'node:test';
import { onRequestGet } from './geo.js';

function makeContext(cf) {
	return { request: { cf } };
}

test('geo: returns the country Cloudflare resolved', async () => {
	const res = await onRequestGet(makeContext({ country: 'CN' }));
	assert.equal(res.status, 200);
	const body = await res.json();
	assert.deepEqual(body, { country: 'CN' });
});

test('geo: falls back to null when cf is absent (local dev)', async () => {
	const res = await onRequestGet(makeContext(undefined));
	const body = await res.json();
	assert.deepEqual(body, { country: null });
});

test('geo: falls back to null when cf.country is absent', async () => {
	const res = await onRequestGet(makeContext({}));
	const body = await res.json();
	assert.deepEqual(body, { country: null });
});

test('geo: response is never cacheable (per-visitor data)', async () => {
	const res = await onRequestGet(makeContext({ country: 'US' }));
	assert.equal(res.headers.get('cache-control'), 'private, no-store');
});
