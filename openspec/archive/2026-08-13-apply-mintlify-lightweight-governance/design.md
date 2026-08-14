---
created_at: 2026-08-09 08:54:59
updated_at: 2026-08-09 08:54:59
---

# 设计说明

## 轻量产品手册模型

MoonBox 保留 `mintlify/docs/latest/` 作为默认公开入口，允许后续存在 `mintlify/docs/vX.Y.Z/` 固定版本投影。`mintlify/` 不成为事实源：长期信息仍来自 `docs/`，发布公告仍来自 `releases/vX.Y.Z/announcement.mdx`，部署方式仍来自 `deploy/`。

`usage_docs` 决策只写入 release 对象，用于表达本版本是否需要刷新公开产品手册：

- `generated`：已生成或刷新 Mintlify 投影，并通过公开安全校验。
- `skipped`：明确确认本版本无需刷新产品手册，记录确认来源、时间和原因。
- `pending_confirmation`：尚未确认，发布准备或发布确认不得视为完成。

## Mintlify 站点校验

`scripts/validate-mintlify-docs.py` 继续兼容 `mintlify/mint.json`，并校验：

- 导航页面存在。
- `site-manifest.json` 的 `latest_version`、`versions`、`projections`、`manual_overrides`、`assets` 结构有效。
- 站内链接和图片引用不缺失。
- 引用 `/assets/screenshots/<file>` 时文件存在；如 manifest 记录 hash，则校验实际文件 hash。
- 不存在 `.env`、`.mintlify/`、构建产物、敏感配置、密钥、Authorization header、Cookie、数据库连接串或对象存储凭据。

## docs-site 部署

本地与生产 Compose 均通过 `docs-site` profile 承载 `mintlify/`。服务只读挂载公开产品手册源目录和静态预览脚本，不挂载真实 env、对象存储、数据库、后端运行时数据或密钥。

发布范围涉及 Mintlify 站点、docs-site 服务、`HOST_PORT_MINTLIFY_DOCS`、文档站 Docker/Compose 配置或静态预览脚本时，release 门禁必须包含：

- `python scripts/generate-mintlify-docs.py --version <version|latest>`
- `python scripts/validate-mintlify-docs.py`
- 对应 `docker compose ... --profile docs-site ... config --quiet`
- 如生产承载方式未确认，记录 blocker 或待确认项。

## 学习对象适配

ProjectTilesFST 的完整 usage-docs 快照、强截图门禁和 `docs.json` 唯一配置不直接迁移。MoonBox 先采用轻量门禁，降低治理成本，并保留后续升级空间。
