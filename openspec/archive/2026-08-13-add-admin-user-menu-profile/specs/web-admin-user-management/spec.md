# web-admin-user-management Delta

## ADDED Requirements

### Requirement: 用户菜单个人资料 Modal

系统 MUST 在管理后台用户菜单中提供“个人资料”入口，并以 Modal 形态支持当前登录用户修改自己的头像和昵称。

#### Scenario: 用户菜单打开个人资料 Modal

- **GIVEN** 后台管理员已登录管理后台
- **WHEN** 管理员打开用户菜单并点击“个人资料”
- **THEN** 前端必须打开个人资料 Modal
- **AND** 前端不得仅展示占位 toast
- **AND** 前端不得跳转到独立页面或打开抽屉
- **AND** 个人资料入口必须与“修改密码”“界面主题”“退出登录”等菜单项保持同一视觉体系

#### Scenario: Modal 只展示个人资料相关字段

- **GIVEN** 个人资料 Modal 已打开
- **THEN** Modal 必须展示用户名、角色摘要、单个头像预览位和昵称输入项
- **AND** Modal 不得展示角色、状态、冻结、删除、重置密码、空间数、最近登录时间或系统内置超级管理员操作
- **AND** Modal 不得与修改密码表单混成同一个表单

#### Scenario: 头像上传区复用创建用户交互

- **GIVEN** 个人资料 Modal 已打开
- **WHEN** 管理员查看头像上传区
- **THEN** 头像上传区必须参照创建用户表单交互
- **AND** 头像上传区必须只展示一个 `admin-avatar large` 等价头像预览位
- **AND** 右侧必须展示格式提示和上传/更换按钮
- **AND** 文件选择必须通过隐藏 file input 触发
- **AND** Modal 内不得同时展示身份摘要头像和上传区头像两个头像图标

#### Scenario: 头像上传状态与即时预览

- **GIVEN** 个人资料 Modal 已打开
- **WHEN** 管理员上传或更换头像
- **THEN** 上传组件必须具备 `idle -> uploading -> done/failed` 状态机
- **AND** 上传中必须禁用重复选择和重复提交
- **AND** 上传失败后必须展示受控错误并允许重试
- **AND** 上传成功后必须在 Modal 单头像预览位即时回显后端返回的持久头像 URL
- **AND** 保存前不得用临时 `blob:` URL 污染当前用户摘要

#### Scenario: 头像上传格式和大小

- **WHEN** 管理员选择头像文件
- **THEN** 系统必须支持 JPG、PNG、WEBP
- **AND** 单文件大小不得超过 2MB
- **AND** 类型不支持或文件过大时必须在 Modal 内展示受控错误

#### Scenario: 保存和取消

- **GIVEN** 个人资料 Modal 已打开
- **WHEN** 管理员点击取消、关闭 Modal 或未保存离开
- **THEN** 前端必须放弃未保存的昵称和头像变更
- **AND** 不得污染当前用户摘要或用户菜单展示

#### Scenario: 保存成功刷新用户菜单

- **GIVEN** 个人资料 Modal 已打开
- **WHEN** 管理员保存有效头像和昵称
- **THEN** 前端必须在保存期间禁用重复提交并展示保存中状态
- **AND** 保存成功后必须刷新当前用户摘要和本地会话缓存
- **AND** 用户菜单头像、昵称或用户名展示必须与后端返回结果一致
- **AND** 用户菜单必须优先显示昵称，昵称为空时回退显示用户名

#### Scenario: 保存失败保留输入

- **GIVEN** 个人资料 Modal 已打开
- **WHEN** 当前用户资料更新失败
- **THEN** 前端必须保留用户已输入的昵称和头像选择状态
- **AND** 前端必须展示可恢复错误
- **AND** 管理员必须能够修正后重试

### Requirement: 个人资料 Modal 原型驱动验收

系统 MUST 将 REQ-0011 的 prototype 作为设计输入，并在实现、验收和归档前完成 UI Skeleton、1440px 视觉验收和最终一致性检查。

#### Scenario: Change 设计承接原型拆解

- **GIVEN** REQ-0011 提供 `prototype/web/context.md` 和 `prototype/web/prototype.html`
- **WHEN** 创建 OpenSpec Change
- **THEN** Change `design.md` 必须包含 UI Skeleton
- **AND** UI Skeleton 必须覆盖用户菜单入口、个人资料 Modal、创建用户同款头像上传结构、单头像预览位、昵称输入、底部保存 CTA、状态容器、数据依赖、可测选择器和 1440px 验收焦点

#### Scenario: 实现阶段完成 Modal 横切验收

- **WHEN** 实现个人资料 Modal
- **THEN** TSX 实现不得让通用 `modal-card` 与专属宽度类并存
- **AND** 必须通过浏览器 computed style 验收 Modal 最终宽度
- **AND** 低视口下 Modal body 必须可滚动，单头像预览位、昵称输入、错误提示、取消和保存按钮均可访问
- **AND** Modal 背景遮罩不得吞掉内部滚动，也不得导致页面主体误滚动
- **AND** 头像预览、上传/更换按钮、昵称输入、错误提示和底部操作区不得互相遮挡

#### Scenario: 实现阶段完成上传链路横切验收

- **WHEN** 实现个人资料头像上传
- **THEN** 上传成功后必须在同一会话立即回显到当前 Modal 和用户菜单展示链路
- **AND** 上传成功后的 URL 或对象引用不得写入日志中的敏感上下文
- **AND** Docker 本地 `:3000` 边界必须能完成头像上传、读取和回显验收
- **AND** 后端上传接口和对象访问路径必须在容器网络、浏览器访问和反向代理路径下保持一致

#### Scenario: 归档前完成 REQ 最终一致性检查

- **WHEN** 准备归档本 Change
- **THEN** 必须确认最终实现与 REQ-0011 的 requirement、acceptance、prototype 和 Change design 一致
- **AND** 必须记录 1440px 视觉验收证据或等价证据入口
