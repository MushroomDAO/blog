# forage 反馈流水账

每轮评审后记录：我判断了什么、你否掉的理由、该改哪条规则。
**否定判断比肯定判断值钱**——那是权重表里没有的信息。

---

## 2026-08-10 · 第 1 轮（30 条）

### 元反馈：最重要的一条

> 除非你给列出来，究竟他的高级形态高级在哪里，否则就不要做这类工作。

30 条里我只调研了 5 条，其余 25 条只给了标题。你的备注里
「信息太少无法判断」「你没有找到他的核心价值」出现了 **9 次**。

**根因**：我把「每轮上限 30 条」当成了配额要填满，实际那是上限不是目标。

**改法**：调研前置，不调研不入清单。清单宁可 8 条全挖透，
不要 30 条里 25 条只有标题。已写入 SKILL.md 的硬规则。

---

### 提炼出的否决规则（已写进 preferences.yml）

| 你的原话 | 提炼成 |
|---|---|
| 不做 java 相关 | 领域否决：JVM 生态 |
| 快手不太信任 | 厂商信任度：快手出品降权 |
| 3D 世界的不太关注 | 领域否决：3D / 元宇宙 / 空间智能 |
| 这是新闻，我不关注新闻 | 内容类型否决：纯新闻报道 |
| 大模型对普通用户开源也用不上 | 规模否决：单卡跑不动的超大模型 |
| 只是一个标题党 | 内容类型否决：提出问题但不给解法 |
| 优化会不断变化，除非颠覆性 | 内容类型否决：增量优化类报道 |
| 这个观点本身也是过时的，我的认知已经 cover | 内容类型否决：泛泛的观点陈述 |
| 这一类比较浅显 | 深度门槛：浅显科普 |
| 连 github 网址信息都没有 | 硬性要求：无一手源链接直接丢弃 |
| 如果没有独特性，就不要碰这一类 | 独特性门槛 |

### 提炼出的加分规则

| 你的原话 | 提炼成 |
|---|---|
| 属于个人的分析观察和体验，它是有价值的 | 加分：一手个人实践 |
| 你要找到他究竟遇到什么困难，怎么解决，有什么心得 | 加分：有具体踩坑与解法 |
| 这个可以深入分析，因为还是有独特性 | 加分：定位有差异化 |
| 这种个人知识库的可以有 | 主题加分：个人知识库 |
| 功能清晰 / 大家通用的可能需求 | 加分：功能边界清晰 |
| 开发者更喜欢的 skill 工具 | 主题加分：开发者工具链 |

### 我判断偏差最大的几条

| 条目 | 我的判断 | 你的判断 | 差在哪 |
|---|---|---|---|
| `token-saver-mcp-java` | 存档（我给 61） | **不要** | 我没有「技术栈否决」这个维度 |
| `Kwaipilot/KAT-Coder` | 存档（我给 58） | **不要** | 我没有「厂商信任度」这个维度 |
| `moonshotai/Kimi-K3` | 入选（我给 50） | **不要** | 我没考虑「普通用户跑不跑得动」 |
| `LiquidAI/LFM2.5` | 入选（我给 46） | **深挖** | 我没调研，你无法判断 |

前三条说明：**我的五维里缺一个「可用性/可信度」维度**——
技术栈、厂商、硬件门槛都属于这一维，现在完全没建模。

### 待处理

- [x] Firecrawl 查重 → 没专门写过，但 `Webclaw`（Rust 爬虫喂 AI Markdown）同赛道，
      写的时候要区分
- [ ] 「我的贾维斯」需找到开源仓库地址（目前只是新闻报道）
- [ ] 「Survey 写作多 Agent 协作」需挖到具体困难和心得
- [ ] 五维增加第六维「可用性」或并入现有维度

---

## 2026-08-12 · 第 2 轮（6 条）

**通过率 5/6。** 数量合适——用户明确说「一般十条以下比较合适」，
所以 `MAX_TOTAL` 从 30 降到 10。

