/**
 * /analytics 看板的唯一渲染实现。
 *
 * 同一份代码跑两遍：
 *   1. 构建期 —— analytics.astro 在 frontmatter 里 import，把静态快照渲染成 HTML，
 *      保证首屏、SEO、以及 JS 被禁时仍然有完整内容。
 *   2. 运行期 —— 页面里的 <script> import 同一个模块，拿 /api/analytics.json 的
 *      实时数据重渲染，以及在中英之间切换。
 *
 * 两条路径共用一份实现，语言切换和实时刷新才不会渲染出两种样子。
 */

// ---------------------------------------------------------------- i18n

export const STRINGS = {
	en: {
		htmlLang: 'en',
		pageTitle: 'Website Analytics',
		pageDesc: (s, e) =>
			`Public traffic dashboard for blog.mushroom.cv — pageviews, geography, referrers and top posts (${s} ~ ${e}).`,
		source: 'Cloudflare Web Analytics (RUM, cookieless)',
		periodSuffix: 'last 30 days',
		liveOn: 'live',
		liveStale: 'build-time snapshot',
		langButton: '中文',
		langButtonLabel: 'Switch to Chinese',

		kpiPageviews: 'Pageviews',
		kpiVisits: 'Visits',
		kpiLast7: 'Pageviews, last 7 days',
		kpiRegions: 'Regions reached',
		botsExcluded: (n) => `${n} bot requests excluded`,
		pagesPerVisit: (n) => `~${n} pages per visit`,
		countriesIn30d: 'countries / regions in 30 days',

		trendHead: 'Daily pageview trend',
		trendNote: 'the final day is still in progress',
		legendPv: 'Pageviews',
		legendVisits: 'Visits',

		geoHead: 'Top 12 regions',
		geoNote: 'share of pageviews',
		geoCallout:
			'<b>Read with care</b>: the author is based in Southeast Asia, so the top regions may include self-visits from writing and debugging. Real reader distribution is more spread out than the chart suggests.',

		refHead: 'Traffic sources',
		refNote: 'grouped by referrer',
		refCallout:
			'<b>How to read this</b>: a large "Direct" share usually means bookmarks, or links opened from WeChat and private messages — Cloudflare cannot see the origin for those, so they all land in this bucket.',

		pagesHead: 'Top 15 pages',
		pagesNote: 'excluding the home page, these are article pageviews',
		colRank: '#',
		colPage: 'Page',
		colPv: 'Pageviews',
		colVisits: 'Visits',

		stackHead: 'Device / OS / Browser',
		stackNote: '30-day totals',
		groupDevice: 'Device type',
		groupOs: 'Operating system',
		groupBrowser: 'Browser',

		footer: (ts, live) =>
			`Data comes from the Cloudflare GraphQL Analytics API (Web Analytics / RUM dataset). No cookies, no personally identifying information. ` +
			(live
				? `This page queries live on load and is cached at the edge for up to 3 minutes. Last refreshed: ${ts} UTC.`
				: `Live refresh is unavailable right now, so these are build-time numbers. Generated: ${ts} UTC.`),

		home: 'Home',
		deviceLabels: { desktop: 'Desktop', mobile: 'Mobile', tablet: 'Tablet', other: 'Other' },
		refLabels: {
			direct: 'Direct / bookmark',
			search: 'Search engines',
			ecosystem: 'Ecosystem (mushroom.cv)',
			ai: 'AI assistant referral',
			other: 'Social / other',
		},
	},

	zh: {
		htmlLang: 'zh-CN',
		pageTitle: '流量看板',
		pageDesc: (s, e) =>
			`blog.mushroom.cv 近 30 天访问数据公开看板：浏览量、地域分布、流量来源与热门文章（${s} ~ ${e}）。`,
		source: 'Cloudflare Web Analytics（RUM，非 Cookie）',
		periodSuffix: '近 30 天',
		liveOn: '实时',
		liveStale: '构建时快照',
		langButton: 'EN',
		langButtonLabel: '切换到英文',

		kpiPageviews: '总浏览量',
		kpiVisits: '独立访问',
		kpiLast7: '近 7 天浏览量',
		kpiRegions: '覆盖地区',
		botsExcluded: (n) => `已剔除 ${n} 次机器人抓取`,
		pagesPerVisit: (n) => `约 ${n} 页 / 次访问`,
		countriesIn30d: '个国家/地区，30 天内',

		trendHead: '每日浏览量趋势',
		trendNote: '最近一日为当天未完结数据',
		legendPv: '浏览量',
		legendVisits: '独立访问',

		geoHead: '地域分布 Top 12',
		geoNote: '按浏览量占比',
		geoCallout:
			'<b>解读提醒</b>：博主本人常驻东南亚，占比靠前的地区可能混入了作者写作/调试时的自访问，实际读者地域分布会比图上更分散。',

		refHead: '流量来源',
		refNote: '按 referrer 归类',
		refCallout:
			'<b>怎么读</b>：「直接访问」占大头通常意味着读者是收藏/书签，或从公众号、私聊分享链接点进来的——这类来源 Cloudflare 拿不到具体出处，都会归到这一类。',

		pagesHead: '最受欢迎的页面 Top 15',
		pagesNote: '首页除外为文章浏览量',
		colRank: '#',
		colPage: '页面',
		colPv: '浏览量',
		colVisits: '独立访问',

		stackHead: '设备 / 系统 / 浏览器',
		stackNote: '30 天汇总',
		groupDevice: '设备类型',
		groupOs: '操作系统',
		groupBrowser: '浏览器',

		footer: (ts, live) =>
			`数据来自 Cloudflare GraphQL Analytics API（Web Analytics / RUM 数据集），不使用 Cookie、不采集个人身份信息。` +
			(live
				? `本页在加载时实时查询，边缘缓存最多 3 分钟。最近刷新：${ts} UTC。`
				: `实时刷新当前不可用，显示的是构建时的数字。生成时间：${ts} UTC。`),

		home: '首页',
		deviceLabels: { desktop: '桌面端', mobile: '移动端', tablet: '平板', other: '其他' },
		refLabels: {
			direct: '直接访问 / 书签',
			search: '搜索引擎',
			ecosystem: '站内跳转（mushroom.cv 生态）',
			ai: 'AI 助手引荐',
			other: '社交 / 其他',
		},
	},
};

