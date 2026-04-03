#!/usr/bin/env node
const { render } = require('./renderer/wechat-renderer');
const { WeChatClient } = require('./wechat-api/client');
const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

// 加载 .env
function loadEnv() {
  const envPath = path.join(__dirname, '../..', '.env');
  if (!fs.existsSync(envPath)) {
    console.error('❌ .env file not found');
    process.exit(1);
  }
  
  const env = {};
  fs.readFileSync(envPath, 'utf-8').split('\n').forEach(line => {
    const match = line.match(/^(\w+)=(.+)$/);
    if (match) {
      env[match[1]] = match[2].trim();
    }
  });
  
  return env;
}

/**
 * M2 主流程
 */
async function publish(markdownFile, options = {}) {
  const { theme = 'claude', author = 'Mycelium' } = options;
  
  console.log('🚀 M2 WeChat Publisher');
  console.log('======================\n');
  
  // 验证文件
  if (!fs.existsSync(markdownFile)) {
    console.error(`❌ File not found: ${markdownFile}`);
    process.exit(1);
  }
  
  // 加载配置
  console.log('[1/5] Loading config...');
  const env = loadEnv();
  if (!env.WECHAT_APP_ID || !env.WECHAT_APP_SECRET) {
    console.error('❌ WECHAT_APP_ID or WECHAT_APP_SECRET not found in .env');
    process.exit(1);
  }
  
  // 读取并渲染 Markdown
  console.log('[2/5] Rendering markdown...');
  const markdown = fs.readFileSync(markdownFile, 'utf-8');
  const result = render(markdown, theme);
  
  console.log(`   Title: ${result.title}`);
  console.log(`   Theme: ${theme}`);
  
  // 初始化微信客户端
  const wechat = new WeChatClient(env.WECHAT_APP_ID, env.WECHAT_APP_SECRET);
  
  // 处理封面图
  console.log('[3/5] Processing cover image...');
  let thumbMediaId = null;
  
  if (result.frontmatter.heroImage) {
    const heroPath = result.frontmatter.heroImage.replace('../../assets/', '');
    const coverPath = path.join(__dirname, '../..', 'src/assets', heroPath);
    
    if (fs.existsSync(coverPath)) {
      try {
        const cover = await wechat.uploadCover(coverPath);
        thumbMediaId = cover.mediaId;
      } catch (e) {
        console.warn(`   ⚠️ Cover upload failed: ${e.message}`);
      }
    }
  }
  
  // 发布草稿
  console.log('[4/5] Creating draft...');
  const digest = result.frontmatter.description 
    ? result.frontmatter.description.substring(0, 60) 
    : '';
  
  try {
    const draft = await wechat.createDraft({
      title: result.title,
      author: author,
      digest: digest,
      content: result.html,
      thumbMediaId: thumbMediaId,
      needOpenComment: true,
      onlyFansCanComment: false,
      declareOriginal: true
    });
    
    // 保存输出
    console.log('[5/5] Saving output...');
    const outputDir = path.join(__dirname, 'output');
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const baseName = path.basename(markdownFile, '.md');
    
    // 保存 HTML
    fs.writeFileSync(
      path.join(outputDir, `${baseName}.html`),
      result.html,
      'utf-8'
    );
    
    // 保存 manifest
    fs.writeFileSync(
      path.join(outputDir, `${baseName}.json`),
      JSON.stringify({
        title: result.title,
        author,
        digest,
        mediaId: draft.mediaId,
        theme,
        publishedAt: new Date().toISOString()
      }, null, 2),
      'utf-8'
    );
    
    console.log('\n✅ Publish successful!');
    console.log('');
    console.log('📋 Draft Info:');
    console.log(`   Title: ${result.title}`);
    console.log(`   Media ID: ${draft.mediaId}`);
    console.log(`   Preview: https://mp.weixin.qq.com`);
    console.log('');
    console.log(`📁 Output: pipeline/m2/output/${baseName}.html`);
    
    return draft;
    
  } catch (error) {
    console.error('\n❌ Publish failed:', error.message);
    process.exit(1);
  }
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length < 1) {
    console.log('M2 WeChat Publisher');
    console.log('');
    console.log('Usage: node index.js <markdown-file> [options]');
    console.log('');
    console.log('Options:');
    console.log('  --theme <name>   Theme: claude|chengyun|blue|sticker (default: claude)');
    console.log('  --author <name>  Author name (default: Mycelium)');
    console.log('');
    console.log('Example:');
    console.log('  node index.js article.md');
    console.log('  node index.js article.md --theme blue --author "Alice"');
    process.exit(1);
  }
  
  const options = { theme: 'claude', author: 'Mycelium' };
  
  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--theme' && i + 1 < args.length) {
      options.theme = args[i + 1];
      i++;
    } else if (args[i] === '--author' && i + 1 < args.length) {
      options.author = args[i + 1];
      i++;
    }
  }
  
  publish(args[0], options).catch(e => {
    console.error(e);
    process.exit(1);
  });
}

module.exports = { publish };
