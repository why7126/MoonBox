---
requirement_id: REQ-0004-admin-user-management
acceptance_status: passed
created_at: 2026-08-07 22:15:09
updated_at: 2026-08-08 23:37:38
---

# 验收清单

## 功能 AC

- [x] AC-001 用户管理入口位于管理后台 `SYSTEM` 或等价系统分组，页面标题为“用户管理”或等价文案。
- [x] AC-002 用户列表展示头像、用户名、昵称、角色、状态、空间数、最近登录时间、创建时间和操作列。
- [x] AC-003 搜索框支持按用户名和昵称筛选，角色筛选仅包含“后台管理员”和“前台用户”。
- [x] AC-004 状态筛选仅包含“全部状态”、待激活、正常和已冻结，不提供“已删除”；筛选变化后列表自动刷新，默认列表与“全部状态”不展示逻辑删除用户。
- [x] AC-005 分页展示用户总数、上一页、下一页、页码、“每页显示”文案和条数下拉框。
- [x] AC-006 新增用户弹窗包含用户名、头像、昵称和角色；用户名与角色标记为必填。
- [x] AC-007 用户名校验规则为全局唯一、4-32 位、仅允许字母和数字、必须以字母开头；不合法时阻止提交并定位字段。
- [x] AC-008 创建成功后用户状态为待激活，重复提交不得产生重复账号。
- [x] AC-009 编辑用户时用户名只读且不可修改；仅允许编辑头像、昵称和角色。
- [x] AC-010 冻结、解冻、删除和重置密码均要求二次确认、原因填写和防重复提交。
- [x] AC-011 冻结成功后，目标用户全部有效会话必须在 10 秒内失效。
- [x] AC-012 删除用户为逻辑删除，保留审计追溯所需数据，不执行物理删除。
- [x] AC-013 系统内置唯一超级管理员展示“系统内置”或等价标识，操作列显示不可操作。
- [x] AC-014 系统内置唯一超级管理员不得出现编辑、重置密码、冻结、解冻或删除入口。
- [x] AC-015 用户管理写操作记录操作者、操作对象、动作、前后值、原因、结果、时间和请求 ID。
- [x] AC-016 临时密码或密码重置结果仅展示一次，不进入日志、埋点或前端持久化。
- [x] AC-017 1280px 及以上桌面视口不破版；1440px 视口下对齐 `prototype/web/prototype.png` 的信息密度和布局结构。
- [x] AC-018 深浅主题下，状态标签、危险操作、二次确认弹窗和 toast 均保持可读、可辨识。

## 横切 AC（knowledge-base）

> 来源：`docs/knowledge-base/best-practices/admin-list-page-consistency.md`、`docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`、`docs/knowledge-base/best-practices/admin-media-upload-chain.md`。

- [x] AC-XCUT-001 用户列表分页 DOM 必须与用户管理基准一致：总数左侧，翻页、页码、“每页显示”文案和条数下拉框右侧。
- [x] AC-XCUT-002 用户管理成功/失败反馈使用 fixed toast，不得引发布局位移或挤压列表、分页、弹窗内容。
- [x] AC-XCUT-003 冻结、解冻、删除、重置密码等状态变更必须使用设计系统确认弹窗，不得调用 `window.confirm`。
- [x] AC-XCUT-004 新增/编辑用户弹窗实现不得同时使用通用 `modal-card` 与专属宽度类，避免 CSS 级联导致宽度失效。
- [x] AC-XCUT-005 新增/编辑用户弹窗在实现验收中必须检查 computed width，确保与设计预期一致且不被通用弹窗样式覆盖。
- [x] AC-XCUT-006 矮视口下用户弹窗 body 必须可滚动，底部操作按钮可访问，页面背景不得吞掉滚动。
- [x] AC-XCUT-007 头像上传必须具备 `idle -> uploading -> done/failed` 状态机，并在上传中禁用重复提交。
- [x] AC-XCUT-008 头像上传成功后必须在同一会话立即回显到弹窗头像和列表头像，不依赖刷新页面。
- [x] AC-XCUT-009 Docker 本地环境 `:3000` 边界必须能完成头像上传到 MinIO `images/avatars/`、经授权后台接口读取和同会话回显验收。


## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-08 23:37:38
accepted_by: workflow-sync
source_change: add-admin-user-management
source_sprint: sprint-001
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

