// T1.3.3 验收测试：/api/search 端点。直接调用 onRequestPost，用内存 Map 模拟
// env.BLOG_SEARCH_KV、假的 env.AI / env.VECTORIZE_INDEX，不需要 wrangler/Miniflare。
//
// 2026-08-23：/api/search 去掉了登录门禁（见 search.js 文件头注释），这个测试文件
// 相应删掉了所有 401/Cookie/会话限速相关用例，只保留跟登录无关的行为：输入校验、
// IP 限速、缓存、AI/Vectorize 失败降级、搜索统计。

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { MAX_ATTEMPTS } from '../_lib/rate-limit.js';
import { onRequestGet, onRequestPost } from './search.js';

function makeFakeKv() {
	const store = new Map();
	return {
		store, // 测试用：直接读写底层 Map，用于伪造/篡改缓存内容（见 Array.isArray 回归测试）
		async get(key) {
			return store.has(key) ? store.get(key) : null;
		},
		async put(key, value) {
			store.set(key, value);
		},
	};
}

function makeFakeAi({ vector = [0.1, 0.2, 0.3], shouldThrow = false, recordedCalls = null } = {}) {
	return {
		async run(model, { text }) {
			if (recordedCalls) recordedCalls.push(text);
			if (shouldThrow) throw new Error('Workers AI unavailable');
			return { data: text.map(() => vector) };
		},
	};
}

function makeFakeAnalytics({ shouldThrow = false, recordedPoints = null } = {}) {
	return {
		writeDataPoint(point) {
			if (shouldThrow) throw new Error('Analytics Engine unavailable');
			if (recordedPoints) recordedPoints.push(point);
		},
	};
}

function makeFakeVectorize({ matches = [], shouldThrow = false } = {}) {
	return {
		async query(vector, opts) {
			if (shouldThrow) throw new Error('Vectorize unavailable');
			return { matches };
		},
	};
}

function makeMatch(articleId, score, overrides = {}) {
	return {
		id: `chunk-${articleId}-${score}`,
		score,
		metadata: {
			article_id: articleId,
			title: `Title for ${articleId}`,
			url: `/blog/${articleId}/`,
			language: 'zh',
			excerpt: `excerpt for ${articleId}`,
			...overrides,
		},
	};
}

const TEST_SESSION_SECRET = 'test-session-secret-do-not-use-in-prod';

async function makeEnv(overrides = {}) {
	return {
		BLOG_SEARCH_KV: makeFakeKv(),
		AI: makeFakeAi(),
		VECTORIZE_INDEX: makeFakeVectorize(),
		// FU-25：真实部署里这个 secret 总是配置好的（登录 Cookie 签名要用），默认给测试
		// env 也配上，跟生产环境行为一致；专门测"secret 缺失"这个边角情况的用例会显式
		// 覆盖成 undefined。
		BLOG_SEARCH_SESSION_SECRET: TEST_SESSION_SECRET,
		...overrides,
	};
}

function makeRequest(body, { ip = '5.5.5.5', contentType = 'application/json' } = {}) {
	const bodyText = JSON.stringify(body);
	const headers = {
		'Content-Type': contentType,
		'CF-Connecting-IP': ip,
		'Content-Length': String(new TextEncoder().encode(bodyText).length),
	};
	return new Request('https://example.com/api/search', { method: 'POST', headers, body: bodyText });
}

test('缺少必需的 Cloudflare 绑定：503（fail-closed，不静默放行到无限速）', async () => {
	const env = await makeEnv({ AI: undefined });
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }), env });
	assert.equal(resp.status, 503);
});

test('Content-Type 不是 application/json：400（同 search-auth.js 的 text/plain 绕过修复）', async () => {
	const env = await makeEnv();
	const resp = await onRequestPost({
		request: makeRequest({ query: 'hello' }, { contentType: 'text/plain' }),
		env,
	});
	assert.equal(resp.status, 400);
});

