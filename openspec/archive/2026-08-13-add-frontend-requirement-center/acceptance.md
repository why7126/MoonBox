---
change_id: add-frontend-requirement-center
status: applied
acceptance_status: passed
source_requirement: REQ-0012-frontend-requirement-center
source_sprint: sprint-002
created_at: 2026-08-10 13:10:06
updated_at: 2026-08-13 22:45:00
---

# Change 验收

## 验收范围

- REQ-0012 `acceptance.md` 中 AC-001 至 AC-023。
- REQ-0012 `acceptance.md` 中 AC-PROTOTYPE-001 至 AC-PROTOTYPE-004。
- REQ-0012 `acceptance.md` 中 AC-XCUT-001 至 AC-XCUT-008。
- `web-catalog-requirement-center` delta spec 中所有 ADDED Requirements 与 Scenarios。

## 验收门禁

- [x] 需求中心 9 阶段看板可在 MoonBox 前台打开。
- [x] Requirement/Bug 卡片、筛选、搜索、Sprint 标签、阶段主动作和归档门禁符合 spec。
- [x] 用户菜单、Hover 切换空间、空间设置弹窗和主题切换符合 prototype。
- [x] 空间设置弹窗通过 admin-modal 横切验收。
- [x] UI Skeleton 先行完成，且实现未跳过原型拆解。
- [x] 1440px 视觉验收通过并记录证据入口。
- [x] REQ-0012 文档与最终 Change 设计和实现证据一致。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-10 13:26:12
accepted_by: ai
evidence:
  - pnpm --dir src/web test -- requirement-center.test.tsx
  - pnpm --dir src/web build
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/visual-1440.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/visual-1440-space-popover.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/visual-1440-space-settings.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/visual-1440-low-modal.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-space-settings.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-low-modal.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapsed.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-shell-alignment.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-user-menu-alignment.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-shell-collapsed-alignment.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-board-prototype-alignment.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-board-bug-filter.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-card-header-prototype.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-card-header-bug-filter.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-structure.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-user-menu-structure.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-structure-collapsed.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-brand-no-overlap.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapse-button-visible.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-admin-parity-brand.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-admin-parity-collapsed.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapse-text-expanded.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapse-text-collapsed.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapse-admin-parity-expanded.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapse-admin-parity-collapsed.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-admin-collapse-24px.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-frontend-admin-collapse-height-parity.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-user-menu-grouped-session.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-space-popover-simplified.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-space-popover-dark-readable.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-admin-return-frontend.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-user-menu-floating-surface.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-admin-user-menu-grouped-surface.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-user-menu-permission-icons.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-admin-user-menu-icons.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-board-scroll-mask.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-space-popover-list-lightweight.png
  - openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-toolbar-refresh-button.png
failed_items: []
notes: `/opsx-modify` 已完成原型差异、前后台视觉对齐、9 阶段看板原型对齐、卡片/表头原型对齐、Sidebar 结构性交互、品牌/折叠按钮/提示文案细节返修，并已将展开/收起按钮形态、collapsed 外凸控制柄覆盖规则、前后台控制柄高度、前台用户菜单分组/危险色、空间二级浮层轻量化、前台菜单 summary 移除、后台返回前台入口、前后台用户菜单浮层层级、后台用户菜单分组、前台进入后台权限显示、前后台菜单图标语义、看板滚动遮罩层级、空间浮层轻量列表行和工具栏手动刷新按钮收敛一致；REQ 最终一致性已在 `/opsx-archive` 前复核通过。
```
