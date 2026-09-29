## 1. UI Skeleton And Contract

- [x] 1.1 阅读当前需求中心前端实现，确认现有筛选维度、数据源、selector 约定、测试框架和 URL/local 持久化行为。
- [x] 1.2 实现或重构筛选工具栏骨架，确保工具栏、触发器、popover、搜索输入、选项列表、空态、清空动作和响应式摘要容器在细化行为前具备稳定布局和测试 selector。
- [x] 1.3 在实现记录中声明 Mock/API 边界：确认当前上下文 API 是否提供所需授权候选项和稳定 ID；若不足，先更新 Change 范围再新增 API 字段。

## 2. Filter State And Semantics

- [x] 2.1 用选中值集合、搜索文本、候选匹配、清空行为和触发器摘要建模枚举筛选维度。
- [x] 2.2 实现同维 OR、跨维 AND 语义，并让全局关键词搜索与已选筛选条件 AND 组合。
- [x] 2.3 保持过滤后的卡片、阶段数量、总数和无结果状态基于同一个过滤结果。
- [x] 2.4 在手动刷新、主题切换、文档抽屉开关和候选搜索文本变化时保留已选筛选状态。

## 3. Multi-select Dropdown UI

- [x] 3.1 为适用枚举维度增加 checkbox 选项行，支持点击文本或 checkbox，并覆盖 hover、focus、disabled、checked 和 unchecked 状态。
- [x] 3.2 增加下拉内候选搜索，匹配可见标签和可用稳定 ID，清空搜索后恢复完整排序候选。
- [x] 3.3 增加单维清空、全局清空、选中摘要、数量摘要、长文本截断和窄宽度摘要降级。
- [x] 3.4 为 Sprint、阶段/状态、优先级、负责人和类型增加稳定候选排序，并提供确定性的名称或 ID 降级排序。
- [x] 3.5 确保 popover 最大高度、内部滚动、Esc 关闭、外部点击关闭和键盘可达，不引发布局跳动。

## 4. Security And Observability Boundaries

- [x] 4.1 确保候选项、数量、搜索提示和错误均只来自授权后的需求中心上下文。
- [x] 4.2 验证空态或错误态不显示本机路径、堆栈、密钥、token、原始隐藏文档或未授权对象身份。
- [x] 4.3 确认未引入 API schema、请求封装、请求日志、行为事件、Task Trace、DB 迁移或对象存储变更；若需要其中任一项，先更新 design、spec、docs 和 validation。

## 5. Tests And Visual Evidence

- [x] 5.1 增加多选 OR/AND 语义、候选搜索、清空、排序、状态保留和权限安全候选的聚焦前端测试。
- [x] 5.2 增加或更新 1440px 默认工具栏、打开下拉、搜索无结果、多选摘要、内部滚动、深浅主题和窄宽度摘要的视觉/交互测试。
- [x] 5.3 采集触发器尺寸、popover 尺寸、checkbox 尺寸、focus ring、边框、背景、文字颜色和滚动容器高度的 computed style 证据。
- [x] 5.4 运行相关单元、组件、E2E 检查，并在 Change trace 记录命令结果。

## 6. Documentation And Consistency

- [x] 6.1 若实现决策改变持久化、对象类型 UI、API 边界或观测状态，更新 REQ-0033 acceptance 或 trace。
- [x] 6.2 归档前确认 requirement.md、acceptance.md、trace.md、Change design.md、spec delta、实现证据和验证结果一致。

## 验收返修记录

完整返修台账见 `acceptance-fixes.md`，本节仅保留可执行任务摘要。

- [x] F1 筛选顺序、分级表达、全选/清空和外部点击关闭已返修并验证。
- [x] F2 Sprint 全选包含“未纳入 Sprint”合成候选项已返修并验证。
- [x] F3 默认 Sprint 范围显示默认态文案、手动改选后再显示已选数量已返修并验证。
- [x] F4 筛选浮层内四个触发器 label 列宽统一、摘要左侧对齐已返修并验证。
