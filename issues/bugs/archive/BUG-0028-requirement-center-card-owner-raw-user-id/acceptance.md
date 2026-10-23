---
bug_id: BUG-0028-requirement-center-card-owner-raw-user-id
title: 需求中心 Capture 卡片负责人名称验收方案
acceptance_status: passed
created_at: 2026-10-08 17:53:55
updated_at: 2026-10-20 08:19:17
owner: 产品团队
---

# 需求中心 Capture 卡片负责人名称验收方案

## 验收范围与契约

昵称 → 用户名 → 未知用户；空 owner 为未分配；历史可读团队名称保留。测试使用隔离运行的真实产品与合成账号，原用户部署没有升级或验收通过声明。

## 逐项证据

- [x] AC-001：昵称优先；单元/API及实际 REQ Capture 观察通过。
- [x] AC-002：仅用户名的安全名称回退；单元与组件回归通过。
- [x] AC-003：空值、未知/删除/越权身份安全回退；单元/API通过。
- [x] AC-004：产品、中文团队和历史文本保留；单元与组件通过。
- [x] AC-005：实际 REQ/BUG Capture confirm、writer、首次 context 及浏览器刷新一致。
- [x] AC-006：卡片/title/详情名称一致；同名筛选结合搜索和刷新实测通过；项目切换由组件回归覆盖。
- [x] AC-007：1440×900/390×844、深浅主题长名称截图与样式签认通过。原反馈视口未知，390px 仅作补充，缺口明确保留；不宣称精确原视口复验。
- [x] AC-008：管理员/查看者读取、查看者禁止写、未登录401、未授权403和空间内目录范围回归通过。

证据入口：[修复验证记录](../../../../openspec/archive/2026-10-19-fix-requirement-center-owner-display/verification.md)、[逐项计划](../../../../openspec/archive/2026-10-19-fix-requirement-center-owner-display/acceptance-plan.json)。产品样本见同 Change 的 evidence/acceptance/product-capture.json，交互与视觉签认见 owner-interactions.json、visual/；正式验收结果由完整报告与 Workflow Sync 回填。

## 数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: [api, web, database_read, openapi_client]

reason: 增加 context 安全展示字段并读取已有目录；没有新增日志、事件、Task Trace、请求封装、对象存储或保留策略，以上 N/A。

validation: 后端5项、组件139项、类型与构建及隔离产品观察通过；不把合成阶段样本解释为真实工作流迁移。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-20 08:19:17
accepted_by: workflow-sync
source_change: fix-requirement-center-owner-display
source_sprint: sprint-010
evidence: [openspec/archive/2026-10-19-fix-requirement-center-owner-display/evidence/acceptance/20261019111809882807-12c80472/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

