---
title: "Cheetah：62MB低内存背后，mmap省掉了什么"
titleEn: "Cheetah: Low-RSS LLM Loading With Rust and mmap"
description: "Cheetah是Rust与C编写的本地LLM加载器，利用mmap权重和Ant分层减少进程驻留副本。本文对照论坛62MB空闲内存与当前文档123MB稳态RSS，解释页缓存、BF16物化、KV缓存和吞吐的取舍，给出141例本机测试与CLI检查的范围，指出平台页大小及Vulkan已知限制，帮助工程师设计可复核的低内存验证。"
descriptionEn: "Cheetah’s Rust LLM loader examined: mmap weights, Ant residency, idle versus peak RSS, page-cache tradeoffs, 141 passing tests and the limits of local checks."
wechatTitle: "Cheetah：62MB空闲内存不等于模型体积"
wechatDigest: "对照作者内存报告与141例本机测试，解释低驻留加载的价值和边界。"
pubDate: "2026-11-18"
updatedDate: "2026-11-18"
category: "Tech-Experiment"
tags: ["Rust", "本地LLM", "mmap", "内存优化", "开源"]
heroImage: "../../assets/images/cheetah-rust-local-llm-memory-loading-guide-banner.jpg"
---

Cheetah 是一个本地大语言模型加载与推理工具，它尝试让权重保持文件映射，减少进程长期持有的内存副本。它值得研究的地方是权重如何驻留、何时回收，以及这种设计把成本转移到了哪里。

仓库 DA3M0/Cheetah 采用 Apache 2.0。本文固定检查提交 `6aa20a8`、版本 `1.0.0-rc4.0`；它变化很快，论坛帖、缓存页面和当前源码不能混为同一个版本。

## 62MB、123MB、13 tok/s，到底是哪组结果？

11 月 15 日的 Rust 论坛帖，作者报告 0.5B 模型重构后空闲内存从 2GB+ 降到 62MB，1.5B 模型空闲约 67MB，并称 0.5B 在 i5-4200M 上达到 13 tok/s。空闲是这里最容易被标题省掉的条件。

当前仓库文档报告的是另一组口径：Qwen 0.5B 在 16MB/32MB 分层预算下，稳态 RSS 123MB、推理峰值 152MB，空载主机时约 7.9–8.4 tok/s。这些都是作者报告，本文没有复现；提示词、上下文、线程、缓存冷热和构建条件没有统一，不能据此宣布性能提升或退化。

| 资料 | 内存数字的条件 | 速度数字的条件 |
| --- | --- | --- |
| 论坛帖 | 62MB，0.5B，idle | 13 tok/s，i5-4200M，作者报告 |
| 固定提交的开发文档 | 123MB 稳态、152MB 峰值，分层预算 | 约 8 tok/s，作者记录的另一轮测试 |
| 本文检查 | 未加载真实模型，未测 RSS 峰值 | 只跑构建、测试和 CLI，不报告推理速度 |

![小M分开检查磁盘权重、进程驻留和系统页缓存，三者不是同一个内存指标](../../assets/images/cheetah-rust-local-llm-memory-loading-guide-fig-01.png)

## mmap 省掉了什么？

0.5B 参数如果每个占 2 字节，权重本身大约就是 1GB。62MB RSS 不意味着把这份权重无损压进了 62MB；文件仍在磁盘，内核还可能把读过的数据留在系统页缓存中。

Cheetah 的开发文档把历史问题归结为权重被框架物化为自有张量，并把 BF16 大量转成 F32。仅增加一个“卸载层级”标签，如果后端仍把每个张量读出来并持有副本，RSS 就不会随标签下降。

新的 native 路径让权重保持 mmap-backed，算子按需读取 BF16/F16/F32 数据，而不是先把全部权重变成长期持有的 F32 数组。这减少了副本和精度扩张，但激活、中间结果、KV cache 与运行时结构仍然需要内存，不能称为整个推理过程零分配。

![小M对比整份物化权重与按需读取映射页，强调省的是长期副本](../../assets/images/cheetah-rust-local-llm-memory-loading-guide-fig-02.png)

## Ant 分层控制的是哪一层？

`cheetah init` 把模型整理为按层对齐的 shard、tensor unit 清单和 manifest。规划器给 unit 分配驻留层级；native 后端用实际页操作连接这些标签。冷 unit 使用后会调用 `madvise(MADV_DONTNEED)`，保留映射，后续访问再触发取页。

