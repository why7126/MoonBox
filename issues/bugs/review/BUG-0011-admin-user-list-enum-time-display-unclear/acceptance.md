---
bug_id: BUG-0011-admin-user-list-enum-time-display-unclear
acceptance_status: not_started
created_at: 2026-08-13 09:32:22
updated_at: 2026-08-13 09:36:40
---

# 验收标准

## AC-BUG-0011-001 角色以标签形式展示

WHEN 管理员进入用户管理页并查看用户列表
THEN 角色列 MUST 使用标签化视觉样式展示「后台管理员」和「前台用户」
AND 不得仅以普通纯文本单元格展示角色枚举值。

## AC-BUG-0011-002 状态语义清晰区分

WHEN 用户列表中存在「待激活」「正常」「已冻结」或「已删除」状态用户
THEN 状态列 MUST 通过明显的标签语义、图标或可区分样式表达不同状态
AND 「已冻结」与「已删除」不得仅依赖同一类红色小圆点造成语义接近。

## AC-BUG-0011-003 时间字段统一格式

WHEN 用户列表展示最近登录时间、创建时间和更新时间
THEN 有值时间 MUST 统一展示为 `yyyy-mm-dd hh:mm:ss`
AND 空值 MUST 展示为 `—`
AND ISO 字符串和已格式化字符串输入都不得破坏列表展示。

## AC-BUG-0011-004 更新时间列可见

WHEN 用户列表接口返回 `updated_at`
THEN 用户列表 MUST 在创建时间后展示「更新时间」列
AND 该列 MUST 使用与其他时间列一致的格式化策略。

## AC-BUG-0011-005 回归测试覆盖

WHEN 修复完成
THEN `src/web/src/admin-user-management.test.tsx` MUST 覆盖用户列表列头、角色标签、状态语义、最近登录时间、创建时间和更新时间展示
AND 相关测试 MUST 通过。

## 建议验证命令

```bash
pnpm --dir src/web test src/admin-user-management.test.tsx
```

## 验收结果回填

```yaml
acceptance_status: not_started
accepted_at: null
accepted_by: null
source_change: null
source_sprint: null
evidence: []
failed_items: []
source_event: bug.review
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