test('请求体超过大小上限：413', async () => {
	const env = await makeEnv();
	const resp = await onRequestPost({
		request: makeRequest({ query: 'x'.repeat(5000) }),
		env,
	});
	assert.equal(resp.status, 413);
});

// 回归测试（T1.3.3 自审对抗式 review 抓到的真实问题）：Content-Length 是请求方自己声明的，
// 谎报成一个很小的值、但实际发送的 body 远超上限，不该只靠这个 header 就放行
test('回归测试：Content-Length 撒谎（远小于实际 body），仍然按实际字节数拦截：413', async () => {
	const env = await makeEnv();
	const bodyText = JSON.stringify({ query: 'x'.repeat(5000) });
	const request = new Request('https://example.com/api/search', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'CF-Connecting-IP': '1.1.1.1',
			'Content-Length': '10', // 谎报成很小的值
		},
		body: bodyText,
	});
	const resp = await onRequestPost({ request, env });
	assert.equal(resp.status, 413);
});

test('请求体不是合法 JSON：400', async () => {
	const env = await makeEnv();
	const badRequest = new Request('https://example.com/api/search', {
		method: 'POST',
		headers: { 'Content-Type': 'application/json', 'CF-Connecting-IP': '1.1.1.1' },
		body: 'not json{{{',
	});
	const resp = await onRequestPost({ request: badRequest, env });
	assert.equal(resp.status, 400);
});

test('query 为空：400', async () => {
	const env = await makeEnv();
	const resp = await onRequestPost({ request: makeRequest({ query: '' }), env });
	assert.equal(resp.status, 400);
});

test('query 超过长度上限：400', async () => {
	const env = await makeEnv();
	const resp = await onRequestPost({ request: makeRequest({ query: 'a'.repeat(401) }), env });
	assert.equal(resp.status, 400);
});

test('限速：同一 IP 超过搜索限速次数后 429', async () => {
	const env = await makeEnv();
	const ip = '7.7.7.7';
	// 搜索限速配置在 search.js 内部（30 次/5 分钟），这里只断言"存在一个上限、超过会 429"，
	// 不依赖具体数字（数字本身在 search.js 里注释说明了理由，测试只验证行为）。
	// 每次换不同的 query（T1.3.4 加了查询缓存之后，重复同一个 query 会命中缓存、
	// 完全跳过限速计数，测限速必须保证每次都是缓存未命中）。
	let lastStatus;
	for (let i = 0; i < 35; i++) {
		const resp = await onRequestPost({ request: makeRequest({ query: `hello-${i}` }, { ip }), env });
		lastStatus = resp.status;
		if (lastStatus === 429) break;
	}
	assert.equal(lastStatus, 429, '连续请求应该在某一次触发限速');
});

test('限速：不同 IP 互不影响', async () => {
	const env = await makeEnv();
	for (let i = 0; i < MAX_ATTEMPTS * 10; i++) {
		const resp = await onRequestPost({
			request: makeRequest({ query: `hello-${i}` }, { ip: '8.8.8.8' }),
			env,
		});
		if (resp.status === 429) break;
	}
	const otherIp = await onRequestPost({
		request: makeRequest({ query: 'hello-other' }, { ip: '9.9.9.9' }),
		env,
	});
	assert.equal(otherIp.status, 200, '另一个 IP 不应该被前一个 IP 的限速影响');
});

test('Workers AI 调用失败：503，不是裸抛异常', async () => {
	const env = await makeEnv({ AI: makeFakeAi({ shouldThrow: true }) });
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }), env });
	assert.equal(resp.status, 503);
});

test('Vectorize 查询失败：503', async () => {
	const env = await makeEnv({ VECTORIZE_INDEX: makeFakeVectorize({ shouldThrow: true }) });
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }), env });
	assert.equal(resp.status, 503);
});

