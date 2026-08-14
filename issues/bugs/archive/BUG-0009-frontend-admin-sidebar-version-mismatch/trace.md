---
bug_id: BUG-0009-frontend-admin-sidebar-version-mismatch
status: done
created_at: 2026-08-12 14:12:57
updated_at: 2026-08-13 22:40:16
severity: medium
priority: P2
lifecycle_stage: archive
related_requirement:
related_bug:
related_change: fix-frontend-admin-sidebar-version-mismatch
iteration: sprint-002
---

# BUG-0009 追踪记录

## 基本信息

| 字段 | 内容 |
|---|---|
| 标题 | 前台与后台侧边栏版本号不一致 |
| 当前状态 | done |
| 生命周期阶段 | review |
| 严重等级 | medium |
| 优先级 | P2 |
| 关联需求 | 无 |
| 关联缺陷 | 无 |
| 关联 Change | fix-frontend-admin-sidebar-version-mismatch |
| 关联 Sprint | sprint-002 |

## 已知证据

| 类型 | 证据 |
|---|---|
| 前台版本来源 | `src/shared/product-version.ts` 定义 `PRODUCT_VERSION = "v0.1.0"`，前台需求中心侧边栏引用该常量展示。 |
| 后台版本来源 | `src/web/src/pages/admin/AdminUserManagementPage.tsx` 的后台侧边栏硬编码 `<em>v1.0.5</em>`。 |
| 测试缺口 | 前台测试断言 `v0.1.0`；后台用户管理测试未断言版本一致性。 |

## 初步影响

用户在前台与后台之间切换时会看到不同产品版本，容易误判发布状态或部署状态。

## 建议后续

1. 通过 `/opsx-apply BUG-0009-frontend-admin-sidebar-version-mismatch` 实现修复。

## OpenSpec Changes

```yaml
openspec_changes:
  - change_id: fix-frontend-admin-sidebar-version-mismatch
    type: fix
    status: archived
status: done
```

## 完善资料

| 文件 | 状态 | 说明 |
|---|---|---|
| bug.md | 已生成 | 正式缺陷说明。 |
| root-cause.md | 已生成 | 直接原因、根本原因、触发条件和分类。 |
| workaround.md | 已生成 | 临时规避与限制。 |
| acceptance.md | 已生成 | 回归验收标准。 |

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-13 22:40:16 | /opsx-archive | Change `fix-frontend-admin-sidebar-version-mismatch` 已归档，状态同步完成。 |
| 2026-08-12 14:36:39 | /opsx-apply | Change `fix-frontend-admin-sidebar-version-mismatch` apply 完成，待 archive。 |
| 2026-08-12 14:12:57 | bug.capture | 创建缺陷 capture 与 trace 壳。 |
| 2026-08-12 14:15:55 | bug.generate | 生成正式缺陷说明 bug.md。 |
| 2026-08-12 14:19:01 | bug.complete | 补齐根因、规避方案、验收标准并进入待评审。 |
| 2026-08-12 14:22:19 | bug.review | 评审通过，确认修复。 |
| 2026-08-12 14:25:06 | sprint.propose | 纳入 sprint-002，归档前已纳入 sprint-002。 |
| 2026-08-12 14:28:19 | bug.opsx | 创建 OpenSpec Change `fix-frontend-admin-sidebar-version-mismatch`。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-08-13 22:40:16 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-frontend-admin-sidebar-version-mismatch
