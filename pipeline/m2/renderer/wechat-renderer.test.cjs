const test = require('node:test');
const assert = require('node:assert/strict');
const { render } = require('./wechat-renderer');

test('inline code preserves HTML-like paths without emitting style tags', async () => {
  const { html } = await render('Path: `styles/<style>/STYLE.md`\n\nEnd of article.', 'blue');
  assert.ok(html.includes('styles/&lt;style&gt;/STYLE.md'));
  assert.ok(!html.includes('<style>'));
  assert.ok(html.includes('End of article.'));
});

test('inline and fenced code preserve literal entities and ampersands', async () => {
  const { html } = await render('`&lt;tag&gt; & value`\n\n```text\n&lt;tag&gt; & value\n```', 'blue');
  assert.equal((html.match(/&amp;lt;tag&amp;gt; &amp; value/g) || []).length, 2);
});
