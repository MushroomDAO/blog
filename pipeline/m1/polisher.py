#!/usr/bin/env python3
"""
M1: AI Content Polisher
将原始文字润色为适合 Blog 的 Markdown 格式
支持：去 AI 味、优化结构、生成 Frontmatter
"""

import re
import json
from datetime import datetime
from typing import Optional

# 文章模板
TEMPLATES = {
    "tech-experiment": {
        "category": "Tech-Experiment",
        "tags": ["experiment", "tutorial"],
        "description": "技术实验记录与经验分享"
    },
    "research": {
        "category": "Research", 
        "tags": ["research", "deep-dive"],
        "description": "深度技术研究与洞察"
    },
    "progress-report": {
        "category": "Progress-Report",
        "tags": ["weekly", "progress"], 
        "description": "项目进展与阶段汇报"
    },
    "tech-news": {
        "category": "Tech-News",
        "tags": ["news", "trends"],
        "description": "前沿科技动态与趋势分析"
    }
}

# 去 AI 味的润色 Prompt 模板
POLISH_PROMPT_TEMPLATE = """你是一位资深的技术内容编辑，负责将 raw text 润色为高质量的 Markdown 文章。

## 润色要求

1. **去 AI 味**（关键！）：
   - 避免"首先...其次...最后..."的机械结构
   - 避免"值得注意的是/需要指出的是"等套话
   - 使用自然、口语化的表达方式
   - 适当使用短句和段落，模拟人工写作
   - 加入个人见解和主观评价

2. **结构优化**：
   - 使用清晰的 H2/H3 标题层级
   - 列表项控制在 3-5 个
   - 段落不超过 5 行

3. **技术内容规范**：
   - 代码块标注语言类型
   - 专业术语首次出现时解释
   - 关键结论用 **粗体** 强调

## 输出格式

```yaml
---
title: "中文标题（简洁有力）"
titleEn: "English Title"
description: "一句话描述（中文）"
descriptionEn: "One sentence description"
category: {category}
tags: {tags}
---
```

## 正文内容

[润色后的 Markdown，去除 AI 味，自然流畅]

## 输入原文

{content}

请直接输出 YAML frontmatter + Markdown 正文，不要有任何解释。"""


def detect_template_type(content: str) -> str:
    """根据内容检测最合适的模板类型"""
    content_lower = content.lower()
    
    if any(kw in content_lower for kw in ["实验", "测试", "benchmark", "性能", "优化"]):
        return "tech-experiment"
    elif any(kw in content_lower for kw in ["周报", "进展", "进度", "本周", "总结"]):
        return "progress-report"
    elif any(kw in content_lower for kw in ["研究", "论文", "分析", "原理", "架构"]):
        return "research"
    else:
        return "tech-news"


def generate_frontmatter(
    title: str,
    title_en: str,
    description: str,
    description_en: str,
    template_type: str,
    custom_tags: Optional[list] = None
) -> str:
    """生成文章 Frontmatter"""
    template = TEMPLATES.get(template_type, TEMPLATES["tech-news"])
    
    tags = custom_tags if custom_tags else template["tags"]
    today = datetime.now().strftime("%Y-%m-%d")
    
    frontmatter = f"""---
title: '{title}'
titleEn: '{title_en}'
description: '{description}'
descriptionEn: '{description_en}'
pubDate: '{today}'
category: '{template["category"]}'
tags: {json.dumps(tags, ensure_ascii=False)}
---

"""
    return frontmatter


def polish_content(
    raw_content: str,
    template_type: Optional[str] = None,
    custom_tags: Optional[list] = None
) -> dict:
    """
    润色内容（实际实现会调用 AI API，这里提供接口定义）
    
    Returns:
        {
            "frontmatter": str,
            "content": str,
            "title": str,
            "template_type": str
        }
    """
    if not template_type:
        template_type = detect_template_type(raw_content)
    
    # 这里会调用 AI API 进行润色
    # 返回结构化的内容
    
    return {
        "template_type": template_type,
        "raw_content": raw_content,
        "prompt": POLISH_PROMPT_TEMPLATE.format(
            content=raw_content,
            category=TEMPLATES[template_type]["category"],
            tags=TEMPLATES[template_type]["tags"]
        )
    }


def sanitize_filename(title: str) -> str:
    """将标题转换为安全的文件名"""
    # 保留中文、英文、数字，其他转为 -
    filename = re.sub(r'[^\w\u4e00-\u9fa5]', '-', title)
    filename = re.sub(r'-+', '-', filename).strip('-')
    return filename[:50]  # 限制长度


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python polisher.py <raw_text_file>")
        print("\nTemplates:")
        for k, v in TEMPLATES.items():
            print(f"  {k}: {v['category']} - {v['description']}")
        sys.exit(1)
    
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        raw = f.read()
    
    result = polish_content(raw)
    print(f"Detected template: {result['template_type']}")
    print(f"Suggested filename: {sanitize_filename(raw.split(chr(10))[0])}.md")
    print("\n--- AI Prompt (copy to AI chat) ---\n")
    print(result['prompt'])