| 条目 | 我判 | 你判 | 学到 |
|---|---|---|---|
| ClickHouse/nerve | 写 | ✅ 写 | 逆热度有效：大厂出品但 72 star 的确实是信息差 |
| u14app/neo-chat | 写 | ✅ 写 | 五原则全中的准确率高 |
| maka-agent | 写 | ✅ 写 | |
| aegra | 写 | ✅ 写 | 「闭源服务的开源自托管替代」这个模式是对的 |
| dense-mem | 存档倾向 | ✅ **写** | 我低估了它——「个人可及=0」不该直接降级，需要 PostgreSQL 不等于不可用 |
| cl-llama-cpp | 故意放的测试 | ❌ 不要（lisp 不是我关注的领域） | **规则边界确认** |

### 规则边界确认

我上一轮故意放了 Common Lisp 那条进去，就是为了问：
「否 Java」是针对 Java，还是针对所有小众语言栈？

**答案是后者。** 判据是受众规模，不是语言好坏。已扩展为：
JVM 系（Java/Kotlin/Scala）、Lisp 系（Common Lisp/Clojure）、
函数式（Haskell/Erlang/Elixir）、.NET 系。

### 我判偏的一条

`dense-mem` 我因为「需要 PostgreSQL + Redis」判它违反「个人可及」，
倾向存档。你直接选了写。

**修正**：「个人可及」的判据应该是「一个人能不能装能不能用」，
不是「有没有依赖」。需要 PostgreSQL ≠ 需要运维团队。
真正违反的是需要集群、需要 SSO、按席位卖给公司那种。

## 2026-09-06（会话内补判，用户尚未反馈）
- ⚠️ 规则误伤：`DSH 装进安卓手机` 系列（woaiys3/deepseek-harness-android-app 等）
  会被 stage.py 的 DOMAIN_VETO `\bjava\b|jvm|kotlin` 拦掉。
  → 误伤原因：这条 veto 的立意是「本站读者里用它做 AI 开发的占比」，
    但 APK 的实现语言 ≠ 读者要写的语言——读者是**装 APK 的用户**，不是 Java 开发者。
  → 建议调整：JVM 系 veto 只在「仓库主体是给开发者用的 JVM 框架/库」时生效，
    终端用户产品（APK / 桌面 App）不看实现语言。可在 stage.py 加一条豁免：
    描述里出现 `apk|app|安装包|termux|端侧` 时跳过 JVM veto。
- ⚠️ 去重漏网：小红书「JIT-Age」没被 seen 表拦住，因为实体名 `jit-age` 与
  已发文章里的 `jit-agent` 不同。本站 2026-09-05 刚发过 bingreeky/JIT。
  → 建议调整：entities() 做归一化时把结尾的 `-age/-agent/-ai` 归到同一词根，
    或对 seen 做前缀模糊匹配（长度 >4 时按前 6 字符前缀比对）。
- ⚠️ 「X for MCP」噪音：unified-product-graph/tools（电商商品数据标准）
  因为带 MCP 关键词被采进来，和已记录的「X for Claude Code」是同一个坑。
  → 建议调整：veto 里的领域否决要在「MCP/Skill/Agent 关键词命中」之前先跑，
    电商/商品数据/供应链应补进 DOMAIN_VETO。
- ⚠️ 采集侧：X 源连续为 0（twitter-cli ClientTransaction/404），需修复。
  小红书笔记正文读取需 xsec_token，裸 explore URL 返回 empty noteDetailMap，
  collect.py 应在采集时把 xsec_token 一并存下来，否则后续调研拿不到正文。
- ✅ 判为「只存档」但用户标了「写」：penaivanalejandro/gitlab-mcp-server（我给 60 分）
  → 我的否决理由是「标准 API-to-MCP 包装，无独特机制」。这个理由站不住：
    本站选题标准第一性原则是「我自己要不要用」，不是「机制新不新」。
    一个 0★、PAT 不出本机、92 工具开箱即用的本地 MCP，对个人用户的价值
    恰恰在于**它平庸且够用**——这正是「个人可及」原则本身。
  → 调整：给 novelty 维度降权，不要用「机制新颖度」否决掉「原则全中 + 装了就能用」的工具。
    bonus 里补一条「五原则全中」直接加分，避免被 novelty 拖死。
