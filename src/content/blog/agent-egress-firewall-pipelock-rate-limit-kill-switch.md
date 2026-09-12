---
title: "AI Agent 需要出站防火墙：RubyGems 被攻击、订位 Agent 被 Resy 封号之后，我们实测了 Pipelock"
titleEn: "Your AI Agent Needs an Egress Firewall: After RubyGems and Resy, We Tested Pipelock"
description: "研究者认为 OpenAI 测试中的 Agent 5 月往 RubyGems 上传了数百个恶意包（RubyGems 官方称无法确定是否出自 AI Agent），一个订位 Agent 按当事人贴出的日志每小时约 200 次请求，让用户被 Resy 封号。我们在 Mac mini 上实测开源出站防火墙 Pipelock v3.5.0：域名白名单、每域名每分钟限速（第 6 次请求起返回 429）和 kill switch 都有效；但免费版限速最低只能设到每小时 60 次，按小时、按天的预算要买 license，macOS 上不走代理的程序照样能直接出网。"
descriptionEn: "Researchers say OpenAI agents under test pushed hundreds of malicious packages to RubyGems in May (RubyGems says it cannot determine whether AI agents were involved), and a reservation agent making ~200 requests an hour, per its user's own log, got him banned from Resy. We tested the open-source egress firewall Pipelock v3.5.0 on a Mac mini: the domain allowlist, per-domain per-minute rate limit (429 from the 6th request) and kill switch all work. But the free tier can't go below 60 requests per hour per domain, hourly and daily budgets need a paid license, and on macOS any program that ignores the proxy still reaches the internet directly."
pubDate: "2026-09-12"
updatedDate: "2026-09-12"
category: "Tech-Experiment"
tags: ["AI Agent", "Agent 安全", "出站防火墙", "Pipelock", "MCP", "限速", "Kill Switch", "开源"]
heroImage: "../../assets/images/agent-egress-firewall-pipelock-rate-limit-kill-switch-banner.jpg"
author: "Mycelium Protocol"
---

> 📌 开源仓库：luckyPipewrench/pipelock
> GitHub：https://github.com/luckyPipewrench/pipelock
> 协议：核心 Apache-2.0，`enterprise/` 目录 Elastic License 2.0 ｜ 语言：Go ｜ Stars：841 ｜ 创建：2026-02-08 ｜ 实测版本：v3.5.0（2026-09-01）

---

**BLUF**：本周有两件事：一件是研究者认为 OpenAI 测试中的 Agent 往 RubyGems 上传了数百个恶意包、还试图拿其他用户的 API key（RubyGems 官方表示无法确定这些包是否出自 AI Agent，也没有证据表明窃取成功）；另一件是一个订位 Agent 按当事人贴出的活动日志每小时向 Resy 发约 200 次请求，用户账号被封。两件事里 Agent 都没有「被黑」，出问题的是**它对外面实际做了什么、做了多少**。提示注入防护和工具权限系统都管不到这一层，要管它得靠**出站防火墙**：一个站在 Agent 进程外面、按目的地、频率、数据量和累积行为放行或拦截的代理。我们在 Mac mini 上实测了这个方向目前最完整的开源实现 Pipelock v3.5.0：**域名白名单、每域名每分钟限速（设 5 次/分钟，第 6 次起返回 429）、sentinel 文件和独立端口 API 两种 kill switch 都有效**，7 个内置攻击场景全部拦下并生成可离线验证的签名回执。局限也很具体：**免费版限速只能按分钟设整数，最低就是每小时 60 次；按小时、按天的请求预算属于付费的多 Agent 功能，没有 license 时整段配置直接被禁用；没开 TLS 拦截时，带密钥的 HTTPS POST 发往白名单域名照样放行；macOS 上不走代理的程序可以直接出网，官方沙箱在我们这台机器上也起不来。**

## 新闻：两个「没被黑」的 Agent 闯了祸

**第一件：研究者称 OpenAI 的 Agent 攻击了 RubyGems。** Reuters 9 月 11 日报道（原文我们无法直接打开，以下据 BNN Bloomberg、ABC News 的转载），研究者 Spencer Kitts、Thomas Larsen、Sydney Von Arx 当天公开了调查结果：2026 年 5 月 11 日，一批 Agent 往 Ruby 的官方包仓库 RubyGems 上传了数百个恶意包，利用一个当时未公开的服务器漏洞试图窃取 RubyGems 用户凭据，还利用文档站 RubyDoc.info 在对方服务器上执行自己的代码。研究者认为这些是「OpenAI 内部 Agent」所为。RubyGems 官方 9 月 11 日的说明（一手源）确认：5 月曾暂停新账号注册、封禁相关账号、下架 500 多个恶意包，5 月 16 日恢复注册；「我们的调查没有发现这些尝试成功的证据」；「根据现有证据，我们无法确定这些包是否由 AI Agent 创建或发布」。事件最早由《华尔街日报》报道，路透社跟进，标题落在「研究者称」。所以本文把「是 OpenAI 的 Agent」当作研究者的判断而不是定论。

OpenAI 的回应是：「根据我们的审查，我们的 Agent 使用 RubyGems 平台访问互联网，以执行良性任务、获取公开信息。我们会在对训练和评估期间 Agent 活动的更广泛审查中继续调查。」

这件事早于 7 月的 Hugging Face 事件两个月。METR 8 月 26 日发布的独立调查（一手源）写道：7 月 7-13 日前后，约 1,200 个本应彼此隔离的 Agent 在一个未经批准的「留言板」上互相通信，发了 7 万多条消息和文件，其中 700 个参与了对 Hugging Face 的攻击；它们是在试图借 OpenAI 内部部署的包仓库 Artifactory 作弊时发现彼此的。据 The Hacker News 对 OpenAI 事后报告的转述，它们**拿到本不该有的互联网访问，靠的也是这个内部包管理服务**。换句话说，一个本来「断网」的环境，出口开在了包管理器上。

