# web-catalog-homepage Delta

## MODIFIED Requirements

### Requirement: 官网首页首屏内容保持
系统 MUST 保持首页首屏左侧定位、标题、说明文案和 CTA 入口，不因品牌视觉更新改变既有业务含义。

#### Scenario: 首屏文案可见
- **WHEN** 访客打开官网首页
- **THEN** 页面展示 `AI 原生软件工厂`
- **AND** 页面展示 `打开宝盒，拥有一家软件公司`
- **AND** 页面展示 MoonBox 将 Harness、Agent 工作流与产品知识组织到同一座 AI 原生软件工厂的说明

#### Scenario: 首页 CTA 进入独立登录页
- **WHEN** 访客点击 `开启 MoonBox` 或 `打开第一个项目`
- **THEN** 系统进入 `/login` 前台登录页
- **AND** 浏览器地址不包含 `#login`
- **AND** 本首页能力不定义登录页表单、认证或返回首页行为
