---
title: "exxperts 拆解：记忆要你批准才写入的本地 AI 同事，「数据不出本机」要打几折？"
titleEn: "exxperts, Torn Down: A Local-First AI Colleague Whose Memory Needs Your Approval — and How Local \"Nothing Leaves Your Machine\" Really Is"
description: "exxperts 是德国咨询公司 EXXETA 开源的桌面 AI 助手（Apache-2.0，357 星）：记忆存成本机 Markdown，每次写入都要你批准，可撤销、可回看历史。我们在 Mac mini 上构建并跑了 30 个记忆与安全相关冒烟测试，全部通过；但接云端模型时，对话和记忆照样发给 Claude 或 ChatGPT，「数据不出本机」只在接本地模型并关掉联网搜索时才成立。"
descriptionEn: "exxperts is an Apache-2.0 desktop AI assistant (357 stars) open-sourced by German consultancy EXXETA: memory lives in local Markdown files, every write needs your approval, and saves can be undone and replayed. We built it on a Mac mini and ran 30 memory and security smoke tests, all passing. But with a cloud model, your conversations and memory still go to Claude or ChatGPT; \"nothing leaves your machine\" only holds with a local model and web search switched off."
wechatTitle: "exxperts拆解：记忆要你批准的本地AI同事"
wechatDigest: "德国EXXETA开源，记忆每次写入都要你批准。实测构建和30个测试全过，但接云端模型时数据照样出本机。"
pubDate: "2026-09-24"
updatedDate: "2026-09-24"
category: "Tech-Experiment"
tags: ["exxperts", "AI Agent", "Agent 记忆", "本地优先", "MCP", "Ollama", "开源"]
heroImage: "../../assets/images/exxperts-local-first-ai-agent-approval-gated-memory-teardown-banner.jpg"
author: "Mycelium Protocol"
---

> 📌 开源仓库：EXXETA/exxperts
> GitHub：https://github.com/EXXETA/exxperts
> 协议：Apache-2.0 ｜ 语言：TypeScript ｜ Stars：357 ｜ 创建：2026-07-07 ｜ 最新版本：v0.13.2（2026-09-23）

---

**BLUF**：exxperts 是一个装在自己电脑上的 AI 助手，德国咨询公司 EXXETA 出品。它和别的「带记忆的 Agent」最大的不同是：**记忆不由模型自己决定写什么，每一次写入都要你在界面上批准**，记忆本身是本机上一份能直接打开的 Markdown 文件，每次保存都留档、可撤销、可以回看任意一天的版本。我们在 Mac mini 上从源码构建成功，跑了仓库自带的 30 个记忆与安全相关冒烟测试，30 个全过；启动服务后用 curl 验证了它只监听 127.0.0.1、没有令牌返回 401、伪造 Host 或带代理头返回 403。

但它的口号「nothing leaves your machine」要打折扣。README 原句后面还有半句「unless you send it」：只要你用的是 Claude、ChatGPT 这类云端模型，对话、记忆内容、附件和工具结果都会随提示词发给模型厂商，项目自己的 memory.md 也写明了这一点。真正全本地，需要接 Ollama 或 LM Studio，再把联网搜索关掉或换成自建 SearXNG。

这篇文章讲四件事：它是什么、记忆审批到底怎么实现、数据在什么情况下会出本机、以及 Mac 用户怎么装、怎么接本地模型。

## exxperts 是什么？

一句话：一个以「房间」为单位、会长期记事的 AI 工作台。一个房间对应一项长期工作（比如「Agent 框架调研」「日本旅行 2026」），里面配好这个房间能用的工具、文件夹、MCP 连接器和技能；房间里的 AI 能搜网页、读网页、写文档和幻灯片、跑后台任务。聊完之后，房间把这次对话里值得记住的东西提出来，等你批准后才写进记忆。

它有四个入口，共用同一份数据目录 `~/.exxperts`：

| 入口 | 怎么拿到 | 说明 |
|---|---|---|
| 桌面应用 | Releases 下载 DMG（Mac Apple Silicon）/ EXE | Electron 封装，macOS 版已公证 |
| 浏览器 | 一行命令安装后跑 `exxperts web` | 本机起一个 Web 服务，浏览器打开 |
| 终端 | `exxperts cli` | 编码工作区 ExxCode，带仓库读写 |
| 源码 | git clone + npm | 开发者用 |

技术栈：服务端是 Fastify + WebSocket，前端是 React，桌面端是 Electron，安装包里自带 Node.js 运行时。Mac 版 DMG 279MB，命令行安装包 159MB。

### 它其实是 Pi 的分支

README 末尾写明，`runtime/` 目录派生自 Mario Zechner 的 Pi（badlogic/pi-mono，MIT，GitHub 上约 10.9 万星），从 Pi v0.70.5 分叉，分叉日期 2026-05-09。我们数了一下仓库里的 TypeScript：总共约 37 万行，其中 runtime 约 20.6 万行（含一个 2.4 万行自动生成的模型清单），EXXETA 自己写的 apps（服务端、Web 界面、桌面端，不含测试脚本）约 15.4 万行。

所以准确的定位是：**Pi 的 Agent 运行时 + EXXETA 自己做的「房间 + 受管记忆」产品层**。多模型支持、工具调用、会话压缩这些底层能力大多来自 Pi；记忆审批、房间、钱包（用量与费用统计）、远程访问这些是 EXXETA 加的。

