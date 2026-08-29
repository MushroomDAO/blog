# A2A 支持——设计文档（草稿，未实施）

> 状态：调研 + 设计，不含代码。这次撤下的 Agent Card 说到底是"指向一个不存在
> 的 A2A 端点"，要重新做，前提是先把 A2A 到底要求什么弄清楚，再判断值不值得
> 做、做多大——这份文档就是干这件事，不是要开工的信号。

## 一、为什么两轮 review 都判定第一版有问题（简要回顾）

第一版做错了两次：第一次用了已经在 v1.0 里废弃的顶层字段（`protocolVersion`/
`url`/`preferredTransport`，v1.0 把这些挪进了 `supportedInterfaces` 数组）；
第二次改成了 v1.0 的字段形状，但卡片指向的 `/api/mcp` 说的是 MCP 方法集，不是
A2A 自己的方法——不管字段形状怎么改，只要背后没有一个真正实现 A2A 方法的
端点，这张卡片就是在撒谎。第二轮 review 明确指出：A2A 的自定义 binding
机制不是用来指向一个完全不相关的 API 的，撤下比继续修字段更诚实。

## 二、规范调研结论

直接读了 A2A v1.0 规范原文（`a2a-protocol.org/latest/specification/`），
不是转述别人的总结。核心结论：

### AgentCard 的完整字段比想象中更多

不只是 `supportedInterfaces` 这一处结构变了。完整的必填字段包括
`id`/`name`/`description`/`version`/`provider`，可选的
`capabilities`（`streaming`/`pushNotifications`/`extendedAgentCard`）、
`securitySchemes` + `security`（声明认证方式）、`signature`（JWS 签名）。
第一版和撤下的第二版都只填了一小部分，就算不谈"指向假端点"这个根本问题，
字段本身也是不完整的。

### 核心方法集比 MCP 重得多

A2A 定义了大约十一个方法：`sendMessage`/`sendStreamingMessage`（发消息）、
`getTask`/`listTasks`/`cancelTask`（Task 查询/管理）、`subscribeToTask`
（订阅单个 Task 的进展）、四个 push notification 配置管理方法、
`getExtendedAgentCard`。规范没有定义"轻量合规"档位——理论上要完整实现
才算合规。

### Task 是一等公民，博客场景大概率用不上

A2A 的核心模型是"客户端提交一个 Task，服务端异步处理，状态在
`SUBMITTED → WORKING → COMPLETED/FAILED/CANCELED/REJECTED`（还有
`INPUT_REQUIRED`/`AUTH_REQUIRED` 两个可恢复的中间态）之间流转，客户端
轮询或订阅进展"。这个模型是为"delegate 一个可能耗时、可能需要中途澄清的
任务"设计的——博客搜索这种毫秒级返回、没有中间状态的查询，套用整套 Task
状态机纯属过度设计。

规范本身留了一个口子：**简单交互可以直接返回一个 `Message`，不需要建
`Task`**。这是博客场景唯一值得走的路径——`sendMessage` 收到"帮我搜一下
xxx"这样的消息，直接同步返回一条包含搜索结果的 `Message`，全程不出现 Task
对象，跳过状态机、跳过 push notification 配置、跳过 streaming。

### 认证：公开无认证是规范支持的合法配置

`securitySchemes` 留空、`security` 留空数组，就是一个完全公开无认证的
A2A 端点，规范明确允许。跟 `/api/mcp`/`/api/search` 现在的设计哲学一致，
不需要额外引入认证机制。

## 三、如果做，最小可行范围大概是什么样

不是要现在动手，是把"最小但诚实"的范围想清楚，方便评估工作量：

- **只实现 `sendMessage` 一个方法**，同步阻塞返回一个 `Message`（不做
  `sendStreamingMessage`/Task 相关的六个方法/push notification 四个方法）。
  `capabilities.streaming`/`capabilities.pushNotifications` 老实填 `false`。
- **`sendMessage` 内部怎么理解自然语言消息**：博客现在的三个 MCP 工具
  （search_posts/get_post/list_recent）已经是"能做什么"的完整清单，A2A
  这一层不需要重新发明——收到消息后用简单规则匹配（比如"最近"/"最新"→
  list_recent，带具体关键词→search_posts）或者干脆固定成"这个 A2A 端点
  只做一件事：把收到的文本当成搜索词，返回搜索结果"，不追求理解任意自然
  语言指令（那需要接一个真正的 LLM 做意图识别，是另一个量级的工作量，
  超出"给 agent 提供只读信息检索"这个诉求）。
- **`AgentCard` 补全**：`id`/`name`/`description`/`version`/`provider`
  照实填，`skills` 沿用现在 llms.txt/MCP 里已经写清楚的能力描述，
  `securitySchemes`/`security` 留空表示公开无认证。
- **代码量级参考**：跟当初做 MCP（`functions/api/mcp.js` +
  `functions/_lib/mcp.js` + 两组测试）是同一个量级——需要一个新的
  `functions/api/a2a.js`（A2A 有自己的方法命名空间、错误码、信封结构，
  不能塞进 `/api/mcp` 里公用）、一个 `functions/_lib/a2a.js` 纯逻辑、
  对应单测，加上正确形状的 `/.well-known/agent-card.json`。**不是改几行
  就能上线的小补丁，是一次和当初做 MCP 差不多规模的独立开发**。

## 四、值不值得做——留给站长判断的问题

- 这套东西目前唯一验证过的真实使用路径是 `/agents` 页面上的 MCP 注册命令
  和 `mushroom` skill，两条路都不需要 A2A。A2A 这一层解决的是"完全没见过
  这个博客、只认 A2A 协议的第三方 agent 能不能发现并使用它"——这个受众
  存不存在、有多大，目前没有证据。
- A2A 生态本身（150+ 组织、Google/Microsoft/AWS 集成）大部分场景是
  **企业级多 agent 协作**（一个 agent 把任务委派给另一个专业 agent 去做），
  不是"个人 agent 查一个公开博客"这种场景——博客这个用例本来就不是 A2A
  设计时瞄准的核心场景，MCP（"给我的 agent 接一个工具/数据源"）反而更贴合。
- 如果决定做，建议范围就是上面第三节的"只做 sendMessage、不做 Task"这个
  最小集，不要一开始就奔着"完整合规"去——规范本身也承认这条简化路径合法。
