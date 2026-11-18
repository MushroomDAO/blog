# 记忆存储：独立安装与递增迁移

当前提供材料到草稿的两步抽取、人工审核与完整图谱事务入库、参与者与固定主题模板，以及三路召回、主题总结审核、撤销和父总结读取替换和两级精排。版本 1～22 可以从空库安装或逐版升级。召回四个岗位已有可配置 HTTP 实现；代理、摘要和每日任务由配套网页服务运行。可选的同源管理网页见 [`memory_web`](../memory_web/README.md)，纯核心调用不依赖网页登录组件。

需要 Python 3.11+。本目录可以单独放到一个父目录下运行，不需要原项目的源码、配置或数据库 SDK。安装 Python 依赖：

```bash
python3 -m pip install -r memory_core/requirements.txt
```

## 数据库与安装

支持 PostgreSQL 17、public schema 中的 pgvector 0.8.x。管理员预先安装 vector 扩展，并创建两个独立角色：迁移所有者和 `memory_app` 应用角色。应用角色不授予超级用户、建库、管理角色、复制、绕过行权限、继承其他角色或在 public 创建对象的权限。迁移所有者拥有目标数据库的建 schema 权限；应用角色只需要连接目标数据库。

第一次使用时，可以用管理员账号在 `psql` 中准备一个独立空数据库；下列数据库名是示例，密码通过交互输入：

```sql
CREATE ROLE memory_owner LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
\password memory_owner
CREATE ROLE memory_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
\password memory_app
CREATE DATABASE memory_example OWNER memory_owner;
\connect memory_example
CREATE EXTENSION vector WITH SCHEMA public;
REVOKE ALL ON DATABASE memory_example FROM PUBLIC;
GRANT CONNECT ON DATABASE memory_example TO memory_app;
```

这是一次性的数据库/角色准备，后面的版本化安装器负责业务结构；重复安装无需重做这些管理员操作。Docker 镜像需要预先包含 vector 扩展文件，只有普通 PostgreSQL 镜像而没有扩展文件时，CREATE EXTENSION 会失败。

连接环境变量由使用者显式设置为完整连接串，包含 host、dbname、user 和相应凭据。密码不要写入本目录；程序不会自动读取任何 `.env`、旧项目配置或本机数据库 service 文件。

```bash
python3 -m memory_core.storage.install --dimensions 1536 --timezone Asia/Shanghai --day-start-hour 3
```

安装入口读取 `MEMORY_INSTALL_DSN`，运行入口读取 `MEMORY_DSN`，配置管理读取所有者的 `MEMORY_CONFIG_DSN`；安全占位示例见 `.env.example`。也可以显式传连接串调用 Python 接口。安装前由管理员完成扩展安装，随后建表和授权全部在同一次迁移事务内完成。首次安装创建 `memory_core` schema，不修改其他 schema 的表或数据。

- 维度必须是 1–2000 的整数。这份基线固定使用普通 vector 的 HNSW 余弦索引；超过 2000 维时在连接数据库前报错，不截断、不偷偷换索引。1536 是安装默认值，不代表已选择公开版的嵌入模型。
- 时区使用 IANA 名称，业务日分界为 0–23 的整点，默认 `Asia/Shanghai`、3 点。应用读取安装在数据库中的同一份配置。
- 时间戳存为带偏移的 TEXT，例如 `2026-06-12T03:00:00+08:00`。业务日比较转换为实际时刻；内容自己的 `source_date` 保留原有日期文本语义。
- 夏令时重复边界使用第一次出现的时刻；不存在的边界顺延到对应的有效时刻。业务日按当地日历的相邻边界确定，不固定为 24 小时。
- 同版本、配置、迁移内容、结构和权限重复安装是无操作，不改数据、序列当前位置或创建重复对象。任何冲突都停止；不会自动删库或“修复”已有结构。后续结构演进使用新的递增迁移，不改已发布的 `001_core.sql`。
- 安装记录保存配置、迁移校验和及结构校验和；版本 2 起另有逐版迁移记录。结构核对涵盖列、默认值、约束、索引、序列定义、函数、触发器、所有者和对象授权。安装器先核对已有版本，再在同一事务内逐版升级；失败保留原版本与数据，拒绝降级。备份工具尚未实现。

## 已实现结构及边界

| 对象 | 当前范围 |
|---|---|
| `memory_items` | INTEGER 卡片编号、显式空间标识、正文/标题/摘要、卡片种类、内容日期、可配置维度的向量、归档原因/时间、创建/语义修改时间、模型报告使用次数与最后报告时间 |
| `memory_keyword_tokens` | 原有七字段词条、来源编号、词频、字段长度、时间和复合主键；复合外键保证词条与卡片属于同一空间 |
| `installation` | 单条技术版本和安装配置记录，应用只有读取权限 |
| `schema_migrations` | 版本 2 起保留各已应用 SQL 的校验和，应用只有读取权限 |
| `space_policies` | 空间参与者、可空相识日、人设、纯称呼词、修订号、初始模板、原材料保留天数、抽取评分/每日额度和核心记忆；应用只读 |
| `source_materials`、`material_extractions`、`pending_memories` | 单日原材料、来源墓碑、稳定抽取请求、版本化候选与审核结果；来源和审核映射均带空间约束 |
| `entities` | 名字、别名、类型、可选向量与指纹；规范化索引共用数据库函数。两个参与者的名字/别名各归一个实体，普通同名实体可以有歧义，要求显式选择 |
| `topics` | 数据库中的主题名、稳定引用、模板 `preset_key`、唯一兜底标记及整理资格。名称、模板项和兜底标记固定；说明从模板文件读取，应用只读 |
| `relations`、`memory_entities`、`memory_topics` | 关系和图谱关联使用带空间的复合外键；关系保留不同来源，不按端点粗略合并 |
| 写入与检索函数 | 关键词替换保持单事务和卡片行锁；BM25 沿用既有字段权重和评分公式；三路检索默认只查指定空间的未归档原子卡 |
| 语义修改触发器 | 正文及经历层、主主题、里程碑等语义字段改变时更新时间；仅归档或重建关键词不冒充正文修改 |

卡片/词条字段类型、枚举和评分依据已核验的现有结构；这不是整个旧库的复制。主键由 SERIAL 改为同为 INTEGER 的 identity；移除私人空间默认值；关键词外键增加空间一致性；公开结构独占 `memory_core` schema。现有归档字段只用于检索范围验证，归档任务尚未接入。

版本 4 新增独立的材料、抽取请求和待审草稿表；审核正文及结构用 JSON 保存，草稿采用整数 identity 编号，与私人旧库 UUID 草稿不共表、不直接迁移。园丁事务、摘要、归档事件、完整核心资料管理、记忆书签和召回诊断将在对应批次加入。版本 5 的审核事务从已确认的卡片、实体和主题构造七字段词条；版本 6 补齐图路查询函数，保持关系来源与一跳扩展各自的白名单、配额和评分。

参与者名字、别名或纯称呼调整时，`SpaceConfiguration` 在同一配置事务中用现有七字段规则重建该空间卡片的关键词索引，保留卡片正文、语义修改时间及实体/主题引用；失败一起回滚，不调用模型。

