/**
 * 多用户配置加载器
 * 
 * 使用方法:
 * 1. 创建新用户: 复制 config/users/default.js 并重命名为 {username}.js
 * 2. 设置环境变量: export BLOG_USER=username
 * 3. 或使用: const config = require('./config').load('username');
 */

const fs = require('fs');
const path = require('path');

const USERS_DIR = path.join(__dirname, 'users');

/**
 * 获取所有可用用户列表
 */
function listUsers() {
  const files = fs.readdirSync(USERS_DIR);
  return files
    .filter(f => f.endsWith('.js') && f !== 'default.js')
    .map(f => f.replace('.js', ''));
}

/**
 * 加载指定用户的配置
 * @param {string} userId - 用户ID，默认从环境变量 BLOG_USER 读取
 */
function loadUser(userId = null) {
  const targetUser = userId || process.env.BLOG_USER || 'default';
  const configPath = path.join(USERS_DIR, `${targetUser}.js`);
  
  if (!fs.existsSync(configPath)) {
    console.warn(`⚠️  User config not found: ${targetUser}`);
    console.warn(`   Available users: ${listUsers().join(', ')}`);
    console.warn(`   Using default config`);
    return require('./users/default.js');
  }
  
  return require(configPath);
}

/**
 * 获取当前用户信息
 */
function getCurrentUser() {
  return loadUser();
}

module.exports = {
  listUsers,
  loadUser,
  getCurrentUser,
};
