import type { CollectionEntry } from 'astro:content';

type PostDates = Pick<CollectionEntry<'blog'>['data'], 'pubDate' | 'updatedDate' | 'lastPublishedAt'>;
type DatedPost = { id: string; data: PostDates };

export function postActivityDate(data: PostDates): Date {
	return new Date(Math.max(
		data.pubDate.valueOf(),
		data.updatedDate?.valueOf() ?? 0,
		data.lastPublishedAt?.valueOf() ?? 0,
	));
}

export function compareRecentPosts(a: DatedPost, b: DatedPost): number {
	return postActivityDate(b.data).valueOf() - postActivityDate(a.data).valueOf()
		|| (b.data.lastPublishedAt?.valueOf() ?? 0) - (a.data.lastPublishedAt?.valueOf() ?? 0)
		|| b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
		|| a.id.localeCompare(b.id);
}
