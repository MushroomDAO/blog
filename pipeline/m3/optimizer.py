#!/usr/bin/env python3
"""
M3 小红书内容优化器
将普通文本转换为小红书风格
"""

import re
import json
from typing import List, Dict, Tuple
from pathlib import Path

class XHSOptimizer:
    """小红书内容优化器"""
    
    # 小红书风格特征词
    EMOTICONS = [
        '🌟', '✨', '💫', '🎯', '🔥', '💥', '🎉', '🎊',
        '💖', '💕', '💗', '💓', '🥰', '😍', '🤩',
        '🤔', '🧐', '🤓', '💡', '📌', '✅', '❌',
        '👉', '👆', '👇', '✌️', '👍', '👏', '🙌',
        '🌿', '🍃', '🌸', '🌺', '🌼', '🌻', '🌷',
        '🍀', '💐', '🌹', '🥀', '🌾', '🌵', '🌲',
        '☀️', '🌤️', '⛅', '🌥️', '☁️', '🌦️', '🌧️',
        '📖', '📚', '📓', '📔', '📝', '✏️', '🖊️',
        '💻', '⌨️', '🖥️', '🖱️', '💾', '💿', '📀',
        '📱', '☎️', '📞', '📟', '📠', '🔋', '🔌'
    ]
    
    # 小红书常用开场白
    OPENINGS = [
        "姐妹们！",
        "家人们！",
        "宝子们！",
        "救命！",
        "谁懂啊！",
        "挖到宝了！",
        "绝绝子！",
        "YYDS！",
        "破防了！",
        "原地封神！"
    ]
    
    # 小红书常用结尾
    ENDINGS = [
        "喜欢的姐妹记得点赞收藏！",
        "觉得有用就关注我吧！",
        "有问题评论区见！",
        "记得一键三连！",
        "下期见！",
        "持续更新中...",
        "点个关注不迷路！"
    ]
    
    # 标签库
    TAG_CATEGORIES = {
        'tech': ['#AI工具', '#效率神器', '#打工人必备', '#科技改变生活', '#生产力工具', '#效率提升', '#人工智能', '#黑科技'],
        'learning': ['#学习方法', '#自我提升', '#知识分享', '#学习日常', '#职场技能', '#干货分享', '#经验分享'],
        'lifestyle': ['#生活方式', '#日常分享', '#好物推荐', '#生活小技巧', '#实用干货', '#宝藏发现'],
        'work': ['#职场日常', '#工作效率', '#职场干货', '#打工人', '#办公技巧', '#职场进阶']
    }
    
    def __init__(self):
        self.max_title_length = 20
        self.max_content_length = 1000
    
    def optimize(self, content: str, category: str = 'tech') -> Dict:
        """
        优化内容
        
        Args:
            content: 原始内容
            category: 分类 (tech/learning/lifestyle/work)
        
        Returns:
            {
                'title': str,
                'content': str,
                'tags': List[str],
                'keywords': List[str],
                'suggested_images': int
            }
        """
        # 1. 提取标题
        title = self._extract_title(content)
        
        # 2. 提取关键词
        keywords = self._extract_keywords(content)
        
        # 3. 转换内容风格
        optimized_content = self._convert_style(content, title)
        
        # 4. 生成标签
        tags = self._generate_tags(content, category, keywords)
        
        # 5. 建议图片数量
        suggested_images = self._suggest_image_count(content)
        
        return {
            'title': title,
            'content': optimized_content,
            'tags': tags,
            'keywords': keywords,
            'suggested_images': suggested_images
        }
    
    def _extract_title(self, content: str) -> str:
        """提取标题"""
        lines = content.strip().split('\n')
        
        # 尝试找第一行作为标题
        for line in lines:
            line = line.strip()
            # 跳过空行和Markdown标记
            if line and not line.startswith('#') and not line.startswith('---'):
                # 清理Markdown格式
                title = re.sub(r'[#*_`]', '', line)
                # 限制长度
                if len(title) > self.max_title_length:
                    title = title[:self.max_title_length - 1] + '...'
                return title
        
        return "分享"
    
    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取（可以改进为TF-IDF或BERT）
        words = re.findall(r'\b[A-Za-z]{3,}\b|\b[\u4e00-\u9fa5]{2,}\b', content)
        
        # 统计词频
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 返回高频词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:5]]
    
    def _convert_style(self, content: str, title: str) -> str:
        """转换为小红书风格"""
        lines = content.strip().split('\n')
        result_lines = []
        
        # 添加开场白 (30%概率)
        if len(lines) > 3 and hash(title) % 10 < 3:
            result_lines.append(self.OPENINGS[hash(title) % len(self.OPENINGS)])
            result_lines.append("")
        
        paragraph_count = 0
        for i, line in enumerate(lines):
            line = line.strip()
            
            # 跳过标题行
            if line == title or line in ['---', '']:
                continue
            
            # 处理Markdown标题
            if line.startswith('#'):
                line = re.sub(r'^#+\s*', '', line)
                line = f"✨ {line}"
            
            # 处理列表
            if line.startswith('- ') or line.startswith('* '):
                line = f"• {line[2:]}"
            
            # 处理数字列表
            if re.match(r'^\d+\.', line):
                line = f"👉 {line}"
            
            # 添加emoji (每隔3行)
            if paragraph_count % 3 == 0 and len(line) > 10:
                emoji = self.EMOTICONS[hash(line) % len(self.EMOTICONS)]
                line = f"{emoji} {line}"
            
            # 短句处理（小红书喜欢短句）
            if len(line) > 50 and '。' in line:
                # 在长句后换行
                sentences = line.split('。')
                for j, sent in enumerate(sentences):
                    if sent.strip():
                        if j < len(sentences) - 1:
                            sent += '。'
                        result_lines.append(sent.strip())
            else:
                result_lines.append(line)
            
            # 每2-3行添加空行
            paragraph_count += 1
            if paragraph_count % 3 == 0 and i < len(lines) - 1:
                result_lines.append("")
        
        # 添加结尾 (50%概率)
        if hash(content) % 10 < 5:
            result_lines.append("")
            result_lines.append(self.ENDINGS[hash(content) % len(self.ENDINGS)])
        
        result = '\n'.join(result_lines)
        
        # 检查字数限制
        if len(result) > self.max_content_length:
            result = result[:self.max_content_length - 3] + '...'
        
        return result
    
    def _generate_tags(self, content: str, category: str, keywords: List[str]) -> List[str]:
        """生成标签"""
        tags = []
        
        # 从分类标签库选择
        if category in self.TAG_CATEGORIES:
            category_tags = self.TAG_CATEGORIES[category]
            # 根据内容哈希选择2-3个
            selected = [category_tags[hash(content + str(i)) % len(category_tags)] 
                       for i in range(3)]
            tags.extend(selected)
        
        # 从关键词生成标签
        for keyword in keywords[:2]:
            if len(keyword) >= 2:
                tag = f"#{keyword}"
                if tag not in tags:
                    tags.append(tag)
        
        # 去重并限制数量
        tags = list(dict.fromkeys(tags))[:5]
        
        return tags
    
    def _suggest_image_count(self, content: str) -> int:
        """建议图片数量"""
        content_length = len(content)
        
        if content_length < 300:
            return 1
        elif content_length < 600:
            return 3
        elif content_length < 1000:
            return 6
        else:
            return 9


