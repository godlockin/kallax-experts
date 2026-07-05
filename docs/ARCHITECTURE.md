# ARCHITECTURE / 融合架构

> **kallax-experts** = eket-experts-extended ∪ agency-agents ∪ kallax-extension
> **目标**:对外独立、可组合、可自动选的专家组项目

## 🎯 融合理念

| 来源 | 强项 | 我们如何继承 |
|------|------|------------|
| [eket-experts-extended](https://github.com/godlockin/eket-experts-extended) | YAML 倒排索引 + CLI 搜索 + 触发器 | **继承 INDEX.yml 倒排索引** + **CLI 工具(search.sh/arena.sh)** |
| [agency-agents](https://github.com/msitarzewski/agency-agents) | frontmatter metadata + 17 division 分类 | **继承 frontmatter schema** + **division 标准化** |
| [kallax](https://github.com/godlockin/kallax) | default 5 + 统一触发(slash command) | **本地 5 个示例** + **跨库引用触发** |

**关键设计决策**:
1. **不复制专家内容** — eket/agency 各自维护,kallax-experts 只维护**统一索引 + frontmatter 标准 + 跨库引用**
2. **frontmatter 标准化** — 所有 expert 必须符合 schema(tools/validate.sh 验证)
3. **YAML 倒排索引** — 关键词 → 专家(中英文双支持)
4. **跨库引用** — 触发关键词可同时命中 builtin + eket + agency
5. **CLI 工具** — search.sh / arena.sh(沿用 eket 风格)

---

## 🏗️ 4 层架构

```
┌─────────────────────────────────────────────────┐
│  Layer 4: Triggers(slash command 集成)           │
│  /kallax init/research/ask                       │
│  → 大模型自动选专家(用 INDEX.yml)               │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  Layer 3: 索引(YAML 倒排)                        │
│  INDEX.yml(500 tokens)                            │
│  - triggers: 关键词 → 专家                      │
│  - external: 跨库引用                          │
│  - divisions: 标准化分类                        │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  Layer 2: 外部库(不复制)                          │
│  ~/.claude/experts-extended/                     │
│  ├── eket/             (70 个,git clone)         │
│  ├── agency-agents/    (280 个,git clone)        │
│  └── (其他自定义)                                   │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  Layer 1: 本地专家(5 个示例)                      │
│  experts/                                       │
│  ├── tech/backend/backend-architect.md         │
│  ├── tech/devops/sre-engineer.md               │
│  ├── ai/aiml/llm-engineer.md                    │
│  ├── business/legal-advisor.md                  │
│  └── design/product-manager.md                  │
└─────────────────────────────────────────────────┘
```

---

## 📋 文件清单

```
kallax-experts/
├── README.md              (项目说明)
├── LICENSE                (MIT)
├── INDEX.yml              (机器可读倒排索引,~500 tokens)
├── INDEX.md               (人类可读索引)
├── experts/               (5 个示例)
│   ├── tech/
│   │   ├── backend/backend-architect.md
│   │   └── devops/sre-engineer.md
│   ├── ai/aiml/llm-engineer.md
│   ├── design/product-manager.md
│   └── business/legal-advisor.md
├── schema/
│   └── frontmatter.yml    (frontmatter 标准)
├── tools/
│   ├── search.sh          (关键词搜索)
│   ├── arena.sh           (竞技场)
│   └── validate.sh        (frontmatter 验证)
├── docs/
│   ├── ARCHITECTURE.md    (本文件)
│   └── CONTRIBUTING.md
└── .github/workflows/
    └── validate.yml       (CI)
```

---

## 🔍 工作流示例

### 用户:"帮我审查 API 安全"

```bash
# 1. 搜索关键词
bash tools/search.sh "API"
# 命中:
#   - local: backend-architect(本地详细)
#   - eket: tech/security
#   - agency-agents: engineering/backend-architect

# 2. 竞技场对比
bash tools/arena.sh "API"
# Top 3 候选 + 匹配度评分

# 3. Claude Code 加载
Read experts/tech/backend/backend-architect.md  # 本地详细
Read ~/.claude/experts-extended/eket/experts/tech/security.md  # 外部详细
```

### 用户:"/kallax 启动一个 React 项目"

```bash
# 1. 大模型读 INDEX.yml(500 tokens)
Read INDEX.yml

# 2. 命中 frontend-engineer(从 agency) + UX 研究员
# 3. Read 详细 prompt
Read ~/.claude/experts-extended/agency-agents/engineering/frontend-engineer.md
```

---

## ⚖️ vs 单独使用 eket/agency

| 维度 | eket-only | agency-only | **kallax-experts** |
|------|----------|------------|---------------------|
| 专家数量 | 70 | 280 | **350**(去重) |
| 索引 | YAML 倒排 | divisions.json | **YAML 倒排 + 跨库引用** |
| CLI 工具 | 有 | 无 | **有(从 eket 学)** |
| frontmatter | 部分 | 完整 | **标准化 + 验证** |
| 跨库 | 否 | 否 | **是** |
| Token 优化 | 索引 1200 tokens | 无索引 | **索引 500 tokens** |

---

## 🚀 路线图

- [ ] 完整倒排索引(从 eket + agency 提取所有 triggers)
- [ ] expert-compose:多专家合成(多视角分析)
- [ ] GitHub Pages(可搜索目录)
- [ ] vscode 扩展(可选)
- [ ] 行业垂直专家(医疗 / 法律 / 金融 等)

---

**Maintained by**:kallax framework
**Last updated**:2026-07-05
**License**:MIT