## 记忆审批是怎么实现的？



每个房间的长期记忆是一份 Markdown 文件 `L1b/current.md`，放在 `~/.exxperts/app/personalized-agents/<房间id>/` 下，你可以直接用编辑器打开。文件固定四节：

- Chronos：这个房间历史的时间线骨架；
- Notes：按主题分组的笔记，每条笔记带一行隐藏元数据：id、保存日期、是否置顶、来自哪次对话；
- Open items：还没了结的事项；
- Waiting conversations：已经「记住」但还没「消化」的对话摘要。

被挤出记忆的笔记不会删掉，而是进 `L1b/archive/entries.md`，每条附上离开的原因，房间需要时还能查。

写入分三步，每一步都是同一个套路：**一个临时工作进程提议，你批准，系统写入，工作进程自己永远不写**。

1. Remember（记住）：一次对话结束时，工作进程把对话压成一段摘要，默认先给你看预览，你可以改、加引导语或拒绝。你在聊天里明确说过「记住这个」的内容会被识别并保留，消化时变成置顶笔记。
2. Memorize（消化）：把等待中的对话按时间顺序逐条读，每条对话生成一小串操作：新增、更新、替换、关闭待办，或者说明为什么不留。卡片上逐条显示改了什么，你可以当场改写某条笔记，或者标记「必须保留」。
3. Review（整理）：按主题整理已有笔记，找出重复、互相矛盾（同一句话换了日期、数字或加了否定）、过时的条目。整理后的文字不允许比原来更长，没被点名的笔记一个字都不会动。

工作进程是一次性的、没有任何工具的模型会话，碰不到文件，也连不了网。所有提议都标记为 `writesMemory: false`，只有「批准」这个接口会写文件，而且写之前会用指纹检查提议生成之后记忆有没有被别人改过。

### 能审计吗？能回滚吗？



可以，这是它做得最扎实的部分：

- 每次保存都先把旧的记忆文件归档（写时复制），再写一条带 SHA-256 指纹的事件记录。History 页面列出每次改动：新增、更新、移走、归档了哪些笔记，更新的笔记会把旧文本划掉放在新文本上面。
- 最近一次 Memorize 或 Review 可以撤销，官方文档说撤销会把上一版记忆按字节原样恢复，同时撤回这次保存加进归档的条目、调低这次保存抬高的预算。
- 时间旅行：记忆增长曲线上点任意一次保存，就能看到那一刻房间「知道」什么。
- 手工增删改笔记也会记进 History。

也有两个默认关闭的开关可以跳过预览（「Remember 不预览直接存」「干净的 Memorize 不出卡片」），但只要一次更新会归档笔记、超预算或有对话没处理完，照样要停下来等你。

我们没有接入真实模型去跑一轮完整的 Remember → Memorize，这部分行为以文档和测试为准。仓库在 `apps/web-server/scripts/` 下有 186 个冒烟测试，我们挑了跟记忆和安全相关的 30 个（absorb、memory、review、local-guard、remote-guard），在 Mac mini 上 95 秒跑完，30/30 通过，覆盖撤销、历史差异、预算结算、出处、检索索引等。

### 记忆预算和回忆检索

每个房间有记忆预算，默认 2 万 token（可调 1 万到 8 万），按「约 4 个字符 1 个 token」估算。超预算时，价值最低的笔记会被提议移入归档：工作习惯类笔记最值钱，事实次之，事件和已关闭事项最便宜；被检索用到过的次数也会加分。置顶笔记和待办事项永远不会被挤出去。

当问题涉及不在眼前的内容时，房间会自己去搜笔记、归档和已消化的完整对话记录。但要注意：**这是关键词检索，不是语义检索**。文档举的例子是「the roofer」找不到「Gschwendtner」，「bill」找不到「invoice」。它对德语和英语做了词形、日期、数字格式的归一（比如 12.03.2025 和 2025-03-12 算同一天），官方明说只测了德语和英语，不按空格分词的语言处理得很差，也就是说中文检索基本别指望。

### 官方自测的效果怎么看？

项目在 LongMemEval-S 上跑了 50 道题（随机种子 1），对比「房间记忆」和「把整段历史塞进提示词」，答题、消化记忆、判分都用 Claude Sonnet 5：

| | 房间记忆 | 全历史塞进提示词 |
|---|---|---|
| 50 题答对 | 43 | 41 |
| 每题 token | 约 3.3 万 | 约 16.8 万 |
| 每题费用 | 约 6 美分 | 约 42 美分 |
| 一次性建记忆 | 约 115 万 token，约 3.23 美元 | 无 |

token 省了约五分之四是实打实的，但准确率 43 比 41 在 50 题上等于打平，官方自己也这么写。另外几条局限也是官方自己列的：样本是开发期间反复用的那一批、同一个模型既答题又判分、基准是个人闲聊不是项目工作。我们再补一条：**消化记忆这一步本身要花钱**，按官方数字大约每段对话 7 美分，用 API 计费的人要算进去。

## 「nothing leaves your machine」成立吗？



分开看：

