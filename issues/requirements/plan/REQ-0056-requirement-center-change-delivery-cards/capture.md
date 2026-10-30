---
req_id: REQ-0056-requirement-center-change-delivery-cards
title: 需求中心交付阶段按 Change 独立成卡采集记录
status: captured
priority: P1
created_at: '2026-10-29 18:19:44'
updated_at: '2026-10-29 18:19:44'
parent_requirement: REQ-0026-requirement-center-standalone-change-cards
recorded_by: product
source: 用户反馈及同会话 explore
product_data_collection_observability:
  status: applicable
  standard_ref: docs/standards/product-data-collection-observability.md
  affected_layers:
  - web
  - api
  - web_request_wrapper
  - usage_events
  - request_logs
  - task_traces
  reason: 交付卡片身份、任务读写和阶段动作需携带来源 Issue 与明确目标 Change，保持授权及链路关联。
  validation: 后续验证卡片与请求目标一致、跨 Change 不串读写、行为与请求/任务关联、脱敏和采集失败不阻断。当前仅采集文档，未验证产品；DB、部署和对象存储暂无变更目标，客户端生成由后续
    API 契约差异决定。
---

# 需求中心交付阶段按 Change 独立成卡采集记录

## 一句话
前期保留 REQ/BUG 卡，交付阶段每个 Change 独立成卡，分别展示状态、Sprint、任务与验收，保留来源追溯、避免重复统计，所有操作绑定明确的目标 Change。

## 原始描述
需求中心交付阶段按 Change 独立成卡：前期保留 REQ/BUG 卡，交付阶段每个 Change 独立展示状态、Sprint、任务与验收，保留来源追溯，避免重复统计，并将所有操作绑定明确的目标 Change。

## 背景与用户价值
- 面向产品经理与研发团队，解决同一需求分阶段、跨迭代或并行交付时，单张 Issue 卡无法分别表达阶段及任务来源的问题。
- 来源样本 REQ-0048-chat-isolated-acceptance-orchestration：sprint-015 已归档子交付与 sprint-016 在研后续交付同时关联，查看进度出现“无法确定 tasks.md 来源”。
- 本次为看板交付模型的演进，包含同一验收闭环中的展示、筛选、统计和操作定位，保持一条需求。
- 初判 P1：影响交付进度查看及操作目标识别；未据此认定生产紧急事故。

## 已确认的范围与探索结论
- 收集、完善、评审阶段保留 REQ/BUG 卡；进入交付阶段后按 Change 唯一身份成卡，覆盖待开发、研发中、验收中、已完成。
- 卡片以该次交付中文名称为标题，标明 Change 身份及来源 REQ/BUG；同一 Change 关联多个 Issue 时仍只生成一张交付卡。
- 状态、Sprint、任务进度、文档和验收均取自对应 Change；需求整体完成和验收在需求详情承接，子交付完成不等于整个需求完成。
- Sprint 筛选按 Change 归属；历史与当前交付可位于不同列和迭代，不复制需求当前 Sprint 覆盖历史归属。
- 交付列数量按 Change 计，需求数量按 Issue 去重；工作量不得把需求总人天重复复制并累加。
- 查看进度、任务勾选及开发、返修、验收、归档等动作同时保留来源 Issue 与目标 Change 身份，防止误读、误写或误执行。
- 复用项目与对象权限；缺失、冲突、不可见的目标不得静默回退到其他 Change。
- 保留无来源 Issue 的独立 Change 能力及已归档证据，不拆分或复制实际 REQ/BUG 文档，不修改旧交付事实。

## 重复检查与用户决策
已检查 requirements CHANGELOG 与注册表。REQ-0026 已交付独立 Change 可见性，旧范围要求关联 Change 留在 Issue 卡内。本次调整其交付展示规则，用户明确选择“新建后续子需求，关联 REQ-0026”，独立验收本次范围，保留原归档历史。REQ-0048 仅为问题来源样本，不作为本需求父级。

## 建议验收方向
- REQ-0048 的历史子交付在 sprint-015 已完成列，当前交付在 sprint-016 研发列，当前迭代筛选不混入旧卡。
- 一个 Issue 多 Change、多活动 Change、全部归档、一个 Change 多 Issue、无来源 Change 均按身份正确展示且不重复计数。
- 每张卡文档、任务读写与阶段操作均命中自身 Change，保留完整来源 Issue 身份；切换、刷新和会话续接不丢失目标。
- Change 验收与需求整体验收分离；任务总数、估算及统计不因关联数量重复累加。
- 无权限、缺失或冲突关系明确提示，禁止跨项目或跨 Change 读取与执行。

## 待澄清
- [ ] 前期 Issue 卡到交付卡的具体切换门槛，以及有剩余未建 Change 范围的需求入口。
- [ ] 多来源 Change 的来源展示顺序、操作会话归属与明确目标的传递契约。
- [ ] 缺少 Change 独立估算时的工作量显示和统计口径，不平均分摊或虚构估算。
- [ ] 筛选、搜索、统计兼容策略与桌面/窄屏卡片布局；后续建立原型及视觉验收契约。

## 非目标
不在 capture 阶段实现界面、调整 API、修复历史状态、生成 PRD、创建 Change 或纳入 Sprint。
