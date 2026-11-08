from pathlib import Path
p=Path('src/content/blog/designing-ai-systems-book-platform-code-review.md');t=p.read_text().replace('wechatTitle: "AI平台怎么建？找到这本书的配套代码"','wechatTitle: "Designing AI Systems：代码解读"');p.write_text(t)