成立的部分：EXXETA 自己没有服务器夹在中间。记忆、对话、凭据、附件、房间生成的文件都以普通文件形式放在 `~/.exxperts/` 下，文件权限收紧（我们实测 auth-token 是 0600，目录是 700）。我们在代码里搜了 posthog、sentry、segment、mixpanel、amplitude 这类遥测和埋点库，应用代码里一个都没有；桌面端的更新检查源码注释写着除了版本号请求什么都不发。远程访问模式默认关闭，打开后也只走你自己的 Tailscale 私网。

我们在本机实测了服务端的边界：

| 测试 | 结果 |
|---|---|
| 监听地址（netstat） | 只有 `127.0.0.1.18787` |
| 从局域网 IP 访问 | 连不上 |
| 不带令牌访问 API | 401 |
| 伪造 `Host: evil.example.com` | 403 |
| 带 `X-Forwarded-For` 头（即使带正确令牌） | 403 |

不成立的部分：只要模型在云端，内容就会出本机。

- 对话与记忆：官方 memory.md 原话是「记忆内容会作为提示词的一部分发给你配置的模型服务商」。房间每轮都会读记忆，所以你的笔记每轮都随提示词发出去。
- 附件和工具结果：你给房间的文件、它读到的网页，进了上下文就会发给模型。
- 联网搜索：Claude 和 ChatGPT 订阅登录的房间，默认走服务商自带的搜索，搜索词在服务商那里处理，而且官方明说这部分不经过 exxperts 自己的出站参数扫描。其他模型走内置搜索：默认直接请求 DuckDuckGo 的 HTML 接口，不用 key；搜索词会发给 DuckDuckGo。
- 更新检查：桌面应用启动时和之后每 6 小时向 GitHub Releases 查一次新版本，只显示提示，不会自动安装。

所以更准确的说法是：**没有厂商云，但有模型云**。它比「把一切都存在 SaaS 上」的助手干净得多，但在接云端模型时，「数据不出本机」只对「存储」成立，对「推理」不成立。这跟我们之前拆的 Bitterbot Desktop 是同一类问题：local-first 说的是记忆放在本地，推理默认还在云端。

## 提交历史：一个人写的大部分代码

- 仓库 2026-07-07 创建，第一次提交在 2026-07-10，标题是「initial public release」，一次提交 1072 个文件、33 万行。之后到今天共 78 次提交。
- 提交者：Fernando Pastor Alonso 69 次，Borja Odriozola Schick 4 次，另外 3 人合计 5 次。README 写明产品由这两位设计和开发。
- 版本节奏很密：18 个 release，从 v0.6.8（2026-07-20）到 v0.13.2（2026-09-23）。第一个公开版本就从 0.6.8 起步，文档也提到「历史架构笔记在开发仓库的归档里」，说明真正的开发在内部仓库，公开仓库收的是大块同步：比如 9 月 15 日 memory v2 那一次提交就是 113 个文件、新增约 3.8 万行。
- CI 是真跑的：每次推送在 Ubuntu、macOS、Windows 三个平台上构建并跑冒烟测试，另有发布流水线、每周 OSV 依赖扫描、Node 版本过期检查。最近 30 次运行里有 3 次失败，都在后续提交里修好了。每个 release 附 SHA256 校验和和三份 CycloneDX SBOM。
- 27 个未关闭的 issue，大多是功能请求（按房间选模型、MCP 自定义请求头等）。

我们的判断：工程规范在同体量开源项目里算很高（安全文档、威胁模型、SBOM、三平台 CI 都齐），但它本质上是一家咨询公司两个人主导的内部产品开源版。README 还写了「这是社区版，企业版在做」，属于开源核心模式。外部贡献者很少，你要改它，基本得自己维护分支。

## 我们在 Mac 上实测了什么？

环境：Mac mini（Apple Silicon），macOS，Node v26.9.0、npm 11.19.1；仓库 commit `6e8371f`（v0.13.2 之后一次提交）。全程不装全局依赖，数据目录用临时 HOME 隔离。

| 步骤 | 结果 |
|---|---|
| `npm ci`（跳过 Chromium 和 Electron 下载） | 849 个包，15 秒，node_modules 661MB |
| `npm run build` | 通过，约 8 秒 |
| 30 个记忆与安全冒烟测试 | 30/30 通过，95 秒 |
| 启动 `exxperts web` 并用 curl 探测 | 见上一节表格，边界行为与 SECURITY.md 一致 |
| 用模拟的 Ollama 接口测「添加网关」 | 能接 `http://127.0.0.1` 地址，但有两个坑，见下 |

本机没有装 Ollama，所以我们用 Python 写了一个假的 OpenAI 兼容接口（只回 `/v1/models`，列出 `qwen3:8b` 和 `nomic-embed-text` 两个模型），让 exxperts 的「添加网关」去探测它。发现三件事：

1. 明文 http 的本机地址可以接，校验只要求以 http:// 或 https:// 开头。
2. API key 不能留空。留空直接返回「Enter the gateway API key to load its models」。Ollama 本身不需要 key，随便填一个字符串就行，我们填 `ollama`，它以 `Bearer ollama` 发了过去。
3. 嵌入模型也出现在可选列表里。它只会排除网关明确声明为非聊天的模型，Ollama 的 `/v1/models` 不声明，所以 `nomic-embed-text` 会混进来，别点批准。上下文窗口也探测不到，表单默认填 128000。

第 3 点是接本地模型时最该注意的坑，下一节细说。

