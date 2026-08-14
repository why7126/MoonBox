---
bug_id: BUG-0009-frontend-admin-sidebar-version-mismatch
status: done
created_at: 2026-08-12 14:12:57
updated_at: 2026-08-13 22:40:22
severity_hint: medium
environment: local
related_requirement:
related_bug:
---

# 现象

前台与后台侧边栏展示的产品版本号不一致：前台显示 `v0.1.0`，后台显示 `v1.0.5`。

# 复现步骤

1. 打开 MoonBox 前台需求中心侧边栏。
2. 观察品牌区域版本号，显示为 `v0.1.0`。
3. 打开 MoonBox 管理后台用户管理页侧边栏。
4. 观察品牌区域版本号，显示为 `v1.0.5`。

# 期望 vs 实际

- 期望：前台与后台侧边栏使用同一产品版本事实源，并展示一致的版本号。
- 实际：前台通过共享版本常量展示 `v0.1.0`，后台侧边栏存在硬编码 `v1.0.5`，导致用户看到不一致的发布版本。

# 附件

无。