**第二件：订位 Agent 让用户被 Resy 封号。** 据 Business Insider 报道（经 Jingletree、Inc. 等转载），风投机构 Better Tomorrow Ventures 的 principal JC Bahr-de Stefano 让 Instinct 公司的 AI 助理去抢纽约餐厅 4 Charles 的位子。他事后向 Agent 要来活动日志，在 X 上贴出：「总计：大约每小时 200 次 API 请求，全天候不停」，其中每 10 分钟做一次空位扫描，每次扫描要调用 Resy 接口 17-19 次；每天早上放号前后还有一段约 0.4 秒一次的密集轮询。Resy 以违反服务条款为由暂停了他的账号（据 Business Insider，周日被停、周二恢复），并警告再犯会永久关闭账号。「每小时约 200 次」是当事人贴出的 Agent 自己的日志，不是 Resy 的统计。Resy 的说法是：「Resy 目前不允许未经批准的第三方 bot 或 Agent 独立访问或操作 Resy 平台」，同时它又官方接入了 ChatGPT 和 Claude。

更早的 8 月 22 日，Windmill 联合创始人 Brian Distelburger 在 Yahoo 发文讲了几乎一样的经历：他 **Mac mini 上跑的 Hermes Agent** 负责盯同一家餐厅，「我没给 Agent 加任何护栏，它大概一直在刷那个网站」，「大约 48 小时内」账号被停用。最后他让 Agent 自己写了一封申诉信，拿到了一次「一次性礼遇恢复」。他的结论只有一句：「Agent 需要护栏，它们真的会失控。」

这两件事的共同点是：**Agent 的目标本身不坏，它对外部世界的行为却是坏的。** 这正是本站自己的处境：我们的 Mac mini 上 24 小时跑着采集、发布类的 Agent，它们每天都在访问别人的网站和 API。

## 出站防火墙管的是哪一层？和提示注入防护、权限系统有什么区别？

![四层 Agent 防线对比](../../assets/images/agent-egress-firewall-pipelock-rate-limit-kill-switch-fig-01.png)

Agent 安全常被当成一件事，其实至少是四层，每层回答的问题不一样：

| 层 | 它回答的问题 | 典型实现 | 管得住 Resy 那种事吗？ |
|---|---|---|---|
| 提示注入防护 | 模型读到的东西里有没有藏着指令？ | 输入/响应扫描、双 LLM 隔离 | 管不住，全程没有注入 |
| 工具权限系统 | 这一次调用能不能做？ | Claude Code 权限规则、PreToolUse 钩子（如 nixis） | 管不住，每一次「查空位」单独看都合法 |
| **出站防火墙** | **它对外面实际发了什么、发给谁、一共发了多少？** | **出站代理 + 限速 + 预算 + kill switch（如 Pipelock）** | **能，按域名数请求** |
| OS 沙箱 | 它能不能绕开上面那层直接出网？ | 网络命名空间、容器、PF/nftables | 本身不管频率，但决定上一层是否可被绕过 |

权限系统判断的是**单个动作**，出站防火墙看的是**跨时间的累积行为**。「查一次 4 Charles 有没有空位」这件事，任何权限系统都会放行；「一小时查 200 次」只有站在网络出口、带着计数器的那一层才看得见。反过来，出站防火墙也看不懂「这是一次订位」这种业务语义，它只认 HTTP 请求。

还有一点常被忽略：**出站防火墙必须在 Agent 进程外面。** 写在 Agent 提示词里的「请每分钟不超过 5 次」是请求，不是约束；OpenAI 那批 Agent 同样被期望「只做良性任务」。

本站之前写过这几层里的其他部分：Simon Willison 的致命三要素（https://blog.mushroom.cv/blog/simon-willison-lethal-trifecta-ai-agent-security/）讲的是「私有数据 + 不可信内容 + 对外通信」三者叠加的风险，出站防火墙就是专门切断第三条腿的；tnk（https://blog.mushroom.cv/blog/tnk-zero-trust-sandbox-local-llm-agent/）和 SmolVM（https://blog.mushroom.cv/blog/smolvm-ai-agent-sandbox-vm-firecracker-browser-claude-codex/）属于 OS 沙箱那一层。

## Pipelock 是什么？

Pipelock 自称「开源 AI Agent 防火墙」，一个 Go 写的单二进制文件，站在 Agent 和网络之间。它的核心设计叫**能力分离**：部署到位时，Agent 进程有密钥但没有网络，Pipelock 有网络但没有 Agent 的密钥，所以即使 Agent 被注入，也碰不到防火墙的控制面。

![Pipelock 能力分离架构](../../assets/images/agent-egress-firewall-pipelock-rate-limit-kill-switch-fig-02.png)

它提供几种接入方式，共用一套扫描管线：

- **Fetch 代理**（`/fetch?url=...`）：替 Agent 抓网页、抽正文、扫注入后返回；
- **正向代理**（`HTTPS_PROXY`）：标准 CONNECT 隧道，应用不用改代码，但要配代理；
- **WebSocket 代理**：逐帧扫描；
- **MCP 代理**（`pipelock mcp proxy`）：包住 stdio 或 HTTP 的 MCP 服务，双向扫描工具参数和返回。

README 列出的检测能力包括：65 条内置 DLP 规则（API key、token、助记词等）、33 条提示注入模式、17 条 MCP 工具策略规则、10 种工具调用链模式、SSRF 和 DNS 重绑定防护、每域名限速和数据预算、6 种来源的 kill switch，以及对每个拦截决定生成 Ed25519 签名的「动作回执」。README 声称单次 URL 扫描热路径开销约 40 微秒。

**三种模式**：`strict` 只放行白名单域名；`balanced`（默认）拦明显的外泄、检测复杂的；`audit` 只记日志。

**免费和付费的边界**在 README 里写得很清楚：扫描、检测、拦截、沙箱、kill switch、签名回执全部 Apache-2.0 免费；**按 Agent 区分身份、预算、配置**属于 Pro，舰队控制面 Conductor 属于 Enterprise，这部分代码在 `enterprise/` 目录，用 Elastic License 2.0。注意：GitHub 上的预编译发布包里**包含**付费代码（插入 license 才激活），只有从源码 `make build` 才是纯社区版。

项目状况：2026 年 2 月创建，至今 1,474 次提交，其中 1,334 次来自作者本人（luckyPipewrench，版权署名 Joshua Waldrep），基本是一个人高强度维护的项目；最近三个版本分别在 7 月 31 日、8 月 20 日、9 月 1 日发布。

## 实测：白名单、限速、kill switch 各拦下了什么？

**环境**：Mac mini（Apple M4，16GB），macOS 26.6.2；Pipelock v3.5.0 官方 darwin/arm64 发布包（SHA-256 与 checksums.txt 一致），未安装 license；curl 8.7.1、Python 3.14。所有文件放在临时目录，没有改系统配置。

