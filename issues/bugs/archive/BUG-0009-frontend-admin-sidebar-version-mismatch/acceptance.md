---
bug_id: BUG-0009-frontend-admin-sidebar-version-mismatch
acceptance_status: passed
created_at: 2026-08-12 14:19:01
updated_at: 2026-08-14 16:29:34
---

# 验收标准

## AC-001 统一版本事实源

WHEN 打开前台需求中心与管理后台用户管理页  
THEN 两个侧边栏品牌区域展示的产品版本号 MUST 一致。

## AC-002 后台移除独立硬编码版本

WHEN 检查后台用户管理页侧边栏实现  
THEN 不应继续保留独立硬编码的 `v1.0.5`，应复用共享版本事实源或等价统一版本入口。

## AC-003 回归测试覆盖后台版本展示

WHEN 运行前端相关测试  
THEN 后台用户管理页测试 MUST 覆盖侧边栏版本号展示，且前台与后台期望版本一致。

## AC-004 影响边界保持不变

WHEN 完成修复并回归  
THEN 不应引入后端 API、数据库、权限、部署拓扑或客户端生成变更。

## 建议验证命令

```bash
pnpm --dir src/web test
```

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: fix-frontend-admin-sidebar-version-mismatch
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