test('正常查询：按 article_id 聚合去重，只保留每篇文章分数最高的 chunk', async () => {
	const matches = [
		makeMatch('article-a', 0.9),
		makeMatch('article-a', 0.6), // 同一篇文章的另一个 chunk，分数更低，应该被丢弃
		makeMatch('article-b', 0.5),
	];
	const env = await makeEnv({ VECTORIZE_INDEX: makeFakeVectorize({ matches }) });
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }), env });
	assert.equal(resp.status, 200);
	const body = await resp.json();
	assert.equal(body.results.length, 2);
	const articleA = body.results.find((r) => r.article_id === 'article-a');
	assert.equal(articleA.score, 0.9, '应该保留分数更高的那个 chunk，不是先出现的那个');
});

test('正常查询：低于相似度阈值的候选被过滤掉', async () => {
	const matches = [makeMatch('article-good', 0.6), makeMatch('article-bad', 0.1)];
	const env = await makeEnv({ VECTORIZE_INDEX: makeFakeVectorize({ matches }) });
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }), env });
	const body = await resp.json();
	assert.equal(body.results.length, 1);
	assert.equal(body.results[0].article_id, 'article-good');
});

test('正常查询：全部候选都低于阈值时返回空数组，不是报错', async () => {
	const matches = [makeMatch('article-a', 0.1), makeMatch('article-b', 0.2)];
	const env = await makeEnv({ VECTORIZE_INDEX: makeFakeVectorize({ matches }) });
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }), env });
	assert.equal(resp.status, 200);
	const body = await resp.json();
	assert.deepEqual(body.results, []);
});

test('正常查询：结果按分数降序排列', async () => {
	const matches = [makeMatch('article-low', 0.45), makeMatch('article-high', 0.8), makeMatch('article-mid', 0.6)];
	const env = await makeEnv({ VECTORIZE_INDEX: makeFakeVectorize({ matches }) });
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }), env });
	const body = await resp.json();
	assert.deepEqual(
		body.results.map((r) => r.article_id),
		['article-high', 'article-mid', 'article-low'],
	);
});

test('正常查询：返回字段形状正确（article_id/title/url/language/excerpt/score）', async () => {
	const matches = [makeMatch('article-a', 0.7, { language: 'en' })];
	const env = await makeEnv({ VECTORIZE_INDEX: makeFakeVectorize({ matches }) });
	const resp = await onRequestPost({ request: makeRequest({ query: 'hello' }), env });
	const body = await resp.json();
	assert.deepEqual(body.results[0], {
		article_id: 'article-a',
		title: 'Title for article-a',
		url: '/blog/article-a/',
		language: 'en',
		excerpt: 'excerpt for article-a',
		score: 0.7,
	});
});

// T1.3.4 新增：查询结果缓存
test('缓存：同一个查询第二次命中缓存，不再调用 AI/Vectorize（即使它们这次会报错）', async () => {
	const kv = makeFakeKv();
	const matches = [makeMatch('article-a', 0.7)];
	const workingEnv = await makeEnv({
		BLOG_SEARCH_KV: kv,
		VECTORIZE_INDEX: makeFakeVectorize({ matches }),
	});

	const first = await onRequestPost({ request: makeRequest({ query: 'Pagefind' }), env: workingEnv });
	assert.equal(first.status, 200);
	const firstBody = await first.json();

	// 第二次请求用会报错的 AI/Vectorize，但共用同一个 KV（缓存应该已经写进去了）
	const brokenEnv = await makeEnv({
		BLOG_SEARCH_KV: kv,
		AI: makeFakeAi({ shouldThrow: true }),
		VECTORIZE_INDEX: makeFakeVectorize({ shouldThrow: true }),
	});
	const second = await onRequestPost({
		request: makeRequest({ query: 'Pagefind' }, { ip: '20.20.20.20' }),
		env: brokenEnv,
	});
	assert.equal(second.status, 200, '第二次应该直接从缓存返回，不应该因为 AI/Vectorize 报错而 503');
	const secondBody = await second.json();
	assert.deepEqual(secondBody.results, firstBody.results);
});