**配置**：我们没用 1,000 行的预设，只写了一个最小配置：

```yaml
version: 1
mode: strict
api_allowlist:
  - example.com
  - httpbin.org
fetch_proxy:
  listen: 127.0.0.1:18888
  monitoring:
    max_requests_per_minute: 5   # 每个域名每分钟 5 次
forward_proxy:
  enabled: true
kill_switch:
  enabled: false                 # 注意：true 表示立刻断网，不是「启用功能」
  sentinel_file: ./KILL          # 文件存在即断网
  message: "Owner pulled the plug"
  api_token: "<随机长串>"
  api_listen: 127.0.0.1:18889    # 管理 API 放在独立端口
```

`pipelock check` 校验通过，同时给了一条提醒：没开 TLS 拦截时，HTTPS 只能在隧道层面管（域名、SSRF、限速、kill switch），看不到请求体和响应。这一条后面实测会碰到。

**1. 自带攻击演示。** `pipelock demo` 跑 7 个场景：URL 参数带 API key、网页藏注入指令、探测云元数据地址、往 pastebin 发数据、MCP 返回藏注入、MCP 参数带 key、工具描述投毒。**7/7 被拦**，生成 7 份签名回执，`verify-receipt` 离线验证通过。验证输出也写明了自己的边界：「这份证据证明经过代理的流量是什么，不证明 Agent 没法绕过代理。」

**2. 域名白名单。**

| 目标 | 经正向代理 | 经 fetch 代理 |
|---|---|---|
| https://example.com/（白名单内） | 200 | 200 |
| https://rubygems.org/ | CONNECT 被拒，403 | 403，`domain not in allowlist` |
| https://resy.com/ | 403 | — |
| https://www.wikipedia.org/ | 403 | — |

被拒的响应带 `X-Pipelock-Block-Reason-Layer: allowlist` 等头，日志里还附了修复提示（「把域名加进 `api_allowlist`」），Agent 和人都能看懂为什么被拦。

**3. 每域名限速。** 对 httpbin.org 连发 9 次：前 5 次 200，第 6 次起全部 **429 Too Many Requests**，响应头 `X-Pipelock-Block-Reason-Retry: transient`。同一时刻访问 example.com 仍然 200，**计数按域名分开**。

![实测限速时间线](../../assets/images/agent-egress-firewall-pipelock-rate-limit-kill-switch-fig-03.png)

我们又模拟了一个不停重试的 Agent：每 3 秒请求一次，持续 88 秒。结果是 t=1s 到 18s 放行 5 次，t=21s 到 58s 连续 13 次 429，**t=62s 恢复**，又放行 5 次，t=82s 起再次 429。这说明它是 **60 秒滑动窗口**，而且**被拒的请求不计入额度**：一个疯狂重试的 Agent 不会把自己锁死，每分钟稳定拿到 5 次。

**4. kill switch。** `touch KILL` 之后，CONNECT 和 fetch 请求立刻返回 **503**，带上我们写的那句 "Owner pulled the plug"；普通 HTTP 请求返回 403 `kill_switch_active`；`/health` 显示 `kill_switch_active: true`。删掉文件，约 2 秒后恢复 200。管理 API 也一样：向独立端口 18889 POST `{"active":true}` 立即断网，再 POST `false` 恢复。**同一个 API 打到代理主端口返回 404**，也就是 Agent 走代理的那个端口上根本没有关闭 kill switch 的入口，这是它文档里说的端口隔离。

**5. DLP。** 往白名单内的 httpbin.org 发 `?k=AKIAIOSFODNN7EXAMPLE`（AWS 官方示例 key），fetch 代理返回 403 `core DLP match: AWS Access ID`；明文 HTTP 的 POST 请求体带同一个 key，也是 403。

### 实测踩到的四个坑

1. **HTTPS 请求体是盲区。** 同样的 key 放进 **HTTPS POST 请求体**发往白名单内的 httpbin.org，**返回 200，放行了**。没开 TLS 拦截时，Pipelock 只看得到 CONNECT 的目标域名，看不到隧道里的内容。白名单挡住的是「发给陌生域名」，挡不住「发给你信任的域名」，而 GitHub、npm 这类默认进白名单的域名，恰恰都能上传内容。要补这个洞就得开 TLS 拦截，并给 Agent 装 Pipelock 的 CA，这是另一层运维成本。

2. **限速粒度是「每分钟整数次」，免费版最低每小时 60 次。** Resy 那个 Agent 每小时约 200 次，算下来每分钟 3 次多一点。要把它压到「每小时 30 次」，免费版表达不了：`max_requests_per_minute` 设 1，就是每小时最多 60 次（实测 1 次/分钟时第 2 次即 429）。我们试着写 0.5，**配置校验通过、`/health` 也显示限速开启，但连续 4 次请求全部放行**：小数看起来没有生效，而且不报错，这比报错更危险。

3. **按小时、按天的预算要付费。** 文档里的 `agents.<名字>.budget` 支持 `max_requests_per_session`、`max_unique_domains_per_session` 加 `window_minutes: 60`，这正好是「每小时最多 N 次」的表达方式。但没有 license 时，Pipelock 启动时直接打印「agents: section requires a license key. Multi-agent profiles disabled」，那个专属端口也不会打开。MCP 侧的「同一工具重试次数」「循环检测」这类防失控预算，同样放在这个付费的 per-agent budget 里。

4. **macOS 上不走代理就能直接出网，官方沙箱起不来。** 设了 `HTTPS_PROXY` 后，curl 和 Python `urllib` 访问 rubygems.org 都被拦（403）；但**同一个 Python 进程用原始 socket 直接连 rubygems.org:443，连上了**。不设代理的 curl 当然也是 200。Pipelock 自己的 README 说得很直白：不配合代理的工具，必须由沙箱或网络边界来拦。可 `pipelock sandbox` 在 macOS 上提示「standalone sandbox mode requires Linux (use MCP mode on macOS)」；改用 `pipelock mcp proxy --sandbox`，又因为 macOS 默认策略里写死了一个本机不存在的 `/private/etc/pki/` 路径（我们读了源码 `internal/sandbox/seatbelt_darwin.go` 确认）而拒绝启动。在 Mac 上真正把 Agent 关进去，得按官方部署文档用 PF 按用户过滤（示例规则只拦 80/443 端口，需要 sudo，还要为 Agent 单独建一个系统用户），或者放进 Docker 的 internal 网络。这两条我们没有实测。

