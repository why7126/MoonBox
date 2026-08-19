---
requirement_id: REQ-0019-space-creation-join-application-flow
title: 前台创建空间流程
owner: product
source: acceptance-feedback
acceptance_status: pending
created_at: 2026-08-15 10:48:11
updated_at: 2026-08-16 11:48:57
---

# 验收标准

## 功能 AC

- [x] AC-001 前台从空间切换浮层提供“创建空间”入口，不展示“加入空间”入口或标签。
- [x] AC-002 弹窗副标题说明每个空间对应一个产品、成员与数据相互隔离、提交后进入平台管理员审批，以及审批通过后系统会创建空间并分配申请人为负责人；表单上方不重复展示审批提示行。
- [x] AC-003 创建表单包含空间名称、空间标识、空间说明、成员上限、存储空间、AI Tokens 和有效期。
- [x] AC-004 除空间说明外，必填项均展示红色星号。
- [x] AC-005 空间名称输入后自动生成空间标识；用户手动修改标识后，后续名称变化不得覆盖该字段。
- [x] AC-006 成员上限默认 20，仅接受 1-100000 的整数，与后台空间管理一致。
- [x] AC-007 存储空间默认 100GB，仅接受大于 0 的数值，单位 GB 与后台空间管理一致。
- [x] AC-008 AI Tokens 默认 1000000，仅接受不小于 0 的整数；输入框不额外展示 `Tokens` 单位。
- [x] AC-009 有效期默认固定日期；到期时间默认本季度最后一天 23:59:59，必须晚于当前时间，并使用与后台空间管理一致的日期时间选择器展示于 AI Tokens 下方。
- [x] AC-010 提交成功后生成待审批创建空间申请，不直接创建可进入空间。
- [x] AC-011 结果态展示待审批状态和“待平台管理员审批后才可使用”的说明。
- [x] AC-012 不提供邀请码、搜索空间、申请加入、我的申请、撤回或重新提交能力。

## UI AC

- [x] AC-UI-001 创建弹窗符合返修后结构：Header、CreateForm、QuotaField、PeriodRadio、DateTimeRow、SuccessView；审批说明整合在 Header 副标题中。
- [x] AC-UI-002 表单在 1440px 桌面视口双列可读，配额、有效期、到期时间和底部操作不重叠。
- [x] AC-UI-003 创建弹窗不展示负责人卡。
- [x] AC-UI-004 主按钮使用 MoonBox 克制金色强调，提交中和成功态反馈清晰。
- [x] AC-UI-005 到期时间选择器在 1440x900 视口打开时不得超出可视区域，必要时向上展开或在视口内限位，确保可完成选择。
- [x] AC-UI-006 到期时间选择器不展示“取消 / 确定”操作；点击 3 个快捷按钮后立即应用并关闭，点击控件外区域关闭并保留当前值；面板不得出现自身滚动条。
- [x] AC-UI-007 弹窗右上角关闭按钮必须清晰可见，具备稳定尺寸、边框/背景和 hover/focus 状态。

## 验收结果回填

```yaml
acceptance_status: pending
accepted_at: null
accepted_by: null
source_change: add-space-creation-join-application-flow
source_sprint: sprint-003
evidence: []
failed_items: []
source_event: opsx.modify
notes: 待验收；由 opsx.apply 标记，后续 archive 时回填结论。
```