// ---------------------------------------------------------------- helpers

/** 标题来自 frontmatter，可能含引号或尖括号；拼 HTML 字符串前必须转义。 */
export const esc = (s) =>
	String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);

const fmt = (n) => Number(n).toLocaleString('en-US');
const pct = (n, total) => (total ? ((n / total) * 100).toFixed(1) : '0.0');

const REF_COLORS = {
	direct: 'rgb(var(--gray))',
	search: 'rgb(var(--accent))',
	ecosystem: '#1f8f86',
	ai: '#8a5fd1',
	other: 'rgb(var(--gray-light))',
};
const DEVICE_COLORS = ['rgb(var(--accent))', '#1f8f86', 'rgb(var(--gray))', '#8a5fd1', '#c9982e', '#5b9bd5'];

const countryName = (c, lang) => (lang === 'zh' ? c.name : c.nameEn || c.name);
const pageTitle = (p, lang) => (lang === 'zh' ? p.title : p.titleEn || p.title);

/** 实时接口在边缘拿不到文章标题，用构建期烤入的标题表补回来。 */
export function mergeTitles(data, titleMap) {
	if (!titleMap) return data;
	return {
		...data,
		pages: data.pages.map((p) => (titleMap[p.path] ? { ...p, ...titleMap[p.path] } : p)),
	};
}

// ---------------------------------------------------------------- sections

