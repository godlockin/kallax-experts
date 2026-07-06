#!/usr/bin/env bash
# compose.sh - 多专家合成(2024 新功能)
#
# 用法:
#   bash tools/compose.sh <keyword> <expert-ids>
#   bash tools/compose.sh "API" security-engineer,performance-engineer
#   bash tools/compose.sh "数据迁移" data-engineer,backend-architect,security
#
# 输出:合成 prompt(写到 /tmp/,可被大模型直接 Read)
#
# 设计:
# - 1 个 keyword + N 个 expert id
# - 自动从每个 expert 提取关键段(关注点/工作流/不要做)
# - 合成 1 个 markdown prompt
# - 大模型 Read 即可(无需下载)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KALLAX_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
INDEX_FILE="$KALLAX_ROOT/INDEX.yml"

# 兼容
if [[ ! -f "$INDEX_FILE" && -f "$KALLAX_ROOT/experts/index/experts-index.yml" ]]; then
  INDEX_FILE="$KALLAX_ROOT/experts/index/experts-index.yml"
fi

# 颜色
if [[ -t 1 ]]; then
  RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'
  CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
else
  RED=''; GREEN=''; YELLOW=''; CYAN=''; BOLD=''; NC=''
fi

if [[ $# -lt 2 ]]; then
  cat <<'EOF'
compose.sh - 多专家合成

用法:
  bash tools/compose.sh <keyword> <expert-ids>
  bash tools/compose.sh "API" security,performance,backend-architect
  bash tools/compose.sh "数据迁移" data-engineer,backend-architect,security

输出:
  - 合成 prompt(写到 /tmp/,可被大模型 Read)
  - 包含每个 expert 的核心关注点
  - 提供"综合视角"模板
EOF
  exit 2
fi

KEYWORD="$1"
shift
EXPERT_IDS=$(echo "$1" | tr ',' ' ')

echo ""
echo -e "${BOLD}🎼 Multi-Expert Composition / 多专家合成${NC}"
echo "关键词: ${CYAN}$KEYWORD${NC}"
echo "专家组合: ${CYAN}$EXPERT_IDS${NC}"
echo ""

# 临时输出文件(固定名字,用户跑完手动 rm 或下次覆盖)
OUT="/tmp/avle-compose-current.md"
: > "$OUT"

# 写头
cat > "$OUT" <<'EOF'
# 🎼 Multi-Expert Composition Prompt / 多专家合成 Prompt

> **用户任务**: 关键词 + 多个专家视角
> **使用方式**: 大模型直接 Read 此文件,按各专家的关注点综合分析

EOF

echo "## 📋 任务上下文" >> "$OUT"
echo "" >> "$OUT"
echo "- 关键词: $KEYWORD" >> "$OUT"
echo "- 涉及专家: $EXPERT_IDS" >> "$OUT"
echo "" >> "$OUT"

# 加载每个 expert
for eid in $EXPERT_IDS; do
  eid=$(echo "$eid" | tr -d ' ')

  # 找 file path(从 INDEX.yml 查)
  inline=$(grep -E "id: $eid,?[[:space:]]+" "$INDEX_FILE" 2>/dev/null | head -1)
  if [[ -z "$inline" ]]; then
    echo -e "${YELLOW}⚠️  builtin 无 '$eid'${NC}"
    continue
  fi

  # 提字段(file/name/emoji 都可能有/无引号)
  # 用 awk 切逗号,简单可靠
  extract_field() {
    local field="$1"
    local pattern="$field:"
    echo "$inline" | awk -F'[,}]' -v p="$pattern" '{
      for(i=1;i<=NF;i++) {
        if(index($i, p) > 0) {
          sub(".*"p"[[:space:]]*", "", $i)
          sub("[[:space:]]*$", "", $i)
          gsub(/^["'"'"'[:space:]]+|["'"'"'[:space:]]+$/, "", $i)
          print $i
        }
      }
    }' | head -1
  }
  file=$(extract_field "file")
  name=$(extract_field "name")
  emoji=$(extract_field "emoji")

  # 找本地文件
  full_path="$KALLAX_ROOT/$file"
  if [[ ! -f "$full_path" ]]; then
    echo -e "${RED}✗ '$eid' 文件不存在: $file${NC}"
    continue
  fi

  echo -e "${GREEN}✓ 加载: ${emoji} $name${NC} ($eid)"

  # 提取关键段
  echo "## 🎭 视角: $emoji $name ($eid)" >> "$OUT"
  echo "" >> "$OUT"

  # 关注点
  echo "**关注点**:" >> "$OUT"
  if awk '/^## 🎯 关注点/{flag=1; next} /^## /{flag=0} flag' "$full_path" | grep -v '^$' | head -15 | sed 's/^/- /' >> "$OUT"; then
    :
  else
    echo "- (无关注点段)" >> "$OUT"
  fi
  echo "" >> "$OUT"

  # 工作流
  echo "**工作流**:" >> "$OUT"
  if awk '/^## 📋 工作流/{flag=1; next} /^## /{flag=0} flag' "$full_path" | grep -v '^$' | head -10 | sed 's/^/- /' >> "$OUT"; then
    :
  else
    echo "- (无工作流段)" >> "$OUT"
  fi
  echo "" >> "$OUT"

  # 不要做
  echo "**不要做**:" >> "$OUT"
  if awk '/^## ⚠️ 不要做/{flag=1; next} /^## /{flag=0} flag' "$full_path" | grep -v '^$' | head -10 | sed 's/^/- /' >> "$OUT"; then
    :
  else
    echo "- (无不要做段)" >> "$OUT"
  fi
  echo "" >> "$OUT"
  echo "---" >> "$OUT"
  echo "" >> "$OUT"
done

# 综合模板
cat >> "$OUT" <<'EOF'
## 🎯 综合分析模板

> **作为上述所有专家,你需要从各自视角综合分析任务。**

### 1. 多视角分析(每个专家)

- **🎭 视角 A**:
  - 关注点 1: ...
  - 关注点 2: ...
  - 风险: ...

- **🎭 视角 B**:
  - ...

### 2. 共同发现
- (多个专家都提到的问题)

### 3. 冲突 / 权衡
- (专家观点冲突时如何取舍)

### 4. 综合建议
- (按优先级排列的可执行建议)

### 5. 下一步
- (立即可做的 + 长期规划)

---

> **重要**:每个专家都有其关注盲点。多视角合成的价值是**互补**,不是**叠加**。
> 最终建议应平衡各方,而不是简单求和。
EOF

echo ""
echo -e "${BOLD}📄 合成 prompt 已写入: $OUT${NC}"
echo ""
echo -e "${CYAN}下一步:${NC}"
echo "  Read $OUT  # 加载合成 prompt"
echo "  按格式输出综合分析"