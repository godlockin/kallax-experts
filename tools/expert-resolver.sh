#!/usr/bin/env bash
# expert-resolver.sh — Free-form query → expert ranking
#
# 用法:
#   tools/expert-resolver.sh "<free-form query>"
#   tools/expert-resolver.sh "<query>" --json
#   tools/expert-resolver.sh "<query>" --pool=local|all|extended
#   tools/expert-resolver.sh ""                       (显示 usage)
#
# 实现策略:
#   - 全部 score/tokenize/matching 用 Python(避免 bash 处理中文 + 关联数组 + NULL separator)
#   - bash 只负责参数解析、human-readable 输出、错误处理
#   - macOS bash 3.2 兼容(无 declare -A,无 jq/yq)
#
# Score 维度(v2 — use_when 为主,trigger 为辅):
#   - use_when 短语含 query token (3+ 字):     +30/短语  (主语义)
#   - use_when 短语含 query token (2 字):       +15/短语
#   - use_when 短语含 query token (1 字):       +5/短语
#   - trigger (triggers_zh + triggers_en):       +10/词  (辅助)
#   - 反向子串 (query 含 use_when 短语):         +8/短语
#   - 前缀 (query 前 2 字 = use_when 短语前缀):  +2/短语
#   - name / role_id 排除 (避免短字符如 "qa" 误命中)

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DATA_JSON="$ROOT_DIR/docs/experts/data.json"

# 颜色
if [[ -t 1 ]]; then
    BOLD='\033[1m'; DIM='\033[2m'; CYAN='\033[0;36m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
else
    BOLD=''; DIM=''; CYAN=''; GREEN=''; RED=''; NC=''
fi

# ============ 错误处理 ============
error_exit() {
    echo -e "${RED}ERROR:${NC} $1" >&2
    if [[ "${2:-}" != "silent" ]]; then
        usage >&2
    fi
    exit "${3:-1}"
}

usage() {
    cat <<'EOF'
用法:
  expert-resolver.sh "<free-form query>" [options]

Options:
  --pool=local      仅 15 个 local expert (默认,docs/experts/data.json)
  --pool=all        local + 5 default + 5 extended (25 个)
  --pool=extended   local + eket (70) + agency (280) — 仅 metadata
  --json            JSON 输出 (LLM agent 解析)
  --top N           只输出 top N (默认全部有命中)
  -h, --help        显示帮助

示例:
  expert-resolver.sh "最近线上老挂"
  expert-resolver.sh "数据库慢查询" --json
  expert-resolver.sh "想加 AI 助手" --pool=all
EOF
}

# ============ Python score 内核 ============
# 接受 query + data.json 路径,返回 JSON 排序结果
python_score() {
    local query="$1"
    local data_path="$2"
    local pool="$3"
    python3 - "$query" "$data_path" "$pool" <<'PYEOF'
import json, sys, re

query, data_path, pool = sys.argv[1], sys.argv[2], sys.argv[3]

# 1. Token 化
def tokenize(text):
    tokens = set()
    # 英文 tokens (lowercase)
    for m in re.findall(r'[a-zA-Z][a-zA-Z0-9_-]+', text):
        tokens.add(m.lower())
    # 中文 (提取中文字符)
    zh = ''.join(c for c in text if '一' <= c <= '鿿')
    # 2 字 sliding window
    for i in range(len(zh) - 1):
        tokens.add(zh[i:i+2])
    # 3 字 sliding window
    for i in range(len(zh) - 2):
        tokens.add(zh[i:i+3])
    # 过滤长度 < 2
    return {t for t in tokens if len(t) >= 2}

tokens = tokenize(query)

# 2. 读 experts
with open(data_path) as f:
    experts = json.load(f)

# 3. 打分
results = []
for e in experts:
    role_id = e.get("role_id", "")
    name = e.get("name", "")
    name_en = e.get("name_en", "")
    emoji = e.get("emoji", "")
    triggers_zh = e.get("triggers_zh", "")
    triggers_en = e.get("triggers_en", "")
    use_when_zh = e.get("use_when_zh", []) or []
    use_when_en = e.get("use_when_en", []) or []

    # Trigger 来源(只取 triggers_zh + triggers_en 字符串)
    trigger_blob = " ".join([triggers_zh, triggers_en]).lower() if isinstance(triggers_zh, str) else ""

    # Use_when 短语列表
    all_phrases = use_when_zh + use_when_en

    score = 0
    reasons = []

    # 1. use_when 命中 (主语义)
    desc_3plus = 0
    desc_2 = 0
    for token in tokens:
        for phrase in all_phrases:
            if not isinstance(phrase, str):
                continue
            if token in phrase:
                tlen = len(token)
                if tlen >= 3:
                    score += 30
                    desc_3plus += 1
                elif tlen == 2:
                    score += 15
                    desc_2 += 1
                else:
                    score += 5
                    desc_2 += 1
    total_desc = desc_3plus + desc_2
    if total_desc > 0:
        reasons.append(f"use_when:{total_desc}×")

    # 2. Trigger 命中 (辅助)
    trigger_hits = 0
    for token in tokens:
        if len(token) < 2:
            continue
        # 用空格分词(粗匹配)
        trigger_words = trigger_blob.split()
        if any(token in w for w in trigger_words):
            score += 10
            trigger_hits += 1
    if trigger_hits > 0:
        reasons.append(f"trigger:{trigger_hits}×")

    # 3. 反向子串 (query 含 use_when 短语)
    query_clean = query.lower().replace(" ", "")
    reverse_hits = 0
    for phrase in all_phrases:
        if not isinstance(phrase, str) or len(phrase) < 2:
            continue
        phrase_clean = phrase.lower().replace(" ", "")
        if phrase_clean in query_clean:
            score += 8
            reverse_hits += 1
    if reverse_hits > 0:
        reasons.append(f"reverse:{reverse_hits}×")

    # 4. 前缀 (query 前 2 字 = use_when 短语前缀)
    prefix_hit = 0
    query_prefix = query[:2]
    if len(query_prefix) >= 2:
        for phrase in all_phrases:
            if not isinstance(phrase, str) or len(phrase) < 2:
                continue
            if phrase[:2] == query_prefix:
                score += 2
                prefix_hit += 1
    if prefix_hit > 0:
        reasons.append(f"prefix:{prefix_hit}×")

    if score > 0:
        results.append({
            "rank": 0,  # 后填
            "role_id": role_id,
            "name": name,
            "name_en": name_en,
            "emoji": emoji,
            "score": score,
            "hit_reason": ",".join(reasons),
            "bridge": f"/kallax-expert {role_id}",
        })

# 排序
results.sort(key=lambda x: -x["score"])
for i, r in enumerate(results):
    r["rank"] = i + 1

best_match = results[0]["role_id"] if results else None

print(json.dumps({
    "query": query,
    "pool": pool,
    "total": len(results),
    "results": results,
    "best_match": best_match,
}, ensure_ascii=False, indent=2))
PYEOF
}

