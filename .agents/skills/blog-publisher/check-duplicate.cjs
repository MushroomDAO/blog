#!/usr/bin/env node
/**
 * 发布前查重 —— 在写稿之前跑，不是在发布之后跑。
 *
 * 为什么需要它：2026-09-09 出过一次重复发布。MiniCPM5-2B 在 09-08 已经作为
 * 「MiniCPM5 + Meshy」发过公众号草稿，但那次 blog 那一步失败了，所以
 * src/content/blog/ 里没有留下任何痕迹。第二天 forage 评审台把同一个 HuggingFace
 * 条目又标成 write，而查重只看了 blog 目录 —— 于是同一批事实被写了两遍。
 *
 * 教训：blog 目录不是「已发布」的唯一账本。公众号草稿箱是独立的一本账，
 * 两边都要查，而且要按「一手源 URL」查，不能只按标题查（同一个仓库可以有
 * 完全不同的标题）。
 *
 * 用法：
 *   node .agents/skills/blog-publisher/check-duplicate.cjs <一手源URL或关键词> [更多...]
 *
 * 退出码：0 = 没查到重复；1 = 查到疑似重复（人工确认后再决定写不写）
 */

const fs = require('fs');
const path = require('path');

const REPO = path.resolve(__dirname, '../../..');
const BLOG_DIR = path.join(REPO, 'src/content/blog');
const M2 = path.join(REPO, 'pipeline/m2');

