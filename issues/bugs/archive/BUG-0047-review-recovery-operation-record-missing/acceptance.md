---
bug_id: BUG-0047-review-recovery-operation-record-missing
title: 评审恢复记录缺失导致成果未应用与卡片未流转验收标准
created_at: '2026-10-19 14:28:26'
updated_at: 2026-10-20 08:19:18
acceptance_status: passed
---

# 评审恢复记录缺失导致成果未应用与卡片未流转验收标准

## 验收范围

实现验收已执行，逐项证据见关联 Change 的 verification.md 与 evidence/acceptance；根因探针不计为修复通过。每项保存脱敏命令结果或产品证据，并关联版本、对象、轮次及应用结果。测试使用隔离项目，不破坏真实用户评审。

- [x] AC-001 动作契约：req-review 与 bug-review 的 baseline/operation 初始化、预检、收尾契约一致；名单外动作明确处理，覆盖已支持候选命令的适用矩阵。
- [x] AC-002 正常评审：通过真实产品入口生成评审成果，后端校验、迁移、同步及回读成功；事实源 approved/review、应用记录与看板一致，原有子文档完整。
- [x] AC-003 缺失与损坏：baseline-only、缺失 operation、非法内容均有明确前置或恢复诊断，不消耗完整模型轮次后才暴露已知准备问题；不伪造成功。
- [x] AC-004 中断兼容：准备写入中断、旧版记录、服务重启后保持成果与基线；只有证据充足才恢复，否则明确阻断，不补空文件绕过。
- [x] AC-005 幂等边界：应用成功但响应丢失、重复核查或恢复不重复迁移、不重复生成评审/应用记录；保留原失败轮次事实。
- [x] AC-006 并发与权限：同对象并发变化、权限收回、项目绑定变化时拒绝过期或越权应用，不覆盖新成果。
- [x] AC-007 诊断与展示：原始阻断原因、阶段及关联任务可追溯；不统一误报执行器不可用。按 REQ-0046 的展示契约，不让助手成功措辞覆盖业务拒绝事实；无可用恢复能力不显示虚假入口。
- [x] AC-008 部署验证：backend、worker、controller 相关动作契约及部署版本经过核对，正式产物包含已验证改动；仅工作区修改不算完成。
- [x] AC-009 关联回归：保留 BUG-0044 的完成门禁、对象互斥和会话连续性；其他治理命令与普通对话不被错误恢复检查阻断，适用与 N/A 逐项说明。

## 证据分层

合成回归覆盖 AC-001、003、004、005、006 的异常分支；真实隔离产品轮次覆盖 AC-002、007、008、009。浏览器检查应覆盖刷新、重连和业务完成/展示同步失败区分；所有步骤注明命令测试或真实观察，不用单元测试替代完整评审应用。

## 数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: API、请求日志、Task Trace、轮次/候选/应用与 Web 状态反馈。

validation: 核对失败阶段、原始错误、操作身份和可信版本的关联；不记录完整 Prompt、凭证或个人标识。已同步 API 诊断说明；无 API/DB schema、安全策略、对象存储或客户端生成变化。受控隔离部署已验证，原业务部署未升级。REQ 中断恢复与 BUG 正常完成分别取证，原终态保留。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-20 08:19:18
accepted_by: workflow-sync
source_change: fix-review-recovery-operation-record-missing
source_sprint: sprint-010
evidence: [openspec/archive/2026-10-19-fix-review-recovery-operation-record-missing/evidence/acceptance/20261019153058472542-5b217550/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

