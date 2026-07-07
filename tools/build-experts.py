#!/usr/bin/env python3
"""build-experts.py - 把 experts/*.md 转为 docs/experts/*/{name}.html + 列表页

输出:
- docs/experts/index.html (可搜索列表)
- docs/experts/<category>/<expert>.html (每个 expert 单独页)
- docs/experts/data.json (JS 搜索用)

用法:
  python3 tools/build-experts.py
"""
import re
import json
import sys
from pathlib import Path
from html import escape

KALLAX_ROOT = Path(".")
EXPERT_DIR = KALLAX_ROOT / "experts"
OUT_DIR = KALLAX_ROOT / "docs" / "experts"


# 极简 markdown 渲染
def md_to_html(text):
    html = text
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(
        r'```(\w*)\n(.*?)```',
        r'<pre><code class="language-\1">\2</code></pre>',
        html, flags=re.DOTALL
    )
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', html)

    # 表格
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
            continue
        elif in_table and not line.startswith('|'):
            out_lines.append('</table>')
            in_table = False
            out_lines.append(line)
        else:
            out_lines.append(line)
    if in_table:
        out_lines.append('</table>')
    html = '\n'.join(out_lines)

    paragraphs = html.split('\n\n')
    html = '\n\n'.join(
        f'<p>{p}</p>' if not p.startswith('<') and not p.startswith('#') else p
        for p in paragraphs
    )
    return html


def extract_frontmatter(md_text):
    """提取 frontmatter 和 body,返回 (fm_str, body_str)"""
    if not md_text.startswith("---"):
        return "", md_text
    parts = md_text.split("---", 2)
    if len(parts) < 3:
        return "", md_text
    return parts[1].strip(), parts[2].strip()


def parse_fm(fm_text):
    """极简 frontmatter 解析 — 支持:key: val / list / inline list / nested dict"""
    result = {}
    current_key = None

    for line in fm_text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # 顶层 key: value
        m = re.match(r'^(\w+):\s*(.*)$', line)
        if m and not line.startswith(" ") and not line.startswith("\t"):
            key = m.group(1)
            value = m.group(2).strip()

            # inline list [a, b, c]
            m_inline = re.match(r'^\[([^\]]*)\]$', value)
            if m_inline:
                items = [x.strip().strip('"').strip("'")
                         for x in m_inline.group(1).split(",") if x.strip()]
                result[key] = items
            else:
                # 字符串去引号
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                result[key] = value
            current_key = key
            continue

        # 嵌套 list 项(以 - 开头)
        if line.lstrip().startswith("- ") and current_key:
            value = line.lstrip()[2:].strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            if not isinstance(result.get(current_key), list):
                result[current_key] = []
            result[current_key].append(value)
            continue

        # 嵌套 dict(以 "  key: value" 开头)
        m2 = re.match(r'^\s+(\w+):\s*(.*)$', line)
        if m2 and current_key:
            sub_key = m2.group(1)
            sub_value = m2.group(2).strip()

            # inline list [a, b, c]
            m_sub_inline = re.match(r'^\[([^\]]*)\]$', sub_value)
            if m_sub_inline:
                items = [x.strip().strip('"').strip("'")
                         for x in m_sub_inline.group(1).split(",") if x.strip()]
                if not isinstance(result.get(current_key), dict):
                    result[current_key] = {}
                result[current_key][sub_key] = items
            else:
                if sub_value.startswith('"') and sub_value.endswith('"'):
                    sub_value = sub_value[1:-1]
                elif sub_value.startswith("'") and sub_value.endswith("'"):
                    sub_value = sub_value[1:-1]
                if not isinstance(result.get(current_key), dict):
                    result[current_key] = {}
                result[current_key][sub_key] = sub_value
            continue

        # 嵌套 dict 的 list 项(以 "    - val" 开头)
        if line.lstrip().startswith("- ") and current_key and isinstance(result.get(current_key), dict):
            value = line.lstrip()[2:].strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            # 找最近的 sub_key(从上一行)
            sub_keys = [k for k in result.get(current_key, {}).keys()]
            if sub_keys:
                last_sub_key = sub_keys[-1]
                if not isinstance(result[current_key][last_sub_key], list):
                    result[current_key][last_sub_key] = []
                result[current_key][last_sub_key].append(value)
            continue

    return result


