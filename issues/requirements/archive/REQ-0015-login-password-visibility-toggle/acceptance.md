---
requirement_id: REQ-0015-login-password-visibility-toggle
acceptance_status: passed
created_at: 2026-08-11 22:03:00
updated_at: 2026-08-14 16:29:34
---

# 验收标准

## 功能 AC

- [ ] AC-001 Web 登录页密码输入框默认隐藏明文，初始 `type` 为 `password`。
- [ ] AC-002 密码字段提供显示/隐藏切换控件，控件位于密码输入框右侧或与输入框紧邻。
- [ ] AC-003 密码隐藏时，控件语义为“显示密码”；密码显示时，控件语义为“隐藏密码”。
- [ ] AC-004 触发切换后，密码输入框可在 `password` 与 `text` 展示类型之间切换。
- [ ] AC-005 切换展示状态不得清空、重置、改写或持久化密码输入值。
- [ ] AC-006 切换控件必须为 `button type="button"` 或等价安全机制，不得触发表单提交或登录接口调用。
- [ ] AC-007 切换后应尽量保持密码输入框焦点和光标位置，避免打断连续输入。
- [ ] AC-008 新增切换控件后，用户名必填、密码必填、记住我、登录中状态、登录失败反馈、登录成功跳转和返回首页行为保持不变。
- [ ] AC-009 切换控件支持键盘聚焦，并可通过 Enter/Space 触发。
- [ ] AC-010 切换控件具备辅助技术可读取的标签，并通过 `aria-pressed` 或等价状态表达当前显隐状态。
- [ ] AC-011 密码明文不得写入 URL、日志、错误上报、埋点、本地存储、测试输出或其他可持久化位置。
- [ ] AC-012 前端测试覆盖默认隐藏、点击显示、再次隐藏、值不丢失、不提交表单和既有登录流程不回归。

## UI AC

- [ ] AC-UI-001 密码输入框右侧预留控件空间，输入文本、placeholder 和浏览器自动填充视觉不得与图标按钮重叠。
- [ ] AC-UI-002 控件使用项目既有图标体系中的 `Eye` / `EyeOff` 或等价图标，尺寸、颜色、hover 和 focus-visible 与 MoonBox 登录页视觉一致。
- [ ] AC-UI-003 控件不得造成登录卡片高度、字段间距、“记住我”、登录按钮或错误反馈区域抖动。
- [ ] AC-UI-004 移动视口下控件仍可点按，不超出登录卡片边界，不遮挡主要输入路径。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 `/req-complete` 必须提供 `prototype/web/context.md`，拆解页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [ ] AC-PROTOTYPE-002 `/req-opsx` 的 Change `design.md` 必须写入登录页密码显隐控件的 UI Skeleton，包含登录页路由、登录卡片、密码字段容器、图标按钮插槽、错误反馈区和可测选择器。
- [ ] AC-PROTOTYPE-003 `/opsx-apply` 必须在 1440px 桌面视口完成视觉验收，确认密码字段控件对齐、间距、焦点态、登录卡片布局和错误反馈区域不回归。
- [ ] AC-PROTOTYPE-004 `/opsx-apply` 必须覆盖关键交互验收：默认隐藏、显示密码、隐藏密码、键盘触发、登录提交和登录失败反馈。
- [ ] AC-PROTOTYPE-005 `/opsx-archive` 前必须确认 linked REQ 与最终 Change 设计、实现证据、1440px 截图、computed style 结果和 Mock/API 边界一致。

## 横切 AC（knowledge-base）

无横切 AC。本需求为 Web 前台登录页字段级体验增强，不命中 `admin-list`、`admin-form`、`admin-modal` 或 `media-upload` 知识库标签。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: update-login-password-visibility-toggle
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

