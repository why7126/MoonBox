---
requirement_id: REQ-0034-requirement-center-default-current-iteration-cards
title: 需求中心默认只显示当前迭代卡片
acceptance_status: passed
owner: product
source: requirement.md
created_at: 2026-09-14 14:56:26
updated_at: 2026-09-29 14:41:41
---

# 验收标准

## 功能 AC

- [ ] AC-001 默认进入需求中心时，卡片集合包含当前迭代和未纳入 Sprint 的 REQ、BUG 和独立 Change。
- [ ] AC-002 当前迭代识别使用 Sprint 生命周期事实源；不得只依赖前端缓存、标题文本、目录名或卡片文案推断。
- [ ] AC-003 仅存在一个当前迭代时，既有 Sprint 多选下拉默认选中该 Sprint 和“未纳入 Sprint”，并展示这两个范围的卡片。
- [ ] AC-004 存在多个当前迭代候选时，既有 Sprint 多选下拉默认选中全部当前 Sprint 和“未纳入 Sprint”，并提供进一步取消或选择单个 Sprint 的显式操作。
- [ ] AC-005 不存在当前迭代或当前迭代无卡片时，默认展示未纳入 Sprint 对象；用户可通过清空 Sprint 多选或选择历史 Sprint 查看其他非当前对象。
- [ ] AC-006 用户可通过清空 Sprint 多选查看全部对象，取消“未纳入 Sprint”收窄到当前 Sprint，或选择历史/归档 Sprint 查看对应范围；切换后既有搜索、类型、负责人、优先级和文档阅读能力保持可用。
- [ ] AC-007 用户点击重置筛选或返回默认视图时，恢复当前 Sprint + 未纳入 Sprint 的多选默认选中状态，而不是全量范围。
- [ ] AC-008 手动刷新保留用户显式 Sprint 选择；空间或项目切换后按新上下文重新计算默认当前 Sprint + 未纳入 Sprint 选择。
- [ ] AC-009 Sprint 事实源解析失败、接口失败或权限不足时，不静默回退全量卡片并伪装为当前迭代结果；错误提示必须脱敏。
- [ ] AC-010 默认范围变更不改变 REQ、BUG、独立 Change 的阶段映射、去重、文档入口、权限判断和归档可见性规则。

## UI AC

- [ ] AC-UI-001 当前迭代状态必须延续需求中心既有 Sprint 多选、筛选器、工具栏和卡片区视觉；不得新增割裂的说明卡片或筛选模块下方提示模块。
- [ ] AC-UI-002 多当前迭代、无当前迭代、接口失败和空态下，筛选栏、指标区、看板列头和卡片文本不重叠、不溢出。
- [ ] AC-UI-003 深浅主题、1440px 桌面视口和窄屏视口下，Sprint 多选中的当前 Sprint、未纳入 Sprint 选中状态、清空入口和候选状态清晰可读。
- [ ] AC-UI-004 长 Sprint ID、长卡片标题和多选 Sprint 状态下，工具栏高度与看板 sticky 表头不发生异常跳动。

## 数据与观测 AC

- [ ] AC-DATA-001 页面加载、Sprint 选择变化、筛选重置、手动刷新和空间/项目切换的行为事件只记录脱敏筛选上下文。
- [ ] AC-DATA-002 若后端聚合接口参与当前迭代识别，请求日志只记录安全摘要、结果数量、错误码和耗时，不保存治理文档全文、本机路径、完整请求/响应体、密钥或 token。
- [ ] AC-DATA-003 若实现阶段确认接口契约无变化，Change 文档必须记录无 API/OpenAPI/客户端生成变更的 N/A 原因。

## 知识库适用性

本需求不命中 `admin-list`、`admin-form`、`admin-modal` 或 `media-upload` 横切标签，因此不追加 AC-XCUT。已引用 `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md` 与 Sprint-005 复盘中的需求中心事实源优先经验，相关要求转化为原型驱动 UI AC 与事实源验收项。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 原型拆解覆盖页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [ ] AC-PROTOTYPE-002 `/req-opsx` 阶段必须在 Change `design.md` 写入 UI Skeleton，覆盖页面壳、工具栏、Sprint 多选、看板列、卡片容器、空态、错误态和稳定选择器。
- [ ] AC-PROTOTYPE-003 实现阶段必须在 1440px 桌面视口验证默认当前 Sprint 选中、多当前 Sprint、无当前 Sprint 和清空/选择 Sprint 的首屏结构、间距、对齐、主题、字号、滚动和文本溢出。
- [ ] AC-PROTOTYPE-004 实现阶段必须覆盖窄屏视口下的 Sprint 多选、清空入口和横向看板滚动，不得遮挡阶段列头或卡片主操作。
- [ ] AC-PROTOTYPE-005 归档前必须确认 REQ `requirement.md`、`acceptance.md`、`trace.md` 与最终 Change 设计、实现证据、1440px 截图、computed style 和 Mock/API 边界一致。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:41:41
accepted_by: workflow-sync
source_change: add-requirement-center-default-current-iteration-cards
source_sprint: sprint-006
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

