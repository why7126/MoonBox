# web-admin-crud-list-template Specification

## Purpose
定义 MoonBox 管理后台 CRUD 列表页模板、通用组件边界、交互一致性与 UI 验收约束，作为后续后台列表型页面的复用基线。

## Requirements
### Requirement: 后台 CRUD 列表页模板
系统 SHALL 提供管理后台 CRUD 列表页模板，用于承载后续列表型后台页面。

#### Scenario: 使用模板创建列表页
- **WHEN** 开发者创建新的后台 CRUD 列表页
- **THEN** 系统 SHALL 提供页面标题区、主操作区、筛选区、表格区、分页区、加载状态、空状态、错误状态和操作反馈区域
- **AND** 模板 SHALL 允许页面传入业务字段、筛选项、表格列、行级操作、状态标签和表单内容

#### Scenario: 模板适配后台 Shell
- **WHEN** CRUD 列表页运行在管理后台受保护页面内
- **THEN** 模板 SHALL 与现有后台 Shell、页头、导航和全局反馈区域兼容
- **AND** 模板不得引入冲突布局、重复导航或营销式页面结构

### Requirement: 后台列表页通用组件边界
系统 SHALL 抽取或规范后台列表页通用组件边界，避免每个后台列表页重复实现筛选、表格、分页、弹窗和 toast 行为。

#### Scenario: 复用列表页组件
- **WHEN** 后台业务页面使用 CRUD 列表页模板
- **THEN** 系统 SHALL 支持复用筛选栏、数据表格、分页、确认弹窗、表单弹窗、toast、空状态和加载状态组件或等价组合模式
- **AND** 业务页面 SHALL 只保留业务字段、接口调用和业务规则

#### Scenario: 避免复制页面级实现
- **WHEN** 新增后台 CRUD 列表页
- **THEN** 实现 SHALL 优先使用模板和通用组件
- **AND** 不得以复制用户管理页大段 JSX/CSS 作为默认创建方式

### Requirement: CRUD 操作一致性
系统 SHALL 为后台 CRUD 列表页的新增、编辑、删除、启用、禁用、重置或等价状态操作提供一致的入口、确认和反馈。

#### Scenario: 状态变更确认
- **WHEN** 后台管理员触发删除、启用、禁用、重置或等价状态变更操作
- **THEN** 系统 SHALL 使用设计系统确认弹窗
- **AND** 系统不得调用 `window.confirm`

#### Scenario: 操作反馈与刷新
- **WHEN** 后台管理员完成新增、编辑、删除或状态变更操作
- **THEN** 系统 SHALL 使用 fixed toast 展示成功或失败反馈
- **AND** 系统 SHALL 按模板规则刷新列表数据、分页状态和筛选条件

### Requirement: 筛选表格分页一致性
系统 SHALL 保证后台 CRUD 列表页的筛选、表格和分页体验与用户管理页基准一致。

#### Scenario: 筛选条件变化
- **WHEN** 后台管理员提交或重置筛选条件
- **THEN** 系统 SHALL 刷新列表结果、分页状态和空态提示
- **AND** 列表结果、分页状态和空态提示 SHALL 与当前筛选条件一致

#### Scenario: 分页 DOM 基准
- **WHEN** 后台 CRUD 列表页展示分页
- **THEN** 系统 SHALL 将总数展示在左侧
- **AND** 系统 SHALL 将翻页、页码、“每页显示”文案和条数下拉展示在右侧

#### Scenario: 表格行内操作
- **WHEN** 表格列较多或发生横向滚动
- **THEN** 行内操作列 SHALL 保持易访问
- **AND** 列宽、操作区和状态标签不得因内容变化造成明显布局跳动

### Requirement: 弹窗宽度与滚动治理
系统 SHALL 对后台 CRUD 列表页中的新增、编辑和确认弹窗执行宽度与滚动治理。

#### Scenario: 弹窗 class 约束
- **WHEN** 实现表单弹窗或确认弹窗
- **THEN** TSX 或模板实现 SHALL 避免通用 `modal-card` 与专属宽度类并存
- **AND** 不得让通用样式覆盖业务弹窗宽度

#### Scenario: 弹窗浏览器验收
- **WHEN** 在浏览器中验收新增、编辑或确认弹窗
- **THEN** 系统 SHALL 通过 computed style 确认最终宽度符合设计预期
- **AND** 低视口下弹窗 body SHALL 可滚动，底部主操作和取消操作 SHALL 可访问
- **AND** 弹窗遮罩不得吞掉内部滚动或导致页面主体误滚动

### Requirement: 后台模板 UI 约束
系统 SHALL 遵循 MoonBox 管理后台 UI 规则和后台列表页横切验收要求。

#### Scenario: 管理后台视觉一致
- **WHEN** 展示后台 CRUD 列表页模板
- **THEN** 页面 SHALL 保持近直角、细线、克制金色强调和后台信息密度
- **AND** 不得引入强装饰风格、大圆角卡片网格或与后台任务无关的营销式元素

#### Scenario: 窄屏与状态稳定
- **WHEN** 后台 CRUD 列表页在常见窄屏或加载、空数据、错误状态下展示
- **THEN** 页面文字不得重叠，控件不得互相遮挡
- **AND** 加载、空状态和错误状态不得造成页面大幅跳动或主要操作不可恢复