这里有两个容易误读的地方。第一，在 native CPU 路径，名为 VRAM 和 RAM 的热层都是进程中的驻留页标签，不能从参数名推导出实际占用了显存。第二，Disk 层后续读取可能命中系统页缓存，不代表每个 token 都从物理 SSD 重读完整文件。

因此，它是在进程驻留量、页故障、缓存和吞吐之间做取舍。要判断是否适合低内存设备，应同时观察进程 RSS、整机可用内存、系统缓存、磁盘读取和生成耗时，而不是只截一张进程列表。RSS 与系统页缓存是可能重叠的统计视角，映射页可以指向同一份物理内存，不能把两者直接相加。

## 本机实际检查了什么？

我们在 Apple Silicon、Rust 1.98.1 上，对固定提交运行 `cargo test --locked`：库测试 3 个、主程序测试 138 个，合计 **141 个通过、0 个失败**。`cargo run --locked -- --help` 也成功。测试涉及初始化 FFI、驻留规划、模型配置、CLI 和 HTTP/流式处理等程序路径。

这次没有下载 Qwen 权重，没有做真实生成、内存压力、吞吐或 Vulkan 测试。源码测试通过也不等于复现作者在 2013 年 i5 上的表现；ARM 主机也没有覆盖 x86 AVX2 专用分支。

还有一个值得移植者检查的细节：`store.rs` 的页对齐按 4096 字节计算，`madvise` 返回值未在该函数中检查；本机 `getconf PAGESIZE` 返回 16384。本文没有据此宣称已复现故障，但这足以提醒团队：跨平台时应验证实际页大小、系统调用结果和驻留效果，不能仅凭编译成功宣布同样低 RSS。

## 工程上怎样试用？

当前固定提交的默认路径是 native CPU，另有可选 Vulkan；`Cargo.toml` 已没有论坛早期提到的 Candle CUDA/Metal 依赖。不要照旧缓存页面选择后端。该版本使用 Safetensors 和 prepared directory，不支持直接加载 GGUF。

先准备一个有权使用的兼容模型源目录，再构建和初始化到独立目录。以下是文档配置方式，本文只执行了测试与 CLI 帮助，没有执行真实模型流程：

```bash
cargo build --release --locked
./target/release/cheetah init ./qwen-source ./qwen-prepared
./target/release/cheetah chat ./qwen-prepared \
  --ctx-size 1024 --max-tokens 64 \
  --ant true --ant-vram 16000000 --ant-ram 32000000
```

示例预算单位是字节，只是复查分层行为的起点，不是适合所有模型的推荐值。源码默认预算明显更大，不能用默认启动结果代替低预算测试。初始化目录会生成权重与元数据，应与源目录分开，并核对磁盘空间。

需要给应用提供接口时，可以使用回环地址上的 OpenAI 兼容服务，并沿用相同的推理与分层参数：

```bash
./target/release/cheetah serve ./qwen-prepared \
  --host 127.0.0.1 --port 8080 \
  --ant true --ant-vram 16000000 --ant-ram 32000000
```

协议兼容也要按端点和流式行为验收。设置认证、模型选择和并发上限时，应核对实际 CLI；不要把支持 `/v1/chat/completions` 理解成兼容所有上层客户端功能。

## 有哪些边界不能跳过？

开发文档仍列出真实 Qwen2-0.5B 某配置在 Vulkan 首次 matmul 处失败的已知问题；这不是本文复现的故障，也不能泛化为所有 Vulkan 模型都失败。它说明“后端已实现”和“目标模型已验收”是两回事。

我们更建议先用 native CPU 路径建立确定性输出或参考实现对照，再比较相同模型、精度、提示词、上下文和线程设置下的冷启动、prefill、decode 与峰值内存。低预算可能提高取页开销，长上下文的 KV cache 也不会因为权重 mmap 就消失。

![小M分别记录冷启动、生成峰值与稳态，并把系统页缓存单独列出](../../assets/images/cheetah-rust-local-llm-memory-loading-guide-fig-03.png)

对工程师，最值得借鉴的是让抽象与真实资源操作对应：驻留策略需要后端配合，不能止于一个枚举；优化权重表示之前，先找出是谁创建和长期持有了副本。Cheetah 展示了一个可读的 Rust/C 实验实现，离生产选型结论还需要真实模型与目标设备的证据。

## FAQ

### 能把“62MB”理解成模型只占62MB吗？

不能。论坛数字指作者报告的空闲内存，权重文件、系统页缓存、推理峰值和 KV cache 需要分别计量。

