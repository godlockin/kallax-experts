#!/usr/bin/env python3
"""inject-use-when.py - 把 use_when_zh/en 字段批量注入 15 个 expert 的 frontmatter

读 tools/use-when-data.json → 找到对应 .md → 在 triggers 后面插入 use_when 块
已存在 use_when 则跳过(幂等)
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(".")
EXPERT_DIR = ROOT / "experts"
DATA_FILE = ROOT / "tools" / "use-when-data.json"


def inject(md_path: Path, use_when: dict) -> bool:
    """把 use_when 插入 frontmatter(triggers 之后),已存在则先删除再注入"""
    text = md_path.read_text(encoding="utf-8")
    if "use_when_zh:" in text or "use_when_en:" in text:
        # 删除已有 use_when 块
        lines = text.split("\n")
        out = []
        in_use_when = False
        for line in lines:
            if line.strip().startswith("use_when_zh:") or line.strip().startswith("use_when_en:"):
                in_use_when = True
                continue
            if in_use_when:
                if line.startswith("  - ") or line.startswith("    - ") or line == "":
                    if line == "":
                        in_use_when = False
                        continue
                    continue
                else:
                    in_use_when = False
            out.append(line)
        text = "\n".join(out)
        print(f"  🔄 {md_path.relative_to(ROOT)} (删除已有 use_when)")

    # 检查 frontmatter 存在
    if not text.startswith("---\n"):
        print(f"  ❌ {md_path.name} 无 frontmatter")
        return False

    # 解析 frontmatter
    parts = text.split("---", 2)
    if len(parts) < 3:
        print(f"  ❌ {md_path.name} frontmatter 不完整")
        return False
    fm = parts[1]
    body = parts[2]

    # 构造 use_when 块(用多行 list 格式,统一)
    use_when_lines = ["use_when_zh:"]
    for item in use_when["use_when_zh"]:
        use_when_lines.append(f"  - {item}")
    use_when_lines.append("use_when_en:")
    for item in use_when["use_when_en"]:
        use_when_lines.append(f"  - {item}")
    use_when_block = "\n".join(use_when_lines)

    lines = fm.split("\n")
    out = []
    inserted = False

    # 找到整个 triggers 块(包括嵌套的 zh/en 子项)的结束位置
    # 然后在 triggers 块**之后**插 use_when
    triggers_idx = -1
    for i, line in enumerate(lines):
        if re.match(r'^triggers:\s*', line) and not line.startswith(" "):
            triggers_idx = i
            break

    if triggers_idx < 0:
        # 没找到 triggers,放在 frontmatter 末尾
        insert_idx = len(lines) - 1
    else:
        # 找 triggers 块的结束(下一个顶层 key)
        insert_idx = triggers_idx + 1
        for i in range(triggers_idx + 1, len(lines)):
            line = lines[i]
            # 顶层 key:无缩进的 `key: value` 格式
            if re.match(r'^[a-zA-Z_]\w*:\s*', line) and not line.startswith(" "):
                insert_idx = i
                break
            insert_idx = i + 1  # 默认下一个空行/项

    # 在 insert_idx 处插入 use_when 块
    out = lines[:insert_idx] + [""] + use_when_block.split("\n") + [""] + lines[insert_idx:]
    new_fm = "\n".join(out)
    new_text = f"---\n{new_fm}---{body}"
    md_path.write_text(new_text, encoding="utf-8")
    print(f"  ✅ {md_path.relative_to(ROOT)} (注入 use_when)")
    return True


def main():
    if not DATA_FILE.exists():
        print(f"❌ {DATA_FILE} not found")
        sys.exit(1)

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    injected = 0
    skipped = 0
    for rel_path, use_when in data.items():
        md_path = EXPERT_DIR / rel_path
        if not md_path.exists():
            print(f"  ❌ {md_path} not found")
            continue
        if inject(md_path, use_when):
            injected += 1
        else:
            skipped += 1

    print(f"\n🎉 注入 {injected} 个 expert,跳过 {skipped} 个")


if __name__ == "__main__":
    main()