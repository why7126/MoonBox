## MODIFIED Requirements

### Requirement: 后台模板 UI 约束

系统 SHALL 遵循 MoonBox 管理后台 UI 规则和后台列表页横切验收要求。

#### Scenario: 管理后台对齐现代 Ops 视觉系统

- **WHEN** 展示后台 CRUD 列表页模板
- **THEN** 页面 SHALL 使用现代 Ops 工作台 Token
- **AND** 后台 Shell、列表、筛选、表格、分页、状态标签、确认弹窗和 toast SHALL 与登录后产品工作台保持视觉一致
- **AND** 页面 SHALL 保持高信息密度、清晰状态、低干扰和可扫描的操作层级
- **AND** 页面不得引入强装饰风格、大圆角卡片网格、厚重阴影或与后台任务无关的营销式元素

#### Scenario: 后台列表页继承横切预防清单

- **WHEN** 后台 CRUD 列表页迁移到现代 Ops 视觉系统
- **THEN** 分页 DOM 必须保持总数在左、翻页和条数下拉在右的基准
- **AND** 成功和失败反馈必须继续使用 fixed toast
- **AND** 删除、冻结、重置、恢复默认或等价危险操作必须使用设计系统确认弹窗
- **AND** 状态变更不得调用 `window.confirm`
- **AND** 筛选条件变化后，结果、分页和空态必须与当前条件一致

### Requirement: 弹窗宽度与滚动治理

系统 SHALL 对后台 CRUD 列表页中的新增、编辑和确认弹窗执行宽度与滚动治理。

#### Scenario: 现代 Ops 弹窗完成 computed style 验收

- **WHEN** 在浏览器中验收新增、编辑、确认或设置弹窗
- **THEN** 系统 SHALL 通过 computed style 确认最终宽度、背景、边框、圆角、阴影和滚动规则符合现代 Ops 设计预期
- **AND** TSX 或模板实现 SHALL 避免通用 `modal-card` 与专属宽度类并存
- **AND** 低视口下弹窗 body SHALL 可滚动，底部主操作和取消操作 SHALL 可访问
- **AND** 弹窗遮罩不得吞掉内部滚动或导致页面主体误滚动