### 141个测试通过，证明低内存效果了吗？

没有。它验证了该提交在本机的测试路径与 CLI；本文没有加载真实模型，也没有测量推理 RSS 或速度。

### Apache 2.0 是否覆盖下载的模型权重？

仓库代码许可与模型权重许可分别看。使用某个模型时，应查看对应模型卡和许可，不能从推理工具的许可推导权重的使用范围。

来源与核查日期：2026-11-18。

仓库：https://github.com/DA3M0/Cheetah
架构文档：https://github.com/DA3M0/Cheetah/blob/6aa20a827cd9a82f2ca739e2d25bc639d54d315c/docs/ANT_MEMORY.md
论坛原帖：https://users.rust-lang.org/t/cheetah-a-local-llm-loader-that-went-from-2gb-to-62mb-after-a-refactor-0-5b-model-13-tok-s-on-a-2013-i5/143689
Linux madvise 语义：https://man7.org/linux/man-pages/man2/madvise.2.html
Apple madvise 返回值说明：https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/madvise.2.html
相关阅读：https://blog.mushroom.cv/blog/rust-anything-record-replay-rust-migration-guide/

---

> © 2026 Author: Mycelium Protocol. 本文采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh) 授权——欢迎转载和引用，须注明作者姓名及原文链接，不得去除署名后以原创发布。

<!--EN-->

Cheetah is a local LLM loader and inference tool that keeps weights file-backed to reduce long-lived in-process copies. Its interesting engineering question is which data stays resident, when pages are released, and where the remaining costs move.

DA3M0/Cheetah is Apache 2.0 licensed. This article inspects commit `6aa20a8`, version `1.0.0-rc4.0`. The project changes quickly, so forum posts, cached pages and current source must be treated as different observations.

## Which memory and speed numbers are being compared?

In the November 15 Rust forum post, the author reports a 0.5B model dropping from over 2GB to 62MB idle memory, a 1.5B model at 67MB idle, and 13 tok/s for 0.5B on an i5-4200M. Idle is a crucial qualifier.

The pinned development documentation reports a different configuration: 123MB steady RSS and 152MB inference peak for Qwen 0.5B under 16MB/32MB tier budgets, and roughly 7.9–8.4 tok/s on an otherwise idle host. These are author-reported results, not measurements reproduced here. Without matching prompts, contexts, threads, cache state and builds, they establish neither a speedup nor a regression.

| Source | Memory condition | Speed condition |
| --- | --- | --- |
| Forum | 62MB idle, 0.5B | 13 tok/s, i5-4200M, author report |
| Pinned developer guide | 123MB steady, 152MB peak, tiered | Approximately 8 tok/s, another author test |
| This article | No real model loaded; no RSS benchmark | Build, tests and CLI only |

![Little M separates on-disk weights, process residency and system page cache](../../assets/images/cheetah-rust-local-llm-memory-loading-guide-fig-01.png)

## What does mmap actually save?

Half a billion parameters at two bytes each already implies approximately 1GB of weights. A 62MB RSS figure does not mean those weights were losslessly compressed into 62MB. The file remains, and previously accessed data may remain in the operating system’s page cache.

The project describes its earlier problem as owned-tensor materialization and extensive BF16-to-F32 conversion. A residency label cannot reduce RSS if the backend still requests and retains every tensor as an owned copy.

The native path keeps weights mmap-backed and reads BF16/F16/F32 data as needed, avoiding a permanent full F32 weight representation. Activations, scratch buffers, KV cache and runtime metadata still allocate memory. This is a weight-path optimization, not allocation-free inference.

![Little M compares materialized weight copies with reading mapped pages as needed](../../assets/images/cheetah-rust-local-llm-memory-loading-guide-fig-02.png)

## What does Ant control?

Initialization produces aligned layer shards, tensor units and a manifest. A planner assigns residency tiers, and the native backend connects those tiers to page operations. After cold units are used, MADV_DONTNEED leaves the mapping in place and allows later accesses to fault pages back in.

On the native CPU backend, tiers named VRAM and RAM both refer to resident pages; their names do not establish actual GPU memory use. Disk-tier accesses may hit the system page cache rather than physically reread the SSD each time.

Evaluate process RSS, whole-machine available memory, cache occupancy, disk reads and generation time together. Lower process residency can trade against page faults and throughput. A process-list screenshot cannot measure that trade alone. These accounting views can overlap: mapped RSS and file cache can refer to the same physical pages, so do not simply add them.

