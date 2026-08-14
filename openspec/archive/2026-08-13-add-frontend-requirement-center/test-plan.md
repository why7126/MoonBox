---
change_id: add-frontend-requirement-center
status: applied
source_requirement: REQ-0012-frontend-requirement-center
source_sprint: sprint-002
created_at: 2026-08-10 13:10:06
updated_at: 2026-08-10 19:56:19
---

# 测试计划

## 前端自动化测试

- 使用 Vitest / Testing Library 覆盖需求中心页面基础渲染。
- 覆盖 9 阶段列、Requirement/Bug 卡片、筛选、搜索和 Sprint 标签展示。
- 覆盖阶段主动作映射和文档缺失/验收未完成阻断。
- 覆盖 Sidebar 展开/收起、主题切换和需求中心导航高亮。
- 覆盖 Hover“切换空间”、180ms 安全区、空间搜索、空间单选和用户区空间摘要更新。
- 覆盖空间设置弹窗分组切换、保存、取消、关闭和 toast。

## 视觉与交互验收

- 使用 1440px 桌面视口验收首屏结构、间距、对齐、主题、字号、弹窗、toast、滚动、Hover 浮层和文本溢出。
- 使用低视口验收空间设置弹窗 body 滚动和底部操作可访问。
- 验收 9 列 Column Header 吸顶时不创建克隆表头、不产生灰色空白、不与卡片列错位。
- 验收 fixed toast 不造成 layout shift。

## 回归范围

- 回归现有 Web 首页与登录页入口不被前台需求中心路由破坏。
- 回归现有管理后台用户菜单相关测试不被前台用户菜单原型命名影响。
- 若实现引入 API 数据接入，再补充 API 客户端和后端集成测试；当前 Change 规格阶段不引入 API/DB 变更。

## 执行记录

