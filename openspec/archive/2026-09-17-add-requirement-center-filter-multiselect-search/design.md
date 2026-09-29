## 背景

REQ-0033 要求增强前台需求中心现有筛选工具栏：枚举维度支持复选、多选、下拉内搜索、稳定排序、选中摘要和清空能力。该需求已纳入 `sprint-006`，来源文档位于 `issues/requirements/review/REQ-0033-requirement-center-filter-multiselect-search/`。

当前需求中心已具备 9 阶段看板、真实数据上下文、对象类型/负责人/分级/Sprint 筛选、关键词搜索、刷新保留筛选条件、权限态和空态。首版变更只增强前端筛选交互和客户端过滤组合，不改变生命周期阶段、卡片动作、事实源、授权边界、DB 或部署拓扑。

原型输入：

- `issues/requirements/review/REQ-0033-requirement-center-filter-multiselect-search/prototype/web/context.md`
- `issues/requirements/review/REQ-0033-requirement-center-filter-multiselect-search/prototype/web/prototype.html`

## 目标 / 非目标

**目标：**

- 将适合枚举选择的筛选维度升级为可复选、多选、可下拉内搜索的工具栏控件。
- 明确同维 OR、跨维 AND 的筛选组合语义，并保持统计区、9 阶段列、卡片列表和空态一致。
- 保持筛选状态在手动刷新、主题切换、文档抽屉开关和下拉搜索中的稳定性。
- 用稳定排序规则提升 Sprint、需求优先级、BUG 严重性、负责人、阶段和类型选项的扫描效率。
- 保持深浅主题、1440px 桌面视口、窄屏摘要、键盘可达和 computed style 验收要求。

**非目标：**

- 不新增服务端分页、服务端高级查询语言或个人筛选模板。
- 不改变 REQ、BUG、Change、Sprint 的事实源、授权边界、阶段映射或统计口径。
- 不新增数据库迁移、对象存储路径、后台异步任务或部署拓扑。
- 不强制新增 URL 参数或浏览器刷新后的筛选持久化；若实现复用既有策略，需在验收证据中说明。

## 设计决策

### D1. 筛选维度模型

使用统一的筛选维度模型表达枚举控件：维度 ID、显示名称、候选项、选中值集合、排序器、搜索匹配器、摘要渲染器和清空能力。对象类型如果现有实现使用分段控件，可以保留分段交互；若升级为下拉，必须保持“全部、需求、缺陷、独立 Change”业务顺序。

备选方案是为每个维度单独实现一套状态和列表逻辑。该方案短期简单，但会重复清空、搜索、排序、摘要和键盘行为，后续 REQ-0032 的 Sprint 状态展示也更难复用，因此不采用。

### D2. 过滤语义

同一维度内多个选项使用 OR 语义，不同维度之间使用 AND 语义。全局关键词搜索继续与筛选维度 AND 组合。统计区和看板卡片必须共用同一过滤结果，避免出现阶段数量、总数和卡片不一致。

### D3. 搜索与排序

下拉内搜索只过滤当前维度候选项，不改变已选集合。候选项搜索至少匹配用户可见名称；Sprint、REQ、BUG、Change 或其他含稳定 ID 的选项同时匹配 ID。搜索清空后恢复完整排序。

排序规则：

- Sprint：当前迭代或最近迭代优先，随后按编号或更新时间倒序，证据不足时按 ID 稳定排序。
- 阶段：按需求中心 9 阶段业务顺序。
- 分级：需求优先级按 P0、P1、P2、P3 展示，BUG 严重性按 blocker、critical、high、medium、low 展示；同一“分级”筛选控件内分组呈现，避免将 BUG 套入需求 P 值。
- Sprint 未纳入项：Sprint 候选项末尾追加“未纳入 Sprint”合成候选项，匹配无明确 Sprint 归属的卡片；Sprint 全选必须包含该候选项，清空 Sprint 维度仍表示不按 Sprint 过滤。
- 负责人：当前用户或最近参与者优先，随后按展示名或 ID 稳定排序。
- 类型：全部、需求、缺陷、独立 Change 或当前业务顺序。

### D4. UI Contract

