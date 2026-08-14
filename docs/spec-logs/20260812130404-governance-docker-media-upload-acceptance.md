---
title: Docker media-upload 验收口径治理
type: governance
created_at: 2026-08-12 13:04:04
updated_at: 2026-08-12 13:04:04
source_change: fix-docker-media-upload-acceptance-gate
source_bug: BUG-0007-docker-media-upload-acceptance-hardcodes-3000-port
---

# Docker media-upload 验收口径治理

## 背景

BUG-0007 发现 Docker media-upload 横切验收同时依赖固定宿主端口和本地持久库中的默认管理员密码，导致 `/opsx-apply` 可能被错误阻塞。

## 更新内容

- 将 media-upload Docker 验收口径从固定端口改为解析 `HOST_PORT_WEB`，默认 `18102`。
- 明确 Docker 本地库为持久状态，验收不得依赖默认管理员密码。
- 新增 `scripts/verify-docker-media-upload.py`，由脚本准备一次性前台测试用户并验证登录、头像上传、受保护读取和回显。
- 更新 `docs/07-object-storage-strategy.md`、`docs/knowledge-base/best-practices/admin-media-upload-chain.md`、`.agents/skills/req-complete/SKILL.md` 与 sprint-002 横切说明。

## 验证

- `uv run pytest tests/unit/test_verify_docker_media_upload.py`：通过。
- `scripts/verify-docker-media-upload.py --file <tmp-image>`：通过；Web 端口 `18102`，测试身份由脚本准备。
- `openspec validate fix-docker-media-upload-acceptance-gate --strict`：通过。

## 影响边界

- API：不新增正式业务 API。
- DB：脚本仅在本地 Docker SQLite 运行时库中准备可回收测试用户，不改变 schema。
- Web：不修改 UI。
- Docker Compose：不改变拓扑。
- 安全：脚本输出不包含密码、Authorization header、Cookie、真实 `.env` 原文或本机绝对路径。

## 后续建议

后续可将 Docker media-upload 验收脚本纳入对应 `/opsx-apply` 自动验证清单，作为媒体上传横切 gate 的标准证据入口。