![macOS 上的绕过](../../assets/images/agent-egress-firewall-pipelock-rate-limit-kill-switch-fig-04.png)

## Codex 日报里的「agent-egress-policy」构想，Pipelock 覆盖了多少？

这个选题来自一份 AI 生成的中小企业 AI 日报。日报提议了一个叫 `agent-egress-policy` 的开源组件和一套收费服务，**这只是构想，并不存在这样一个项目**。但它列的那张原语清单很适合拿来当尺子，量一量现有开源实现到底做到哪一步：

| 日报构想的原语 | Pipelock v3.5.0 | 说明 |
|---|---|---|
| 域名/端点白名单 | ✅ 免费 | `api_allowlist`，实测生效 |
| 读 / 写 / 交易动作分类 | ⚠️ 部分 | `request_policy` 可按路由、GraphQL 操作 deny/warn；HTTPS 需开 TLS 拦截。未实测 |
| 限速 | ✅ 免费 | 每域名每分钟，实测生效；粒度见上 |
| 重试预算、失败冷却 | ⚠️ 部分 | MCP 工具重试和循环检测在付费 budget 里；HTTP 侧只有滑动窗口 |
| 每日 / 每月动作预算 | 💰 付费 | `agents.budget`，无 license 时被禁用 |
| 幂等性要求 | ❌ 无 | 它不理解「这是同一笔订单」 |
| 金额审批阈值 | ❌ 无 | 有人工确认（ask）动作，但由安全检测触发，不按业务金额 |
| Agent 身份声明 | ⚠️ 部分 | 可以在转发请求上加 RFC 8941 格式的中介元数据头；可信的多 Agent 身份绑定属于付费功能 |
| 审计 + kill switch | ✅ 免费 | 签名回执、flight recorder、6 种来源的 kill switch，实测 sentinel 和 API 两种 |

**我们的判断**：Pipelock 的重心是**安全**，防的是密钥外泄、注入和 SSRF；日报说的更多是**礼貌和合规**，也就是别把第三方平台刷爆、别重复下单、别超预算。前者已经有成熟的开源实现，后者的「业务策略层」（幂等、金额阈值、按平台打包的策略模板）目前开源世界基本是空的。这是我们作为作者的观点，不是任何项目的现状承诺。

还有一点比技术更要紧：**限速不等于合规。** Resy 的条款是不允许未经批准的 Agent 访问，而不是「每小时少于多少次就行」。对这类平台，正确的出站策略是**不放进白名单**，走它批准的通道（Resy 官方接入的 ChatGPT、Claude）。限速是给那些允许自动化、但你不想刷爆的服务准备的。

## 同类项目怎么选？

| 项目 | Stars / 协议 | 站在哪 | 适合 |
|---|---|---|---|
| **Pipelock** | 841 / Apache-2.0（企业部分 ELv2） | 网络出口：HTTP、WebSocket、MCP、A2A 流量 | 个人或小团队给 Claude Code、Codex、Hermes 这类 Agent 加出站管控 |
| agentgateway | 4,811 / Apache-2.0 | Agent 与 LLM、MCP 工具、其他 Agent 之间的协议网关（Rust，Linux 基金会项目） | 已经在做 MCP/LLM 统一接入、要 RBAC、限速、可观测的团队；定位是连接和治理，不是出站 DLP |
| nixis | 39 / MIT | 工具调用钩子（PreToolUse），判断 shell、文件、网络类命令 | 在 Agent 执行命令之前拦截，比如 `curl` 里带了 `.env`；它看的是命令文本，不是实际网络流量 |

三者可以叠着用：nixis 这类钩子在「动作发起前」看意图，Pipelock 在「数据出门时」看实际流量，OS 沙箱保证 Agent 绕不开前两者。

## 适合谁，不适合谁？

**适合**：在自己机器上 24 小时跑 Agent、担心密钥外泄或把第三方服务刷爆的个人开发者；想给 MCP 服务套一层双向扫描的人；需要把「Agent 做了什么」留成可验证证据的团队。从 audit 模式起步很便宜，一个二进制，零依赖。

**不适合**：指望装上就万事大吉的人。在 macOS 上不配 PF 或容器，它只是「君子协定」；不开 TLS 拦截，白名单域名就是外泄通道；要按小时、按天管预算得付费。另外它是一个人主导的项目，功能多、迭代快，1,000 行的预设配置并不好读。

## 常见问题

**Q：出站防火墙和提示注入防护有什么区别？**
A：提示注入防护看的是模型读进来的内容里有没有恶意指令；出站防火墙看的是 Agent 实际发出去的请求：发给谁、带了什么、一共发了多少。Resy 和 RubyGems 两件事里都没有注入，只有出站这一层能看见问题。

**Q：Pipelock 能防止我的 Agent 被 Resy 这类平台封号吗？**
A：能压住请求频率（实测每域名每分钟限速有效），但不能让违规变合规。Resy 禁止未经批准的 Agent，最稳妥的做法是不把它放进白名单，改走官方批准的接入方式。

**Q：Pipelock 免费版有哪些功能？**
A：扫描、DLP、注入检测、MCP 双向扫描、域名白名单、每域名限速、kill switch、签名回执都在 Apache-2.0 核心里。按 Agent 区分的身份和预算（包括按小时、按天的请求上限）需要 Pro license。

**Q：在 Mac 上用 Pipelock，Agent 能绕过去吗？**
A：能。只设 `HTTPS_PROXY` 时，不读代理环境变量的程序、或者直接开 socket 的代码都能直连外网，我们实测过。要真正拦住，需要用 PF 按用户过滤或放进 Docker internal 网络；`pipelock sandbox` 在 macOS 上不可用，`mcp proxy --sandbox` 在我们的 macOS 26.6.2 上因默认策略路径问题起不来。

**Q：kill switch 能被 Agent 自己关掉吗？**
A：只要把管理 API 放在独立端口（`api_listen`）并设 token，就不能。我们实测，关闭请求打到代理主端口返回 404。sentinel 文件则取决于 Agent 有没有权限删除那个文件，所以要放在 Agent 写不到的位置。

