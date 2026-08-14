## MODIFIED Requirements

### Requirement: 用户管理 UI 横切一致性
系统 SHALL 遵循 MoonBox 管理后台 UI 规则和用户管理横切验收要求，并将用户管理页作为后台 CRUD 列表页模板化适配的首个验收样板。

#### Scenario: 后台侧边栏产品版本一致
- **WHEN** 后台管理员进入用户管理页面
- **THEN** 管理后台侧边栏品牌区域 MUST 展示 MoonBox 共享产品版本
- **AND** 该版本 MUST 与前台需求中心侧边栏展示的产品版本一致
- **AND** 后台用户管理页不得使用独立硬编码补丁号作为产品版本展示
