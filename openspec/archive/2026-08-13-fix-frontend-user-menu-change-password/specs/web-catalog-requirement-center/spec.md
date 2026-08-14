# web-catalog-requirement-center Delta

## ADDED Requirements

### Requirement: 前台用户菜单修改密码

系统 MUST 支持已登录前台用户从需求中心用户菜单发起自助修改密码，并在成功后清理完整本地会话。

#### Scenario: 前台菜单点击打开修改密码弹窗

- **GIVEN** 用户已登录前台并进入 `/requirements`
- **WHEN** 用户打开左侧底部用户菜单并点击“修改密码”
- **THEN** 系统必须关闭用户菜单
- **AND** 系统必须打开标题为“修改密码”的弹窗
- **AND** 弹窗必须包含“当前密码”“新密码”“确认新密码”三个输入项
- **AND** 弹窗文字、输入框、边框、光标和主按钮在前台深色与浅色主题中必须保持可读可填写

#### Scenario: 前台修改密码提交调用既有接口

- **GIVEN** 用户已打开前台修改密码弹窗
- **AND** 用户填写当前密码、新密码和确认新密码
- **AND** 两次新密码一致
- **WHEN** 用户点击“更新密码”
- **THEN** 系统必须调用 `/api/v1/admin/auth/change-password`
- **AND** 请求体必须包含 `current_password`、`new_password`、`confirm_password`
- **AND** 请求必须携带当前可用登录会话 token 的 Bearer 授权头
- **AND** 当用户只有 `moonbox.frontend.session.access_token` 且没有 `moonbox.admin.session` 时，系统必须使用 frontend session token 提交改密请求
- **AND** 后端必须允许任意正常登录用户通过该接口修改自己的密码，不得要求后台管理员角色
- **AND** 后台用户管理等管理接口必须继续要求后台管理员权限

#### Scenario: 前台修改密码成功后重新登录

- **WHEN** 前台修改密码接口返回成功
- **THEN** 系统必须清理 `moonbox.admin.session`
- **AND** 系统必须清理 `moonbox.frontend.session`
- **AND** 浏览器地址必须跳转到 `/login`
- **AND** 用户必须重新登录后才能回到前台需求中心

#### Scenario: 前台修改密码失败保留状态

- **WHEN** 前台修改密码接口返回错误
- **THEN** 修改密码弹窗必须保持打开
- **AND** 已填写内容不得被静默清空
- **AND** 页面必须展示接口返回的错误信息或默认失败提示
- **AND** 系统不得清理当前会话
- **AND** 用户继续修改任一密码输入项后，旧的提交级错误必须清除，避免与当前字段级错误同时展示

#### Scenario: 确认密码不一致不发起请求

- **GIVEN** 用户填写的新密码和确认新密码不一致
- **WHEN** 用户点击“更新密码”
- **THEN** 系统必须展示“两次输入的新密码不一致”
- **AND** 系统不得调用 `/api/v1/admin/auth/change-password`

#### Scenario: 后台修改密码流程保持不回归

- **WHEN** 用户进入后台用户管理页
- **AND** 通过后台用户菜单点击“修改密码”
- **THEN** 后台必须仍能打开修改密码弹窗
- **AND** 修改成功后必须清理后台会话并回到登录页