test('缓存：查询做大小写/首尾空白归一化，"Pagefind" 和 " pagefind " 命中同一条缓存', async () => {
	const kv = makeFakeKv();
	const matches = [makeMatch('article-a', 0.7)];
	const workingEnv = await makeEnv({ BLOG_SEARCH_KV: kv, VECTORIZE_INDEX: makeFakeVectorize({ matches }) });

	await onRequestPost({ request: makeRequest({ query: 'Pagefind' }), env: workingEnv });

	const brokenEnv = await makeEnv({
		BLOG_SEARCH_KV: kv,
		AI: makeFakeAi({ shouldThrow: true }),
		VECTORIZE_INDEX: makeFakeVectorize({ shouldThrow: true }),
	});
	const resp = await onRequestPost({
		request: makeRequest({ query: '  pagefind  ' }, { ip: '21.21.21.21' }),
		env: brokenEnv,
	});
	assert.equal(resp.status, 200, '大小写/空白不同但语义相同的 query 应该命中同一条缓存');
});

// 回归测试（FU-16）：NFKC 归一化折叠全角字符 + 折叠连续空白
test('缓存：全角字符和连续空白也能归一化命中同一条缓存', async () => {
	const kv = makeFakeKv();
	const matches = [makeMatch('article-a', 0.7)];
	const workingEnv = await makeEnv({ BLOG_SEARCH_KV: kv, VECTORIZE_INDEX: makeFakeVectorize({ matches }) });

	// 全角 "Ｐａｇｅｆｉｎｄ" 经 NFKC 归一化后应该等价于半角 "pagefind"
	await onRequestPost({ request: makeRequest({ query: 'Ｐａｇｅｆｉｎｄ' }), env: workingEnv });

	const brokenEnv = await makeEnv({
		BLOG_SEARCH_KV: kv,
		AI: makeFakeAi({ shouldThrow: true }),
		VECTORIZE_INDEX: makeFakeVectorize({ shouldThrow: true }),
	});
	const resp = await onRequestPost({
		request: makeRequest({ query: 'pagefind' }, { ip: '24.24.24.24' }),
		env: brokenEnv,
	});
	assert.equal(resp.status, 200, '全角字符归一化后应该命中半角同义查询的缓存');

	// 中间连续多个空格也应该归一化命中同一条缓存："foo   bar" -> "foo bar"
	await onRequestPost({ request: makeRequest({ query: 'foo   bar' }, { ip: '26.26.26.26' }), env: workingEnv });
	const resp2 = await onRequestPost({
		request: makeRequest({ query: 'foo bar' }, { ip: '27.27.27.27' }),
		env: brokenEnv,
	});
	assert.equal(resp2.status, 200, '连续空白折叠后应该命中同一条缓存');
});

// 回归测试（FU-16 round 2 review 抓到的真实 bug）：归一化原来只用在算缓存 key，传给
// env.AI.run() 的还是原始未归一化的 query——全角/半角查询被判成"同一条缓存"，但只有
// 先到的那个真正用自己的原文去 embedding，后到的那个直接吃缓存，等于两个查询在
// embedding 层面根本没有真的等价。这里直接断言 AI.run() 收到的文本本身就是归一化后的
// 字符串，不是原始输入——修复后 embedding 输入和缓存 key 用的是同一份数据，不会再割裂。
test('缓存归一化：传给 env.AI.run() 的是归一化后的文本，不是原始未归一化的 query', async () => {
	const recordedCalls = [];
	const kv = makeFakeKv();
	const matches = [makeMatch('article-a', 0.7)];
	const env = await makeEnv({
		BLOG_SEARCH_KV: kv,
		AI: makeFakeAi({ recordedCalls }),
		VECTORIZE_INDEX: makeFakeVectorize({ matches }),
	});

	await onRequestPost({ request: makeRequest({ query: '  Ｐａｇｅｆｉｎｄ  ' }), env });

	assert.equal(recordedCalls.length, 1);
	assert.deepEqual(recordedCalls[0], ['pagefind'], 'AI 应该收到归一化后的文本（NFKC 折叠全角 + trim），不是原始的全角+首尾空白字符串');
});

