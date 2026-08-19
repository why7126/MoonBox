---
change_id: add-space-creation-join-application-flow
type: add
status: proposed
source_requirement: REQ-0019-space-creation-join-application-flow
sprint: sprint-003
created_at: 2026-08-15 11:08:25
updated_at: 2026-08-15 11:08:25
---

# Proposal: 新增前台空间创建与加入申请流程

## 背景

MoonBox 已通过后台空间管理能力提供空间申请审批、通过后创建空间与同名产品、拒绝、通知和审计。前台当前仅有空间切换入口与真实数据接入规划，缺少普通用户发起创建空间申请、精准搜索已有空间并申请加入、查看申请状态、撤回和拒绝后重提的完整流程。

## 目标

- 在前台提供空间申请中心，覆盖创建空间申请、精准搜索加入空间申请和我的申请列表。
- 创建空间必须进入后台审批流程，审批通过前不得生成正式空间或产品绑定。
- 加入空间首版仅支持完整空间名称或唯一标识的精准搜索，不提供模糊发现、邀请码、邀请链接或公开空间目录。
- 申请状态覆盖待审批、通过、拒绝、撤回，并支持撤回和拒绝后修改重提。
- 审批通过后与空间切换真实数据能力联动，使用户可看到新增可访问空间。

## 非目标

- 不重做后台申请审批页面；后台审批继续复用 `web-admin-space-management` 的空间申请审批能力。
- 不实现邀请码、邀请链接、公开空间目录、推荐空间列表或后台主动邀请用户加入空间。
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
capabilities:
  new:
    - 前台空间申请中心
    - 创建空间申请提交
    - 加入空间精准搜索与申请
    - 当前用户申请列表、撤回和重新提交
  modified:
    - 前台空间切换入口需要跳转或打开申请中心
    - 后台审批结果需要驱动前台申请状态与空间切换刷新
```

## 依赖

- `REQ-0017-admin-space-management`：后台审批、通过后创建空间和产品绑定、拒绝、通知与审计。
- `REQ-0018-frontend-space-switcher-real-data`：用户可访问空间列表与切换刷新。
- 原型驱动 UI Gate：`docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`。
