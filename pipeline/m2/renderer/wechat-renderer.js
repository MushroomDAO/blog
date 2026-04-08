const { marked } = require('marked');
const yaml = require('js-yaml');
const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const os = require('os');

// 主题配置 - 扩展更多主题
const THEMES = {
  claude: {
    name: 'Claude',
    primary: '#D97757',
    bgLight: '#FFF5F0',
    bgGray: '#FAF9F7',
    text: '#2D2D2D',
    codeBg: '#2D2D2D',
    codeText: '#E8E8E8',
    gradient: 'linear-gradient(135deg, #D97757 0%, #E8A87C 100%)'
  },
  chengyun: {
    name: '橙韵',
    primary: '#fb923c',
    bgLight: '#fff7ed',
    bgGray: '#fafaf9',
    text: '#292524',
    codeBg: '#1c1917',
    codeText: '#fafaf9',
    gradient: 'linear-gradient(135deg, #fb923c 0%, #fdba74 100%)'
  },
  blue: {
    name: '蓝色专业',
    primary: '#2563eb',
    bgLight: '#eff6ff',
    bgGray: '#f8fafc',
    text: '#0f172a',
    codeBg: '#0f172a',
    codeText: '#f8fafc',
    gradient: 'linear-gradient(135deg, #2563eb 0%, #3b82f6 100%)'
  },
  sticker: {
    name: '贴纸',
    primary: '#D97757',
    bgLight: '#FFF5F0',
    bgGray: '#FAF9F7',
    text: '#2D2D2D',
    codeBg: '#2D2D2D',
    codeText: '#E8E8E8',
    gradient: 'linear-gradient(135deg, #D97757 0%, #E8A87C 100%)'
  },
  // 新增主题
  mint: {
    name: '薄荷绿',
    primary: '#10b981',
    bgLight: '#ecfdf5',
    bgGray: '#f9fafb',
    text: '#111827',
    codeBg: '#064e3b',
    codeText: '#d1fae5',
    gradient: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)'
  },
  purple: {
    name: '神秘紫',
    primary: '#7c3aed',
    bgLight: '#f5f3ff',
    bgGray: '#fafaf9',
    text: '#1f2937',
    codeBg: '#4c1d95',
    codeText: '#ede9fe',
    gradient: 'linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%)'
  },
  cyber: {
    name: '赛博朋克',
    primary: '#06b6d4',
    bgLight: '#ecfeff',
    bgGray: '#f8fafc',
    text: '#0e7490',
    codeBg: '#164e63',
    codeText: '#cffafe',
    gradient: 'linear-gradient(135deg, #06b6d4 0%, #22d3ee 100%)'
  },
  rose: {
    name: '玫瑰粉',
    primary: '#e11d48',
    bgLight: '#fff1f2',
    bgGray: '#fafaf9',
    text: '#881337',
    codeBg: '#9f1239',
    codeText: '#ffe4e6',
    gradient: 'linear-gradient(135deg, #e11d48 0%, #fb7185 100%)'
  }
};

// 获取随机主题
function getRandomTheme() {
  const themeNames = Object.keys(THEMES);
  const randomIndex = Math.floor(Math.random() * themeNames.length);
  return themeNames[randomIndex];
}

// 清理标题（去掉 title: 前缀）
function cleanTitle(title) {
  if (!title) return 'Untitled';
  // 去掉开头的 title: 或 title：
  return title.replace(/^title\s*[:：]\s*/i, '').trim();
}

// 下载外部图片
async function downloadImage(url, outputDir) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https:') ? https : http;
    const urlObj = new URL(url);
    const ext = path.extname(urlObj.pathname) || '.jpg';
    const filename = `downloaded_${Date.now()}${ext}`;
    const filepath = path.join(outputDir, filename);
    
    const file = fs.createWriteStream(filepath);
    
    client.get(url, (response) => {
      if (response.statusCode !== 200) {
        file.close();
        fs.unlinkSync(filepath);
        reject(new Error(`Download failed: ${response.statusCode}`));
        return;
      }
      
      response.pipe(file);
      
      file.on('finish', () => {
        file.close();
        resolve(filepath);
      });
      
      file.on('error', (err) => {
        file.close();
        fs.unlinkSync(filepath);
        reject(err);
      });
    }).on('error', (err) => {
      file.close();
      if (fs.existsSync(filepath)) {
        fs.unlinkSync(filepath);
      }
      reject(err);
    });
  });
}

// 生成底部 banner HTML
function generateFooterBanner(theme) {
  return `
<div style="margin-top:40px;padding:24px;background:${theme.gradient};border-radius:12px;text-align:center;color:#fff;">
  <div style="font-size:24px;margin-bottom:8px;">🍄</div>
  <div style="font-size:16px;font-weight:bold;margin-bottom:8px;">Mycelium</div>
  <div style="font-size:13px;opacity:0.95;line-height:1.6;">
    <span style="margin:0 4px;">🪵 Infras</span>
    <span style="opacity:0.6;">|</span>
    <span style="margin:0 4px;">🦠 Protocols</span>
    <span style="opacity:0.6;">|</span>
    <span style="margin:0 4px;">🕸️ Networks</span>
  </div>
  <div style="margin-top:12px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.3);font-size:12px;opacity:0.9;">
    📍 blog.mushroom.cv
  </div>
</div>
`;
}

