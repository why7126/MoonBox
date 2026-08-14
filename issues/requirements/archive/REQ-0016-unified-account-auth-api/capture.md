---
req_id: REQ-0016-unified-account-auth-api
status: archived
created_at: 2026-08-12 00:11:02
updated_at: 2026-08-13 22:49:22
recorded_by: product
source: explore
priority_hint: P1
parent_requirement:
---

# 一句话

统一账号认证与个人中心 API，使用 `/api/v1/auth/*` 作为唯一正式路径，并消除 `admin/auth` 命名和前后台双 session 存储造成的边界混淆。

# 原始描述

统一账号认证与个人中心 API，消除 admin/auth 命名和前后台双 session 存储造成的边界混淆。

新增 `/api/v1/auth/*`，不保留旧路径。

# 待澄清

- [ ] 确认旧 `/api/v1/admin/auth/*` 路径是否直接删除，以及是否接受一次性破坏性迁移对前端、测试、OpenAPI 和客户端生成物的影响。
- [ ] 明确 `/api/v1/auth/me` 与个人资料更新是否面向所有登录用户，还是仍限制后台管理员可编辑头像和昵称。
- [ ] 明确前端是否统一为单一 `moonbox.session` 存储，并迁移前台需求中心与管理后台的会话读取逻辑。

# 探索结论

后端当前实际复用同一组 `/api/v1/admin/auth/*` 接口，前台需求中心也使用同一 Bearer token；问题主要来自路径命名仍带 `admin`，以及前端存在 `moonbox.admin.session` 与 `moonbox.frontend.session` 两套存储，造成能力边界和开发认知混淆。