- 事实源优先级：需求中心上下文 API 返回的授权对象和筛选候选项优先；前端派生候选项只能来自当前已授权对象集合，不能从无权对象、隐藏原始文档或本地示例数据推断。
- 品牌与 Token：沿用 MoonBox Ops 工作台视觉体系，近直角、细边框、高信息密度、MoonBox 金色强调，深浅主题均可读。
- 组件：工具栏触发器、Popover、搜索输入、复选框候选项、内部滚动列表、单维清空、无结果空态、全局清空、选中摘要和默认范围摘要。
- 交互状态：closed、open、searching、empty、checked、unchecked、disabled、hover、focus、keyboard active、loading-preserved、select-all-visible。
- 筛选顺序：筛选容器内按 Sprint、分级、负责人、阶段排序；Sprint 候选只展示“进行中 / 已归档”两类状态，“当前迭代”作为同行辅助标签，并追加“未纳入 Sprint”合成候选项；当 Sprint 选中集合等于默认 Sprint 范围时，外层筛选数量保持默认态，Sprint 触发器展示“默认 Sprint 范围”，手动改变 Sprint 选择后再展示选项名或已选数量；分级候选项分为“需求优先级”和“缺陷严重性”，P 值与说明同行展示。
- 权限规则：筛选候选项、数量、搜索提示和错误态只显示当前用户有权访问的上下文；筛选不得作为访问控制依据。
- Mock/API 边界：首版优先复用现有需求中心上下文和前端已加载对象；不新增 API 字段。若实现发现现有响应无法提供必要候选项或 ID，必须更新本 Change 范围，补 OpenAPI/Orval/API 文档和观测声明。
- computed style 验收点：触发器高度与工具栏对齐、Popover 宽度与最大高度、复选框尺寸、focus ring、边框/背景/文字颜色、滚动容器高度、长文本截断和窄屏摘要。

### D5. UI Skeleton

- 页面结构：保留当前需求中心 Shell、标题区、统计区、工具栏、9 阶段横向看板、文档抽屉和 AI 入口结构。
- 工具栏：全局搜索、对象类型入口、筛选容器、刷新按钮和全局清空入口在同一工作区内稳定排布；筛选容器内的多选维度顺序为 Sprint、分级、负责人、阶段。
- 多选下拉：触发器展示占位、默认范围摘要或已选摘要；同一筛选浮层内各触发器使用统一 label 列宽，确保 Sprint、分级、负责人、阶段的摘要文案从同一水平位置开始；Popover 内从上到下为搜索输入、候选项列表、无结果空态或内部滚动、底部全选当前结果/清空/已选数量反馈。
- 状态容器：默认、打开、搜索匹配、搜索无结果、多选摘要、禁用候选项、权限空候选项、刷新保留筛选、窄屏折行或数量摘要。
- 可测 selector 建议：`[data-testid="requirement-filter-toolbar"]`、`[data-testid="requirement-filter-trigger-<dimension>"]`、`[data-testid="requirement-filter-popover-<dimension>"]`、`[data-testid="requirement-filter-search-<dimension>"]`、`[data-testid="requirement-filter-option-<dimension>-<value>"]`、`[data-testid="requirement-filter-clear-<dimension>"]`、`[data-testid="requirement-filter-clear-all"]`。
- 1440px 验收焦点：默认工具栏、展开下拉、搜索无结果、多选摘要、筛选触发器摘要左侧对齐、候选项内部滚动、刷新保留筛选、深浅主题和文本溢出。

## product_data_collection_observability

```yaml
status: not_applicable
affected_layers: []
reason: 本 Change 首版仅增强前台需求中心筛选控件、客户端候选项搜索、筛选组合和 UI 验收；不新增或修改 API 请求头、响应字段、请求封装、数据库、请求日志、行为事件、Task Trace、对象存储或 Agent Workflow。
validation: opsx-apply 阶段需验证无 OpenAPI/Orval/API 文档差异、无新增请求日志字段、无新增行为事件和无 DB 迁移；若实现新增筛选行为事件、URL 持久化、服务端候选项或服务端查询，必须改为 applicable 并补齐标准验证。
```

## 风险 / 取舍

- [Risk] 多选摘要过长挤压刷新按钮或搜索框。→ 使用少量展示名称、较多数量摘要和窄屏数量优先策略。
- [Risk] 搜索候选项时误清空已选条件。→ 下拉搜索状态与选中集合分离，搜索清空只恢复候选项可见范围。
- [Risk] 前端派生候选项暴露无权对象数量。→ 候选项来源限制为授权上下文；错误和空态脱敏。
- [Risk] 与 REQ-0032 Sprint 下拉状态展示存在组件重叠。→ 多选组件承载通用交互，Sprint 状态展示作为候选项内容增强，避免重复实现。

## 迁移计划

本变更不需要数据迁移。发布时随前端需求中心代码上线；如出现筛选异常，可回退到上一版前端构建，服务端事实源和数据库无需回滚。

## 待确认问题

- 当前实现是否已有 URL 参数或本地最近筛选策略可复用，需要在 `/opsx-apply` 读代码后确认；首版不强制新增持久化。
- 对象类型维度是否保持现有分段控件还是统一进入多选下拉，由实现阶段根据当前布局密度决定，但必须保留组合语义和统计一致性。
