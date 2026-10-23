---
bug_id: BUG-0044-requirement-stage-premature-transition-session-split
title: 需求中心阶段门禁与原会话续用验收标准
created_at: '2026-10-19 11:03:36'
updated_at: 2026-10-20 08:19:17
acceptance_status: passed
---

# 需求中心阶段门禁与原会话续用验收标准

## 验收状态

实施与逐项证据已核对，正式状态由当前 Change 的自动验收清单与 Workflow Sync 回填。真实操作使用隔离对象和受控延迟，不在业务 BUG-0028 上重复执行写入命令。

## 验收项

### AC-001 完成型迁移门禁

- [x] AC-001 隔离环境延迟命令终态，先写入治理阶段文档。卡片保持未完成业务阶段并显示执行中，后续治理动作不可启动；仅终态成功且业务校验、同步通过后迁移一次。
- 验证证据：后端门禁测试、真实页面前后截图及脱敏轮次时间线。

### AC-002 原会话续用

- [x] AC-002 前轮完成后从卡片执行下一命令，沿用同用户同项目同主对象的可用会话；忙碌时查看原执行并保留草稿，不静默另建。
- 验证证据：会话选择测试、点击前后会话映射。

### AC-003 对象级并发控制

- [x] AC-003 双标签页、不同会话、并发请求和直接 API 同时启动同对象治理操作，最多一个被接受；其余返回受控状态，不依赖按钮锁。
- 验证证据：并发集成测试与请求/任务摘要。

### AC-004 权限与会话边界

- [x] AC-004 多用户、不同项目同名对象、多历史会话、归档/删除会话分别验证；不复用不可访问会话，不泄露其他用户标题或内容。
- 验证证据：权限回归及选择策略矩阵。

### AC-005 执行型迁移

- [x] AC-005 开始开发/返修实际启动后及时显示研发中；不等整个命令结束，失败启动不伪造已开始；不覆盖首次 apply 完成事实。
- 验证证据：生命周期回归与真实启动页面。

### AC-006 失败与停止恢复

- [x] AC-006 轮次失败或停止但存在产物时显示结果待核对，保留有效成果；核验后明确是否可推进，不盲目回滚或直接放行。
- 验证证据：故障注入、产物校验及页面反馈。

### AC-007 未知终态与重连

- [x] AC-007 未知终态、刷新、断连及服务重启后先恢复一致的执行事实；确认终态前不重复执行，恢复操作幂等。
- 验证证据：恢复集成测试、刷新前后证据。

### AC-008 成功与业务校验分离

- [x] AC-008 轮次 completed 但业务校验或状态同步失败时不完成迁移；通过后阶段、按钮、索引一致，重复回调不重复迁移。
- 验证证据：完成条件组合测试及同步结果。

### AC-009 全入口覆盖

- [x] AC-009 逐项覆盖 REQ/BUG 分析、生成、完善、评审、迭代、Opsx、开发、归档与 Agent 助手；直接 Chat、只读按钮和未接入命令列明各自行为，不将静态映射当真实执行证据。
- 验证证据：入口矩阵：命令、阶段、会话状态、请求、预期/实际、证据入口。

### AC-010 外部治理同步

- [x] AC-010 外部 Codex/CLI 合法更新经治理校验后可收敛，不强求产品 Chat 轮次；明确无法观测的外部并发边界。
- 验证证据：隔离外部命令样本与同步证据。

### AC-011 只读入口可用

- [x] AC-011 执行期间文档、研发/测试进度、验收详情仍可读取；不被全局治理动作锁误伤。
- 验证证据：浏览器交互回归。

### AC-012 链路观测与安全

- [x] AC-012 可关联行为、请求、任务、对象与轮次并解释复用/忙碌/拒绝/阶段生效；直接 API 无行为事件仍可排障；不记录凭证和原始 Prompt。
- 验证证据：脱敏观测样本及日志安全断言。

## 证据与环境要求

记录环境、版本、对象业务 ID、时间及执行状态；真实浏览器证据覆盖 1440px 的执行中、成功可继续、失败/未知及查看执行交互。API/并发/恢复合成测试与真实产品观察分别标记，不能互相替代。原始日志、凭证及内部个人标识不进入长期文档。

## 数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: Web、API、请求日志、Task Trace、Chat 执行状态。

validation: AC-012；schema、部署和客户端生成是否变化由实现方案确定，若未变化逐项注明 N/A 原因。本次文档完善未改变这些边界。

## 本轮证据签认

逐AC结论与入口见[Change逐项签认](../../../../openspec/archive/2026-10-19-fix-requirement-stage-completion-session-continuity/evidence/acceptance/signoff.md)。真实REQ正向、BUG慢收尾及负向校验、HTTP入口矩阵、合成故障注入分别标明。1440px实际产品视口与computed style已核对；原会话、草稿与只读入口可用。最终机器readiness仍以验收清单为准，勾选不替代该门禁。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-20 08:19:17
accepted_by: workflow-sync
source_change: fix-requirement-stage-completion-session-continuity
source_sprint: sprint-010
evidence: [openspec/archive/2026-10-19-fix-requirement-stage-completion-session-continuity/evidence/acceptance/20261019134548470464-cd1793b5/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

