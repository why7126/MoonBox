## ADDED Requirements

### Requirement: 官网首页品牌入口
系统 MUST 在官网首页顶部展示 MoonBox 品牌入口，并使用 `moonbox-nav-logo.png` 作为左上角导航专用品牌 Logo。

#### Scenario: 访客打开首页看到品牌 Logo
- **WHEN** 未登录访客打开 MoonBox 官网首页
- **THEN** 页面顶部左侧展示 MoonBox 品牌 Logo
- **AND** Logo 使用 `/brand/moonbox/moonbox-nav-logo.png`
- **AND** Logo 来源于产品 Logo 大画布裁剪后的导航专用横版资产

#### Scenario: Logo 不破坏导航布局
- **WHEN** 首页在桌面端或移动端展示
- **THEN** Logo 不导致导航高度、对齐或相邻 CTA 出现明显布局跳动

### Requirement: 官网首页首屏产品视觉
系统 MUST 在官网首页首屏右侧展示 `image.png` 产品视觉，并保持主体清晰可辨。

#### Scenario: 桌面端展示右侧产品视觉
- **WHEN** 访客在桌面端打开官网首页
- **THEN** 首屏右侧展示 `image.png`
- **AND** 图片主体无明显变形、遮挡或过度裁切

#### Scenario: 移动端展示产品视觉
- **WHEN** 访客在移动端打开官网首页
- **THEN** 产品视觉可按响应式规则重排
- **AND** Logo、标题、CTA 和产品视觉不互相遮挡

### Requirement: 官网首页首屏内容保持
系统 MUST 保持首页首屏左侧定位、标题、说明文案和 CTA 入口，不因品牌视觉更新改变既有业务含义。

#### Scenario: 首屏文案可见
- **WHEN** 访客打开官网首页
- **THEN** 页面展示 `AI 原生软件工厂`
- **AND** 页面展示 `打开宝盒，拥有一家软件公司`
- **AND** 页面展示 MoonBox 将 Harness、Agent 工作流与产品知识组织到同一座 AI 原生软件工厂的说明

#### Scenario: 首页 CTA 进入登录入口
- **WHEN** 访客点击 `开启 MoonBox` 或 `打开第一个项目`
- **THEN** 系统进入既有登录页入口
- **AND** 本首页能力不定义登录页表单、认证或返回首页行为

### Requirement: 官网首页能力摘要
系统 MUST 在首页首屏下方保留三项核心能力摘要。

#### Scenario: 访客看到三项能力摘要
- **WHEN** 访客浏览首页首屏下方区域
- **THEN** 页面展示 `Agent 工作流`
- **AND** 页面展示 `产品知识库`
- **AND** 页面展示 `交付 Harness`

### Requirement: 首页 Patch 范围约束
系统 MUST 将本次首页变更限制为品牌 Logo、首屏产品视觉和相关展示约束，不得扩大到登录页、接口或数据层。

#### Scenario: 首页不出现登录页表单
- **WHEN** 访客停留在官网首页
- **THEN** 页面不展示用户名输入、密码输入、记住我、忘记密码、申请体验或返回首页入口

#### Scenario: 非首页能力不变
- **WHEN** 本 Change 实施完成
- **THEN** API、数据库、对象存储和管理后台能力不因本 Change 发生契约变化
