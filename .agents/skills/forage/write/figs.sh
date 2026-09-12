#!/bin/bash
# ============================================================================
# 按交接 JSON 的 figs 描述，调 Codex 生成 4 张正文插图
#
#   bash .agents/skills/forage/write/figs.sh SLUG
#
# 读 radar/staging/SLUG.json（ip + figs），稿子在 radar/staging/SLUG.md 或
# src/content/blog/SLUG.md。图落到 src/assets/images/SLUG-fig-NN.png。
# 实测每篇 5-14 分钟，调用方的超时要给够；多篇可以并行跑（出图在云端）。
# ============================================================================
set -uo pipefail
cd "$(dirname "$0")/../../../.."
S="$1"
STAGE=radar/staging
J="$STAGE/$S.json"
MD=src/content/blog/$S.md; [ -f "$MD" ] || MD="$(pwd)/$STAGE/$S.md"
[ -f "$J" ] || { echo "❌ 缺交接 JSON：$J"; exit 1; }

IP=$(python3 -c "import json;print(json.load(open('$J')).get('ip','mushroom'))")
case "$IP" in
  baobao) SK=mycelium-baobao-cat-illustrations ;;
  avatar) SK=mycelium-avatar-illustrations ;;
  *)      SK=mycelium-mushroom-illustrations ;;
esac
LIST=$(python3 -c "
import json
f=json.load(open('$J'))['figs']
print('\n'.join(f'- 图{k}（保存为 src/assets/images/$S-fig-{k}.png）：{v}' for k,v in sorted(f.items())))")

START=$(date +%s)
codex exec -C "$(pwd)" -s workspace-write "Use \$$SK 读取 $MD 了解上下文。锚点已经选好，严格按下面几条逐张生成 16:9 纯白底手绘正文配图（主角承担核心动作，把该段的核心流程/逻辑骨架画出来；图上文字尽量少、只用简短中文或数字、不要错别字）：
$LIST
用完 image_generation 工具后，每张图默认落在 ~/.codex/generated_images/<session-id>/ 下（不是仓库里！），生成完必须在同一个回合里用 shell cp 把它们按上面指定的文件名复制到 src/assets/images/ —— 这是硬性最后一步，没做完不算完成。不要生成 banner，不要拼图，不要修改 markdown 文件。" > "$STAGE/$S.codex.log" 2>&1
echo "codex exit=$? elapsed=$(( $(date +%s)-START ))s"
ls src/assets/images/$S-fig-*.png 2>/dev/null || {
  echo "⚠️ 仓库里没有图。先捞孤儿：find ~/.codex/generated_images -mindepth 1 -maxdepth 1 -newermt '20 minutes ago'"
  exit 1
}
