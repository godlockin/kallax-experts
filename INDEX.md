# INDEX / 人类可读索引

> 机器可读版:[INDEX.yml](INDEX.yml)(~500 tokens)
> 本文件用于人眼浏览,会膨胀到 ~2000+ tokens

## 📊 总览

| 类别 | 数量 | 来源 | 路径 |
|------|------|------|------|
| **本地示例** | 5 | 原创 | [experts/](experts/) |
| **eket 引用** | 70 | 跨库 | `~/.claude/experts-extended/eket/` |
| **agency 引用** | 280 | 跨库 | `~/.claude/experts-extended/agency-agents/` |
| **合计** | **355** | 跨库去重 |  |

## 🏠 本地 5 个示例

| 角色 | emoji | 关注点 | 路径 |
|------|-------|--------|------|
| 后端架构师 | 🏗️ | 架构 / API / 数据库 | [experts/tech/backend/backend-architect.md](experts/tech/backend/backend-architect.md) |
| SRE 工程师 | 🛡️ | 可靠性 / 监控 / 故障响应 | [experts/tech/devops/sre-engineer.md](experts/tech/devops/sre-engineer.md) |
| LLM 工程师 | 🤖 | LLM / RAG / Prompt | [experts/ai/aiml/llm-engineer.md](experts/ai/aiml/llm-engineer.md) |
| 产品经理 | 🎯 | 用户 / 需求 / 增长 | [experts/design/product-manager.md](experts/design/product-manager.md) |
| 法律顾问 | ⚖️ | 合规 / 合同 / 风险 | [experts/business/legal-advisor.md](experts/business/legal-advisor.md) |

## 🔗 外部引用

### eket(70 个,git clone 装)

```bash
git clone --depth 1 https://github.com/godlockin/eket-experts-extended.git \
  ~/.claude/experts-extended/eket
```

| Domain | 数量 | 路径 |
|--------|------|------|
| tech(工程技术) | 8 | `eket/experts/tech/` |
| ai(AI/ML) | 8 | `eket/experts/ai/` |
| design(设计) | 5 | `eket/experts/design/` |
| marketing(营销) | 5 | `eket/experts/marketing/` |
| pr(公关) | 4 | `eket/experts/pr/` |
| business(商业) | 22 | `eket/experts/business/` |
| consulting(咨询) | 3 | `eket/experts/consulting/` |
| hr(HR) | 5 | `eket/experts/hr/` |
| training(培训) | 3 | `eket/experts/training/` |
| knowledge(知识) | 3 | `eket/experts/knowledge/` |
| ops(运营) | 4 | `eket/experts/ops/` |

### agency-agents(280 个,git clone 装)

```bash
git clone --depth 1 https://github.com/msitarzewski/agency-agents.git \
  ~/.claude/experts-extended/agency-agents
```

| Division | 数量 |
|----------|------|
| engineering | 34 |
| marketing | ~20 |
| design | ~15 |
| product | ~10 |
| security | ~10 |
| testing | ~10 |
| sales | ~10 |
| ...(17 total) | ~280 |

## 🛠️ 工具

| 命令 | 用途 |
|------|------|
| `bash tools/search.sh <keyword>` | 关键词搜索 |
| `bash tools/arena.sh <keyword>` | 竞技场(多专家对比) |
| `bash tools/validate.sh` | 验证 frontmatter |

## 📋 完整触发器(关键词 → 专家)

> 机器可读版见 [INDEX.yml](INDEX.yml)

**架构 / 技术**:
- `架构` / `架构设计` → backend-architect + eket:tech/architect
- `后端` / `API` → backend-architect + agency-agents
- `数据库` / `DB` → eket:tech/dba + agency-agents
- `性能` / `性能优化` → sre-engineer + eket:tech/performance
- `SRE` / `可靠性` / `监控` → sre-engineer
- `K8s` / `容器` / `部署` → eket:tech/devops
- `前端` → agency-agents:engineering/frontend-engineer
- `移动` / `iOS` / `Android` → eket:tech/mobile

**AI/ML**:
- `LLM` / `RAG` / `向量库` → llm-engineer
- `机器学习` / `AI` → llm-engineer + agency-agents
- `prompt` → llm-engineer + agency-agents

**产品/UX/营销**:
- `产品` / `需求` → product-manager
- `UX` / `UI` → agency-agents:design
- `营销` / `增长` → agency-agents:marketing
- `SEO` / `内容` → agency-agents:marketing

**商业/法律/金融**:
- `法律` / `合同` / `合规` → legal-advisor
- `金融` / `财务` → agency-agents:finance

---

**Version**: 1.0.0
**Last updated**: 2026-07-05