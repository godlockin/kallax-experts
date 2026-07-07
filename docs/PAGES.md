# GitHub Pages 配置 / Pages Setup

> **当前状态**:`status: built` ✅,可访问 `https://godlockin.github.io/kallax-experts/`
>
> **关键配置**:`build_type: legacy` + `branch: miao` + `path: /docs`

## 📋 当前配置

| 字段 | 值 |
|------|-----|
| Source branch | `miao` |
| Source path | `/docs` |
| Build type | `legacy` (auto via `pages-build-deployment` workflow) |
| Custom domain | (none, default `*.github.io`) |
| HTTPS | ✅ Enforced |

## 🏗️ 目录结构 vs 访问路径

> **关键**:`path: /docs` 时,**`docs/` 内的文件映射到站点根**。

```
仓库(branch miao)                    →  部署 URL
─────────────────────────────────────────────────
index.html                          →  /
docs/README.html                    →  README.html
docs/USAGE.html                     →  USAGE.html
docs/ARCHITECTURE.html              →  ARCHITECTURE.html
docs/CONTRIBUTING.html              →  CONTRIBUTING.html
docs/INDEX.html                     →  INDEX.html
docs/experts/index.html             →  experts/index.html
docs/experts/data.json               →  experts/data.json
docs/experts/ai/aiml/llm-engineer.html →  experts/ai/aiml/llm-engineer.html
... (15 expert .html)              →  experts/<category>/<name>.html
```

**根 `index.html` 在仓库根**(作为站点首页),**不是** `docs/index.html`。

## 🔄 构建流程

每次 push 到 miao 分支,自动:

```
git push origin miao
   ↓
GitHub Actions: pages-build-deployment
   ↓
build job: success(空,只是占位)
   ↓
deploy job: 把 miao 分支的 docs/ + 根 index.html 部署到 GitHub Pages CDN
   ↓
URL: https://godlockin.github.io/kallax-experts/
```

## 🤖 自动 build-html + build-experts

`.github/workflows/build.yml` 跑(每次 push):

```yaml
1. checkout 代码
2. setup-python 3.11
3. python3 tools/build-html.py     # 把 docs/*.md → docs/*.html
4. python3 tools/build-experts.py # 把 experts/*.md → docs/experts/**/{name}.html + index.html
5. bash tools/validate.sh        # 验证 frontmatter
6. 验证 build output(文件存在 + 链接)
```

> **重要**:build.yml **不会** 触发 GitHub Pages build。
> GitHub Pages build 由 `pages-build-deployment` workflow 单独触发。

## ⚙️ API 配置

```bash
# 当前状态
gh api repos/godlockin/kallax-experts/pages | python3 -m json.tool

# 改 source branch
gh api -X PUT repos/godlockin/kallax-experts/pages \
  --input '{"source":{"branch":"<branch>","path":"/<path>"}}'

# 触发 build
git push origin <branch>  # 自动触发
# 或
gh workflow run "pages-build-deployment"
```

## 🔒 隐私保护

**所有 .md / .html 文件已脱敏**:
- 无真实人名 / 邮箱 / 公司
- 维护者显示 `@test-maintainer`
- 仓库地址显示 `your-org/kallax-experts`(README 中)
- 但实际 GitHub URL 用真实 `godlockin/kallax-experts`

## ⚠️ 已知问题

1. **CDN 缓存**:GitHub Pages CDN 缓存约 1-5 分钟,push 后不会立即看到
2. **404 on first deploy**:默认分支 / path 不匹配时,旧 URL 可能 404(已 fix: branch=miao)
3. **Workflow 失败重试**:GitHub Actions 偶发 "Deployment failed, try again later"(已 fix: 空 commit 触发)

## 📊 已部署 URL 状态

```bash
$ for url in "" "experts/" "experts/tech/security/security-engineer.html" \
            "USAGE.html" "ARCHITECTURE.html" "experts/data.json"; do
    code=$(curl -sL -o /dev/null -w "%{http_code}" "https://godlockin.github.io/kallax-experts/$url")
    echo "  $code  /$url"
done
# 期望:全 200
```

## 🔧 故障排查

### URL 404
- ✅ 检查 `gh api pages` 是否有 status: built
- ✅ 检查 `path` 是否正确(branch=miao, path=/docs)
- ✅ 检查文件是否在 docs/(不是根)
- ✅ 等待 5-10 分钟(CDN 缓存)

### Build failed: "Deployment failed, try again later"
- ✅ 等 1 小时重试(GitHub 临时服务问题)
- ✅ 空 commit 触发:`git commit --allow-empty -m "retry"`

### Workflow 失败
- ✅ 看 `gh run view <run-id> --log`
- ✅ 修 docs/ 里不合法 frontmatter

## 📜 历史

| 时间 | 事件 |
|------|------|
| 2026-07-05 | 创建仓库 + 首批 5 expert |
| 2026-07-05 | 加 10 expert(借鉴 eket + agency) |
| 2026-07-06 | 加 compose.sh + GitHub Pages 部署 |
| 2026-07-06 | 启用 Pages(build_type=legacy) |
| 2026-07-07 | 加 experts 列表 + JS 搜索 |
| 2026-07-07 | 加 build.yml CI 自动 build |
| 2026-07-07 | 修 path 链接(docs/ → /) |

## 🔗 关联文件

- `index.html` — 根入口(GitHub Pages 站根)
- `docs/PAGES.md` — 本文件
- `docs/README.md` — 项目说明
- `tools/build-html.py` — .md → .html
- `tools/build-experts.py` — expert 列表 + 详情页
- `tools/validate.sh` — frontmatter 验证
- `.github/workflows/build.yml` — CI 自动 build
- `.github/workflows/validate.yml` — frontmatter 验证 CI
- `.github/workflows/pages.yml` —(已删除,GitHub 自动 pages-build-deployment 接管)