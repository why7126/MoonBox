## 背景

当前 `data/` 同时存在按存储类型划分的 `data/sqlite/`、`data/s3/`，以及按运行时服务划分的 `data/runtime/backend/`、`data/runtime/chat-platform/`、`data/runtime/governance/`。其中 `data/runtime/backend/sqlite/` 与 `data/sqlite/` 语义重复，容易让本地开发、Docker 运行、Chat Platform 和迁移脚本对真实数据库位置产生误判。

## 变更内容

- 明确 `data/sqlite/` 是本地 SQLite 唯一持久数据库目录，`data/s3/` 是本地 MinIO/S3 对象数据目录。
- 明确 `data/runtime/` 只承载 Chat Platform、Governance、Codex 执行器等运行控制状态，不再作为业务数据库或媒体对象的 canonical 目录。
- 更新目录结构规范、部署文档、数据库文档、Docker 基线说明和目录校验脚本。
- 对既有 `data/runtime/backend/sqlite/`、`data/runtime/backend/media/` 保留迁移期 warning，不在本 Change 中移动或删除真实运行数据。
- 写入治理日志并将纯治理 Change 纳入 `sprint-007`。

## 能力影响

### 新增能力

- 目录结构校验会报告 legacy runtime backend 存储目录 warning，帮助后续迁移前识别重复落点。

### 修改能力

- `harness-runtime`: 明确 `data/` 下持久存储与运行时控制状态的目录边界。
- `deployment-governance`: 明确本地 SQLite、对象存储、Chat Platform runtime 与治理 runtime 的宿主机目录归属。

## 影响范围

- 规则：`rules/directory-structure.md`。
- 文档：`docs/02-deployment.md`、`docs/04-database-design.md`、`docs/README.md`、`scripts/docker/README.md`。
- 脚本：`scripts/validate-directory-structure.py`。
- OpenSpec：本 Change 的 proposal、design、tasks、trace、test-plan 和 delta spec。
- Sprint：`sprint-007` 新增纯治理 Change scope。
- API/DB/Web/管理端/客户端/Orval：不触达业务实现或 schema。
- Docker Compose：本 Change 只更新治理和迁移说明，不直接改 Compose 挂载，避免在未迁移真实数据前切换运行库路径。
