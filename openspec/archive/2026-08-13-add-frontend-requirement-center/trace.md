---
change_id: add-frontend-requirement-center
status: applied
type: add
source_requirement: REQ-0012-frontend-requirement-center
source_sprint: sprint-002
created_at: 2026-08-10 13:10:06
updated_at: 2026-08-13 22:45:00
prototype_refs:
  - path: issues/requirements/review/REQ-0012-frontend-requirement-center/prototype/prototype.html
    role: html-structure
  - path: issues/requirements/review/REQ-0012-frontend-requirement-center/prototype/prototype-context.md
    role: prototype-decomposition
  - path: issues/requirements/review/REQ-0012-frontend-requirement-center/prototype/prototype.png
    role: visual-reference-1440
knowledge_base_refs:
  - docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
  - docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md
  - docs/knowledge-base/retrospectives/sprint-001-retrospective.md
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: passed
  req_final_consistency: passed
---

# Trace

## 创建记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-08-10 13:10:06 | req.opsx | proposed | 基于 REQ-0012 创建 OpenSpec Change，新增 `web-catalog-requirement-center` 能力，承接 prototype-driven UI Gate 与 admin-modal 横切验收。 |
| 2026-08-10 13:26:12 | opsx.apply | applied | 完成前台需求中心页面、9 阶段看板、筛选搜索、用户菜单、Hover 空间切换、空间设置弹窗、主题切换、测试与视觉验收；本 Change 不引入后端、API、DB 或对象存储变更。 |
| 2026-08-10 14:08:00 | opsx.modify | applied | 根据验收反馈修正与原型差异：空间设置弹窗恢复 1040px、16px 圆角与阴影；空间浮层恢复 fixed 位置；卡片动作改为产品化文案；补 click outside 关闭和唯一 `#themeSwitch`；已重跑视觉验收。 |
| 2026-08-10 14:21:00 | opsx.modify | applied | 根据验收反馈修正前台 Sidebar：补齐原型 8 个菜单，恢复品牌副标题、版本徽标、active 金色左线和品牌区折叠按钮，并统一后台式 lucide 图标密度与折叠行为。 |
| 2026-08-10 14:36:00 | opsx.modify | applied | 根据前后台截图反馈继续修正前台整体视觉：Sidebar 改用真实 MoonBox 图标、后台式品牌高与折叠按钮、14px 菜单字体、40px 导航行高、46px 用户触发器、chevron 和轻量用户菜单；保留前台 8 个菜单与需求中心高亮。 |
| 2026-08-10 16:20:00 | opsx.modify | applied | 根据验收反馈修正 9 阶段看板与原型差异：恢复原型列头结构、命令副标题、两位数 count、列宽/间距/卡片密度；Bug 筛选下仍清晰表达共 9 个阶段并降低空列压迫感。 |
| 2026-08-10 16:35:00 | opsx.modify | applied | 根据验收反馈修正 9 阶段卡片与表头原型差异：恢复 italic 小号 ID、单 pill meta、docs 分隔区、无边框 mini action、9px 更新时间，并将阶段表头贴近列顶部边框。 |
| 2026-08-10 16:53:30 | opsx.modify | applied | 根据验收反馈修正前台 Sidebar 与后台侧栏结构性交互差异：统一 13px 字体 token、中文品牌副标题、导航分组、collapsed 外凸折叠按钮和用户菜单 theme switch 视觉。 |
| 2026-08-10 17:03:54 | opsx.modify | applied | 根据验收反馈修正前台 Sidebar 品牌区与折叠按钮层级，并移除冗余横向滚动提示：品牌区版本号不再重合，collapsed 按钮不再被右侧内容遮挡。 |
| 2026-08-10 17:12:10 | opsx.modify | applied | 根据验收反馈撤销上一轮 grid 品牌区，恢复后台管理同构的 flex 品牌区、absolute 版本徽标与折叠按钮定位；保留副标题省略和 collapsed 按钮层级保护。 |
| 2026-08-10 17:26:59 | opsx.modify | applied | 根据验收反馈参照后台管理修正前台 Sidebar 展开/收起按钮：改用文本 `‹` / `›`，展开态透明轻量，收起态外凸控制柄无阴影且可点击。 |
| 2026-08-10 17:47:20 | opsx.modify | applied | 根据验收反馈继续修正前台 Sidebar 收起态展开/收起按钮：逐项复刻后台 `admin-collapse` 尺寸、文本居中和 `border/background !important` 覆盖规则，并为 sticky 侧栏补 stacking 层，确保 collapsed 控制柄完整露出且中心点命中按钮。 |
| 2026-08-10 17:54:58 | opsx.modify | applied | 根据验收反馈参照当前前台效果修正后台 Sidebar 收起态按钮高度：后台 `.admin-collapse` 脱离 `.admin-sidebar button` 的 40px 高度和 padding，前后台 collapsed 控制柄统一为 `24px × 24px`、`padding=0` 且中心点可点击。 |
| 2026-08-10 18:13:12 | opsx.modify | applied | 根据验收反馈修正前台用户菜单：触发箭头改为底部弹出语义的 `⌃` / `⌄`；菜单按账号、空间、偏好、会话轻量分组；退出登录单独成组并使用后台一致危险色。 |
| 2026-08-10 18:47:47 | opsx.modify | applied | 根据验收反馈继续修正前台用户菜单与空间二级浮层：进入后台文案统一，切换空间增加 `>` 二级提示；空间浮层移除标题/搜索/组织分组，展示中文角色和成员数，创建/加入合并，设置空间仅管理角色可见。 |
| 2026-08-10 18:59:42 | opsx.modify | applied | 根据验收反馈修正前台用户菜单顶部信息、空间浮层可读性和后台返回入口：移除前台 summary 与 `MoonBox Lab`，空间列表按钮显式暗色样式，后台用户菜单新增“返回前台”。 |
| 2026-08-10 19:19:46 | opsx.modify | applied | 根据验收反馈统一前后台用户菜单浮层视觉与分组：用户菜单和空间二级浮层使用区别于侧边栏的浮层背景、边框、阴影和 hover 态；后台用户菜单按账号、导航、偏好、会话分组，退出登录继续单独成组并保持危险色一致。 |
| 2026-08-10 19:56:19 | opsx.modify | applied | 根据验收反馈修正前后台用户菜单权限与图标一致性：前台“进入后台”仅对具备用户级后台访问权限的用户显示；相同功能统一图标，不同功能避免复用同一图标。 |
| 2026-08-11 17:45:07 | opsx.modify | applied | 根据验收反馈修正看板滚动层级：`.rc-column-head` 增加隔离 stacking context 和向上延伸 18px 的不透明 `::before` 遮罩，列头 `z-index` 提升到 `8`，卡片上滑时不再在列头顶部透出。 |
| 2026-08-11 22:00:52 | opsx.modify | applied | 根据验收反馈轻量化空间二级浮层列表项：空间项默认无边框，hover 使用弱背景，selected 使用金色弱背景、右侧勾选和 2px 左侧金线；底部“创建或加入空间”按钮继续保留边框。 |
| 2026-08-12 10:00:00 | opsx.modify | applied | 根据验收反馈新增需求中心手动刷新图标按钮：用户可主动刷新 9 阶段实时情况，刷新中按钮禁用并旋转，成功保留当前筛选并更新上下文，失败保留当前看板并显示轻量 toast。 |
| 2026-08-13 22:45:00 | opsx.archive | applied | 归档前最终一致性复核通过：REQ requirement、acceptance、trace 与 Change design、delta spec、实现证据和 1440px 视觉验收结果一致。 |

