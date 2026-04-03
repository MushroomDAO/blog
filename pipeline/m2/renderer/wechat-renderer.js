const { marked } = require('marked');
const yaml = require('js-yaml');

// 主题配置
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
 * 渲染 Markdown 为微信 HTML
 * 使用 marked 的 walkTokens 方式
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
  
  // 扩展 marked，添加微信兼容的渲染
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
      const href = token.href;
      // 微信图片占位符
      if (href.includes('WECHATIMGPH')) {
        return `<table style="width:100%;margin:20px 0;border-collapse:collapse;"><tbody><tr><td style="padding:40px;text-align:center;background:${theme.bgLight};border-radius:8px;color:#999;font-size:14px;">${href}</td></tr></tbody></table>`;
      }
      return `<table style="width:100%;margin:20px 0;border-collapse:collapse;"><tbody><tr><td style="text-align:center;"><img src="${href}" alt="${token.text}" style="max-width:100%;border-radius:8px;"></td></tr></tbody></table>`;
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
  
  // 配置 marked
  marked.use({ renderer });
  
  // 渲染
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
