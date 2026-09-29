## 背景

`sync_issue_subdocuments()` 已能安全同步 Issue 主文档：REQ 使用 `requirement.md`，BUG 使用 `bug.md`。当前 `SyncEngine` 的默认触发条件覆盖 `req.*`、`bug.*`、`opsx.*`、`sprint.archive` 和显式扫描，但 `sprint.propose` 只进入 trace、registry、CHANGELOG 更新条件，未进入子文档同步条件。

因此当 `/sprint-propose --bug BUG-xxxx-slug` 让 `derive_issue()` 把 BUG 从 `approved` 派生为 `in_sprint` 时，`bug.md` 不会自动获得同一状态。

## 目标

- 让 `sprint.propose` 聚焦 REQ/BUG 时同步对应主文档状态。
- 保留现有聚焦边界，只同步命令传入的 `--req` / `--bug`。
- 不改变 `acceptance.md` 的验收语义和回填规则。
- 不批量扫描或改写无关 Issue 子文档。

## 非目标

- 不重写历史 BUG 文档。
- 不改变 Sprint 四件套派生格式。
- 不修改 REQ/BUG 生命周期状态机。
- 不触碰业务 `src/`、API、数据库或前端实现。

## 实现方案

1. 在 `SyncEngine._run()` 的 `should_sync_subdocuments` 判定中新增 `event == "sprint.propose"` 分支。
2. 该分支仅在当前 `iid` 等于 `req_id` 或 `bug_id` 时触发。
3. 继续复用 `sync_issue_subdocuments()`，由其只更新主文档 `status`，并按既有逻辑处理 `acceptance.md` 的 `acceptance_status`。
4. 增加单元测试：构造聚焦 BUG、planning Sprint 和 derived `in_sprint`，验证 `sync_issue_subdocuments()` 被调用且接收到的派生态为 `in_sprint`。

## product_data_collection_observability

```yaml
status: not_applicable
affected_layers: []
reason: 本变更仅增强 Agent Workflow 治理脚本对 Markdown Issue 子文档主状态的派生同步，不新增或修改 API、数据库、请求日志、行为事件、Task Trace、请求封装、对象存储或运行时产品数据采集。
validation: 通过聚焦单元测试、Workflow Sync dry-run/check、OpenSpec 与目录治理校验确认；业务运行时测试不适用。
```

## 风险

- `sprint.propose` 聚焦 Issue 若同时存在 `acceptance.md`，复用现有子文档同步会维持 `acceptance_status: not_started`；这与纳入 Sprint 后尚未实施的验收语义一致。
- 若调用方未传入 `--req` 或 `--bug`，本变更不会扩大同步范围，仍需按 Sprint 文档和 trace 派生结果检查整体一致性。
