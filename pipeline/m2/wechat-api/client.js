const axios = require('axios');
const fs = require('fs');
const path = require('path');
const FormData = require('form-data');

/**
 * 微信公众号 API 客户端
 */
class WeChatClient {
  constructor(appId, appSecret) {
    this.appId = appId;
    this.appSecret = appSecret;
    this.accessToken = null;
    this.tokenExpiry = null;
  }

  /**
   * 获取 Access Token
   */
  async getAccessToken() {
    // 缓存有效期内直接返回
    if (this.accessToken && this.tokenExpiry && Date.now() < this.tokenExpiry) {
      return this.accessToken;
    }

    const url = 'https://api.weixin.qq.com/cgi-bin/token';
    const params = {
      grant_type: 'client_credential',
      appid: this.appId,
      secret: this.appSecret
    };

    try {
      const { data } = await axios.get(url, { params });
      
      if (data.access_token) {
        this.accessToken = data.access_token;
        // 提前 5 分钟过期
        this.tokenExpiry = Date.now() + (data.expires_in - 300) * 1000;
        console.log('✅ Access token obtained');
        return this.accessToken;
      } else {
        throw new Error(`Token error: ${JSON.stringify(data)}`);
      }
    } catch (error) {
      console.error('❌ Failed to get access token:', error.message);
      throw error;
    }
  }

  /**
   * 上传图片到微信 CDN（文章内容图片）
   */
  async uploadImage(imagePath) {
    const token = await this.getAccessToken();
    const url = `https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token=${token}`;
    
    const form = new FormData();
    form.append('media', fs.createReadStream(imagePath));
    
    try {
      const { data } = await axios.post(url, form, {
        headers: form.getHeaders()
      });
      
      if (data.url) {
        console.log(`✅ Image uploaded: ${path.basename(imagePath)}`);
        return data.url;
      } else {
        throw new Error(`Upload failed: ${JSON.stringify(data)}`);
      }
    } catch (error) {
      console.error('❌ Image upload failed:', error.message);
      throw error;
    }
  }

  /**
   * 上传封面图素材（永久素材）
   */
  async uploadCover(imagePath) {
    const token = await this.getAccessToken();
    const url = `https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${token}&type=image`;
    
    const form = new FormData();
    form.append('media', fs.createReadStream(imagePath));
    
    try {
      const { data } = await axios.post(url, form, {
        headers: form.getHeaders()
      });
      
      if (data.media_id) {
        console.log(`✅ Cover uploaded: media_id=${data.media_id}`);
        return {
          mediaId: data.media_id,
          url: data.url
        };
      } else {
        throw new Error(`Upload failed: ${JSON.stringify(data)}`);
      }
    } catch (error) {
      console.error('❌ Cover upload failed:', error.message);
      throw error;
    }
  }

  /**
   * 发布草稿
   */
  async createDraft(article) {
    const token = await this.getAccessToken();
    const url = `https://api.weixin.qq.com/cgi-bin/draft/add?access_token=${token}`;
    
    const payload = {
      articles: [{
        title: article.title,
        author: article.author || 'Mycelium',
        digest: article.digest || '',
        content: article.content,
        content_source_url: article.sourceUrl || '',
        thumb_media_id: article.thumbMediaId,
        need_open_comment: article.needOpenComment !== false ? 1 : 0,
        only_fans_can_comment: article.onlyFansCanComment ? 1 : 0,
        original_article_type: article.declareOriginal !== false ? 1 : 0
      }]
    };
    
    try {
      const { data } = await axios.post(url, payload, {
        headers: { 'Content-Type': 'application/json; charset=utf-8' }
      });
      
      if (data.media_id) {
        console.log(`✅ Draft created: media_id=${data.media_id}`);
        return {
          mediaId: data.media_id,
          createTime: data.create_time
        };
      } else {
        throw new Error(`Create draft failed: ${JSON.stringify(data)}`);
      }
    } catch (error) {
      // A lost response can follow a successful draft/add. Read the server
      // ledger before returning failure; never issue a second draft/add here.
      if (['ECONNRESET', 'ECONNABORTED', 'ETIMEDOUT', 'EPIPE', 'ERR_NETWORK'].includes(error.code)) {
        try {
          const recovered = await this.findCreatedDraft(payload.articles[0], token);
          if (recovered) {
            console.warn('ℹ️ Draft response lost; recovered the matching server draft');
            return recovered;
          }
        } catch (readError) {
          console.error('❌ Draft reconciliation failed; do not blindly recreate:', readError.message);
        }
      }
      console.error('❌ Create draft failed:', error.message);
      throw error;
    }
  }

  async findCreatedDraft(expected, token) {
    if (!expected.thumb_media_id || !expected.content) return undefined;
    const matches = new Map();
    for (let offset = 0; ; offset += 20) {
      const { data } = await axios.post(
        `https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token=${token}`,
        { offset, count: 20, no_content: 0 }, { timeout: 15000 }
      );
      if (data.errcode) throw new Error(`Draft ledger read failed: ${data.errcode}`);
      if (!Array.isArray(data.item)) throw new Error('Draft ledger response is incomplete');
      for (const item of data.item) {
        const news = item.content?.news_item;
        if (news?.length !== 1 || !item.media_id) continue;
        const article = news[0];
        const fields = ['title', 'author', 'digest', 'content', 'content_source_url',
          'thumb_media_id', 'need_open_comment', 'only_fans_can_comment'];
        if (fields.every(field => article[field] === expected[field])) {
          matches.set(item.media_id, {mediaId: item.media_id, createTime: item.create_time, recovered: true});
        }
      }
      if (data.item.length < 20) break;
    }
    if (matches.size > 1) throw new Error('Multiple identical server drafts require reconciliation');
    return matches.values().next().value;
  }
}

module.exports = { WeChatClient };
