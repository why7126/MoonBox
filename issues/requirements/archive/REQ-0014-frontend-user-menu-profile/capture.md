---
req_id: REQ-0014-frontend-user-menu-profile
status: archived
created_at: 2026-08-11 16:04:37
updated_at: 2026-08-13 22:44:04
recorded_by: product
source: 用户输入
priority_hint: P1
parent_requirement: REQ-0012-frontend-requirement-center
---

# 一句话

在前台需求中心用户菜单中实现个人资料弹窗，仅支持修改头像和昵称，保存后同步刷新前台用户菜单展示和当前用户上下文。

# 原始描述

前台用户菜单栏个人资料功能：在前台需求中心用户菜单中实现个人资料弹窗，仅支持修改头像和昵称，保存后刷新前台用户菜单展示和当前用户上下文；头像上传复用现有对象存储链路，前台视觉保持现有 rc-* UI/UE，不包含密码修改和后台用户管理。

# 待澄清

- [ ] 昵称字段校验规则：长度、允许字符、是否允许为空。
- [ ] 头像上传限制：文件类型、大小上限、裁剪/压缩策略、默认头像回退规则。
- [ ] 保存失败与上传失败时的前台提示文案和回滚策略。

# 探索结论

（/req-explore 后人工确认写入）
