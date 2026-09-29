## 背景与现状

MoonBox 原始规划中，`data/sqlite/` 承载本地 SQLite 数据库，`data/s3/` 承载自建 MinIO/S3 对象数据。Chat Platform 和 Governance 引入后，为隔离 Codex 执行器、会话状态、工作区与治理控制器状态，新增了 `data/runtime/`。

当前问题在于 `data/runtime/backend/` 又复刻了后端 `/app/data` 的完整挂载结构，导致 `data/runtime/backend/sqlite/moonbox.db` 成为 Docker/Chat 实际使用库，而 `data/sqlite/moonbox.db` 仍作为本地直连默认库存在。目录名已经无法表达“哪个是 canonical 持久数据库”。

## 目标

- 建立单一目录语义：持久数据按存储类型归属，运行控制状态按 runtime 归属。
- 保留既有真实运行数据，不在治理 Change 中执行迁移、删除或覆盖。
- 通过文档和校验脚本让 legacy 重复目录可见，避免后续继续把业务持久数据写入 `data/runtime/backend/`。

## 非目标

- 不移动、删除、压缩或覆盖 `data/` 下任何真实运行文件。
- 不修改后端 API、数据库 schema、Web、管理端或客户端业务实现。
- 不直接切换 Docker Compose 挂载路径；该动作必须在完成数据库备份、停服、校验和迁移后由独立迁移 Change 执行。

## 目录职责

```text
data/
  sqlite/        # 本地 SQLite 唯一持久数据库目录
  s3/            # 本地 MinIO/S3 对象数据目录
  runtime/       # 运行控制状态，不作为业务数据库或对象存储 canonical 根
    chat-platform/
      state/
      runtime/   # Codex HOME/CODEX_HOME、session 和执行器内部状态
      workspaces/
      backups/
    governance/
      ...
  tmp/           # 本地临时文件处理目录
  ai-usage/      # AI Usage 脱敏派生事实
  visual-evidence/
```

`data/runtime/backend/sqlite/` 与 `data/runtime/backend/media/` 被视为迁移期 legacy 目录。目录结构校验先输出 warning，不阻断；等独立迁移 Change 完成后，再升级为阻断或删除兼容逻辑。

## 迁移策略

1. 停止使用 SQLite 的后端、Chat Worker 和 Governance Controller。
2. 备份 `data/runtime/backend/sqlite/moonbox.db` 与 `data/sqlite/moonbox.db`。
3. 对比两个库的表清单、关键表行数和 `PRAGMA integrity_check`。
4. 选择权威库并迁移到 `data/sqlite/moonbox.db`。
5. 更新 Compose 挂载，使容器内 `/app/data/sqlite/moonbox.db` 指向宿主机 `data/sqlite/moonbox.db`。
6. 启动服务并验证 Chat 会话、媒体上传、治理控制器和空间申请演示数据。
7. 确认无回退后，清理 legacy runtime backend 存储目录。

## 风险

| 风险 | 缓解 |
|---|---|
| 未停服移动 SQLite 导致数据丢失或 WAL 不一致 | 本 Change 不执行迁移；后续迁移 Change 必须停服、备份和完整性校验。 |
| 文档先行导致当前 Compose 与目标目录不一致 | 部署文档明确当前为迁移期 legacy 状态，并要求独立迁移 Change 才能切换挂载。 |
| 继续向 `data/runtime/backend/` 写入新持久数据 | 目录校验输出 warning，规则声明该路径不再作为 canonical 持久存储目录。 |

## product_data_collection_observability

```yaml
status: not_applicable
affected_layers: []
reason: 仅修改目录治理规则、部署/数据库文档、校验脚本和 OpenSpec 治理事实源，不修改 API、数据库 schema、请求封装、行为事件、请求日志、Task Trace 或对象存储实现。
validation: 通过目录结构校验、上下文预算校验、OpenSpec 中文校验、目标 Change 校验、Sprint scope 校验和 Workflow Sync 校验确认。
```
