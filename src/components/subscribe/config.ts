// listmonk 实例地址（Fly.io 部署，见 pipeline/newsletter/listmonk-fly/），公开订阅页 URL 本身不是秘密——
// 邮件里的"阅读全文"/退订链接也会把它暴露给收件人，因此可以放心写死在前端代码里。
export const LISTMONK_BASE_URL = 'https://list.mushroom.cv';
export const SUBSCRIBE_FORM_URL = `${LISTMONK_BASE_URL}/subscription/form`;
export const SUBSCRIBE_LIST_UUID = '575531a8-2817-4787-aa78-df7338e1747d';
export const ALTCHA_CHALLENGE_URL = `${LISTMONK_BASE_URL}/api/public/captcha/altcha`;
export const ALTCHA_SCRIPT_URL = `${LISTMONK_BASE_URL}/public/static/altcha.umd.js`;
