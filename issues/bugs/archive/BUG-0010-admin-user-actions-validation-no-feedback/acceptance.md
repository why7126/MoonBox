---
bug_id: BUG-0010-admin-user-actions-validation-no-feedback
acceptance_status: passed
created_at: 2026-08-13 09:29:45
updated_at: 2026-08-14 16:29:34
---

# 验收标准

## AC-BUG-0010-01 编辑态不受用户名校验静默阻断

Given 管理员打开用户管理页某个已有用户的编辑弹窗  
When 该用户用户名不满足当前新增用户正则，但管理员只修改昵称、头像或角色  
Then 点击「保存」应正常触发用户更新请求，或在保存失败时展示明确后端/前端错误  
And 不得因为不可编辑的用户名字段静默禁用保存按钮

## AC-BUG-0010-02 新增态仍保留用户名校验

Given 管理员打开新增用户弹窗  
When 用户名为空、长度不足、非字母开头或包含非法字符  
Then 保存应被阻断并展示“请输入 4-32 位字母或数字，且以字母开头。”等明确错误  
And 合法用户名仍可继续创建用户

## AC-BUG-0010-03 操作原因空值有可见反馈

Given 管理员打开重置密码、冻结、解冻或删除确认弹窗  
When 操作原因为空或只包含空白字符  
Then 点击「确认」后应在弹窗内展示“操作原因至少需要 4 个字。”或等价错误提示  
And 错误提示应使用 `.admin-form-error` 或同等错误样式
And “操作原因”标签应展示红色 `*` 必填标识，且 `*` 应紧跟字段名同一行展示

## AC-BUG-0010-04 操作原因不足 4 字仍有可见反馈

Given 管理员打开重置密码、冻结、解冻或删除确认弹窗  
When 操作原因少于 4 个字符  
Then 页面应展示明确错误提示  
And 不应调用对应重置密码、冻结、解冻或删除 API

## AC-BUG-0010-05 合法操作原因保持成功路径

Given 管理员打开重置密码、冻结、解冻或删除确认弹窗  
When 操作原因不少于 4 个字符  
Then 点击「确认」应调用对应 API  
And 成功后应关闭确认弹窗并展示既有成功反馈或临时密码弹窗

## AC-BUG-0010-06 回归测试

Then 前端测试应覆盖：

- 编辑已有异常用户名用户时，可保存昵称、头像或角色等可编辑字段。
- 空操作原因点击确认时展示错误提示。
- 短操作原因不调用 API 且展示错误提示。
- 重置密码、冻结、解冻、删除确认弹窗的操作原因均展示必填标识，且红星与字段名同一行展示。
- 合法操作原因仍保持原有成功流程。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: fix-admin-user-actions-validation-feedback
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