版本 9 为主题增加稳定的 `preset_key`，移除按空间复制的说明列。主题说明唯一来源为 `presets/topics.json`（恋人 11 项、通用 8 项），每次构造上下文直接读取；升级模板说明后所有空间立即使用新版，不增加空间修订或改写已有草稿。说明作为第二步分类依据，“用户”“AI”替换为空间配置名字；感情历程保留“不挂普通聊天、撒娇、陪伴”的窄定义。经历层仍由模型判断并保存，网页不展示；核心取舍留待真实模型对比，见 `OPEN-EXPERIENCE-01`。

## 材料、两步抽取与人工审核

- `SpaceConfiguration.set_extraction_rules(space, expected_revision=..., minimum_importance=7, daily_limit=5)` 使用独立配置所有者连接修改该空间规则，原设置未传的字段保留，普通应用不能改配置。核心记忆用 `set_core_memory(space, expected_revision=..., core_memory="...")` 单独管理，与人设 `set_persona` 分开。
- 一天按安装时区及业务日整点划分，默认北京 03:00～次日 03:00。用原材料消息时间判断；不按上传时间或卡片讲述往事的日期计。每份材料必须在单一业务日内；跨日先拆开，缺时间须明确提供 business_date。默认同空间所有材料共享五条，第一步候选落盘即计，拒绝、结构失败或原文删除不释放；重试不再占额。额度满后本次请求记为无候选，不自动偷偷重抽。
- 第一模型岗位按[筛选成文提示词](prompts/selection.md)输出 title/content/summary/importance 和 `segment_id + quote`；程序验证逐字引用、过滤低于门槛的结果，并按原顺序截取剩余额度。第二岗位按[结构提示词](prompts/extraction.md)补检索摘要和图谱结构，不能改正文、评分与证据。固定响应只验证协议，不能证明模型真的会正确筛选。
- `DraftStore.submit` 用明确来源标识和请求标识保证幂等；同标识不同材料报错。`extract` 在模型格式错误时最多生成两次，错误只记录步骤/类型，原材料保留；第一步成功后第二步失败保留候选和证据，重试仅补失败的结构。没有进程内后台任务，不存在靠重启猜测成功的状态。
- `get/list/source/edit/reject` 提供版本检查、分页及来源状态。配置发生变化，已有候选须按新修订逐条复核编辑；尚未生成候选的请求可用 `reconfirm_extraction` 明确确认新修订再重试。人工编辑保留合法的 0 分，不把生成门槛变成人工拒收条件。
- 入口在落材料、保存生成结果和人工编辑前筛查常见密钥格式、凭证上下文和部分号码格式，命中则拒绝且不记录命中值，不自动脱敏。格式筛查不能识别所有编码/拆分或无上下文的秘密。来源标识不含凭证，不能把生产连接信息放进材料。

### 确认收录事务

`ReviewStore.approve(draft_id, expected_version=..., expected_policy_revision=..., request_key=..., embedder=..., embedding_model=...)` 显式提供嵌入岗位及其模型标识，不选择真实供应商。先校验当前草稿、配置、逐字证据和来源；模型/向量准备都在业务写入之前完成。第二步另接收证据段落的原消息时间，避免把凌晨消息的业务日期误当日历日期来解释“明天”。

- 先按既有语义做向量查重：相似度 ≥0.92 判重复，范围包括同空间全部有向量的卡片，归档卡及主题总结也参与。查重向量或查询失败允许收录，结果标记 failed_open；正式卡片及需要更新的实体向量仍必须成功准备，缺失/维度错误不能写空向量。
- 对同空间的确认串行，在事务内重新查重，避免两个不同草稿同时进入后重复入库；重复只写审核结果，不建新卡。查询失败用独立保存点回滚，不能让失败的 SQL 破坏后续整事务。
- 复核草稿版本、空间配置修订、来源删除状态和向量准备时使用的实体记录，然后在一个事务中写卡片、实体及别名、实体桥接、关系、主题桥接/主主题、真实分词生成的七字段词条与 approved 结果。任一步失败完整回滚，原草稿仍可重试。
- 同一草稿重复确认返回原结果；并发确认也只建一张卡。审核请求标识不能用于另一张草稿。同名/别名有多个候选时明确要求实体编号，不盲合并；同端点、同类型但不同来源的关系继续保留。两个配置参与者复用其实体，应用不擅改配置所有者管理的名字/别名。
- `card_source(memory_id)` 从唯一的草稿到卡片映射回查完整原文或“原文已删除”。删除原文保留已批准卡片与短证据摘录；不会伪装仍能读取完整原文。原文已删的待审草稿不能首次确认收录，已经批准的重复确认仍返回原结果。

本批 CLI 是同步的受信任服务端入口，不提供对外鉴权、供应商或真实模型默认值。显式设置应用 `MEMORY_DSN` 后：

```bash
python3 -m memory_core.daily.workflow --space example-space submit synthetic-material.json
python3 -m memory_core.daily.workflow --space example-space extract 1 --fixed-responses fixed-responses.json
python3 -m memory_core.daily.workflow --space example-space list --after-id 0 --limit 50
python3 -m memory_core.daily.workflow --space example-space show 1
python3 -m memory_core.daily.workflow --space example-space source 1
```

审核前按刚读到的草稿 version 和配置 revision 填参；编辑会递增 version。以下是独立动作示例，确认与拒绝二选一，不顺序执行整段：

```bash
python3 -m memory_core.daily.workflow --space example-space edit 1 reviewed-payload.json --version 2 --revision 1
python3 -m memory_core.daily.workflow --space example-space approve 1 --version 2 --revision 1 \
  --request-key review-example-1 --embedding-label fixed-synthetic-v1 --fixed-responses fixed-responses.json
python3 -m memory_core.daily.workflow --space example-space reject 1 --version 2
```

材料文件字段为 source_key、request_key、segments，来源 source_kind 默认为 mainline；可选 business_date 仅用于显式日期。每段含唯一 segment_id、speaker（user/assistant）、text、带偏移 timestamp（无时间为 null）。`delete-source MATERIAL_ID` 删除完整原文，`expire --now OFFSET_TIMESTAMP` 按保留天数显式清理，不运行定时任务。固定文件使用 `FixedModels` 的 `extract` 请求文本到响应映射，两个岗位都是固定响应，未知输入明确失败。`selection_prompt/structure_prompt` 可供调用方离线准备精确输入的合成夹具。

## 空间规则、参与者与主题

新安装默认采用恋人主题模板，可在安装时传 `--topic-template general` 选择通用模板。完整标签与顺序只有一份，位于 [主题预设数据](presets/topics.json)；只在创建空间时选择恋人或通用模板，之后不能切换或改主题名称、说明；数据库保留稳定主题编号和模板项标识，说明始终从模板文件读取。代码只使用主题引用和兜底标记，不判断具体主题名。所有主题的整理资格初始关闭；里程碑是卡片的布尔标记。

安装选择的是新空间默认模板，参与者必须由使用者显式填写。首次配置示例只使用虚构名字：

```bash
python3 -m memory_core.storage.space --space example-space \
  --user-name "Example User" --user-alias "User Alias" \
  --assistant-name "Example Assistant" --assistant-alias "Assistant Alias" \
  --ignored-term "dear"
```

命令使用 `MEMORY_CONFIG_DSN` 所有者连接；普通 `MEMORY_DSN` 账号无权修改规则、主题或参与者实体。已有空间的修改须提供读取到的 `--expected-revision`，并提供完整参与者及保留配置；纯称呼词省略时保留已有值；并发旧修订会失败，避免覆盖别人修改。配置账号不应放进前端。