// 回归测试（T1.3.4 round 2 自审对抗式 review 抓到的真实问题）：缓存命中原来完全不计入
// 限速，等于给共享 KV namespace 开了一条不限速的读流量通道——不是"省计费调用"这个威胁
// 模型要挡的东西，是另一种拒绝服务面。修复后限速在缓存检查之前做，缓存命中依然要计次，
// 只是命中之后跳过真正计费的 AI/Vectorize。
test('缓存：命中缓存依然要计入限速——重复同一个查询超过限速上限后一样会 429', async () => {
	const kv = makeFakeKv();
	const matches = [makeMatch('article-a', 0.7)];
	const ip = '22.22.22.22';
	const workingEnv = await makeEnv({ BLOG_SEARCH_KV: kv, VECTORIZE_INDEX: makeFakeVectorize({ matches }) });
	await onRequestPost({ request: makeRequest({ query: 'Pagefind' }, { ip }), env: workingEnv });

	// 同一个 IP，远超 MAX_ATTEMPTS 次重复同一个查询——即使命中缓存，限速计数依然在累加，
	// 超过上限后应该 429，不能因为命中缓存就对限速免疫
	let lastStatus;
	for (let i = 0; i < 50; i++) {
		const resp = await onRequestPost({ request: makeRequest({ query: 'Pagefind' }, { ip }), env: workingEnv });
		lastStatus = resp.status;
		if (lastStatus === 429) break;
	}
	assert.equal(lastStatus, 429, '缓存命中不应该让请求对限速免疫');
});

test('缓存：命中缓存确实跳过了 AI/Vectorize 调用（限速额度内的正常重复查询不报错）', async () => {
	const kv = makeFakeKv();
	const matches = [makeMatch('article-a', 0.7)];
	const ip = '23.23.23.23';
	const workingEnv = await makeEnv({ BLOG_SEARCH_KV: kv, VECTORIZE_INDEX: makeFakeVectorize({ matches }) });
	await onRequestPost({ request: makeRequest({ query: 'Pagefind' }, { ip }), env: workingEnv });

	// 第二次用会报错的 AI/Vectorize，但因为命中缓存，不应该真的调用到它们
	const brokenEnv = await makeEnv({
		BLOG_SEARCH_KV: kv,
		AI: makeFakeAi({ shouldThrow: true }),
		VECTORIZE_INDEX: makeFakeVectorize({ shouldThrow: true }),
	});
	const resp = await onRequestPost({ request: makeRequest({ query: 'Pagefind' }, { ip }), env: brokenEnv });
	assert.equal(resp.status, 200, '限速额度内的缓存命中应该正常返回，不应该被跳过的 AI/Vectorize 报错影响');
});

// 回归测试（round 2 review 的非阻塞建议）：KV 里如果是脏数据（非数组，比如缓存写入被
// 别的进程/手动操作污染，或者未来缓存 schema 变了但旧值还没过期），原来会不校验形状就
// 原样透传给前端——search.astro 的 searchVectorRanked 是 Promise.all 里唯一没 .catch
// 的一支，拿到非数组直接 .map 会整个搜索请求打死，连 Pagefind 那半本来能成功的结果都
// 一起没了。修复后非数组值当作缓存未命中处理，照常走 AI/Vectorize 重新计算。
test('缓存：命中的缓存值不是数组（脏数据）时，当作未命中处理，不会原样透传', async () => {
	const kv = makeFakeKv();
	const matches = [makeMatch('article-a', 0.7)];
	const workingEnv = await makeEnv({ BLOG_SEARCH_KV: kv, VECTORIZE_INDEX: makeFakeVectorize({ matches }) });

	// 先正常发一次请求，让代码自己算出真正的缓存 key 并写入；随后直接改写底层 Map，
	// 用非数组值污染这条缓存——不需要在测试里重新实现一遍 queryCacheKey 的哈希算法。
	await onRequestPost({ request: makeRequest({ query: 'Pagefind' }, { ip: '28.28.28.28' }), env: workingEnv });
	// 同一个 KV namespace 也扛着限速计数器的 key，不能假设"只写了一条"——精确找出
	// 缓存自己的那条（searchcache: 前缀）来篡改，不碰限速计数器的 key。
	const cacheKey = [...kv.store.keys()].find((k) => k.startsWith('searchcache:'));
	assert.ok(cacheKey, '应该已经写入了一条 searchcache: 前缀的缓存');
	kv.store.set(cacheKey, JSON.stringify({ not: 'an array' }));

	const resp = await onRequestPost({ request: makeRequest({ query: 'Pagefind' }, { ip: '29.29.29.29' }), env: workingEnv });
	assert.equal(resp.status, 200, '脏缓存不应该导致请求失败');
	const body = await resp.json();
	assert.ok(Array.isArray(body.results), '应该当作缓存未命中，重新计算出正常的数组结果，而不是把脏数据原样返回');
	assert.equal(body.results[0].article_id, 'article-a');
});

