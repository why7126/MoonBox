---
title: 独立 Change 自动分级与卡片只读展示设计
created_at: '2026-11-01 00:33:51'
updated_at: '2026-11-01 00:57:00'
---

# 独立 Change 自动分级与卡片只读展示设计

## 背景与现状
来源为 issues/requirements/review/REQ-0059-standalone-change-auto-classification。change_index.py 当前把独立对象 priority 投影为标签，ChangePriorityEditor 经 PUT priority 与异步控制器保存。本设计引用 REQ 全部 FR、AC 和 business-flow.md；保持来源 Issue 与归档只读边界。

## 目标与非目标
创建时评估、正确显示维度、卡片只读；不重排 Sprint、不批量补评历史、不新增 DB 表或重设计全页。

## 设计决策
D1：采用现有 DS 组件和 token 的局部调整。原型为结构输入，不移植其演示双列布局；避免 CSS Port 引入第二套样式。
D2：trace.change_type 使用 fix/non_fix，区别于 API 对象 type=change。旧对象缺字段时只按 fix- 前缀兼容，显式类型与前缀冲突标记待核实；有来源或来源受限先走来源逻辑。
D3：当前值仍位于 trace.severity/priority；classification 包含 state(assessed/pending)、dimension、rationale、evidence_refs、evaluated_at、evaluated_by。枚举/类型/理由共享校验，Agent 负责基于材料判断，脚本不通过关键词生成等级。新建成功前校验；不足保留 proposed 草稿和明确缺口，不报告完整成功。重试保留有效记录。重评原子维护必要历史，保留旧 priority_history。
D4：创建技能 opsx-propose 与 openspec-propose 共用评估约束，初始化保持 schema v1；仅无来源对象启用评估。REQ/BUG 转换不重复评估来源值。实施时核实创建入口覆盖与初始化器职责，避免仅修改提示词却未设完成校验。

## 数据与 API
卡片投影补充分级维度、评估状态和 severity，缺失/非法/冲突显式可识别；fix 历史 priority 不参与当前展示。已有来源字段与权限隐藏逻辑不变。筛选按维度工作，不改变默认排序。
旧 PUT /api/v1/requirement-center/changes/{change_id}/priority 对 fix 返回类型冲突错误且不入队；non_fix 保留维护窗口、权限、版本及审计。执行排队操作前再次判断类型、来源和归档状态。删除前端保存调用和事件，保留旧客户端合法路径。最终响应结构及错误码通过现有 API 标准确定，更新 OpenAPI、Orval客户端、docs/03-api-index.md 及契约测试。无新增DB表或迁移，SQLite/MySQL均复用既有操作记录；对象存储及部署无变更。

## UI Contract
事实源优先级：REQ HTML结构 > 截图/原型说明 > 验收计划 > UI规则 > 旧spec；业务只读与来源保护不可牺牲。现有主题token、字体、卡片宽度、边距及原交付动作保持；只替换标签和删除编辑区，卡片高度允许自然回收。权限不足无编辑入口，正常权限同样只读。原型为Mock，产品使用真实API。

## UI Skeleton
需求中心 → 既有看板列 → rc-delivery-card → 标题、分级/负责人/估算、文档、状态、交付动作。先完成 Skeleton 并取得首轮确认，再做详细样式及数据交互。状态容器覆盖 fix/non_fix/来源、valid/missing/invalid/conflict，读取API明确维度。1440px检查层级、对齐和空白回收；390px无文字溢出。

## UI Reference Replication Contract
局部一致，不复制整个截图布局。参考拆解与selector矩阵见REQ prototype/web/context.md。产品 rc-delivery-card 对应 .card；rc-priority-tag/rc-severity-tag 对应 .level；rc-card-meta 对应 .meta；rc-card-actions 对应 .actions。测试按data-issue-id限定对象，不能只匹配第一个标签。
动作矩阵：设置优先级 → 原内联编辑 → change-priority-edit/editor/save → 所有状态删除 → DOM/焦点/Network；返修、验收、归档 → 既有组件族 → rc-card-actions内实际selector实施前补证 → 保留原权限/禁用/错误状态 → 原功能回归。无新增modal，不逐按钮重建。
样式采样：各阶段1440×900与390×844、深浅主题；标签 font-size/line-height/padding/border/color/background，元信息 gap，卡片 width/overflow。期望为同视口既有token与非修改区基线，当前值实施时浏览器采样，未采样不标通过。批次为Skeleton确认、标签状态与删除入口、双视口主题及真实API验收；证据存 evidence/acceptance/。

## 原型冲突处理
Conflict Resolution：原spec“编辑反馈与筛选”要求编辑，REQ明确删除，delta以只读替换；HTML中的静态底部文字不是新的禁用动作，真实产品保留原功能；Mock双列用于状态比较，不替代看板断点。无其他已知业务冲突。

## 观测声明
product_data_collection_observability: applicable；affected_layers: web、api、governance。reason: 分级投影与治理写入审计。validation: AC-010/011验证权限、可信请求关联、直接调用不伪造行为、必要审计原子性与脱敏；无新保留周期，既有异步操作继续Task Trace，静态标签无新任务。引用 docs/standards/product-data-collection-observability.md。

## 验证与知识库
AC-001/002创建链路及共享校验；003冲突不足；004/005/006 DOM、筛选、视觉；007/008来源历史；009幂等失败；010/011接口与审计。原型四项按REQ计划执行。引用 prototype-driven-ui-gate.md 与 sprint-017-retrospective.md：区分真实观察/合成回归，保留历史，追加前重算容量。

## 风险与回滚
容量30.5/30人天，无缓冲；若超支优先提出延后本P2，不降验收标准。旧客户端与排队写入可能绕过维度，读写端共享校验并执行前复核。回滚采用兼容读路径和功能回退，不删除新增评估事实、不把严重性转为优先级；回滚后确认旧界面不会错误展示fix旧值，必要时保留只读投影修正。
