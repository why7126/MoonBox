## 背景

REQ-0034 要求需求中心进入页面时默认聚焦当前工作。当前需求中心已有 9 阶段看板、真实数据上下文、Sprint 多选筛选、对象类型/负责人/优先级筛选、独立 Change 卡片、刷新保留筛选条件和稳定快照机制。本变更不重做看板，也不新增范围按钮组或筛选下方提示模块；默认工作范围直接通过既有 Sprint 多选下拉选中当前 Sprint 集合和“未纳入 Sprint”表达。

来源文档：

- `issues/requirements/review/REQ-0034-requirement-center-default-current-iteration-cards/requirement.md`
- `issues/requirements/review/REQ-0034-requirement-center-default-current-iteration-cards/acceptance.md`
- `issues/requirements/review/REQ-0034-requirement-center-default-current-iteration-cards/prototype/web/context.md`
- `issues/requirements/review/REQ-0034-requirement-center-default-current-iteration-cards/prototype/web/prototype.html`

## 目标 / 非目标

**目标：**

- 默认视图聚焦当前迭代和未纳入 Sprint 范围，并覆盖 REQ、BUG 和独立 Change。
- 当前迭代识别以 Sprint 生命周期事实源为准，支持 0、1、多个当前迭代候选。
- 通过既有 Sprint 多选能力保留查看全部、历史、未纳入迭代和归档范围的入口，不新增独立范围筛选模块。
- 保持统计区、9 阶段列、卡片集合、空态、错误态和筛选状态一致。
- 覆盖原型驱动 UI Contract、UI Skeleton、1440px 和窄屏验收。
- 保持权限、安全脱敏、行为事件和请求日志边界清晰。

**非目标：**

- 不新增 Sprint 创建、启动、归档、评审或容量规划流程。
- 不改变 REQ、BUG、OpenSpec Change 的生命周期状态机和 9 阶段映射。
- 不删除历史、归档、未纳入迭代或全部范围查看能力。
- 不新增数据库表、迁移、对象存储路径、后台异步任务或部署拓扑。
- 不把前端筛选状态作为授权判断依据。

## 设计决策

### D1. 默认范围模型

需求中心不新增独立范围控件。首次进入页面、项目/空间上下文重置或用户点击清空全部筛选时，既有 Sprint 多选下拉默认选中当前 Sprint 集合和“未纳入 Sprint”；用户清空 Sprint 多选即查看全部对象，选择历史或归档 Sprint 即查看对应范围。用户显式调整 Sprint 多选后，普通手动刷新保留用户选择。

不采用额外的“当前迭代｜全部｜历史｜未纳入迭代｜归档”按钮组，因为需求中心已有 Sprint 多选，下拉选中状态足以表达当前迭代和未纳入 Sprint，并减少重复筛选层级。

### D2. 当前迭代事实源

当前迭代候选优先来自 `iterations/change/` 中 `status` 为 `planning` 或 `in_progress` 的有效 Sprint。`iterations/archive/` 默认不属于当前迭代。若未来存在显式 current Sprint 标记，需在实现阶段定义优先级并补测试；本 Change 首版不新增该配置。

当存在多个当前迭代候选时，Sprint 多选默认选中这些 Sprint 的并集并同时选中“未纳入 Sprint”，不按编号、更新时间或读取顺序任取一个。用户可以在同一下拉中取消某个当前 Sprint、取消未纳入 Sprint 或进一步选择单个 Sprint。

### D3. 卡片范围与统计一致

默认范围过滤必须作用于同一套授权对象集合，并同时驱动统计区、9 阶段列、卡片列表和筛选无结果/当前迭代空态。未授权对象不得参与范围候选、统计、搜索提示或异常详情。

独立 Change 归属当前迭代时，必须使用 Change 自身 iteration 或 Sprint `changes[]` 成员关系等真实事实源；不能因为关联 Issue 不可见而推断为独立当前卡片。

### D4. UI Contract

- 事实源优先级：需求中心上下文 API 与治理事实源优先；`prototype.html` 表达布局方向；`prototype/web/context.md` 表达状态矩阵；`acceptance.md` 表达验收边界；`rules/ui-design.md` 提供视觉 token。
- 页面与入口：前台 `/requirements` 需求中心，默认落点为当前迭代范围。
- 信息架构：保留 Shell、标题区、指标区、筛选工具栏、9 阶段看板、文档抽屉和阶段动作；不新增筛选模块下方提示模块。
- 视觉 token：沿用 MoonBox Ops 深浅主题、近直角、细边框、高信息密度和金色强调；不得新增营销式说明卡片。
- 交互状态：single-current、multi-current、no-current、no-card、custom-sprint-selection、error、loading-preserved。
- 图标与文案：用户可见文案在 Sprint 候选 meta 中使用“当前迭代”等产品化表达，不直接暴露脚本命令；不得新增独立范围按钮文案组。
- 权限规则：范围候选、数量、错误详情和搜索提示均只基于当前用户授权上下文。
- Mock/API 边界：原型仅表达结构，不代表 API 已接入；实现阶段需确认现有上下文 API 是否已提供 Sprint 状态、iteration、scope 和独立 Change 归属。若新增字段，必须同步 API 文档、OpenAPI/客户端类型和测试。
- computed style 验收点：Sprint 多选触发器高度、工具栏 gap、看板 sticky header、空态区域、深浅主题文本颜色、窄屏换行和横向滚动。

