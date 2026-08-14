---
bug_id: BUG-0008-admin-users-self-freeze-delete-not-forbidden
acceptance_status: passed
created_at: 2026-08-12 13:51:18
updated_at: 2026-08-14 16:29:34
---

# 验收标准

## AC-001 后端拒绝当前用户冻结自己

- GIVEN 当前登录用户是后台管理员
- AND 目标 `user_id` 等于当前登录用户 ID
- WHEN 调用 `POST /api/v1/admin/users/{user_id}/freeze`
- THEN API MUST 返回 `403 Forbidden`
- AND MUST NOT 修改该用户 `status`
- AND MUST NOT 撤销该用户当前会话

## AC-002 后端拒绝当前用户删除自己

- GIVEN 当前登录用户是后台管理员
- AND 目标 `user_id` 等于当前登录用户 ID
- WHEN 调用 `DELETE /api/v1/admin/users/{user_id}`
- THEN API MUST 返回 `403 Forbidden`
- AND MUST NOT 将该用户 `status` 改为 `已删除`
- AND MUST NOT 设置该用户 `deleted_at`
- AND MUST NOT 撤销该用户当前会话

## AC-003 后端保留其他用户状态操作能力

- GIVEN 当前登录用户是后台管理员
- AND 目标用户不是当前登录用户
- AND 目标用户不是系统内置超级管理员
- WHEN 调用冻结、解冻、删除或重置密码接口
- THEN 既有合法状态流转 SHOULD 保持可用
- AND 既有系统内置超级管理员保护 MUST 保持 `403 Forbidden`

## AC-004 前端当前账号行禁用冻结删除

- GIVEN 管理后台用户管理页面已加载当前登录用户信息
- AND 用户列表包含当前账号
- WHEN 渲染当前账号所在行
- THEN 当前账号行 MUST 保留冻结按钮但置为禁用状态
- AND 当前账号行 MUST 保留删除按钮但置为禁用状态
- AND 禁用态 SHOULD 提供不可冻结/删除当前登录账号的原因
- AND MUST NOT 额外显示“当前账号”文案

## AC-005 前端非当前账号操作保持可用

- GIVEN 用户列表包含其他非系统用户
- WHEN 渲染其他非系统用户所在行
- THEN 编辑、重置密码、冻结或解冻、删除等既有操作 SHOULD 保持可用
- AND 确认弹窗、操作原因校验和 API 调用路径 SHOULD 与既有行为一致

## AC-006 回归测试覆盖

- GIVEN 修复该缺陷
- WHEN 运行后端 API 回归测试
- THEN 应覆盖当前用户自冻结和自删除返回 `403` 的场景
- AND 应覆盖目标用户状态未改变、当前会话仍可使用的断言
- WHEN 运行前端用户管理回归测试
- THEN 应覆盖当前账号行冻结/删除入口不可用
- AND 应覆盖其他用户仍可进入冻结/删除确认流程

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: fix-admin-user-self-freeze-delete-protection
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

