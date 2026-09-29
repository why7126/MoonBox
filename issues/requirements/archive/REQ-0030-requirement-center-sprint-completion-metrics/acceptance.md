---
requirement_id: REQ-0030-requirement-center-sprint-completion-metrics
title: 需求中心指标卡新增 Sprint 已完成与累计数量
acceptance_status: passed
owner: product
created_at: 2026-09-14 14:50:18
updated_at: 2026-09-29 14:41:41
---

# 验收标准

## 功能 AC

- [x] AC-001 需求中心指标区展示 Sprint 指标，至少包含已完成 Sprint 数和总体 Sprint 数。
- [x] AC-002 指标文案采用“已完成 / 总体”或等价表达，并能让用户理解这是项目级 Sprint 总览。
- [x] AC-003 已完成 Sprint 默认统计 `iterations/archive/` 下的有效 Sprint。
- [x] AC-004 累计 Sprint 统计 `iterations/change/` 与 `iterations/archive/` 下的有效 Sprint。
- [x] AC-005 若存在 `status: completed` 但未迁入 archive 的历史兼容 Sprint，聚合逻辑必须明确处理策略并避免重复计数。
- [x] AC-006 搜索关键字、对象类型、负责人、优先级和 Sprint 筛选不得改变 Sprint 数量指标。
- [x] AC-007 用户手动刷新、切换空间或重新加载需求中心后，Sprint 数量指标随聚合接口结果刷新。
- [x] AC-008 无 Sprint 时展示稳定的 `0 / 0` 或等价空态，不隐藏指标卡。
- [x] AC-009 Sprint 数据解析失败、接口失败或权限不足时展示轻量错误态，并提供重试或恢复路径。
- [x] AC-010 错误态不得展示本机绝对路径、系统用户名、内部堆栈、密钥、token、`.env` 内容或未脱敏治理文档全文。
- [x] AC-011 加载中、刷新中和错误态不得造成指标区高度跳动、卡片挤压、文本溢出或看板列头错位。
- [x] AC-012 后续实现若新增或扩展需求中心接口字段，必须同步 API 文档、OpenAPI 来源和客户端类型约束。
- [x] AC-013 后续实现必须覆盖 Sprint 聚合口径测试、筛选不影响指标的前端测试、加载/空态/错误态测试和脱敏安全测试。
- [x] AC-014 request_logs 仅记录请求摘要、状态、耗时和脱敏统计上下文；usage_events 仅记录页面加载、刷新或空间切换等稳定事件，不记录原始文档内容。
- [x] AC-015 所有指标卡片高度应比初版更紧凑，且不得造成标题、数字、筛选区或看板列头重叠。
- [x] AC-016 所有指标名后必须展示统一信息图标，鼠标悬停或键盘聚焦时通过项目内统一浮层 tooltip 展示说明。
- [x] AC-017 需求、Bug 与独立 Change 指标展示为“已完成 / 总体”，并按方案 A 继续跟随当前筛选条件变化。
- [x] AC-018 Sprint 卡片标题文案为 `Sprint`，删除卡片底部“已完成 / 累计 · 项目级总览”辅助文案；项目级口径说明改由 tooltip 承载。

## 原型驱动 UI AC

- [x] AC-PROTOTYPE-001 原型拆解完整记录页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [x] AC-PROTOTYPE-002 `/req-opsx` 生成的 Change `design.md` 必须写入 UI Contract，覆盖指标区位置、项目级口径说明、深浅主题、加载态、空态、错误态和 Mock/API 边界。
- [x] AC-PROTOTYPE-003 `/req-opsx` 生成的 Change `design.md` 必须写入 UI Skeleton，覆盖需求中心页面壳、指标区、筛选区、看板区域、状态容器和可测 selector。
- [x] AC-PROTOTYPE-004 `/opsx-apply` 必须先完成 1440px UI Skeleton 首轮视觉确认，再进入细节实现。
- [x] AC-PROTOTYPE-005 1440px 视觉验收必须覆盖深色主题与浅色主题的指标卡布局、数字层级、辅助文案、筛选区并存、看板列头对齐和文本溢出。
- [x] AC-PROTOTYPE-006 响应式验收必须覆盖移动或窄视口下指标区换行、数字不溢出、筛选区不遮挡和看板横向滚动边界。
- [x] AC-PROTOTYPE-007 实现阶段必须声明 Mock/API 边界，明确 Sprint 数量来自真实聚合接口、测试 fixture 还是 demo 模式；默认生产路径不得用 Mock 数字冒充真实数据。
- [x] AC-PROTOTYPE-008 归档前必须完成 REQ 最终一致性检查，确认 requirement、acceptance、trace、prototype 与最终 Change 设计、实现证据和视觉验收结果一致。

## 横切 AC（knowledge-base）

本 REQ 为前台需求中心指标增强，未命中 `req-complete` 当前定义的 `admin-list`、`admin-form`、`admin-modal`、`media-upload` 横切标签。

- [x] AC-XCUT-001 N/A — 非管理端 CRUD 列表页，不适用 `admin-list-page-consistency.md`。
- [x] AC-XCUT-002 N/A — 非管理端全页表单/设置页，不适用 `admin-form-page-consistency.md`。
- [x] AC-XCUT-003 N/A — 非管理端宽弹窗 CSS 级联场景，不适用 `admin-modal-width-css-cascade.md`。
- [x] AC-XCUT-004 N/A — 本需求不包含图片、视频、头像或 Logo 上传链路，不适用 `admin-media-upload-chain.md`。

## Knowledge-base Cross-cutting Report

| 标签 | 引用文档 | 将写入 acceptance 的 AC 条数 |
|---|---|---:|
| N/A | 无匹配后台横切 best-practice | 0 |

补充读取最近复盘：`docs/knowledge-base/retrospectives/sprint-005-retrospective.md`。本 REQ 承接“需求中心卡片需要事实源优先”和“原型与视觉证据覆盖状态组合”的经验。

## Readiness

```yaml
readiness: ready
knowledge_base_gate: N/A
prototype_gate: pass
review_ready: true
next: 无
```

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:41:41
accepted_by: workflow-sync
source_change: add-requirement-center-sprint-completion-metrics
source_sprint: sprint-006
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

