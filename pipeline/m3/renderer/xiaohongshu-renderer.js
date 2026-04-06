#!/usr/bin/env node
const { marked } = require('marked');
const yaml = require('js-yaml');
const { THEMES, getRandomTheme } = require('./themes');

function cleanTitle(title) {
  if (!title) return '分享';
  return title.replace(/^title\s*[:：]\s*/i, '').trim();
}

function generateFooterBanner(theme) {
  return `
<div style="margin-top:30px;padding:20px;background:${theme.gradient};border-radius:12px;text-align:center;color:${theme.colors.text};">
  <div style="font-size:20px;margin-bottom:6px;">🍄</div>
  <div style="font-size:15px;font-weight:bold;margin-bottom:6px;">Mushroom</div>
  <div style="font-size:12px;opacity:0.9;line-height:1.5;">
    <span style="margin:0 3px;">🪵 Infras</span>
    <span style="opacity:0.5;">|</span>
    <span style="margin:0 3px;">🦠 Protocols</span>
    <span style="opacity:0.5;">|</span>
    <span style="margin:0 3px;">🕸️ Networks</span>
  </div>
  <div style="margin-top:10px;padding-top:10px;border-top:1px solid rgba(0,0,0,0.1);font-size:11px;opacity:0.8;">
    📍 blog.mushroom.cv | XStack18
  </div>
</div>`;
}

function generateHeaderWatermark() {
  return `
<div style="text-align:center;margin-bottom:15px;padding:10px;background:#fafaf9;border-radius:8px;border:1px dashed #ddd;">
  <span style="font-size:13px;color:#888;">🍄 原文发布于 blog.mushroom.cv</span>
</div>`;
}

function render(markdown, themeName = null) {
  const selectedTheme = themeName && THEMES[themeName] ? themeName : getRandomTheme();
  const theme = THEMES[selectedTheme];
  
  console.log(`Using theme: ${theme.name} (${selectedTheme})`);
  
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
  
  const cleanedTitle = cleanTitle(frontmatter.title);
  
  const renderer = {
    heading(token) {
      const text = this.parser.parseInline(token.tokens);
      const level = token.depth;
      
      if (level === 1) {
        return `<h1 style="font-size:20px;font-weight:bold;color:${theme.colors.text};margin-bottom:20px;text-align:center;line-height:1.4;">${text}</h1>`;
      }
      if (level === 2) {
        return `<h2 style="font-size:17px;font-weight:bold;color:${theme.colors.text};margin-top:25px;margin-bottom:12px;padding-left:10px;border-left:3px solid ${theme.colors.primary};">${text}</h2>`;
      }
      return `<h3 style="font-size:15px;font-weight:bold;color:${theme.colors.text};margin-top:18px;margin-bottom:10px;">${text}</h3>`;
    },
    
    paragraph(token) {
      const text = this.parser.parseInline(token.tokens);
      return `<p style="font-size:15px;line-height:1.8;color:${theme.colors.text};margin:12px 0;">${text}</p>`;
    },
    
    blockquote(token) {
      const text = this.parser.parse(token.tokens);
      return `<blockquote style="margin:15px 0;padding:12px 15px;background:${theme.colors.bgLight};border-left:3px solid ${theme.colors.primary};border-radius:0 8px 8px 0;color:${theme.colors.text};font-size:14px;line-height:1.6;">${text}</blockquote>`;
    },
    
    list(token) {
      const items = token.items.map(item => {
        const text = this.parser.parse(item.tokens);
        return `<li style="margin:6px 0;line-height:1.7;">${text}</li>`;
      }).join('');
      
      if (token.ordered) {
        return `<ol style="margin:12px 0;padding-left:20px;color:${theme.colors.text};">${items}</ol>`;
      }
      return `<ul style="margin:12px 0;padding-left:20px;color:${theme.colors.text};list-style-type:disc;">${items}</ul>`;
    },
    
    code(token) {
      const code = token.text;
      const preview = code.length > 100 ? code.substring(0, 100) + '...' : code;
      return `<div style="margin:15px 0;padding:12px;background:${theme.colors.bgGray};border-radius:8px;font-family:monospace;font-size:12px;color:${theme.colors.text};overflow-x:auto;"><code>${preview.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></div>`;
    },
    
    codespan(token) {
      return `<code style="background:${theme.colors.bgGray};padding:2px 6px;border-radius:4px;font-family:monospace;font-size:13px;color:${theme.colors.primary};">${token.text}</code>`;
    },
    
    strong(token) {
      const text = this.parser.parseInline(token.tokens);
      return `<strong style="color:${theme.colors.primary};font-weight:bold;">${text}</strong>`;
    },
    
    em(token) {
      const text = this.parser.parseInline(token.tokens);
      return `<em style="color:${theme.colors.textLight};">${text}</em>`;
    },
    
    link(token) {
      const text = this.parser.parseInline(token.tokens);
      return `<span style="color:${theme.colors.primary};text-decoration:underline;">${text}</span>`;
    },
    
    image(token) {
      return `<div style="margin:15px 0;text-align:center;"><img src="${token.href}" alt="${token.text}" style="max-width:100%;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);"></div>`;
    },
    
    table(token) {
      const header = token.header.map(cell => {
        const text = this.parser.parseInline(cell.tokens);
        return `<th style="padding:10px;text-align:left;border-bottom:2px solid ${theme.colors.primary};font-weight:bold;color:${theme.colors.text};background:${theme.colors.bgGray};">${text}</th>`;
      }).join('');
      
      const body = token.rows.map((row) => {
        const cells = row.map(cell => {
          const text = this.parser.parseInline(cell.tokens);
          return `<td style="padding:8px 10px;border-bottom:1px solid #eee;color:${theme.colors.text};">${text}</td>`;
        }).join('');
        return `<tr>${cells}</tr>`;
      }).join('');
      
      return `<div style="overflow-x:auto;margin:15px 0;"><table style="width:100%;border-collapse:collapse;font-size:14px;"><thead><tr>${header}</tr></thead><tbody>${body}</tbody></table></div>`;
    },
    
    hr() {
      return `<div style="text-align:center;margin:20px 0;color:${theme.colors.primary};">✦ ✦ ✦</div>`;
    },
    
    text(token) {
      return token.text;
    }
  };
  
  marked.use({ renderer });
  
  let html = marked.parse(content);
  
  const headerWatermark = generateHeaderWatermark();
  const footerBanner = generateFooterBanner(theme);
  
  html = `<section style="background:#fff;border-radius:12px;padding:15px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;">${headerWatermark}${html}${footerBanner}</section>`;
  
  return {
    frontmatter,
    html,
    title: cleanedTitle,
    theme: selectedTheme
  };
}

module.exports = {
  render,
  THEMES,
  getRandomTheme,
  cleanTitle
};
