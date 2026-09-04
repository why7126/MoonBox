---
change_id: optimize-workflow-sync-issue-output-next
type: update
status: proposed
created_at: 2026-08-27 08:02:44
updated_at: 2026-08-27 08:02:44
---

# 优化 Workflow Sync Issue 输出与 next 推导

## 背景

Workflow Sync 已负责同步 Issue 主文档、验收文档、registry、trace、Sprint 四件套和当前态看板。使用中有两个治理体验问题：

- `--apply-issue-subdocuments` 的 summary 输出只提供聚合计数，不便直接确认正文状态块与验收块本轮实际应用了哪些字段。
- `/req-opsx` 或 `/bug-opsx` 创建 Change 后，同一轮 sync 可能仍使用回填前的 Issue 派生态刷新当前态看板，导致 `下一步` 继续提示 `/req-opsx` 或 `/bug-opsx`。

## 目标

- 让子文档 apply 的 summary 输出包含更新文件数、字段数、验收状态和安全同步项。
- 让 `req.opsx` / `bug.opsx` 同轮回填 Change 后，当前态看板 `下一步` 推导进入 `/opsx-apply <REQ-full-id>` 或 `/opsx-apply <BUG-full-id>`。
- 补充聚焦单元测试，固定这两个回归点。

## 非目标

- 不修改业务 `src/` 代码、API、数据库、Web、管理后台或客户端实现。
- 不改变 REQ/BUG 生命周期状态机。
- 不扩大对子文档语义不明 `status` 字段的自动改写范围。

## 影响范围

```yaml
impact:
  backend: false
  web: false
  miniapp: false
  admin: false
  database: false
  storage: false
  api: false
  governance: true
```
