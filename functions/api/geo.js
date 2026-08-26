/**
 * GET /api/geo
 *
 * 每日视频（daily-video）用来做地域路由的最小接口：告诉浏览器这次请求是从哪个
 * 国家/地区来的，VideoFrame 组件用它来决定默认展示 B 站源还是 YouTube 源。
 *
 * 只读 `request.cf.country`（Cloudflare 边缘自己解析好的字段，Pages Functions
 * 天然可用），不查库、不发外部请求，成本几乎为零——跟 /api/search 需要调
 * Workers AI / Vectorize 完全不是一个量级，缓存也不必做。
 *
 * 本地 `astro dev`（不经过 Cloudflare 边缘）拿不到 `request.cf`，返回
 * `country: null`；调用方（VideoFrame）要有这种情况下的兜底。
 *
 * 故意不做任何缓存（含不用 `caches.default`）：返回值因访客所在地而异，
 * 一旦被当成共享缓存对象存住，第一个访问者的国家会被错误地发给后面所有
 * 访客——这个接口的正确性完全依赖"每次请求都读一次边缘算好的 cf.country"。
 */
export async function onRequestGet(context) {
	const country = context.request.cf?.country ?? null;
	return new Response(JSON.stringify({ country }), {
		status: 200,
		headers: {
			'content-type': 'application/json; charset=utf-8',
			'cache-control': 'private, no-store',
		},
	});
}
