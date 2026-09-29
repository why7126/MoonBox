---
requirement_id: REQ-0033-requirement-center-filter-multiselect-search
title: 需求中心筛选下拉框支持复选搜索多选与排序优化
acceptance_status: passed
owner: product
source: requirement.md
created_at: 2026-09-14 14:50:41
updated_at: 2026-09-29 14:41:41
---

# 验收标准

## 功能 AC

- [ ] AC-001 多选维度：需求中心现有枚举类筛选维度中，Sprint、分级、负责人、阶段以及已存在的 Change/归档可见性类维度按实现适用性支持多选；分级在同一控件内分组承载需求优先级和 BUG 严重性；不适合多选的自由文本或二元开关需在设计中说明保留原因。
- [ ] AC-002 组合语义：同一筛选维度内多选使用 OR 语义，不同筛选维度之间使用 AND 语义；卡片列表、阶段数量和空态与组合条件一致。
- [ ] AC-003 下拉搜索：下拉内搜索至少匹配用户可见名称；含稳定 ID 的候选项同时支持 ID 匹配；清空搜索后恢复完整候选列表。
- [ ] AC-004 选中状态：候选项通过复选框表达选中状态，点击复选框或文本均可切换；hover、focus、disabled、checked 和 unchecked 状态在深浅主题下可区分。
- [ ] AC-005 已选摘要：未选择时显示默认占位；少量选择展示选项名；较多选择展示数量摘要；当 Sprint 选中集合等于默认 Sprint 范围时，外层筛选数量可保持 0，Sprint 触发器必须显示“默认 Sprint 范围”或等价默认态文案；用户手动改变 Sprint 选择后再显示选项名或已选数量；长文本不挤压工具栏其他控件。
- [ ] AC-006 批量选择与清空能力：支持全选当前维度候选项、清空单个维度和全局清空筛选；下拉内搜索生效时，全选范围限于当前搜索结果；Sprint 全选必须包含“未纳入 Sprint”候选项；清空后统计、阶段列、卡片和空态同步恢复。
- [ ] AC-007 排序规则：筛选项顺序为 Sprint、分级、负责人、阶段；Sprint 只展示进行中/已归档两类状态且“当前迭代”为同行标签，并提供“未纳入 Sprint”合成候选项匹配无明确 Sprint 归属的卡片；需求 P 值与说明同行展示，BUG 严重性与需求优先级分组区分；证据不足时降级为名称或 ID 稳定排序。
- [ ] AC-008 状态保持：手动刷新、主题切换、打开或关闭文档抽屉、在下拉内搜索候选项时，已选筛选条件不丢失。
- [ ] AC-009 权限安全：候选项、搜索提示、数量和错误态只基于当前用户有权访问的上下文；无权限对象不得通过筛选控件泄露。
- [ ] AC-010 脱敏错误：解析失败、权限不足或候选项为空时不暴露本机路径、内部堆栈、密钥、Token、原始治理文档全文或隐藏对象身份。

## UI AC

- [ ] AC-UI-001 下拉面板作为工具栏浮层展示，不改变需求中心页面壳、看板列、卡片密度或阶段结构。
- [ ] AC-UI-002 下拉面板包含搜索输入、候选列表、复选框、全选入口、清空入口和无结果空态；候选项较多时使用内部滚动，不推动页面布局大幅跳动。
- [ ] AC-UI-003 支持键盘可达、焦点态、Esc 关闭、点击外部关闭；内部按钮、输入和滚动容器阻止冒泡时，外部点击仍可关闭浮层。
- [ ] AC-UI-004 1440px 桌面视口下，工具栏、多选摘要、筛选浮层内触发器摘要左侧对齐、下拉宽度、列表滚动和空态不发生遮挡或文本溢出。
- [ ] AC-UI-005 窄屏或低宽度场景下，触发器摘要优先转为数量摘要，避免挤压刷新、搜索和其他筛选控件。
- [ ] AC-UI-006 深浅主题下，复选框、边框、背景、文字、focus ring 和强调色符合 MoonBox Ops token，可读且不使用装饰性渐变。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 原型拆解已覆盖页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点，见 prototype/web/context.md。
- [ ] AC-PROTOTYPE-002 后续 `/req-opsx` 必须在 Change design.md 写入 UI Skeleton，明确工具栏、多选下拉、候选项列表、空态、权限态、可测 selector 和 Mock/API 边界。
- [ ] AC-PROTOTYPE-003 后续 `/opsx-apply` 完成 UI 任务前必须记录 1440px 视觉验收，覆盖默认、展开、搜索无结果、多选摘要、深浅主题和文本溢出。
- [ ] AC-PROTOTYPE-004 后续 `/opsx-archive` 前必须确认 requirement.md、acceptance.md、trace.md 与最终 Change 设计、实现证据和验收结论一致。

## 知识库横切 AC

Knowledge-base Cross-cutting Report 判定本需求不命中 admin-list、admin-form、admin-modal、media-upload 标签，因此不追加 AC-XCUT。相关知识库要求以原型驱动 UI AC 和需求中心事实源优先约束承接：

- 来源：`docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`
- 来源：`docs/knowledge-base/retrospectives/sprint-004-retrospective.md`
- 来源：`docs/knowledge-base/retrospectives/sprint-005-retrospective.md`

## 非目标验收

- [ ] AC-NON-001 不要求新增服务端分页、服务端筛选查询语言或个人筛选模板。
- [ ] AC-NON-002 不改变 REQ、BUG、Change、Sprint 的事实源、授权边界、状态映射和统计口径。
- [ ] AC-NON-003 不新增真实执行动作、OpenSpec Change、源代码或数据库迁移。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:41:41
accepted_by: workflow-sync
source_change: add-requirement-center-filter-multiselect-search
source_sprint: sprint-006
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