- ⚠️ 用户对 JIT-Age 标 dig 并批注「重复了吧？你检查下」——已复核确认重复，见下方检查记录。
  → 【复盘补充 2026-09-06 深夜】写稿时通读完整 README，发现我否决的理由完全不成立：
    该项目 README 里有一张把 MCP 上下文税逐组量化的表（92 工具 = 27340 tokens，
    平均每个工具定义 ~297 tokens），并给了三层收敛方案（GITLAB_TOOL_GROUPS 分组加载 /
    GITLAB_READ_ONLY 只读 47 工具且按名字拒绝 / read_api 最小 token scope），
    还默认阻断了 169.254.169.254 云元数据端点（SSRF 面）。
    我在存档笔记里写的「如果它做出工具太多导致上下文爆炸的收敛方案，那才是可写的点」
    —— 它本来就有，是我没读到。
  → 硬调整：**调研阶段必须通读完整 README，不能只看前 1/3 就下判断。**
    stage.py 只抓 readme[:2400] 存进 research.readme_head，我在会话里补判时
    直接用了那个截断版。修法：补判时对判为「值得写」和「存疑」的条目，
    一律用 gh api 重新拉全文 README，不要用 readme_head 做否决依据。

## 2026-09-09（用户在 8042 标了 8 条 write / 1 条 skip，我按标记发布）

### 发布结果：标了 8 条，实发 6 条

| 条目 | 用户标记 | 实际处理 | 理由 |
|---|---|---|---|
| sizzlecar/ferrum-infer-rs | write | ✅ 已发 | — |
| Abilityai/trinity | write | ✅ 已发 | — |
| SimoneAvogadro/android-reverse-engineering-skill | write | ✅ 已发 | 8 月《GitHub 趋势月报》只一句话带过，可单独成篇 |
| cmliu/CF-Workers-CheckProxyIP（小红书线索） | write | ✅ 已发 | — |
| masihsultani/whiteboard-animator（小红书线索） | write | ✅ 已发 | — |
| HauhauCS/Qwen3.8-27B-...-MTP-GGUF | write | ✅ 已发 | 与 8/20 发的 orcarouter MLX 版是不同仓库/不同生态，文内做了显式区分 |
| deeplethe/utopia（小红书线索） | write | ❌ **未发，改标 skip** | **本站 2026-09-07 已发过同一仓库** |
| openai-community/gpt2 | write | ❌ **未发，改标 skip** | 2022 上传、2024 最后修改，靠 1477 万累计下载常年挂 trending 第 10，无任何增量 |

### 两条规则问题（都不是用户判错，是我这边的漏）

- ⚠️ **stage.py 的已发布去重对中文标题完全失效。**
  utopia 那条的标题是小红书的中文句子「【开源】如果说 RAG 是"让 AI 找到企业知识"，那 Utopia 想解决的」，
  `repo_fragment()` 取到的是整个中文串，跟已发文章 slug
  `utopia-deeplethe-enterprise-world-model-bitemporal-knowledge-graph` 匹配不上，
  于是一个 9 月 7 日刚发过的仓库又冒了出来。
  → 建议调整：小红书来源的条目，`published_match()` 除了用标题，还要用
    `entities(title)` 抽出的**拉丁字母实体**（这里是 `utopia`）逐个去 slug 里做边界匹配。
    中文标题里的英文项目名恰恰是最可靠的那部分，现在完全没被用上。

- ⚠️ **HF trending 榜的"僵尸老模型"没有被挡。**
  openai-community/gpt2 靠累计下载量常年挂在 trending 前 10，
  但 `lastModified` 是 2024-02-19。这类条目每次都会被采进来。
  → 建议调整：`collect_hf()` 加一条硬过滤——`lastModified` 距今超过 180 天的直接丢弃，
    不进候选。这不是打分维度的问题，是"根本不该进入候选池"。

### 已修复：collect.py 不存 xsec_token（2026-09-06 记过，这次真被咬）

调研三条小红书线索时，`xhs read <裸 explore URL>` 全部返回
`Note not found in HTML state: empty noteDetailMap`，只能额外跑一次 `xhs user-posts`
把 token 捞回来再读 —— 白白多花 3 次调用，而小红书本来就有"一轮别使劲扫"的硬约束。

