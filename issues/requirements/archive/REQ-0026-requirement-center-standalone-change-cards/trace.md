---
requirement_id: REQ-0026-requirement-center-standalone-change-cards
title: 需求中心 Change 可见性与关联追溯
status: done
created_at: '2026-09-12 17:51:26'
updated_at: 2026-09-17 08:12:45
lifecycle_stage: archive
lifecycle:
  generated: '2026-09-12 21:11:07'
  captured: '2026-09-12 17:51:26'
  enriched: '2026-09-12 21:17:00'
  reviewed: '2026-09-13 23:55:55'
  approved: '2026-09-13 23:55:55'
iteration: sprint-005
openspec_changes:
  - change_id: add-requirement-center-change-visibility
    type: add
    status: proposed
related_requirements:
  - REQ-0022-local-project-import-product-iteration
knowledge_base_refs:
  - docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
  - docs/knowledge-base/retrospectives/sprint-003-retrospective.md
cross_cutting_tags: []
prototype_refs:
  - path: issues/requirements/archive/REQ-0026-requirement-center-standalone-change-cards/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/archive/REQ-0026-requirement-center-standalone-change-cards/prototype/web/context.md
    role: decomposition-and-contract
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: passed
  computed_style: passed
  key_interactions: passed
  req_final_consistency: checked_before_archive
product_data_collection_observability:
  status: applicable
  affected_layers:
    - web
    - api
  reason: 阶段按钮复用Web交互及API能力门禁；需核验行为与请求日志关联，不新增执行服务或DB。
  validation: 旧范围证据见Change；新增动作待验证行为事件、直接API拒绝、请求ID、脱敏、采集失败不阻断及能力门禁。无新执行器，Task Trace复用现有链路；DB、部署、对象存储和保留周期不变，客户端生成仅在后续接口变化时适用。
scope_revision:
  status: 迭代内
  reviewed_at: '2026-09-13 23:55:55'
  reason: 独立Change阶段按钮与现有能力门禁复用，旧范围已应用，新范围未实施
related_change: add-requirement-center-change-visibility
priority: P1
---

# 需求追踪

## 当前摘要

既有可见性和Sprint标签已实施，保留迭代内及原Change关联。本轮新增阶段动作范围已完善，已评审通过，待Sprint范围核对和OpenSpec同步后实施，不沿用旧视觉通过结论。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-09-14 08:44:27 | /opsx-archive | Change `add-requirement-center-change-visibility` 已归档，状态同步完成。 |
| 2026-09-14 00:06:08 | /opsx-apply | Change `add-requirement-center-change-visibility` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-09-13 23:59:50 | sprint.propose | sprint-005纳入阶段按钮增补3人天，REQ共8人天；待同步OpenSpec，新范围未实施。 |
| 2026-09-13 23:55:55 | req.review | 阶段按钮增补评审通过；新增动作待Sprint范围核对及OpenSpec同步，保留原实施历史。 |
| 2026-09-13 23:53:03 | req.complete | 纳入独立Change阶段按钮；补充矩阵、权限与执行门禁、原型状态及6项动作AC、1项横切AC；新增范围待评审。 |
| 2026-09-13 01:01:49 | /opsx-modify | Change `add-requirement-center-change-visibility` 验收返修已同步，待复验或 archive。 |
| 2026-09-12 23:33:35 | /opsx-apply | Change `add-requirement-center-change-visibility` apply 完成，待 archive。 |
| 2026-09-12 23:26:33 | /opsx-apply | Change `add-requirement-center-change-visibility` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-09-12 17:51:26 | req.capture | 记录独立 Change 卡片需求，初判 P1。 |
| 2026-09-12 21:11:07 | req.generate | 整合独立 Change 可见性与关联身份追溯，生成 PRD，状态更新为 draft。 |
| 2026-09-12 21:17:00 | req.complete | 补齐故事、流程、11项功能AC、5项原型AC、2项同域横切AC和交互原型；承接Sprint-003抽屉、Mock边界与文档一致性经验。 |
| 2026-09-12 22:20:18 | req.complete | 按用户反馈重做当前卡片对照：原ID下新增同字号Change ID，中文标题改为Change标题；撤销自建关联区/抽屉，同步全部子文档，视觉证据待验证。 |
| 2026-09-12 22:24:33 | req.review | 通过范围与实现策略评审；保留后续视觉、权限及一致性门禁。 |
| 2026-09-12 22:42:37 | req.opsx | 生成add-requirement-center-change-visibility，承接两项卡片调整及独立Change范围。 |

- 阶段迁移：plan → review（/req-review）

## 固定禁用提示返修结论

本节替代上一轮独立Change一律禁用的结论。后端复用REQ/BUG阶段必需文档与非空门禁，并核对唯一Sprint；缺失/空文档/只读才返回相应原因，不再固定生成测试核对或能力未接入提示。文档存在不代表测试执行通过；前端复用已有testProgress/manualAcceptanceCount判断，数据不存在不伪造检查结论。

独立Change与REQ/BUG进入同一动作处理器：研发中读取tasks；真实模式中当前未支持的开发/归档动作点击后显示现有统一能力提示，不执行写入；Demo沿用现有弹窗和模拟流转，不接入真实执行。取消、提交防重入和刷新行为复用当前组件，未新增服务或权限。

验证：后端94项、前端79项、TypeScript通过；1440/390深浅主题4组真实组件合成API浏览器验收通过，截图和computed style位于evidence/action-gates/。非部署观察，未执行真实开发/归档。保留现有权限和真实能力限制；新证据替代旧固定禁用截图。

## 独立交付验收来源返修（当前结论）

验收中不再固定要求acceptance.md：优先校验trace.acceptance_refs声明的Change内相对Markdown路径；显式引用无效、缺失或为空返回具体待核实原因，不回退。未声明时查现有acceptance.md、verification.md，再识别trace中非空“验证记录/验收记录/验证结果/验收结果”章节。不得跨Change或通过绝对路径、父路径、符号链接越界读取。没有证据来源提示待核实，不补建文件；本机制定位证据，不自动判断验收通过，验收态和tasks全勾均不代替验收。

真实仓库样本standardize-sprint-default-capacity以trace验证记录作为来源；unify-issue-classification-metadata使用acceptance.md，两者当前源码均无来源阻塞。后端95项回归通过，包含显式引用、缺失、空源、越界与历史trace来源；浏览器复用真实组件+合成API在1440/390深浅主题验收，证据evidence/action-gates，非部署验收。

运行页面核对：用户地址localhost:18102对应moonbox-web，加载index-y8JI4bjc.js，其中无旧能力提示；moonbox-backend镜像动作函数也无旧提示，但仍采用上一版固定acceptance.md清单，尚未部署本次解析。未对运行容器做重建或重启，截图旧提示的实际响应来源仍未取得，不断言缓存根因。

REQ主文档、故事、流程、验收、trace、原型context及HTML已核对同步；capture/review保留历史，不需改写。API既有action字段形状不变，无需OpenAPI/Orval生成；product_data_collection_observability为applicable，affected_layers为api，复用请求日志/授权，验证无越界；无新增DB、部署配置、存储、保留周期或Task Trace。
- 2026-09-14 08:44:27 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive add-requirement-center-change-visibility

## 关联缺陷

| BUG | 严重等级 | 状态 | 关联 Change | 说明 |
|---|---|---|---|---|
| BUG-0018-standalone-change-acceptance-source-unverified | medium | done | fix-standalone-change-acceptance-source | 独立 Change 卡片误报验收来源待核实 |
