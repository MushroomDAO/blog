#!/usr/bin/env node
/**
 * MemPalace 账本导出/导入 —— 让查重能跨机器工作。
 *
 * 问题：MemPalace 的库在 ~/.mempalace/palace/chroma.sqlite3，不在仓库里。
 * 把仓库克隆到另一台机器（Mac mini）后，那台机器的 MemPalace 是空的或者
 * 内容不同，于是同一个选题在 A 机器查得到、在 B 机器查不到 —— 查重结果
 * 取决于你坐在哪台机器前面，这比没有查重更危险。
 *
 * 解法：把抽屉导出成仓库里的一个 JSONL 文本账本，跟着 git 走。
 * 查重时两边都读并合并：本机 sqlite 有最新的，仓库 JSONL 有别的机器写的。
 *
 * 不直接把 chroma.sqlite3 提交进 git 的原因：7MB 二进制，每次变更全量重写，
 * 一年下来仓库会膨胀几百 MB，而且完全没法 diff 和 review。
 *
 * 用法：
 *   node sync-ledger.cjs export   # 本机 MemPalace → 仓库账本（发布后跑，pre-commit 钩子自动跑）
 *   node sync-ledger.cjs import   # 仓库账本 → 本机 MemPalace（新机器 bootstrap 时跑）
 *   node sync-ledger.cjs status   # 看两边差多少
 *
 * 关于 import：查重本身**不需要**它 —— check-duplicate.cjs 已经同时读
 * chroma 和这份 JSONL 账本，所以另一台机器写的条目在这台机器上照样查得到。
 * import 存在的意义是让本机 palace 自己补全，这样 mempalace 的语义搜索
 * （以及 MCP 的 mempalace_search）也能命中别的机器写的内容，而不只是
 * 精确文本查重能命中。
 */

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const REPO = path.resolve(__dirname, '../../..');
const LEDGER = path.join(REPO, '.agents/skills/blog-publisher/published-ledger.jsonl');
const DB = path.join(process.env.HOME || '', '.mempalace/palace/chroma.sqlite3');

// 从账本 import 进来的抽屉，导出时必须排除掉，否则会形成无界的反馈循环：
// `mempalace mine` 会把文本重排（加 **Summary**、按 chunk 切分），哈希跟账本里
// 的原文对不上，于是这些抽屉被 status 判成「只在本机」，下次 export 又把重排版
// 灌回账本 —— 账本 369 → 1175 → 再 import → 再膨胀，没有收敛点。
// 2026-09-10 在 Mac mini 上实测到：import 199 条后 status 仍显示 199 条只在仓库，
// palace 从 5 条涨到 976 条。
// 判据用 wing：import 统一进 IMPORT_WING，真实抽屉进各自的业务 wing。
const IMPORT_WING = '_ledger-import';
// 'published' 是 2026-09-10 那次事故用的 wing，留着兼容，别再用这个名字建 wing。
const EXCLUDED_WINGS = [IMPORT_WING, 'published'];

function readPalace() {
  if (!fs.existsSync(DB)) return [];
  const notImported = EXCLUDED_WINGS.map(
    (w) => `NOT EXISTS (SELECT 1 FROM embedding_metadata m WHERE m.id = c.rowid AND m.key = 'wing' AND m.string_value = '${w}')`
  ).join(' AND ');
  const sql =
    "SELECT replace(replace(c.c0, char(10), ' '), char(9), ' ') " +
    `FROM embedding_fulltext_search_content c WHERE ${notImported};`;
  let out;
  try {
    out = execFileSync('sqlite3', [DB, sql], { encoding: 'utf8', maxBuffer: 128 * 1024 * 1024 });
  } catch {
    // 老版本 palace 可能没有 embedding_metadata 表，退回不过滤的读法
    out = execFileSync(
      'sqlite3',
      [DB, "SELECT replace(replace(c0, char(10), ' '), char(9), ' ') FROM embedding_fulltext_search_content;"],
      { encoding: 'utf8', maxBuffer: 128 * 1024 * 1024 }
    );
  }
  return out.split('\n').map((l) => l.trim()).filter(Boolean);
}

function readLedger() {
  if (!fs.existsSync(LEDGER)) return [];
  return fs
    .readFileSync(LEDGER, 'utf8')
    .split('\n')
    .filter((l) => l.trim())
    .map((l) => {
      try { return JSON.parse(l); } catch { return null; }
    })
    .filter(Boolean);
}

