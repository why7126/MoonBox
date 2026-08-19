---
change_id: fix-admin-user-list-enum-time-display
status: applied
created_at: 2026-08-15 09:24:03
updated_at: 2026-08-15 10:04:45
---

# Tasks

- [x] 1. 更新用户管理列表渲染
  - [x] 1.1 为角色列增加标签化展示。
  - [x] 1.2 为状态列增加清晰语义标签、图标或状态样式映射。
  - [x] 1.3 增加统一时间格式化函数，覆盖最近登录时间、创建时间、更新时间。
  - [x] 1.4 在创建时间后增加更新时间列，并同步 `colgroup`、表格宽度和横向滚动密度。
- [x] 2. 补充回归测试
  - [x] 2.1 更新用户列表列头和首行单元格断言。
  - [x] 2.2 覆盖更新时间列、角色标签、状态语义和空时间展示。
  - [x] 2.3 覆盖 ISO 字符串和已格式化字符串输入的时间展示。
- [x] 3. 验证
  - [x] 3.1 运行 `pnpm --dir src/web test src/admin-user-management.test.tsx`。
  - [x] 3.2 运行 `python scripts/validate-root-cause-evidence.py --bug BUG-0011-admin-user-list-enum-time-display-unclear`。
  - [x] 3.3 确认无需同步 API、DB、部署、安全或客户端生成。
- [x] 4. 知识沉淀判断
  - [x] 4.1 已复核 `docs/knowledge-base/best-practices/admin-list-page-consistency.md`；本次沿用既有后台列表一致性 gate，无需新增独立 incident。

## 验收返修记录

### 2026-08-15 09:56:27

- 反馈：用户管理列表中角色候选项标签边框视觉噪声偏高；状态标签应使用空间管理页同款状态标签表达。
- 调整：角色标签去除实线边框，保留轻量底色、图标和文字；用户状态标签改为与空间管理页一致的无边框、无底色、彩色图标语义表达。
- 验证：更新 `src/web/src/admin-user-management.test.tsx` 的 CSS 保护断言，并重新运行聚焦前端测试、OpenSpec strict 校验和根因证据 gate。

### 2026-08-15 10:04:45

- 反馈：用户状态标签仍需对齐空间管理页圆形 check 状态样式；用户角色标签不保留浅底色。
- 调整：用户状态「正常」图标切换为与空间管理页一致的 `CheckCircle2` 圆形 check；角色标签去除专属浅底色，仅保留图标和彩色文字。
- 验证：补充角色无背景与用户状态图标来源的测试断言，并重新运行聚焦前端测试、OpenSpec strict 校验、根因证据 gate、文档 diff 检查。
