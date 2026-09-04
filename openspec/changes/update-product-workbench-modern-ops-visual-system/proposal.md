## 背景与动机

MoonBox 登录后的产品工作台已经承担需求、Bug、Sprint、Agent 和文档流转等高频 Ops 操作，但现有视觉体系仍偏品牌叙事延展，信息密度、状态反馈和操作扫描效率不足。REQ-0023 已确认全面向附件 `moonbox-board.html` 的现代 Ops 工作台风格靠拢，并允许调整品牌分层、设计 token 与 UI 设计系统。

## 变更内容

- 将登录后产品工作台定位从“宝盒品牌页面延展”升级为“现代 Ops 工具台”，强调高密度、清晰状态、低干扰和可快速推进研发。
- 建立双品牌分层策略：公开首页和登录过渡可保留 MoonBox 宝盒叙事，登录后工作台、需求中心和管理后台共用现代 Ops 视觉系统。
- 重构设计系统 token，覆盖画布、侧边栏、面板、边框、文字、金色强调、状态色、圆角、阴影、间距、控件高度、字体和动效。
- 规范产品工作台核心组件：Sidebar、Header、统计卡、Toolbar、搜索、segmented、筛选 Popover、Kanban、Card、Drawer、Modal、Toast 和 AI 入口。
- 将附件风格作为设计输入吸收统计趋势、筛选 badge、空列虚线占位、卡片状态边、footer 动作分区和命令/ID 等宽表达，不机械复制附件 HTML。
- 为 UI Change 强制承接 UI Contract、UI Skeleton、1440px 视觉证据、computed style、深浅主题、Mock/API 边界和 REQ 最终一致性。
- 不改变 REQ、BUG、Sprint、OpenSpec 状态机，不新增 API、数据库、对象存储、请求日志、行为埋点或 Task Trace 字段。

## 能力影响

### 新增能力

- 无。

### 修改能力

- `design-system`：将 MoonBox 设计系统从旧品牌叙事基线扩展为双品牌分层与现代 Ops 工作台 token/组件基线。
- `web-catalog-requirement-center`：将需求中心和登录后工作台 Shell 迁移为现代 Ops 风格，并保留真实数据、阶段动作和原型驱动验收边界。
- `web-admin-crud-list-template`：使管理后台列表、弹窗、toast 和状态组件能够复用现代 Ops 视觉基线，同时保留后台 CRUD 一致性门禁。

## 影响范围

- Web 前台：`src/web` 的工作台 Shell、需求中心、全局导航、用户菜单、筛选、看板、抽屉和主题样式。
- 管理后台：共用 Shell、CRUD 列表模板、弹窗、toast、状态标签与确认组件视觉一致性。
- 设计系统：`src/shared/design-system/tokens/`、`src/web/src/styles/globals.css`、设计系统预览页和 UI 校验脚本。
- 文档与治理：`rules/ui-design.md`、设计系统相关长期文档、原型驱动 UI 验收证据和 linked REQ 文档一致性。
- 测试：聚焦前端测试、设计系统校验、1440px 与窄屏视觉验收、computed style 证据、深浅主题回归。
- 产品数据采集与链路观测：N/A，本 Change 不调整 API、DB、行为事件、请求日志、Task Trace、对象存储或请求封装。
