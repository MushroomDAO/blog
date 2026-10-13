const test = require('node:test');
const assert = require('node:assert/strict');
const axios = require('axios');
const { WeChatClient } = require('./client');

const article = { title: 'Mellum', digest: 'Verified model', content: '<p>actual body</p>', thumbMediaId: 'new-cover' };
const news = { title: article.title, digest: article.digest, content: article.content, thumb_media_id: article.thumbMediaId };
const entry = (id, content = news) => ({ media_id: id, create_time: 123, content: { news_item: [content] } });

async function simulate(readLedger, run, error = Object.assign(new Error('socket hang up'), { code: 'ECONNRESET' })) {
  const saved = axios.post, calls = [];
  const client = new WeChatClient('fixture', 'fixture');
  client.accessToken = 'fixture-token'; client.tokenExpiry = Date.now() + 60000;
  axios.post = async (url, body) => {
    const endpoint = new URL(url).pathname;
    calls.push({ endpoint, body });
    if (endpoint.endsWith('/draft/add')) throw error;
    return { data: await readLedger(body.offset) };
  };
  try { await run(client, calls, error); } finally { axios.post = saved; }
}

test('a committed draft with a lost response is recovered without a second create request', async () => {
  await simulate(async () => ({ item: [entry('server-accepted')] }), async (client, calls) => {
    const result = await client.createDraft(article);
    assert.equal(result.mediaId, 'server-accepted'); assert.equal(result.recovered, true);
    assert.equal(calls.filter(x => x.endpoint.endsWith('/draft/add')).length, 1);
    assert.equal(calls.filter(x => x.endpoint.endsWith('/draft/batchget')).length, 1);
  });
});

test('a matching title with different content is not reused or blindly recreated', async () => {
  await simulate(async () => ({ item: [entry('old', { ...news, content: '<p>old body</p>' })] }), async (client, calls, error) => {
    await assert.rejects(client.createDraft(article), e => e === error);
    assert.equal(calls.filter(x => x.endpoint.endsWith('/draft/add')).length, 1);
  });
});

test('an empty server ledger preserves the original error and never retries creation', async () => {
  await simulate(async () => ({ item: [] }), async (client, calls, error) => {
    await assert.rejects(client.createDraft(article), e => e === error);
    assert.equal(calls.length, 2);
  });
});

test('ambiguous duplicate server drafts are not reported as a successful recovery', async () => {
  await simulate(async () => ({ item: [entry('one'), entry('two')] }), async (client, calls, error) => {
    await assert.rejects(client.createDraft(article), e => e === error);
    assert.equal(calls.filter(x => x.endpoint.endsWith('/draft/add')).length, 1);
  });
});

test('an unavailable draft ledger never turns uncertainty into successful creation', async () => {
  await simulate(async () => ({ errcode: 48001 }), async (client, calls, error) => {
    await assert.rejects(client.createDraft(article), e => e === error);
    assert.equal(calls.length, 2);
  });
});

test('server reconciliation paginates instead of only checking the newest page', async () => {
  await simulate(async offset => ({ item: offset === 0 ? Array.from({ length: 20 }, (_, i) => entry('other-' + i, { ...news, title: 'other' })) : [entry('second-page')] }), async (client, calls) => {
    assert.equal((await client.createDraft(article)).mediaId, 'second-page');
    assert.deepEqual(calls.slice(1).map(x => x.body.offset), [0, 20]);
  });
});

test('an explicit Tencent rejection does not use network-error reconciliation', async () => {
  await simulate(async () => { throw new Error('unexpected ledger read'); }, async (client, calls, error) => {
    await assert.rejects(client.createDraft(article), e => e === error);
    assert.equal(calls.length, 1);
  }, new Error('Create draft failed: {"errcode":40007}'));
});