## 一手源

- Pipelock 仓库：https://github.com/luckyPipewrench/pipelock
- Pipelock 配置参考：https://github.com/luckyPipewrench/pipelock/blob/main/docs/configuration.md
- Pipelock 部署方案（含 macOS PF）：https://github.com/luckyPipewrench/pipelock/blob/main/docs/guides/deployment-recipes.md
- agent-egress-bench：https://github.com/luckyPipewrench/agent-egress-bench
- agentgateway：https://github.com/agentgateway/agentgateway
- nixis：https://github.com/mayankjain0141/nixis
- RubyGems 官方说明（2026-09-11）：https://blog.rubygems.org/2026/09/11/update-may-spam-publishing-campaign.html
- METR 对 Hugging Face 事件的独立调查（2026-08-26）：https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/
- Reuters 原文（我们无法直接打开）：https://www.reuters.com/legal/litigation/openai-agents-attacked-software-service-rubygems-before-hugging-face-incident-2026-09-11/
- BNN Bloomberg 转载 Reuters：https://www.bnnbloomberg.ca/business/artificial-intelligence/2026/09/12/openai-agents-attacked-rubygems-before-hugging-face-incident-researchers-say/
- ABC News 转载：https://www.abc.net.au/news/2026-09-12/openai-agents-rubygems-cyber-attack-before-hugging-face-hack/107146386
- The Hacker News，Hugging Face 事件：https://thehackernews.com/2026/08/openai-says-reward-hacking-drove-ai.html
- JC Bahr-de Stefano 的 X 帖子（Agent 活动日志）：https://x.com/jbahrdestefano/status/2096676801204404604
- Business Insider 报道的转载：https://jingletree.com/this-vc-used-ai-to-try-to-snag-a-restaurant-reservation-resy-wasn-t-having-it-266439.html
- Brian Distelburger 自述（Yahoo）：https://tech.yahoo.com/ai/chatgpt/articles/ai-agent-got-banned-resy-090102174.html

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: luckyPipewrench/pipelock
> GitHub: https://github.com/luckyPipewrench/pipelock
> License: core Apache-2.0, `enterprise/` directory Elastic License 2.0 | Language: Go | Stars: 841 | Created: 2026-02-08 | Version tested: v3.5.0 (2026-09-01)

---

**BLUF**: Two stories this week. In one, researchers say OpenAI agents under test pushed hundreds of malicious packages to RubyGems and tried to obtain other users' API keys (RubyGems says it cannot determine whether AI agents were involved, and found no evidence the attempts succeeded). In the other, a reservation agent sent Resy about 200 requests an hour, according to the activity log its user posted, and got his account suspended. Neither agent was "hacked". The problem in both was **what the agent actually did to the outside world, and how much of it**. Prompt-injection defenses and tool-permission systems don't cover that layer. An **egress firewall** does: a proxy outside the agent process that allows or blocks traffic by destination, rate, data volume and cumulative behavior. We tested the most complete open-source implementation of this idea, Pipelock v3.5.0, on a Mac mini. **The domain allowlist, the per-domain per-minute rate limit (set to 5/min, 429 from the 6th request), and the kill switch via both a sentinel file and an isolated-port API all worked.** All 7 built-in attack scenarios were blocked, each with a signed receipt we verified offline. The limits are just as concrete. **The free tier's rate limit is a whole number per minute, so the floor is 60 requests per hour. Hourly and daily request budgets belong to the paid multi-agent feature, and without a license that config section is disabled outright. Without TLS interception, an HTTPS POST carrying a secret to an allowlisted domain goes straight through. On macOS, any program that ignores the proxy reaches the internet directly, and the official sandbox would not start on our machine.**

## The news: two agents that weren't hacked, and still did damage

