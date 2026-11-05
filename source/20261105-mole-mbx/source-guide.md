# Mole 与 MBX (Mr. Boxington) 安装与使用指南

本文档介绍 macOS 终端清理优化工具 **Mole** 与 Rust 跨工作区共享构建缓存工具 **MBX** 的安装与使用方法。

---

## 1. Mole - macOS 系统清理与磁盘分析工具

- **官方仓库**：[tw93/Mole](https://github.com/tw93/Mole)
- **开发分支仓库**：[jhfnetboy/Mole](https://github.com/jhfnetboy/Mole)

### 1.1 安装方式

**方式一：官方一键安装（推荐）**
```bash
curl -fsSL https://raw.githubusercontent.com/tw93/mole/main/install.sh | bash
```

**方式二：本地源码编译安装**
```bash
git clone https://github.com/jhfnetboy/Mole.git
cd Mole
make build
# 运行本地构建二进制：
./mole
```

### 1.2 常用命令

| 命令 | 说明 |
|---|---|
| `mo` | 启动交互式终端主菜单 |
| `mo clean` | 安全清理系统缓存、日志与开发工具垃圾（支持 `--dry-run` 预览） |
| `mo uninstall <App>` | 彻底卸载应用及其关联残留配置与缓存 |
| `mo analyze [目录]` | 启动基于 BubbleTea 的图形化磁盘占用分析 TUI |
| `mo analyze --trend` | **时序空间变化监测**：对比 7 天前后目录大小增量 $\Delta$，分析激增合理性并给出清理建议 |
| `mo analyze --trend --days 14` | 指定对比历史时间窗口（如 14 天） |
| `mo status` | 紧凑型系统状态与硬件健康度看板 |

---

## 2. MBX (Mr. Boxington) - Rust 跨工作区共享编译缓存

- **作者**：jdx (mise 作者)
- **源码与文档**：[github.com/jdx/mr-boxington](https://github.com/jdx/mr-boxington)

### 2.1 安装方式

**方式一：通过 Cargo 安装（推荐）**
```bash
cargo install mbx --locked
```

**方式二：通过 mise 安装**
```bash
mise use --global --tool-option mr_boxington=true rust mr-boxington
```

### 2.2 全局初始化与环境配置

1. 运行初始化设置：
   ```bash
   mbx setup
   ```
2. 将 Cargo Shim 代理路径加入系统环境变量（写入 `~/.zshrc` 或 `~/.bashrc`）：
   ```bash
   export PATH="$HOME/Library/Application Support/mbx/bin:$PATH"
   ```
3. 重新加载配置后，所有 `cargo` 命令将自动经由 `mbx` 拦截加速。

### 2.3 常用操作指令

- **旧仓库迁移接入**：进入已有 Rust 项目根目录执行：
  ```bash
  mbx adopt
  ```
  *(无损直接接管现存 `target/` 目录，将其纳入全局共享池，省去全量重编)*
- **正常构建**：各项目无感正常使用：
  ```bash
  cargo build
  cargo test
  cargo clippy
  ```
- **查看缓存节省与命中统计**：
  ```bash
  mbx stats
  ```
- **健康度与配置检查**：
  ```bash
  mbx doctor
  ```
- **手动触发磁盘缓存回收 (GC)**：
  ```bash
  mbx gc
  ```

---

## 3. 本次实战磁盘清理与优化记录（沉淀参考）

在本次优化会话中，系统可用空间从 **~275 GB 提升至 495 GB**，累计安全释放净空间超过 **220 GB**。以下为排查逻辑与具体处置方案：

### 3.1 大模型权重与推理缓存消重（累计释放 ~125 GB）

- **痛点诊断**：
  1. `~/.cache/huggingface/hub` 中残留大量原版未量化大模型缓存（如 MOSS 语音、Whisper 等），占 51 GB；
  2. 同一模型在多处重复保存了不同格式：例如 `Qwen3.6-35B` 同时存在于 `gguf-models`（34 GB）和 `~/.omlx/models`（MLX 8-bit 40 GB、MLX 6-bit 27 GB、4-bit 23 GB），单模型占用了 124 GB；
  3. `~/.omlx/cache` 堆积了 36 GB 的历史推理 KV/Context 临时缓存。
- **处置方案**：
  - 清理 HF 原版模型，后续统一只拉取 `mlx-community/*` 量化版；
  - 确立 **`~/.omlx/models` 为唯一核心模型池**，只保留推理速度与显存最优的 6-bit / 4-bit 黄金版本，清理冗余的 GGUF 8-bit 和 MLX 8-bit；
  - 外部服务通过软链接复用（如 `~/.mlx-serve/models/shared-models -> ~/.omlx/models`），实现**单份物理空间、双边透明可用**；
  - 清空 `~/.omlx/cache` 临时推理缓存。

### 3.2 废弃视频流水线与训练残留清理（累计释放 ~58 GB）

- **痛点诊断**：
  1. `~/vpipe-work` 占 48 GB（含 44 GB 的 `MiniMax-H3-FL2VA-4bit` 视频模型与生成产物）；
  2. 查阅本地日志发现：在本地生成一段仅 2.3 秒的 544p 低清短视频耗时超 8 分钟，性价比极低，已无实用价值；
  3. `~/lora-david` 占 10.7 GB，为已经结束的 LoRA 训练历史残留。
- **处置方案**：
  - 果断彻底删除 `~/vpipe-work` 与 `~/.mlx-serve/models` 中的同款视频模型副本；
  - 彻底删除 `~/lora-david`。

### 3.3 代码备份与开发目录瘦身（累计释放 ~15.5 GB）

- **痛点诊断**：
  1. `~/Dev/backup` 占 21 GB，经扫描发现内部存有近百个 `node_modules` 依赖文件夹；
  2. `~/Dev/crypto-projects` 中存在两份完全一样的斯坦福小镇 Python 虚拟环境（`environment` 占 2.2 GB），以及闲置插件的前端依赖（1.5 GB）。
- **优化原则与处置**：
  - **版本控制备份原则**：只要已 Push 到 GitHub/GitLab 远程，本地备份无需留存完整的 `.git` 历史目录，只保留纯代码树即可；
  - **依赖免备份原则**：任何备份仓库都不应备份 `node_modules`（可随时 `pnpm install` 恢复）；
  - 执行递归清除备份中的所有 `node_modules`，`~/Dev/backup` 体积由 21 GB 骤降至 10 GB；
  - 清理 `crypto-projects` 中的重复 Python 环境与闲置依赖，释放 4.5 GB。

### 3.4 常用构建缓存安全边界

- **Gradle 缓存**：安全清空 `~/.gradle/caches`（释放 2.9 GB），后续构建会自动重新拉取。
- **Docker / OrbStack 缓存边界**：
  - **严禁**自动运行 `docker system prune -a --volumes`，因为 `--volumes` 会永久抹除已停止容器的持久化数据库卷（如本地 MySQL/PostgreSQL）；
  - 工具与日常维护应只针对构建缓存（`docker builder prune`）与悬空镜像。