def optimize_content(content: str, category: str = 'tech') -> Dict:
    """
    便捷函数：优化内容
    
    Usage:
        result = optimize_content("你的文章内容")
        print(result['title'])
        print(result['content'])
        print(result['tags'])
    """
    optimizer = XHSOptimizer()
    return optimizer.optimize(content, category)


if __name__ == '__main__':
    # 测试
    test_content = """
# AutoAgent：首个自优化智能体开源库

AutoAgent 是由 Kevin Gu 等人开发的全球首个专注于"自优化（Self-optimizing）"的开源智能体框架。

## 创新架构

采用了极简的"元/任务"分离架构：

- 任务智能体负责实际执行
- 元智能体作为监督者负责改进

## 核心机制

强调"推理轨迹就是一切"：

1. 元智能体深度读取推理过程
2. 针对性修正失败模式
3. 防止过拟合的自我反思

## 实测表现

在极具挑战的基准测试中双双登顶：

| 基准测试 | 成绩 |
|---------|------|
| SpreadsheetBench | 96.5% |
| TerminalBench | 55.1% |

这证明了AI可以实现高度动态的自组装与自我进化。
"""
    
    result = optimize_content(test_content, 'tech')
    print("=== 优化结果 ===")
    print(f"\n标题: {result['title']}")
    print(f"\n标签: {result['tags']}")
    print(f"\n关键词: {result['keywords']}")
    print(f"\n建议图片数: {result['suggested_images']}")
    print(f"\n内容:\n{result['content']}")