## Mac 用户怎么装？怎样才算真正全本地？



安装，二选一：

- 桌面版：Releases 下载 `exxperts-desktop-mac-arm64.dmg`（279MB），已经过 Apple 公证，双击打开。只支持 Apple Silicon，Intel Mac 需要从源码构建。
- 命令行：`curl -fsSL https://raw.githubusercontent.com/EXXETA/exxperts/main/install.sh | bash`，再跑 `exxperts web`。建议先把 install.sh 下载下来读一遍再执行。装完可以跑 `exxperts doctor` 体检。

两种方式共用 `~/.exxperts`，同一时间只跑一个服务。

接 Ollama 做到全本地，按这个顺序：

1. 先让 Ollama 用够大的上下文启动，例如 `OLLAMA_CONTEXT_LENGTH=32768 ollama serve`。原因：房间记忆预算默认 2 万 token，再加系统提示词和对话，小上下文根本装不下。exxperts 靠你填的上下文窗口判断装不装得下，默认按 128000 算，如果 Ollama 实际只开了几千，就可能出现提示词被悄悄截断、它自己却不知道的情况。这是我们根据代码和 Ollama 行为做的推断，没有用真模型复现。
2. AI setup → Add another provider → Add gateway：地址填 `http://localhost:11434/v1`，key 随便填（比如 `ollama`），Load models。
3. 只批准支持函数调用的聊天模型（官方明说房间每轮都要调工具，不支持函数调用的模型别选）；**把「Context window」改成你在第 1 步实际开的值**；嵌入模型不要批准；再选一个模型负责 Memorize 和 Review。
4. AI setup → Web search 选「关闭」，或者用 `exxperts setup search` 起一个本机 SearXNG 容器（需要 Docker 或 OrbStack）。注意 SearXNG 也是替你去查公网搜索引擎，搜索词照样出本机，只是不直接暴露给单一搜索引擎。要彻底不出网，就关掉搜索。
5. LM Studio 同理，地址换成 `http://localhost:1234/v1`。

做完这些，推理、记忆、搜索都不出本机，剩下的只有桌面版查更新这一个请求。

要提醒的是：官方所有效果数据都是在 Claude 上测的，消化记忆默认也跑在 Opus 5.5 上。消化和整理要求模型按格式输出一串结构化操作，小模型能不能稳定做好，官方没测，我们也没测。16GB 内存的 Mac 跑 8B 左右的模型做日常对话可以，但别指望记忆质量和官方数字一样。

## 跟其他带记忆的 Agent 比，它的区别在哪？

核心区别只有一个：**谁有权往记忆里写东西**。

| 项目 | 形态 | 记忆由谁写 | 记忆存在哪 | 本站判断 |
|---|---|---|---|---|
| exxperts | 桌面/Web 应用，单用户 | 人批准后系统写 | 本机 Markdown + 归档 + 事件记录 | 可审计、可撤销最强；检索只有关键词 |
| Letta（原 MemGPT） | Agent 服务端 + SDK，约 2.5 万星，Apache-2.0 | 模型通过工具自己改记忆块 | 数据库 | 给开发者搭 Agent 的框架，不是给终端用户的应用 |
| Mem0 | 记忆层库/API，约 6.6 万星，Apache-2.0 | 大模型从对话里自动抽取 | 向量库等后端 | 嵌进你自己产品的组件，默认自动写 |
| Bitterbot Desktop | 桌面 Agent，2459 星，MIT | 每 2 小时自动「做梦」整理 | 本地 | 记忆本地、推理默认云端，带实验性技能市场 |
| OpenMuse | 个人助理模板，MIT，Alpha | 由接入的 Agent 后端决定 | 自部署 | 重点在持久浏览器和后台任务，不在记忆治理 |

简单说，Letta 和 Mem0 是给开发者的积木，默认让模型自动记；exxperts 是给终端用户的成品，默认一个字都不自动记。如果你怕 AI 把错的东西记下来、越记越偏，或者在企业里需要说清楚「AI 为什么知道这件事」，exxperts 的做法最稳；如果你想要的是开箱即用、少点按钮，每次都要审批会显得啰嗦。

## 适合谁，不适合谁？

适合：

- 需要长期跟进多个项目、又不放心 AI 自动记忆的个人或顾问；
- 企业里要求「AI 知道什么必须能追溯」的场景，它的出处、历史、撤销正对这个需求；
- 已经有 Claude 或 ChatGPT 订阅、想要一个带长期记忆的桌面工作台的人（可以直接用订阅登录，不必另买 API）。

不适合：

- 主要用中文工作的人：记忆检索不支持中文分词，官方只测了德语和英语；
- 想要零点击、全自动记忆的人；
- 要在服务器上多人共用的团队：官方明确只支持单用户本机，反向代理和对外暴露端口都不支持，而且会主动拒绝带代理头的请求。

## 常见问题

Q：exxperts 收费吗？
A：社区版 Apache-2.0，个人和商用都免费。模型费用自己付：用 Claude/ChatGPT 订阅，或者自带 API key。官方说企业版在做。

Q：它和 Claude Code、Codex 这类编程 Agent 是什么关系？
A：它的终端入口 ExxCode 是编程工作区，底层运行时来自 Pi，本身就是一个编程 Agent 框架。但产品重心是「房间 + 受管记忆」的知识工作，不是写代码。

