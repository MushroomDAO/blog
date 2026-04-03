# M1: Blog Pipeline

将原始文字一键发布到 Mycelium Blog。

## 工作流程

```
原始文字 → AI 润色 → 生成 Markdown → 保存 → Build → Deploy
```

## 使用方式

### 方式 1: 手动流程（推荐）

1. **准备原始文字**（raw.txt）

2. **获取 AI Prompt**
```bash
python3 pipeline/m1/polisher.py raw.txt
```

3. **复制 Prompt 到 AI 对话**，获取润色后的 Markdown

4. **保存为 .md 文件**

5. **一键发布**
```bash
./pipeline/m1/m1-publish.sh article.md [cover.png]
```

### 方式 2: 直接发布已有 Markdown

```bash
./pipeline/m1/m1-publish.sh article.md

# 带图片
./pipeline/m1/m1-publish.sh article.md cover.png diagram.png

# 仅保存，不 build/deploy
python3 pipeline/m1/publisher.py article.md --skip-build --skip-deploy
```

## 文章模板

| 类型 | category | tags | 适用场景 |
|------|----------|------|----------|
| tech-experiment | Tech-Experiment | experiment, tutorial | 技术实验、教程 |
| research | Research | research, deep-dive | 深度研究 |
| progress-report | Progress-Report | weekly, progress | 周报、进展 |
| tech-news | Tech-News | news, trends | 科技动态 |

## 文件结构

```
m1/
├── polisher.py       # AI 润色 Prompt 生成
├── publisher.py      # 发布流程（保存→Build→Deploy）
├── m1-publish.sh     # 一键发布脚本
└── README.md         # 本文档
```

## 依赖

- Python 3.9+
- pnpm (build)
- wrangler (deploy)

## 测试 checklist

- [ ] `python3 polisher.py test.txt` 生成正确 Prompt
- [ ] `./m1-publish.sh article.md` 成功发布
- [ ] 带图片 `./m1-publish.sh article.md cover.png` 正确复制图片
- [ ] Build 成功
- [ ] Deploy 成功
- [ ] 浏览器访问确认