// ── 归一化：把一手源 URL 压成可比较的身份 ────────────────────────
// https://github.com/Owner/Repo/ 、http://github.com/owner/repo 、
// github.com/Owner/Repo#readme 都应该判为同一个东西
function normalize(s) {
  return String(s)
    .toLowerCase()
    .replace(/^https?:\/\//, '')
    .replace(/^www\./, '')
    .replace(/[#?].*$/, '')
    .replace(/\/+$/, '')
    .trim();
}

// 从一段文本里抽出所有 github/huggingface/arxiv 源标识
function extractSources(text) {
  const out = new Set();
  const patterns = [
    /(?:https?:\/\/)?(?:www\.)?github\.com\/([\w.-]+\/[\w.-]+)/gi,
    /(?:https?:\/\/)?(?:www\.)?huggingface\.co\/(?:models\/)?([\w.-]+\/[\w.-]+)/gi,
    /arxiv[:\s/]+(\d{4}\.\d{4,5})/gi,
  ];
  for (const re of patterns) {
    let m;
    while ((m = re.exec(text)) !== null) out.add(normalize(m[1]));
  }
  return out;
}

// 显著实体名：像 minicpm5 / goinfer / qwen3 这种，一旦在别处正文出现过，
// 基本就是同一个选题。纯标题相似度抓不到这种 —— 09-08 那篇
// 「MiniCPM5 + Meshy：…双开」和「2B 打赢 4B：…MiniCPM5-2B…」词面相似度只有
// 个位数，但正文讲的是同一个模型。所以必须扫正文，不能只扫标题。
function salientNames(s) {
  return [...new Set(
    String(s)
      .toLowerCase()
      .split(/[^a-z0-9.-]+/)
      .map((w) => w.replace(/^[.-]+|[.-]+$/g, ''))
      // 至少 5 个字符、且带数字或连字符 —— 过滤掉 model/local/open 这类通用词
      .filter((w) => w.length >= 5 && /[0-9-]/.test(w))
      // 纯版本号/纯数字没有区分度
      .filter((w) => !/^[0-9.]+$/.test(w))
  )];
}

// URL 骨架词：任何一条带链接的记录都有它们，算进相似度只会制造噪声
const STOP = new Set([
  'https', 'http', 'www', 'com', 'org', 'io', 'co', 'net',
  'github', 'huggingface', 'arxiv', 'blog', 'mushroom', 'cv',
  'md', 'readme', 'main', 'tree', 'blob',
]);

// 中英文都能用的粗粒度关键词切分
function tokens(s) {
  return new Set(
    String(s)
      .toLowerCase()
      .replace(/[^\w一-鿿]+/g, ' ')
      .split(/\s+/)
      .filter((w) => w.length >= 2 && !STOP.has(w))
  );
}

function jaccard(a, b) {
  if (!a.size || !b.size) return 0;
  let inter = 0;
  for (const x of a) if (b.has(x)) inter++;
  return inter / (a.size + b.size - inter);
}

// ── 账本 1：blog 已有文章 ────────────────────────────────────────
function loadBlogEntries() {
  return fs
    .readdirSync(BLOG_DIR)
    .filter((f) => /\.mdx?$/.test(f))
    .map((f) => {
      const raw = fs.readFileSync(path.join(BLOG_DIR, f), 'utf8');
      const title = (raw.match(/^title:\s*"(.*)"/m) || [])[1] || f;
      return { where: 'blog', id: f.replace(/\.mdx?$/, ''), title, sources: extractSources(raw), text: raw.toLowerCase() };
    });
}

// ── 账本 2：公众号草稿箱（远程，权威）─────────────────────────────
// blog 那一步失败过、也可能以后再失败，所以草稿箱必须直接问微信，
// 不能只信 pipeline/m2/output/ 的本地记录 —— 那份记录只有本机跑过的才有。
async function loadWeChatDrafts() {
  let WeChatClient, axios;
  try {
    ({ WeChatClient } = require(path.join(M2, 'wechat-api/client.js')));
    axios = require(path.join(M2, 'node_modules/axios'));
  } catch (e) {
    return { error: `无法加载微信客户端：${e.message}` };
  }
  const { WECHAT_APP_ID, WECHAT_APP_SECRET } = process.env;
  if (!WECHAT_APP_ID || !WECHAT_APP_SECRET) {
    return { error: '缺少 WECHAT_APP_ID / WECHAT_APP_SECRET（先 source .env）' };
  }
  const c = new WeChatClient(WECHAT_APP_ID, WECHAT_APP_SECRET);
  const token = await c.getAccessToken();
  const items = [];
  const errors = [];

  // 两个端点都要查：
  //   draft/batchget       —— 还没群发的草稿
  //   freepublish/batchget —— 已经群发出去的（草稿群发后就从上面那个消失）
  // 只查草稿箱的话，历史文章一篇都查不到 —— 实测草稿数会从 11 掉到 6，
  // 掉下去的那 5 条不是不存在了，是已经发出去了。
  for (const ep of ['draft', 'freepublish']) {
    for (let offset = 0; ; offset += 20) {
      let data;
      try {
        ({ data } = await axios.post(
          `https://api.weixin.qq.com/cgi-bin/${ep}/batchget?access_token=${token}`,
          { offset, count: 20, no_content: 0 }
        ));
      } catch (e) {
        errors.push(`${ep}: ${e.message}`);
        break;
      }
      if (data.errcode) {
        errors.push(`${ep}: ${data.errcode} ${data.errmsg}`);
        break;
      }
      const batch = data.item || [];
      for (const it of batch) {
        // freepublish 的结构多一层 content.news_item，字段名也不同
        const news = (it.content && it.content.news_item) || [];
        for (const a of news) {
          const body = `${a.title || ''} ${a.digest || ''} ${a.content || ''}`;
          items.push({
            where: ep === 'draft' ? 'wechat' : 'wechat-pub',
            id: it.media_id || it.article_id || '',
            title: a.title || '(无标题)',
            date: it.content.update_time
              ? new Date(it.content.update_time * 1000).toISOString().slice(0, 10)
              : '',
            sources: extractSources(body),
            text: body.replace(/<[^>]+>/g, ' ').toLowerCase(),
          });
        }
      }
      if (batch.length < 20) break;
    }
  }
  return { items, error: errors.length ? errors.join('; ') : undefined };
}


// ── 账本 3：本地公众号发布记录 ─────────────────────────────────
// pipeline/m2/output/<slug>.json —— 每成功建一次草稿就落一条，
// 用户发布后手工删草稿箱不会动它，所以它记得住「发过什么」，
// 而草稿箱只记得「还没发什么」。局限：被 gitignore，只在本机；
// 别的机器跑的那次（比如 09-08 的 MiniCPM5+Meshy）这里也没有。
const M2_OUTPUT = path.join(M2, 'output');

function loadM2Output() {
  if (!fs.existsSync(M2_OUTPUT)) return { items: [] };
  const items = [];
  for (const f of fs.readdirSync(M2_OUTPUT)) {
    if (!f.endsWith('.json')) continue;
    try {
      const j = JSON.parse(fs.readFileSync(path.join(M2_OUTPUT, f), 'utf8'));
      const slug = f.replace(/\.json$/, '');
      const body = `${slug} ${j.title || ''} ${j.digest || ''}`;
      items.push({
        where: 'm2log',
        id: slug,
        title: j.title || slug,
        date: (j.publishedAt || '').slice(0, 10),
        sources: extractSources(body),
        text: body.toLowerCase(),
      });
    } catch (e) {
      /* 单个坏文件不该让整次查重失败 */
    }
  }
  return { items };
}

// ── 账本 4：MemPalace（知识库）─────────────────────────────────
// mempalace 本来就是设计成发布账本的 —— 老条目都带着「已发布：<blog URL>
// 公众号草稿已发」。但 2026-09 这批选题一条都没入库，账本断更了，
// 于是它对查重完全没起作用。直读 chroma 的全文表，不依赖 MCP。
const { execFileSync } = require('child_process');
const MEMPALACE_DB = path.join(
  process.env.HOME || '',
  '.mempalace/palace/chroma.sqlite3'
);

function loadMemPalace() {
  if (!fs.existsSync(MEMPALACE_DB)) return { error: `找不到 ${MEMPALACE_DB}` };
  try {
    const out = execFileSync(
      'sqlite3',
      [MEMPALACE_DB, "SELECT replace(replace(c0, char(10), ' '), char(9), ' ') FROM embedding_fulltext_search_content;"],
      { encoding: 'utf8', maxBuffer: 128 * 1024 * 1024 }
    );
    const items = out
      .split('\n')
      .filter((l) => l.trim())
      .map((line, i) => ({
        where: 'mempalace',
        id: `drawer-${i}`,
        title: line.slice(0, 60).trim(),
        text: line.toLowerCase(),
        sources: extractSources(line),
      }));
    return { items };
  } catch (e) {
    return { error: `读 mempalace 失败：${e.message}` };
  }
}

// ── 主流程 ──────────────────────────────────────────────────────
(async () => {
  const args = process.argv.slice(2);
  if (!args.length) {
    console.error('用法: node check-duplicate.cjs <一手源URL或关键词> [更多...]');
    process.exit(2);
  }

  const queries = args.map((a) => ({
    raw: a,
    sources: extractSources(a),
    toks: tokens(a),
    names: salientNames(a),
  }));

  const blog = loadBlogEntries();
  const wechatResult = await loadWeChatDrafts();
  const wechat = wechatResult.items || [];
  if (wechatResult.error) {
    const onlyFreepublish =
      /freepublish/.test(wechatResult.error) && !/draft:/.test(wechatResult.error);
    if (onlyFreepublish && wechat.length) {
      // 48001 = 这个号没有「已群发列表」接口权限（订阅号常见）。草稿箱查到了，
      // 但已经群发出去的文章就查不到了 —— 那部分只能靠 MemPalace 兜底，
      // 所以「发布后入库」不是可选步骤。
      console.error(`ℹ️  已群发列表读不到（${wechatResult.error}）`);
      console.error('   草稿箱只反映「还没发的」：发布后草稿会被手工删掉，所以');
      console.error('   「草稿箱里没有」不等于「没发过」。已发的靠本地发布记录 + MemPalace 兜底。');
    } else {
      console.error(`⚠️  公众号账本没查成（${wechatResult.error}）`);
      console.error('   本次结果不完整，别当成完整查重。');
    }
  }

  const m2Result = loadM2Output();
  const m2log = m2Result.items || [];

  const mpResult = loadMemPalace();
  const mempalace = mpResult.items || [];
  if (mpResult.error) console.error(`⚠️  MemPalace 账本没查成（${mpResult.error}）`);

  const all = [...blog, ...wechat, ...m2log, ...mempalace];
  console.log(
    `账本：blog ${blog.length} 篇 + 公众号草稿箱 ${wechat.length} 条 + ` +
      `本地发布记录 ${m2log.length} 条 + MemPalace ${mempalace.length} 抽屉\n`
  );

  let hit = false;
  for (const q of queries) {
    console.log(`── 查：${q.raw}`);
    const findings = [];

    for (const e of all) {
      // 信号 1（强）：一手源完全相同 —— 同一个仓库/模型，几乎必然是同一个选题
      for (const s of q.sources) {
        if (e.sources.has(s)) {
          findings.push({ level: '重复', why: `一手源相同: ${s}`, e });
        }
      }
      // 信号 2（强）：显著实体名出现在对方正文里 —— 这条才抓得住
      // 「同一个东西、完全不同标题」的情况
      for (const n of q.names) {
        if (e.text && e.text.includes(n)) {
          findings.push({ level: '重复', why: `正文出现实体名「${n}」`, e });
        }
      }
      // 信号 3（弱）：标题关键词重叠
      const sim = jaccard(q.toks, tokens(e.title));
      if (sim >= 0.3) {
        findings.push({ level: '疑似', why: `标题相似度 ${(sim * 100).toFixed(0)}%`, e });
      }
    }

    // 同一条目只报最强的那个信号
    const seen = new Map();
    for (const f of findings) {
      const k = `${f.e.where}:${f.e.id}`;
      if (!seen.has(k) || f.level === '重复') seen.set(k, f);
    }

    if (!seen.size) {
      console.log('   ✅ 两本账都没查到\n');
      continue;
    }
    hit = true;
    for (const f of seen.values()) {
      const tag =
        f.e.where === 'blog' ? 'BLOG  '
        : f.e.where === 'mempalace' ? '知识库'
        : f.e.where === 'wechat-pub' ? `已群发 ${f.e.date}`
        : f.e.where === 'm2log' ? `发过 ${f.e.date}`
        : `微信草稿 ${f.e.date}`;
      console.log(`   ${f.level === '重复' ? '❌' : '⚠️ '} [${tag}] ${f.e.title}`);
      console.log(`      ${f.why}`);
    }
    console.log('');
  }

  if (hit) {
    console.log('查到重复或疑似重复 —— 先人工确认再决定写不写。');
    console.log('注意：');
    console.log('  · 公众号/发过记录有、blog 没有 ＝ 上次 blog 那步失败了，应该补发 blog 而不是重写。');
    console.log('  · 三本账不一致本身就是信号，说明上次的发布流程中途断了，先把断的那段补上。');
    process.exit(1);
  }
  process.exit(0);
})();