- 每个角色的名字和若干别名指向同一实体；角色之间不能重叠。实体规范化沿用 NFKC、大小写、空白及成对包裹符的规则，Python 查询使用同一个数据库规范化函数。
- 版本 8 增加可选的 `acquaintance_date`（相识日），以 TEXT 保存有效的 `YYYY-MM-DD` 日历日期，不带时区；`NULL` 表示未设置。旧空间升级后为空，不补造日期。所有者可调用 `SpaceConfiguration.set_acquaintance_date(space, expected_revision=..., acquaintance_date="2024-02-29")` 单独修改，传 `None` 清空；`configure` 也接受此参数，省略时保留已有值。日期、参与者与修订号共同提交，应用角色只读。相识日修改仍递增配置修订以防覆盖；版本 9 的审核配置留档只记录参与者名字与别名，因此改日期不触发网页复核提醒。迁移不改写历史留档。当前只作为配置元数据，不自动写成记忆或加入抽取提示。
- 纯称呼词单独保存为检索忽略词，不作为任何实体名字或别名。新恋人空间默认使用 `presets/ignored_terms.json` 中的宝宝、宝贝、亲爱的、老公、老婆、Daddy，通用空间默认为空；网页不提供填写入口。CLI 的 `--ignored-term` 可重复传入并覆盖清单，`--clear-ignored-terms` 清空；省略时保留已有值，新空间则取模板默认值。`clean_address_terms` 供关键词编排确定性清洗，参与者名字仍可检索；模型清洗只在消息长于 15 字或命中纯称呼词时执行。
- 图起点默认只屏蔽该空间的两个参与者实体，集合直接读取参与者引用，不维护第二份编号列表。`filter_graph_seeds` 及其 SQL 校验使用同一记录，检查修订号、引用和空间；图路查询也读取同一配置，只限制起点，不屏蔽邻居遍历或关键词/向量路的相关卡片。
- 版本 9 起 `SpaceConfiguration.edit_topic` 只保留所有者修改整理资格的能力，主题改名和说明编辑会明确拒绝；数据库也锁定主题名、模板项与兜底标记。资格读取与后续 SQL 都以同一数据库字段为准，当前不启动园丁或归档。
- `source_retention_days=NULL` 表示原材料永久保留，正整数表示保留天数，零或负数报错。版本 4 已提供显式清理和来源删除状态；没有自动调度。删除原文只清空 segments、保留来源墓碑，不重新导入同一来源；草稿保存的短证据摘录仍可保留，完整原文显示“原文已删除”。

`GraphStore.resolve_entity` 遇到多个同名/别名结果会要求明确选择；确认新对象后再调用 `create_entity`。显式 `entity_key` 用于重复/并发请求的技术幂等，不以名字或内容相似度冒充同一个对象。`create_relation` 同样可使用显式关系键，来源不同的两条关系可以共存。图谱写入和关联有各自事务与空间约束，整条审核由 `ReviewStore.approve` 放在同一事务中完成。

## 版本升级与固定模型契约

版本 9 按原主题名绑定模板项，保留主题与卡片编号、关联和历史留档；遇到改过名而无法对应模板的旧主题会停止并回滚，不猜测含义。当前无真实用户，合成预览可重建；将来已有数据须先明确整理映射。

同一个 `python3 -m memory_core.storage.install` 命令会将已支持的旧库升级到当前版本；`--target-version` 可选择仍受支持的目标版本，用于独立验证和分步升级。版本 1 的 SQL 保持原样；后续 SQL 的校验和逐个记录，已应用文件发生变化时拒绝运行。时间格式函数也随版本迁移更新，避免元数据升级后仍按旧版本读取时区。

`models/models.py` 定义抽取、嵌入、关键词清洗、专用精排、最终精排的调用契约。`models/http_models.py` 实现四个召回岗位，不选择默认型号；`models/completion_model.py` 为关键词、最终精排及网页摘要/日记共用聊天传输。`testing/fixed_models.py` 只供显式测试使用：每个输入必须有预先声明的固定响应，未知输入报错，错误和坏格式也按样本原样返回给待测解析器。它不是运行时降级模型。两个抽取岗位分别显式传入；未提供岗位或对应固定响应时失败，不回退到真实模型。

## 召回岗位配置

