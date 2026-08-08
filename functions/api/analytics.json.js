/**
 * GET /api/analytics.json
 *
 * 实时返回 blog.mushroom.cv 近 30 天的 Cloudflare Web Analytics（RUM）快照。
 * /analytics 页面在构建时已烤入一份静态快照做打底渲染，加载后调用本接口
 * 覆盖成当前数据 —— 接口挂了页面不会空，只是显示构建时的旧数字。
 *
 * 输出结构与 src/data/blog-analytics.json 完全一致，只有一个例外：
 * 边缘运行时读不到 src/content/blog/*.md，所以 pages[].title / titleEn
 * 只能由 slug 兜底生成，由前端用构建期烤入的标题表覆盖。
 *
 * 需要的环境变量（Cloudflare Pages → Settings → Environment variables）：
 *   CF_ANALYTICS_TOKEN  必需。**必须是只读 token**，权限只给
 *                       Account → Account Analytics → Read。
 *                       绝对不要复用部署用的 CLOUDFLARE_API_TOKEN：
 *                       那个 token 带 Pages 写权限，一旦泄漏等于交出发布权。
 *   CF_ACCOUNT_TAG      可选，默认用下方常量。
 *   CF_RUM_SITE_TAG     可选，默认用下方常量。
 */

const DEFAULT_ACCOUNT_TAG = '7bf23342f21baa5ebfc7bc7b74f5a1f2';
const DEFAULT_SITE_TAG = 'd7e4a410d16548ea8e729ced7499afe8';
const DAYS = 30;

// 边缘缓存时长。CF 的 RUM 数据本身有几分钟摄取延迟，缓存 3 分钟不影响新鲜度，
// 但能把 GraphQL 调用从「每次页面加载一次」压到「每 3 分钟一次」。
const EDGE_TTL = 180;
const BROWSER_TTL = 120;

const COUNTRY_NAMES = {
	SG: '新加坡', CN: '中国', TH: '泰国', US: '美国', HK: '香港',
	DE: '德国', JP: '日本', TW: '台湾', MY: '马来西亚', KR: '韩国',
	AR: '阿根廷', CA: '加拿大', AU: '澳大利亚', AE: '阿联酋',
	NL: '荷兰', VE: '委内瑞拉', IE: '爱尔兰', GB: '英国',
	NZ: '新西兰', SA: '沙特阿拉伯', IN: '印度', FR: '法国',
	ID: '印度尼西亚', VN: '越南', PH: '菲律宾', BR: '巴西',
	RU: '俄罗斯', ES: '西班牙', IT: '意大利', CH: '瑞士',
};

const COUNTRY_NAMES_EN = {
	SG: 'Singapore', CN: 'China', TH: 'Thailand', US: 'United States',
	HK: 'Hong Kong', DE: 'Germany', JP: 'Japan', TW: 'Taiwan',
	MY: 'Malaysia', KR: 'South Korea', AR: 'Argentina', CA: 'Canada',
	AU: 'Australia', AE: 'United Arab Emirates', NL: 'Netherlands',
	VE: 'Venezuela', IE: 'Ireland', GB: 'United Kingdom',
	NZ: 'New Zealand', SA: 'Saudi Arabia', IN: 'India', FR: 'France',
	ID: 'Indonesia', VN: 'Vietnam', PH: 'Philippines', BR: 'Brazil',
	RU: 'Russia', ES: 'Spain', IT: 'Italy', CH: 'Switzerland',
};

const SEARCH_HOSTS = new Set([
	'www.google.com', 'www.google.com.hk', 'www.google.com.tw',
	'cn.bing.com', 'www.bing.com', 'www.baidu.com', 'duckduckgo.com',
]);
const AI_HOSTS = new Set(['chatgpt.com', 'www.perplexity.ai', 'ima.qq.com', 'claude.ai']);
const ECOSYSTEM_SUFFIXES = ['mushroom.cv', 'mushroom.box', 'aastar.io', 'aastar.xyz'];

