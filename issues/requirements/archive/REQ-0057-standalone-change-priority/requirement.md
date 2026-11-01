---
title: 独立 Change 优先级定义与卡片展示
status: done
priority: P2
created_at: '2026-10-30 09:41:28'
updated_at: 2026-10-31 22:15:27
owner: 产品团队
source: capture.md 与同会话探索证据
lifecycle_stage: archive
iteration: null
requirement_id: REQ-0057-standalone-change-priority
parent_requirement: REQ-0056-requirement-center-change-delivery-cards
related_requirements:
- REQ-0056-requirement-center-change-delivery-cards
product_data_collection_observability:
  status: applicable
  standard_ref: docs/standards/product-data-collection-observability.md
  affected_layers:
  - web
  - api
  - governance
  reason: 涉及卡片元数据来源与 API 投影；本次仅记录，不修改采集或请求契约。DB、部署、对象存储和安全权限无本次变更。
  validation: 复用探索中的页面与源码证据；后续检查字段来源、权限与日志脱敏，客户端生成依实际 API 差异确定。
terminal: web-catalog
version: v1
---

# 独立 Change 优先级定义与卡片展示

## 背景与证据
需求中心已展示无 REQ/BUG 来源的独立 Change，但后端 change_index.py 的 cards 将 priority 固定为空。当前分级规则只定义 REQ priority 与 BUG severity。用户无法从独立 Change 卡片判断交付先后；截图“未分配”实际是负责人，并非分级。

复用 2026-10-30 同会话 /explore 的用户截图、Firefox 本地 /requirements 刷新至 09:33:58 的观察及代码证据；本轮聚焦复核相关代码未改变，不宣称重新进行了产品验证。

## 目标用户与目标
产品经理、研发负责人需要为独立治理或交付 Change 明确排序依据，并在看板中识别。目标是形成可维护、可追溯的优先级，清楚区分负责人、交付优先级和缺陷严重度。

## 范围
包含无来源 Issue 的独立 Change 优先级定义、授权维护、卡片展示、优先级筛选及旧数据兼容。活动对象可维护；归档对象保留历史只读展示。作为 REQ-0056 的子需求独立验收，与父需求共享卡片身份及权限规则。

不包含 BUG 严重度重定义、关联 Issue 优先级覆盖、多来源分级冲突解决、自动安排 Sprint、自动开发或归档，也不修复 BUG-0070 的时间字段和 BUG-0071 的验收检查断点。不自动重排 Sprint 或批量改写历史归档。

## 功能要求

### FR-001 分级定义与事实源
采用 P0、P1、P2、P3 四档，分别表示紧急、较高、常规和较低交付优先级。独立 Change 的 trace.md Frontmatter priority 作为唯一事实源；不得新造 REQ/BUG 注册条目承载 Change 分级。实施前经评审扩展现有只覆盖 Issue 的治理契约，而非直接修改已生效规则。

缺失值表示“优先级未设置”，非法值表示“优先级待核实”；不自动映射 severity、不猜测默认等级。文档导入、命令写入与界面读取遵循同一字段语义。明确关联但来源不可见的 Change 不能被误判为独立对象。

### FR-002 授权维护与一致性
在独立 Change 卡片提供“设置优先级”入口及内联编辑区，绑定项目、完整 Change ID 和当前版本。复用已有对象写入权限；服务端再次检查权限及活动状态。保存成功后更新卡片；失败保留原值并说明原因。并发冲突提示重新加载，禁止覆盖他人变更。编辑区显式保存/取消，Esc 取消并返回焦点；外部点击不关闭。采用显式保存是因为存在异步校验、并发冲突与审计副作用，不假设文档抽屉具备写权限。

记录旧值、新值、操作者及变更时间；无实际分级变化的重复保存不刷新业务更新时间。归档记录不可通过此入口修改。

### FR-003 卡片展示与筛选
优先级标签明确标注为优先级，与负责人分别呈现；负责人缺失显示“负责人未分配”。卡片刷新、搜索及阶段切换后保持相同分级。扩展现有分级筛选以识别独立 Change 优先级，未设置和待核实可识别；不新增默认自动排序，不改变既有排序口径。

### FR-004 兼容与来源边界
旧 Change 缺字段仍可查看和执行原先获准的操作，不把优先级设为新的归档门禁。优先级与验收状态相互独立。REQ/BUG 来源卡继续使用原 Issue 分级；严重度不转换成 P 值。独立 Change 后续建立 Issue 关联时不得静默覆盖任何来源字段，来源转换后停止本入口编辑，按父需求展示 Issue 分级；保留原 Change 值供追溯，不覆盖来源字段。

### FR-005 API 与观测
读取、保存、刷新后的字段语义一致，错误清楚区分权限、版本冲突、非法值与归档只读。复用请求封装和既有采集链路，关联行为及请求标识，禁止记录凭证或文档全文。任何采集失败不阻断主要操作。具体接口及客户端生成在 Change 设计阶段确定。

## UI 约束
沿用需求中心 token、卡片和标签组件，不进行整页视觉重设计。覆盖桌面 1440px 与窄屏、长 Change ID、不同主题、缺负责人及非法优先级。交互清楚区分查看、编辑、保存中、失败及只读；不能仅用颜色表达分级。

用户截图是现象证据，不是要求一对一复刻的参考稿。原型、动作矩阵与视觉验收计划见 prototype/web/context.md 和 acceptance.md；最终双视口视觉证据及产品/隔离样本边界见关联Change verification.md。

## 验收方向与非功能要求
- 四档值保存并刷新后可复核，合法数据在卡片及筛选中一致。
- 缺失、非法、无权限、并发冲突及归档对象均有明确反馈，不伪造默认值。
- 负责人和分级不混淆，REQ/BUG 原有分级及筛选正常。
- 不因优先级缺失阻断开发或归档，不批量迁移历史记录。
- 不为显示一个标签新增全量重检查，保持摘要首屏加载策略。
以上要求已完成验收，逐项结果见acceptance.md及关联Change验收证据。

## 关联需求与独立交付
父需求：REQ-0056-requirement-center-change-delivery-cards（已归档）。背景：REQ-0026-requirement-center-standalone-change-cards 已交付可见性。本子需求不修改父级状态，也不重复实现交付拆卡。

## 设计待收敛项
本轮已收敛内联编辑、必要变更记录和来源转换行为，详见 business-flow.md；trace priority 事实源已落实并同步治理规范。接口采用受控异步操作，复用现有操作记录，不新增数据库迁移。

## 当前状态
文档、用户故事、业务流程、验收计划与 HTML 原型已补齐，已评审通过（approved）。原型拆解、Skeleton确认、视觉证据与最终实现一致性均已完成；已关联 add-standalone-change-priority，实施与验证记录见该Change。


## 异步保存实施约定
已确认保留服务端维护窗口和异步控制器。未就绪提示暂不可保存；入队后显示保存中，完成后回读卡片。关闭编辑区不撤销已提交操作，重新读取以服务端事实为准。必要审计随trace原子提交，异步链路复用Task Trace；不新增数据库表。UI Skeleton首轮结构已获用户确认。
