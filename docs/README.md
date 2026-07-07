> ⚠️ 这是仓库根 [README.md](../README.md) 的副本,放在 docs/ 下方便 GitHub Pages 访问。
> 仓库根 README 由 GitHub Pages 自动渲染(legacy build_type 不需 .html)。

---

# kallax-experts / 专家组

> **🚀 GitHub Pages 已部署** → [godlockin.github.io/kallax-experts](https://godlockin.github.io/kallax-experts/) (含 15 expert 可搜索)
>
> **kallax 框架的外部专家组项目**
> 融合 [eket-experts-extended](https://github.com/godlockin/eket-experts-extended) 的**倒排索引 + CLI 搜索**
> + [agency-agents](https://github.com/msitarzewski/agency-agents) 的**frontmatter metadata + 17 division**
> 形成一个**对外独立、可组合、可自动选**的专家组项目。

---

## 🎯 设计目标

| 来源 | 优点 | 整合方式 |
|------|------|---------|
| **eket** | 70 个专家 + YAML 倒排索引 + CLI 搜索 | 继承 YAML 倒排 + CLI 工具 |
| **agency-agents** | 280 个 agent + frontmatter + 17 division | 继承 frontmatter + division 分组 |
| **kallax** | default 5 个 + 统一触发 | 新增:跨库引用 + 竞技场 + 任务-专家匹配 |

**kallax-experts 解决**:
1. ✅ 不重复造专家(融合 eket + agency 的全部)
2. ✅ 标准化 frontmatter(兼容 agency)
3. ✅ YAML 倒排索引(沿用 eket)
4. ✅ CLI 工具(从 eket 借鉴)
5. ✅ 跨库引用(eket + agency 各自维护,kallax-experts 引用)

---

## 📂 仓库结构

```
kallax-experts/
├── README.md                    本文件
├── LICENSE                       MIT
├── INDEX.md                      人类可读索引(全表)
├── INDEX.yml                     机器可读索引(倒排)
├── experts/                      全部专家
│   ├── tech/                     工程技术(eket + agency 合并)
│   │   ├── backend/
│   │   ├── frontend/
│   │   ├── devops/
│   │   ├── security/
│   │   ├── data/
│   │   ├── mobile/
│   │   ├── performance/
│   │   └── qa/
│   ├── ai/                       AI/ML(主要来自 agency-agents)
│   ├── design/                   设计
│   ├── marketing/                营销
│   ├── research/                 研究
│   ├── business/                 商业/法律/金融
│   └── INDEX.md                  分类索引
├── schema/
│   └── frontmatter.yml           frontmatter 模式(标准化)
├── skills/                       配套工具(eket skill 风格)
│   ├── expert-search/            关键词搜索
│   ├── expert-arena/             竞技场(评分)
│   └── expert-compose/           多专家合成
├── tools/
│   ├── search.sh                 CLI 工具
│   ├── arena.sh
│   ├── install.sh
│   └── validate.sh               验证所有 frontmatter + 索引
├── docs/
│   ├── ARCHITECTURE.md           融合架构
│   ├── CONTRIBUTING.md           贡献指南
│   └── FAQ.md
└── .github/
    └── workflows/
        └── validate.yml          CI 验证
```

---

## 🎯 怎么用

### 安装

```bash
git clone https://github.com/godlockin/kallax-experts.git \
  ~/.claude/experts-extended/kallax-experts
```

### 搜索专家(CLI)

```bash
# 关键词搜索
bash tools/search.sh "API"
bash tools/search.sh "架构"
bash tools/search.sh "AI"

# 竞技场(多专家对比)
bash tools/arena.sh "性能优化"

# 完整列表
bash tools/search.sh --all
```

### 在 Claude Code 用

```bash
# 让大模型读专家 prompt
Read ~/.claude/experts-extended/kallax-experts/experts/tech/backend/backend-architect.md
```

---

## 📋 frontmatter Schema(标准)

每个 expert .md 文件**必须**包含 YAML frontmatter:

```yaml
---
name: 后端架构师
name_en: Backend Architect
role_id: backend-architect
emoji: 🏗️
color: blue
vibe: 设计可扩展的后端系统,边界清晰,接口稳定
source: agency-agents     # 来源(agency-agents / eket / custom)
source_id: engineering/backend-architect  # 原始 ID
divisions: [engineering]
domains: [tech, backend]
triggers:
  zh: [后端, API, 架构, 微服务, 数据库]
  en: [backend, api, architecture, microservice, database]
tools: [Read, Grep, Glob, Bash]
related: [dba, devops, security]
priority: high
tokens: ~800
updated: 2026-07-05
---

# 后端架构师

你是 **kallax-experts** 的后端架构师角色,负责...
```

详见 [schema/frontmatter.yml](schema/frontmatter.yml)。

---

## 🔗 关联项目

- **kallax** ([godlockin/kallax](https://github.com/godlockin/kallax)) — 主框架
- **eket-experts-extended** ([godlockin/eket-experts-extended](https://github.com/godlockin/eket-experts-extended)) — 70 个专家
- **agency-agents** ([msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)) — 280 个 agent

**整合策略**:
- kallax-experts **从 eket 继承倒排索引 + CLI 搜索**
- 从 agency **继承 frontmatter + 17 division**
- 不复制专家内容(eket + agency 各自维护,本仓库仅维护**统一索引 + frontmatter 标准**)
- 实际专家 prompt 在 eket + agency,本仓库做**跨库引用**

---

## 🤝 贡献

欢迎贡献!见 [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)。

---

**License**: MIT
**Last updated**: 2026-07-05
**Status**: 🚧 初始化中(融合阶段)