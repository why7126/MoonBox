---
title: 统一运行状态与核验入口实施追溯
created_at: '2026-10-20 12:58:01'
updated_at: '2026-10-20 22:23:43'
req_id: REQ-0046-chat-execution-output-status-feedback
change_id: fix-chat-unified-run-status-verification
iteration: sprint-011
status: applied
execution:
  schema_version: 1
  started_at: 2026-10-20 12:59:38
  completed_at: 2026-10-20 14:39:23
  last_event: opsx.apply
---

# 统一运行状态与核验入口实施追溯

## 来源与就绪

REQ-0046-chat-execution-output-status-feedback，P2，sprint-011，已评审并in_sprint。Requirement Readiness: partially ready；文档与原型拆解齐备，可进入实现，Skeleton、视觉与真实联验仍pending。已执行opsx.start并完成状态、动作与卡片实现；完成门禁以tasks和verification.md为准。

## 原型与冲突记录

来源：issues/requirements/review/REQ-0046-chat-execution-output-status-feedback/prototype/web/prototype.html及context.md。局部一致策略、Conflict Resolution、UI Contract、UI Skeleton与动作矩阵见design.md。原型拆解done；Skeleton已实现并补充1440/390证据；双视口关键交互与computed style已采集；Mock/API边界已声明；最终REQ一致性pending。

## 依赖与验收记录

关联fix-verified-result-execution-guard-convergence；后端12/14，同版REQ/BUG样本通过，本REQ已实施，联合UI及最终补跑结果见verification.md。REQ AC-023—026对应BUG AC-010/任务3.5；证据放各Change evidence/并保留指纹及可解析交叉引用。非联合展示任务可独立推进。完整任务见tasks.md，已运行定向测试与真实产品核验。

product_data_collection_observability: applicable；affected_layers: web/api/request_logs/task_traces；reason与validation见design.md。无DB迁移、对象存储或部署机制改变，不新增权限。API消费与潜在字段缺口处理边界已明确。


## 实施进度与验证

已接入纯状态投影、每轮详情、恢复/草稿/证据/差异动作族、卡片核验与原轮次定位；移除独立底部面板。增加只读关联字段并同步生成客户端。前端52项定向测试通过；后端73项及6个子场景通过，新增卡片身份断言后17项交接测试通过。类型与构建通过，仅既有包体体积提示。视觉正在采集，尚未签认全部 AC。首次骨架截图为1470宽，后补1440采样将明确标记补证，不追写为实现前用户签认。

## 验证记录

交付、证据等级、旧证据复用范围、合成与真实恢复边界、全仓Capture既有失败、视觉及观测声明见 [实施验证](verification.md)。当前REQ真实完成且冲突恢复核验保持1轮1应用；BUG9096的字段契约拒绝保留为负例，授权的BUG9097正常补验已通过，REQ/BUG均1轮1应用且交接在60秒内。未归档、未创建后续Issue。

长耗时真实样本发现原20次轮询预算耗尽后未随终态重读，已由refreshKey（原轮次状态/候选状态）、可见性恢复及核验事件重新启动有限读取预算修复；新增超过63秒后终态到达的回归通过，不增加模型调用。最终前端指纹在构建后更新；后端及已完成真实轮次保持不变。

## 最终验收结果

15/15实施任务完成。逐AC正式报告30/30通过、0失败、0阻塞、0待采集；3次命令执行、27次安全去重。见[evidence/acceptance/20261020143355295059-8a155cca/summary.md](evidence/acceptance/20261020143355295059-8a155cca/summary.md)。BUG-0052联合验收14/14通过，未追加模型调用；本地Docker服务健康与资源记录见evidence/local-deployment.json。

最终Workflow Sync：opsx.apply与opsx.accept均成功，REQ acceptance_status=passed；归档临时副本预演passed，readiness ready且无stale项。未执行正式归档、提交或推送。AI Usage自动发现无可归因token事件，usage_mode unavailable、0条command run、Sprint用量快照skipped，不编造用量。

