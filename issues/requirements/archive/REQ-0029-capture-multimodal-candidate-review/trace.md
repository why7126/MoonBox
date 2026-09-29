---
requirement_id: REQ-0029-capture-multimodal-candidate-review
title: 新建 Capture 支持图文 AI 整理、候选审阅与确认后幂等批量采集
status: done
created_at: '2026-09-14 08:40:20'
updated_at: 2026-09-29 14:41:41
recorded_by: product
owner: 产品团队
source: 用户反馈
lifecycle_stage: archive
parent_requirement: null
iteration: sprint-007
openspec_changes:
- change_id: add-capture-multimodal-candidate-review
  type: add
  status: archived
related_requirements: []
lifecycle:
  captured: '2026-09-14 08:40:20'
  generated: 2026-09-14 10:25:56
  completed: 2026-09-14 12:10:59
  reviewed: '2026-09-14 23:56:37'
  approved: '2026-09-14 23:56:37'
knowledge_base_refs:
- docs/knowledge-base/best-practices/admin-media-upload-chain.md
- docs/knowledge-base/incidents/20260912-capture-persistence.md
- docs/knowledge-base/retrospectives/sprint-005-retrospective.md
cross_cutting_tags:
- media-upload
prototype_refs:
- path: issues/requirements/review/REQ-0029-capture-multimodal-candidate-review/prototype/web/prototype.html
  role: html-structure
- path: issues/requirements/review/REQ-0029-capture-multimodal-candidate-review/prototype/web/context.md
  role: decomposition
- path: issues/requirements/review/REQ-0029-capture-multimodal-candidate-review/prototype/web/prototype-qa.json
  role: prototype-only-validation
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: done
  req_final_consistency: done
product_data_collection_observability:
  status: applicable
  affected_layers:
  - usage_events
  - request_logs
  - task_traces
  - task_trace_spans
  reason: 图文上传、AI 整理、审阅及批次确认涉及行为、API 和多步骤写入；四层适用，无层级 N/A。
  validation: 文档已覆盖 AC-OBS-001 至 004；真实调用、故障注入和 UI 观察在实施阶段验证，不用原型代替。
readiness: Partially Ready
knowledge_base_gate: Pass
related_change: add-capture-multimodal-candidate-review
priority: P1
---
# REQ-0029-capture-multimodal-candidate-review Trace

## 来源与范围

来源为用户本次 `/req-capture` 输入；已确定并交付新建 Capture 的图文整理、候选审阅、确认后编号与幂等采集边界，详见 `capture.md`。

本条记录的是产品能力需求；本次命令分配的需求编号不属于未来产品内未确认的候选编号。需求评审已通过，已纳入 sprint-007，关联 OpenSpec Change `add-capture-multimodal-candidate-review` 已归档，实施与真实验收已完成。

## 变更记录

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-29 14:35:07 | /opsx-archive | Change `add-capture-multimodal-candidate-review` 已归档，状态同步完成。 |
| 2026-09-16 09:29:05 | /opsx-modify | Change `add-capture-multimodal-candidate-review` 验收返修已同步，待复验或 archive。 |
| 2026-09-15 15:59:38 | /opsx-apply | Change `add-capture-multimodal-candidate-review` apply 完成，待 archive。 |
| 2026-09-15 15:58:00 | /opsx-apply | 完成真实浏览器输入/上传/预览/模型审阅验收，合成UI状态覆盖结果/失败/冲突；同步文档与完成门禁。 |
| 2026-09-15 08:45:00 | /opsx-apply | 用户确认正式 UI 方向为“单一 MD 编辑器 + 内嵌图片/文本文件材料块”；前端实现与文档同步。 |
| 2026-09-15 01:14:27 | /opsx-apply | Change `add-capture-multimodal-candidate-review` opsx.progress 已同步；研发中，未宣告完成。 |
| 2026-09-15 00:32:12 | /opsx-apply | Change `add-capture-multimodal-candidate-review` opsx.start 已同步；研发中，未宣告完成。 |
| 2026-09-14 23:56:37 | /req-review | 评审通过，P1 保留；36 条 AC 与观测/原型材料检查通过，RC-001 至 003 留作实施门禁；下一步先纳入 Sprint。 |
| 2026-09-14 12:10:59 | /req-complete | REQ-0029-capture-multimodal-candidate-review 已完成文档补齐，状态同步为 pending_review。 |
| 2026-09-14 10:25:26 | /req-generate | REQ-0029-capture-multimodal-candidate-review 已生成 requirement.md，状态同步为 draft。 |
| 2026-09-14 08:40:20 | /req-capture | 创建采集记录，初判 P1；同一 Capture 交付闭环保持单条，保留用户已确定边界与后续探索点。 |
| 2026-09-14 10:25:26 | /req-generate | 生成 v1 PRD，状态转为 draft；承接探索结论，保留未确认决策，不创建六件套或 Change。 |
| 2026-09-14 11:10:14 | /req-complete | 用户选择按推荐建议；收敛自动保存、整批续作与首版限额；补齐故事、流程、验收及原型。读 Sprint-005 复盘与 Capture 事故，承接终态反馈、锁内编号、恢复和真实观察；6 条上传横切 AC。 |

