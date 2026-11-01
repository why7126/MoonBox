---
title: 独立 Change 创建时自动分级与卡片只读展示
status: done
priority: P2
requirement_id: REQ-0059-standalone-change-auto-classification
created_at: '2026-11-01 00:21:42'
updated_at: '2026-11-01 01:06:57'
owner: 产品团队
source: capture.md 与用户确认的探索结论
lifecycle_stage: archive
parent_requirement: REQ-0057-standalone-change-priority
related_requirements:
- REQ-0057-standalone-change-priority
iteration: null
openspec_changes: []
product_data_collection_observability:
  status: applicable
  affected_layers:
  - web
  - api
  - governance
  reason: 涉及 Web 分级展示、API 元数据投影和治理自动评估及变更审计。无新增 DB 表、对象存储或部署需求；实施设计仍需复核兼容性。
  validation: 后续验证自动评估依据可追溯、分级投影一致、旧编辑入口及相关事件处理、来源 Issue 分级不被覆盖。
  standard_ref: docs/standards/product-data-collection-observability.md
terminal: web-catalog
version: v1
---

# 独立 Change 创建时自动分级与卡片只读展示

## 背景与证据
REQ-0057 已交付独立 Change 优先级定义和卡片编辑能力。用户提供的截图显示 fix-archive-historical-closure 卡片展示“优先级未设置”及“设置优先级”，希望由创建 Change 的 Agent 提前完成分级，减少手工维护并区分修复严重性与交付优先级。

同会话只读检查确认 RequirementCenterPage.tsx 对无来源 Issue 的 Change 统一展示 priority，且挂载 ChangePriorityEditor；rules/document-governance.md 的独立 Change 分级规则允许此行为。本需求是对已交付规则的演进，不宣称现有实现违反原需求。本轮复用用户截图及此前源码证据，未执行新的运行态验收。

## 目标用户与目标
产品经理、研发负责人及创建独立 Change 的 Agent。创建后即可看到有依据的分级；fix 与非 fix 使用正确语义；卡片不承担分级维护职责。

## 范围
包含独立 Change 创建时类型识别、自动评估、分级事实源及评估依据、卡片只读展示、相关筛选兼容、历史数据读取及治理调整记录。

不包含重新定义 BUG 等级、修改来源 Issue 分级、多来源冲突算法、自动排期、自动评审或归档、批量改写历史归档。历史补评执行不随本需求上线自动触发。

## 功能要求

### FR-001 来源与类型识别
先判断是否具有 REQ/BUG 来源，有来源继续引用原 Issue 分级；来源不可见或解析失败不能当作无来源。独立 Change 中，fix 使用 severity，其他类型使用 priority。

设计默认采用明确类型元数据作为权威依据；缺少类型的旧数据可按完整 fix- 前缀兼容识别，不按标题中包含“修复”等自由文本判定。类型与名称冲突时标记待核实，不静默转换。具体复用字段由后续设计核实，不在本 PRD 臆造已有字段。

### FR-002 创建时自动评估
独立 Change 创建流程在产物生成阶段完成分级评估并持久化，成功返回前验证分级字段、合法枚举与评估依据。fix 使用 blocker、critical、high、medium、low；非 fix 使用 P0、P1、P2、P3。

严重性以功能阻断、影响范围、数据或安全影响、替代方案为依据；优先级以业务价值、紧迫性、依赖和延期成本为依据，沿用项目现有等级定义。保留结论、理由及参考材料，不统一填默认等级，不以名称前缀决定等级。

信息不足时先自主读取可用材料，仍不足则标记评估待补充并明确缺口；不得伪造已评估成功，也不得在卡片增加设置入口。该状态不自动变为历史对象的开发或归档阻断。

### FR-003 事实源与重评
独立 Change 的 trace Frontmatter 承载当前分级；仅一个分级维度参与当前展示。保留评估依据及必要时间、执行主体、旧值与新值记录。原 priority 与 priority_history 等历史记录不得因 fix 改用 severity 被抹除，也不得将 P 值机械映射为严重性。

创建流程重试不重复覆盖有效分级或刷新业务时间。后续调整通过具备权限及版本校验的治理流程进行，并记录理由；归档对象只读。已有关联来源时停止独立分级写入，保留原值追溯但展示来源分级。

