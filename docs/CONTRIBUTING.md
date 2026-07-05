# CONTRIBUTING / 贡献指南

> 欢迎贡献 kallax-experts!这里说明怎么加新专家、修复问题、贡献新功能。

## 🚀 快速开始

### 1. Fork 仓库

```bash
# GitHub 上 fork
# git clone 你的 fork
git clone https://github.com/<your-name>/kallax-experts.git
cd kallax-experts
```

### 2. 加新专家(本地)

```bash
# 1. 在正确目录创建 .md
mkdir -p experts/tech/your-domain
cat > experts/tech/your-domain/your-expert.md <<'EOF'
---
name: 你的专家名
name_en: Your Expert
role_id: your-expert
emoji: 🤖
vibe: 一句话定位
source: custom  # 或 agency-agents / eket
source_id: path/in/source
divisions: [engineering]  # 至少 1 个
domains: [tech, your-domain]
triggers:
  zh: [关键词1, 关键词2]
  en: [keyword1, keyword2]
tools: [Read, Grep]
related: [other-expert]
priority: medium
tokens: ~500
updated: 2026-07-05
---

# 你的专家

## 🎯 关注点
...

## 🛠️ 工具
...

## 📋 工作流
...
EOF
```

### 3. 验证

```bash
bash tools/validate.sh
# 必须 ✅ 全部通过
```

### 4. 提交

```bash
git add experts/tech/your-domain/your-expert.md
git commit -m "feat: add your-expert (tech/your-domain)"
git push origin main
# 在 GitHub 开 PR
```

## ✅ 必填字段

每个 expert `.md` 必须包含:

```yaml
name:           # 中文名
name_en:        # 英文名(推荐)
role_id:        # 唯一 ID,小写连字符
emoji:          # 视觉标识
vibe:           # 一句话定位(<= 30 字)
source:         # 来源(agency-agents / eket / custom / fusion)
divisions:      # 至少 1 个,从 17 个 agency 兼容 list
domains:        # 详细领域
triggers:       # 至少 1 个语言(zh 或 en)
tools:          # 常用工具列表
related:        # 相关专家
priority:       # high/medium/low
tokens:         # 估计 token 量
updated:        # YYYY-MM-DD
```

详见 [schema/frontmatter.yml](schema/frontmatter.yml)。

## ❌ 不接受的

- ❌ 没有 frontmatter
- ❌ 缺必填字段
- ❌ 引用真实个人/公司信息
- ❌ 复制 eket/agency 内容(请用 `source: eket`/`agency` 引用)
- ❌ 建议违反法律的操作
- ❌ 给出具体法律建议(只能给风险提示)

## 🧪 CI

PR 触发 `.github/workflows/validate.yml`:
- 自动跑 `tools/validate.sh`
- 任何 frontmatter 不符合 → CI 失败
- 必须通过才合并

## 📋 Commit 规范

```bash
feat: add new expert (category/name)
fix: fix schema for existing expert
docs: update INDEX.md
chore: misc
```

## 🔍 验证命令

```bash
# 验证所有 expert
bash tools/validate.sh

# 搜索关键词
bash tools/search.sh "API"

# 竞技场
bash tools/arena.sh "API"
```

## 📚 资源

- [README.md](README.md)
- [ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [frontmatter schema](schema/frontmatter.yml)
- [eket-experts-extended](https://github.com/godlockin/eket-experts-extended)
- [agency-agents](https://github.com/msitarzewski/agency-agents)

---

**License**: MIT
**Version**: 1.0.0