const flagEmoji = (code) =>
	!code || code.length !== 2
		? '🏳️'
		: String.fromCodePoint(...[...code.toUpperCase()].map((c) => 0x1f1e6 + c.charCodeAt(0) - 65));

function bucketReferer(host) {
	if (!host) return 'direct';
	if (SEARCH_HOSTS.has(host) || ['google.', 'bing.', 'baidu.', 'duckduckgo.'].some((s) => host.includes(s))) return 'search';
	if (AI_HOSTS.has(host) || ['chatgpt.com', 'perplexity.ai', 'claude.ai'].some((s) => host.includes(s))) return 'ai';
	if (ECOSYSTEM_SUFFIXES.some((suf) => host.endsWith(suf))) return 'ecosystem';
	return 'other';
}

function buildQuery(accountTag, siteTag, start, end) {
	const filt = `siteTag: "${siteTag}", datetime_geq: "${start}", datetime_leq: "${end}"`;
	return `query {
    viewer { accounts(filter: {accountTag: "${accountTag}"}) {
      daily: rumPageloadEventsAdaptiveGroups(limit: 100, filter: {${filt}}, orderBy: [date_ASC]) {
        count sum { visits } dimensions { date } }
      byCountry: rumPageloadEventsAdaptiveGroups(limit: 25, filter: {${filt}}, orderBy: [count_DESC]) {
        count sum { visits } dimensions { countryName } }
      byPage: rumPageloadEventsAdaptiveGroups(limit: 20, filter: {${filt}}, orderBy: [count_DESC]) {
        count sum { visits } dimensions { requestPath } }
      byReferer: rumPageloadEventsAdaptiveGroups(limit: 25, filter: {${filt}}, orderBy: [count_DESC]) {
        count dimensions { refererHost } }
      byDevice: rumPageloadEventsAdaptiveGroups(limit: 10, filter: {${filt}}, orderBy: [count_DESC]) {
        count dimensions { deviceType } }
      byBrowser: rumPageloadEventsAdaptiveGroups(limit: 10, filter: {${filt}}, orderBy: [count_DESC]) {
        count dimensions { userAgentBrowser } }
      byOS: rumPageloadEventsAdaptiveGroups(limit: 10, filter: {${filt}}, orderBy: [count_DESC]) {
        count dimensions { userAgentOS } }
      byBot: rumPageloadEventsAdaptiveGroups(limit: 5, filter: {${filt}}, orderBy: [count_DESC]) {
        count dimensions { bot } }
    } }
  }`;
}

function shape(d, startDate, endDate, generatedAt) {
	const daily = [...d.daily].sort((a, b) => (a.dimensions.date < b.dimensions.date ? -1 : 1));
	const dailyOut = daily.map((x) => ({
		date: x.dimensions.date.slice(5),
		pv: x.count,
		visits: x.sum.visits,
	}));

	const sumWindow = (slice) => ({
		pv: slice.reduce((a, x) => a + x.pv, 0),
		visits: slice.reduce((a, x) => a + x.visits, 0),
	});

	const byDesc = (arr) => [...arr].sort((a, b) => b.count - a.count);

	const countries = byDesc(d.byCountry)
		.slice(0, 12)
		.map((x) => {
			const code = x.dimensions.countryName || '??';
			return {
				code,
				flag: flagEmoji(code),
				name: COUNTRY_NAMES[code] || code,
				nameEn: COUNTRY_NAMES_EN[code] || code,
				pv: x.count,
				visits: x.sum.visits,
			};
		});

	const referers = { direct: 0, search: 0, ecosystem: 0, ai: 0, other: 0 };
	for (const x of d.byReferer) referers[bucketReferer(x.dimensions.refererHost || '')] += x.count;

	const pages = byDesc(d.byPage)
		.slice(0, 15)
		.map((x) => {
			const path = x.dimensions.requestPath;
			let slug = path.replace(/^\/+|\/+$/g, '');
			if (slug.startsWith('blog/')) slug = slug.slice(5);
			// 边缘拿不到文章标题，前端会用构建期烤入的标题表覆盖这两个字段
			const fallback = slug || '首页';
			return {
				title: slug ? fallback : '首页',
				titleEn: slug ? fallback : 'Home',
				path,
				pv: x.count,
				visits: x.sum.visits,
			};
		});

	const topDim = (rows, dim) => byDesc(rows).map((x) => ({ label: x.dimensions[dim], count: x.count }));
	const botRow = d.byBot.find((x) => x.dimensions.bot === 1);

	return {
		generatedAt,
		live: true,
		period: { start: startDate, end: endDate },
		totals: {
			pageviews: dailyOut.reduce((a, x) => a + x.pv, 0),
			visits: dailyOut.reduce((a, x) => a + x.visits, 0),
			bots: botRow ? botRow.count : 0,
		},
		last7: sumWindow(dailyOut.slice(-7)),
		prior7: sumWindow(dailyOut.slice(-14, -7)),
		daily: dailyOut,
		countries,
		countryTotal: d.byCountry.reduce((a, x) => a + x.count, 0),
		referers,
		pages,
		devices: topDim(d.byDevice, 'deviceType'),
		os: topDim(d.byOS, 'userAgentOS'),
		browsers: topDim(d.byBrowser, 'userAgentBrowser'),
	};
}

