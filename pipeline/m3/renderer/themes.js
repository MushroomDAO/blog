/**
 * M3 小红书渲染主题配置
 * 6种视觉风格
 */

const THEMES = {
  fresh: {
    name: '清新绿',
    nameEn: 'fresh',
    emoji: '🌿',
    colors: {
      primary: '#10b981',
      bgLight: '#ecfdf5',
      bgGray: '#f0fdf4',
      text: '#064e3b',
      textLight: '#34d399',
      codeBg: '#064e3b',
      codeText: '#d1fae5'
    },
    gradient: 'linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)',
    style: '适合：生活方式、自然、健康、环保'
  },
  
  orange: {
    name: '活力橙',
    nameEn: 'orange',
    emoji: '🍊',
    colors: {
      primary: '#f97316',
      bgLight: '#fff7ed',
      bgGray: '#fff7ed',
      text: '#7c2d12',
      textLight: '#fdba74',
      codeBg: '#7c2d12',
      codeText: '#ffedd5'
    },
    gradient: 'linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)',
    style: '适合：美食、旅行、探店、运动'
  },
  
  pink: {
    name: '甜美粉',
    nameEn: 'pink',
    emoji: '💕',
    colors: {
      primary: '#ec4899',
      bgLight: '#fdf2f8',
      bgGray: '#fdf2f8',
      text: '#831843',
      textLight: '#f9a8d4',
      codeBg: '#831843',
      codeText: '#fce7f3'
    },
    gradient: 'linear-gradient(135deg, #fdf2f8 0%, #fce7f3 100%)',
    style: '适合：美妆、穿搭、情感、日常'
  },
  
  blue: {
    name: '专业蓝',
    nameEn: 'blue',
    emoji: '💼',
    colors: {
      primary: '#3b82f6',
      bgLight: '#eff6ff',
      bgGray: '#eff6ff',
      text: '#1e3a8a',
      textLight: '#93c5fd',
      codeBg: '#1e3a8a',
      codeText: '#dbeafe'
    },
    gradient: 'linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)',
    style: '适合：职场、学习、科技、效率'
  },
  
  purple: {
    name: '神秘紫',
    nameEn: 'purple',
    emoji: '🔮',
    colors: {
      primary: '#8b5cf6',
      bgLight: '#f5f3ff',
      bgGray: '#f5f3ff',
      text: '#4c1d95',
      textLight: '#c4b5fd',
      codeBg: '#4c1d95',
      codeText: '#ede9fe'
    },
    gradient: 'linear-gradient(135deg, #f5f3ff 0%, #ede9fe 100%)',
    style: '适合：创意、艺术、思考、深度'
  },
  
  brown: {
    name: '暖棕',
    nameEn: 'brown',
    emoji: '🍂',
    colors: {
      primary: '#a16207',
      bgLight: '#fefce8',
      bgGray: '#fefce8',
      text: '#713f12',
      textLight: '#fde047',
      codeBg: '#713f12',
      codeText: '#fef9c3'
    },
    gradient: 'linear-gradient(135deg, #fefce8 0%, #fef9c3 100%)',
    style: '适合：读书、文化、复古、历史'
  }
};

// 获取随机主题
function getRandomTheme() {
  const keys = Object.keys(THEMES);
  return keys[Math.floor(Math.random() * keys.length)];
}

// 获取所有主题名称
function getThemeNames() {
  return Object.keys(THEMES);
}

// 获取主题详情
function getTheme(name) {
  return THEMES[name] || THEMES.fresh;
}

module.exports = {
  THEMES,
  getRandomTheme,
  getThemeNames,
  getTheme
};