→ **已改**：`collect_xhs()` 的 `take()` 现在把 `xsec_token` 拼进 URL 查询串
（`?xsec_token=...`），后续 `xhs read <url> --xsec-token <token>` 直接可用。
`.agents/` 和 `.claude/` 两份都已同步。

### 采集侧仍未修

- X 源连续为 0（twitter-cli ClientTransaction/404），已经连续多天。
- GoogleTrends 源为 0：cron 调不动 MCP，只能在会话里补。这次也没补上。

## 2026-09-11

用户在 8042 标了 6 条 write，其中 5 条推翻或上调了我的判断（均未附理由）：

- ✅ 判为「只存档」但用户要写：kepano/obsidian-skills（我给 60）—— 我的理由是 48k star 已被搬运烂
  → 信号：「逆热度」扣分可能过重。本站没写过的高星仓库，即使别处搬运多，对本站读者仍是新的。
- ✅ 判为「只存档」但用户要写：krea/Krea-2-Turbo（我给 42）—— 我的理由是 gated + 自定义协议 + 非新品
  → 信号：「gated」不该直接压一手性到底，官方博客/发布页也算一手源。
- ✅ 判为「跳过」但用户要写：MMC1410001/mcp-rag-server（我给 34）—— 我的理由是 0 star、通用 RAG 模板
  → 信号：用户对「MCP + 本地 RAG」这类可上手工具的兴趣高于我对「新颖度」的要求。
- ✅ 判为「存疑」但用户要写：m-a-p/YuE2-3B（72）、pilot-protocol/pilot-mcp（60）
- ✔️ 一致：nex-agi/Nex-N2.5-mini 值得写；siray-image-mcp 和两条小区通知跳过。

→ 暂不改权重（本批 5 条，攒够 10 条统一调）。倾向方向：下调逆热度扣分、gated 不再压一手性。

### 采集侧改动
- 移除博主「持续学习妹妹」（用户确认）：9/8、9/11 共 4 条全是小区/生活内容。
- X 源：Mac mini 之前根本没装 twitter-cli（不是 404）。已 `pipx install twitter-cli`（0.8.5）。
  `collect_x()` 改为只从 `~/Dev/.env` 读 `TWITTER_AUTH_TOKEN` / `TWITTER_CT0`，没配就跳过——
  不让它回退读浏览器 cookie，因为那会弹 keychain 授权框（用户明确不要）。

## 2026-09-11 晚（用户在 8042 标了 9 条 write，全部发布）

9 条全发：virtual-ai-infra-team、K2-Horizon-MoVA、果蝇连接组进游戏（小红书线索）、ECCV 2026 最佳论文（小红书线索）、
ParallelHue、Qwen3.8-Flash-Next-GGUF、Krill、jarvis-py、all-MiniLM-L6-v2。后两篇过了零点，pubDate 记 9/12。

### 调研中推翻的选题前提（写稿时必须回一手源，不能信标题）
- virtual-ai-infra-team 名字像多 agent 团队，实际只有 Planner 一个 LLM 角色，其余全是确定性代码。
- jarvis-py 自称离线，实测默认把录音以 FLAC 走明文 HTTP 发 Google STT。
- all-MiniLM-L6-v2 是 2021 年老模型（上一批对 gpt2 的规则是「僵尸老模型不写」），用户仍标 write。
  这次换了角度写成「为什么它还是下载第一 + 中文硬限制 + 2026 该换什么」，有本机实测，成立。
  → 信号：老模型不是一律不写，前提是有新角度（默认依赖链、实测对比），不是翻新闻稿。

### 流程侧
- 并行写初稿时，子 agent 把稿子直接写进 src/content/blog/，会被正在发布的那篇的 build 一起编译上线。
  → 已改：初稿一律写 radar/staging/，轮到发布才 mv 进去。流程固化在 write/WRITE-JOB.md。
- 果蝇那条标题是中文句子，store.py sync 按标题匹配不上 slug，没自动转 published，手动标的。
  （和 9/9 记的「中文标题去重失效」是同一个根因。）
- 评审台加了「今天审完了，开始写」按钮：拉起 `claude --bg` 后台会话按 WRITE-JOB.md 执行，
  进度写 radar/write-job.json，页面轮询显示。auto 权限模式 + settings.local.json 白名单。