| 时间 | 命令/工具 | 结果 | 说明 |
|---|---|---|---|
| 2026-08-10 13:22:30 | `pnpm --dir src/web test -- requirement-center.test.tsx` | pass | 5 个测试文件、37 个用例通过，覆盖需求中心新增测试与既有 Web 回归。 |
| 2026-08-10 13:22:16 | `pnpm --dir src/web build` | pass | TypeScript 与 Vite production build 通过。 |
| 2026-08-10 13:24:00 | Playwright Chromium `1440x900` | pass | 页面 `/requirements`，9 列、9 卡片、空间浮层、空间设置弹窗、toast、computed width 和 `modal-card` 并存检查通过。 |
| 2026-08-10 13:25:00 | Playwright Chromium `1440x640` | pass | 低视口下弹窗 body `overflow-y:auto`，底部保存操作可访问，遮罩可滚动。 |
| 2026-08-10 14:06:26 | `pnpm --dir src/web test -- requirement-center.test.tsx` | pass | 返修后 5 个测试文件、37 个用例通过，新增覆盖产品化动作文案、click outside 和唯一 `#themeSwitch`。 |
| 2026-08-10 14:06:26 | `pnpm --dir src/web build` | pass | 返修后 TypeScript 与 Vite production build 通过。 |
| 2026-08-10 14:08:00 | Playwright Chromium `1440x900` | pass | 返修后动作文案 `开始开发 →`、命令 title `/opsx-apply`、`#themeSwitch` 唯一、空间浮层 fixed `left=208/bottom=72`、click outside 关闭、弹窗 `1040px`、16px 圆角、阴影和 `modal-card` 并存检查通过。 |
| 2026-08-10 14:08:00 | Playwright Chromium `1440x640` | pass | 返修后低视口弹窗 `1040px × 576px`，body `overflow-y:auto`，保存更改按钮可访问，遮罩可滚动。 |
| 2026-08-10 14:21:00 | Playwright Chromium `1440x900` | pass | Sidebar 返修后 8 个原型菜单、需求中心高亮、版本 `v4.0.5`、品牌副标题、active 金色左线、8 个图标、折叠 `72px` 和 label 隐藏均通过。 |
| 2026-08-10 14:36:00 | `pnpm --dir src/web test -- requirement-center.test.tsx` | pass | 返修后 5 个测试文件、37 个用例通过，覆盖前台需求中心与管理后台回归。 |
| 2026-08-10 14:36:00 | `pnpm --dir src/web build` | pass | 返修后 TypeScript 与 Vite production build 通过。 |
| 2026-08-10 14:36:00 | Playwright Chromium `1440x900` | pass | 前后台视觉对齐返修后，Sidebar 224px、品牌高 72px、8 个菜单、需求中心高亮、40px 导航行高、14px 导航字号、16px 图标、`2px × 18px` 金色左线、46px 用户触发器、6px 用户菜单和 72px 折叠态均通过。 |
| 2026-08-10 16:20:00 | `pnpm --dir src/web test -- requirement-center.test.tsx` | pass | 返修后 5 个测试文件、37 个用例通过，新增覆盖原型命令副标题、两位数 count 和 Bug 筛选仍保留 9 阶段。 |
| 2026-08-10 16:20:00 | `pnpm --dir src/web build` | pass | 返修后 TypeScript 与 Vite production build 通过。 |
| 2026-08-10 16:20:00 | Playwright Chromium `1440x900` | pass | 看板原型对齐返修后，全部筛选下 9 列、原型命令副标题、两位数 count、`258px` 列宽和 `132px` 卡片最小高度通过；Bug 筛选下仍保留 9 列、两位数 count 和 2 张 Bug 卡片。 |
| 2026-08-10 16:35:00 | `pnpm --dir src/web test -- requirement-center.test.tsx` | pass | 返修后 5 个测试文件、37 个用例通过，新增覆盖单 pill meta。 |
| 2026-08-10 16:35:00 | `pnpm --dir src/web build` | pass | 返修后 TypeScript 与 Vite production build 通过。 |
| 2026-08-10 16:35:00 | Playwright Chromium `1440x900` | pass | 卡片与表头原型对齐返修后，阶段表头 `top=0` 且顶部 gap 为 `2px` 顶线，卡片 ID 为 11px italic，meta 为单 pill，docs 有 1px 上边框，mini action 无边框；Bug 筛选下仍保留 9 列与 2 张 Bug 卡片。 |
| 2026-08-10 16:53:30 | `pnpm --dir src/web test -- requirement-center.test.tsx` | pass | 返修后 5 个测试文件、37 个用例通过，新增覆盖中文品牌副标题、导航分组和 theme switch 滑块。 |
| 2026-08-10 16:53:30 | `pnpm --dir src/web build` | pass | 返修后 TypeScript 与 Vite production build 通过。 |
| 2026-08-10 16:53:30 | Playwright Chromium `1440x900` | pass | Sidebar 结构性交互返修后，品牌文案 `MoonBox` / `AI原生软件工厂` 完整显示，前台 8 菜单按 `WORKSPACE` / `CAPABILITIES` 分组，导航与用户菜单为 13px，折叠态宽度 `72px`、折叠按钮 `right=-13px`。 |
| 2026-08-10 17:03:54 | `pnpm --dir src/web test -- requirement-center.test.tsx` | pass | 返修后 5 个测试文件、37 个用例通过，覆盖横向滚动提示已移除。 |
| 2026-08-10 17:03:54 | `pnpm --dir src/web build` | pass | 返修后 TypeScript 与 Vite production build 通过。 |
| 2026-08-10 17:03:54 | Playwright Chromium `1440x900` | pass | 品牌区 `MoonBox/AI原生软件工厂` 与 `v4.0.5` 无重叠，collapsed 折叠按钮 `z-index=30` 且中心点可点击，页面不再包含“按住 Shift 横向滚动 · 共 9 个阶段”。 |
| 2026-08-10 17:12:10 | `pnpm --dir src/web test -- requirement-center.test.tsx` | pass | 返修后 5 个测试文件、37 个用例通过。 |
| 2026-08-10 17:12:10 | `pnpm --dir src/web build` | pass | 返修后 TypeScript 与 Vite production build 通过。 |
| 2026-08-10 17:12:10 | Playwright Chromium `1440x900` | pass | 撤销 grid 品牌区后，前台 Sidebar 顶部恢复后台式 `flex`、版本徽标 `absolute right=36px`、折叠按钮 `absolute right=10px`；`MoonBox` 与版本徽标无重叠，collapsed 按钮 `z-index=30` 且中心点可点击。 |
| 2026-08-10 17:26:59 | `pnpm --dir src/web test -- requirement-center.test.tsx` | pass | 返修后 5 个测试文件、37 个用例通过。 |
| 2026-08-10 17:26:59 | `pnpm --dir src/web build` | pass | 返修后 TypeScript 与 Vite production build 通过。 |
| 2026-08-10 17:26:59 | Playwright Chromium `1440x900` | pass | 展开态按钮为文本 `‹`，`right=10px`、透明无边框无阴影；收起态按钮为文本 `›`，`right=-13px`、1px 边框、侧栏背景、无阴影、`z-index=30` 且中心点可点击。 |
| 2026-08-10 17:47:20 | `pnpm --dir src/web test -- requirement-center.test.tsx` | pass | 返修后 5 个测试文件、37 个用例通过。 |
| 2026-08-10 17:47:20 | `pnpm --dir src/web build` | pass | 返修后 TypeScript 与 Vite production build 通过。 |
| 2026-08-10 17:47:20 | Playwright Chromium `1440x900` | pass | 复验后台同构控制柄：展开态 `‹`、透明无边框、`text-align=center`；收起态 `›`、`right=-13px`、1px 边框、侧栏背景、无阴影、`text-align=center`，侧栏 `z-index=20`，按钮中心点命中 `.rc-collapse`。 |
| 2026-08-10 17:54:58 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx` | pass | 返修后 5 个测试文件、37 个用例通过，覆盖前台需求中心和后台用户管理回归。 |
| 2026-08-10 17:54:58 | `pnpm --dir src/web build` | pass | 返修后 TypeScript 与 Vite production build 通过。 |
| 2026-08-10 17:54:58 | Playwright Chromium `1440x900` | pass | 前后台 collapsed 控制柄复验通过：后台 `.admin-collapse` 与前台 `.rc-collapse` 均为 `24px × 24px`、`padding=0`、`right=-13px`、`top=24px`、1px 边框、侧栏背景、无阴影且中心点命中按钮。 |
| 2026-08-10 18:13:12 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx` | pass | 返修后 5 个测试文件、37 个用例通过，覆盖前台需求中心和后台用户管理回归。 |
| 2026-08-10 18:13:12 | `pnpm --dir src/web build` | pass | 返修后 TypeScript 与 Vite production build 通过。 |
| 2026-08-10 18:13:12 | Playwright Chromium `1440x900` | pass | 用户菜单分组和语义复验通过：关闭态箭头 `⌃`、打开态 `⌄`；账号/空间/偏好/会话 4 组；退出登录单独会话组，颜色 `rgb(212, 116, 118)`，`#themeSwitch` 数量为 1。 |
| 2026-08-10 18:47:47 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx` | pass | 返修后 5 个测试文件、37 个用例通过，覆盖空间浮层轻量化、hover 关闭和设置空间文案。 |
| 2026-08-10 18:47:47 | `pnpm --dir src/web build` | pass | 返修后 TypeScript 与 Vite production build 通过。 |
| 2026-08-10 18:47:47 | Playwright Chromium `1440x900` | pass | 空间二级浮层验收通过：无标题、无搜索、无组织分组；空间项展示中文角色与成员数；“切换空间”展示 `>`；“进入后台”和“设置空间”文案存在；hover 个人资料后浮层立即关闭。 |
| 2026-08-10 18:59:42 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx` | pass | 返修后 5 个测试文件、37 个用例通过，覆盖前台菜单 summary 移除与后台“返回前台”。 |
| 2026-08-10 18:59:42 | `pnpm --dir src/web build` | pass | 返修后 TypeScript 与 Vite production build 通过。 |
| 2026-08-10 18:59:42 | Playwright Chromium `1440x900` | pass | 前台用户菜单不再包含 `.rc-menu-summary` 或 `MoonBox Lab`；空间列表按钮为暗色可读样式；后台用户菜单包含“返回前台”。 |
| 2026-08-10 19:19:46 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx` | pass | 返修后 5 个测试文件、37 个用例通过，覆盖前台用户菜单 4 组、后台用户菜单 4 组和退出登录单独会话组。 |
| 2026-08-10 19:19:46 | `pnpm --dir src/web build` | pass | 返修后 TypeScript 与 Vite production build 通过。 |
| 2026-08-10 19:19:46 | Playwright Chromium `1440x900` | pass | 前台用户菜单与空间二级浮层使用区别于侧边栏的浮层背景、边框和阴影；后台用户菜单使用同类浮层 surface，并按账号、导航、偏好、会话分组。 |
| 2026-08-10 19:56:19 | `pnpm --dir src/web test -- requirement-center.test.tsx admin-user-management.test.tsx` | pass | 返修后 5 个测试文件、38 个用例通过，覆盖前台 `canAccessAdmin` 权限条件、前台菜单图标不复用和后台菜单图标不复用。 |
| 2026-08-10 19:56:19 | `pnpm --dir src/web build` | pass | 返修后 TypeScript 与 Vite production build 通过。 |
| 2026-08-10 19:56:19 | Playwright Chromium `1440x900` | pass | 前台用户菜单存在具备权限后的“进入后台”，7 个菜单项使用 7 个不同图标；后台用户菜单 5 个菜单项使用 5 个不同图标。 |