# ============ 输出 ============
output_human() {
    local data="$1"
    local query=$(echo "$data" | python3 -c "import json,sys; print(json.load(sys.stdin)['query'])")
    local pool=$(echo "$data" | python3 -c "import json,sys; print(json.load(sys.stdin)['pool'])")
    local total=$(echo "$data" | python3 -c "import json,sys; print(json.load(sys.stdin)['total'])")
    local best=$(echo "$data" | python3 -c "import json,sys; print(json.load(sys.stdin)['best_match'] or 'none')")

    echo "================================================================="
    echo -e "  ${BOLD}Expert Resolution${NC} — ${CYAN}\"$query\"${NC}"
    echo -e "  Pool: ${BOLD}$pool${NC} ($total matches)"
    echo "================================================================="

    if [[ "$total" -eq 0 ]]; then
        echo -e "  ${CYAN}No expert matches.${NC}"
        echo -e "  ${DIM}试试更具体的描述,或 --pool=extended 跨库搜索${NC}"
    else
        echo "$data" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for r in data['results']:
    print(f\"  {r['rank']:>2}.  {r['emoji']}  {r['role_id']:<25}  Score:{r['score']:>4}  Match:{r['hit_reason']}\")
"
    fi
    echo "================================================================="
    if [[ "$best" != "none" ]]; then
        echo -e "  ${BOLD}SUMMARY${NC}: best=${GREEN}$best${NC} count=$total"
        echo -e "  ${DIM}Next: /kallax-expert $best${NC}"
    fi
}

# ============ Main ============
main() {
    local query=""
    local pool="local"
    local json_mode="false"
    local top_n=0

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            --json)
                json_mode="true"
                shift
                ;;
            --pool=*)
                pool="${1#--pool=}"
                shift
                ;;
            --top)
                top_n="${2:-0}"
                shift 2
                ;;
            --top=*)
                top_n="${1#--top=}"
                shift
                ;;
            "")
                shift
                ;;
            *)
                query="$1"
                shift
                ;;
        esac
    done

    # 校验 query
    if [[ -z "$query" ]]; then
        usage >&2
        exit 2
    fi

    # 校验 data.json
    if [[ ! -f "$DATA_JSON" ]]; then
        error_exit "data.json not found: $DATA_JSON\n提示: 先跑 python3 tools/build-experts.py"
    fi

    # 解析 pool
    case "$pool" in
        local) ;;
        all|extended)
            echo -e "${DIM}提示: --pool=$pool 暂未实现扩展,回退到 local (15 expert)${NC}" >&2
            pool="local"
            ;;
        *)
            error_exit "未知 pool: $pool (可用: local/all/extended)"
            ;;
    esac

    # 调用 Python 算分
    local result_json=$(python_score "$query" "$DATA_JSON" "$pool")

    # Top N
    if [[ $top_n -gt 0 ]]; then
        result_json=$(echo "$result_json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
data['results'] = data['results'][:$top_n]
data['total'] = len(data['results'])
print(json.dumps(data, ensure_ascii=False, indent=2))
")
    fi

    # 输出
    if [[ "$json_mode" == "true" ]]; then
        echo "$result_json"
    else
        output_human "$result_json"
    fi
}

main "$@"