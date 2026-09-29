---
requirement_id: REQ-0031-requirement-center-current-iteration-capacity
title: 需求中心显示当前迭代容量已使用与总容量
acceptance_status: passed
owner: product
source: requirement.md
priority: P1
created_at: 2026-09-14 14:50:31
updated_at: 2026-09-29 14:41:41
---

# 验收标准

## 功能 AC

- [ ] AC-001 需求中心必须展示当前迭代容量，至少包含 Sprint ID、已使用容量、总容量和容量状态。
- [ ] AC-002 单个当前迭代时，页面展示该 Sprint 的 `已使用容量 / 总容量`，且单位与 Sprint 容量治理规则一致。
- [ ] AC-003 同时存在 2 个当前迭代时，两个 Sprint 的容量项均可见，不被静默合并、覆盖或隐藏。
- [ ] AC-004 如果展示两个当前迭代的汇总容量，必须同时保留每个 Sprint 的分项明细，并明确汇总统计范围。
- [ ] AC-005 已使用容量必须来自 Sprint Scope 中 REQ、BUG、Change 的容量合计，不得用卡片数量或阶段数量替代。
- [ ] AC-006 总容量优先读取 Sprint 显式容量；没有显式容量时使用项目默认容量规则，并展示默认来源提示。
- [ ] AC-007 容量状态至少覆盖正常、接近上限、已超量和待核实；超量状态只提示风险，不自动阻止浏览、筛选或打开文档。
- [ ] AC-008 容量事实源缺失、冲突或无法计算时，展示待核实状态并保留 Sprint ID，不得显示伪造的 0/0。
- [ ] AC-009 手动刷新、切换项目或外部 Sprint Scope 变化后，容量展示与最新稳定快照一致。
- [ ] AC-010 刷新失败时保留上一次成功容量信息，并展示轻量失败提示；不得清空整个看板。
- [ ] AC-011 无权访问的项目或 Sprint 不得通过容量数值、异常提示、搜索或响应字段泄露。
- [ ] AC-012 后端聚合接口如新增或扩展字段，必须同步 API 文档、OpenAPI 来源、客户端类型和请求日志字段约束。

## UI 状态 AC

- [ ] AC-UI-001 容量信息应靠近当前迭代相关统计或筛选区域，避免散落在每张卡片内造成重复噪音。
- [ ] AC-UI-002 容量项在深色和浅色主题下均清晰可读，符合 MoonBox Ops 视觉系统的近直角、细边框、高密度信息风格。
- [ ] AC-UI-003 两个当前迭代并存时，两个容量项视觉权重一致，不默认把其中一个降为隐藏项。
- [ ] AC-UI-004 接近上限、已超量和待核实状态应有可辨识视觉反馈，但不得使用阻断式弹窗或遮罩。
- [ ] AC-UI-005 窄屏下容量项允许换行、折叠或进入可展开区域，但不能完全隐藏当前迭代容量。
- [ ] AC-UI-006 容量数值、Sprint ID 或状态文案过长时不得遮挡统计区、筛选器、看板列头、卡片 ID 或阶段动作。

## 数据采集与链路观测 AC

- [ ] AC-OBS-001 容量展示相关刷新、当前迭代筛选或项目切换行为应复用 Web 行为事件采集；采集失败不得阻断页面主流程。
- [ ] AC-OBS-002 容量聚合请求应写入请求日志摘要，记录路由、状态、耗时、结果数量或脱敏错误码。
- [ ] AC-OBS-003 行为事件、请求日志和错误摘要不得记录 Authorization、Cookie、`.env` 内容、本机绝对路径、完整 Markdown 正文或真实客户敏感数据。
- [ ] AC-OBS-004 若后续实现引入后台批量计算、异步刷新或跨项目容量任务，OpenSpec 阶段必须重新评估是否接入 Task Trace 和流程节点。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 原型拆解必须覆盖页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [ ] AC-PROTOTYPE-002 `/req-opsx` 生成 Change 时，design.md 必须写入 UI Skeleton，覆盖容量指标区域、当前迭代分项、异常态、刷新失败态、深浅主题和可测选择器。
- [ ] AC-PROTOTYPE-003 `/opsx-apply` 实现阶段必须在 1440px 桌面视口验收单当前迭代、双当前迭代、超量、待核实和刷新失败状态。
- [ ] AC-PROTOTYPE-004 `/opsx-apply` 或 `/opsx-modify` 涉及 UI 返修后，旧截图和旧视觉结论立即视为 stale，必须重新取证。
- [ ] AC-PROTOTYPE-005 `/opsx-archive` 前必须完成 REQ 最终一致性检查，确认 requirement.md、acceptance.md、trace.md 与最终 Change 设计、实现证据、Mock/API 边界和容量口径一致。

## 横切 AC（knowledge-base）

本 REQ 不命中 `admin-list`、`admin-form`、`admin-modal`、`media-upload` 四类管理端横切标签，因此无管理端横切 AC。

> 来源：`docs/knowledge-base/best-practices/prototype-driven-ui-gate.md` 与 `docs/knowledge-base/retrospectives/sprint-005-retrospective.md`。本需求承接需求中心事实源优先、容量风险前置、UI 状态组合取证经验。

- [ ] AC-XCUT-001 Change `design.md` 必须声明容量事实源优先级，不能由前端临时状态、卡片数量或历史快照推断容量。
- [ ] AC-XCUT-002 Change `tasks.md` 中 UI Skeleton 任务必须早于容量聚合细节实现任务。
- [ ] AC-XCUT-003 1440px 视觉验收必须覆盖状态组合，而不只覆盖静态布局，至少包括正常、双当前迭代、超量和待核实。
- [ ] AC-XCUT-004 归档前必须确认 Sprint 容量 soft-pass 或超量状态有明确用户可见提示和文档化取舍说明。
- [ ] AC-XCUT-005 文档、接口和 UI 展示必须以 Issue trace、Sprint scope、Change 事实源和后端能力字段为准，不得依赖临时卡片或 Mock 结论。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:41:41
accepted_by: workflow-sync
source_change: add-requirement-center-current-iteration-capacity
source_sprint: sprint-006
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 验收返修记录

| 时间 | 反馈 | 处理 | 证据 |
|---|---|---|---|
| 2026-09-14 18:24:52 | 当前迭代容量 UI 样式参考附件 HTML `.capacity` 模块；不需要可见文案“当前迭代容量”；保持现有 UI 设计系统一致，其他不调整。 | 已在原 Change 边界内返修容量条：移除可见标题，保留 `aria-label`；改为紧凑横向条、容量进度轨和状态点；未改 API、DB、权限、部署、筛选或看板模块。 | `openspec/archive/2026-09-17-add-requirement-center-current-iteration-capacity/evidence/capacity-modify-1440.png`、`openspec/archive/2026-09-17-add-requirement-center-current-iteration-capacity/evidence/capacity-modify-computed-style.json`；前端聚焦测试 1 passed，TypeScript pass。 |
