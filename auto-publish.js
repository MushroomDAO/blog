#!/usr/bin/env node
/**
 * 全自动发布：Raw Text → AI润色 → 封面 → P1 Blog → P2 微信
 * Usage: node auto-publish.js "你的文章内容"
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// 模拟 AI 润色（直接生成高质量 Markdown）
function aiPolish(rawText) {
  // 提取标题（第一行或关键句）
  const lines = rawText.split('\n').filter(l => l.trim());
  const title = lines[0].replace(/[#*]/g, '').trim().substring(0, 30);
  
  // 生成英文标题
  const titleEn = title; // 简化处理
  
  // 提取描述（前100字）
  const desc = rawText.replace(/[#*\[\]]/g, '').substring(0, 80) + '...';
  
  // 检测分类
  let category = 'Tech-News';
  if (rawText.includes('实验') || rawText.includes('benchmark')) category = 'Tech-Experiment';
  if (rawText.includes('研究') || rawText.includes('论文')) category = 'Research';
  
  // 提取标签
  const tags = [];
  if (rawText.toLowerCase().includes('ai')) tags.push('ai');
  if (rawText.toLowerCase().includes('gemma') || rawText.toLowerCase().includes('llm')) tags.push('llm');
  if (rawText.toLowerCase().includes('blockchain')) tags.push('blockchain');
  if (tags.length === 0) tags.push('tech', 'news');
  
  // 格式化正文
  let content = rawText
    .replace(/^#+\s*/gm, '') // 移除原有的 markdown 标题
    .replace(/\*\*/g, '**')
    .trim();
  
  // 添加结构
  const sections = content.split('\n\n').filter(s => s.trim());
  let formatted = '';
  
  sections.forEach((section, i) => {
    if (i === 0) {
      // 第一段作为引言
      formatted += section + '\n\n';
    } else if (section.length < 50 && !section.includes('。')) {
      // 可能是小标题
      formatted += `## ${section}\n\n`;
    } else {
      formatted += section + '\n\n';
    }
  });
  
  const today = new Date().toISOString().split('T')[0];
  
  return `---
title: '${title}'
titleEn: '${titleEn}'
description: '${desc}'
descriptionEn: '${desc}'
pubDate: '${today}'
category: '${category}'
tags: ${JSON.stringify(tags)}
---

${formatted}`;
}

// 主流程
function publish(rawText) {
  console.log('🚀 Auto Publish Starting...\n');
  
  const blogRoot = __dirname;
  
  // Step 1: AI 润色
  console.log('[1/4] AI polishing...');
  const markdown = aiPolish(rawText);
  const tmpFile = '/tmp/auto-article.md';
  fs.writeFileSync(tmpFile, markdown, 'utf-8');
  console.log('   ✅ Article polished');
  
  // Step 2: 生成封面
  console.log('[2/4] Generating cover...');
  const title = markdown.match(/title:\s*'(.+?)'/)?.[1] || 'Article';
  const coverPath = execSync(
    `cd "${blogRoot}" && python3 pipeline/m1/cover_generator.py "${title}" 2>/dev/null | tail -1`,
    { encoding: 'utf-8' }
  ).trim();
  const coverName = path.basename(coverPath);
  console.log(`   ✅ Cover: ${coverName}`);
  
  // Step 3: P1 Blog
  console.log('[3/4] Publishing to Blog...');
  execSync(
    `cd "${blogRoot}" && python3 pipeline/m1/publisher.py "${tmpFile}" --images "src/assets/${coverName}"`,
    { stdio: 'inherit' }
  );
  
  // Step 4: P2 WeChat
  console.log('[4/4] Publishing to WeChat...');
  const mdFile = execSync(
    `ls -t "${blogRoot}/src/content/blog/"*.md | head -1`,
    { encoding: 'utf-8' }
  ).trim();
  
  execSync(
    `cd "${blogRoot}/pipeline/m2" && node index.js "${mdFile}" --theme claude`,
    { stdio: 'inherit' }
  );
  
  // 清理
  fs.unlinkSync(tmpFile);
  
  console.log('\n🎉 All Done!');
  console.log('   Blog: https://blog.mushroom.cv');
  console.log('   WeChat: https://mp.weixin.qq.com');
}

// CLI
const content = process.argv.slice(2).join(' ');
if (!content) {
  console.log('Usage: node auto-publish.js "你的文章内容"');
  console.log('或者从文件: node auto-publish.js "$(cat article.txt)"');
  process.exit(1);
}

publish(content);
