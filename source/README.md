# source/ — 内容来源暂存目录

每个待发布的内容放在独立子目录下。扫描脚本会定期检测新目录并自动发布。

## 目录结构

```
source/
  ITEM-NAME/           # 每个内容一个目录，名称用英文短横线，无空格
    info.txt           # 主体文字内容（可选）
    notes.md           # 补充说明（可选）
    url.txt            # 来源 URL，每行一个（可选）
    meta.yaml          # 元数据提示（可选，见下方说明）
    *.png / *.jpg      # 图片，第一张优先用作 banner（可选）
    *.mp4 / *.mov      # 视频（可选，提取封面帧）
    .published         # 发布完成后自动创建，不要手动添加
    .processing        # 处理中临时锁，不要手动添加
```

## meta.yaml 格式（可选）

```yaml
title: "可选标题提示"          # 不写则由 AI 生成
category: "Tech-News"          # Tech-News | Tech-Experiment | Research | Progress-Report | DN
tags: ["tag1", "tag2"]         # 不写则由 AI 生成
theme: "blue"                  # 微信主题：blue | claude | chengyun | mint | purple | cyber | rose
```

## 使用方式

1. 新建子目录，放入内容文件
2. 等扫描脚本自动检测（默认每小时一次），或手动触发：
   ```bash
   ./scripts/scan-sources.sh
   ```
3. 发布完成后目录内会出现 `.published` 文件

## 示例

```
source/
  agent-game-forge/
    info.txt          # 用户提供的原始文字介绍
    url.txt           # https://github.com/0x0funky/agent-game-forge
    screenshot.png    # 项目截图，用作 banner
```
