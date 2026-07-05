#!/usr/bin/env bash
# validate.sh - 验证所有 expert .md 符合 frontmatter schema
# 跑: bash tools/validate.sh

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KALLAX_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
EXPERT_DIR="$KALLAX_ROOT/experts"
SCHEMA_FILE="$KALLAX_ROOT/schema/frontmatter.yml"

PASS=0
FAIL=0
TOTAL=0

# 颜色
if [[ -t 1 ]]; then
  GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
else
  GREEN=''; RED=''; NC=''
fi

ok() { echo -e "  ${GREEN}✓${NC} $1"; PASS=$((PASS+1)); }
fail() { echo -e "  ${RED}✗${NC} $1"; FAIL=$((FAIL+1)); }

# 必填字段
required_fields=("name" "role_id" "emoji" "divisions" "triggers")

# 遍历所有 expert .md
while IFS= read -r -d '' f; do
  TOTAL=$((TOTAL+1))
  filename=$(basename "$f")

  # 检查 frontmatter
  if ! head -1 "$f" | grep -q "^---$"; then
    fail "$filename: 缺 frontmatter (---)"
    continue
  fi

  # 提取 frontmatter 段
  fm=$(awk '/^---$/{c++; if(c==2) exit; next} c==1' "$f")

  # 必填字段
  missing=()
  for field in "${required_fields[@]}"; do
    if ! echo "$fm" | grep -qE "^${field}:"; then
      missing+=("$field")
    fi
  done

  if [[ ${#missing[@]} -gt 0 ]]; then
    fail "$filename: 缺必填字段 (${missing[*]})"
  else
    ok "$filename"
  fi
done < <(find "$EXPERT_DIR" -name "*.md" -type f -print0)

echo ""
echo "📊 验证结果"
echo "  Total: $TOTAL"
echo "  Pass:  $PASS"
echo "  Fail:  $FAIL"

if [[ $FAIL -eq 0 ]]; then
  echo ""
  echo "✅ 全部通过"
  exit 0
else
  echo ""
  echo "❌ $FAIL 项失败"
  exit 1
fi