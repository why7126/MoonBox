---
req_id: REQ-0005-admin-auth-system
status: archived
created_at: 2026-08-07 23:23:55
updated_at: 2026-08-08 22:46:23
recorded_by: product
source: 用户输入
priority_hint: P1
parent_requirement:
---

# 管理后台登录认证系统

新增管理后台登录认证系统，支持超级管理员账号密码登录、Token/Session、退出登录和后台路由守卫。

# 原始描述

新增管理后台登录认证系统，支持超级管理员账号密码登录、Token/Session、退出登录和后台路由守卫。

# 待澄清

- [ ] 超级管理员账号的初始化方式：环境变量、种子数据、安装向导或后台手动创建。
- [ ] Token/Session 的具体策略：JWT、服务端 Session、刷新机制、过期时长与 Remember me 行为。
- [ ] 后台路由守卫范围：仅前端路由拦截，还是同时要求后端管理 API 权限校验。
- [ ] 退出登录是否需要服务端失效 Token/Session，以及多端登录是否互踢。
- [ ] 登录失败、锁定、审计日志、密码策略和安全告警是否纳入本期范围。

# 探索结论

（/req-explore 后人工确认写入）
