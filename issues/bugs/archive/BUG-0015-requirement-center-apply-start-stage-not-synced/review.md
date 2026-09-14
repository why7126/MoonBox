---
bug_id: BUG-0015-requirement-center-apply-start-stage-not-synced
created_at: 2026-09-12 17:49:30
updated_at: 2026-09-12 17:49:30
review_status: approved
reviewed_at: 2026-09-12 17:49:30
severity: medium
priority: P2
hotfix: false
---

# 缺陷评审

## 结论

评审通过，确认修复。根因范围限定为启动状态写入缺口及 Workflow Sync 与看板判定口径不一致；未把实际部署缓存或刷新故障认定为已确认根因。

用户本次执行 bug-review，按项目无 flag 默认通过规则完成评审。评审通过不表示修复完成或验收通过，不自动纳入 Sprint、生成 OpenSpec 或实施代码。

## 评审清单

| 项目 | 结论 | 依据 |
|---|---|---|
| 可复现或根因充分 | 通过 | root-cause.md 为 confirmed，6条可定位证据；根因门禁通过，state-matrix.json 的两份源码 SHA-256 与当前源码一致，四组合成复现结果可复核。 |
| 严重等级合理 | 通过 | medium / P2；影响研发状态可信度与协作判断，暂无数据丢失、安全事故或研发阻断证据。 |
| 回归验收明确 | 通过 | acceptance.md 的 AC-001 至 AC-011 覆盖 REQ/BUG、0/N、门禁失败、重复同步、中断恢复、完成门禁及真实刷新；均尚未执行。 |
| 是否需 hotfix | 否 | 采用常规 fix，先纳入 Sprint 再创建修复 Change。 |

## 修复范围与约束

- 统一启动、进度与完成的状态事实源和派生规则，已启动 0/N 不回退到准备开发态。
- 两份 apply 技能和 Sprint 编排共用契约；Issue 迭代内 与 Change 进行态 保留各自语义。
- 不提前勾选任务，不把完成同步当启动同步，不把单文件手工修改当完整修复。
- 真实 API/浏览器刷新观察属于后续修复验收条件，不能用合成函数复现替代。
- BUG-0014 仅作复现案例；本条目前无 Sprint、无修复 Change，不继承案例的 sprint-005。

## 数据采集与链路观测

- product_data_collection_observability: applicable
- affected_layers: Agent Workflow、后端治理状态读取、Web 阶段展示。
- N/A 原因：本次评审不变更 API、DB、对象存储、部署、安全或客户端生成物；正式设计按实现范围复核，CLI 不伪造界面行为事件。
- validation: 根因结构门禁与源码哈希复核通过；真实部署与11项修复验收未执行。

## 后续流程

先执行 /sprint-propose --bug BUG-0015-requirement-center-apply-start-stage-not-synced；完成正式纳入及状态同步后才进入 bug-opsx。
