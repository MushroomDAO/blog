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

// 修正（round 2 review 用真实威胁模型实测证实的 bug，见 checkAndIncrement 里的
// 详细说明）：key 现在带一个固定时间桶编号，不同桶各自独立计数、各自独立过期。
function rateLimitKey(id, prefix, windowSeconds) {
	const bucket = Math.floor(Date.now() / 1000 / windowSeconds);
	return `${prefix}${id}:${bucket}`;
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
	const key = rateLimitKey(id, prefix, windowSeconds);
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

		// 修正（round 2 review 用 M6 威胁模型实测证实的真实 bug）：原来 key 不带时间桶，
		// 每次 put 都把 TTL 重设成整窗口长度——只要请求间隔小于窗口长度，这个 KV 条目
		// 就永远不会真正到期。实测：一个每分钟搜一次的正常读者，会在第 30 分钟耗尽
		// 30 次预算后被 429，且之后还要再等一个窗口长度（这里是 5 分钟）才恢复——这不是
		// "5 分钟窗口限 30 次"，是"距离上次成功请求 5 分钟内不能有第 31 次"，对持续、
		// 低速的真实使用反而更容易触发限速，实测相当于 30 次预算只够约 5 次真实搜索
		// （叠加前端 300ms 防抖，一次完整键入约产生 6 个请求）。现在 key 本身带固定
		// 时间桶（见 rateLimitKey），每个桶的 TTL 只需要设成窗口长度——桶边界到了会
		// 换一个全新的 key，旧桶不管中途有没有请求都会在窗口长度后自然过期，不再
		// 因为持续活跃就被无限期推后。不是滑动窗口的精确实现（严格滑动窗口需要记录
		// 每次尝试的时间戳列表），但边界行为不再有上面这个反直觉的 bug。
		await kv.put(key, String(count + 1), { expirationTtl: windowSeconds });
		return { allowed: true, remaining: maxAttempts - count - 1 };
	} catch {
		return { allowed: false, remaining: 0 };
	}
}

export { WINDOW_SECONDS, MAX_ATTEMPTS, rateLimitKey, checkAndIncrement };
