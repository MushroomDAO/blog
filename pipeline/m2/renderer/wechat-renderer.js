const { marked } = require('marked');
const yaml = require('js-yaml');
const fs = require('fs');
const path = require('path');

// 微信兼容的主题样式
const THEMES = {
  claude: {
    name: 'Claude',
    primary: '#D97757',
    bgLight: '#FFF5F0',
    bgGray: '#FAF9F7',
    text: '#2D2D2D',
    codeBg: '#2D2D2D',
    codeText: '#E8E8E8'
  },
  chengyun: {
    name: '橙韵',
    primary: '#fb923c',
    bgLight: '#fff7ed',
    bgGray: '#fafaf9',
    text: '#292524',
    codeBg: '#1c1917',
    codeText: '#fafaf9'
  },
  blue: {
    name: '蓝色专业',
    primary: '#2563eb',
    bgLight: '#eff6ff',
    bgGray: '#f8fafc',
    text: '#0f172a',
    codeBg: '#0f172a',
    codeText: '#f8fafc'
  },
  sticker: {
    name: '贴纸',
    primary: '#D97757',
    bgLight: '#FFF5F0',
    bgGray: '#FAF9F7',
    text: '#2D2D2D',
    codeBg: '#2D2D2D',
    codeText: '#E8E8E8'
  }
};

/**
 * 微信兼容的 marked renderer
 */
function createWeChatRenderer(themeName = 'claude') {
  const theme = THEMES[themeName] || THEMES.claude;
  const renderer = new marked.Renderer();
  
  // H1: 居中
  renderer.heading = (text, level) => {
    if (level === 1) {
      return `<h1 style="font-size:22px;font-weight:bold;color:#1A1A1A;margin-bottom:30px;text-align:center;line-height:1.4;">${text}</h1>`;
    }
    if (level === 2) {
      return `<h2 style="font-size:20px;font-weight:bold;color:#1A1A1A;margin-top:40px;margin-bottom:20px;padding-left:12px;padding-bottom:8px;border-left:4px solid ${theme.primary};border-bottom:1px dashed ${theme.primary};">${text}</h2>`;
    }
    return `<h3 style="font-size:18px;font-weight:bold;color:${theme.text};margin-top:30px;margin-bottom:16px;">${text}</h3>`;
  };
  
  // 段落
  renderer.paragraph = (text) => {
    return `<p style="font-size:16px;line-height:1.8;color:${theme.text};margin:16px 0;">${text}</p>`;
  };
  
  // 引用块
  renderer.blockquote = (quote) => {
    return `<blockquote style="margin:20px 0;padding:16px 20px;background:${theme.bgLight};border-left:4px solid ${theme.primary};border-radius:0 8px 8px 0;color:${theme.text};font-size:16px;line-height:1.7;">${quote}</blockquote>`;
  };
  
  // 列表
  renderer.list = (body, ordered) => {
    const tag = ordered ? 'ol' : 'ul';
    const style = ordered 
      ? `margin:16px 0;padding-left:24px;color:${theme.text};`
      : `margin:16px 0;padding-left:24px;color:${theme.text};list-style-type:disc;`;
    return `<${tag} style="${style}">${body}</${tag}>`;
  };
  
  renderer.listitem = (text) => {
    return `<li style="margin:8px 0;line-height:1.8;">${text}</li>`;
  };
  
  // 代码块 - 微信用 table 包裹
  renderer.code = (code, language) => {
    const lines = code.split('\n').map(line => 
      `<tr><td style="padding:4px 12px;font-family:'Courier New',monospace;font-size:14px;line-height:1.6;color:${theme.codeText};white-space:pre;">${line.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</td></tr>`
    ).join('');
    
    return `<table style="width:100%;margin:20px 0;background:${theme.codeBg};border-radius:8px;overflow:hidden;"><tbody>${lines}</tbody></table>`;
  };
  
  // 行内代码
  renderer.codespan = (code) => {
    return `<code style="background:${theme.bgGray};padding:2px 6px;border-radius:4px;font-family:'Courier New',monospace;font-size:14px;color:${theme.primary};">${code}</code>`;
  };
  
  // 粗体
  renderer.strong = (text) => {
    return `<strong style="color:${theme.primary};font-weight:bold;">${text}</strong>`;
  };
  
  // 链接
  renderer.link = (href, title, text) => {
    return `<a href="${href}" style="color:${theme.primary};text-decoration:none;">${text}</a>`;
  };
  
  // 图片 - 微信用 table 包裹
  renderer.image = (href, title, text) => {
    // 微信图片占位符
    if (href.includes('WECHATIMGPH')) {
      return `<table style="width:100%;margin:20px 0;border-collapse:collapse;"><tbody><tr><td style="padding:40px;text-align:center;background:${theme.bgLight};border-radius:8px;color:#999;font-size:14px;">${href}</td></tr></tbody></table>`;
    }
    return `<table style="width:100%;margin:20px 0;border-collapse:collapse;"><tbody><tr><td style="text-align:center;"><img src="${href}" alt="${text}" style="max-width:100%;border-radius:8px;"></td></tr></tbody></table>`;
  };
  
  // 表格
  renderer.table = (header, body) => {
    return `<table style="width:100%;border-collapse:collapse;margin:20px 0;font-size:16px;"><thead style="background:${theme.bgGray};">${header}</thead><tbody>${body}</tbody></table>`;
  };
  
  renderer.tablerow = (content) => {
    return `<tr>${content}</tr>`;
  };
  
  renderer.tablecell = (content, flags) => {
    if (flags.header) {
      return `<th style="padding:12px;text-align:left;border-bottom:2px solid ${theme.primary};font-weight:bold;color:${theme.text};">${content}</th>`;
    }
    return `<td style="padding:10px 12px;border-bottom:1px solid #eee;color:${theme.text};">${content}</td>`;
  };
  
  // 分隔线
  renderer.hr = () => {
    return '<hr style="border:none;border-top:1px dashed #ddd;margin:30px 0;">';
  };
  
  return renderer;
}

/**
 * 渲染 Markdown 为微信 HTML
 */
function render(markdown, themeName = 'claude') {
  const theme = THEMES[themeName] || THEMES.claude;
  
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
  
  // 配置 marked
  const renderer = createWeChatRenderer(themeName);
  marked.setOptions({
    renderer,
    gfm: true,
    breaks: false,
    headerIds: false,
    mangle: false
  });
  
  // 渲染内容
  let html = marked.parse(content);
  
  // 包裹外层容器
  html = `<section style="background:rgba(0,0,0,0.02);border-radius:12px;padding:20px;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif;">${html}</section>`;
  
  return {
    frontmatter,
    html,
    title: frontmatter.title || 'Untitled',
    theme: themeName
  };
}

module.exports = { render, THEMES };