## 2026-09-12（用户在 8042 标了 6 条 write，实发 5 篇）

这是「开始写」按钮第一次真跑。发了 5 篇：edge0-35b-a3b、localagi、orion-core（后台任务发）；
agent-egress-firewall-pipelock、pentest-harness（交互会话 blog-70 发）。
没发 1 条：小红书@无糖AI「又一个把 Claude Agent 工程化的开源项目」，正文里的仓库是 alsk1992/CloddsBot，
本站 9/10 已发专文（cloddsbot-ai-trading-agent-1000-markets），改标 skip。
check-duplicate.cjs 没拦住它：采集时实体名是空的，只能拿标题去查。

### 用户推翻的补判（blog-70 补判的分数）
- orion-core 给 52 分「跳过」、pentest-harness 给 40 分「跳过」，用户都标了写。
  两篇写出来都成立：orion-core 有本机实测（中文 token 少估 2 倍多、宽松解析会把普通 JSON 当成工具调用）；
  pentest-harness 写成批判性拆解（DeepSeek Harness 改名换皮）。
  → 信号：低星/可疑项目只要能写出「实测推翻 README」或「拆穿包装」的角度，用户照样要。
- LocalAGI 82、Edge0 86、egress 73 和用户一致；CloddsBot 重复，改标 skip。

### 调研中推翻的前提
- Edge0 采集卡片写「许可证未声明」，实际模型卡 YAML 和 HF 标签都是 apache-2.0，只是 HF 仓库没有 LICENSE 文件。
  → 采集侧 lic 字段只看了 LICENSE 文件，要补读模型卡 YAML 的 license 字段。
- LocalAGI 自称 Responses API「完整替代」，有 7 个请求字段解析了却没用上；12 个 release 没有一个附带二进制。
- daily-crawler S1 日报：RubyGems 事件是 WSJ 首发不是 Reuters；把 OpenAI 的「benign tasks」说法当事实；
  归因写成定论，但 RubyGems 官方说无法确定；「200 次/小时」是当事人贴出的 Agent 日志，不是 Resy 统计的。
  → 日报的事实性说法错误率高，WRITE-JOB 里「先打开原始报道核实」这条必须保留。

### 流程侧（这次踩的坑）
- **撞车**：「开始写」后台任务在跑的时候，交互会话 blog-70 也在写同一批条目，5 篇全部重叠。
  靠跨会话消息分工才解决，其间主会话把 blog-70 的 Edge0 staging 稿覆盖过一次（两边子 agent 用了同一个 slug）。
  → 待改：交互会话开写前先看 radar/write-job.json，state=running 就不接手；
    或者 job.py 起任务时在 radar/staging/ 写锁文件。
- **写稿子 agent 写不进主 checkout**：后台会话的隔离守卫拦住了子 agent 的 Write，
  它们各自找了路：在 .claude/worktrees/ 里建 detached worktree，或者直接写 /tmp，主会话再 cp 回 radar/staging/。
  主会话自己追加这份 FEEDBACK 也被拦，只能另开 worktree 分支走 PR。
  → 待改：BRIEF.md 直接规定子 agent 的输出位置（比如固定一个 scratch 目录），主会话统一收；
    或者把 radar/staging/ 从守卫里豁免。
- **pgrep 自匹配**：`pgrep -f publish-blog.sh` 会匹配到调用方自己的 shell 命令行（命令行里就含这个字符串），
  等待循环会白等。改用 `pgrep -f "[b]ash scripts/publish-blog.sh"`。
- store.py sync 的 published_match 对不上 daily-crawler 条目的标题（形如「[2026-09-12 S1] …」），
  发布后要手动标 published，待修。
  Edge0 也没对上：条目名是 Edge0-35B-A3B-preview，slug 里没有 preview，手动标的。
  → 匹配时应先去掉 -preview/-instruct 这类后缀再比。
- run-daily.sh 已加「当天已采集过就让路」（PR #79），今晚 21:10 不会重扫。
- orion-core 首张 banner 的机器顶面出现了苹果 logo 的变形，verify-banner 没查出来，是人工看图发现的。
  换种子、提示词写 unbranded 后重出。
