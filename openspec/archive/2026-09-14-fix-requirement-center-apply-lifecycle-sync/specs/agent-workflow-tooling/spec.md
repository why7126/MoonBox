---
change_id: fix-requirement-center-apply-lifecycle-sync
bug_id: BUG-0015-requirement-center-apply-start-stage-not-synced
created_at: 2026-09-12 21:00:30
updated_at: 2026-09-12 21:00:30
---

## ADDED Requirements

### Requirement: 研发执行生命周期同步

系统 MUST 区分研发启动、任务进度与完成事件，并以一致事实源派生Change、Issue关联状态和看板；Issue主状态及分级字段遵循现有归属。

#### Scenario: 门禁通过后启动零完成任务
- **WHEN** 已纳入Sprint的REQ或BUG通过实施前门禁并正式开始apply
- **THEN** 系统 MUST 幂等记录启动事实并使Change进入in_progress，即使任务完成数为零
- **AND** 两份apply技能与Sprint编排 MUST 使用相同契约

#### Scenario: 启动未通过门禁
- **WHEN** 前置门禁失败或只执行dry-run
- **THEN** 系统 MUST NOT 写入启动事实或改变待开发状态

#### Scenario: 进度同步与中断恢复
- **WHEN** 已启动Change更新任务、重跑同步或中断后恢复
- **THEN** 系统 MUST 保留启动事实、真实任务计数和幂等性，不退回proposed，不自动标记完成
- **AND** 跨文件部分失败 MUST 可重试修复投影且不覆盖并发修改

#### Scenario: 完成门禁与旧终态兼容
- **WHEN** 新生命周期契约的Change任务全部勾选但尚未通过完成门禁
- **THEN** 系统 MUST 保持研发中，仅在完成事件通过门禁后标记applied
- **AND** 旧条目 MUST 保持兼容，不伪造启动时间，不重开已完成或归档Issue
