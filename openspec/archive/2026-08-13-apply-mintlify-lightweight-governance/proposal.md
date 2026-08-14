---
created_at: 2026-08-09 08:54:59
updated_at: 2026-08-09 08:54:59
---

# 应用轻量 Mintlify 治理与部署边界

## 背景

MoonBox 已有 `mintlify/` 产品手册投影、`site-manifest.json`、`generate-mintlify-docs.py`、`validate-mintlify-docs.py` 和 `docs-site` Compose 服务，但 release 决策、站点投影、公开安全和部署承载边界仍分散在规则、脚本和部署文档中。

本 Change 基于 `/spec-study ProjectTilesFST --focus mintlify` 的候选结论，采用轻量治理方案：保留 MoonBox 当前 `latest` 优先的产品手册模型，不完整照搬版本化 usage-docs 快照体系；同时补齐 Mintlify 服务部署的本地预览、生产承载和发布门禁。

## 目标

- 明确 `usage_docs` 生成 / 跳过 / 待确认三态只作为发布决策门禁，不强制每版创建完整 `releases/vX.Y.Z/usage-docs/` 快照。
- 增强 `mintlify/site-manifest.json`、导航、链接、截图资产和公开安全校验规则。
- 将 `docs-site` 服务部署纳入部署治理和 release 门禁，明确本地预览、生产承载、只读挂载、安全输出和 Compose 校验要求。
- 更新 `/usage-docs-*` 技能、规则、部署文档和学习报告，形成可复用治理闭环。

## 非目标

- 不修改 `src/` 业务代码、API、数据库 schema、Web 管理端或后端运行时代码。
- 不切换到 `mintlify/docs.json` 作为唯一主配置。
- 不强制每个产品手册页面都必须有真实系统截图；当前采用 SHOULD + 可追溯共享资产校验。
- 不引入完整 ProjectTilesFST 版本化 usage-docs 生成体系。

## 影响范围

- `.agents/skills/usage-docs-*`
- `rules/document-governance.md`
- `rules/release.md`
- `rules/directory-structure.md`
- `docs/02-deployment.md`
- `deploy/README.md`、`deploy/local/README.md`、`deploy/prod/README.md`
- `scripts/validate-mintlify-docs.py`
- `docs/spec-logs/`
- `openspec/archive/2026-08-13-apply-mintlify-lightweight-governance/`
