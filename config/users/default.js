/**
 * 默认用户配置 - 示例模板
 * 复制此文件并重命名为你的用户名，如：mushroom.js
 */
module.exports = {
  // ==================== 用户标识 ====================
  id: 'default',
  name: 'Default User',
  
  // ==================== Blog 配置 (M1) ====================
  blog: {
    // Cloudflare Pages 配置
    projectName: 'blog-mushroom',
    domain: 'blog.mushroom.cv',
    
    // 品牌信息
    brand: {
      name: '🍄 Mushroom Research Blog',
      description: '日常科研记录与技术分享',
      twitter: '@MushroomdDAO1984',
      github: 'MushroomDAO',
    },
    
    // 封面水印
    watermark: {
      topLeft: '🍄 Mushroom Blog',
      bottomRight: 'XStack18',
    },
    
    // 默认分类
    defaultCategory: 'Tech-News',
    
    // 作者信息
    author: 'Mycelium',
  },
  
  // ==================== 微信公众号配置 (M2) ====================
  wechat: {
    // 公众号 AppID 和 Secret
    // 从 https://mp.weixin.qq.com 获取
    appId: process.env.WECHAT_APP_ID || '',
    appSecret: process.env.WECHAT_APP_SECRET || '',
    
    // 公众号 ID (gh_xxx)
    mpId: process.env.WECHAT_MP_ID || '',
    
    // 默认作者名
    defaultAuthor: 'Mycelium',
    
    // 默认主题
    defaultTheme: 'claude',
    
    // 是否默认开启评论
    enableComment: true,
  },
  
  // ==================== 小红书配置 (M3) ====================
  xiaohongshu: {
    // MCP 服务地址
    // 需要在 Mac Mini 上部署 xiaohongshu-mcp
    mcpUrl: process.env.XHS_MCP_URL || 'http://localhost:3456',
    
    // 默认主题
    defaultTheme: 'blue',
    
    // 水印配置
    watermark: {
      topLeft: '🍄 Mushroom Blog',
      bottomRight: 'XStack18',
    },
  },
};