## 当前验收返修

跨入口归档准入、卡片详情折叠、完整 AC 汇总和真实归档联验进行中；此前通过报告不覆盖本轮改动。根因、补充发现与证据分层见 [返修台账](acceptance-fixes.md)。保留首次 applied 与 completed_at，最终结论待本轮复验。

本轮跨入口返修实现与独立验证已完成；真实隔离归档证据见 evidence/cross-entry-archive-verification.json，完整反馈及 REQ 子文档扫尾见 acceptance-fixes.md。最终 ready 状态以当前增量验收为准；正式对象未归档。


## 本轮返修最终验收

31/31 全部通过，当前 ready，归档预演与正式产品准备通过；保留 applied 和首次执行完成时间。报告 [最终验收](evidence/acceptance/20261020174447645231-8323c712/summary.md)，证据与版本边界见 [返修台账](acceptance-fixes.md)。正式对象未归档。

## 归档预演返修记录
旧预演结论撤销；修复与复验见 acceptance-fixes.md 的“归档预演零退出码误判返修”。首次 apply 完成事实保留。

本轮归档预演复验：46 项回归通过；完整验收 passed，证据 evidence/acceptance/20261020182810727116-1a7870a0/summary.md；双顺序临时归档证据 evidence/archive-preview-joint.json。

## 验收输入返修
产品投影遗漏 tests 与目录指纹缺失已定位，返修过程和最终证据见 acceptance-fixes.md。保留首次完成事实。

发送快照竞争返修进行中；真实发送与并发测试、部署证据见 acceptance-fixes.md，原准备成功证据不代表完整发送成功。

发送竞争实际 HTTP 入队与幂等证据：evidence/send-snapshot-http.json；核心 128 项通过。未调用模型或归档正式对象，终态验收不冒称完成。

实际发送终态复验：两次隔离模型归档均完成，保护解除；证据见 evidence/send-snapshot-real-chain.json，详情见 acceptance-fixes.md。正式对象未归档。

历史归档基线返修：连续哈希归档证据承接旧记录，产品与CLI共享恢复准入；完整台账见 acceptance-fixes.md，验证完成后回填 evidence/archive-baseline-admission.json。

归档基线返修完成：正式 REQ/BUG 的产品准备、发送预检与 CLI 一致放行；36/20 项验收通过，旧记录保留，正式对象未归档。证据：evidence/archive-baseline-admission.json。

## 本轮增量验收复核

2026-10-20 22:23:43：完整范围36/36通过，36项按当前输入与附件指纹复用，新增AC命令执行0、去重0、失败0、阻塞0、待采集0。本轮独立执行归档临时副本预演，退出0；readiness ready，无stale。报告：[本轮完整验收](evidence/acceptance/20261020222304220411-1d492481/summary.md)。既有产品轮次与视觉证据复用，不宣称本轮重新采集。Workflow Sync opsx.accept退出0，REQ验收passed；未执行正式归档。AI Usage缺少会话输入，unavailable；治理采集start返回invalid-input-or-ledger，未建立有效运行记录。

派生验收输出返修进行中；保留首次 apply 事实，完整台账见 acceptance-fixes.md。

再次验收归档返修：完整验收报告 openspec/changes/fix-chat-unified-run-status-verification/evidence/acceptance/20261020230640604685-f5130615/summary.md；真实发送终态与独立 CLI 归档证据见 evidence/reaccept-archive-real-chain.json。未归档正式对象。最终统一准入及记录不变性见 evidence/acceptance/reaccept-final-verification.json。

再次验收归档返修：完整验收报告 openspec/changes/fix-chat-unified-run-status-verification/evidence/acceptance/20261020232311082751-fd2d8cda/summary.md；真实发送终态与独立 CLI 归档证据见 evidence/reaccept-archive-real-chain.json。未归档正式对象。最终统一准入及记录不变性见 evidence/acceptance/reaccept-final-verification.json。