export function renderKpis(data, lang) {
	const t = STRINGS[lang];
	const deltaPv = data.last7.pv - data.prior7.pv;
	const deltaPct = data.prior7.pv ? ((deltaPv / data.prior7.pv) * 100).toFixed(1) : '0.0';
	const dir = deltaPv > 0 ? 'up' : deltaPv < 0 ? 'down' : 'flat';
	const arrow = deltaPv > 0 ? '▲' : deltaPv < 0 ? '▼' : '–';
	const perVisit = data.totals.visits ? (data.totals.pageviews / data.totals.visits).toFixed(2) : '0.00';

	return `
    <div class="kpi">
      <div class="label">${esc(t.kpiPageviews)}</div>
      <div class="value">${fmt(data.totals.pageviews)}</div>
      <div class="delta flat">${esc(t.botsExcluded(fmt(data.totals.bots)))}</div>
    </div>
    <div class="kpi">
      <div class="label">${esc(t.kpiVisits)}</div>
      <div class="value">${fmt(data.totals.visits)}</div>
      <div class="delta flat">${esc(t.pagesPerVisit(perVisit))}</div>
    </div>
    <div class="kpi">
      <div class="label">${esc(t.kpiLast7)}</div>
      <div class="value">${fmt(data.last7.pv)}</div>
      <div class="delta ${dir}">${arrow} ${deltaPct}% (${fmt(data.prior7.pv)} → ${fmt(data.last7.pv)})</div>
    </div>
    <div class="kpi">
      <div class="label">${esc(t.kpiRegions)}</div>
      <div class="value">${data.countries.length}+</div>
      <div class="delta flat">${esc(t.countriesIn30d)}</div>
    </div>`;
}

export function renderTrend(data) {
	const W = 1000, H = 200, padT = 14, padB = 20;
	const n = data.daily.length;
	if (!n) return '';
	const maxV = Math.max(...data.daily.map((d) => d.pv)) * 1.12 || 1;
	const xAt = (i) => (n === 1 ? W / 2 : (i / (n - 1)) * W);
	const yAt = (v) => padT + (1 - v / maxV) * (H - padT - padB);
	const path = (key) => data.daily.map((d, i) => `${i === 0 ? 'M' : 'L'} ${xAt(i).toFixed(1)} ${yAt(d[key]).toFixed(1)}`).join(' ');
	const linePv = path('pv');
	const areaPv = `${linePv} L ${xAt(n - 1).toFixed(1)} ${yAt(0).toFixed(1)} L 0 ${yAt(0).toFixed(1)} Z`;
	const labelIdx = [...new Set([0, Math.round((n - 1) * 0.25), Math.round((n - 1) * 0.5), Math.round((n - 1) * 0.75), n - 1])];

	const grid = [0, 1, 2, 3, 4]
		.map((i) => `<line x1="0" y1="${padT + (i / 4) * (H - padT - padB)}" x2="${W}" y2="${padT + (i / 4) * (H - padT - padB)}" />`)
		.join('');
	const labels = labelIdx
		.map(
			(i) =>
				`<text x="${xAt(i)}" y="${H - 2}" class="trend-label" text-anchor="${i === 0 ? 'start' : i === n - 1 ? 'end' : 'middle'}">${esc(data.daily[i].date)}</text>`,
		)
		.join('');

	return `<g class="trend-grid">${grid}</g>
    <defs><linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="rgb(var(--accent))" stop-opacity="0.3" />
      <stop offset="100%" stop-color="rgb(var(--accent))" stop-opacity="0" />
    </linearGradient></defs>
    <path d="${areaPv}" fill="url(#areaFill)" stroke="none" />
    <path d="${path('visits')}" fill="none" stroke="#1f8f86" stroke-width="1.6" stroke-opacity="0.85" />
    <path d="${linePv}" fill="none" stroke="rgb(var(--accent))" stroke-width="2.25" />
    <circle cx="${xAt(n - 1)}" cy="${yAt(data.daily[n - 1].pv)}" r="4.5" fill="rgb(var(--accent))" stroke="#fff" stroke-width="2" />
    ${labels}`;
}

export function renderCountries(data, lang) {
	const max = Math.max(...data.countries.map((c) => c.pv)) || 1;
	return data.countries
		.map(
			(c) => `<div class="row">
      <span class="flag">${c.flag}</span>
      <span class="name">${esc(countryName(c, lang))}</span>
      <span class="track"><span class="fill" style="width:${(c.pv / max) * 100}%"></span></span>
      <span class="pct">${pct(c.pv, data.countryTotal)}%</span>
    </div>`,
		)
		.join('');
}

export function renderReferers(data, lang) {
	const t = STRINGS[lang];
	const total = Object.values(data.referers).reduce((a, b) => a + b, 0);
	return Object.keys(data.referers)
		.map((k) => ({ key: k, count: data.referers[k] }))
		.sort((a, b) => b.count - a.count)
		.map(
			(r) => `<div class="chip">
      <span class="tag"><i style="background:${REF_COLORS[r.key]}"></i>${esc(t.refLabels[r.key] || r.key)}</span>
      <span class="num">${pct(r.count, total)}%</span>
    </div>`,
		)
		.join('');
}