### FR-004 卡片只读展示
独立 fix 卡显示“严重性”及对应等级；其他独立 Change 显示“优先级”及 P 值。各阶段卡片统一移除设置优先级按钮、内联编辑区及键盘可达的编辑入口，不以弹窗、菜单或抽屉转移同类卡片操作。

有效值缺失显示对应“待评估”，非法值或类型冲突显示“待核实”。fix 的历史 priority 不作为当前严重性展示。负责人、工作量、验收及归档状态保持独立语义。刷新、搜索、阶段切换后投影一致；分级筛选不混淆严重性与优先级，不新增自动排序。

### FR-005 历史兼容与接口边界
已有非 fix 合法 priority 保留；旧 fix 缺 severity 时显示严重性待评估，不自动转换或补写。活动对象可通过后续治理补评，归档对象保留只读历史。缺分级不新增历史对象执行门禁。

移除卡片客户端保存调用及无效交互事件。后续设计审计原受控编辑 API 的调用者，明确保留给治理、弃用或关闭策略；不得仅隐藏按钮就声称服务端写入口已关闭，也不得破坏其他合法调用。现有权限、并发校验与必要审计不因入口变化而放宽。

## UI 约束与证据计划
用户截图是现状问题证据，非整体视觉复刻稿；本需求仅调整分级标签及移除编辑入口，不重设计卡片。保留既有布局、负责人、工作量和交付操作。后续验收覆盖 1440px 与窄屏、fix/非 fix/来源 Issue、有效/缺失/非法分级以及各交付阶段，检查鼠标与键盘均无卡片分级编辑入口。已补充局部状态原型，视觉验收待实施阶段完成。

## 验收要点
- 新建独立 fix / 非 fix 分别生成合法 severity / priority 和可追溯依据。
- 信息不足、类型冲突、非法值有明确状态，不静默填默认值。
- 重试不覆盖有效评估，不制造重复历史或更新时间。
- 卡片仅展示正确维度，无设置按钮及替代编辑入口；刷新与筛选一致。
- 来源 REQ/BUG 值保持引用，来源不可见不误判独立。
- 旧非 fix priority 保留；旧 fix 不作机械映射；归档历史不批量改写。
- 权限、并发及必要审计不退化，旧 API 兼容策略明确并验证。

## 影响面与验证边界
同步创建技能及治理分级规则、元数据读取与 API 契约、Web 标签和筛选、旧编辑调用及相关测试。若 API schema 改变则同步 OpenAPI 和生成客户端。本需求不要求数据库迁移或部署变化；安全影响限于既有写入授权和审计边界，实施设计仍须验证。

产品数据采集适用 web、api、governance；移除编辑行为后不再产生虚假保存事件，治理评估及修改保留必要审计；若通过任务链路执行，按现有 Task Trace 规范记录，不将直接治理操作伪装成用户点击。验证关注字段来源、评估追溯、无敏感内容及采集失败与必要审计的不同处理。对象存储不涉及新增读写。

## 关联需求与优先级
父需求 REQ-0057-standalone-change-priority 已归档，保持其历史事实；本需求单独评审和验收。P2：改善治理准确性及操作体验，目前无核心业务阻断证据。

## 当前状态
开发与15项验收已通过，Skeleton 已获用户确认，视觉证据及真实CLI观察已记录。Change 已合并规格并迁入归档目录，REQ 状态由 Workflow Sync 同步为 done；归档收尾正在复核当前说明与证据导航。

## 后续设计核实
已在 business-flow.md 明确建议新增 change_type、classification 结构及原 priority API 兼容与类型约束；现有卡片对象 type 不能用于 fix 判定。实施前继续复核全部外部调用者。历史批量补评需另行明确范围与授权，不影响本次新建流程与只读展示交付。

## 评审补充边界
新建评估 pending 可保留 proposed 草稿，但不得报告创建流程完整成功；历史缺等级不新增开发或归档门禁。实施与视觉条件见 review.md。

## 实施一致性核对

2026-11-01 核对本文件与实现一致：创建Agent评估，完成门禁校验；卡片只读按维度展示；来源和历史保留。证据见 Change `update-standalone-change-auto-classification/evidence/acceptance/implementation-review.md`。无数据库迁移、部署拓扑调整或新增权限。
