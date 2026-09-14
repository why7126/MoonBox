---
change_id: fix-requirement-center-apply-lifecycle-sync
bug_id: BUG-0015-requirement-center-apply-start-stage-not-synced
created_at: 2026-09-12 20:58:55
updated_at: 2026-09-13 23:43:10
---

## 背景

[BUG-0015](../../../issues/bugs/review/BUG-0015-requirement-center-apply-start-stage-not-synced/bug.md) 已确认研发启动后卡片仍停留待开发：0/N 无法表达已启动，Workflow Sync 与看板又使用不同状态来源。需要把启动、进度和完成的状态同步连成可验证的闭环，避免团队误判或重复发起研发。

## 变更内容

- 增加通过门禁后的研发启动同步，0/N 立即进入研发中。
- 统一状态事实源、任务进度派生与看板映射；重跑和恢复不回退已启动事实。
- 两份 apply 技能及 Sprint 编排接入同一契约，完成门禁通过后才写入 applied。
- 回归覆盖REQ/BUG、门禁失败、0/N、部分完成、幂等、恢复、终态保护与真实刷新。

## 能力范围

### 新增能力

无新增独立业务能力。

### 修改能力

- `agent-workflow-tooling`：增加启动、进度与完成事件及统一事实源契约。
- `web-catalog-requirement-center-real-data`：明确九阶段中待开发、研发中、验收中的判定与刷新一致性。

## 影响范围

涉及 scripts/workflow_sync、后端 requirement_center 及治理快照读取、前端看板回归、两份apply技能、sprint-apply、流程规则和相关测试。保持Issue主状态in_sprint语义和分级元数据归属；不增加独立业务页面。预计沿用现有context响应结构，无数据库表结构、对象存储或部署变更；若实现改变接口或持久化边界，同步API索引、OpenAPI/客户端和相应文档测试。

来源BUG已评审并纳入sprint-005，M=3人天，Sprint总计17/20人天；剩余机动3人天，避免扩大范围。BUG-0014仅作为复现案例。

## 回滚计划

按同一变更整体回退状态读取器、同步器与技能入口，避免新旧写读口径混用。新增启动元数据采用兼容的可选字段；回退不删除已保存的启动或完成证据，不批量改写历史Issue。回退后以任务真实证据人工核对状态，并标明旧版本无法识别0/N启动；若文件写入中断，先恢复完整事实源再重跑同步，禁止将已完成或归档记录降级。

## 数据采集与链路观测

- product_data_collection_observability: applicable
- affected_layers: agent_workflow、web、api治理状态读取。
- N/A原因：无新增usage_events、request_logs、task_traces表字段或保留周期，无对象存储依赖；CLI启动不伪造界面行为。现有API鉴权与请求关联保持，是否涉及Schema变动在实现时复核。
- validation: 根因6条证据与四组合成复现通过；本Change尚未实现，AC-001至011及真实刷新验收待执行。
