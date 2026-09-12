# 评审台「开始写」任务 —— 后台会话执行手册

你是被 8042 评审台的「开始写」按钮拉起的后台 Claude Code 会话（`claude --bg`）。
用户已经在评审台上把今天的条目都判完了，现在要你把标了 **写** 的条目全部写完、发布
（blog + 公众号草稿），不要再问「要不要发布」。用户不在终端前，全程无人值守；
他可以用 `claude attach <id>` 接进来看。

这套流程是 2026-09-11 那批 9 篇手动跑通后固化下来的，按顺序做。

## 0. 汇报进度的方式

页面读 `radar/write-job.json`。每完成一个里程碑就汇报一次（用户在 MacBook 上看的就是这个）：

```bash
python3 .agents/skills/forage/write/job.py progress "<一句话>"
```

结束时**必须**二选一收尾，否则页面会一直显示「进行中」：

```bash
python3 .agents/skills/forage/write/job.py done "发了 N 篇：slug1, slug2…；跳过 M 篇：理由"
python3 .agents/skills/forage/write/job.py fail "卡在哪一步、为什么、已完成了哪些"
```

## 1. 取清单 + 查重

```bash
python3 .agents/skills/forage/store.py sync        # 先对账，已发布的 write 会转成 published
python3 - <<'EOF'
import sys, json; sys.path.insert(0, '.agents/skills/forage')
from store import conn
for r in conn().execute("SELECT id,src,title,url,u_note FROM items WHERE decision='write'"):
    print(json.dumps(dict(r), ensure_ascii=False))
EOF
```

- 条目的 `u_note` 是用户的批注，**必须照做**（例如「这是视频，借鉴其他报道和一手信息来写」）。
- 每条跑查重：`set -a; source .env; set +a; node .agents/skills/blog-publisher/check-duplicate.cjs "<url>" "<实体名>"`。
  「正文出现实体名」只说明别的文章顺带提过，要打开看是不是专文，不是专文就照写。
- 真重复的，在评审台改标 skip：
  `curl -s -X POST "$(cat radar/.server-url)api/decide" -H 'Content-Type: application/json' -d '{"id":"<id>","decision":"skip"}'`

## 2. 并行写初稿（子 agent）

每条起一个 general-purpose 子 agent（一次性全部并行发出），prompt 里写：

> 先完整阅读 .agents/skills/forage/write/BRIEF.md 并严格遵守。工作目录 /Users/jason/Dev/mycelium/blog。
> 你的选题：<来源> <url>，用户批注：<u_note>。<对这条的具体提示：是什么、要核实什么、给 Mac 用户什么建议…>

要点：
- 小红书线索只是线索，必须回查到一手源（GitHub / HF / 官方公告 / 论文）。小红书 CLI 每条最多调 2 次，撞验证码立刻停。
- 稿子写到 `radar/staging/SLUG.md`，交接信息写到 `radar/staging/SLUG.json`。**不许进 `src/content/blog/`**。
- 子 agent 判 `write:false` 的（找不到一手源 / 空壳），不发，在 done 汇总里写明理由。

## 3. 每篇的收尾（初稿一回来就开始，不用等全部）

出图可以和别的篇并行，**发布必须串行**（build/deploy/git 会互相踩）。

```bash
S=<slug>
# 插图（Codex，云端出图，5-14 分钟；后台跑，多篇可同时跑）
bash .agents/skills/forage/write/figs.sh $S           # Bash timeout 给 600000，或 run_in_background
# banner（本地 FLUX，约 75 秒，一次只跑一个）
bash .agents/skills/banner-creator/generate-banner.sh "$S" "$(python3 -c "import json;print(json.load(open('radar/staging/$S.json'))['banner_prompt'])")"
```

banner 生成后用 Read 看一眼图（验证脚本管不了「好不好看、切不切题」）。插图挑一张看一眼。

轮到发布时：

```bash
python3 .agents/skills/forage/write/insert.py $S        # 压图到 <90KB + 替换 <!--FIG:NN--> 占位
mv radar/staging/$S.md src/content/blog/
scripts/publish-blog.sh src/content/blog/$S.md --wechat --theme blue
python3 .agents/skills/forage/write/mem.py $S "YYYY-MM-DD 已发布；<一句话结论>" "<索引标题>"
python3 .agents/skills/forage/write/job.py progress "$S 已发布"
```

`publish-blog.sh` 包含 build → SEO 校验 → deploy → 线上 200 → commit+push → 语义索引 → 公众号草稿。
看它的输出确认 `→ 200`、`✓ pushed`、`Draft created: media_id=`，三个都有才算发完。

发布前把 `pubDate`/`updatedDate` 改成**当天**（跑过零点就用新日期）。

## 4. 收尾

```bash
python3 .agents/skills/forage/store.py sync    # 已发布的 write 条目转成 published，页面上就挪到「已发布」
```

在 `.agents/skills/forage/FEEDBACK.md` 追加一节今天的记录：用户标了几条、实发几条、没发的理由、
调研中发现的采集侧问题。然后 `job.py done`。

## 权限边界

这个会话跑在 auto 模式下，发布流程固定用到的命令已在 `.claude/settings.local.json` 放行。
遇到被拦的操作，**不要想办法绕过**：换一条正当路径，实在不行就跳过这一步，
在 done/fail 的汇总里写清楚「哪步被拦、需要用户做什么」。
