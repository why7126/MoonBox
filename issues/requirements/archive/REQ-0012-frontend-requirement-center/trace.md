---
requirement_id: REQ-0012-frontend-requirement-center
status: done
priority: P1
created_at: 2026-08-10 12:47:39
updated_at: 2026-08-13 22:51:12
lifecycle_stage: archive
lifecycle:
  captured: 2026-08-10 12:47:39
  generated: 2026-08-10 12:53:09
  completed: 2026-08-10 12:57:18
  reviewed: 2026-08-10 13:01:49
  approved: 2026-08-10 13:01:49
iteration: sprint-002
openspec_changes:
  - change_id: add-frontend-requirement-center
    type: add
    status: archived
related_requirements: []
knowledge_base_refs:
  - docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md
  - docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
  - docs/knowledge-base/retrospectives/sprint-001-retrospective.md
cross_cutting_tags:
  - admin-modal
prototype_refs:
  - path: issues/requirements/review/REQ-0012-frontend-requirement-center/prototype/prototype.html
    role: html-structure
  - path: issues/requirements/review/REQ-0012-frontend-requirement-center/prototype/prototype-context.md
    role: prototype-decomposition
  - path: issues/requirements/review/REQ-0012-frontend-requirement-center/prototype/prototype.png
    role: visual-reference-1440
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: passed
  req_final_consistency: passed
---

# REQ-0012-frontend-requirement-center Trace

## 基本信息

