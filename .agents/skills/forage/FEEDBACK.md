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
