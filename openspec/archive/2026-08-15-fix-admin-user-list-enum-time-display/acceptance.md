---
change_id: fix-admin-user-list-enum-time-display
status: applied
acceptance_status: passed
created_at: 2026-08-15 09:24:03
updated_at: 2026-08-15 10:04:45
---

# Acceptance

## 验收口径

- 角色字段标签化展示。
- 状态字段语义清晰区分。
- 最近登录时间、创建时间、更新时间统一格式化为 `yyyy-mm-dd hh:mm:ss`，空值展示 `—`。
- 用户列表在创建时间后展示更新时间列。
- 用户管理页回归测试覆盖上述行为。

## 验证命令

```bash
pnpm --dir src/web test src/admin-user-management.test.tsx
python scripts/validate-root-cause-evidence.py --bug BUG-0011-admin-user-list-enum-time-display-unclear
```

## 验证结果

- `pnpm --dir src/web test src/admin-user-management.test.tsx`：通过，27 tests passed。
- `openspec validate fix-admin-user-list-enum-time-display`：通过。
- `python scripts/validate-root-cause-evidence.py --bug BUG-0011-admin-user-list-enum-time-display-unclear`：通过，root_cause_status=confirmed，evidence_count=8。
- API、DB、部署、安全、客户端生成：本次未修改，无需同步。

## 验收返修结果

- 2026-08-15 09:56:27：按反馈采用“角色标签去边框、状态标签使用空间管理页状态标签”的方案。
- 第一轮返修角色标签：去除实线边框，保留轻量底色、图标和文本；第二轮返修进一步去除浅底色。
- 状态标签：改为空间管理页同款无边框、彩色图标表达。
- 2026-08-15 10:04:45：继续按反馈采用“用户状态标签对齐空间管理页圆形 check 状态样式；用户角色标签去除浅底色，仅保留图标和彩色文字”的方案。