## Conflict Resolution

HTML > PNG > prototype-context.md > acceptance.md > ui-design.md > openspec/specs。当前无阻断冲突。

## Skeleton 状态

| 项目 | 状态 | 说明 |
|---|---|---|
| 原型拆解 | done | `/req-complete` 已补齐页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。 |
| UI Skeleton | done | 已新增 `RequirementCenterPage`，覆盖页面壳、组件插槽、状态容器、数据依赖和可测选择器。 |
| 1440px 视觉验收 | passed | Playwright Chromium，`1440x900`，页面 `/requirements`，最新工具栏刷新按钮证据见 `implementation/modify-visual-1440-toolbar-refresh-button.png`；低视口弹窗证据见 `implementation/modify-visual-1440-low-modal.png`。 |
| REQ 最终一致性 | passed | REQ `requirement.md`、`acceptance.md`、`trace.md` 已与 Change design、delta spec、实现证据和 1440px 视觉验收结果一致。 |

## 实现证据

| 类型 | 结果 | 证据 |
|---|---|---|
| 前端实现 | pass | `src/web/src/pages/catalog/RequirementCenterPage.tsx`、`src/web/src/App.tsx`、`src/web/src/styles/globals.css` |
| 前端测试 | pass | `pnpm --dir src/web test -- requirement-center.test.tsx`，37 tests passed |
| 前端构建 | pass | `pnpm --dir src/web build` |
| admin-modal 横切 | pass | `modalCardClassCount=0`，computed width `1040px`，border-radius `16px`，body overflow-y `auto` |
| 低视口弹窗 | pass | Playwright Chromium `1440x640`，弹窗 `1040px × 576px`，保存按钮可见，遮罩 overflow-y `auto` |
| 视觉验收 | pass | `implementation/modify-visual-1440-space-settings.png`、`implementation/modify-visual-1440-low-modal.png` |
| Sidebar 返修验收 | pass | `implementation/modify-visual-1440-sidebar.png`、`implementation/modify-visual-1440-sidebar-collapsed.png` |
| Shell 视觉对齐验收 | pass | `implementation/modify-visual-1440-shell-alignment.png`、`implementation/modify-visual-1440-user-menu-alignment.png`、`implementation/modify-visual-1440-shell-collapsed-alignment.png` |
| 看板原型对齐验收 | pass | `implementation/modify-visual-1440-board-prototype-alignment.png`、`implementation/modify-visual-1440-board-bug-filter.png` |
| 卡片与表头原型对齐验收 | pass | `implementation/modify-visual-1440-card-header-prototype.png`、`implementation/modify-visual-1440-card-header-bug-filter.png` |
| Sidebar 结构性交互验收 | pass | `implementation/modify-visual-1440-sidebar-structure.png`、`implementation/modify-visual-1440-user-menu-structure.png`、`implementation/modify-visual-1440-sidebar-structure-collapsed.png` |
| Sidebar 品牌与折叠层级验收 | pass | `implementation/modify-visual-1440-sidebar-brand-no-overlap.png`、`implementation/modify-visual-1440-sidebar-collapse-button-visible.png` |
| Sidebar 后台同构品牌区验收 | pass | `implementation/modify-visual-1440-sidebar-admin-parity-brand.png`、`implementation/modify-visual-1440-sidebar-admin-parity-collapsed.png` |
| Sidebar 展开收起按钮同构验收 | pass | `implementation/modify-visual-1440-sidebar-collapse-text-expanded.png`、`implementation/modify-visual-1440-sidebar-collapse-text-collapsed.png` |
| Sidebar 收起控制柄后台同构复验 | pass | `implementation/modify-visual-1440-sidebar-collapse-admin-parity-expanded.png`、`implementation/modify-visual-1440-sidebar-collapse-admin-parity-collapsed.png` |
| 前后台收起控制柄高度一致验收 | pass | `implementation/modify-visual-1440-admin-collapse-24px.png`、`implementation/modify-visual-1440-frontend-admin-collapse-height-parity.png` |
| 前台用户菜单分组与危险色验收 | pass | `implementation/modify-visual-1440-user-menu-grouped-session.png` |
| 空间二级浮层轻量化验收 | pass | `implementation/modify-visual-1440-space-popover-simplified.png` |
| 用户菜单 summary 移除与空间浮层暗色验收 | pass | `implementation/modify-visual-1440-space-popover-dark-readable.png` |
| 后台返回前台入口验收 | pass | `implementation/modify-visual-1440-admin-return-frontend.png` |
| 前台用户菜单浮层层级验收 | pass | `implementation/modify-visual-1440-user-menu-floating-surface.png` |
| 后台用户菜单分组与浮层层级验收 | pass | `implementation/modify-visual-1440-admin-user-menu-grouped-surface.png` |
| 前台用户菜单权限与图标验收 | pass | `implementation/modify-visual-1440-user-menu-permission-icons.png` |
| 后台用户菜单图标一致性验收 | pass | `implementation/modify-visual-1440-admin-user-menu-icons.png` |
| 看板滚动遮罩验收 | pass | `implementation/modify-visual-1440-board-scroll-mask.png`；computed style：`.rc-column-head position=sticky`、`z-index=8`、`background=rgb(14, 16, 35)`、`isolation=isolate`，`::before inset=-18px 0 0`、`pointer-events=none`。 |
| 空间浮层轻量列表验收 | pass | `implementation/modify-visual-1440-space-popover-list-lightweight.png`；computed style：空间项 `borderWidth=0px`、hover 弱背景、selected 左线 `width=2px`、`pointer-events=none`，动作按钮 `borderWidth=1px`。 |
| 工具栏刷新按钮验收 | pass | `implementation/modify-visual-1440-toolbar-refresh-button.png`；computed style：按钮 `width=38px`、`height=38px`、`borderWidth=1px`，刷新中 `disabled=true`、`aria-busy=true`、图标 `animationName=rc-spin`、`animationDuration=0.8s`。 |
