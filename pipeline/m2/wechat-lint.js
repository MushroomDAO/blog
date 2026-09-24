#!/usr/bin/env node
// 公众号搜一搜规则检查（规则来源见 docs/WECHAT-SOUSOU-RULES.md）。
// index.js 渲染前调用它打警告；scripts/publish-blog.sh 发布前调用它做闸门。
//
// 硬性（error）：wechatTitle / wechatDigest 缺失或超长。只对 ENFORCE_FROM 之后的
// 文章生效——旧文不补字段，重发旧文时只打警告，走 title/description 兜底。
// 软性（warning）：加粗过多、标题像标题党/堆关键词。只提醒，不拦。
const fs = require('fs');
const yaml = require('js-yaml');

const TITLE_MAX = 30;
// 摘要不填时微信默认抓正文前 54 字，这里按同样长度约束手写摘要
const DIGEST_MAX = 54;
const BOLD_PER_1000 = 3;
const BOLD_TOTAL_MAX = 12;
const ENFORCE_FROM = new Date('2026-09-25');
const CLICKBAIT = ['震惊', '炸裂', '重磅', '王炸', '封神', '颠覆', '杀疯', '看完', '必看', '速看', '绝了', '！！', '？？'];

function parse(markdown) {
  const m = markdown.match(/^---\s*\n([\s\S]*?)\n---\s*\n/);
  const frontmatter = m ? yaml.load(m[1]) || {} : {};
  let body = m ? markdown.slice(m[0].length) : markdown;
  const en = body.indexOf('<!--EN-->');
  if (en >= 0) body = body.slice(0, en);
  return { frontmatter, body };
}

// 按字符数算（中英文都算 1），和公众号后台的计数方式一致
const len = (s) => [...String(s || '')].length;

// 没写 wechatDigest 时的兜底：在句末标点处截，不在半句话中间切
function fallbackDigest(description) {
  const chars = [...String(description || '')];
  if (chars.length <= DIGEST_MAX) return chars.join('');
  const head = chars.slice(0, DIGEST_MAX).join('');
  const cut = Math.max(...['。', '！', '？', '；'].map((p) => head.lastIndexOf(p)));
  return cut >= 10 ? head.slice(0, cut + 1) : head.replace(/[，、：,:\s]*$/, '') + '…';
}

function lint(markdown) {
  const { frontmatter: fm, body } = parse(markdown);
  const errors = [];
  const warnings = [];
  const pub = fm.pubDate ? new Date(fm.pubDate) : new Date();
  const enforce = !(pub < ENFORCE_FROM);
  const report = (msg) => (enforce ? errors : warnings).push(msg);

  const title = fm.wechatTitle || fm.title || '';
  if (!fm.wechatTitle) report(`缺少 wechatTitle（≤${TITLE_MAX} 字，实体名 + 一句核心结论）`);
  else if (len(fm.wechatTitle) > TITLE_MAX) report(`wechatTitle ${len(fm.wechatTitle)} 字，超过 ${TITLE_MAX}：${fm.wechatTitle}`);

  if (!fm.wechatDigest) report(`缺少 wechatDigest（≤${DIGEST_MAX} 字，一句完整的话）`);
  else if (len(fm.wechatDigest) > DIGEST_MAX) report(`wechatDigest ${len(fm.wechatDigest)} 字，超过 ${DIGEST_MAX}：${fm.wechatDigest}`);

  const bait = CLICKBAIT.filter((w) => title.includes(w));
  if (bait.length) warnings.push(`标题含标题党用词：${bait.join(' ')}`);
  // 「A：B，C，D」这种三段以上的堆叠式标题
  if (title.split(/[，,：:｜|、；;—]+/).filter(Boolean).length >= 4) warnings.push(`标题分段过多，像在堆关键词：${title}`);

  const prose = body.replace(/```[\s\S]*?```/g, '');
  const bold = (prose.match(/\*\*[^*\n]+\*\*/g) || []).length;
  const chars = prose.replace(/\s/g, '').length || 1;
  const perK = (bold * 1000) / chars;
  if (bold > BOLD_TOTAL_MAX || perK > BOLD_PER_1000) {
    warnings.push(`加粗 ${bold} 处（${perK.toFixed(1)}/千字），建议每个 H2 小节最多 1 处、全文 ≤${BOLD_TOTAL_MAX}`);
  }

  return {
    errors,
    warnings,
    title,
    digest: fm.wechatDigest || fallbackDigest(fm.description),
  };
}

module.exports = { lint, fallbackDigest, TITLE_MAX, DIGEST_MAX };

if (require.main === module) {
  const file = process.argv[2];
  if (!file) {
    console.error('usage: node wechat-lint.js <article.md>');
    process.exit(2);
  }
  const r = lint(fs.readFileSync(file, 'utf-8'));
  r.errors.forEach((e) => console.log(`  ✗ [公众号] ${e}`));
  r.warnings.forEach((w) => console.log(`  ⚠️ [公众号] ${w}`));
  if (!r.errors.length) console.log(`  ✓ 公众号标题「${r.title}」(${len(r.title)} 字)`);
  process.exit(r.errors.length ? 1 : 0);
}
