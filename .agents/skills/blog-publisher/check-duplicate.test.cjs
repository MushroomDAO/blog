const test = require('node:test');
const assert = require('node:assert/strict');
const {extractSources, salientNames} = require('./check-duplicate.cjs');

test('source URLs do not turn protocol/domain words into duplicate entities', () => {
  assert.deepEqual(salientNames('https://github.com/wheresryan22/anatomy'), []);
  assert.deepEqual(salientNames('https://huggingface.co/openbmb/MiniCPM5-2B'), []);
  assert.deepEqual(salientNames('https://example.com/any/page'), []);
});
test('qualified names keep their owner instead of matching a common word alone', () => {
  assert.deepEqual(salientNames('wheresryan22/anatomy'), ['wheresryan22/anatomy']);
  assert.deepEqual(salientNames('Loopera'), ['loopera']);
  assert.deepEqual(salientNames('MiniCPM5-2B model'), ['minicpm5-2b']);
});
test('source identities still match case, anchors and README paths', () => {
  assert.deepEqual([...extractSources('https://github.com/Loopera-ai/Loopera#readme')], ['loopera-ai/loopera']);
  assert.deepEqual([...extractSources('https://github.com/Loopera-ai/loopera/tree/main')], ['loopera-ai/loopera']);
});