const json = (body, status, extraHeaders = {}) =>
	new Response(JSON.stringify(body), {
		status,
		headers: { 'content-type': 'application/json; charset=utf-8', ...extraHeaders },
	});

export async function onRequestGet(context) {
	const { request, env, waitUntil } = context;

	const token = env.CF_ANALYTICS_TOKEN;
	if (!token) {
		// 没配 token 不是异常，是「还没接上」——页面继续用构建快照即可
		return json(
			{ error: 'not_configured', detail: 'CF_ANALYTICS_TOKEN is not bound to this Pages project.' },
			503,
			{ 'cache-control': 'no-store' },
		);
	}

	const cache = caches.default;
	const cacheKey = new Request(new URL('/api/analytics.json', request.url).toString(), { method: 'GET' });
	const hit = await cache.match(cacheKey);
	if (hit) return hit;

	const end = new Date();
	const start = new Date(end.getTime() - DAYS * 86400_000);
	const iso = (d) => d.toISOString().replace(/\.\d{3}Z$/, 'Z');

	let payload;
	try {
		const upstream = await fetch('https://api.cloudflare.com/client/v4/graphql', {
			method: 'POST',
			headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' },
			body: JSON.stringify({
				query: buildQuery(
					env.CF_ACCOUNT_TAG || DEFAULT_ACCOUNT_TAG,
					env.CF_RUM_SITE_TAG || DEFAULT_SITE_TAG,
					iso(start),
					iso(end),
				),
			}),
		});

		if (!upstream.ok) {
			return json({ error: 'upstream_http', status: upstream.status }, 502, { 'cache-control': 'no-store' });
		}

		const body = await upstream.json();
		if (body.errors?.length) {
			return json({ error: 'graphql', detail: body.errors[0]?.message ?? 'unknown' }, 502, { 'cache-control': 'no-store' });
		}

		const account = body.data?.viewer?.accounts?.[0];
		if (!account?.daily?.length) {
			return json({ error: 'empty_dataset' }, 502, { 'cache-control': 'no-store' });
		}

		payload = shape(account, start.toISOString().slice(0, 10), end.toISOString().slice(0, 10), iso(end));
	} catch (err) {
		return json({ error: 'fetch_failed', detail: String(err) }, 502, { 'cache-control': 'no-store' });
	}

	const response = json(payload, 200, {
		'cache-control': `public, max-age=${BROWSER_TTL}, s-maxage=${EDGE_TTL}`,
		'access-control-allow-origin': 'https://blog.mushroom.cv',
	});
	waitUntil(cache.put(cacheKey, response.clone()));
	return response;
}
