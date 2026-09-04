---
change_id: update-product-workbench-modern-ops-visual-system
status: passed
created_at: 2026-08-31 08:42:00
updated_at: 2026-09-03 08:57:10
---

# 验收计划

## 功能验收

- [x] 品牌分层策略已落地：公开品牌层与登录后现代 Ops 工作台层边界清晰。
- [x] 设计系统 token、预览页和校验脚本已覆盖现代 Ops 工作台。
- [x] 需求中心 Shell、统计、工具栏、筛选、看板、卡片、抽屉、AI 入口、toast 和深浅主题完成迁移。
- [x] 管理后台 CRUD 列表、弹窗、toast、状态标签和确认组件对齐现代 Ops 基线。
- [x] 未改变 REQ、BUG、Sprint、OpenSpec 状态机。

## UI 验收

- [x] 1440px 首屏截图覆盖工作台 Shell、需求中心看板、筛选 Popover、用户菜单、后台弹窗和深浅主题。
- [x] 窄屏验收覆盖 Sidebar 折叠、工具栏换行、横向看板和文本不溢出。
- [x] computed style 证据覆盖字体、字号、行高、间距、圆角、边框、背景、颜色、z-index、overflow 和 position。
- [x] 浮层验收覆盖筛选 Popover、用户菜单和后台弹窗的可退出状态。

## 数据采集与链路观测

- [x] N/A 声明保持成立：未新增 API、DB、请求日志、行为事件、Task Trace、对象存储或请求封装。

## 验证命令

- [x] `python scripts/validate-design-system.py`
- [x] 前端聚焦测试或等价 Vitest/Testing Library 测试
- [x] 1440px 与窄屏 Playwright 视觉验收
- [x] `openspec validate update-product-workbench-modern-ops-visual-system --strict`
- [x] `python scripts/sync-workflow-status.py --event opsx.apply --change update-product-workbench-modern-ops-visual-system --sprint auto --dry-run`

## 验收证据

| 类型 | 入口 | 结果 |
|---|---|---|
| 需求中心 1440px | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual/requirements-1440.png` | 通过 |
| 筛选 Popover 1440px | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual/requirements-filter-popover-1440.png` | 通过 |
| 用户菜单 1440px | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual/requirements-user-menu-1440.png` | 通过 |
| 浅色主题 1440px | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual/requirements-light-1440.png` | 通过 |
| 侧边栏折叠 1440px | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual/requirements-collapsed-1440.png` | 通过 |
| 移动视口 390px | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual/requirements-mobile-390.png` | 通过 |
| 后台列表 1440px | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual/admin-users-1440.png` | 通过 |
| 后台弹窗 1440px | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual/admin-user-modal-1440.png` | 通过 |
| 设计系统页 1440px | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual/design-system-1440.png` | 通过 |
| computed style | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual/computed-styles.json` | 通过 |

## 返修验收证据

| 类型 | 入口 | 结果 |
|---|---|---|
| 附件对照返修截图集 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/` | 通过 |
| 移动端挤压复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-mobile-390.png` | 通过 |
| 筛选 Popover 密度复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-filter-popover-1440.png` | 通过 |
| computed style 复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/computed-styles.json` | 通过 |
| 标题区布局复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png` 与 `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/computed-styles.json` | 通过 |
| 前台品牌区复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png` 与 `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/computed-styles.json` | 通过 |
| 版本号与展开收起按钮复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png` 与 `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/computed-styles.json` | 通过 |
| 九阶段看板视觉复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png` 与 `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/computed-styles.json` | 通过 |
| 九阶段暗场质感复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`requirements-board-scrolled-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段列结构表达复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`requirements-one-card-empty-columns-1440.png`、`requirements-board-scrolled-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段列头与空列文案复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段空列颜色复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段空列低对比承载框弱化复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段列头冻结恢复与空列低存在感占位复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段 sticky 列头防穿透复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段 sticky 列头边界遮罩复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-sticky-head-boundary-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段 sticky 连续遮罩带方案回退复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-sticky-head-boundary-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段 header/body 分离与列体内部滚动复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-sticky-head-boundary-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段空列附件样式承载框复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段空列占位文字字体复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png` 与 `computed-styles.json` | 通过 |
| 需求中心标题小标题文案复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png` | 通过 |
| 新建 Capture 入口按钮复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段列头附件样式复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`requirements-one-card-empty-columns-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段空列占位符最终附件样式复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段任务卡片轻量票据化复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png` 与 `computed-styles.json` | 通过 |
| 需求中心指标卡两层信息结构复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段列体首项顶部对齐复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段任务卡片优先级/负责人双标签复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段任务卡片内部信息布局复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段任务卡片自适应高度与列体滚动缓冲复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段任务卡片自然高度与统一信息栈节奏复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段多卡片列按研发中卡片基准完整展示复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-board-scrolled-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段横向列间隙收窄复验 | CSS 契约与 `src/web/src/requirement-center.test.tsx` | 通过 |
| 新增 Capture 弹窗附件化复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-capture-modal-1440.png` 与 `computed-styles.json` | 通过 |
| 新增 Capture 弹窗文案与必填标识复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-capture-modal-1440.png` 与 `computed-styles.json` | 通过 |
| 右下 Agent 助手入口与操作面板复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-agent-modal-1440.png` 与 `computed-styles.json` | 通过 |
| 九阶段卡片动作 Action Modal 组件族复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-action-analysis-modal-1440.png`、`requirements-action-generate-modal-1440.png`、`requirements-action-complete-modal-1440.png`、`requirements-action-sprint-modal-1440.png`、`requirements-action-opsx-modal-1440.png`、`requirements-action-progress-modal-1440.png` 与 `computed-styles.json` | 通过 |
| 需求分析 Action Modal 要点勾选交互复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-action-analysis-selection-1440.png` 与 `computed-styles.json` | 通过 |
| 已完成卡片只读展示复验 | `src/web/src/requirement-center.test.tsx` 覆盖 `done` 阶段无进度区、无 `查看归档` 动作按钮且保留 `archive.md`、`trace.md` | 通过 |
| 加入迭代 Action Modal sprintModal 复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-action-sprint-modal-1440.png` 与 `computed-styles.json`，并由 `src/web/src/requirement-center.test.tsx` 覆盖对象块、迭代模式、radio、容量条、容量不足 badge、新建迭代编号和确认按钮联动 | 通过 |
| 九阶段卡片进度行字体与颜色复验 | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/computed-styles.json` 覆盖 `.rc-progress`、`.rc-progress-action`、`.rc-progress-label`、`.rc-progress-value`；`src/web/src/requirement-center.test.tsx` 覆盖 DOM 拆分与抽屉按钮能力 | 通过 |
