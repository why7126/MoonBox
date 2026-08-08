---
purpose: Mintlify 公开产品文档站源目录说明
content: MoonBox 产品手册源文件、版本快照、公告投影、截图资产和部署边界
created_at: 2026-08-04 00:00:00
updated_at: 2026-08-04 00:00:00
owner: MoonBox 产品团队
---

# Mintlify 文档站源目录

`mintlify/` 承载 MoonBox 公开产品手册、Mintlify 配置、公告投影和可公开截图资产。

- `mintlify/docs/latest/` 指向最新已发布且产品手册校验通过的版本。
- `mintlify/docs/vX.Y.Z/` 由发布快照同步或投影生成。
- `mintlify/releases/` 承载公开发布公告投影。
- `mintlify/assets/screenshots/` 集中存放按内容 hash 命名的共享截图资产。
- `mintlify/site-manifest.json` 记录站点投影、共享资产、`latest` 指针和人工修正记录；Mintlify 页面不得替代 `docs/`、`releases/`、`deploy/` 或 OpenSpec 事实源。

本目录不得存放构建产物、真实客户数据、密钥、数据库连接串、真实 `.env`、Authorization header、Cookie、运行时数据库或不可公开运维信息。

## 站点投影规则

- `mintlify/mint.json` 是当前主配置；若后续迁移到 `docs.json`，必须同步 `scripts/validate-mintlify-docs.py` 和本文档。
- `latest` 只允许指向最新已发布、产品手册已生成且 Mintlify 校验通过的版本。
- `mintlify/docs/vX.Y.Z/` 是固定版本快照，生成后默认冻结；旧版本内容修正必须在 `site-manifest.json manual_overrides` 或对应 release manifest 中记录原因、确认人、时间、影响文件和摘要。
- `mintlify/assets/screenshots/` 只放可公开真实系统截图，文件名 SHOULD 使用 `sha256-<digest-prefix>-<semantic-name>.<ext>`；页面引用 SHOULD 使用 `/assets/screenshots/<file>`。
- 更新 `latest`、导航、截图或人工修正记录后，必须运行 `python scripts/validate-mintlify-docs.py`。

## 生成与校验

```bash
python scripts/generate-mintlify-docs.py --version latest
python scripts/validate-mintlify-docs.py
```

生成脚本只投影公开文档源，不替代 `docs/`、`releases/` 或 OpenSpec 事实源。需要对外发布时，先完成 release 校验，再生成 Mintlify 投影并通过公开内容安全校验。

## 本地和生产部署

本地预览：

```bash
bash deploy/scripts/up.sh local self-storage-sqlite
```

生产承载：

```bash
bash deploy/scripts/up.sh prod external-storage-external-mysql
```

Compose 中的 `docs-site` 服务只挂载 `mintlify/` 源目录和静态预览脚本，默认端口由 `HOST_PORT_MINTLIFY_DOCS` 控制。
