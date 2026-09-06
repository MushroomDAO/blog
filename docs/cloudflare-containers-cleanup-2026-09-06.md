# Cloudflare Containers 清理记录（2026-09-06）

## 为什么做这件事

8/16–9/6 的账单里，**Containers 占了 99.9%**：

| 项目 | 费用 |
|---|---|
| Container Memory（GiB-second） | $18.96 |
| Container Disk（GB-second） | $1.02 |
| 其余全部（Workers / D1 / KV / R2 / Vectorize / DO） | $0.00（都在免费额度内） |
| **合计 22 天** | **$19.98**，按周期预计 $28.16 |

关键诊断：把用量除以观察时长，得到**平均常驻 4.04 GiB 内存 + 8.08 GB 磁盘，而 vCPU 平均只用了 0.0108 核（约 1%）**。

也就是说容器几乎不干活，但内存一直占着。**Cloudflare Containers 按内存驻留秒计费，不按请求数**，所以空闲照样烧钱——这跟 Workers 的计费模型完全不同，是这次超支的根本原因。

## 当时在跑的四个容器

| 容器 | vCPU | 内存 | 磁盘 | 归属 |
|---|---|---|---|---|
| workbench-loop-engineer-loopengineercontainer | 1 | 6 GiB | 12 GB | `~/Dev/auraai/Self-FDE-WorkBench` |
| workbench-fde-copilot-fdecopilotcontainer | 1 | 6 GiB | 12 GB | `~/Dev/auraai/Self-FDE-WorkBench` |
| mushroom-listmonk-listmonkcontainer | 0.25 | 1 GiB | 4 GB | 本仓库 `pipeline/newsletter/listmonk-container/` |
| hello-container-test-hellocontainer | 0.0625 | 256 MiB | 2 GB | 本仓库 `pipeline/newsletter/hello-container-test/` |

两个 workbench 各 6 GiB，**占总内存容量的 90%（12 / 13.25 GiB）**——按内存权重摊，$18.96 里约 $17 是它们的。

注意：四个容器的代码里**都写了 `sleepAfter = "10m"`**，但账单显示它们并没有真正闲下来。休眠没有兑现成省钱，这一点值得下次上容器前先验证。

## 删了什么

四个全删。删除的是**容器应用**，不是镜像——镜像仍在 `registry.cloudflare.com`，随时可以重新部署恢复。

### 判断依据

- **hello-container-test**：7/27 建的测试容器，零业务价值，纯遗留。
- **mushroom-listmonk**：Cloudflare Container 版的 listmonk，**已被 Fly.io 版本取代**。证据是 `pipeline/newsletter/listmonk-fly/fly.toml` 自己的注释：

  > same trade-off already accepted in **the earlier Cloudflare Container spike**

  现役链路是：`list.mushroom.cv`（DNS `AAAA → 100::` + proxied，流量由 `mushroom-listmonk-proxy` worker 接管）→ **Fly 上的 `mushroom-listmonk`**。前端 `SubscribeForm.astro` 直接 POST 到 `https://list.mushroom.cv/subscription/form`。

- **两个 workbench**：属于另一个项目，最后部署在 8 月初，6 GiB 对 1% CPU 明显超配。经确认后停掉，需要时再部署。

### 删除后的验证

```
/health            → 200   （首次请求 000 是 Fly 机器冷启动，重试即 200 / 0.19s）
/subscription/form → 200   （前端表单实际打的端点）
blog.mushroom.cv   → 200
```

**订阅功能不受影响。**

## 怎么恢复

镜像都还在，重新部署即可：

```bash
# blog 仓库的两个（如果真的还需要）
cd pipeline/newsletter/listmonk-container && npx wrangler deploy
cd pipeline/newsletter/hello-container-test && npx wrangler deploy

# workbench 两个
cd ~/Dev/auraai/Self-FDE-WorkBench/deploy/fde-copilot   && npx wrangler deploy
cd ~/Dev/auraai/Self-FDE-WorkBench/deploy/loop-engineer && npx wrangler deploy
```

查看当前状态：

```bash
npx wrangler containers list            # 有哪些容器、几个活实例
npx wrangler containers info <ID>       # 规格（vcpu / memory / disk）
npx wrangler containers images list     # registry 里还留着哪些镜像
```

## 下次上 Containers 之前

1. **先问它需不需要常驻。** 按内存秒计费意味着一个空转的 6 GiB 容器和一个满负荷的 6 GiB 容器花一样的钱。偶发任务用 Workers 或 Queues，别用 Container。
2. **规格按实际用量定，不要按"以防万一"定。** 这次 1% 的 CPU 利用率说明 6 GiB / 1 vCPU 是凭感觉填的。
3. **`sleepAfter` 写了不等于生效**，上线后要回头核对账单里的 GiB-second，用「用量 ÷ 时长」算出真实常驻量再判断。
4. **测试容器用完就删。** `hello-container-test` 白跑了 40 天。
5. 设一个预算告警（Cloudflare 正在给 pay-as-you-go 账号默认铺开），别等月底看账单。