// 生成顶部 watermark
function generateHeaderWatermark() {
  return `
<div style="text-align:center;margin-bottom:20px;padding:12px;background:#fafaf9;border-radius:8px;border:1px dashed #ddd;">
  <span style="font-size:14px;color:#666;">🍄 原文发布于 blog.mushroom.cv</span>
</div>
`;
}

/**
 * 渲染 Markdown 为微信 HTML
 */
async function render(markdown, themeName = null, wechatClient = null) {
  // 如果没有指定主题，随机选择一个
  const selectedTheme = themeName && THEMES[themeName] ? themeName : getRandomTheme();
  const theme = THEMES[selectedTheme];
  
  console.log(`Using theme: ${theme.name} (${selectedTheme})`);
  
  // 解析 frontmatter
  const frontmatterMatch = markdown.match(/^---\s*\n([\s\S]*?)\n---\s*\n/);
  let frontmatter = {};
  let content = markdown;
  
  if (frontmatterMatch) {
    try {
      frontmatter = yaml.load(frontmatterMatch[1]);
      content = markdown.slice(frontmatterMatch[0].length);
    } catch (e) {
      console.warn('Frontmatter parse error:', e.message);
    }
  }
  
  // 清理标题
  const cleanedTitle = cleanTitle(frontmatter.title);
  
  // 处理图片（外部URL和本地路径）
  if (wechatClient) {
    // 匹配所有图片：外部URL和本地路径
    const imageRegex = /!\[([^\]]*)\]\(([^\)]+)\)/g;
    const matches = [...content.matchAll(imageRegex)];
    
    // 分类处理：外部URL需要下载，本地路径直接使用
    const externalImages = [];
    const localImages = [];
    
    for (const match of matches) {
      const [fullMatch, altText, imagePath] = match;
      // 跳过已经是微信 CDN 的图片
      if (imagePath.includes('mmbiz.qpic.cn') || imagePath.includes('mmbiz.qlogo.cn')) {
        continue;
      }
      // 外部URL
      if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
        externalImages.push(match);
      } else {
        // 本地路径
        localImages.push(match);
      }
    }
    
    const totalImages = externalImages.length + localImages.length;
    if (totalImages > 0) {
      console.log(`   Found ${totalImages} image(s) to process...`);
      
      // 创建临时目录
      const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'wechat-img-'));
      
      // 处理外部图片
      for (const match of externalImages) {
        const [fullMatch, altText, imageUrl] = match;
        
        try {
          console.log(`   Downloading: ${imageUrl.substring(0, 60)}...`);
          const localPath = await downloadImage(imageUrl, tempDir);
          
          console.log(`   Uploading to WeChat...`);
          const wxUrl = await wechatClient.uploadImage(localPath);
          
          content = content.replace(fullMatch, `![${altText}](${wxUrl})`);
          console.log(`   ✅ External image processed`);
        } catch (e) {
          console.warn(`   ⚠️ Failed to process external image: ${e.message}`);
        }
      }
      
      // 处理本地图片
      for (const match of localImages) {
        const [fullMatch, altText, imagePath] = match;
        
        try {
          // 解析相对路径为绝对路径
          let absolutePath;
          if (imagePath.startsWith('../../assets/')) {
            // 从文章路径解析
            // __dirname = pipeline/m2/renderer/
            // ../../.. = 项目根目录
            absolutePath = path.join(__dirname, '../../..', 'src/assets', imagePath.replace('../../assets/', ''));
          } else if (imagePath.startsWith('/')) {
            absolutePath = imagePath;
          } else {
            absolutePath = path.resolve(imagePath);
          }
          
          if (!fs.existsSync(absolutePath)) {
            console.warn(`   ⚠️ Image not found: ${absolutePath}`);
            continue;
          }
          
          console.log(`   Uploading local image: ${path.basename(absolutePath)}...`);
          const wxUrl = await wechatClient.uploadImage(absolutePath);
          
          content = content.replace(fullMatch, `![${altText}](${wxUrl})`);
          console.log(`   ✅ Local image processed`);
        } catch (e) {
          console.warn(`   ⚠️ Failed to process local image: ${e.message}`);
        }
      }
      
      // 清理临时目录
      try {
        fs.rmSync(tempDir, { recursive: true, force: true });
      } catch (e) {
        // 忽略清理错误
      }
    }
  }
  
  // 配置 marked
  const renderer = {
    heading(token) {
      const text = this.parser.parseInline(token.tokens);
      const level = token.depth;
      
      if (level === 1) {
        return `<h1 style="font-size:22px;font-weight:bold;color:#1A1A1A;margin-bottom:30px;text-align:center;line-height:1.4;">${text}</h1>`;
      }
      if (level === 2) {
        return `<h2 style="font-size:20px;font-weight:bold;color:#1A1A1A;margin-top:40px;margin-bottom:20px;padding-left:12px;padding-bottom:8px;border-left:4px solid ${theme.primary};border-bottom:1px dashed ${theme.primary};">${text}</h2>`;
      }
      return `<h3 style="font-size:18px;font-weight:bold;color:${theme.text};margin-top:30px;margin-bottom:16px;">${text}</h3>`;
    },
    
    paragraph(token) {
      const text = this.parser.parseInline(token.tokens);
      return `<p style="font-size:16px;line-height:1.8;color:${theme.text};margin:16px 0;">${text}</p>`;
    },
    
    blockquote(token) {
      const text = this.parser.parse(token.tokens);
      return `<blockquote style="margin:20px 0;padding:16px 20px;background:${theme.bgLight};border-left:4px solid ${theme.primary};border-radius:0 8px 8px 0;color:${theme.text};font-size:16px;line-height:1.7;">${text}</blockquote>`;
    },
    
    list(token) {
      const items = token.items.map(item => {
        const text = this.parser.parse(item.tokens);
        return `<li style="margin:8px 0;line-height:1.8;">${text}</li>`;
      }).join('');
      
      if (token.ordered) {
        return `<ol style="margin:16px 0;padding-left:24px;color:${theme.text};">${items}</ol>`;
      }
      return `<ul style="margin:16px 0;padding-left:24px;color:${theme.text};list-style-type:disc;">${items}</ul>`;
    },
    
    code(token) {
      const code = token.text;
      const lines = code.split('\n').map(line => 
        `<tr><td style="padding:4px 12px;font-family:'Courier New',monospace;font-size:14px;line-height:1.6;color:${theme.codeText};white-space:pre;">${line.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</td></tr>`
      ).join('');
      
      return `<table style="width:100%;margin:20px 0;background:${theme.codeBg};border-radius:8px;overflow:hidden;"><tbody>${lines}</tbody></table>`;
    },
    
    codespan(token) {
      return `<code style="background:${theme.bgGray};padding:2px 6px;border-radius:4px;font-family:'Courier New',monospace;font-size:14px;color:${theme.primary};">${token.text}</code>`;
    },
    
    strong(token) {
      const text = this.parser.parseInline(token.tokens);
      return `<strong style="color:${theme.primary};font-weight:bold;">${text}</strong>`;
    },
    
    em(token) {
      const text = this.parser.parseInline(token.tokens);
      return `<em>${text}</em>`;
    },
    
    link(token) {
      const text = this.parser.parseInline(token.tokens);
      return `<a href="${token.href}" style="color:${theme.primary};text-decoration:none;">${text}</a>`;
    },
    
    image(token) {
      // 图片已经在前面处理过了，直接渲染
      return `<table style="width:100%;margin:20px 0;border-collapse:collapse;"><tbody><tr><td style="text-align:center;"><img src="${token.href}" alt="${token.text}" style="max-width:100%;border-radius:8px;"></td></tr></tbody></table>`;
    },
    
    table(token) {
      const header = token.header.map(cell => {
        const text = this.parser.parseInline(cell.tokens);
        return `<th style="padding:12px;text-align:left;border-bottom:2px solid ${theme.primary};font-weight:bold;color:${theme.text};">${text}</th>`;
      }).join('');
      
      const body = token.rows.map((row, i) => {
        const bg = i % 2 === 0 ? 'background:#fff;' : `background:${theme.bgGray};`;
        const cells = row.map(cell => {
          const text = this.parser.parseInline(cell.tokens);
          return `<td style="padding:10px 12px;border-bottom:1px solid #eee;color:${theme.text};${bg}">${text}</td>`;
        }).join('');
        return `<tr>${cells}</tr>`;
      }).join('');
      
      return `<table style="width:100%;border-collapse:collapse;margin:20px 0;font-size:16px;"><thead style="background:${theme.bgGray};"><tr>${header}</tr></thead><tbody>${body}</tbody></table>`;
    },
    
    hr() {
      return '<hr style="border:none;border-top:1px dashed #ddd;margin:30px 0;">';
    },
    
    text(token) {
      return token.text;
    }
  };
  
  marked.use({ renderer });
  
  // 渲染
  let html = marked.parse(content);
  
  // 添加顶部 watermark
  const headerWatermark = generateHeaderWatermark();
  
  // 添加底部 banner
  const footerBanner = generateFooterBanner(theme);
  
  // 包裹外层容器
  html = `<section style="background:rgba(0,0,0,0.02);border-radius:12px;padding:20px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;">${headerWatermark}${html}${footerBanner}</section>`;
  
  return {
    frontmatter,
    html,
    title: cleanedTitle,
    theme: selectedTheme
  };
}

module.exports = { render, THEMES, getRandomTheme, cleanTitle };