Q：记忆文件能用 Obsidian 之类的工具直接看吗？
A：能，`L1b/current.md` 就是普通 Markdown。但手工改文件不会记进 History，建议在应用里的 Room settings → Memory 编辑，改动才会留痕、可撤销。

Q：房间能执行命令吗？危险吗？
A：只有「完全访问」模式的房间能用 Bash，默认每条命令都弹卡片让你确认；「受限工作区」模式把文件工具关在一个文件夹里，敏感文件（密钥、`.git`）碰不到。远程设备不能把房间切成自动执行。

Q：「数据不出本机」到底能不能信？
A：存储层面能信，我们没在代码里找到遥测库，服务也只监听本机。推理层面取决于你选的模型：接云端模型，内容就会发给模型厂商；接 Ollama/LM Studio 并关掉搜索，才是真正不出本机。

Q：Windows 和 Linux 能用吗？
A：能。Windows 有签名安装包，Linux 有 x64 命令行包，CI 在三个平台上都跑测试。桌面版目前只有 Mac Apple Silicon 和 Windows x64。

## 一手源

- GitHub 仓库：https://github.com/EXXETA/exxperts
- 记忆机制文档：https://github.com/EXXETA/exxperts/blob/main/docs/memory.md
- 工作原理文档：https://github.com/EXXETA/exxperts/blob/main/docs/how-exxperts-works.md
- 联网搜索文档：https://github.com/EXXETA/exxperts/blob/main/docs/web-search.md
- 模型服务商配置：https://github.com/EXXETA/exxperts/blob/main/docs/provider-setup.md
- 安全与威胁模型：https://github.com/EXXETA/exxperts/blob/main/SECURITY.md
- 上游 Pi：https://github.com/badlogic/pi-mono
- Releases：https://github.com/EXXETA/exxperts/releases

本文为开源项目客观拆解，开源仅供学习研究参考，不构成使用或投资建议。

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

> 📌 Repository: EXXETA/exxperts
> GitHub: https://github.com/EXXETA/exxperts
> License: Apache-2.0 | Language: TypeScript | Stars: 357 | Created: 2026-07-07 | Latest release: v0.13.2 (2026-09-23)

---

**BLUF**: exxperts is an AI assistant that runs on your own computer, made by the German consultancy EXXETA. What sets it apart from other "agents with memory" is that **the model does not decide what to remember: every write to memory needs your approval in the UI**. The memory itself is a Markdown file on your disk you can open directly, and every save is archived, can be undone, and can be replayed as of any day. We built it from source on a Mac mini and ran the 30 memory and security smoke tests that ship with the repo: 30 of 30 passed. With the server running, curl confirmed it listens only on 127.0.0.1, returns 401 without a token, and returns 403 for a forged Host header or proxy headers.

Its slogan, "nothing leaves your machine", needs a discount, though. The README sentence continues "unless you send it": as long as you use a cloud model such as Claude or ChatGPT, your conversations, memory content, attachments and tool results go to the model provider inside the prompt, and the project's own memory.md says so. Fully local use requires Ollama or LM Studio, with web search switched off or pointed at a self-hosted SearXNG.

This post covers four things: what it is, how the memory approval actually works, when data leaves your machine, and how Mac users can install it and connect a local model.

## What is exxperts?

In one sentence: an AI workbench organized into "rooms" that keeps long-term notes. A room corresponds to an ongoing piece of work (say "Agent frameworks research" or "Trip: Japan 2026") and holds the tools, folders, MCP connectors and skills that room may use. The AI in a room searches and reads the web, writes documents and slide decks, and runs background tasks. When a conversation ends, the room proposes what is worth keeping, and nothing is written to memory until you approve it.

It has four entry points sharing one data directory, `~/.exxperts`:

| Entry point | How to get it | Notes |
|---|---|---|
| Desktop app | DMG (Mac Apple Silicon) / EXE from Releases | Electron; the macOS build is notarized |
| Browser | One-line install, then `exxperts web` | Starts a local web server and opens your browser |
| Terminal | `exxperts cli` | The ExxCode coding workspace, with repo access |
| Source | git clone + npm | For developers |

The stack: a Fastify + WebSocket server, a React front end, an Electron desktop shell, and a bundled Node.js runtime in the release packages. The Mac DMG is 279 MB; the command-line archive is 159 MB.

### It is actually a fork of Pi

The end of the README says the `runtime/` directory is derived from Pi by Mario Zechner (badlogic/pi-mono, MIT, about 109,000 stars on GitHub), forked from Pi v0.70.5 on 2026-05-09. We counted the TypeScript in the repo: about 370,000 lines in total, of which the runtime is about 206,000 (including a 24,000-line generated model catalog), and EXXETA's own apps (server, web UI, desktop, excluding test scripts) are about 154,000.

So the accurate description is **Pi's agent runtime plus EXXETA's own product layer of rooms and governed memory**. Multi-provider support, tool calling and session compaction come largely from Pi; memory approval, rooms, the wallet (usage and cost tracking) and remote access are EXXETA's additions.

## How does the memory approval work?



Each room's long-term memory is one Markdown file, `L1b/current.md`, under `~/.exxperts/app/personalized-agents/<room-id>/`, and you can open it in any editor. It has four fixed sections:

