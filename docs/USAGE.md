# USAGE / 引用策略

> **关键**:**大模型不需要现场下载**
> 专家 prompt 是静态 .md,**已部署本地**,通过 Read 工具读取(0 网络请求)

## 📦 一次性安装(非大模型操作)

用户在终端跑一次:

```bash
# 装 3 个专家库(约 30MB,~10 秒)
git clone --depth 1 https://github.com/godlockin/kallax-experts.git \
  ~/.claude/experts-extended/kallax-experts

git clone --depth 1 https://github.com/godlockin/eket-experts-extended.git \
  ~/.claude/experts-extended/eket

git clone --depth 1 https://github.com/msitarzewski/agency-agents.git \
  ~/.claude/experts-extended/agency-agents

# 或用 kallax 封装
bash /path/to/kallax/scripts/expert-install.sh kallax-experts
bash /path/to/kallax/scripts/expert-install.sh eket
bash /path/to/kallax/scripts/expert-install.sh agency-agents
```

> **一次性**,约 30MB,~10 秒。后续大模型调用 0 网络。

---

## 🤖 大模型如何用

### 方式 1:直接 Read 专家文件

```bash
# 大模型看到 user 问 "API 安全"
# 自动:
Read ~/.claude/experts-extended/kallax-experts/experts/tech/security/security-engineer.md
# 或
Read ~/.claude/experts-extended/kallax-experts/experts/tech/backend/backend-architect.md
# 或
Read ~/.claude/experts-extended/eket/experts/tech/security.md  # eket 原文
```

### 方式 2:用 search.sh 找(避免大模型靠猜)

```bash
# 用户: "我想审查 API 安全"
# 大模型:
bash ~/.claude/experts-extended/kallax-experts/tools/search.sh "API 安全"
# 输出: 命中 4 个候选(本地 + 跨库)
# 然后大模型:
Read <file>
```

### 方式 3:用 compose.sh 多专家合成(2024 新)

```bash
# 用户: "从安全 + 性能 + 架构 三角度审查 API"
# 大模型:
bash ~/.claude/experts-extended/kallax-experts/tools/compose.sh "API" security,performance,architecture
# 输出: 多专家综合 prompt(可直接 Read)
```

---

## 🔗 引用机制详解

### 4 种引用方式

| 方式 | 大模型动作 | 网络 | 速度 | 适用 |
|------|----------|------|------|------|
| **1. 直接 Read** | Read <path> | 0 | 极快 | 单个专家 |
| **2. search 找** | Bash + Read | 0 | 快 | 不知道哪个专家 |
| **3. compose 合成** | Bash + Read | 0 | 中 | 多角度问题 |
| **4. install 装** | 用户(终端) | 是(首次) | 慢(10s) | 一次性 |

### 触发器(关键词 → 专家)

大模型**不靠记住文件路径**,而是:
1. 看用户问什么(关键词)
2. 跑 `search.sh <keyword>` 找候选
3. Read 对应 .md
4. 应用该 expert 的 prompt

示例流程:
```
用户: "我的 PostgreSQL 慢查询怎么优化?"
  ↓
大模型: 提取关键词 "PostgreSQL 慢查询"
  ↓
Bash: tools/search.sh "PostgreSQL"
  ↓
  命中: database-optimizer / performance-engineer / eket:tech/dba
  ↓
Read: ~/.claude/experts-extended/kallax-experts/experts/tech/performance/performance-engineer.md
  ↓
应用 prompt: "你是性能工程师,关注点 1. 2. 3. ... 工作流 ..."
  ↓
输出: 专业分析 + 优化建议
```

---

## 📊 性能对比(无现场下载)

| 方式 | 网络请求 | 延迟 | Token 成本 |
|------|---------|------|----------|
| **Read 本地** | 0 | <10ms | 700-1000 tokens |
| **curl 远程 URL** | 1+ | 100-1000ms | 700-1000 + 200 流量 |
| **WebFetch 抓网页** | 1 | 200-2000ms | 2000+ tokens(网页噪声) |

**结论**:**本地 Read 远胜于任何远程方式**(快 100x + 准 + 省钱)。

---

## 🎯 何时更新专家?

专家是**静态 .md**,极少更新:
- 当行业有重大变化(法规 / 新技术)
- 当触发器需要扩展
- 当发现错误或遗漏

**更新流程**:
```bash
# 1. 用户(终端)更新本地
cd ~/.claude/experts-extended/kallax-experts
git pull

# 2. 验证
bash tools/validate.sh

# 3. 大模型下次 Read 时自动拿到新版本
```

---

## 🛡️ 安全考虑

| 风险 | 缓解 |
|------|------|
| 仓库被恶意修改 | GitHub PR review + signed commits |
| 本地文件被篡改 | validate.sh + sha 校验 |
| 包含真实 PII | 全部占位符(无真实人/公司) |
| 仓库被下架 | 多源备份(eket / agency) |

---

## 📋 总结

| 问题 | 答案 |
|------|------|
| 大模型需要现场下载? | **不需要** |
| 怎么引用? | `Read <本地路径>` |
| 文件在哪? | `~/.claude/experts-extended/kallax-experts/` |
| 装一次,能用多久? | 永久(直到新版本 git pull) |
| 更新? | 1) git pull 2) validate.sh 3) 重新 Read |
| 多专家? | compose.sh(2024 新功能) |

**核心**:**离线 + 本地 + 快速 + 静态**。

---

**Maintained by**:kallax framework
**Version**: 1.0