## 本次完善验证

- 原型离线 QA：10 项检查通过；4 张原型截图（1440px 深浅主题、结果页、390px）及样式摘要已导出。
- 人工视觉检查：桌面深色与移动端浅色截图已查看，材料/候选层级清晰、操作可见，移动端无横向溢出。
- 原型 QA 仅验证演示交互，无真实模型、上传、编号或文件写入；不改变产品 AC 的 pending 状态。
- 知识库 gate：Pass；media-upload 转化 6 条 AC-XCUT，Capture 事故与 Sprint-005 复盘映射 AC-011 至 015。
- Readiness：Partially Ready，文档齐；真实 UI Skeleton、视觉验收与最终实现一致性为后续实施门禁。

## 关联缺陷

| BUG | 严重等级 | 状态 | 关联 Change | 说明 |
|---|---|---|---|---|
| BUG-0020-req-complete-status-projection-drift | medium | done | fix-req-complete-status-projection-drift | req.complete 后 REQ 状态投影残留 draft/enriching 导致数据漂移 |

## 本轮实施证据（产品验收尚未完成）

后端、真实模型与存储、幂等恢复和客户端数据层已完成验证，证据统一见 `openspec/archive/2026-09-29-add-capture-multimodal-candidate-review/evidence/verification-summary.json` 与 `model-quality.md`。SQLite78项、MySQL39项、前端请求3项通过，真实合成图文链路通过。UI Skeleton首轮已按用户确认方向完成，真实浏览器主链与合成UI状态验收通过；apply 与归档均已执行完成。


## 附件原型复刻返修

2026-09-16：用户验收反馈要求按 `layout-4-console-workbench.html` 一比一复刻 Capture 弹窗布局，并保持当前 UI 设计系统。本次 `/opsx-modify` 已将 Change 文档、规格 delta、任务和验收修复记录同步到归档 Change 的 `acceptance-fixes.md`。

| 时间 | 命令 | 说明 |
|---|---|---|
| 2026-09-16 17:45:00 | /opsx-modify | Change `add-capture-multimodal-candidate-review` 已按附件拆分删除与来源依据行内化完成验收返修：第 2 步不展示 AI 审阅结果，来源依据卡内展示，拆分/删除卡内展开，确认创建直接提交；待用户复验或 archive。 |
| 2026-09-16 19:05:00 | /opsx-modify | Change `add-capture-multimodal-candidate-review` 已完成拆分/删除面板向下展开返修：拆分为左右两个完整子条目且可分别选择需求或 BUG；待用户复验或 archive。 |
| 2026-09-16 19:52:00 | /opsx-modify | Change `add-capture-multimodal-candidate-review` 已完成上传文本文件可删除返修：文本文件显示独立 chip，删除 chip 同步移除 MD 来源文件块；待用户复验或 archive。 |
| 2026-09-16 19:58:00 | /opsx-modify | Change `add-capture-multimodal-candidate-review` 已完成候选卡编辑/删除按钮图标与编辑面板向下展开返修；待用户复验或 archive。 |
| 2026-09-16 22:24:00 | /opsx-modify | Change `add-capture-multimodal-candidate-review` 已完成第 3 步创建结果态返修：左对齐结果卡、REQ/BUG 编号 badge、目录/文件/来源摘要和实底幂等/产物边界说明；待用户复验或 archive。 |


| 2026-09-16 23:05:00 | /opsx-modify | Change `add-capture-multimodal-candidate-review` 已完成项目内相似 REQ/BUG 提示返修：候选卡展示可能相关项，支持继续创建、合并到已有记录、作为已有记录补充材料或删除；合并/补充候选不进入确认创建批次且不分配新编号；待用户复验或 archive。 |
| 2026-09-16 23:12:00 | /opsx-modify | Change `add-capture-multimodal-candidate-review` 已完成 MD 文本材料块可删除返修：MD 文本 chip 动态显示并可删除，删除时保留上传来源文件块和图片材料，材料计数同步更新；待用户复验或 archive。 |
| 2026-09-16 23:30:00 | /opsx-modify | Change `add-capture-multimodal-candidate-review` 已完成默认 Markdown 编辑器不显示来源 chip 返修：来源材料只展示并统计额外上传的图片和文本文件，编辑器正文默认隐含存在；待用户复验或 archive。 |
| 2026-09-16 23:38:00 | /opsx-modify | Change `add-capture-multimodal-candidate-review` 已完成相似项提示空态隐藏返修：无匹配时不显示可能相关模块或继续创建文案，有匹配时保留合并/补充材料并使用恢复创建入口；待用户复验或 archive。 |
| 2026-09-16 23:48:00 | /opsx-modify | Change `add-capture-multimodal-candidate-review` 已完成创建结果态图标移除返修：成功、失败或中断结果态不显示圆形勾选图标，confirming loading 保留；待用户复验或 archive。 |
- 2026-09-29 14:35:07 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive add-capture-multimodal-candidate-review
