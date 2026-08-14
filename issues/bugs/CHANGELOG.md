---
purpose: 缺陷当前态看板索引
content: 每个 BUG 一行记录当前状态、下一步和事实源路径
created_at: 2026-08-10 08:59:32
updated_at: 2026-08-13 22:51:29
owner: MoonBox 产品团队
---

# 缺陷当前态看板索引

本文件用于快速浏览 BUG 当前状态、阶段、关联 Sprint、关联 Change、下一步和事实源路径。

完整事实源仍以各 BUG 目录内 `trace.md`、`issues/bugs/_registry.yaml`、OpenSpec Change、Sprint 四件套和正式规格为准；本文件只做目录级看板入口，不记录完整生命周期流水。

## 维护规则

- 每个 BUG 保留一行当前态快照；状态、阶段、严重等级、关联 Sprint、关联 Change 或下一步变化时更新对应行。
- 新建 BUG 时新增行；归档后保留行，并将下一步写为“无”或归档后的复盘建议。
- 不复制 `trace.md` 的完整变更记录、复现日志原文、截图个人信息、根因全文或 workaround 全文。
- 普通文案润色、格式调整、错别字修复、非状态性验收措辞调整 MAY 不更新本文件。
- 如本文件与事实源不一致，必须以事实源为准，并通过 Workflow Sync 或 `trace.fix` 类治理动作修正快照。

## 安全边界

本文件不得写入用户隐私数据、真实客户数据、密钥、访问令牌、未脱敏日志、订单原文、聊天原文、工单原文、截图中的个人信息、本机绝对路径、系统用户名或用户主目录。

## 当前态看板

| BUG | 标题 | 严重等级 | 当前状态 | 阶段 | 关联 Sprint | 关联 Change | 最近更新时间 | 下一步 | 事实源 |
|---|---|---|---|---|---|---|---|---|---|
| BUG-0011-admin-user-list-enum-time-display-unclear | 用户管理列表枚举标签与时间字段展示不清晰 | medium | approved | review | - | - | 2026-08-13 09:36:01 | `/sprint-propose --bug BUG-0011-admin-user-list-enum-time-display-unclear` | `issues/bugs/review/BUG-0011-admin-user-list-enum-time-display-unclear/trace.md` |
| BUG-0010-admin-user-actions-validation-no-feedback | 用户管理编辑保存与确认操作缺少校验反馈 | high | done | archive | sprint-002 | fix-admin-user-actions-validation-feedback | 2026-08-13 22:49:07 | 无 | `issues/bugs/archive/BUG-0010-admin-user-actions-validation-no-feedback/trace.md` |
| BUG-0009-frontend-admin-sidebar-version-mismatch | 前台与后台侧边栏版本号不一致 | medium | done | archive | sprint-002 | fix-frontend-admin-sidebar-version-mismatch | 2026-08-13 22:40:16 | 无 | `issues/bugs/archive/BUG-0009-frontend-admin-sidebar-version-mismatch/trace.md` |
| BUG-0008-admin-users-self-freeze-delete-not-forbidden | 管理后台登录用户不能冻结和删除自己 | high | done | archive | sprint-002 | fix-admin-user-self-freeze-delete-protection | 2026-08-13 22:41:26 | 无 | `issues/bugs/archive/BUG-0008-admin-users-self-freeze-delete-not-forbidden/trace.md` |
| BUG-0007-docker-media-upload-acceptance-hardcodes-3000-port | Docker 媒体上传横切验收依赖固定端口和默认管理员密码 | high | done | archive | sprint-002 | fix-docker-media-upload-acceptance-gate | 2026-08-13 22:51:12 | 无 | `issues/bugs/archive/BUG-0007-docker-media-upload-acceptance-hardcodes-3000-port/trace.md` |
| BUG-0006-frontend-login-needs-real-frontend-auth | 前台登录入口缺少真正前台用户认证能力 | high | done | archive | sprint-002 | fix-unified-frontend-login-auth | 2026-08-13 22:51:29 | 无 | `issues/bugs/archive/BUG-0006-frontend-login-needs-real-frontend-auth/trace.md` |
| BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin | 从后台返回前台时用户菜单显示未登录 | medium | done | archive | sprint-002 | fix-frontend-user-menu-session-state | 2026-08-13 22:45:09 | 无 | `issues/bugs/archive/BUG-0005-frontend-user-menu-shows-logged-out-after-returning-from-admin/trace.md` |
| BUG-0004-frontend-user-menu-change-password-not-implemented | 前台用户菜单栏修改密码入口未实现 | medium | done | archive | sprint-002 | fix-frontend-user-menu-change-password | 2026-08-13 22:48:26 | 无 | `issues/bugs/archive/BUG-0004-frontend-user-menu-change-password-not-implemented/trace.md` |
| BUG-0003-homepage-start-moonbox-should-open-login-route | 官网开启 MoonBox 应进入 /login 独立登录页 | medium | done | archive | sprint-002 | fix-homepage-login-route | 2026-08-13 22:49:27 | 无 | `issues/bugs/archive/BUG-0003-homepage-start-moonbox-should-open-login-route/trace.md` |
| BUG-0002-homepage-frontend-login-entry-routes-to-admin | 首页前台登录入口误跳后台登录页 | high | done | archive | sprint-002 | fix-homepage-frontend-login-entry-routes-to-admin | 2026-08-13 23:04:21 | 无 | `issues/bugs/archive/BUG-0002-homepage-frontend-login-entry-routes-to-admin/trace.md` |
| BUG-0001-admin-web-login-api-proxy-and-spa-fallback | Docker Web 管理后台登录 API 误路由且缺少 SPA fallback | high | done | archive | sprint-002 | fix-admin-web-login-api-proxy-and-spa-fallback | 2026-08-13 22:45:09 | 无 | `issues/bugs/archive/BUG-0001-admin-web-login-api-proxy-and-spa-fallback/trace.md` |
