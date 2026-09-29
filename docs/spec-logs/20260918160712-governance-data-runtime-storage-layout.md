---
title: data 目录持久存储与运行时边界治理
created_at: 2026-09-18 16:07:12
updated_at: 2026-09-18 16:07:12
type: governance
change: standardize-data-runtime-storage-layout
sprint: sprint-007
---

# data 目录持久存储与运行时边界治理

## 迭代目标

统一 `data/` 目录语义，明确本地 SQLite、对象存储和运行时控制状态的归属，避免 `data/sqlite/` 与 `data/runtime/backend/sqlite/`、`data/s3/` 与 `data/runtime/backend/media/` 继续形成重复事实源。

## 变更摘要

- 明确 `data/sqlite/` 是本地 SQLite canonical 持久数据库目录。
- 明确 `data/s3/` 是自建 MinIO/S3 兼容对象数据目录。
- 明确 `data/runtime/` 仅承载 Chat Platform、Governance、Codex 执行器等运行控制状态。
- 对 legacy `data/runtime/backend/sqlite/` 与 `data/runtime/backend/media/` 增加目录校验 warning。
- 补齐部署、数据库、Docker 基线、目录结构规则和 OpenSpec delta。
- 不迁移、不删除、不覆盖任何真实运行数据。

## 影响范围

| 维度 | 影响 |
|---|---|
| API | 不适用，未修改接口。 |
| DB | 不修改 schema；仅声明本地 SQLite canonical 目录和迁移门禁。 |
| Web | 不适用，未修改前端。 |
| 客户端 | 不适用，未修改客户端生成物。 |
| 管理端 | 不适用。 |
| Orval | 不适用。 |
| Docker Compose | 未直接修改 Compose 挂载；文档标记当前 legacy 路径和后续迁移注意事项。 |
| 对象存储 | 明确 `data/s3/` 为本地对象数据 canonical 目录。 |

## 更新文件

- `rules/directory-structure.md`
- `docs/02-deployment.md`
- `docs/04-database-design.md`
- `docs/README.md`
- `scripts/docker/README.md`
- `scripts/validate-directory-structure.py`
- `openspec/changes/standardize-data-runtime-storage-layout/`
- `iterations/change/sprint-007/sprint.yaml`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

验证结果以 Change `trace.md` 的“验证记录”为准。目录结构校验在 legacy runtime backend 存储目录存在时通过并输出 warning；该 warning 用于提示迁移期重复目录，不阻断当前治理变更。

## 后续建议

后续如需真正切换 Docker Compose 挂载并迁移数据库，应创建独立迁移 Change，按停服、备份、完整性校验、关键表行数对比、启动验证和回滚方案执行。