export function renderPages(data, lang) {
	return data.pages
		.map(
			(p, i) => `<tr>
      <td class="rank">${i + 1}</td>
      <td class="title">
        <a href="${esc(p.path)}" target="_blank" rel="noopener">${esc(pageTitle(p, lang))}</a>
        <span class="path">${esc(p.path)}</span>
      </td>
      <td class="num">${fmt(p.pv)}</td>
      <td class="num">${fmt(p.visits)}</td>
    </tr>`,
		)
		.join('');
}

export function renderStacks(data, lang) {
	const t = STRINGS[lang];
	const groups = [
		{ label: t.groupDevice, rows: data.devices, translate: true },
		{ label: t.groupOs, rows: data.os, translate: false },
		{ label: t.groupBrowser, rows: data.browsers, translate: false },
	];
	return groups
		.map((g) => {
			const max = Math.max(...g.rows.map((r) => r.count)) || 1;
			const rows = g.rows
				.map((r, i) => {
					const label = g.translate ? t.deviceLabels[r.label] || r.label : r.label;
					return `<div class="row">
          <span class="name">${esc(label)}</span>
          <span class="track"><span class="fill" style="width:${(r.count / max) * 100}%;background:${DEVICE_COLORS[i % DEVICE_COLORS.length]}"></span></span>
          <span class="num">${fmt(r.count)}</span>
        </div>`;
				})
				.join('');
			return `<div><div class="note" style="margin-bottom:0.5em;">${esc(g.label)}</div><div class="mini-bars">${rows}</div></div>`;
		})
		.join('');
}

/** 把一份数据完整刷进已有的 DOM 结构里（实时刷新和语言切换都走这里）。 */
export function paint(root, data, lang) {
	const t = STRINGS[lang];
	const set = (sel, html) => {
		const el = root.querySelector(sel);
		if (el) el.innerHTML = html;
	};
	const text = (sel, value) => {
		const el = root.querySelector(sel);
		if (el) el.textContent = value;
	};

	document.documentElement.lang = t.htmlLang;

	text('[data-a="title"]', `📊 ${t.pageTitle}`);
	text('[data-a="source"]', t.source);
	text('[data-a="period"]', `${data.period.start} ~ ${data.period.end} · ${t.periodSuffix} · ${data.live ? t.liveOn : t.liveStale}`);

	const btn = root.querySelector('[data-a="lang"]');
	if (btn) {
		btn.textContent = t.langButton;
		btn.setAttribute('aria-label', t.langButtonLabel);
	}

	set('[data-a="kpis"]', renderKpis(data, lang));
	set('[data-a="trend"]', renderTrend(data));
	set('[data-a="countries"]', renderCountries(data, lang));
	set('[data-a="referers"]', renderReferers(data, lang));
	set('[data-a="pages"]', renderPages(data, lang));
	set('[data-a="stacks"]', renderStacks(data, lang));

	text('[data-a="trend-head"]', t.trendHead);
	text('[data-a="trend-note"]', t.trendNote);
	text('[data-a="legend-pv"]', t.legendPv);
	text('[data-a="legend-visits"]', t.legendVisits);
	text('[data-a="geo-head"]', t.geoHead);
	text('[data-a="geo-note"]', t.geoNote);
	set('[data-a="geo-callout"]', t.geoCallout);
	text('[data-a="ref-head"]', t.refHead);
	text('[data-a="ref-note"]', t.refNote);
	set('[data-a="ref-callout"]', t.refCallout);
	text('[data-a="pages-head"]', t.pagesHead);
	text('[data-a="pages-note"]', t.pagesNote);
	text('[data-a="col-rank"]', t.colRank);
	text('[data-a="col-page"]', t.colPage);
	text('[data-a="col-pv"]', t.colPv);
	text('[data-a="col-visits"]', t.colVisits);
	text('[data-a="stack-head"]', t.stackHead);
	text('[data-a="stack-note"]', t.stackNote);

	const ts = String(data.generatedAt).slice(0, 16).replace('T', ' ');
	text('[data-a="footer"]', t.footer(ts, !!data.live));
}
