# web-catalog-login-page Delta

## MODIFIED Requirements

### Requirement: 登录页入口与页面状态
系统 MUST 提供 `/login` Web 登录页入口，使首页登录相关 CTA 能进入同一个独立登录页，并以路径路由表达登录页当前状态。

#### Scenario: 首页 CTA 进入登录页
- **WHEN** 访客在官网首页点击登录相关 CTA
- **THEN** 系统显示 Web 登录页
- **AND** 浏览器路径为 `/login`
- **AND** 浏览器地址不包含 `#login`
- **AND** 首页主体内容不再作为当前主交互界面展示

#### Scenario: 直接访问登录页状态
- **WHEN** 访客直接打开 `/login`
- **THEN** 系统显示 Web 登录页
- **AND** 用户名输入框可成为首个可填写字段
- **AND** 页面不展示管理后台登录页

#### Scenario: 登录后进入前台需求中心
- **WHEN** 用户在 `/login` 提交前台登录表单
- **THEN** 系统进入 `/requirements`
- **AND** 系统调用既有后台登录 API
- **AND** 登录成功后保存后台 session 与前台进入态
- **AND** `/requirements` 不得显示管理后台登录页

#### Scenario: 后台入口未登录时使用统一登录页
- **WHEN** 用户未登录并访问 `/admin`
- **THEN** 系统回到 `/login`
- **AND** 页面显示统一 MoonBox 登录页
- **AND** 页面不得显示独立管理后台登录页

#### Scenario: 未登录访问前台需求中心
- **WHEN** 用户未建立前台登录状态并访问 `/requirements`
- **THEN** 系统回到 `/login` 前台登录页
- **AND** 页面不展示管理后台登录页

#### Scenario: 需求中心识别已有后台权限
- **WHEN** 用户已建立前台登录状态
- **AND** 浏览器本地存在有效后台 admin session
- **AND** 用户进入 `/requirements`
- **THEN** 系统显示前台需求中心
- **AND** 用户菜单展示后端返回的当前用户名称
- **AND** 有后台权限时展示 `进入后台`

#### Scenario: 需求中心仅有前台登录状态
- **WHEN** 用户已建立前台登录状态
- **AND** 浏览器本地不存在后台 admin session
- **AND** 用户进入 `/requirements`
- **THEN** 系统显示前台需求中心
- **AND** 用户菜单不得显示 `未登录`
- **AND** 用户菜单不得展示 `进入后台`

#### Scenario: 需求中心匿名上下文使用前台用户名兜底
- **WHEN** 用户已建立前台登录状态
- **AND** 需求中心上下文返回空用户、空用户名或 `未登录`
- **THEN** 用户菜单显示前台登录用户名
- **AND** 用户菜单不得显示 `未登录`

### Requirement: 登录页返回首页
系统 MUST 在登录页提供返回首页入口，并在返回时恢复首页视图、清除登录页路由状态。

#### Scenario: 用户从登录页返回首页
- **WHEN** 用户点击登录页左上角的返回首页入口
- **THEN** 系统恢复官网首页视图
- **AND** 浏览器路径回到 `/`
- **AND** 浏览器地址不包含 `#login`
- **AND** 登录页表单、遮罩和登录卡片不再作为当前主交互界面展示
