---
title: 本地数据挂载与自动快照轮转变更追溯
created_at: 2026-10-08 14:44:33
updated_at: 2026-10-08 15:48:57
change_id: add-local-data-mount-and-snapshot-rotation
status: applied
requirement: REQ-0043-unify-data-mount-and-snapshot-rotation
bug: null
sprint: sprint-009
product_data_collection_observability:
  status: applicable
  affected_layers:
    - db
    - task_traces
    - task_trace_spans
  reason: 本地数据库、自动快照与迁移属于 DB 和多步骤后台维护；当前无新增 API、UI 或客户端请求，usage_events、request_logs 与请求封装为 N/A。
  validation: 后续实施核对目录与账本、迁移/快照/恢复任务摘要及节点关联和脱敏；若新增 API 或界面入口，重新补充对应观测层与文档测试。
execution:
  schema_version: 1
  started_at: 2026-10-08 14:45:47
  completed_at: 2026-10-08 15:48:57
  last_event: opsx.apply
---

# 本地数据挂载与自动快照轮转变更追溯

## 来源与范围

来源为已评审并纳入 sprint-009 的 REQ-0043。Change 类型为 add，新增本地自动快照轮转能力，修改部署治理中的本地目录要求。需求验收入口为 `issues/requirements/review/REQ-0043-unify-data-mount-and-snapshot-rotation/acceptance.md`，覆盖 AC-001 至 AC-019。

## 实施状态

已执行 `opsx.start`、`opsx.progress`、`opsx.apply`，19/19 任务完成，本地挂载、离线迁移工具和自动快照轮转已交付。实际宿主库存只有 canonical 业务库，未发现 legacy 业务库或旧快照账本；因此没有对真实业务库执行迁移、清理或回滚。实施完成时间由 Workflow Sync 记录。

## 验证计划

重点验证实际挂载与数据不分叉、旧库差异停止、默认 2/正整数/0、受保护快照、独立删除日志、故障注入、SQLite/MySQL 与离线恢复。API、UI 和客户端生成当前为 N/A；实施若增加入口需重评并补齐验证。

## 验证记录

- 静态配置：根 Compose、本地 Compose、Chat 与 Governance overlay 配置均可解析；根与 overlay 的 backend、chat-worker、governance-controller 各只有一个 `/app/data` 挂载，来源为宿主 `data`。`scripts/docker-up.sh --check` 与本地 Compose 示例校验通过。
- 根据 `.env.example` 使用反馈，移除了由脚本生成的仓库白名单与绑定、内部测试变量和重复的治理根变量；保留部署者输入及快照上限。使用精简后的 `.env.example` 再跑 `scripts/docker-up.sh self-storage-sqlite --check` 通过。
- 合成回归：聚焦后端用例 30 项通过，覆盖双库差异与显式选源、损坏库、旧媒体阻断、生产数据库门禁、API/Worker 快照配置不一致、配置值、Worker 快照调用、轮转、受保护与来源不明副本、登记/过期失败、删除日志及治理成套离线恢复。
- 隔离运行观察：一次性后端容器挂载临时 `data` 后，`/health` 返回 200；第二次容器启动可打开同一 canonical SQLite，未生成 legacy 路径。临时数据已清理。此证据不等同于真实 Chat Worker、Chat 执行或完整 Compose 部署验收。
- 数据安全：真实 `data/sqlite/moonbox.db` 只做只读盘点，legacy 库不存在；未执行真实库切换。`deletions.sqlite` 与快照文件未在真实目录清理。
- 观测范围：自动快照在业务库写入 `local_snapshot` Task Trace 与 `local_snapshot.*` span，记录固定错误码和副本计数。离线迁移停服期间没有在线 DB Task Trace，迁移库存 manifest 记录不透明任务 ID、阶段和状态；HTTP API、OpenAPI、Orval、UI、请求日志、行为埋点和客户端请求封装均无新增入口。
- 真实本地运行观察：使用项目后端虚拟环境运行 `scripts/docker-up.sh self-storage-sqlite`，根部署脚本完成配置预检和目录准备；backend、Web、MinIO、chat-worker、governance-controller 均健康。`docker inspect` 显示 backend、chat-worker、governance-controller 的 `/app/data` 均挂载同一宿主 `data`；容器内 API `/health` 返回 200。宿主 HTTP 探测受当前工具网络隔离影响，改由容器内验证。
- 启动脚本修复：首次启动尝试使用系统 Python，因缺少 `sqlalchemy` 停在私有备份目录准备前；改用现有后端虚拟环境完成启动。`scripts/docker-common.sh` 现优先自动选取该虚拟环境，未设置 `PYTHON_BIN` 的真实 `.env` 启动预检、Shell 语法与 diff whitespace 校验通过。
- 真实重启与轮转：backend 和 chat-worker 受控重启后均恢复健康；第二次重启 chat-worker 后，自动快照库存依次为 1、2、2 份，最早副本被轮转，当前两份摘要有效。业务库 `PRAGMA integrity_check=ok`，未出现 legacy 业务库；业务库中有 3 条 `local_snapshot` 任务及各 3 条 started/rotated span。
- 真实离线恢复：在 chat-worker 私有运行目录内用最新自动快照创建临时离线恢复库，`PRAGMA integrity_check=ok`，删除意图重放入口返回 0 条（本次环境没有待重放删除）；临时恢复目录在验证结束时自动清理，未切换在线库。
- 真实 Chat 执行：经用户授权，在隔离临时 SQLite、临时 Git 仓库和临时 Worker 容器中发出一条极短消息；执行状态 `completed`、额度 `settled` 且实际 Token 数大于 0。测试仓库未变化，主动删除后的离线恢复不复活已删除会话；探针容器与认证副本已清理。正式服务仍健康，canonical 库完整，legacy 未再出现。
- 验收限制：约 24 小时自然周期尚未实际等待，周期调用路径由聚焦测试覆盖。本机无 legacy 业务库，因此未对真实旧库执行切换；双库内容冲突与回滚由隔离回归验证。REQ AC-001 至 AC-019 已逐条记录证据层级；最终人工 sign-off 留给后续验收/归档流程。

## 中断续接检查点

身份：REQ-0043-unify-data-mount-and-snapshot-rotation、`add-local-data-mount-and-snapshot-rotation`、sprint-009。`opsx.start`、`opsx.progress`、`opsx.apply` 均已成功；用户授权的隔离真实 Chat 会话已完成并清理，19 项 AC 均有实施验证证据。合成回归、真实部署及不适用边界分层记录于本节和 REQ 验收清单。AI Usage Hook 返回 warning/unavailable（无可归因 command-run 事件），不影响 Change applied。最终人工 sign-off、生产升级与归档仍为后续独立流程。
