---
bug_id: BUG-0049-archive-wrapper-workflow-sync-unrecognized
title: 归档包装脚本同步成功漏识别验收计划
created_at: '2026-10-19 23:00:04'
updated_at: 2026-10-20 08:19:17
acceptance_status: passed
source_event: bug.complete
---

# 归档包装脚本同步成功漏识别验收计划

## 验收范围与前提

使用独立待归档样本验证完整路径；BUG-0048 仅用于原执行的受控恢复验证，不重放归档。固定对象、执行标识和文件摘要，记录版本、环境、轮次、操作凭证和页面证据。以下条目依据实际执行结果与证据签认，非文档齐备推断。

## 验收条目

- [x] AC-001 包装脚本完整成功：同步与 Issue 迁移成功、文件结构正确且摘要稳定时，可信凭证被识别，门禁完成；看板进入完成，Chat 和对象只读权限一致。保存真实轮次与页面证据。
- [x] AC-002 失败拒绝：内部同步失败、迁移失败或凭证缺失/损坏分别阻断确认，显示可定位原因，保留文档和原执行，不伪造完成。
- [x] AC-003 身份与摘要：跨对象、动作或执行凭证不能使用；核验期间文件变化拒绝。无关治理写入后的旧凭证须按明确策略重新验证，不能忽略摘要差异。
- [x] AC-004 原执行恢复：针对 BUG-0048 已归档事实重新可信核验，不启动模型、不重放归档、不重复迁移；验证通过后门禁和看板一致，原历史记录保留。无法取得证明时报告具体阻断。
- [x] AC-005 幂等与重启：重复确认、并发核验、服务重启后恢复不会产生重复成果或错误解锁；旧执行不能覆盖新执行门禁。
- [x] AC-006 直接命令回归：顶层正式同步命令仍可识别；--check、--dry-run、同名伪装和仅模型成功文字均不能形成完成证明。
- [x] AC-007 页面一致性：完成后重新读取或刷新看板与原会话，阶段、待核对提示和权限一致；失败样本仍展示待核对且保留查看执行入口。

## 证据与验证方式

AC-001/004/007 包含真实产品观察；其他条目用聚焦回归与故障注入验证，并标明合成证据。文件归档、轮次 completed、退出码 0 均不能单独代替完整验收。证据在后续 Change 下保存，脱敏关联原轮次而不保存完整消息与身份信息。

## 数据采集与链路观测

- product_data_collection_observability: applicable
- affected_layers: Agent Workflow、私有操作凭证、执行门禁、状态读取和 Web 投影。
- validation: 对比动作、对象、执行、凭证、最终摘要、确认或拒绝结果，检查审计不含敏感内容。
- N/A：本计划未要求新增数据库字段或 API；如实现需要，须在 Change 中声明迁移与客户端生成影响并补充验证。


## 逐项验收签认

- AC-001：BUG-0051独立串行首次产品归档，同轮包装脚本退出0、completed、服务端证明绑定原操作、正式文件与看板done一致。执行期间无宿主治理写入。
- AC-002/003/005/006：93项聚焦测试及6项子测试覆盖身份、失败、摘要漂移、幂等与旧执行隔离、正式同步/check/dry-run差异；合成测试不冒充产品观察。
- AC-004：BUG-0048原轮次恢复，未启动模型或重放归档，原历史步骤保留。
- AC-005/007补充真实观察：BUG-0050首次包装归档成功后遇父任务并发写入注册表漂移，平台正确以archive_issue_not_promoted拒绝；只读check定位两处派生漂移，串行修复并重启服务后收敛done。该样本仅用于拒绝/恢复，不代替BUG-0051首次成功。
- AC-007：1440×900看板完成与Chat完全只读一致；拒绝时保留查看执行入口；刷新及重启恢复证据位于Change evidence/acceptance。

签认：Codex，真实观察与命令回归分别记录；证据入口：`openspec/archive/2026-10-20-fix-archive-wrapper-workflow-sync-proof/evidence/acceptance/`。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-20 08:19:17
accepted_by: workflow-sync
source_change: fix-archive-wrapper-workflow-sync-proof
source_sprint: sprint-010
evidence: [openspec/archive/2026-10-20-fix-archive-wrapper-workflow-sync-proof/evidence/acceptance/20261020001225440659-456da770/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