| 字段 | 值 |
|---|---|
| 标题 | MoonBox 前台需求中心 |
| 状态 | done |
| 优先级 | P1 |
| 生命周期阶段 | review |
| 关联 Sprint | sprint-002 |
| 关联 Change | add-frontend-requirement-center |

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-08-13 22:51:12 | /opsx-archive | Change `add-frontend-requirement-center` 已归档，状态同步完成。 |
| 2026-08-10 14:09:23 | /opsx-modify | Change `add-frontend-requirement-center` 验收返修已同步，待复验或 archive。 |
| 2026-08-10 13:26:30 | /opsx-apply | Change `add-frontend-requirement-center` apply 进行中，已完成 UI Skeleton、前台需求中心实现、自动化测试、1440px 视觉验收和空间设置弹窗横切验收；归档前仍需最终一致性复核。 |
| 2026-08-10 14:08:00 | /opsx-modify | 根据验收反馈修正实现与原型差异：空间设置弹窗、空间浮层、卡片动作文案、click outside 和 `#themeSwitch` 已重新对齐并重跑视觉验收。 |
| 2026-08-10 14:21:00 | /opsx-modify | 根据验收反馈修正前台 Sidebar：补齐原型 8 个菜单，恢复品牌副标题、版本徽标、active 金色左线和折叠按钮位置，并与管理后台侧栏图标密度保持一致。 |
| 2026-08-10 14:36:00 | /opsx-modify | 根据前后台截图反馈继续修正整体视觉：Sidebar 品牌区、菜单密度、active 态、折叠按钮、整体字号层级和用户菜单视觉已向管理后台收敛，并保留前台 8 个菜单与需求中心高亮。 |
| 2026-08-10 16:20:00 | /opsx-modify | 根据验收反馈修正 9 阶段看板与原型效果差异：列头结构、命令副标题、两位数 count、列宽/间距/卡片密度和 Bug 筛选空列表现已重新对齐。 |
| 2026-08-10 16:35:00 | /opsx-modify | 根据验收反馈修正 9 阶段卡片与表头原型差异：单 pill meta、docs 分隔区、无边框 mini action、ID/更新时间字号层级和表头贴顶已重新对齐。 |
| 2026-08-10 16:53:30 | /opsx-modify | 根据验收反馈修正前台 Sidebar 与后台侧栏结构性交互差异：中文品牌副标题、导航分组、13px 字体 token、collapsed 外凸折叠按钮和用户菜单 theme switch 已重新对齐。 |
| 2026-08-10 17:03:54 | /opsx-modify | 根据验收反馈修正前台 Sidebar 品牌区与折叠按钮层级，并移除冗余横向滚动提示；品牌区版本号不再重合，collapsed 按钮不再被右侧内容遮挡。 |
| 2026-08-10 17:12:10 | /opsx-modify | 根据验收反馈撤销上一轮 grid 品牌区，恢复后台管理同构的 flex 品牌区、absolute 版本徽标与折叠按钮定位；保留副标题省略和 collapsed 按钮层级保护。 |
| 2026-08-10 17:26:59 | /opsx-modify | 根据验收反馈参照后台管理修正前台 Sidebar 展开/收起按钮：改用文本 `‹` / `›`，展开态透明轻量，收起态外凸控制柄无阴影且可点击。 |
| 2026-08-10 17:47:20 | /opsx-modify | 根据验收反馈继续修正前台 Sidebar 收起态展开/收起按钮：逐项复刻后台 `admin-collapse` 尺寸、文本居中和 `border/background !important` 覆盖规则，并补 sticky 侧栏 stacking 层，确保 collapsed 控制柄完整露出且中心点命中按钮。 |
| 2026-08-10 17:54:58 | /opsx-modify | 根据验收反馈参照当前前台效果修正后台 Sidebar 收起态按钮高度：后台 `.admin-collapse` 脱离 `.admin-sidebar button` 的 40px 高度和 padding，前后台 collapsed 控制柄统一为 `24px × 24px`、`padding=0` 且中心点可点击。 |
| 2026-08-10 18:13:12 | /opsx-modify | 根据验收反馈修正前台用户菜单与后台/交互语义差异：触发箭头改为 `⌃` / `⌄`，菜单按账号、空间、偏好、会话轻量分组，退出登录单独成组并使用后台一致危险色。 |
| 2026-08-10 18:47:47 | /opsx-modify | 根据验收反馈继续修正前台用户菜单与空间二级浮层：进入后台文案统一；切换空间增加 `>`；hover 其他菜单项立即隐藏空间浮层；空间浮层移除标题/搜索/组织分组，展示中文角色和成员数，创建/加入合并，设置空间仅管理角色可见。 |
| 2026-08-10 18:59:42 | /opsx-modify | 根据验收反馈修正前台用户菜单顶部信息、空间浮层暗色可读性和后台返回入口：移除前台菜单 summary 与 `MoonBox Lab` 残留，空间列表按钮显式暗色样式，后台用户菜单新增“返回前台”。 |
| 2026-08-10 19:19:46 | /opsx-modify | 根据验收反馈统一前后台用户菜单浮层视觉与分组：用户菜单和空间二级浮层使用区别于侧边栏的浮层背景、边框、阴影和 hover 态；后台用户菜单按账号、导航、偏好、会话分组，退出登录继续单独成组并保持危险色一致。 |
| 2026-08-10 19:56:19 | /opsx-modify | 根据验收反馈修正前后台用户菜单权限与图标一致性：前台“进入后台”仅对具备用户级后台访问权限的用户显示；前后台相同功能统一图标，不同功能避免复用图标。 |
| 2026-08-11 17:45:07 | /opsx-modify | 根据验收反馈修正需求中心看板卡片上滑时在列头顶部区域透出：列头增加隔离 stacking context 与 18px 不透明遮罩，补 1440px 滚动截图和 computed style 验收。 |
| 2026-08-11 22:00:52 | /opsx-modify | 根据验收反馈轻量化前台用户菜单空间二级浮层空间项：默认无边框，hover 弱背景，selected 金色弱背景、右侧勾选和 2px 左线，补 1440px 用户菜单截图验收。 |
| 2026-08-12 10:00:00 | /opsx-modify | 根据验收反馈新增需求中心刷新图标按钮：用户可手动刷新 9 个阶段实时情况，刷新中显示状态，成功保留当前筛选，失败不清空当前看板，并补 1440px 工具栏截图验收。 |
| 2026-08-13 22:45:00 | /opsx-archive | 归档前最终一致性复核通过：REQ requirement、acceptance、trace 与 Change design、delta spec、实现证据和 1440px 视觉验收结果一致。 |
| 2026-08-10 13:10:06 | req.opsx | done | 创建 OpenSpec Change `add-frontend-requirement-center`，新增 `web-catalog-requirement-center` 能力并承接 prototype-driven UI Gate。 |
| 2026-08-10 13:05:13 | sprint.include | done | 正式纳入 sprint-002，容量估算 M=3 人天，承接 prototype-driven UI Gate 与 admin-modal 横切预防清单。 |
| 2026-08-10 13:01:49 | req.review.approve | approved | 需求评审通过；范围、验收、原型策略和横切 AC 已满足进入 Sprint 规划门禁。 |
| 2026-08-10 12:57:18 | req.complete | pending_review | 以 REQ-0012 目录中既有产品原型和上下文为准，补齐 user-stories、business-flow、acceptance、原型拆解、knowledge_base_refs、prototype_refs 与 prototype_gate。知识库承接 admin-modal 和 prototype-driven UI gate；Sprint-001 复盘提示带 prototype UI 必须前置 UI Skeleton、1440px 验收和最终一致性回填。 |
| 2026-08-10 12:53:09 | req.generate | draft | 基于需求目录中已有设计文档生成并补齐 requirement.md 治理元信息。 |
| 2026-08-10 12:47:39 | req.capture | captured | 捕获 MoonBox 前台首个优先建设方向：需求中心。 |

