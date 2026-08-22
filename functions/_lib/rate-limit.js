/**
 * T1.3.6：登录接口限速——同 IP 15 分钟内最多 5 次尝试。
 * T1.3.3 复用同一套计数器给 `/api/search` 限速，key 加不同前缀（"searchlimit:"）区分，
 * 窗口/次数也不同（登录场景要严，搜索场景要宽松，见 search.js 里的调用）。
 *
 * 用 Cloudflare KV 做计数器，跟 T1.3.5 的索引 manifest 共用同一个 KV namespace
 * （避免为限速这一个小功能单独建一个 namespace），key 加前缀跟
 * manifest 的 article_id/_global key 区分开，不会撞车。
 *
 * 已知局限（记入 followups FU-6）：KV 是最终一致的（全球传播约 60s），按 PoP 计数对
 * 分布式撞库偏弱——同一个 IP 打到不同 Cloudflare 边缘节点，短时间内可能各自独立计数，
 * 实际能达到的请求量比名义上限更宽松。在"单一共享密码 + 低访问量个人博客"这个威胁模型下
 * 可接受，真正需要更强限速时应换 Durable Objects 或 Cloudflare 原生的 Rate Limiting binding。
 */

const WINDOW_SECONDS = 15 * 60;
const MAX_ATTEMPTS = 5;

function rateLimitKey(id, prefix = 'ratelimit:') {
	return `${prefix}${id}`;
}

/**
 * 返回 { allowed: boolean, remaining: number }。
 * 每次调用都会把这次尝试计入次数（不管这次调用最终算不算"成功"）——限的是"打了多少次"，
 * 不是"打错了多少次"，避免攻击者用"每次都故意在最后一步失败"之类的手法绕过。
 *
 * `options` 全部可选，缺省值跟原来登录场景的行为完全一致（15 分钟 5 次、"ratelimit:"
 * 前缀），不传 options 的旧调用点（search-auth.js）行为不变。
 */
async function checkAndIncrement(
	kv,
	id,
	{ prefix = 'ratelimit:', windowSeconds = WINDOW_SECONDS, maxAttempts = MAX_ATTEMPTS } = {},
) {
	const key = rateLimitKey(id, prefix);
	// 修正（FU-19，T1.3.4 self-review 发现的既有 bug）：KV 配额耗尽/短暂故障时
	// get/put 都可能抛异常，原来完全没捕获——会让一次本该成功的登录/搜索请求变成裸
	// 500，而不是这个端点该走的降级路径。跟 T1.3.6 B2 同一个道理：限速是这条路径唯一
	// 的滥用防线，"限速本身临时坏掉"不该悄悄放行到无限次尝试，所以 fail-closed（当成
	// "不允许"处理），不是 fail-open——调用方看到的是跟"超过限速"一样的
	// { allowed: false }，不会哪里都裸抛异常。
	try {
		const raw = await kv.get(key);
		const count = raw ? parseInt(raw, 10) || 0 : 0;

		if (count >= maxAttempts) {
			return { allowed: false, remaining: 0 };
		}

		// expirationTtl 每次都重新设置成整窗口长度——不是滑动窗口的精确实现（严格滑动窗口
		// 需要记录每次尝试的时间戳列表），但对"挡自动化脚本连续猛冲"这个目的已经够用，
		// 换来的是实现简单、只占一个 KV key
		await kv.put(key, String(count + 1), { expirationTtl: windowSeconds });
		return { allowed: true, remaining: maxAttempts - count - 1 };
	} catch {
		return { allowed: false, remaining: 0 };
	}
}

export { WINDOW_SECONDS, MAX_ATTEMPTS, rateLimitKey, checkAndIncrement };
