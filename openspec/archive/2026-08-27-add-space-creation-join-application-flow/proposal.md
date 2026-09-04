---
change_id: add-space-creation-join-application-flow
type: add
status: modified
source_requirement: REQ-0019-space-creation-join-application-flow
sprint: sprint-003
created_at: 2026-08-15 11:08:25
updated_at: 2026-08-27 09:20:00
---

# Proposal: 新增前台创建空间申请流程

## 背景

MoonBox 已通过后台空间管理能力提供空间申请审批、通过后创建空间与同名产品、拒绝、通知和审计。前台当前仅有空间切换入口与真实数据接入规划，缺少普通用户发起创建空间申请的入口和待审批反馈。

## 目标

- 在前台空间切换上下文提供“创建空间”入口。
- 打开创建空间弹窗，采集空间名称、标识、说明、成员上限、存储空间、AI Tokens 和有效期。
- 创建空间必须进入后台审批流程，审批通过前不得生成正式空间或产品绑定。
- 审批通过后后台创建正式空间并分配申请人为负责人，后续空间切换真实数据能力刷新可访问空间。

## 非目标

- 不重做后台申请审批页面；后台审批继续复用 `web-admin-space-management` 的空间申请审批能力。
- 不实现加入空间、精准搜索空间、我的申请列表、撤回、拒绝后重新提交、邀请码、邀请链接、公开空间目录、推荐空间列表或后台主动邀请用户加入空间。
- 不实现自动过期、批量审批、批量撤回或批量重新提交。
- 不改变空间与产品一对一绑定、配额、冻结、回收和审计规则。

## 影响范围

```yaml
impact:
  backend: true
  web: true
  miniapp: false
  admin: false
  database: true
  storage: false
  api: true
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: "本 Change 复用既有空间申请 API 与 admin_space_applications 表，仅新增前台创建申请入口和字段校验，不新增或修改 usage_events、request_logs、task_traces、task_trace_spans、请求日志字段、行为埋点、Task Trace 或客户端请求封装。"
  validation: "归档前复核 docs/standards/product-data-collection-observability.md；API/DB 长期文档已同步创建空间申请语义，未涉及观测层 schema 或采集链路。"
capabilities:
  new:
    - 创建空间申请提交
  modified:
    - 前台空间切换入口打开创建空间弹窗
    - 后台审批结果需要驱动前台申请状态与空间切换刷新
```

## 依赖

- `REQ-0017-admin-space-management`：后台审批、通过后创建空间和产品绑定、拒绝、通知与审计。
- `REQ-0018-frontend-space-switcher-real-data`：用户可访问空间列表与切换刷新。
- 原型驱动 UI Gate：`docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`。
