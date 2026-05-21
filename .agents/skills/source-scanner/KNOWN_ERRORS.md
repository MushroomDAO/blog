# Source Scanner — 已知错误与修复方案

扫描流水线自动归因记录。每次步骤失败时追加，下次执行前参考。

---

## [2026-05-21] 步骤: wechat_draft

**错误**: `errcode: 40164 invalid ip x.x.x.x, not in whitelist`

**原因**: 服务器出口 IP 未加入微信公众号 IP 白名单

**修复方案**:
- 登录 mp.weixin.qq.com → 设置与开发 → 基本配置 → IP白名单
- 添加当前机器出口 IP（可用 `curl ifconfig.me` 查询）
- IP 变化时（如 DHCP 或重拨）需要重新更新

---

## [2026-05-21] 步骤: wechat_draft

**错误**: `errcode: 40007 invalid media_id`

**上下文**: 公众号草稿创建时封面图片 media_id 无效

**原因**: WeChat media_id 有效期仅 72 小时，pipeline/m2/ 复用了过期的 media_id

**修复方案**:
- 每次创建草稿前必须重新上传封面图片，不能复用旧 media_id
- 如果 source 目录里没有图片，m2 pipeline 会用默认封面 — 确保默认封面在每次运行时重新上传
- 检查 `pipeline/m2/index.js` 的封面处理逻辑，确认是否有缓存机制导致复用

---

## [2026-05-21 17:01] 步骤: ai_generate
**错误**: `AI returned empty response`
**上下文**: dir=20260521-165937-inbox model=Qwen3.6-35B-A3B-MLX-8bit
**建议**: 检查本地 AI 服务是否在线: curl http://127.0.0.1:8088/v1/models
---

## [2026-05-21 17:25] 步骤: ai_generate
**错误**: `AI returned empty response`
**上下文**: dir=20260521-165937-inbox model=Qwen3.6-35B-A3B-MLX-8bit
**建议**: 检查本地 AI 服务是否在线: curl http://127.0.0.1:8088/v1/models
---

## [2026-05-21 17:28] 步骤: ai_generate
**错误**: `AI returned empty response`
**上下文**: dir=20260521-165937-inbox model=Qwen3.6-35B-A3B-MLX-8bit
**建议**: 检查本地 AI 服务是否在线: curl http://127.0.0.1:8088/v1/models
---

## [2026-05-21 17:32] 步骤: wechat_draft
**错误**: ``
**上下文**: slug=research-paper-writing-tool-upgrade- retries=3
**建议**: 查看 /Users/jason/Dev/mycelium/blog/source/.scan.log 获取完整错误
---
