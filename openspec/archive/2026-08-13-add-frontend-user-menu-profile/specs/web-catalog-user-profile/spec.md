## ADDED Requirements

### Requirement: 前台用户菜单个人资料弹窗

MoonBox 前台需求中心 SHALL 在用户菜单中提供个人资料弹窗，允许当前登录用户维护自己的头像和昵称。

#### Scenario: 打开个人资料弹窗

- **GIVEN** 用户已登录并打开前台需求中心
- **AND** 左侧边栏处于展开态
- **WHEN** 用户打开底部用户菜单并点击“个人资料”
- **THEN** 系统 SHALL 关闭用户菜单
- **AND** 系统 SHALL 打开 `rc-*` 风格的个人资料弹窗
- **AND** 弹窗 SHALL 仅展示头像、昵称、仅用户名只读摘要、取消和保存操作
- **AND** 弹窗 SHALL 提供与后台个人资料 Modal 同构的标题行和右上角关闭按钮
- **AND** 弹窗 SHALL NOT 在昵称字段下展示保存后刷新菜单的实现说明文案

#### Scenario: 排除密码与后台管理字段

- **GIVEN** 用户打开个人资料弹窗
- **WHEN** 系统展示弹窗内容
- **THEN** 弹窗 SHALL NOT 展示密码修改字段
- **AND** 弹窗 SHALL NOT 展示角色、权限、账号状态、后台用户管理、重置密码、冻结或删除操作

### Requirement: 前台当前用户头像上传

前台个人资料弹窗 SHALL 复用现有对象存储头像上传链路，并在同一会话即时回显头像。

#### Scenario: 上传头像成功

- **GIVEN** 用户打开个人资料弹窗
- **WHEN** 用户选择符合类型和大小限制的 JPG、PNG 或 WebP 头像
- **THEN** 系统 SHALL 进入 uploading 状态
- **AND** 系统 SHALL 禁用重复选择和保存
- **WHEN** 上传接口返回持久头像 URL
- **THEN** 系统 SHALL 使用受保护头像读取链路获取头像内容
- **AND** 系统 SHALL 在弹窗内即时预览新头像
- **AND** 系统 SHALL 保存持久头像 URL，而不是保存 `blob:` URL

#### Scenario: 上传头像失败

- **GIVEN** 用户打开个人资料弹窗
- **WHEN** 头像类型不支持、文件超过 2MB、对象存储写入失败或受保护读取失败
- **THEN** 系统 SHALL 在弹窗内展示受控错误
- **AND** 系统 SHALL 保留上一个有效头像或当前有效预览
- **AND** 系统 SHALL 允许用户重新选择文件

### Requirement: 前台昵称修改与展示回退

前台个人资料弹窗 SHALL 支持当前用户修改昵称，并在昵称为空时回退展示用户名。

#### Scenario: 保存昵称

- **GIVEN** 用户打开个人资料弹窗
- **WHEN** 用户输入不超过 128 个字符的昵称并保存
- **THEN** 系统 SHALL 去除昵称首尾空白
- **AND** 系统 SHALL 保存清理后的昵称
- **AND** 前台用户菜单 SHALL 优先展示昵称

#### Scenario: 清空昵称

- **GIVEN** 用户打开个人资料弹窗
- **WHEN** 用户清空昵称并保存
- **THEN** 系统 SHALL 保存为空值或等价空状态
- **AND** 前台用户菜单 SHALL 回退展示用户名

### Requirement: 保存后刷新前台当前用户上下文

系统 SHALL 在个人资料保存成功后刷新前台当前用户上下文、用户菜单展示和本地会话缓存。

#### Scenario: 保存成功刷新菜单

- **GIVEN** 用户在个人资料弹窗中修改头像或昵称
- **WHEN** 用户点击保存且保存接口返回最新 user
- **THEN** 系统 SHALL 直接使用返回 user 更新前台 currentUser
- **AND** 系统 SHALL 刷新用户菜单头像、昵称或用户名展示
- **AND** 系统 SHALL 同步本地会话缓存
- **AND** 系统 SHALL 同步后台 admin session，使用户进入后台后后台用户菜单展示最新头像、昵称或用户名
- **AND** 系统 SHALL 不要求用户刷新页面

#### Scenario: 保存失败保留输入

- **GIVEN** 用户在个人资料弹窗中修改头像或昵称
- **WHEN** 保存接口返回失败
- **THEN** 系统 SHALL 保持弹窗打开
- **AND** 系统 SHALL 保留用户已输入内容
- **AND** 系统 SHALL 展示受控错误并允许重试

### Requirement: 原型驱动前台个人资料 UI 验收

该 Change SHALL 承接 REQ-0014 的 prototype-driven UI Gate，并在实现和归档前保留视觉证据。

#### Scenario: UI Skeleton 先行

- **GIVEN** Change 进入实现阶段
- **WHEN** 细节实现任务开始前
- **THEN** 实现 SHALL 先完成 UI Skeleton
- **AND** Skeleton SHALL 覆盖用户菜单入口、个人资料弹窗、头像上传状态、保存反馈和 currentUser 更新边界
- **AND** Skeleton SHALL 产出 1440px 视觉证据

#### Scenario: 视觉与样式验收

- **GIVEN** Change 实现完成
- **WHEN** 执行验收
- **THEN** 验收 SHALL 覆盖 1440px 用户菜单打开态、弹窗默认态、头像上传成功预览、上传失败提示、保存失败提示和保存成功菜单刷新
- **AND** 验收 SHALL 记录关键 computed style 或等价检查
- **AND** 验收 SHALL 确认前后台个人资料 Modal 交互结构一致，且前台仍使用 `rc-*` 视觉 token
- **AND** 验收 SHALL 确认前后台菜单头像均为 32px，个人资料弹窗头像均为 48px
- **AND** 验收 SHALL 确认前台昵称输入框文字、光标与背景具备可读对比
- **AND** 验收 SHALL 确认前后台主题偏好在同一 SPA 会话内跨路由同步
- **AND** 归档前 SHALL 确认 linked REQ 与 Change design、实现证据、视觉证据和 Mock/API 边界一致
