# web-catalog-login-page Specification Delta

## MODIFIED Requirements

### Requirement: 登录页入口与页面状态
系统 MUST 提供 Web 前台登录页入口，使首页登录相关 CTA 能进入同一个前台登录页，并通过 `#login` 或等价前端状态表达登录页当前状态。

#### Scenario: 首页 CTA 进入前台登录页
- **WHEN** 访客在官网首页点击 `开启 MoonBox` 或 `打开第一个项目`
- **THEN** 系统显示 Web 前台登录页
- **AND** 首页主体内容不再作为当前主交互界面展示
- **AND** 系统不得展示管理后台登录页
- **AND** 当前路径不得变为 `/admin`

#### Scenario: 直接访问登录页状态
- **WHEN** 访客直接打开带 `#login` 或等价登录状态的地址
- **THEN** 系统显示 Web 前台登录页
- **AND** 用户名输入框可成为首个可填写字段

#### Scenario: 原型提交进入前台需求中心
- **WHEN** 访客在当前前台登录原型中填写用户名和密码并点击 `登录并开启宝盒`
- **THEN** 系统不得发起真实后端鉴权请求
- **AND** 系统不得跳转到 `/admin`
- **AND** 系统必须进入前台需求中心 `/requirements`
