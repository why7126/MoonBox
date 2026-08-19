---
change_id: add-space-creation-join-application-flow
status: modified
source_requirement: REQ-0019-space-creation-join-application-flow
created_at: 2026-08-15 11:08:25
updated_at: 2026-08-16 10:15:00
---

# Design: 前台创建空间申请流程

## 1. 验收返修决策

| 决策 | 结论 |
|---|---|
| 前台范围 | 只保留创建空间申请 |
| 删除范围 | 加入空间、精准搜索空间、我的申请列表、撤回、重新提交 |
| 创建行为 | 前台提交待审批申请，平台管理员审批通过后才创建正式空间 |
| 负责人 | 创建弹窗不展示负责人卡；审批通过后申请人成为空间负责人 |
| API 策略 | 复用 `/api/v1/catalog/workspace-applications/create` 路径，返回待审批申请 |
| 单位策略 | 存储空间显示 GB；AI Tokens 输入框不额外展示 `Tokens` 单位，与后台空间管理保持一致 |
| 校验策略 | 成员、存储、AI Tokens 和到期时间默认值/边界与后台空间管理创建表单一致 |

## 2. UI Contract

### 2.1 页面与入口

- 空间切换浮层底部入口文案为“创建空间”。
- 点击入口打开创建空间弹窗。
- 弹窗副标题说明：每个空间对应一个产品，成员与数据相互隔离；提交后进入平台管理员审批，通过后系统会创建空间并分配申请人为负责人。
- 弹窗不得在表单上方重复展示审批提示行。
- 弹窗中不得出现“加入空间”“搜索空间”“申请加入”“我的申请”等入口或状态。

### 2.2 页面结构

```text
CreateSpaceDialog
  ├─ DialogHeader
  ├─ CreateSpaceApplicationForm
  │   ├─ BaseGrid(space_name*, space_code*)
  │   ├─ TextArea(description)
  │   ├─ QuotaGrid(member_limit*, storage_gb*)
  │   ├─ QuotaGrid(ai_tokens*, period_radio*)
  │   ├─ DateTimeRow(expires_at*) when fixed_date
  │   └─ DialogActions(cancel, submit)
  └─ PendingResult
      └─ CloseButton
```

### 2.3 表单规则

- 空间名称：必填，2-80 个字符，红色星号标识。
- 空间标识：必填，2-32 位小写字母、数字或连字符，以小写字母开头，红色星号标识。
- 空间说明：可选，最多 512 个字符，不展示星号。
- 成员上限：默认 20，范围 1-100000，与后台字段 `member_quota` 一致。
- 存储空间：默认 100GB，必须大于 0，与后台字段 `storage_quota_gb` 一致。
- AI Tokens：默认 1000000，必须为不小于 0 的整数，与后台字段 `ai_quota_tokens` 一致，输入框不额外展示 `Tokens` 单位。
- 有效期：默认固定日期。
- 到期时间：默认本季度最后一天 23:59:59，必须晚于当前时间；选择固定日期后在 AI Tokens 下方另起一行展示，并使用与后台空间管理一致的日期时间选择器。

### 2.4 交互规则

- 输入空间名称后自动生成空间标识。
- 用户手动修改空间标识后，名称变化不再覆盖标识。
- 提交中按钮禁用并显示“正在创建...”。
- 提交成功展示“申请已提交”和待审批状态。
- 审批通过前不展示进入空间入口。
- 到期时间选择器打开时必须检测视口剩余空间；下方空间不足且上方空间更充足时向上展开，并优先通过位置调整保持完整展示。
- 到期时间选择器不展示“取消 / 确定”操作；点击 3 个快捷按钮后立即应用并关闭，点击控件外区域关闭并保留当前值，面板自身不得出现滚动条。
- 弹窗右上角关闭按钮必须使用清晰 icon button 样式，包含稳定尺寸、可见边框/背景和 hover/focus 状态。

## 3. 数据模型与 API

请求：

```yaml
create_space_application:
  name: string
  code: string
  description: string | null
  member_quota: integer
  storage_quota_gb: number
  ai_quota_tokens: integer
  expiry_type: long_term | fixed_date
  expires_at: string | null
```

响应：

```yaml
create_space_application_result:
  application: AdminSpaceApplicationRead
```

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/api/v1/catalog/workspace-applications/create` | 前台提交创建空间申请并返回待审批申请 |

## 4. 验证策略

- 后端 pytest 覆盖前台提交待审批申请、申请人/拟负责人、后台一致配额字段、未创建正式空间、join 路由不可用和越界配额拒绝。
- 前端 Vitest/Testing Library 覆盖创建入口、弹窗标题、无加入入口、必填星号、后台一致默认值/限制、AI Tokens 无单位、到期时间控件、名称生成标识、创建提交和待审批结果态。
- UI 返修后重新采集 1440px 视觉证据与 computed style；到期时间选择器需覆盖 1440x900 近底部打开场景。

## 5. Mock/API 边界

- 视觉验收可 mock 创建申请接口响应。
- 生产实现调用真实 API：`/api/v1/catalog/workspace-applications/create`。
- 前台不调用加入空间、精准搜索空间、我的申请、撤回或重新提交接口。
- 后台空间申请审批是正式空间创建的事实源。
