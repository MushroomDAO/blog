/**
 * Mushroom 用户配置 - 实际使用示例
 */
module.exports = {
  id: 'mushroom',
  name: 'Mushroom DAO',
  
  blog: {
    projectName: 'blog-mushroom',
    domain: 'blog.mushroom.cv',
    
    brand: {
      name: '🍄 Mushroom Research Blog',
      description: '日常科研记录与技术分享',
      twitter: '@MushroomdDAO1984',
      github: 'MushroomDAO',
    },
    
    watermark: {
      topLeft: '🍄 Mushroom Blog',
      bottomRight: 'XStack18',
    },
    
    defaultCategory: 'Tech-News',
    author: 'Mycelium',
  },
  
  wechat: {
    appId: process.env.WECHAT_APP_ID || '',
    appSecret: process.env.WECHAT_APP_SECRET || '',
    mpId: process.env.WECHAT_MP_ID || 'gh_ba9082b3a7aa',
    defaultAuthor: 'Mycelium',
    defaultTheme: 'claude',
    enableComment: true,
  },
  
  xiaohongshu: {
    mcpUrl: process.env.XHS_MCP_URL || 'http://localhost:3456',
    defaultTheme: 'blue',
    watermark: {
      topLeft: '🍄 Mushroom Blog',
      bottomRight: 'XStack18',
    },
  },
};
