---
bug_id: BUG-0052-verified-result-execution-guard-not-released
status: done
created_at: '2026-10-20 08:49:59'
updated_at: 2026-10-21 08:39:36
severity: high
owner: 产品团队
source: 用户截图、同会话 explore 及明确记录授权
lifecycle_stage: plan
related_requirement: REQ-0046-chat-execution-output-status-feedback
related_bug: BUG-0049-archive-wrapper-workflow-sync-unrecognized
related_bugs:
- BUG-0047-review-recovery-operation-record-missing
- BUG-0044-requirement-stage-premature-transition-session-split
title: 成果已核验但执行保护未解除导致需求卡片滞留待评审
environment: 本地产品，部署版本待核查
---

# 成果已核验但执行保护未解除导致需求卡片滞留待评审

## 现象与影响

REQ-0046 文档与注册表已 approved，对应评审成果应用 applied / verified，但需求中心卡片仍在“待评审”，显示“结果待核对 · 已产生的文档会保留”，加入迭代禁用。high 为初判：阻断后续规划且可能诱导重复评审；尚无数据丢失证据，不外推为所有治理命令故障。

## 复现与期望

1. 本地产品 /requirements 查看 REQ-0046 卡片的阶段、异常标签和加入迭代动作。
2. 通过查看执行进入原评审会话，核对完成反馈及恢复面板。
3. 只读核对该对象 trace、注册表与同一执行关联的应用、保护记录，禁止重新评审或手动解锁取证。

期望：可信业务完成与保护解除最终一致；已评审生命周期与执行异常分别表达，异常说明具体，核验安全且不重放业务副作用。
实际：生命周期 approved 与已核验应用并存，保护仍 needs_review，卡片被旧 confirmed_stage=review-ready 覆盖。

## 已有证据与根因边界

复用本会话 2026-10-20 的截图、Chrome 本地产品页面及 canonical SQLite 聚焦只读查询；仅保存脱敏摘要，不复制数据库、原始记录、会话标识或本机路径。不是本次重新执行评审的结果。

| 编号 | 来源 | 观察 |
|---|---|---|
| E1 | 用户截图、/requirements 页面 | 待评审列中 REQ-0046 显示结果待核对；加入迭代禁用 |
| E2 | REQ trace 与 requirements/_registry.yaml | approved / review，无 Sprint、Change |
| E3 | 同一原评审的保护记录 | action=req-review，terminal_status=completed，state=needs_review，reason_code=result_unverified，confirmed_stage=review-ready，result_revision 为空；记录更新时间对应 2026-10-19 19:33:44 |
| E4 | 按 E3 原执行关联查询候选与应用 | candidate=applied，application=applied，phase=verified，二者错误字段为空 |
| E5 | src/backend/app/governance/reader.py | 不可发送时用 confirmed_stage 覆盖卡片阶段，并禁用后续动作 |
| E6 | src/backend/app/governance/execution_context.py | reconcile 依赖操作证明及当前快照匹配；已有活动/待核对 operation 时 reconcile_external 直接返回 |

直接显示机制 confirmed：执行保护覆盖生命周期投影。保护未解除的具体根因仍 probable/待验证：可能涉及证明缺失、版本失配或核对链路未完成；不能断言本次文档修改导致故障，也不能仅凭 applied 标记绕过完成核验。

## 后端修复与产品预防目标

本 BUG 统一承接“完成证明与执行保护最终一致”的后端闭环，单条记录而不拆散同一完成核对链路；展示与入口交互由 REQ-0046 承接。

1. 建立可供 Chat、看板与恢复详情共用的可信操作结果契约，关联对象、轮次、操作、成果、应用、核验和版本；禁止各消费端从正文独立推断完成。
2. 应用核验后可靠推进保护确认；处理跨存储提交窗口、服务重启、响应丢失与重连。安全核对只读业务成果且幂等，不重跑模型、不重复应用，允许受控更新核对状态。
3. 评估将完成证明绑定至本操作的对象、文件与必要依赖版本，而非无关全仓变更。相关依赖变化仍须拒绝并解释，不能通过缩小指纹范围削弱并发安全；最终方案须有根因证据和评审。
4. 区分不可变历史完成证明与当前资源/下一步准入：后续合法修改不改写历史成功，但可使新动作需重新核验。失败、停止与恢复完成历史均保留。
5. 业务阶段、执行保护和下一步准入分别返回：异常不伪造生命周期回退；未经可信生命周期核验的 approved 文本不得单独放行。
6. 提供结构化原因和合法动作：证明缺失、相关文件变化、执行占用未知、权限不足等；读取/核验与恢复写入严格区分，保护仍按对象归属、权限、版本及幂等校验。
7. 检测“已核验但保护未解除”“无活动执行却持续占用”等矛盾并触发有界核对；仍不收敛时记录原因、最近核验时间与需维护者处理项，避免无限重试或重复通知。

## 建议验收

- 正常首次应用核验后保护解除，看板、Chat 与恢复详情同源收敛。
- 在核验成功与保护确认之间注入失败/重启、响应丢失后仍可安全收敛；重复核对不重复模型调用、成果应用或迁移。
- 无关文件变化不影响操作完成证明；相关依赖变化精确拒绝，不覆盖较新成果。
- 历史完成保持可追溯，当前资源变化只影响适用的新动作；旧事件、多轮/多操作不串用结果。
- 证明缺失、占用未知、撤权等不以 approved/applied 单字段解锁；提供安全原因与允许动作。
- 已评审但待核对在可信生命周期列展示异常，准入仍可阻断；与 REQ-0046 联合验收。
- 状态矛盾检测有界、可观测，服务重启不丢失核对进度；合成故障、真实首次成功、历史恢复与部署版本证据分别记录。

## 重复检查与分工

检查 bugs/CHANGELOG.md、_registry.yaml 及相关 capture：BUG-0047 为缺恢复记录导致成果未应用；BUG-0049 为归档包装脚本同步观测漏识别；BUG-0044 为阶段提前迁移与会话分裂。均已归档；当前“评审应用已 verified、保护仍待核对”触发与修复目标不同，建立关联而不重开旧结论。BUG-0050/0051 为归档验收夹具，不承接本次产品修复。

REQ-0046 负责生命周期与异常分层展示、状态文案、核验/差异/原执行入口、权限态及统一动作反馈；本 BUG 负责后端可信证明、保护收敛、冲突检测与核验能力。UI 不绕过 BUG 的准入门禁；后端未提供能力时不出现虚假可用入口。

## 数据采集与待补证

product_data_collection_observability: applicable

affected_layers: governance completion proof、execution guard、API、request_logs、task_traces、看板状态投影；用户交互观测由 REQ-0046 承接。

validation: 后续核对操作关联、证明版本、保护跃迁、原因与核验次数；不记录原始 Prompt、凭证、客户内容。本次仅文档记录，API/DB schema、部署、安全策略及客户端生成均未修改。

待补证：对应私有完成证明的存在与内容摘要、当前/历史指纹差异、运行部署版本、核对失败分支及隔离复现。保留原始记录，不伪造 proof、不手动更新 guard、不重复评审。