### D5. UI Skeleton

- 页面壳：复用需求中心主页面，不新增独立路由。
- 工具栏：全局搜索、对象类型、Sprint 多选、阶段/负责人/优先级多选、刷新、重置保持稳定布局。
- Sprint 状态：默认在 Sprint 多选中选中当前 Sprint 和“未纳入 Sprint”；多个当前迭代时显示“已选 N 项”；非当前范围通过用户显式 Sprint 选择或清空状态表达。
- 看板区：9 阶段列、横向滚动和 sticky header 保持现状，卡片密度不因默认 Sprint 选择发生跳动。
- 状态容器：无当前 Sprint、当前 Sprint 无卡片、筛选无结果、接口失败和权限不足必须是不同状态，不互相伪装。
- 可测 selector：复用 `[data-testid="requirement-filter-trigger-sprint"]`、`[data-testid="requirement-filter-popover-sprint"]`、`[data-testid="requirement-filter-option-sprint-<id>"]`、`[data-testid="requirement-filter-clear-sprint"]` 和 `[data-testid="requirement-filter-clear-all"]`；不得新增 `requirement-range-*` selector。
- 1440px 验收焦点：标题、指标、工具栏、Sprint 多选、9 阶段列头和首屏卡片稳定对齐；深浅主题清晰；文本不重叠。

## product_data_collection_observability

```yaml
status: applicable
affected_layers:
  - usage_events
  - request_logs
reason: 默认当前迭代范围会影响需求中心页面加载、范围切换、筛选重置、手动刷新和空间/项目切换；若后端聚合接口参与当前迭代识别，需要请求日志记录安全摘要。
validation: opsx-apply 阶段需验证行为事件只记录脱敏筛选上下文；请求日志不保存治理文档全文、本机路径、完整请求/响应体、密钥或 token；若接口契约无变化，记录无 OpenAPI/Orval/API 文档差异；若新增 API 字段，补齐 API 文档、OpenAPI、客户端类型和请求日志脱敏测试。
```

## Conflict Resolution

事实源优先级：

```text
prototype.html > prototype/web/context.md > acceptance.md > requirement.md > rules/ui-design.md > openspec/specs
```

本 Change 的原型用于表达结构、状态和布局方向；最终验收以 Change design、delta spec、acceptance、1440px/关键交互视觉证据、computed style、Mock/API 边界和 REQ 最终一致性回填共同为准。若实现阶段发现现有需求中心组件与原型存在冲突，优先保留父需求 REQ-0012 的 9 阶段看板、卡片密度、权限边界和文档入口，再局部调整 Sprint 多选默认状态。

## 风险 / 取舍

- [Risk] 默认当前迭代让用户误以为历史卡片不存在。→ 在 Sprint 多选中直接显示当前 Sprint + 未纳入 Sprint 选中状态，清空多选即可查看全部，选择历史/归档 Sprint 即可追溯。
- [Risk] 当前 Sprint 加未纳入对象导致默认范围过大。→ 默认保留规划前待处理对象，并在同一 Sprint 多选中提供取消“未纳入 Sprint”或单 Sprint 显式筛选。
- [Risk] 前端临时推断与后端事实源不一致。→ Sprint 候选和卡片归属以真实上下文和治理事实源为准，测试覆盖刷新与项目切换。
- [Risk] 观测字段可能记录过多上下文。→ 行为事件和请求日志只保留脱敏筛选摘要、结果数量、错误码和耗时。

## 迁移计划

本变更不需要数据库迁移。上线随需求中心前后端实现发布。若出现默认范围异常，可回退到上一版前端范围策略；服务端治理事实源不需要回滚。若实现新增 API 字段，回滚需同时回退客户端类型和 API 文档。

## 待确认问题

- 当前实现是否已有可复用的范围枚举或 URL/local persistence 策略，需要 `/opsx-apply` 读代码后确认。
- 当前上下文 API 是否已提供足够的 Sprint 状态、成员关系和独立 Change iteration 信息；若不足，需要在实现阶段扩大 API 契约范围。
