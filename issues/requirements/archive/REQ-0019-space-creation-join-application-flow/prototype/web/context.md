---
requirement_id: REQ-0019-space-creation-join-application-flow
title: 前台创建空间申请原型拆解
status: modified
created_at: 2026-08-15 10:48:11
updated_at: 2026-08-15 14:31:00
---

# Prototype Context

## 页面与 DOM

| 页面/状态 | DOM | 组件 |
|---|---|---|
| 原业务页面 | `#app-shell` | Sidebar、UserMenu |
| 切换空间浮层 | `#space-popover` | SpaceOption、CreateEntry |
| 创建空间弹窗 | `#space-modal` | Dialog、Toast |
| 创建表单 | `#create-view` | TextField、QuotaField、PeriodRadio、DateRow |
| 结果态 | `#success-view` | PendingResult、PrimaryButton |

## 数据模型

```ts
type CreateSpaceApplicationPayload = {
  name: string;
  code: string;
  description?: string;
  member_quota: number;
  storage_quota_gb: number;
  ai_quota_tokens: number;
  expiry_type: "long_term" | "fixed_date";
  expires_at?: string;
};
```

## 字段与接口

| 字段 | 数据 | 接口预期 |
|---|---|---|
| 名称/标识 | `name` / `code` | 创建前校验名称和标识唯一性 |
| 成员上限 | `member_quota` | 默认 20，1-100000，与后台空间管理一致 |
| 存储空间 | `storage_quota_gb` | 默认 100GB，大于 0，与后台空间管理单位一致 |
| AI Tokens | `ai_quota_tokens` | 默认 1000000，不小于 0，输入框不额外展示 `Tokens` 单位 |
| 有效期 | `expiry_type` / `expires_at` | 默认固定日期；到期时间默认本季度最后一天 23:59:59 |
| 创建 | `CreateSpaceApplicationPayload` | 前台提交待审批创建空间申请 |

## 状态矩阵

| 场景 | 状态 | UI 表达 |
|---|---|---|
| 创建弹窗 | 默认 | 展示完整创建申请表单和审批说明 |
| 必填项 | 默认 | 除空间说明外展示红色星号 |
| 名称输入 | 自动生成标识 | 空间标识随名称生成 |
| 标识手动修改 | 用户覆盖 | 后续名称变化不再覆盖标识 |
| 固定日期 | 展开日期时间选择器 | 到期时间在 AI Tokens 下方另起一行 |
| 创建提交 | loading | 按钮禁用并显示“正在创建...” |
| 提交成功 | pending | 展示申请已提交和待审批说明 |
| 创建失败 | error | 展示错误提示 |

## Mock/API 边界

- 返修后的生产实现不得展示或调用加入空间、精准搜索空间或我的申请列表。
- 视觉验收可 mock 创建申请接口响应；运行时创建必须调用真实后端创建空间申请接口。
- 审批通过前不创建正式空间，不展示进入空间入口。
