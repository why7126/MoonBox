## MODIFIED Requirements

### Requirement: 用户管理 UI 横切一致性
系统 SHALL 遵循 MoonBox 管理后台 UI 规则和用户管理横切验收要求，并将用户管理页作为后台 CRUD 列表页模板化适配的首个验收样板。

#### Scenario: 状态操作确认
- **WHEN** 后台管理员触发冻结、解冻、删除或重置密码
- **THEN** 系统使用设计系统确认弹窗，且不得调用 `window.confirm`

#### Scenario: Toast 不位移
- **WHEN** 用户管理页面展示成功或失败反馈
- **THEN** 系统使用 fixed toast，且不得引发布局位移或挤压列表、分页、弹窗内容

#### Scenario: 弹窗宽度与滚动
- **WHEN** 新增或编辑用户弹窗在桌面或低视口打开
- **THEN** computed width 与设计预期一致，弹窗 body 可滚动，底部操作按钮可访问

#### Scenario: 用户管理页模板化适配
- **WHEN** 用户管理页迁移到后台 CRUD 列表页模板或等价组合模式
- **THEN** 用户管理页 SHALL 保持用户列表、筛选、分页、创建、编辑、冻结、解冻、逻辑删除、重置密码、头像上传、临时密码展示和超级管理员保护能力无可感知回退
- **AND** 页面 SHALL 只保留用户管理业务字段、接口调用和业务规则
- **AND** 可复用的页面骨架、筛选、表格、分页、弹窗和 toast 行为 SHALL 收敛到模板或通用组件
