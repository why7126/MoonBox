---
req_id: REQ-0010-admin-user-menu-password-change
status: archived
created_at: 2026-08-10 08:47:44
updated_at: 2026-08-14 08:45:11
recorded_by: product
source: 用户输入
priority_hint: P1
parent_requirement: REQ-0005-admin-auth-system
captured_via: capture
classification_rationale: 尚未交付的新能力；用户描述为后台管理用户菜单栏新增密码修改入口与流程，不是已有能力偏差。
---

# 一句话

后台管理需要在用户菜单栏提供密码修改功能，支持当前登录用户从个人菜单入口完成账号密码更新。

# 原始描述

后台管理，实现用户菜单栏的密码修改功能。

# 待澄清

- [ ] 入口位置：是否放在管理后台右上角用户菜单，菜单项命名为“修改密码”。
- [ ] 验证策略：修改密码时是否必须输入当前密码，并校验新密码复杂度与确认密码一致性。
- [ ] 会话策略：修改成功后是否保持当前会话，还是强制重新登录。
- [ ] 影响范围：是否仅支持当前登录用户自助修改，不包含管理员为他人重置密码。

# 探索结论

（/req-explore 后人工确认写入）