- Chronos: a temporal spine of the room's history;
- Notes: notes grouped by topic, each with a hidden metadata line: id, the day it was saved, whether it is pinned, and the conversation it came from;
- Open items: loops that are still open;
- Waiting conversations: summaries of conversations you remembered but have not memorized yet.

Notes pushed out of memory are not deleted. They go to `L1b/archive/entries.md` with the reason they left, and the room can still read them when it needs to.

Writing happens in three steps, all on the same contract: **a temporary worker proposes, you approve, the system writes, and the worker never writes anything itself**.

1. Remember: at the end of a conversation, a worker compresses it into a summary, shown as a preview by default. You can edit it, add a steering note, or reject it. Anything you explicitly asked the room to remember in chat is detected and carried through, and becomes a pinned note when memorized.
2. Memorize: reads the waiting conversations one at a time, in chronological order. For each, it proposes a short list of operations: add, update, supersede, close an open item, or let it go with a reason. The card shows what each conversation changed; you can rewrite a note on the spot or mark one as must-keep.
3. Review: tidies existing notes topic by topic, finding duplicates, contradictions (the same words with a different date, number or negation), and stale entries. A tidied note may not end up longer than what it replaced, and a note the review does not name is never touched.

Workers are one-shot model sessions with no tools at all: they cannot touch files or the network. Every proposal is marked `writesMemory: false`; only the approval endpoint writes files, and before writing it checks fingerprints to detect whether memory changed since the proposal was made.

### Can you audit it? Can you roll it back?



Yes, and this is the most solid part of the project:

- Every save first archives the previous memory file (copy-on-write) and then writes an event record with SHA-256 fingerprints. The History page lists every change: which notes a save added, updated, moved or archived, with an updated note's old text struck through above the new text.
- The latest Memorize or Review can be undone. The docs say undo restores the previous memory byte for byte, takes back the archive rows that save added, and lowers a budget that save raised.
- Time travel: click any save on the memory growth chart to see what the room "knew" at that moment.
- Hand edits to notes are recorded in History too.

Two toggles, off by default, let you skip the preview ("Remember: save without the preview" and "Memorize: save a clean update without the card"). But any update that archives notes, crosses the budget, or leaves a conversation unfinished still stops and waits for you.

We did not connect a real model to run a full Remember → Memorize round, so for that behavior we rely on the docs and tests. The repo ships 186 smoke tests under `apps/web-server/scripts/`. We picked the 30 related to memory and security (absorb, memory, review, local-guard, remote-guard) and ran them on the Mac mini in 95 seconds: 30 of 30 passed, covering undo, history diffs, budget settlement, provenance and the search index.

### Memory budget and recall

Each room has a memory budget: 20,000 tokens by default, adjustable from 10,000 to 80,000, estimated at about four characters per token. When a save would exceed it, the lowest-value notes are proposed for the archive. Working-style notes are worth the most, facts less, events and closed items the least, and each time a note was actually recalled counts in its favor. Pinned notes and open items never get pushed out.

When a question concerns something not in view, the room searches its notes, its archive and the full transcripts of memorized conversations on its own. Note, though: **this is keyword search, not semantic search**. The docs' own example: "the roofer" does not find "Gschwendtner", and "bill" does not find "invoice". It normalizes word forms, dates and number formats for German and English (12.03.2025 and 2025-03-12 count as the same day). The docs say only German and English were measured and that languages written without spaces between words are handled poorly, so Chinese or Japanese recall is not something to count on.

### How to read the project's own benchmark

The project ran 50 questions from LongMemEval-S (seed 1), comparing room memory against pasting the whole history into the prompt, with Claude Sonnet 5 answering, memorizing and judging:

| | Room memory | Full history in the prompt |
|---|---|---|
| Correct of 50 | 43 | 41 |
| Tokens per question | about 33,000 | about 168,000 |
| Cost per question | about 6 cents | about 42 cents |
| One-time memory build | about 1.15M tokens, about $3.23 | none |

The roughly four-fifths token saving is real, but 43 versus 41 out of 50 is a tie, and the project says so itself. It also lists its own limits: the sample was the one used during development, the same model answers and judges, and the benchmark is personal chat rather than project work. We would add one more: **memorizing itself costs money**, about 7 cents per conversation by the project's numbers, which matters if you pay per API token.

## Does "nothing leaves your machine" hold?



Take it in two parts.

What holds: there is no EXXETA server in the middle. Memory, conversations, credentials, attachments and the files a room produces are plain files under `~/.exxperts/` with tightened permissions (we saw the auth-token file at 0600 and directories at 700). We searched the code for telemetry and analytics libraries such as posthog, sentry, segment, mixpanel and amplitude and found none in the application code; the desktop update checker's source comment says nothing but the version request ever leaves the machine. Remote mode is off by default, and when turned on it only serves your own devices over your own Tailscale network.

We tested the server boundary locally:

| Test | Result |
|---|---|
| Listening address (netstat) | Only `127.0.0.1.18787` |
| Access from the LAN IP | Unreachable |
| API request without a token | 401 |
| Forged `Host: evil.example.com` | 403 |
| `X-Forwarded-For` header (even with a valid token) | 403 |

What does not hold: once the model is in the cloud, content leaves your machine.