// 内容哈希做去重键 —— 同一条抽屉在两台机器上导出应该产生同一个 id
function hash(s) {
  let h = 0;
  for (let i = 0; i < s.length; i++) {
    h = (h * 31 + s.charCodeAt(i)) | 0;
  }
  return (h >>> 0).toString(16).padStart(8, '0');
}

const cmd = process.argv[2] || 'status';

if (cmd === 'import') {
  // 只补本机缺的那些。走 `mempalace mine` 而不是直写 chroma——
  // 直写 sqlite 会绕过向量化，条目进得去但搜不出来，比不导入更糟。
  const palace = readPalace();
  const have = new Set(palace.map(hash));
  const missing = readLedger().filter((e) => !have.has(e.h));

  if (!missing.length) {
    console.log('✅ 本机 MemPalace 已包含账本里的全部条目，无需导入。');
    process.exit(0);
  }

  const inbox = path.join(REPO, '.agents/skills/blog-publisher/.ledger-inbox');
  fs.rmSync(inbox, { recursive: true, force: true });
  fs.mkdirSync(inbox, { recursive: true });
  for (const e of missing) {
    fs.writeFileSync(path.join(inbox, `${e.h}.md`), e.text + '\n');
  }
  console.log(`账本里有 ${missing.length} 条本机没有，已摊到 ${path.relative(REPO, inbox)}/`);

  try {
    execFileSync('mempalace', ['mine', inbox, '--wing', IMPORT_WING, '--agent', 'sync-ledger', '--no-gitignore'],
      { stdio: 'inherit' });
    console.log(`✅ 导入完成：${missing.length} 条已进入本机 MemPalace（wing=${IMPORT_WING}）。`);
    console.log('   注意：mempalace mine 会重排并切分文本，所以再跑 status 仍会显示这些条目');
    console.log('   「只在仓库」—— 那是正常的，不是没导入成功。导出时它们会被排除，不会污染账本。');
    fs.rmSync(inbox, { recursive: true, force: true });
  } catch (err) {
    console.error('❌ mempalace mine 失败。可能是没装 mempalace（brew/pipx），或 palace 未 init。');
    console.error(`   摊开的文件留在 ${path.relative(REPO, inbox)}/，修好后手动跑：`);
    console.error(`   mempalace mine ${path.relative(REPO, inbox)} --wing ${IMPORT_WING} --no-gitignore`);
    console.error('   注意：查重不受影响 —— check-duplicate.cjs 直接读账本，不依赖这一步。');
    process.exit(1);
  }
} else if (cmd === 'export') {
  const palace = readPalace();
  const existing = readLedger();
  const seen = new Set(existing.map((e) => e.h));

  let added = 0;
  const lines = existing.map((e) => JSON.stringify(e));
  for (const text of palace) {
    const h = hash(text);
    if (seen.has(h)) continue;
    seen.add(h);
    lines.push(JSON.stringify({ h, text }));
    added++;
  }
  // 按哈希排序，让 diff 稳定 —— 不排序的话每次导出顺序都可能变，
  // git diff 会变成一坨看不懂的东西
  lines.sort();
  fs.writeFileSync(LEDGER, lines.join('\n') + '\n');
  const kb = (fs.statSync(LEDGER).size / 1024).toFixed(0);
  console.log(`✅ 导出完成：新增 ${added} 条，账本共 ${lines.length} 条（${kb} KB）`);
  console.log(`   ${path.relative(REPO, LEDGER)}`);
  if (added) console.log('   记得 commit —— 不提交的话另一台机器还是查不到。');
} else {
  const palace = readPalace();
  const ledger = readLedger();
  const palaceHashes = new Set(palace.map(hash));
  const ledgerHashes = new Set(ledger.map((e) => e.h));
  const onlyPalace = [...palaceHashes].filter((h) => !ledgerHashes.has(h)).length;
  const onlyLedger = [...ledgerHashes].filter((h) => !palaceHashes.has(h)).length;

  console.log(`本机 MemPalace : ${palace.length} 条`);
  console.log(`仓库账本       : ${ledger.length} 条`);
  console.log(`只在本机       : ${onlyPalace} 条${onlyPalace ? '  ← 跑 export 并提交' : ''}`);
  console.log(`只在仓库       : ${onlyLedger} 条${onlyLedger ? '  ← 别的机器写的，查重时会自动合并读到' : ''}`);
  if (!fs.existsSync(DB)) {
    console.log('\n注意：这台机器没有 MemPalace 库，查重将只依赖仓库账本。');
  }
}