## What did we verify locally?

On Apple Silicon with Rust 1.98.1, `cargo test --locked` passed 3 library tests and 138 main-program tests: **141 passed, 0 failed**. `cargo run --locked -- --help` also succeeded. The tests exercise paths including initialization FFI, residency planning, model configuration, CLI and HTTP/stream handling.

We downloaded no Qwen weights and tested no real generation, memory pressure, throughput or Vulkan execution. Passing tests on this host does not reproduce the author’s 2013-i5 result or exercise the x86 AVX2-specific branch.

A portability detail deserves inspection: store.rs aligns advice ranges to 4096 bytes and does not check the madvise return value in that function. This host reports a 16384-byte page size. We did not reproduce a failure from this observation; teams porting it should verify page alignment, system-call results and real residency behavior rather than inferring low RSS from a successful build.

## How can engineers evaluate it?

The pinned version defaults to native CPU with optional Vulkan. Its Cargo manifest no longer includes the historical Candle CUDA/Metal path mentioned in the forum. Use the pinned source rather than cached backend descriptions. This version accepts Safetensors and prepared directories, not GGUF.

Obtain a compatible model whose terms permit your use, then prepare it into a separate generated directory. These are documented evaluation commands; we ran tests and CLI help, not this real-model flow:

```bash
cargo build --release --locked
./target/release/cheetah init ./qwen-source ./qwen-prepared
./target/release/cheetah chat ./qwen-prepared \
  --ctx-size 1024 --max-tokens 64 \
  --ant true --ant-vram 16000000 --ant-ram 32000000
```

Budgets are bytes and are an experimental starting point, not a universal recommendation. Defaults are much larger; a default launch does not reproduce a low-budget run. Initialization generates weights and metadata, so keep source and destination separate and account for disk space.

An application can use the loopback OpenAI-compatible service with the same residency options:

```bash
./target/release/cheetah serve ./qwen-prepared \
  --host 127.0.0.1 --port 8080 \
  --ant true --ant-vram 16000000 --ant-ram 32000000
```

Verify the endpoints and stream behavior your client uses, and inspect authentication, model selection and concurrency options. Supporting chat completions does not establish every higher-level client feature.

## What limitations matter?

The developer guide still lists a real Qwen2-0.5B configuration failing at its first Vulkan matmul. This is a documented limitation, not a failure reproduced here, and it does not establish that every Vulkan model fails. An implemented backend and an accepted target-model configuration are different milestones.

Start with native CPU and compare outputs against a reference. Then hold model, precision, prompt, context and thread settings constant while measuring cold load, prefill, decode and peak memory. Low budgets can add page-fault overhead; mapping weights does not remove a long context’s KV cache.

![Little M records cold load, generation peak and steady residency separately from system cache](../../assets/images/cheetah-rust-local-llm-memory-loading-guide-fig-03.png)

The reusable design lesson is to connect resource abstractions to actual backend behavior. A tier enum alone cannot enforce residency. Before optimizing weight representation, identify who creates and owns the copies. Cheetah is an inspectable Rust/C experiment; production selection still needs evidence from real weights and the intended device.

## FAQ

### Does 62MB mean the model occupies only 62MB?

No. It is the author’s idle-memory report. On-disk weights, system cache, inference peaks and KV cache need separate accounting.

### Do 141 passing tests prove low-memory inference?

No. They verify test paths and CLI operation on this host. We did not measure real-model RSS or inference speed.

### Does the code license cover model weights?

No blanket conclusion follows. Check the model card and its own license separately from the inference tool’s Apache 2.0 code license.

Sources checked November 18, 2026:

Repository: https://github.com/DA3M0/Cheetah
Pinned architecture: https://github.com/DA3M0/Cheetah/blob/6aa20a827cd9a82f2ca739e2d25bc639d54d315c/docs/ANT_MEMORY.md
Forum: https://users.rust-lang.org/t/cheetah-a-local-llm-loader-that-went-from-2gb-to-62mb-after-a-refactor-0-5b-model-13-tok-s-on-a-2013-i5/143689
Linux madvise: https://man7.org/linux/man-pages/man2/madvise.2.html
Apple madvise: https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/madvise.2.html
Related engineering: https://blog.mushroom.cv/blog/rust-anything-record-replay-rust-migration-guide/

---

> © 2026 Author: Mycelium Protocol. Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — free to share and adapt with attribution. You must credit the author and link to the original; removing attribution and republishing as original is not permitted.