- Conversations and memory: memory.md says verbatim that "memory content is sent to your configured model provider as part of prompts". The room reads its memory every turn, so your notes go out with every prompt.
- Attachments and tool results: files you hand a room and pages it reads go to the model once they are in context.
- Web search: rooms signed in with a Claude or ChatGPT subscription use the provider's own search by default, so search terms are handled by the provider, and the docs state that this path does not pass through exxperts' own outbound-argument scanning. Other models use the built-in search, which by default queries DuckDuckGo's HTML endpoint directly with no key, so search terms go to DuckDuckGo.
- Update checks: the desktop app asks GitHub Releases for a newer version at launch and every six hours after; it only shows a notice and installs nothing by itself.

A more accurate version of the claim: **no vendor cloud, but a model cloud**. It is much cleaner than assistants that keep everything in a SaaS backend, but with a cloud model, "nothing leaves your machine" holds for storage, not for inference. This is the same pattern we found in Bitterbot Desktop: "local-first" means memory is stored locally, while reasoning defaults to the cloud.

## Commit history: mostly one person's code

- The repo was created on 2026-07-07. The first commit, on 2026-07-10, is titled "initial public release" and adds 1,072 files and 330,000 lines in one commit. There are 78 commits to date.
- Committers: Fernando Pastor Alonso with 69, Borja Odriozola Schick with 4, and three others with 5 between them. The README credits these two with designing and building the product.
- Releases come fast: 18 of them, from v0.6.8 (2026-07-20) to v0.13.2 (2026-09-23). The first public version already started at 0.6.8, and the docs mention "historical architecture notes live in the development repository's archive", which means real development happens in an internal repo and the public one receives large syncs. The memory v2 commit on September 15, for example, touched 113 files and added about 38,000 lines.
- CI really runs: every push builds and runs smoke tests on Ubuntu, macOS and Windows, plus a release pipeline, a weekly OSV dependency scan and a Node version currency check. Three of the last 30 runs failed, all fixed in later commits. Each release ships SHA256 checksums and three CycloneDX SBOMs.
- There are 27 open issues, mostly feature requests (per-room model selection, custom headers on MCP connectors, and so on).

Our read: the engineering discipline is high for a project this size (a security doc, a threat model, SBOMs and three-platform CI are all there), but at heart it is the open edition of an internal product led by two people at a consultancy. The README also says "this repository is the exxperts Community Edition; an Enterprise version is in the works", which is an open-core model. Outside contributions are few, so if you want to change it, expect to maintain your own fork.

## What did we test on a Mac?

Environment: Mac mini (Apple Silicon), macOS, Node v26.9.0, npm 11.19.1; repo at commit `6e8371f` (one commit after v0.13.2). No global installs; the data directory was isolated under a temporary HOME.

| Step | Result |
|---|---|
| `npm ci` (Chromium and Electron downloads skipped) | 849 packages, 15 s, node_modules 661 MB |
| `npm run build` | Passed, about 8 s |
| 30 memory and security smoke tests | 30/30 passed, 95 s |
| Start `exxperts web` and probe with curl | See the table above; boundaries match SECURITY.md |
| "Add gateway" against a mock Ollama endpoint | Accepts an `http://127.0.0.1` address, with the pitfalls below |

Ollama is not installed on this machine, so we wrote a fake OpenAI-compatible endpoint in Python (it only answers `/v1/models`, listing `qwen3:8b` and `nomic-embed-text`) and pointed exxperts' "Add gateway" at it. Three findings:

1. A plain-http local address is accepted; validation only requires the URL to start with http:// or https://.
2. The API key cannot be empty. Leaving it blank returns "Enter the gateway API key to load its models". Ollama does not need a key, so any string works; we entered `ollama` and it was sent as `Bearer ollama`.
3. Embedding models show up in the approvable list. It only excludes models the gateway explicitly declares as non-chat, and Ollama's `/v1/models` declares nothing, so `nomic-embed-text` appears; do not approve it. The context window is not detected either, and the form defaults to 128,000.

Point 3 is the biggest pitfall with local models; more on it next.

## How should Mac users install it, and what does fully local take?



Install, either way:

- Desktop: download `exxperts-desktop-mac-arm64.dmg` (279 MB) from Releases. It is notarized by Apple and opens with a double-click. Apple Silicon only; Intel Macs have to build from source.
- Command line: `curl -fsSL https://raw.githubusercontent.com/EXXETA/exxperts/main/install.sh | bash`, then `exxperts web`. We suggest downloading install.sh and reading it before running it. Afterwards, `exxperts doctor` checks the install.

Both share `~/.exxperts`, and only one server runs at a time.

Going fully local with Ollama, in this order:

1. Start Ollama with a large enough context, e.g. `OLLAMA_CONTEXT_LENGTH=32768 ollama serve`. Why: a room's memory budget defaults to 20,000 tokens, plus system prompt and conversation, and a small context cannot hold that. exxperts decides whether things fit based on the context window you entered, 128,000 by default; if Ollama actually runs with a few thousand, the prompt may be silently truncated without exxperts knowing. This is our inference from the code and Ollama's behavior; we did not reproduce it with a real model.
2. AI setup → Add another provider → Add gateway: base URL `http://localhost:11434/v1`, any key (e.g. `ollama`), then Load models.
3. Approve only chat models that support function calling (the docs say rooms call tools every turn, so models without function calling are poor choices). **Set "Context window" to the value you actually configured in step 1.** Do not approve embedding models. Pick a model to run Memorize and Review.
4. In AI setup → Web search, choose "off", or run `exxperts setup search` to start a local SearXNG container (needs Docker or OrbStack). Note that SearXNG still queries public search engines on your behalf, so search terms still leave the machine, just not to one engine directly. To keep everything offline, turn search off.
5. LM Studio works the same way at `http://localhost:1234/v1`.

