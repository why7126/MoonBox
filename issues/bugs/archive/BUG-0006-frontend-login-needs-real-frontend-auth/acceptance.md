---
bug_id: BUG-0006-frontend-login-needs-real-frontend-auth
acceptance_status: passed
created_at: 2026-08-11 23:11:09
updated_at: 2026-08-14 16:29:34
---

# 验收标准

## AC-001 普通前台用户可统一登录并默认进入前台

GIVEN 存在角色为“前台用户”、状态为“正常”的账号
WHEN 用户在 `/login` 输入正确用户名和密码并提交
THEN 登录成功，系统默认进入前台
AND 用户菜单不展示“进入后台”入口
AND 用户无法访问后台页面或后台 API。

## AC-002 待激活用户首次登录后自动激活

GIVEN 存在角色为“前台用户”或“后台管理员”、状态为“待激活”的账号
WHEN 用户在 `/login` 输入正确用户名和密码并提交
THEN 登录成功，系统默认进入前台
AND 该账号状态自动更新为“正常”
AND 后续登录按“正常”账号处理。

## AC-003 后台管理员和超级管理员默认进入前台且可进入后台

GIVEN 存在角色为“后台管理员”的账号，或系统超级管理员账号
WHEN 用户在 `/login` 输入正确用户名和密码并提交
THEN 登录成功，系统默认进入前台
AND 前台用户菜单展示“进入后台”入口
WHEN 用户点击“进入后台”
THEN 系统校验当前用户具备后台权限后进入后台。

## AC-004 冻结、删除和凭证错误用户不得登录

GIVEN 存在状态为“已冻结”或“已删除”的账号，或输入不存在账号/错误密码
WHEN 用户在 `/login` 提交登录
THEN 登录失败
AND 不创建有效服务端会话
AND 不写入有效前端登录态
AND 错误提示为受控登录失败提示，不暴露内部权限实现细节。

## AC-005 前台接口不再依赖后台管理员角色

GIVEN 普通前台用户已经登录
WHEN 访问需求中心前台上下文接口
THEN 接口接受统一登录态并返回该用户可访问的前台上下文
AND 不要求用户具备后台管理员角色。

## AC-006 后台接口保持后台权限边界

GIVEN 普通前台用户已经登录
WHEN 访问后台用户管理、后台认证资料更新、后台上传或其他后台 API
THEN 请求被拒绝
AND 后台接口只允许后台管理员或超级管理员访问。

## AC-007 契约和回归测试同步

GIVEN 修复已完成
WHEN 运行相关后端集成测试和前端登录/需求中心/后台入口测试
THEN 覆盖普通前台用户、后台管理员、超级管理员、待激活自动激活、冻结/删除拒绝、后台入口显隐和后台 API 拒绝路径
AND OpenAPI、API 文档、认证文档与前端调用契约保持一致。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: fix-unified-frontend-login-auth
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

