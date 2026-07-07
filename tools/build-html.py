#!/usr/bin/env python3
"""build-html.py - 把 docs/*.md 转为 .html(GitHub Pages 静态)

不需要 pandoc,纯 Python markdown(简化版本)。
GitHub Pages build_type=legacy + path=/docs:
- docs/index.html 是入口
- docs/*.html 也可访问
- 但 .md 直接 404(除非 jekyll)

这个脚本把 .md → .html,放在 docs/ 同目录。
GitHub Pages 直接 serve .html。

用法:
  python3 tools/build-html.py
"""
import re
import sys
from pathlib import Path
from html import escape

# 极简 markdown 渲染(只支持 kallax 文档需要的语法)
def md_to_html(text):
    html = text
    # 标题
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # 代码块 ```...```
    html = re.sub(
        r'```(\w*)\n(.*?)```',
        r'<pre><code class="language-\1">\2</code></pre>',
        html, flags=re.DOTALL
    )

    # 行内代码 `...`
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # 链接 [text](url)
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

    # 加粗 **...**
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)

    # 表格(简化)
    lines = html.split('\n')
    in_table = False
    out_lines = []
    for line in lines:
        if line.startswith('|') and '---' not in line:
            if not in_table:
                out_lines.append('<table>')
                in_table = True
            cells = [c.strip() for c in line.split('|')[1:-1]]
            row = '<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>'
            out_lines.append(row)
        elif '---' in line and in_table:
            continue  # 跳过分隔行
        elif in_table and not line.startswith('|'):
            out_lines.append('</table>')
            in_table = False
            out_lines.append(line)
        else:
            out_lines.append(line)
    if in_table:
        out_lines.append('</table>')
    html = '\n'.join(out_lines)

    # 段落
    html = re.sub(r'\n\n+', r'\n\n', html)
    paragraphs = html.split('\n\n')
    html = '\n\n'.join(
        f'<p>{p}</p>' if not p.startswith('<') and not p.startswith('#') else p
        for p in paragraphs
    )

    return html

# 包装成完整 HTML
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | kallax-experts</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    max-width: 900px; margin: 2em auto; padding: 0 1em;
    color: #1a1a1a; background: #fafafa; line-height: 1.6;
  }}
  h1, h2, h3 {{ color: #1a1a1a; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; }}
  h1 {{ font-size: 2em; }}
  h2 {{ font-size: 1.5em; margin-top: 1.5em; }}
  h3 {{ font-size: 1.2em; margin-top: 1.2em; border-bottom: none; }}
  pre {{ background: #f5f5f5; padding: 1em; border-radius: 6px; overflow-x: auto; }}
  code {{ background: #f0f0f0; padding: 0.1em 0.3em; border-radius: 3px; font-family: monospace; }}
  pre code {{ background: transparent; padding: 0; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
  td, th {{ border: 1px solid #ddd; padding: 0.5em; }}
  th {{ background: #f0f0f0; }}
  a {{ color: #0066cc; }}
  p {{ margin: 1em 0; }}
  .back {{ background: #fff; padding: 1em; border-radius: 6px; margin-bottom: 2em; border: 1px solid #eee; }}
</style>
</head>
<body>
<a href="index.html" class="back">← 返回 kallax-experts 首页</a>
{content}
<hr>
<p class="back">
  <a href="https://github.com/godlockin/kallax-experts/blob/main/{md_path}">📝 在 GitHub 上编辑此页</a>
  · <a href="https://github.com/godlockin/kallax-experts">kallax-experts</a>
</p>
</body>
</html>"""

def main():
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("docs/ not found")
        sys.exit(1)

    converted = 0
    for md_file in sorted(docs_dir.glob("*.md")):
        # 跳过根 README(本仓库 README 是项目说明,放根,GitHub 自动渲染)
        if md_file.name == "README.md" and md_file.parent.resolve() == Path(".").resolve():
            continue

        md_text = md_file.read_text(encoding="utf-8")
        body = md_to_html(md_text)

        # 提取第一个 # 标题
        title_match = re.search(r'^# (.+)$', md_text, re.MULTILINE)
        title = title_match.group(1) if title_match else md_file.stem

        html = HTML_TEMPLATE.format(
            title=escape(title),
            content=body,
            md_path=f"docs/{md_file.name}"
        )

        html_file = md_file.with_suffix(".html")
        html_file.write_text(html, encoding="utf-8")
        print(f"  {md_file.name} → {html_file.name}")
        converted += 1

    print(f"\n✅ Converted {converted} .md → .html")

if __name__ == "__main__":
    main()