// 搜索使用统计（用户明确要求：想看上线后有多少人在用、都搜了什么）。
test('搜索统计：新计算的结果会写一条 Analytics Engine 数据点（query/结果数/非缓存命中）', async () => {
	const recordedPoints = [];
	const matches = [makeMatch('article-a', 0.7)];
	const env = await makeEnv({
		VECTORIZE_INDEX: makeFakeVectorize({ matches }),
		SEARCH_ANALYTICS: makeFakeAnalytics({ recordedPoints }),
	});
	const resp = await onRequestPost({ request: makeRequest({ query: 'Pagefind' }, { ip: '30.30.30.30' }), env });
	assert.equal(resp.status, 200);
	assert.equal(recordedPoints.length, 1);
	assert.deepEqual(recordedPoints[0].blobs, ['pagefind']);
	assert.deepEqual(recordedPoints[0].doubles, [1, 0], '结果数=1，cacheHit 标记=0（未命中缓存）');
});

// FU-25 回归测试：index1 存的是 HMAC(secret, IP)，不是明文 IP。
test('搜索统计（FU-25）：index1 不是明文 IP，是带密钥的哈希值', async () => {
	const recordedPoints = [];
	const env = await makeEnv({
		VECTORIZE_INDEX: makeFakeVectorize({ matches: [makeMatch('article-a', 0.7)] }),
		SEARCH_ANALYTICS: makeFakeAnalytics({ recordedPoints }),
	});
	await onRequestPost({ request: makeRequest({ query: 'Pagefind' }, { ip: '30.30.30.30' }), env });
	assert.equal(recordedPoints.length, 1);
	assert.equal(recordedPoints[0].indexes.length, 1);
	assert.notEqual(recordedPoints[0].indexes[0], '30.30.30.30', 'index1 不应该是明文 IP');
	assert.match(recordedPoints[0].indexes[0], /^[0-9a-f]{32}$/, 'index1 应该是 128 位十六进制哈希');
});

test('搜索统计（FU-25）：同一个 IP 每次都算出同一个哈希（uniqueIps 统计要靠这个才准）', async () => {
	const recorded1 = [];
	const env1 = await makeEnv({
		VECTORIZE_INDEX: makeFakeVectorize({ matches: [makeMatch('article-a', 0.7)] }),
		SEARCH_ANALYTICS: makeFakeAnalytics({ recordedPoints: recorded1 }),
	});
	await onRequestPost({ request: makeRequest({ query: 'first query' }, { ip: '40.40.40.40' }), env: env1 });

	const recorded2 = [];
	const env2 = await makeEnv({
		VECTORIZE_INDEX: makeFakeVectorize({ matches: [makeMatch('article-a', 0.7)] }),
		SEARCH_ANALYTICS: makeFakeAnalytics({ recordedPoints: recorded2 }),
	});
	await onRequestPost({ request: makeRequest({ query: 'second query' }, { ip: '40.40.40.40' }), env: env2 });

	assert.equal(recorded1[0].indexes[0], recorded2[0].indexes[0], '同一个 IP + 同一把密钥，两次请求应该算出同一个哈希');
});

