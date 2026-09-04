# 设计：UI 参考稿复刻治理流程

## 目标

把“全面贴近附件”“一对一复刻”“保持与某页面一致”这类 UI 诉求从主观描述转成可执行、可采样、可分批验收的视觉契约，减少后期靠用户逐元素指出偏差。

## 治理模型

UI 参考稿复刻分为三个保真模式：

| 模式 | 适用 | 验收口径 |
|---|---|---|
| 一对一复刻 | 用户明确要求与附件、HTML、截图或既有页面一致 | 组件结构、selector、computed style 和关键状态逐项对齐 |
| 风格迁移 | 用户要求“靠拢”“借鉴风格”，但保留当前信息架构 | 先锁定可迁移 token、组件风格和不可迁移边界 |
| 局部一致 | 用户只要求某个区域对齐参考稿 | 只为目标组件建立契约，非目标写入排除项 |

## UI Reference Replication Contract

当 Change 涉及 UI 参考稿复刻，`design.md` 需要新增 `UI Reference Replication Contract`，至少包含：

- 参考事实源：附件 HTML、截图、既有页面、当前实现截图、业务语义保留项和冲突优先级。
- 组件清单：页面壳、品牌区、标题区、指标卡、筛选区、看板列头、空列、任务卡、标签、按钮、浮层、响应式和滚动/sticky。
- Selector 映射：参考稿 selector、目标实现 selector、测试 selector、组件文件、状态类和是否纳入本批。
- 视觉契约：字体、字号、字重、行高、颜色、背景、边框、圆角、阴影、padding、gap、宽高、overflow、position、z-index 和 hover/focus/open/collapsed 状态。
- Computed style 采样清单：页面、视口、主题、交互状态、selector、期望属性、当前值、验收阈值和证据入口。
- 分批实现计划：先壳层与布局，再组件组，再交互/响应式，最后视觉回归；每批都需要截图或 computed style 摘要。
- 非目标和保留项：不复制的参考稿元素、保留的产品语义、业务能力和数据边界。

## 分批门禁

参考稿复刻不得只用单个“大视觉升级”任务闭环。推荐批次：

1. 页面壳、品牌区和标题区。
2. 指标卡、筛选区和主要工具按钮。
3. 看板列头、空列、列体和 sticky/滚动边界。
4. 任务卡、标签、文档入口、状态和动作区。
5. 弹窗、Popover、菜单和关键交互状态。
6. 移动端、窄视口、横向滚动和文本溢出。

每批完成条件：目标 selector 已映射，关键 computed style 已采样，截图或等价视觉证据已记录，非目标未被误改。

## 影响面

- `rules/ui-design.md`：新增参考稿复刻规则。
- `docs/standards/prototype-ui-acceptance.md`：新增合同模板、selector 映射和采样清单。
- `.agents/skills/*`：让 explore/req/opsx 阶段承接同一复刻契约。
- `AGENTS.md`、`rules/agent-context-budget.md`：补充入口和读取边界。

## 不涉及

- 不修改 MoonBox 产品工作台当前实现。
- 不新增前端自动截图脚本。
- 不修改正式 `openspec/specs/`，待归档时由 delta 合并。