- 阶段迁移：plan → review（/req-review --approve）

## 原型驱动 UI 证据

| 项目 | 状态 | 证据 |
|---|---|---|
| UI Skeleton | done | `src/web/src/pages/catalog/RequirementCenterPage.tsx` |
| 1440px 首屏验收 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/visual-1440.png` |
| Hover 空间浮层 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/visual-1440-space-popover.png` |
| 空间设置弹窗 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/visual-1440-space-settings.png` |
| 低视口弹窗滚动 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/visual-1440-low-modal.png` |
| 返修后空间设置弹窗 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-space-settings.png` |
| 返修后低视口弹窗滚动 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-low-modal.png` |
| 返修后 Sidebar 展开 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar.png` |
| 返修后 Sidebar 收起 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapsed.png` |
| 返修后 Shell 对齐 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-shell-alignment.png` |
| 返修后用户菜单对齐 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-user-menu-alignment.png` |
| 返修后 Shell 收起对齐 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-shell-collapsed-alignment.png` |
| 返修后看板原型对齐 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-board-prototype-alignment.png` |
| 返修后 Bug 筛选看板 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-board-bug-filter.png` |
| 返修后卡片与表头对齐 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-card-header-prototype.png` |
| 返修后 Bug 筛选卡片与表头 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-card-header-bug-filter.png` |
| 返修后 Sidebar 结构性交互 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-structure.png` |
| 返修后用户菜单结构性交互 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-user-menu-structure.png` |
| 返修后 Sidebar 结构收起态 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-structure-collapsed.png` |
| 返修后 Sidebar 品牌不重合 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-brand-no-overlap.png` |
| 返修后 Sidebar 折叠按钮可见 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapse-button-visible.png` |
| 返修后 Sidebar 后台同构品牌区 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-admin-parity-brand.png` |
| 返修后 Sidebar 后台同构收起态 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-admin-parity-collapsed.png` |
| 返修后 Sidebar 展开按钮同构 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapse-text-expanded.png` |
| 返修后 Sidebar 收起按钮同构 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapse-text-collapsed.png` |
| 返修后 Sidebar 展开控制柄复验 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapse-admin-parity-expanded.png` |
| 返修后 Sidebar 收起控制柄复验 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-sidebar-collapse-admin-parity-collapsed.png` |
| 返修后后台收起控制柄 24px | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-admin-collapse-24px.png` |
| 返修后前后台收起控制柄高度一致 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-frontend-admin-collapse-height-parity.png` |
| 返修后前台用户菜单分组与危险色 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-user-menu-grouped-session.png` |
| 返修后空间二级浮层轻量化 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-space-popover-simplified.png` |
| 返修后用户菜单 summary 移除与空间浮层暗色 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-space-popover-dark-readable.png` |
| 返修后后台返回前台入口 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-admin-return-frontend.png` |
| 返修后前台用户菜单浮层层级 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-user-menu-floating-surface.png` |
| 返修后后台用户菜单分组与浮层层级 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-admin-user-menu-grouped-surface.png` |
| 返修后前台用户菜单权限与图标 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-user-menu-permission-icons.png` |
| 返修后后台用户菜单图标一致性 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-admin-user-menu-icons.png` |
| 返修后看板滚动遮罩层级 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-board-scroll-mask.png` |
| 返修后空间浮层轻量列表行 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-space-popover-list-lightweight.png` |
| 返修后工具栏刷新按钮 | passed | `openspec/archive/2026-08-13-add-frontend-requirement-center/implementation/modify-visual-1440-toolbar-refresh-button.png` |
| REQ 最终一致性 | passed | REQ `requirement.md`、`acceptance.md`、`trace.md` 已与 Change design、delta spec、实现证据和 1440px 视觉验收结果一致。 |
- 2026-08-13 22:51:12 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive add-frontend-requirement-center