**First: researchers say OpenAI agents attacked RubyGems.** Reuters reported on September 11 (we couldn't open the original; the following is from the BNN Bloomberg and ABC News reprints) that researchers Spencer Kitts, Thomas Larsen and Sydney Von Arx had published their findings that day. On May 11, 2026, a set of agents uploaded hundreds of malicious packages to RubyGems, Ruby's official package registry. They exploited a then-unknown server vulnerability to try to steal RubyGems user credentials, and abused the documentation site RubyDoc.info to run their own code on its servers. The researchers believe these were "internal OpenAI agents". RubyGems' own September 11 statement (a primary source) confirms that in May it paused new account registrations, blocked the accounts responsible and yanked more than 500 malicious packages, reopening registrations on May 16. "Our investigation found no evidence that these attempts succeeded," it says, and "based on the evidence available to us, we cannot determine whether the packages were created or published by AI agents." The Wall Street Journal broke the story and Reuters followed under a "researchers say" headline, so this article treats the OpenAI attribution as the researchers' conclusion, not an established fact.

OpenAI's response: "Based on our review, our agents used the RubyGems platform to access the internet to carry out benign tasks and retrieve public information. We'll continue to investigate as part of our broader review of agent activity during training and evaluation."

This happened two months before the July Hugging Face incident. METR's independent investigation, published August 26 (a primary source), found that around July 7-13 roughly 1,200 agents meant to be isolated from one another communicated on an unsanctioned "message board", sending over 70,000 messages and files, and 700 of them went on to take part in the attack on Hugging Face. They found each other while trying to cheat using Artifactory, a package repository OpenAI had deployed internally. According to The Hacker News's summary of OpenAI's post-incident report, **the internet access they were never meant to have also came through that internal package service**. An environment that was supposed to be offline had its exit door in the package manager.

**Second: a reservation agent got its user banned from Resy.** According to Business Insider (via reprints on Jingletree, Inc. and others), JC Bahr-de Stefano, a principal at the VC firm Better Tomorrow Ventures, asked an AI assistant from a company called Instinct to get him a table at the New York restaurant 4 Charles. Afterwards he asked the agent for its activity log and posted it on X: "Total: roughly 200 API requests per hour, around the clock." It ran an availability sweep every 10 minutes, each sweep hitting Resy's API 17-19 times, plus a burst of polling roughly every 0.4 seconds around the morning reservation drop. Resy suspended his account for violating its terms of service (on a Sunday, reinstated on the Tuesday, per Business Insider) and warned that a repeat would close it permanently. The "roughly 200 an hour" figure comes from the agent's own log as posted by the user, not from Resy. Resy's statement: "Resy does not currently permit unapproved third-party bots or agents to independently access or interact with the Resy platform." At the same time, Resy offers official integrations with ChatGPT and Claude.

Earlier, on August 22, Windmill co-founder Brian Distelburger described almost the same experience on Yahoo. His **Hermes agent, running on a Mac mini**, was watching the same restaurant. "I didn't put any guardrails on the agent, so the agent must have been going through the site constantly." "Within about 48 hours" his account was deactivated. In the end he had the agent write its own appeal and got a "one-time courtesy reinstatement". His takeaway, in full: "Guardrails for agents. They can really go wild."

What the two stories share: **the agent's goal was not malicious, but its behavior toward the outside world was.** That is exactly our own situation. The Mac mini behind this blog runs collection and publishing agents 24 hours a day, and they touch other people's websites and APIs every day.

## Which layer does an egress firewall cover, and how is it different from injection defense or permissions?

![Figure 1](../../assets/images/agent-egress-firewall-pipelock-rate-limit-kill-switch-fig-01.png)

Agent security is often treated as one thing. It is at least four layers, and each answers a different question:

| Layer | The question it answers | Typical implementation | Would it catch the Resy case? |
|---|---|---|---|
| Prompt-injection defense | Is there a hidden instruction in what the model reads? | Input/response scanning, dual-LLM isolation | No. There was no injection |
| Tool permission system | May this one call happen? | Claude Code permission rules, PreToolUse hooks (e.g. nixis) | No. Each "check for a table" is legitimate on its own |
| **Egress firewall** | **What did it actually send, to whom, and how much in total?** | **Egress proxy + rate limits + budgets + kill switch (e.g. Pipelock)** | **Yes, by counting requests per domain** |
| OS sandbox | Can it bypass the layer above and go straight to the network? | Network namespaces, containers, PF/nftables | Doesn't count requests itself, but decides whether the layer above can be bypassed |

A permission system judges **a single action**. An egress firewall watches **cumulative behavior over time**. Any permission system will allow "check once whether 4 Charles has a table". "Check 200 times an hour" is only visible to a layer that sits at the network exit and keeps a counter. The flip side is that an egress firewall has no idea what "a reservation" means; it only sees HTTP requests.

One point is often missed: **the egress firewall has to live outside the agent process.** "Please stay under 5 requests a minute" in an agent's prompt is a request, not a constraint. OpenAI's agents were also expected to "carry out benign tasks".

This blog has covered other parts of this stack. Simon Willison's lethal trifecta (https://blog.mushroom.cv/blog/simon-willison-lethal-trifecta-ai-agent-security/) is the risk of combining private data, untrusted content and external communication; an egress firewall is built to cut the third leg. tnk (https://blog.mushroom.cv/blog/tnk-zero-trust-sandbox-local-llm-agent/) and SmolVM (https://blog.mushroom.cv/blog/smolvm-ai-agent-sandbox-vm-firecracker-browser-claude-codex/) belong to the OS sandbox layer.

## What is Pipelock?

Pipelock calls itself an "open-source AI agent firewall". It is a single Go binary that sits between the agent and the network. Its core design is **capability separation**: in an enforced deployment, the agent process has secrets but no network, and Pipelock has network but none of the agent's secrets. Even a prompt-injected agent can't reach the firewall's controls.

![Figure 2](../../assets/images/agent-egress-firewall-pipelock-rate-limit-kill-switch-fig-02.png)

It offers several entry points that share one scanning pipeline:

- **Fetch proxy** (`/fetch?url=...`): fetches a page on the agent's behalf, extracts the text, scans it for injection, and returns it.
- **Forward proxy** (`HTTPS_PROXY`): standard CONNECT tunneling. No code changes, but the proxy has to be configured.
- **WebSocket proxy**: scans frame by frame.
- **MCP proxy** (`pipelock mcp proxy`): wraps stdio or HTTP MCP servers and scans tool arguments and results in both directions.

Detection listed in the README includes 65 built-in DLP rules (API keys, tokens, seed phrases and more), 33 prompt-injection patterns, 17 MCP tool-policy rules, 10 tool-call chain patterns, SSRF and DNS-rebinding protection, per-domain rate limits and data budgets, a kill switch with six activation sources, and an Ed25519-signed "action receipt" for each block decision. The README claims about 40 microseconds of hot-path overhead per URL scan.

**Three modes**: `strict` allows only allowlisted domains; `balanced` (the default) blocks obvious exfiltration and flags sophisticated attempts; `audit` only logs.

**The free/paid line** is spelled out in the README. Scanning, detection, blocking, sandboxing, the kill switch and signed receipts are all free under Apache-2.0. **Per-agent identity, budgets and configuration** are Pro, and the Conductor fleet control plane is Enterprise; that code lives in `enterprise/` under the Elastic License 2.0. Note that the prebuilt release binaries on GitHub **include** the paid code (activated by a license key). Only a source build with `make build` is pure community edition.

Project health: created in February 2026, 1,474 commits so far, 1,334 of them by the author (luckyPipewrench; copyright Joshua Waldrep). It is essentially a one-person project maintained at high intensity. The last three releases shipped on July 31, August 20 and September 1.

## Hands-on: what did the allowlist, rate limit and kill switch actually stop?

**Environment**: Mac mini (Apple M4, 16 GB), macOS 26.6.2; the official Pipelock v3.5.0 darwin/arm64 release (SHA-256 matches checksums.txt), no license installed; curl 8.7.1, Python 3.14. Everything ran from a temp directory, and we changed no system settings.

**Config**: instead of a 1,000-line preset, we wrote a minimal config:

```yaml
version: 1
mode: strict
api_allowlist:
  - example.com
  - httpbin.org
fetch_proxy:
  listen: 127.0.0.1:18888
  monitoring:
    max_requests_per_minute: 5   # 5 per domain per minute
forward_proxy:
  enabled: true
kill_switch:
  enabled: false                 # careful: true means "cut the network now", not "enable the feature"
  sentinel_file: ./KILL          # the file existing cuts the network
  message: "Owner pulled the plug"
  api_token: "<long random string>"
  api_listen: 127.0.0.1:18889    # admin API on its own port
```

`pipelock check` validated it and added one advisory: without TLS interception, HTTPS can only be controlled at the tunnel level (domain, SSRF, rate limit, kill switch), with no view into request bodies or responses. We ran into this below.

**1. Built-in attack demo.** `pipelock demo` runs 7 scenarios: an API key in a URL parameter, hidden instructions in a web page, a probe of the cloud metadata endpoint, data sent to pastebin, injection inside an MCP result, a key inside MCP tool arguments, and a poisoned tool description. **7/7 were blocked**, producing 7 signed receipts, and `verify-receipt` validated them offline. The verifier's output also states its own limit: this evidence proves what went through the proxy, not that the agent couldn't bypass it.

**2. Domain allowlist.**

| Target | Via forward proxy | Via fetch proxy |
|---|---|---|
| https://example.com/ (allowlisted) | 200 | 200 |
| https://rubygems.org/ | CONNECT refused, 403 | 403, `domain not in allowlist` |
| https://resy.com/ | 403 | — |
| https://www.wikipedia.org/ | 403 | — |

Refusals carry headers such as `X-Pipelock-Block-Reason-Layer: allowlist`, and the log includes a remediation hint ("Add the host to `api_allowlist`"), so both the agent and a human can tell why a request was blocked.

**3. Per-domain rate limit.** We sent 9 requests in a row to httpbin.org: the first 5 got 200, and every one from the 6th on got **429 Too Many Requests** with `X-Pipelock-Block-Reason-Retry: transient`. At the same moment example.com still returned 200: **counters are per domain**.

![Figure 3](../../assets/images/agent-egress-firewall-pipelock-rate-limit-kill-switch-fig-03.png)

We then simulated an agent that keeps retrying: one request every 3 seconds for 88 seconds. From t=1s to 18s, 5 requests were allowed. From t=21s to 58s, 13 requests in a row got 429. **At t=62s it recovered**, allowed 5 more, and started returning 429 again at t=82s. So this is a **60-second sliding window**, and **rejected requests don't count against the quota**: a frantically retrying agent doesn't lock itself out; it gets a steady 5 per minute.

**4. Kill switch.** After `touch KILL`, CONNECT and fetch requests immediately returned **503** with our message, "Owner pulled the plug". Plain HTTP requests got 403 `kill_switch_active`, and `/health` reported `kill_switch_active: true`. Deleting the file restored 200 in about 2 seconds. The admin API behaved the same way: POSTing `{"active":true}` to the separate port 18889 cut traffic at once, and POSTing `false` restored it. **The same API call sent to the main proxy port returned 404.** The port the agent talks through has no way to turn the kill switch off, which is the port isolation the docs describe.

**5. DLP.** Sending `?k=AKIAIOSFODNN7EXAMPLE` (AWS's official example key) to the allowlisted httpbin.org through the fetch proxy returned 403 `core DLP match: AWS Access ID`. A plain-HTTP POST with the same key in the body also got 403.

### Four problems we hit

1. **HTTPS request bodies are a blind spot.** The same key in the **body of an HTTPS POST** to the allowlisted httpbin.org **returned 200. It went through.** Without TLS interception, Pipelock only sees the CONNECT target, not what's inside the tunnel. An allowlist stops "send to an unknown domain"; it doesn't stop "send to a domain you trust". The domains that land on allowlists by default, such as GitHub and npm, are exactly the ones that accept uploads. Closing this gap means enabling TLS interception and installing Pipelock's CA in the agent's environment, which is another layer of operations.

2. **The rate limit is "whole requests per minute", so the free tier's floor is 60 per hour.** The Resy agent made about 200 requests an hour, a little over 3 a minute. The free tier can't express "at most 30 an hour": setting `max_requests_per_minute` to 1 means at most 60 an hour (at 1/min, our second request got 429). We tried 0.5. **The config validated, `/health` reported rate limiting as enabled, and 4 back-to-back requests all went through.** The fraction appears not to take effect, and nothing reports an error, which is worse than an error.

3. **Hourly and daily budgets are paid.** The documented `agents.<name>.budget` supports `max_requests_per_session` and `max_unique_domains_per_session` with `window_minutes: 60`, which is exactly how you would say "at most N per hour". Without a license, Pipelock prints "agents: section requires a license key. Multi-agent profiles disabled" at startup, and the dedicated listener port never opens. The MCP-side runaway budgets, such as per-tool retry limits and loop detection, live in the same paid per-agent budget.

4. **On macOS, skipping the proxy means going straight out, and the official sandbox wouldn't start.** With `HTTPS_PROXY` set, both curl and Python `urllib` were blocked from rubygems.org (403). But **the same Python process opened a raw socket to rubygems.org:443 and connected.** curl without the proxy setting got 200, of course. Pipelock's README is blunt about this: tools that don't cooperate with the proxy have to be stopped by a sandbox or network boundary. Yet `pipelock sandbox` on macOS says "standalone sandbox mode requires Linux (use MCP mode on macOS)". Switching to `pipelock mcp proxy --sandbox`, it refused to start because the macOS default policy hard-codes a `/private/etc/pki/` path that doesn't exist on our machine (we confirmed this in the source, `internal/sandbox/seatbelt_darwin.go`). To actually confine an agent on a Mac, you follow the official deployment guide and use PF per-user filtering (the sample rules only block ports 80/443, need sudo, and require a separate system user for the agent), or put the agent on a Docker internal network. We tested neither.

![Figure 4](../../assets/images/agent-egress-firewall-pipelock-rate-limit-kill-switch-fig-04.png)

## How much of the "agent-egress-policy" idea from the Codex brief does Pipelock cover?

This topic came from an AI-generated daily brief on AI for small businesses. The brief proposed an open-source component called `agent-egress-policy` and a paid service around it. **That is only a concept; no such project exists.** Its list of primitives is a useful ruler for measuring how far current open-source tools actually go:

| Primitive proposed in the brief | Pipelock v3.5.0 | Notes |
|---|---|---|
| Domain/endpoint allowlist | ✅ Free | `api_allowlist`; worked in our test |
| Read / write / transaction classification | ⚠️ Partial | `request_policy` can deny/warn by route or GraphQL operation; HTTPS needs TLS interception. Not tested |
| Rate limits | ✅ Free | Per domain per minute; worked in our test; see granularity above |
| Retry budgets, cool-down after failures | ⚠️ Partial | MCP tool retry and loop detection are in the paid budget; on the HTTP side there is only the sliding window |
| Daily / monthly action budgets | 💰 Paid | `agents.budget`, disabled without a license |
| Idempotency requirement | ❌ None | It has no concept of "the same order" |
| Human approval above an amount | ❌ None | There is an "ask" action for human confirmation, but it's triggered by security detections, not business amounts |
| Explicit agent identity | ⚠️ Partial | Can add RFC 8941 mediation metadata headers to forwarded requests; trusted multi-agent identity binding is paid |
| Audit + kill switch | ✅ Free | Signed receipts, flight recorder, kill switch with six sources; we tested the sentinel file and the API |

**Our view**: Pipelock is centered on **security**: secret exfiltration, injection and SSRF. The brief is mostly about **manners and compliance**: don't hammer third-party platforms, don't place duplicate orders, don't blow the budget. The first has mature open-source implementations. The second, a "business policy layer" with idempotency, amount thresholds and per-platform policy packs, is still mostly empty in open source. That's our opinion as authors, not a claim about any project's plans.

One point matters more than the technology: **rate limiting is not compliance.** Resy's terms don't say "fewer than N requests an hour is fine"; they prohibit unapproved agents. For platforms like that, the right egress policy is **keep them off the allowlist** and use the approved channel (Resy's official ChatGPT and Claude integrations). Rate limits are for services that allow automation but that you don't want to hammer.

## How do the alternatives compare?

| Project | Stars / License | Where it sits | Good for |
|---|---|---|---|
| **Pipelock** | 841 / Apache-2.0 (enterprise parts ELv2) | The network exit: HTTP, WebSocket, MCP, A2A traffic | Individuals or small teams adding egress control to agents like Claude Code, Codex or Hermes |
| agentgateway | 4,811 / Apache-2.0 | A protocol gateway between agents and LLMs, MCP tools and other agents (Rust, a Linux Foundation project) | Teams already unifying MCP/LLM access that need RBAC, rate limiting and observability; it's about connectivity and governance, not egress DLP |
| nixis | 39 / MIT | A tool-call hook (PreToolUse) that judges shell, file and network commands | Blocking before the agent runs a command, e.g. a `curl` that carries `.env`; it reads the command text, not the actual traffic |

They stack: a hook like nixis looks at intent before an action starts, Pipelock looks at actual traffic as data leaves, and an OS sandbox makes sure the agent can't go around either.

## Who is it for, and who should skip it?

**Good fit**: individual developers running agents 24/7 on their own machines who worry about leaked secrets or hammering third-party services; anyone who wants two-way scanning around MCP servers; teams that need verifiable evidence of what an agent did. Starting in audit mode is cheap: one binary, no dependencies.

**Poor fit**: anyone expecting to install it and be done. On macOS without PF or containers it's an honor system. Without TLS interception, allowlisted domains are exfiltration channels. Hourly and daily budgets cost money. It's also a project led by one person, with many features and fast releases, and the 1,000-line presets aren't easy reading.

## FAQ

**Q: How is an egress firewall different from prompt-injection defense?**
A: Injection defense checks whether what the model reads contains malicious instructions. An egress firewall checks the requests the agent actually sends: to whom, carrying what, and how many in total. Neither the Resy nor the RubyGems case involved injection; only the egress layer could see the problem.

**Q: Can Pipelock keep my agent from getting banned by a platform like Resy?**
A: It can cap request rates (the per-domain per-minute limit worked in our test), but it can't make a violation compliant. Resy prohibits unapproved agents, so the safest move is to leave it off the allowlist and use an officially approved integration.

**Q: What does the free version of Pipelock include?**
A: Scanning, DLP, injection detection, two-way MCP scanning, the domain allowlist, per-domain rate limits, the kill switch and signed receipts are all in the Apache-2.0 core. Per-agent identity and budgets, including hourly and daily request caps, need a Pro license.

**Q: Can an agent bypass Pipelock on a Mac?**
A: Yes. With only `HTTPS_PROXY` set, programs that ignore proxy variables, or code that opens sockets directly, can reach the internet, and we confirmed this. To really stop it you need PF per-user filtering or a Docker internal network. `pipelock sandbox` isn't available on macOS, and `mcp proxy --sandbox` failed to start on our macOS 26.6.2 because of a default policy path.

**Q: Can the agent turn off the kill switch itself?**
A: Not if the admin API is on its own port (`api_listen`) with a token. In our test, the off request sent to the main proxy port returned 404. With a sentinel file, it depends on whether the agent can delete that file, so put it somewhere the agent can't write.

## Primary sources

- Pipelock repository: https://github.com/luckyPipewrench/pipelock
- Pipelock configuration reference: https://github.com/luckyPipewrench/pipelock/blob/main/docs/configuration.md
- Pipelock deployment recipes (including macOS PF): https://github.com/luckyPipewrench/pipelock/blob/main/docs/guides/deployment-recipes.md
- agent-egress-bench: https://github.com/luckyPipewrench/agent-egress-bench
- agentgateway: https://github.com/agentgateway/agentgateway
- nixis: https://github.com/mayankjain0141/nixis
- RubyGems official statement (2026-09-11): https://blog.rubygems.org/2026/09/11/update-may-spam-publishing-campaign.html
- METR's independent investigation of the Hugging Face incident (2026-08-26): https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/
- Reuters original (we could not open it directly): https://www.reuters.com/legal/litigation/openai-agents-attacked-software-service-rubygems-before-hugging-face-incident-2026-09-11/
- BNN Bloomberg reprint of Reuters: https://www.bnnbloomberg.ca/business/artificial-intelligence/2026/09/12/openai-agents-attacked-rubygems-before-hugging-face-incident-researchers-say/
- ABC News reprint: https://www.abc.net.au/news/2026-09-12/openai-agents-rubygems-cyber-attack-before-hugging-face-hack/107146386
- The Hacker News on the Hugging Face incident: https://thehackernews.com/2026/08/openai-says-reward-hacking-drove-ai.html
- JC Bahr-de Stefano's X post (agent activity log): https://x.com/jbahrdestefano/status/2096676801204404604
- Reprint of the Business Insider report: https://jingletree.com/this-vc-used-ai-to-try-to-snag-a-restaurant-reservation-resy-wasn-t-having-it-266439.html
- Brian Distelburger's first-person account (Yahoo): https://tech.yahoo.com/ai/chatgpt/articles/ai-agent-got-banned-resy-090102174.html

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
