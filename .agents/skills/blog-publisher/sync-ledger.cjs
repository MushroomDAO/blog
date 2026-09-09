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
 *   node sync-ledger.cjs export   # 本机 MemPalace → 仓库账本（发布后跑）
 *   node sync-ledger.cjs status   # 看两边差多少
 */

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const REPO = path.resolve(__dirname, '../../..');
const LEDGER = path.join(REPO, '.agents/skills/blog-publisher/published-ledger.jsonl');
const DB = path.join(process.env.HOME || '', '.mempalace/palace/chroma.sqlite3');

function readPalace() {
  if (!fs.existsSync(DB)) return [];
  const out = execFileSync(
    'sqlite3',
    [DB, "SELECT replace(replace(c0, char(10), ' '), char(9), ' ') FROM embedding_fulltext_search_content;"],
    { encoding: 'utf8', maxBuffer: 128 * 1024 * 1024 }
  );
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

if (cmd === 'export') {
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