`RecallModelsConfig.from_env()` 只读显式环境，不加载 `.env` 或旧网关配置。四个岗位前缀为 `MEMORY_EMBEDDING`、`MEMORY_KEYWORD`、`MEMORY_DOCUMENT_RERANK`、`MEMORY_FINAL_RERANK`，各自支持 `_MODEL`、`_BASE_URL`、`_API_KEY`。没有默认型号；专用地址/key 必须成对填写，省略时复用 `MEMORY_UPSTREAM_BASE_URL` / `MEMORY_UPSTREAM_API_KEY`。第一级精排单独填写地址、key 和型号，接口格式由 `MEMORY_DOCUMENT_RERANK_FORMAT` 选择，默认 `voyage`，通用格式用 `cohere`。见[硅基流动配置示例](../memory_web/README.md#第一级精排配置)。

嵌入采用 [OpenAI 格式](https://developers.openai.com/api/docs/guides/embeddings)，不发送缩维参数；启动时用固定短文本核对安装维度，每次返回也复核维度、有限数值和非零向量。审核收录与召回使用同一个适配器。已经写入卡片后，即使同维度也不能随意换嵌入型号，现有坐标需要重算。关键词与最终精排沿用现有提示词和输出解析。两种第一级精排格式均须返回完整、不重复的文档排序，否则第一级退回粗排顺序。Voyage 请求沿用供应商默认的输入截断。

`MEMORY_RECALL_MODEL_TIMEOUT_SECONDS` 是每次 HTTP 的上限，默认 5 秒；网页把它限制在整轮召回总时限的剩余时间内（总时限默认 8 秒）。超时包括连接、响应头和完整响应体，不因分段到达反复重置；错误只返回岗位与安全错误码，不带 key、供应商正文或原始异常。未配嵌入时仍可关键词检索，但审核收录明确失败，不写空坐标。

## 自动召回与固定模型验证

`RecallService(SearchStore(dsn, space), settings=None)` 绑定受信任服务端已经授权的空间，默认设置直接构造 `RecallSettings()`；`RecallService.from_env(space)` 才显式读取召回环境项。没有隐式 `.env` 加载，没有用另一份配置把 false 改回 true。

默认值唯一维护在 [recall/recall_config.py](recall/recall_config.py) 的 `RecallSettings` 字段中；下面的说明表由测试与程序核对。环境项缺省时直接使用该定义，整数格式错误回到对应默认值，负数按 0（关闭附文）处理。可离线查询，不需数据库或模型凭据：

```bash
python3 -m memory_core.recall.recall --show-defaults
```

| 环境项 | 默认值 |
|---|---|
| `MEMORY_RERANK_FULL_LIST_ENABLED` | true |
| `MEMORY_RERANK_TAIL_GATE_ENABLED` | true |
| `MEMORY_RERANK_EXACT_ENTITY_GATE_ENABLED` | false |
| `MEMORY_GRAPH_ENTITY_NAME_ONLY_ENABLED` | false |
| `MEMORY_RERANK_EVIDENCE_ENABLED` | true |
| `MEMORY_RERANK_EVIDENCE_MAX_CHILDREN` | 3 |
| `MEMORY_RERANK_EVIDENCE_MAX_TITLE_CHARS` | 60 |
| `MEMORY_RERANK_EVIDENCE_MAX_SUMMARY_CHARS` | 120 |
| `MEMORY_RERANK_EVIDENCE_MAX_TOTAL_CHARS` | 480 |
| `MEMORY_GRAPH_ENABLED` | true |

- 当前原句用于向量和专用排序；关键词使用条件清洗和本地 jieba 最多六词。关键词提示词读取配置中的参与者和纯称呼词；无有效清洗响应时使用确定性清洗。
- 每路 30，合并最多 30；各路按最大原分归一化，权重关键词 0.25、向量 0.35、图 0.30，二/三路命中分别加 0.06/0.10。记忆向量不设 0.30 阈值；0.30 仅用于实体向量起点，实体和主题种子各最多十个。
- 图路实体直连每起点按日期取五条，分数 `min(1,1/ln(关联数+1))`；主题直连 0.85。关系来源每起点/类型五条、去重后全局十条，0.75；一跳 0.60。关系来源与一跳有不同的通用类型集合，唯一 SQL 定义在迁移 006。空间、归档、卡片种类先过滤，再截断配额。
- 每轮固定配置修订，读取、图起点校验和最终输出均检查；期间配置改变要求重试，不混合两版规则。查询不写业务数据。关键词失败保留向量/图路；嵌入失败保留关键词。诊断标明失败步骤及异常类型，不带供应商原始异常正文。
- 只读既有整理结果：吸收子卡换成同空间有效父总结；同父去重，继承最高分，不叠加也不补搜。归档且没有父总结的子卡丢弃；父总结已归档时丢弃命中，其他父总结不可用时保留子卡。主题总结生成与审核见下文；记忆书签见版本 20，核心记忆见版本 21。
- 父总结仅附本轮实际命中子卡的依据，默认三张、标题 60 字、摘要 120 字、每篇总长 480 字。专用排序看正文前 600 字并在其外看到附文；最终精排看原子正文前 200 字、总结全文及附文。正式 `content` 始终不变。
- 全量排序默认 true：非空候选都走专用排序，完整顺序传最终精排；候选≤5 跳过最终模型，最多选五条。排序失败/不完整→全部粗排候选；最终超时/无效/少于五个有效序号→排序前五；两级都失败→粗排前五。不加最低相关度、不额外补搜。false 保留旧的前十、失败粗排前十五和有效序号不足时补齐规则。
- 上一条回复结尾仅送最终精排：最近 assistant 清理工具前言/动作/语音后，末两句最多 120 字；最近为空不往前找。旧门控仍要求当前消息没有具体字面实体或关键词实体、话尾有非口头禅问句。名词片段、身体词、短词边界和问句判断保持原逻辑；排除集合由空间的两个参与者名字/全部别名与纯称呼词构造，没有私人名单。实体目录缓存五分钟，空间配置修订改变立即重建排除词；新版完整实体门控仍默认 false。没有关键词元数据或实体目录读取失败就不递话尾。

固定响应入口：

```bash
python3 -m memory_core.recall.recall --space example-space --query "植物" --fixed-responses fixed-responses.json
```

可用 `--messages synthetic-messages.json` 提供合成历史，仅决定话尾；`--no-rerank` 显式跳过两级精排，返回粗排/替换后的前五。不带 `--fixed-responses` 时按显式环境配置装配 HTTP 岗位；没有配置的岗位走原有逐级降级。Python `recall` 要显式提供 embedder、cleaner、reranker、selector 四个岗位。

固定夹具验证实际模型输入，不仅验证编号：关键词键为 JSON `[原句, keyword_prompt(原句, policy)]`；专用排序键为 `[ranking_query(原句), 卡片编号列表, 正文文档列表]`，响应为 **0 起始文档位置**列表；最终精排键为 `[原句或门控话尾查询, 卡片编号列表, selection_prompt(...)]`，响应为 **1 起始候选序号**的逗号文本。各格式函数可供离线准备合成夹具。

关键词和最终精排的输出上限为 60 token，temperature=0。关键词、最终精排和回执补判都按接口关闭思考。OpenRouter 用 `reasoning.effort=none`，DeepSeek 直连用 `thinking.type=disabled`，硅基流动国内站和国际站用 `enable_thinking=false`。其他兼容接口需选择支持短答案的型号。HTTP 失败不自动重试，走既有逐级降级。假 HTTP 测试不证明真实模型质量。 [OpenRouter](https://openrouter.ai/docs/guides/best-practices/reasoning-tokens) · [DeepSeek](https://api-docs.deepseek.com/guides/thinking_mode/) · [硅基流动](https://docs.siliconflow.cn/docs/api/chat-completions-post)

结果提供 `candidates / ordered / final` 和逐阶段诊断。`final` 每项含真实卡片编号、完整正文、路由和原因，以及 `citations` 来源引用/逐字短证据；完整材料不嵌入引用。删除原文后 source_status 为 deleted，已批准卡片仍可召回。没有来源映射的既有卡明确标记 unmapped，不虚构证据；父总结引用本轮命中子卡。`final.content` 不含附文或上一条回复；前两份候选列表仅用于诊断，不能拿来代替最终正文注入。数据库应用账号仍是受信任服务端账号，尚无外部 HTTP 鉴权。

## 最小使用

```python
from memory_core.storage.postgres import KeywordToken, PostgresStore

store = PostgresStore.from_env(space_id="example-space")
# 合成向量用于演示接口，不是可用的嵌入模型输出。
vector = [1.0] + [0.0] * (store.settings.dimensions - 1)
card_id = store.write_card(
    "合成示例：整理植物观察笔记", vector,
    [KeywordToken("植物", field="content")],
)
hits = store.search_vectors(vector)
keyword_hits = store.search_keywords("植物 OR 观察")
store.replace_keywords(card_id, [KeywordToken("植物")])
```

`write_card` 将卡片和初始关键词作为一个事务提交，任一步失败全部回滚。`replace_keywords` 失败保留旧词条。底层接口仍允许调用方显式提供词条，查询使用 `词 OR 词` 契约；审核路径已用本地 jieba 搜索分词构造七字段索引，保留原分词与结构化整词语义，私人称呼改读空间忽略词。自然语言入口 `RecallService` 复用相同分词和 BM25，不以简单字符串匹配代替。

存储对象必须显式绑定记忆空间，查询和写入使用参数绑定；其他空间的卡片不能通过该对象替换词条。数据库应用账号是受信任的服务端账号，能够处理多个空间，不能发给用户或浏览器。凭据到允许空间的授权随代理/MCP 入口实现；当前存储层的空间过滤不等于完整服务鉴权。数据库不需要开放公网端口。

## 隔离验证环境

需要主机 Python 3 和 Docker 权限。在独立开发目录运行：

```bash
python3 memory_core/dev/environment.py start
python3 memory_core/dev/environment.py test
python3 memory_core/dev/environment.py stop
python3 memory_core/dev/environment.py start
python3 memory_core/dev/environment.py destroy
```

`start` 创建随机名称且有归属标签的内部网络、独立数据卷和 PostgreSQL 容器，生成仅供本环境使用的随机凭据。没有主机端口映射、不加入已有网络、不挂载生产目录或 Docker socket、不启动定时任务。停止后再次 start 保留同一套合成数据；destroy 只处理名称与标签同时匹配的本环境资源，不使用 prune。启动中断时保留状态供精确 destroy 后重建。

测试依赖镜像安装固定版本 psycopg 和 jieba；测试运行时只挂载本目录，根文件系统只读、临时目录有限额、网络只能到隔离数据库。测试包含真实的应用角色写入与两路检索、事务回滚、空间和归档范围、重复安装与结构/权限冲突、不同维度、安装失败回滚及默认 CLI/Python 入口。没有测试库时测试会失败，不会跳过后冒称通过。

`.state/` 内的测试凭据不入 Git，目录权限 0700、文件 0600。destroy 删除容器、网络、数据卷和凭据；测试依赖镜像 `memory-core-storage-tests:20261029` 保留用于复跑，分支合并且不再需要复跑时可按此精确标签删除，不清理其他镜像。若测试进程被强行中断，先 destroy 再 start，避免将未收尾的旧测试库当空库。所有材料都是合成数据，没有模型费用；这类测试不证明召回质量、完整业务升级或生产适配已经通过。


## 对话原文基础（版本 10）

新增五张表及空间的 `conversation_retention_days`；实际列、约束与索引以 [010_conversations.sql](migrations/010_conversations.sql) 为准。HTTP 与钥匙留在 `memory_web`，核心不导入网页或上游客户端。

| 表 | 职责 |
| --- | --- |
| `conversation_turns` | 一份轮次版本、固定时间线位置、接续消息、待替换对象、生成状态与采用状态、整轮业务日、冻结/上下文组成/召回记录及过期标记。 |
| `conversation_requests` | 每次 HTTP 交换、客户端请求编号/操作/目标轮次、重试关系、顺序、请求校验摘要、模型/流式、上游响应编号、用量/使用回执、错误阶段及状态。 |
| `conversation_messages` | 用户与 AI 的有效正文、图片占位及异步描述结果、本轮顺序、匹配摘要、完整性和带偏移的时间；业务日期只从轮次读取。 |
| `conversation_tool_events` | 调用或结果、工具调用编号/名称、原始协议载荷、本轮顺序与明确报告的状态；供当轮续接及两个自有工具的历史卡片，不作为日记、摘要或抽取原料。 |
| `conversation_space_state` | 每空间当前轮次/请求、占用凭证/期限和历史版本。数据库占用凭证与超时、心跳和历史版本支持跨进程的一轮互斥。 |

原文编号使用 BIGINT identity，关联均携带空间约束；跨空间引用不能落库。同一时间线位置最多一份 current，candidate 不会提前挤掉旧版；replaced 仅留档，首发没有恢复接口，不在后续对话页显示。业务日按用户消息到达服务的时间一次确定，回复或工具续轮跨界也跟随原轮次。文字与时间分开，图片数据/地址、思考和内部注入不保存为新原料；工具循环由客户端执行，按调用编号接续同一轮并冻结上下文；整批编号不能匹配时，核对调用条数及工具名顺序后记回原编号，本轮消息照客户端重发内容透传；回执过滤由网页代理负责，摘要只消费已定版的整轮正文，见下方版本 12。

对话保留默认 30 天，NULL 表示永久，与既有导入材料 `source_retention_days` 分开，不覆盖其值。配置空间时可传 `conversation_retention_days`，CLI 对应 `--conversation-retention-days N` 或 `--conversation-retention-forever`；省略则保留已有值，新空间使用默认值。仍使用配置所有者和预期修订号。及时摘要固定只保留 15 天（`SUMMARY_RETENTION_DAYS`，只服务当天，往日由日记接手）；对话保留更短时随对话一起清理。

`ConversationStore.expire(now=带偏移时间)` 是清理入口，由网页每日任务自动调度：清空到期轮次的正文、工具载荷、冻结内容及召回记录，保留编号和来源墓碑；已复制到 `source_materials` 的原文以 `segment_id=conversation-message:<消息编号>` 关联，同事务清空相应材料，已生成卡片保留。迟到的生成任务不能把已过期正文写回来。冻结全文仅供正在进行的轮次重放，结束即释放，后续对话页读取组成清单。摘要结果表在 3D 保存完整轮次的实际覆盖关系，不能把消息最大编号当成唯一消费状态。


轮次事务由 `conversations/conversation_rounds.py` 维护，不含图片数据的冻结与工具结果配对由 `conversations/conversation_context.py` 维护，`ConversationStore` 仍是统一入口。`begin` 返回轮次/请求编号、随机占用凭证与仅含系统词和当前消息的初始请求；首轮由代理调用 `history_input` 和 `save_context` 组装托管历史后才发上游，工具续轮用冻结前缀与前端本轮消息组装请求，精简续轮由账本补全；同空间其他请求明确冲突，不排队花钱。`finish` 只有凭证、轮次和当前步骤仍一致才能提交，最后一步成功时原子采用候选；工具等待不会提前替换。`renew` 只续当前步骤；`expire_leases` 在到期后把轮次标未完成并释放冻结，支持多 worker 按行跳过锁处理。保留期清理与这些操作统一先锁空间状态再锁轮次，清理后迟到结果不能复活原文。

版本 11 的 [011_hosted_context.sql](migrations/011_hosted_context.sql) 增加空间人设、卡片 `used_count/last_used_at` 及按时间线位置查询各版本的索引，不修改五张对话表的字段或旧迁移。`set_persona` 走既有配置所有者与修订锁；普通应用只读人设。`conversations/conversation_history.py` 负责当前版本历史、图片描述/占位、组装清单和冻结记录；固定聊天文字在 `conversations/chat_text.py`，两个自有工具的历史卡片由 `recall/tool_history.py` 拼接。`finish(..., reported=[本轮本地编号], reported_none=False)` 仅认可冻结记录中的编号，明确报告“无”时用 `reported_none=True` 保存 `reported_unused`，不增加计数，在同一事务里保存回执、计数和正文；同一位置的工具步骤、重试/重做不重复增加同卡计数。前端可见正文的匹配指纹仍支持独立入参，代理已使用剥离回执后的正文。


`recall/tool_history.py` 从本空间当前采用、未过期轮次的工具事件读取参数和客户端回传文字，直接拼接 `memory` / `mark_moment` 历史卡片，不调用模型，也不重新读取卡片或书签。`memory` 保留参数、总数/本页数量/下一页位置、相关候选边界和编号/日期/标题/状态；普通卡摘要（get 为正文）最多 500 字，主题总结最多 4000 字，search/browse 每次最多列 12 条。公开工具返回没有事件跨度字段，主题总结使用已有日期、标题和“主题总结”标记。`get_sources` 照自用版列出这一页全部来源目录，不截 12 条、不重放来源全文；`list_topics` 和可识别的查询错误同样留卡。书签卡保留动作、分区或编号和短结果摘要。公开版不加入模型重排信息或不存在的 tool_trace 回查提示。

识别直接名称、Kelivo 的服务器限定名及已知消歧后缀、Operit 的服务器限定名和 package_proxy/proxy 封装；只有同时匹配公开工具返回格式才生成卡片。名称被截断、未知改名、未知返回格式、图片或其他无法解析的结果均回退原来的名字/已返回或未返回一行。待返回调用不伪造结果；非自有工具不回放参数或结果。工具卡仍不是实际 AI 正文，不改变未获回应/未完成的判断。日记、及时摘要、每日抽卡继续经 `conversation_material` 只读取聊天正文，防止把查到的历史当成当天新原料。保留期清理仍清空原始工具载荷，卡片不另建表、不留可复活的副本。


## 及时摘要与覆盖（版本 12）

[012_conversation_summaries.sql](migrations/012_conversation_summaries.sql) 增加摘要记录和精确轮次覆盖两张表，不修改既有对话正文列。`SummaryStore.next_plan` 只选择当前采用且已结束的轮次，每轮计两条，保留接力尾部；模型在存储事务之外执行，`save` 复核具体版本、正文指纹、配置修订及剩余接力后原子提交，追加新轮次不误判为来源失效。覆盖表限制同空间/业务日及唯一覆盖，已覆盖轮次不能再替换。读取摘要时核对覆盖版本；无效摘要不遮蔽剩余原话。

一级摘要默认满 28 条触发，最旧 24 条（12 轮）进入摘要、最后两轮接力；字符超限可以提前触发，但仍保留接力。未合并一级摘要满 8 份，将最旧三份合成二次摘要，保留原始摘要，只在成功后改用合并结果。注入仅取当前请求所属业务日，全部有效二次摘要及未合并一级摘要按来源顺序排列。摘要稳定段位于人设/日记位后、原话前，工具续轮重放冻结内容。

`daily/summary_policy.py` 单处定义阈值与整轮长度保护，`daily/summaries.py` 维护短事务、覆盖和跨 worker 会话锁；摘要存储不导入 HTTP 客户端。公开提示词、参与者称呼、摘要注入及省略提示集中在 `conversations/chat_text.py`。模型岗位、环境配置、后台调度与只读页面见 `memory_web/README.md`。保留期清理扩展现有 `ConversationStore.expire`：一级摘要及相关二次摘要随覆盖原话清空正文，保留覆盖墓碑，不改已生成卡片；自动调度由网页每日任务提供。


## 日记与每日任务（版本 13）

[013_diaries_and_daily_tasks.sql](migrations/013_diaries_and_daily_tasks.sql) 新增两张表，不修改已有原话字段。`DiaryStore` 以结束日期的全部当前采用轮次为材料，和摘要共用 `conversations/conversation_material.py` 的正文组装；保存时复核来源指纹、版本、保留期与空间设置。日记正文和任务成功状态共同提交，重复键、执行次数和跨 worker 会话锁保证发布幂等。人工编辑使用日记修订号，并永久标记用户修改；已有日记不被自动任务重写。

`daily/daily_policy.py` 按安装时区与业务日分界计算执行时刻、补写范围和最近日记篇数。`daily/daily_tasks.py` 保存可扩展种类的执行结果与重试信息，不在核心导入模型客户端。网页服务负责唤醒和模型调用，配置及故障恢复边界见 `memory_web/README.md`。`history_input(..., recent_diary_count=3)` 返回最近完成日期的日记，`save_context` 将其放在人设后、摘要前并冻结版本。原话清理不删除日记，也不改变日记的用户编辑状态。


## 每日抽卡与审核方式（版本 14）

迁移 `014_daily_card_extraction.sql` 为 `space_policies` 加 `review_mode`（`auto` / `manual`，默认 `auto`），为 `daily_tasks` 加 `model_usage` 数组，不增加表。当前原材料只允许 `mainline`，卡片可为 `mainline` / `gardener`（既有空来源保留）；历史迁移保持原样。若旧安装包含不支持的来源，升级明确停止并回滚，数据不删、不改名，须先由所有者导出或处理后再升级。

`DailyCardStore` 只把已结束日期当前采用版本的正文交给现有 `ReviewStore.submit/extract/approve`，不新增卡片写入流程。分段使用同一处定义的 `conversation-message:<id>`，实际消息时间保留；跨日整轮沿用用户消息所属日期，普通材料入口仍严格拒绝无轮次依据的跨日混合。图片、未获回应和未完成标注复用历史渲染，不读取工具档案或思考。原话到期时，现有清理事务按这些编号一起清空原材料副本，保留已生成卡片及来源墓碑。

两步全部整理成功才进入待审核，并开始等待计时。每张卡通过正常审核事务准备坐标、实体、关系、主题及关键词；任何一步失败整卡回滚，已完整收录的卡重复执行直接复用审核结果。失败草稿保留供续跑，第二步失败不重新筛选或占用一份新额度。来源版本改变时拒绝旧自动收录，下一次以新来源重新提交；旧未通过草稿经正常拒绝流程留档，原有每日候选额度不会因拒绝而返还。

`SpaceConfiguration.set_auto_approval` 沿用配置锁和修订号。新卡片先进入待审核；默认等待 48 小时，在之后那次每日任务中按正常审核事务收录。参与者、筛选等上下文变化时沿用原有复核机制，不自动沿用旧判断。自动审核在提交事务内再次核对开关、到期时钟、任务执行权、原话版本及保留期，迟到结果不能写入卡片。

调度、显式型号配置、逐日用量和管理入口见 [网页说明](../memory_web/README.md#每日抽卡与审核方式4a)。


## 卡片属性与删除（版本 15）

`CardStore(dsn, space).edit(card_id, {"title": "新标题", "topic_ids": [主题编号], "is_milestone": False})` 只改标题、主题、里程碑，主题规则复用审核约定。正文、检索摘要、日期、经历层和实体不开放修改；现有向量和图谱保持，关键词与属性在同一事务里重建，不调用模型。已归档卡片使用同一接口，归档状态不变；主题总结只读。

`CardStore.delete(card_id)` 永久删除卡片（含向量）、关键词、主题与实体桥接、本卡产生的关系，并清理不再被任何卡片或关系引用的相关实体。共享实体、仍被待审草稿引用的实体和空间参与者保留。对应已收录、重复未收录的审核记录变为 `deleted`，清空 narrative、payload、卡片引用及配置留档；记录和业务日期保留，原来的候选计数不会返还。同一审核请求重试只返回已删除状态，不复活卡片。上述写入在同一事务完成，失败全部回滚。

迁移 `015_card_deletion.sql` 只调整审核草稿表的状态和清空约束，不新增表或字段。安装及旧库升级仍走原安装器。删除子卡不改写主题总结；对话原话、日记、摘要和当轮历史召回记录也不回算。已知限制：不保存删除指纹，之后重新抽取或导入同一段原话，仍可能再次收录；卡片属性没有版本冲突检查，多处编辑以最后一次成功保存为准。


## 待审核与到期入库（版本 16）

`016_delayed_approval.sql` 将原 `space_policies.review_mode` 转成布尔字段 `auto_approve_enabled`，新空间默认开启，原 auto→true、manual→false；不改历史迁移。草稿新增 `review_ready_at` TEXT 及待审查询索引，不新建表。旧完整待审草稿从升级时重新获得完整等待期；未整理完整的草稿在首次成功进入 pending 后开始计时。人工保存草稿修改会重计，自动整理/入库重试和开关变化不重计。关闭开关时只允许人工确认。

`ReceiptJudgeStore`（`daily/receipt_judge.py`）为模型未写回执的轮次提供夜间补判：`candidates(day)` 列出某业务日注入了卡片、最终请求回执为 `unreported` 的当前轮次；`apply` 每轮单独提交：先取得实时存档同一把空间对话锁（`conversation_rounds.lock_space_state`），复核该轮仍是当前版本、未删除且仍未报告后，按与模型回执相同的同位置去重规则计数，写入 `judged` / `judged_unused`。`parse` 只给出无效编号的轮次不写入，保持未报告。归档的 `receipt_health` 把这两种状态与模型报告同等计入。

`ApprovalSettings` 从 `MEMORY_AUTO_APPROVE_AFTER_HOURS` 读取正整数小时，默认 48。它同时用于原子卡片和主题总结。等待按业务日计算：小时数向上取整为天数（48 小时即 2 天），草稿在其 `review_ready_at` 所属业务日之后第 N 天的那次每日任务中到期收录，与草稿在当天几点生成无关，避免每日任务稍后生成的草稿被多推迟一天。时区、业务日分界和每日时刻复用安装配置。补跑和失败重试按任务所属业务日判断到期，迟到的补跑不会把属于后一天的草稿提前收录。

`PendingApprovalStore` 复用原审核事务、草稿版本、抽取上下文和来源记录；安全的开关修订不阻断已有等待，但更早的语义配置变化仍需复核。每日 approval 任务在抽卡之后、清理之前执行，不依赖抽卡型号是否配置。同空间互斥、按业务日防重、失败重试沿用 `daily_tasks`。每卡完整成功或回滚，失败卡继续留待审；已经处理过的卡不会重复入库。入库使用现有嵌入岗位，不调用新的聊天模型。


## 在场卡片归档与恢复（版本 17）

`017_card_archiving.sql` 只给卡片新增 `restored_at` TEXT，并给已有归档时间增加按空间查询的部分索引；不改历史迁移、不新增表。归档保留卡片正文、坐标、关键词与图谱，仅写 `archive_reason=decay` 和 `archived_at`；已有检索规则在评分与 LIMIT 前排除归档。仅处理在场的原子卡。已有父总结引用或已标记吸收的子卡始终跳过；五个园丁主主题内尚未整理的原子卡等到有整理决定后再纳入归档判断，标为 retained 的卡照常按原有时钟计算。

`ArchiveSettings` 集中维护期限：规则 365、反思 180、知识 180、事件 120、情绪 365 天，对应 `.env.example` 中 `MEMORY_ARCHIVE_*_DAYS`。豁免层永不归档，里程碑至少 365 天。计时使用 `last_used_at`，为空才用 `created_at`，再与 `restored_at` 取较晚者；不使用内容日期，也不因改标题或主题重计。按实际经过天数计算，时区与时间文本格式沿用安装配置。

回执保护默认最近 14 天、至少 20 轮、回执率不低于 0.8，通过 `MEMORY_ARCHIVE_RECEIPT_WINDOW_DAYS / RECEIPT_MIN_SAMPLES / RECEIPT_MIN_RATE` 配置（后两项同样带 `MEMORY_ARCHIVE_` 前缀）。只统计当前采用、已经结束、确实记录过卡片注入且仍在保留期内的轮次；任一步报告使用或明确报告未使用均算一轮有效回执。工具多步、同编号重试不增加样本，已替换版本、未注入、尚未结束的轮次不计；结束但未报告的失败或中断轮次计入未报告。样本不足或比例低时整次跳过归档，下一次每日任务重新判断。14 天能平滑单日波动且处于默认 30 天保留窗口内；20 轮避免少量回复决定结果；80% 容许偶发漏标，同时拦住持续漏标。

`ArchiveStore.archive_task` 在已有每日任务执行权保护下锁卡后重新判断，归档和任务完成同一事务；出错整次回滚并由原重试机制继续。`restore(card_id, expected_archived_at=..., now=...)` 核对当前归档时间，旧按钮遇到新一轮归档返回冲突。恢复只清空当前归档标记、写恢复时间；保留原入库时间、使用时间和次数。重复恢复已经在场的卡片不再次延长时钟，不调用模型。

`memory_query.MemoryQueryStore/MemoryQueryService` 提供绑定空间的主动查档：`search/browse/get/get_sources/list_topics`。查询复用三路检索及第一级文档精排，不调用第二级大模型精排。主动查档的 `search` 直接返回命中的子卡，并带父总结编号，不替换成父总结或合并；父总结替换只用于代理自动召回。`browse/search` 默认查原子卡，可用 `source_scope=topic_summary/all` 查总结或两者。`get` 在单个行更新事务中增加使用次数、写最后使用时间并恢复归档；不会获取代理的空间轮次锁，也不生成回执。其余动作不计使用。MCP 的协议、访问钥匙鉴权和中文展示由 [memory_web](../memory_web/README.md#mcp-主动查记忆5a) 提供，核心不依赖 MCP SDK 或网页模块。

已知限制：只展示当前归档月份，不保存历次归档/恢复轨迹；恢复后退出归档列表。回执是模型自报，无法识别没有报告的实际使用；归档提交后才到达的使用回执会保留，但不自动恢复该卡。统计窗口超出实际原话保留期时，只能统计仍留存的轮次，样本不足会暂停。


## 主题总结（版本 18）

`TopicSummaryStore` 复用每日任务锁、主题父子字段与到期自动入库开关。只处理五个固定主题键 `relationship / others / work / interests / health` 的在场原子卡，按主主题和事件日期分组；缺事件日期时才取入库日期。每月 3 日只看已结束的完整月份，少于 `MEMORY_TOPIC_SUMMARY_MIN_CARDS=5` 张的月份并到下一个窗口；整个月加入后超过 `MEMORY_TOPIC_SUMMARY_MAX_CARDS=30` 张时，本次报错并保留全部来源，不截断半个月或偷偷丢卡。门槛沿用原实现的 5/30 张，均可配置。

只新增总结批次和来源关联两张表。来源表保存同空间卡片编号、内容校验摘要与 written/skipped 结果，不复制原卡正文；删卡时清空关联和校验摘要。模型必须为每个输入编号给出恰好一次结果，无跳过理由分类。模型输出不合格式最多重试一次；费用元数据随调用记入批次及月度任务，不保存模型思考或完整请求。

提示词带入同空间、同主主题此前已生效总结的标题及每篇最多 800 字正文，包含已归档总结；待审、驳回及已撤销的总结不带入。已有总结单独标明只作衔接和避免重复的背景，不是本窗口来源、不进入吸收清单。写作要求明确禁止评论、风险提示、建议、学术腔和抽象套话，固定文字集中在 `lifecycle/topic_summary_text.py`。

总结只读待审，人工确认或等待默认 48 小时后的每日任务自动确认。两者使用同一事务：先验证来源和参与者，再算总结坐标，提交时再验证；写入总结卡、主题、写入子卡的已有实体引用和关键词，然后只吸收 written 子卡。skipped 标为已整理但继续正常召回、使用和归档，不再每月重复整理。模型输出为空且全部 skipped 时，不生成空的待审总结。

生效后的总结不可修改，只可整篇撤销。撤销删除总结和索引，恢复仍存在的 written 子卡并从撤销时重计归档时钟；skipped 子卡只解除已整理标记，原归档时钟不改。被删除的子卡不复活。驳回、撤销都使这段素材至少等到下一个月度运行，并延伸到下一个已结束月份；允许后续月份没有新增卡片，不能因此捏造新事实。年度汇总不实现。

召回继续搜子卡、显示总结。同一总结下命中的子卡合并；总结已归档时不回退显示被吸收的原文。总结使用 `tier_2_reflection`，仍可记录使用次数。自动归档跳过总结；已归档的旧总结仍可恢复。

已知限制：来源属性被改、删除或归档，以及参与者名字/别名改变时，旧待审总结拒绝生效，需驳回后下月重写。程序核验清单完整性，不能证明模型正文真正对应每张 written 卡，需要审核判断。升级前没有批次记录的旧总结保持只读与可归档恢复，不凭空补造可撤销记录。全部来源子卡被删后，既有“搜子卡”路径可能不再命中该总结，管理页仍可查看。


## 消息图片描述（版本 19）

`019_image_descriptions.sql` 只给 `conversation_messages` 新增可空的 `image_descriptions JSONB`。按原图片顺序保存每张图的描述或失败结果，以及型号、数字用量和安全错误码；不存图片本身、图片地址、key 或模型原始报错。未完成或未配置时为空，多图全部结束后一次写入。数据库约束核对数量和用户角色，触发器禁止覆盖已写结果；到期清理时和原话一起清空，迟到结果不能重新写入已清理或过期消息。没有新增任务表。

`MessageImages` 在短事务中核对空间、消息和保留期，写入一次最终结果。原 `content_parts`、匹配指纹、用户时间及轮次归属保持原样。`render_turn` 统一把成功结果渲染为 `[图片：描述]`，没有描述的图片仍用原占位，后续托管历史、及时摘要、日记与抽卡都读取它；稳定的原材料消息编号不变。图片只参与记忆描述，不加入本轮召回查询，纯图片仍跳过召回。

当轮与工具续轮仍使用前端提供的原图，后台描述不能替换它。已冻结的本轮历史不刷新；描述写入后不可修改，此后的历史前缀保持稳定。摘要、日记和抽卡的已有来源校验会拒绝生成期间变动的输入，但不会追改已经生成的摘要、日记或卡片。提示词和图片标注集中在 `conversations/chat_text.py`，岗位与后台资源配置见配套网页说明。

## 记忆书签（版本 20）

`020_recent_notes.sql` 新增两张表：`recent_notes` 每空间一行，保存四区 TEXT、内容 version 和最新一次秘书任务 JSON；`moment_bookmarks` 只保存待整理的 UUID 书签、分区、单行正文、记录时间与业务日。所有者迁移明确授权普通应用角色；应用角色不能删除已整理书签的整行记录。旧版本升级不改卡片、聊天或已有迁移，重复安装校验结构和授权。

`BookmarkStore` 绑定空间执行 add/list/update/delete，支持短编号与完整 UUID，歧义拒绝。`RecentNotesStore.absorb` 把任务日期之前所有待整理的书签按记录时间倒序追加到四区顶部，与删书签、版本更新和每日任务完成共同提交。`recent_notes` 是独立任务种类，不消费聊天或日记原料、不调用模型，也不占代理轮次锁。时间与业务日沿用安装配置；多天漏跑一起补入。

秘书提示词、四区编号、空白字数统计和结果校验在 `bookmarks/recent_note_tidy.py`；书签和注入共用 `bookmarks/recent_note_text.py` 的四区名称。`RecentNotesStore.save` 接收客户端确认的多个分区正文与 expected_version，一次事务保存，版本不一致整体拒绝；采纳整理时再核对最新 tidy_job_id 与基准版本，并将任务标为已采纳。建议套用与长期事项按起始日期排序由管理页完成。后台执行、取消、重启恢复和管理员接口见 [网页说明](../memory_web/README.md#记忆书签与夜间整理5b)。核心不导入私人模块、MCP SDK 或网页代码。

`ConversationHistory.history_input/save_context` 在同一空间历史读取中取四区内容，放在日记后、及时摘要前，空分区或全空时不发送占位。工具续轮继续使用首次冻结的上下文，已整理书签的后续变化只在新一轮生效。它不改变召回卡片的使用回执或统计。


## 核心记忆（版本 21）

`021_core_memory.sql` 把旧的事实列表按行合并，迁入 `space_policies.core_memory TEXT` 后移除旧列；超过 5000 字的旧数据会让迁移整体回滚，需所有者先整理后再升级，不截断内容。已执行的迁移保持原文。当前审核配置留档只记录参与者身份，旧版 SQL 的背景摘要已由版本 9 替换，升级后没有旧列依赖。

内容由用户手写，系统不自动修改；所有者配置服务保留凭据与敏感信息检查，数据库另有 5000 字硬约束（包括空白、换行，按 Unicode 字符计数）。`set_core_memory` 与人设共用空间 revision 防止覆盖；抽卡空间上下文及其 digest 使用这段正文。托管代理在本轮首次读取时冻结正文，按人设、核心记忆、日记、已整理的书签、及时摘要的顺序注入；空正文不注入，工具续轮保持首次内容，保存从新一轮生效。


## 导入（版本 22）

`ImportStore` 在独立的 `import_jobs` / `import_items` 保存预览、选择和处理进度，`source_materials.material_kind` 明确区分聊天与用户记忆。`iter_upload` 以 ijson 流式逐条解析官方 ChatGPT/Claude/Gemini 的 JSON（ZIP 成员通过 `archive.open` 流式读取），以及 UTF-8 的 `## YYYY-MM-DD` 加正文文件；不读附件、思考或工具调用。ChatGPT 只从 `current_node` 回溯采用分支，支持分片；Claude 兼容两套消息键名；Gemini 从 `Prompted ` 标题取提问，把 `safeHtmlItem` 回答转成纯文本，跳过反馈等活动，不把附件提示或 Gem 名加入原文。

聊天按安装时区与业务日分界拆成“来源对话 × 日期”，原消息时间保留在证据中，走现有两步抽卡和全空间每日额度。记忆文件按用户指定日期保留每条正文，`submit_memory` 跳过挑选和评分门槛，由第二步补标题、摘要、主题与图谱，并按每日抽卡共用的成文规则决定是否改写表达；不占聊天每日额度。其 importance=10 只满足现有待审数据协议，不调用模型评分。两种第二步共用 `prompts/extraction.md` 的完整结构规则，`structure_variants.json` 只保留角色、成文边界、日期、输出字段与输入说明的差异；测试锁住聊天版本的完整渲染，除已批准的“不输出 mixed，也不拆分本卡”段落外，与拆分前逐字一致。

防重键为来源、外部对话编号的哈希和业务日期，记忆文件为日期与正文哈希；`source_materials` 墓碑保留键，删除原材料后重传仍跳过。队列在原材料及抽取请求落盘的同一事务中保存抽取编号、清掉重复正文。领取在事务内把待处理条目标为运行中，结算时只在没有待处理或运行中条目时完成任务。失败条目可单独重试；手动停止保留在途条目的结果。重启重新领取未结算条目，已保存的筛选与结构结果直接复用。导入原文只写原材料表，不写任何 `conversation_*` 表，不参与当天历史、及时摘要或日记；审核、到期自动入库、归档和按内容月份的主题总结均复用现有链路。

版本 23 为每批任务保存是否直接收录。旧任务默认走原有审核流程。直接收录走现有审核事务，失败待审。记忆文件的保留决定由模型返回 `content: null`，程序直接使用原文。改写只影响卡片正文，原材料和逐字证据保留。

原材料保留期从上传/保存时开始，复用空间的 `source_retention_days`；为空表示不按天清理。预览和失败队列的正文也受此规则管理，清理后保留进度与防重信息。已完成卡片沿用新卡的收录、使用与归档时钟。网页后台、入口和接口见[管理网页的导入说明](../memory_web/README.md#导入第-6-块)。

上传处理使用文件流，按最多 64 项或约 1 MiB 正文分批写入现有导入表；解析失败整批事务回滚。预览/确认只读 message_count 等元数据，不再加载 segments。Gemini 用磁盘临时分组按业务日及真实时间排序，逐天交接，不按 Gem 筛选。内存以单个对话或 Gemini 单个业务日为单位，不累计整份导出的正文。一次上传不超过 90 MiB，相关 JSON 解压累计不超过 1 GiB；ZIP 内 JSON 的声明大小和实际读取字节都校验。`parse_upload` 只保留为小输入显式返回列表的便捷接口，网页不使用它。
