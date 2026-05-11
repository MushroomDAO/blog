/**
 * 小宝宝用户配置 - 公众号自动发布
 *
 * 需要在 .env 文件中设置（或直接 export）：
 *   WECHAT_APP_ID_XBB=wx...
 *   WECHAT_APP_SECRET_XBB=...
 *   WECHAT_MP_ID_XBB=gh_...
 */
module.exports = {
  id: 'xiaobaobao',
  name: '小宝宝',

  // ==================== Blog 配置 (M1) ====================
  blog: {
    projectName: 'blog-xiaobaobao',
    domain: '',              // 填入域名，如 blog.xxxx.com

    brand: {
      name: '小宝宝',
      description: '',
      twitter: '',
      github: '',
    },

    watermark: {
      topLeft: '小宝宝',
      bottomRight: '',
    },

    defaultCategory: 'Tech-News',
    author: '小宝宝',
  },

  // ==================== 微信公众号配置 (M2) ====================
  wechat: {
    // 从 https://mp.weixin.qq.com -> 设置与开发 -> 基本配置 获取
    appId:     process.env.WECHAT_APP_ID_XBB     || '',
    appSecret: process.env.WECHAT_APP_SECRET_XBB || '',

    // 公众号原始 ID（gh_xxx），从公众号账号信息页获取
    mpId: process.env.WECHAT_MP_ID_XBB || '',

    defaultAuthor: '小宝宝',
    defaultTheme: 'chengyun',   // 可选：chengyun / blue / mint / cyber / dark
    enableComment: true,
  },

  // ==================== 小红书配置 (M3，暂未开通) ====================
  xiaohongshu: {
    mcpUrl: process.env.XHS_MCP_URL || 'http://localhost:3456',
    defaultTheme: 'blue',
    watermark: {
      topLeft: '小宝宝',
      bottomRight: '',
    },
  },
};