With that, inference, memory and search all stay local; the only remaining request is the desktop app's update check.

One caveat: all of the project's quality numbers were measured on Claude, and Memorize defaults to Opus 5.5 on the Claude profile. Memorize and Review require the model to emit a structured list of operations; whether small models do that reliably was not measured by the project, and not by us either. A 16 GB Mac can run a model around 8B for everyday chat, but do not expect memory quality to match the published numbers.

## How does it differ from other agents with memory?

The core difference is one question: **who is allowed to write to memory**.

| Project | Shape | Who writes memory | Where it lives | Our take |
|---|---|---|---|---|
| exxperts | Desktop / web app, single user | The system, after human approval | Local Markdown + archive + event records | Strongest auditability and undo; keyword-only recall |
| Letta (formerly MemGPT) | Agent server + SDK, ~25K stars, Apache-2.0 | The model edits its memory blocks via tools | Database | A framework for developers building agents, not an end-user app |
| Mem0 | Memory layer library/API, ~66K stars, Apache-2.0 | An LLM extracts memories from conversations automatically | Vector store and other backends | A component to embed in your own product; writes automatically by default |
| Bitterbot Desktop | Desktop agent, 2,459 stars, MIT | Automatic "dreaming" every 2 hours | Local | Local memory, cloud-default inference, experimental skill market |
| OpenMuse | Personal assistant template, MIT, alpha | Depends on the plugged-in agent backend | Self-hosted | Focus on a persistent browser and background tasks, not memory governance |

Put simply, Letta and Mem0 are building blocks for developers that let the model remember automatically; exxperts is a finished product for end users that remembers nothing automatically. If you worry about an AI memorizing wrong things and drifting, or you work somewhere that must explain "why does the AI know this", exxperts' approach is the safest. If you want zero clicks, approving every save will feel tedious.

## Who is it for, and who should skip it?

Good fit:

- Individuals or consultants tracking several long-running projects who do not trust automatic AI memory;
- Organizations that need every piece of AI knowledge to be traceable; its provenance, history and undo target exactly that;
- People who already pay for Claude or ChatGPT and want a desktop workbench with long-term memory (you can sign in with the subscription instead of buying API access).

Poor fit:

- People who work mainly in Chinese, Japanese or other unspaced languages: recall does not segment them, and only German and English were measured;
- People who want zero-click, fully automatic memory;
- Teams wanting a shared server: the project supports only single-user local use, does not support reverse proxies or exposed ports, and actively refuses requests carrying proxy headers.

## FAQ

Q: Does exxperts cost anything?
A: The Community Edition is Apache-2.0, free for personal and commercial use. You pay for models yourself, via a Claude/ChatGPT subscription or your own API key. The project says an Enterprise version is in the works.

Q: How does it relate to coding agents like Claude Code or Codex?
A: Its terminal entry, ExxCode, is a coding workspace, and the underlying runtime comes from Pi, which is itself a coding-agent framework. But the product's focus is knowledge work in rooms with governed memory, not writing code.

Q: Can I read the memory file in Obsidian or similar tools?
A: Yes, `L1b/current.md` is plain Markdown. But editing the file by hand is not recorded in History; edit in Room settings → Memory inside the app so changes are tracked and undoable.

Q: Can rooms run shell commands? Is that risky?
A: Only rooms in "Full access" mode can use Bash, and by default every command shows an approval card first. "Bounded workspace" mode fences the file tools to one folder, with sensitive files (keys, `.git`) out of reach. Remote devices cannot switch a room to auto-run.

Q: Can I trust "nothing leaves your machine"?
A: For storage, yes: we found no telemetry libraries in the code, and the server listens only locally. For inference, it depends on your model: with a cloud model, content goes to the provider; with Ollama/LM Studio and search turned off, nothing leaves.

Q: Does it work on Windows and Linux?
A: Yes. Windows has a signed installer, Linux has an x64 command-line package, and CI runs tests on all three platforms. The desktop app currently ships for Mac Apple Silicon and Windows x64 only.

## Primary sources

- GitHub repository: https://github.com/EXXETA/exxperts
- Memory docs: https://github.com/EXXETA/exxperts/blob/main/docs/memory.md
- How it works: https://github.com/EXXETA/exxperts/blob/main/docs/how-exxperts-works.md
- Web search docs: https://github.com/EXXETA/exxperts/blob/main/docs/web-search.md
- Provider setup: https://github.com/EXXETA/exxperts/blob/main/docs/provider-setup.md
- Security and threat model: https://github.com/EXXETA/exxperts/blob/main/SECURITY.md
- Upstream Pi: https://github.com/badlogic/pi-mono
- Releases: https://github.com/EXXETA/exxperts/releases

This is an objective teardown of an open-source project. Open source is shared for learning and research only; this is not a recommendation to use or invest.

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
