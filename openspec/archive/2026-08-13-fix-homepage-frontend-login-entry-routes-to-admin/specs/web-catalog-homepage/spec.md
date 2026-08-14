# web-catalog-homepage Specification Delta

## MODIFIED Requirements

### Requirement: 官网首页首屏内容保持
系统 MUST 保持首页首屏左侧定位、标题、说明文案和 CTA 入口，不因品牌视觉更新或后台能力引入改变既有前台业务含义。

#### Scenario: 首屏文案可见
- **WHEN** 访客打开官网首页
- **THEN** 页面展示 `AI 原生软件工厂`
- **AND** 页面展示 `打开宝盒，拥有一家软件公司`
- **AND** 页面展示 MoonBox 将 Harness、Agent 工作流与产品知识组织到同一座 AI 原生软件工厂的说明

#### Scenario: 首页 CTA 进入前台登录入口
- **WHEN** 访客点击 `开启 MoonBox` 或 `打开第一个项目`
- **THEN** 系统显示 Web 前台登录页
- **AND** 系统不得跳转到 `/admin`
- **AND** 系统不得展示管理后台登录页

#### Scenario: 后台入口不由首页 CTA 触发
- **WHEN** 访客停留在官网首页并点击首页前台 CTA
- **THEN** 系统保持前台入口语义
- **AND** 后台登录页只允许通过明确访问 `/admin` 或具备权限的后台入口出现
