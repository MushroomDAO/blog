import assert from 'node:assert/strict';
import test from 'node:test';
import { compareRecentPosts, postActivityDate } from './post-activity.ts';

test('an updated October 5 article enters the latest eight without changing its publication date', () => {
	const splash = { id: 'splash', data: { pubDate: new Date('2026-10-05'), updatedDate: new Date('2026-10-22') } };
	const previous = Array.from({ length: 8 }, (_, i) => ({
		id: `previous-${i}`, data: { pubDate: new Date('2026-10-21') },
	}));
	assert.equal([...previous, splash].sort(compareRecentPosts).slice(0, 8)[0].id, 'splash');
	assert.equal(splash.data.pubDate.toISOString(), '2026-10-05T00:00:00.000Z');
});

test('same-day publication times take precedence over alphabetical input order', () => {
	const earlier = { id: 'a-earlier', data: { pubDate: new Date('2026-10-22'), lastPublishedAt: new Date('2026-10-22T10:00:00Z') } };
	const later = { id: 'z-later', data: { pubDate: new Date('2026-10-22'), lastPublishedAt: new Date('2026-10-22T15:00:00Z') } };
	assert.deepEqual([earlier, later].sort(compareRecentPosts).map(post => post.id), ['z-later', 'a-earlier']);
});

test('legacy posts use dates and a stable tie break, rather than filesystem order', () => {
	const a = { id: 'a', data: { pubDate: new Date('2026-10-22') } };
	const b = { id: 'b', data: { pubDate: new Date('2026-10-22') } };
	assert.equal(postActivityDate(a.data).toISOString(), '2026-10-22T00:00:00.000Z');
	assert.deepEqual([b, a].sort(compareRecentPosts).map(post => post.id), ['a', 'b']);
});

test('same local-day publications retain time order when their UTC timestamps fall on the previous day', () => {
	const earlier = { id: 'a-earlier', data: { pubDate: new Date('2026-10-22'), lastPublishedAt: new Date('2026-10-21T18:00:00Z') } };
	const later = { id: 'z-later', data: { pubDate: new Date('2026-10-22'), lastPublishedAt: new Date('2026-10-21T19:00:00Z') } };
	assert.deepEqual([earlier, later].sort(compareRecentPosts).map(post => post.id), ['z-later', 'a-earlier']);
});