test('搜索统计（FU-25）：不同 IP 算出不同哈希', async () => {
	const recordedPoints = [];
	const env = await makeEnv({
		VECTORIZE_INDEX: makeFakeVectorize({ matches: [makeMatch('article-a', 0.7)] }),
		SEARCH_ANALYTICS: makeFakeAnalytics({ recordedPoints }),
	});
	await onRequestPost({ request: makeRequest({ query: 'q1' }, { ip: '41.41.41.41' }), env });
	await onRequestPost({ request: makeRequest({ query: 'q2' }, { ip: '42.42.42.42' }), env });
	assert.equal(recordedPoints.length, 2);
	assert.notEqual(recordedPoints[0].indexes[0], recordedPoints[1].indexes[0]);
});

test('搜索统计（FU-25）：BLOG_SEARCH_SESSION_SECRET 未配置时，index1 是空字符串，不退化成弱哈希/明文', async () => {
	const recordedPoints = [];
	const env = await makeEnv({
		VECTORIZE_INDEX: makeFakeVectorize({ matches: [makeMatch('article-a', 0.7)] }),
		SEARCH_ANALYTICS: makeFakeAnalytics({ recordedPoints }),
		BLOG_SEARCH_SESSION_SECRET: undefined,
	});
	const resp = await onRequestPost({ request: makeRequest({ query: 'Pagefind' }, { ip: '43.43.43.43' }), env });
	assert.equal(resp.status, 200, 'secret 缺失不该影响搜索请求本身');
	assert.equal(recordedPoints.length, 1);
	assert.deepEqual(recordedPoints[0].indexes, ['']);
});

test('搜索统计：缓存命中也会写一条数据点，cacheHit 标记为 1', async () => {
	const recordedPoints = [];
	const kv = makeFakeKv();
	const matches = [makeMatch('article-a', 0.7)];
	const workingEnv = await makeEnv({ BLOG_SEARCH_KV: kv, VECTORIZE_INDEX: makeFakeVectorize({ matches }) });
	await onRequestPost({ request: makeRequest({ query: 'Pagefind' }, { ip: '31.31.31.31' }), env: workingEnv });

	const envWithAnalytics = await makeEnv({ BLOG_SEARCH_KV: kv, SEARCH_ANALYTICS: makeFakeAnalytics({ recordedPoints }) });
	const resp = await onRequestPost({ request: makeRequest({ query: 'Pagefind' }, { ip: '32.32.32.32' }), env: envWithAnalytics });
	assert.equal(resp.status, 200);
	assert.equal(recordedPoints.length, 1);
	assert.deepEqual(recordedPoints[0].doubles, [1, 1], 'cacheHit 标记=1（命中缓存）');
});

test('搜索统计：SEARCH_ANALYTICS 绑定缺失时不影响搜索本身正常返回', async () => {
	const env = await makeEnv({ VECTORIZE_INDEX: makeFakeVectorize({ matches: [makeMatch('article-a', 0.7)] }) });
	// 故意不设置 env.SEARCH_ANALYTICS —— 模拟绑定还没配置好/部署滞后的情况
	const resp = await onRequestPost({ request: makeRequest({ query: 'Pagefind' }, { ip: '33.33.33.33' }), env });
	assert.equal(resp.status, 200, '统计功能是运营可视化数据，不是安全控制，缺失不应该 fail-closed');
});

test('搜索统计：writeDataPoint 抛异常时不影响搜索本身正常返回', async () => {
	const env = await makeEnv({
		VECTORIZE_INDEX: makeFakeVectorize({ matches: [makeMatch('article-a', 0.7)] }),
		SEARCH_ANALYTICS: makeFakeAnalytics({ shouldThrow: true }),
	});
	const resp = await onRequestPost({ request: makeRequest({ query: 'Pagefind' }, { ip: '34.34.34.34' }), env });
	assert.equal(resp.status, 200, '统计写入失败不应该让整个搜索请求跟着报错');
	const body = await resp.json();
	assert.ok(Array.isArray(body.results));
});

test('GET 请求：405', async () => {
	const resp = await onRequestGet();
	assert.equal(resp.status, 405);
});