PAGE_TEMPLATE = """<!DOCTYPE html>
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
  .frontmatter {{ background: #f9f9f9; padding: 1em; border-radius: 6px; font-size: 0.9em; }}
  .frontmatter dt {{ font-weight: bold; display: inline-block; min-width: 100px; }}
  .frontmatter dd {{ display: inline; margin: 0; }}
  .frontmatter dd::after {{ content: ""; display: block; }}
</style>
</head>
<body>
<a href="https://godlockin.github.io/kallax-experts/experts/" class="back">← 返回 Experts 列表</a> |
<a href="https://godlockin.github.io/kallax-experts/" class="back">🏠 回到 kallax-experts 首页</a>

<h1>{emoji} {name} <code style="font-size: 0.6em;">{role_id}</code></h1>
<p><em>{vibe}</em></p>

{fm_html}

{body_html}

<hr>
<p>
  <a href="https://github.com/godlockin/kallax-experts/blob/main/experts/{md_relpath}">📝 在 GitHub 上编辑此 expert</a>
  · <a href="https://github.com/godlockin/kallax-experts">kallax-experts</a>
</p>
</body>
</html>"""


LIST_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Experts 列表 | kallax-experts</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
    max-width: 1000px; margin: 2em auto; padding: 0 1em;
    color: #1a1a1a; background: #fafafa; line-height: 1.6;
  }}
  h1 {{ font-size: 2em; border-bottom: 3px solid #1a1a1a; padding-bottom: 0.3em; }}
  .search {{
    width: 100%; padding: 0.8em 1em; font-size: 1.1em;
    border: 2px solid #0066cc; border-radius: 8px; margin: 1.5em 0;
  }}
  .stats {{ display: flex; gap: 1.5em; margin: 1em 0; color: #666; }}
  .filters {{ margin: 1em 0; display: flex; flex-wrap: wrap; gap: 0.5em; }}
  .filter-btn {{
    padding: 0.3em 0.8em; border: 1px solid #ddd; border-radius: 4px;
    background: white; cursor: pointer; font-size: 0.9em;
  }}
  .filter-btn:hover {{ background: #f0f0f0; }}
  .filter-btn.active {{ background: #0066cc; color: white; border-color: #0066cc; }}
  .expert-list {{ margin-top: 1em; }}
  .expert {{
    background: #fff; padding: 1.2em; margin: 0.6em 0;
    border-radius: 8px; border-left: 4px solid #0066cc;
    cursor: pointer; transition: transform 0.1s;
  }}
  .expert:hover {{ background: #f5f5f5; transform: translateX(2px); }}
  .expert h3 {{ margin: 0; font-size: 1.2em; border: none; }}
  .expert h3 a {{ text-decoration: none; color: #1a1a1a; }}
  .expert h3 a:hover {{ color: #0066cc; }}
  .expert .meta {{ color: #666; font-size: 0.85em; margin-top: 0.4em; }}
  .expert .vibe {{ color: #555; font-style: italic; margin-top: 0.3em; }}
  .badge {{
    display: inline-block; padding: 0.1em 0.5em; border-radius: 3px;
    font-size: 0.8em; margin-right: 0.3em;
  }}
  .badge-source {{ background: #e3f2fd; color: #1976d2; }}
  .badge-priority {{ background: #fff3e0; color: #f57c00; }}
  .badge-trigger {{ background: #c8e6c9; color: #2e7d32; font-weight: bold; }}
  .badge-desc {{ background: #fff9c4; color: #f57f17; }}
  .no-results {{ text-align: center; padding: 3em; color: #999; }}
  .back {{ background: #fff; padding: 1em; border-radius: 6px; margin-bottom: 2em; border: 1px solid #eee; }}
</style>
</head>
<body>
<a href="https://godlockin.github.io/kallax-experts/experts/" class="back">← 回到 kallax-experts 首页</a>

<h1>🎭 Experts 列表 / Browse</h1>
<p>共 <strong id="total-count">0</strong> 个 expert(本地 15 个,加上跨库引用 350+ 个)。</p>

<input type="search" class="search" id="search" placeholder="🔍 搜索关键词:API, 安全, LLM, 性能, RAG..." autofocus>

<div class="stats">
  <span>📦 <strong id="shown-count">0</strong> shown</span>
  <span>📁 <span id="division-filter-info">all divisions</span></span>
</div>

<div class="filters" id="filters"></div>

<div class="expert-list" id="expert-list"></div>

<div class="no-results" id="no-results" style="display:none;">
  <p>🤷 没找到匹配的 expert</p>
  <p>试试其他关键词,或 <a href="https://github.com/godlockin/kallax-experts">在 GitHub 上加一个</a></p>
</div>

<script>
const EXPERTS = {experts_json};

function render() {{
  const q = document.getElementById('search').value.toLowerCase().trim();
  const division = document.querySelector('.filter-btn.active')?.dataset.division || null;

  let filtered = EXPERTS;
  if (q) {{
    // 混合搜索:对每个 expert 计算 3 个 score 维度
    filtered = filtered.map(e => {{
      const blob = (e.name + ' ' + (e.name_en || '') + ' ' + (e.vibe || '') + ' ' + (e.triggers_zh || '') + ' ' + (e.triggers_en || '') + ' ' + e.role_id).toLowerCase();
      const useWhenZh = (e.use_when_zh || []).join(' ').toLowerCase();
      const useWhenEn = (e.use_when_en || []).join(' ').toLowerCase();

      // score 维度
      const triggerHit = blob.includes(q) ? 1 : 0;
      // use_when 双向子串:用户词 in expert 描述,或 expert 描述词 in 用户词
      let descHit = 0;
      let descReason = '';
      if (useWhenZh.includes(q) || useWhenEn.includes(q)) {{
        descHit = 1;
        descReason = q;
      }} else {{
        // 反向:use_when 里的短语出现在用户输入里
        const allPhrases = [...(e.use_when_zh || []), ...(e.use_when_en || [])];
        for (const phrase of allPhrases) {{
          if (phrase.length >= 2 && q.includes(phrase.toLowerCase())) {{
            descHit = 1;
            descReason = phrase;
            break;
          }}
        }}
        // 同义词/前缀(中文 2 字前缀)
        if (!descHit && q.length >= 2) {{
          for (const phrase of allPhrases) {{
            if (phrase.length >= 2 && phrase.toLowerCase().startsWith(q.slice(0, 2))) {{
              descHit = 0.5;
              descReason = phrase;
              break;
            }}
          }}
        }}
      }}

      const totalScore = triggerHit * 100 + descHit * 10;
      return {{ ...e, _score: totalScore, _trigger: triggerHit, _desc: descHit, _descReason: descReason }};
    }})
    .filter(e => e._score > 0)  // 必须有命中(trigger 或 desc)
    .sort((a, b) => {{
      if (b._score !== a._score) return b._score - a._score;
      const priorityOrder = {{'high': 0, 'medium': 1, 'low': 2}};
      const pa = priorityOrder[a.priority] ?? 3;
      const pb = priorityOrder[b.priority] ?? 3;
      if (pa !== pb) return pa - pb;
      return (a.name_en || '').localeCompare(b.name_en || '');
    }});
  }}
  if (division) {{
    filtered = filtered.filter(e => e.divisions.includes(division));
  }}

  // 无 query 时按 priority + 字母排序
  if (!q) {{
    const priorityOrder = {{'high': 0, 'medium': 1, 'low': 2}};
    filtered.sort((a, b) => {{
      const pa = priorityOrder[a.priority] ?? 3;
      const pb = priorityOrder[b.priority] ?? 3;
      if (pa !== pb) return pa - pb;
      return (a.name_en || '').localeCompare(b.name_en || '');
    }});
  }}

  const list = document.getElementById('expert-list');
  if (filtered.length === 0) {{
    list.innerHTML = '';
    document.getElementById('no-results').style.display = 'block';
  }} else {{
    document.getElementById('no-results').style.display = 'none';
    list.innerHTML = filtered.map(e => {{
      const matchBadge = q ? (
        e._trigger ? '<span class="badge badge-trigger">🎯 精确</span> ' :
        '<span class="badge badge-desc">💡 语义「' + escapeHtml(e._descReason || '') + '」</span> '
      ) : '';
      return `
      <div class="expert">
        <h3><a href="${{e.path}}">${{e.emoji}} ${{e.name}} <code style="font-size: 0.7em; color: #888;">${{e.role_id}}</code></a></h3>
        <div class="vibe">${{e.vibe || ''}}</div>
        <div class="meta">
          ${{matchBadge}}
          <span class="badge badge-source">📦 ${{e.source || 'custom'}}</span>
          <span class="badge badge-priority">${{e.priority || 'medium'}}</span>
          📁 ${{(e.divisions || []).join(', ') || 'n/a'}}
          · 🔑 ${{(e.triggers_zh || '').slice(0, 60)}}${{(e.triggers_zh || '').length > 60 ? '...' : ''}}
        </div>
      </div>
    `}}).join('');
  }}
  document.getElementById('shown-count').textContent = filtered.length;
}}

function escapeHtml(s) {{
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}}

function renderFilters() {{
  const divisions = new Set();
  EXPERTS.forEach(e => (e.divisions || []).forEach(d => divisions.add(d)));
  const filtersEl = document.getElementById('filters');
  filtersEl.innerHTML = `<button class="filter-btn active" data-division="">all (${{EXPERTS.length}})</button>` +
    Array.from(divisions).sort().map(d => {{
      const count = EXPERTS.filter(e => (e.divisions || []).includes(d)).length;
      return `<button class="filter-btn" data-division="${{d}}">${{d}} (${{count}})</button>`;
    }}).join('');
  filtersEl.querySelectorAll('.filter-btn').forEach(btn => {{
    btn.addEventListener('click', () => {{
      filtersEl.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      render();
    }});
  }});
}}

document.getElementById('search').addEventListener('input', render);
document.getElementById('total-count').textContent = EXPERTS.length;
renderFilters();
render();
</script>
</body>
</html>"""


def main():
    if not EXPERT_DIR.exists():
        print(f"❌ {EXPERT_DIR} not found")
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    experts = []
    converted = 0

    for md_file in sorted(EXPERT_DIR.glob("**/*.md")):
        rel = md_file.relative_to(EXPERT_DIR)
        category = rel.parts[0] if len(rel.parts) > 1 else "other"
        name = md_file.stem

        md_text = md_file.read_text(encoding="utf-8")
        fm_raw, body = extract_frontmatter(md_text)
        fm = parse_fm(fm_raw)

        # 提字段
        name_val = fm.get("name", name)
        name_en = fm.get("name_en", "")
        role_id = fm.get("role_id", name)
        emoji = fm.get("emoji", "🤖")
        vibe = fm.get("vibe", "")
        source = fm.get("source", "custom")
        priority = fm.get("priority", "medium")

        # list 字段
        divisions = fm.get("divisions", [])
        if not isinstance(divisions, list):
            divisions = [divisions] if divisions else []
        domains = fm.get("domains", [])
        if not isinstance(domains, list):
            domains = [domains] if domains else []

        # triggers(可能是 dict)
        triggers = fm.get("triggers", {})
        if isinstance(triggers, dict):
            triggers_zh = " ".join(triggers.get("zh", []))
            triggers_en = " ".join(triggers.get("en", []))
        else:
            triggers_zh = str(triggers) if triggers else ""
            triggers_en = ""

        # use_when(用户场景描述,跟 triggers 区分:这是"用户症状"不是"角色关键词")
        use_when_zh_list = fm.get("use_when_zh", [])
        if not isinstance(use_when_zh_list, list):
            use_when_zh_list = [use_when_zh_list] if use_when_zh_list else []
        use_when_en_list = fm.get("use_when_en", [])
        if not isinstance(use_when_en_list, list):
            use_when_en_list = [use_when_en_list] if use_when_en_list else []

        # 渲染 body
        body_html = md_to_html(body)

        # frontmatter 块
        fm_items = [
            ("role_id", role_id),
            ("vibe", vibe),
            ("source", source),
            ("divisions", ", ".join(divisions) if divisions else "n/a"),
            ("domains", ", ".join(domains)),
            ("triggers_zh", triggers_zh[:200] + ("..." if len(triggers_zh) > 200 else "")),
            ("triggers_en", triggers_en[:200] + ("..." if len(triggers_en) > 200 else "")),
            ("priority", priority),
        ]
        if "source_path" in fm:
            fm_items.append(("source_path", fm["source_path"]))
        if "tokens" in fm:
            fm_items.append(("tokens", fm["tokens"]))
        if "updated" in fm:
            fm_items.append(("updated", fm["updated"]))

        fm_html = '<div class="frontmatter"><dl>' + "".join(
            f'<dt>{escape(k)}:</dt><dd>{escape(str(v))}</dd>' for k, v in fm_items
        ) + '</dl></div>'

        html = PAGE_TEMPLATE.format(
            title=escape(name_val),
            emoji=emoji,
            name=escape(name_val),
            role_id=escape(role_id),
            vibe=escape(vibe),
            fm_html=fm_html,
            body_html=body_html,
            md_relpath=str(rel)
        )

        out_html = OUT_DIR / rel
        out_html = out_html.with_suffix(".html")
        out_html.parent.mkdir(parents=True, exist_ok=True)
        out_html.write_text(html, encoding="utf-8")
        converted += 1

        # 加到 experts 列表
        experts.append({
            "name": name_val,
            "name_en": name_en,
            "role_id": role_id,
            "emoji": emoji,
            "vibe": vibe,
            "source": source,
            "priority": priority,
            "divisions": divisions,
            "domains": domains,
            "triggers_zh": triggers_zh,
            "triggers_en": triggers_en,
            "use_when_zh": use_when_zh_list,
            "use_when_en": use_when_en_list,
            "path": out_html.relative_to(OUT_DIR).as_posix(),
        })

        print(f"  {rel} → {out_html.relative_to(KALLAX_ROOT)}")

    # 列表页
    experts_json = json.dumps(experts, ensure_ascii=False, indent=2)
    list_html = LIST_TEMPLATE.format(experts_json=experts_json)
    list_file = OUT_DIR / "index.html"
    list_file.write_text(list_html, encoding="utf-8")

    # data.json
    data_file = OUT_DIR / "data.json"
    data_file.write_text(json.dumps(experts, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ 列表页: {list_file.relative_to(KALLAX_ROOT)}")
    print(f"✅ 数据:   {data_file.relative_to(KALLAX_ROOT)}")
    print(f"\n🎉 Converted {converted} expert .md → .html")


if __name__ == "__main__":
    main()