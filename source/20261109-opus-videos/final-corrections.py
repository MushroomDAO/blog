from pathlib import Path
p=Path('src/content/blog/awesome-opus-videos-code-animation-guide.md');t=p.read_text()
t=t.replace('没有随附动画的 HTML/JS 源码，也没有可直接启动的渲染应用','没有独立的动画 HTML/JS 源文件，也没有可直接启动的渲染应用')
t=t.replace('It does not ship the animations’ HTML/JS source or a runnable rendering application.','It does not contain standalone animation HTML/JS source files or a runnable rendering application.')
t=t.replace('最初的审计脚本误把可选复刻链接要求为必填，并用简单代码围栏解析截断了一个内嵌代码块的长提示词；核对数据结构后修正了审计器，上游内容未改。','')
t=t.replace('An initial auditor incorrectly required every remake URL and truncated one nested-fence prompt. We corrected the auditor to match the data structure without changing upstream content. ','')
p.write_text(t)
