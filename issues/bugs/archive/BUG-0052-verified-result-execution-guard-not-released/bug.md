---
bug_id: BUG-0052-verified-result-execution-guard-not-released
title: 成果已核验但执行保护未解除导致需求卡片滞留待评审
severity: high
status: done
owner: 产品团队
created_at: '2026-10-20 08:58:02'
updated_at: 2026-10-21 08:39:35
discovered_at: '2026-10-20 08:43:54'
environment: 本地 Docker 产品，相关运行代码指纹与工作区一致
related_requirement: REQ-0046-chat-execution-output-status-feedback
related_bug: BUG-0049-archive-wrapper-workflow-sync-unrecognized
related_change: null
root_cause_status: confirmed
---

# 成果已核验但执行保护未解除导致需求卡片滞留待评审

## 现象与影响

REQ-0046 的 trace 与注册表均 approved，原评审执行 completed，候选与应用已 applied / verified，业务操作 completed / complete；但对象执行保护仍为 needs_review / result_unverified，confirmed_stage 为 review-ready，result_revision 为空。需求中心卡片滞留“待评审”，显示结果待核对，加入迭代禁用；Chat 恢复面板却已显示业务完成。

严重等级 high：阻断合法后续规划，造成跨页面结果矛盾并可能诱导重复评审；未发现数据丢失，不宣称全部治理操作均受影响。已确认样本为 source 模式 req-review；其他依赖相同保护核对逻辑的命令存在潜在影响，需逐能力回归，不能直接外推。opsx-archive 已有独立证明分支，不将其等同本例。

## 复现与期望

### 既有现场核查（只读）

1. 本地 /requirements 查看 REQ-0046 阶段、异常标识与加入迭代按钮。
2. 使用“查看执行”定位原评审；核对需求 trace、注册表与原轮次的保护、候选、应用及业务操作记录。
3. 按原候选 baseline.files 合并 result.after 重建历史成果快照；读取应用的 workflow_sync 证明，比较历史成果与当前 stable 快照的摘要，并分别执行纯函数 validate_result。
4. 对照核对分支、外部同步避让分支与卡片阶段覆盖分支，不调用实际 reconcile、确认或恢复写接口。

期望：历史操作完成可证明，执行保护在可靠核验后收敛；生命周期、执行异常与下一步准入分别表达。无关后续修改不使历史成功永久无法确认；相关变更仍接受权限、归属、版本和并发核验。
实际：证明绑定整个治理目录的旧摘要，后续修改导致核对永久不满足；已完成的业务操作不直接闭合保护，外部同步避让旧保护，卡片继续投影旧阶段。

### 最小内存验证（已执行）

从上述历史成果快照复制字典，在内存中增加一份无关 docs Markdown，再计算 digest 和 validate_result。业务校验保持 true，摘要变为不同值；根据当前核对条件 synced 为 false，将跳过 guards.confirm。没有创建探针文件，没有修改数据库、原成果或证明。该验证证明失配条件，不冒充完整端到端故障注入回归。

## 已确认根因

root_cause_status: confirmed，范围为当前持续未收敛机制；首次错过确认窗口的精确历史时序另列不确定性。

### RC-1 历史完成证明与当前全局指纹耦合

snapshot.py 的 ROOTS 包含 issues、iterations、openspec、docs、rules，digest 对范围内文件路径和内容摘要整体计算。execution_context.reconcile 先检查 journal 的同步步骤，再检查应用 proof；后者要求 proof.object_id 匹配且 proof.source_hash 等于当前 snapshot.revision。已有应用证明存在时不进入缺失证明恢复分支。当前摘要不同导致 synced=false，随后直接 continue，不执行保护确认。

当前现场：proof 与重建历史成果摘要相等；proof 与当前摘要不等；历史和当前业务校验均 true。故障不是证明丢失，也不是当前需求未通过既有业务校验。业务校验 true 只说明现有结构性校验通过，不单独代表所有并发与副作用门禁均可绕过。

### RC-2 完成链路与保护确认链路分离，缺少可靠收敛保障

source 模式 preparation.collect 写入 workflow_sync 证明、applied/verified 应用及 applied 候选；recovery_service.checkpoint 将业务操作推进 completed/complete。这两条完成路径不直接确认 execution_guard。guards.confirm 当前由 execution_context.reconcile 调用，而 reconcile 的入口集中在看板读取和命令准入。

原执行终态先将保护置 needs_review；后续完成与保护确认之间存在窗口。一旦全局快照发生变化，延后的核对无法使用原证明，不会自动基于历史完成事实与当前相关依赖重新建立安全确认。

### RC-3 补偿避让与旧阶段投影使阻塞持续且难以解释

reconcile_external 遇到 running/needs_review 且存在 operation_id 时直接返回，不会用外部同步覆盖它。reader 在 can_send=false 时用 guard.confirmed_stage 覆盖生命周期阶段，并禁用动作。普通 req-review 证明失配只跳过核对，未更新为具体失配原因，因此页面始终笼统提示 result_unverified。

这些保护的安全目的合理；缺陷在于缺少可恢复的一致性闭环，修复不能简单删去版本比较或直接把 guard 改成 idle。

## 可复核证据

证据采集日期 2026-10-20，承接紧邻本命令的 bug-explore；本命令只落盘结论，未重新执行评审或恢复。时间统一为 Asia/Shanghai；私有操作、会话与用户标识不落盘。

| 编号 | 来源及方法 | 结果与支持判断 |
|---|---|---|
| E1 | 用户截图与 Chrome 本地 /requirements | 已评审文档对应卡片仍在待评审，结果待核对，加入迭代禁用 |
| E2 | canonical SQLite 以原对象/轮次关联只读查询 | guard=needs_review，action=req-review，terminal=completed，confirmed_stage=review-ready，result_revision=null；应用 applied/verified，错误为空 |
| E3 | 运行容器私有 operation 记录，只输出白名单字段 | 原轮次 operation 存在，phase=terminal、classification=partial_write；记录中 10 个步骤 sync_succeeded 均 false；应用 workflow_sync 存在，event=req.review，对象匹配 |
| E4 | baseline.files + result.after 在内存重建 | proof_matches_historical_result=true；historical_business_valid=true，排除历史成果证明缺失或不匹配 |
| E5 | 同运行容器读取当前 stable 快照 | proof_matches_current=false；current_business_valid=true；采样共 2728 文件，与历史有 184 项变化，其中目标目录 9 项、目标目录外 175 项；计数仅为当次快照 |
| E6 | 历史快照增加无关文档的内存样本 | business_valid=true、hash_changed=true；证明无关修改也足以触发全局摘要失配 |
| E7 | guard、候选、应用、业务操作时间字段 | 2026-10-19 19:33:44 保护仍待核对；19:33:50 应用 applied/verified、业务操作 completed/complete；后续现场保护未解除 |
| E8 | backend 容器与工作区 SHA-256 对比 | execution_context、execution_guard、reader、preparation、recovery_service、snapshot、execution_validation 七份相关模块逐项一致，排除这些路径的部署代码不一致 |

复核代码入口（行号随版本可能变化，以函数为准）：

- `src/backend/app/governance/snapshot.py`：ROOTS、digest。
- `src/backend/app/governance/execution_context.py`：reconcile，应用 proof 比较及跳过确认分支（取证时约 185—217 行）；reconcile_external 避让分支（约 235—241 行）。
- `src/backend/app/governance/preparation.py`：_verify_source_workflow_sync、collect 的 source 模式完成分支。
- `src/backend/app/governance/recovery_service.py`：checkpoint。
- `src/backend/app/governance/execution_guard.py`：terminal、confirm。
- `src/backend/app/governance/reader.py`：build_requirement_center_context 的 confirmed_stage 覆盖（约 117—129 行）。

## 结论边界与待补充历史细节

尚不能确定首次错过确认窗口时，哪一次读取、哪一份文件变化或执行调度先后触发失配；不据此把故障单独归因于 2026-10-20 的需求文档更新。当前持续阻塞的逻辑条件与代码机制已由 E2—E8 确认，历史起点不确定不改写为完整时序已复现。

原 capture 中“证明可能缺失”的初判保留为采集历史，本次检查已排除该样本证明缺失。175 项目标目录外变化不全部认定为语义无关依赖；无关修改足以触发失配由 E6 独立证明。当前完整端到端故障注入、自动恢复及跨命令范围仍待修复阶段验证。

## 修复方向与预防目标

1. 让应用核验与保护确认具备可靠交接及幂等重试，覆盖提交窗口、服务重启和响应丢失；不依赖用户恰好在文件变化前打开看板。具体事务/持久任务方案留待设计评审。
2. 分离不可变历史操作完成证明与当前资源/下一步准入。核验绑定对象、轮次、成果、应用和必要依赖，保留当前版本与并发围栏；评估将全仓摘要拆为操作相关证明和当前准入检查，不粗暴取消摘要核验。
3. 对“有可信完成证明但保护未闭合”提供受控重核验，不重跑模型、不重复应用、不覆盖后续成果；既有源文件后续合法修改不改写原执行终态。
4. 输出结构化原因：缺证明、相关依赖变化、占用未知、权限变化等；记录最近核验结果与可用动作。状态矛盾检测和补偿有界，不无限重试或重复通知。
5. Chat、卡片和恢复详情消费统一可信结果。生命周期、异常和准入分离；前端不能仅凭 approved/applied 单字段解锁。
6. 现有数据仅通过正式受控核验路径恢复；保留原证明、失败/停止历史及审计，不手工改库、补假 proof 或重复评审。

## 建议回归与验收

- 正常首次成功：证明、应用、业务操作与保护最终一致。
- 应用完成/保护确认窗口故障、重启、响应丢失：最终收敛，模型和副作用不重复。
- 无关文件变更不阻断历史完成确认；相关依赖变化具体拒绝，准入仍安全。
- 历史完成与当前资源变化分离，失败/停止后恢复不伪造首次成功。
- 多对象、多轮、旧事件迟到、重复核验、权限撤销、占用未知和缺证明不错误解锁。
- 具体失败原因可观测；已评审但受保护的 UI 保留可信阶段并阻断危险动作。
- E6 内存验证、组件/API 回归、真实正常/恢复样本和部署版本证据分别登记，不互相替代。

## 关联与交付边界

后端完成证明、保护解除、相关依赖判定、补偿和结构化能力由本 BUG 承接。REQ-0046 的 FR-013/014、AC-023—026 承接展示、异常说明及核验/差异/原执行入口；真实联调依赖后端能力，但不扩大原恢复权限。BUG-0047 为成果未应用，BUG-0049 为归档包装同步观测漏识别，本例保持独立并关联历史修复。

初次 bug-generate 仅生成主文档并同步至 draft。后续 bug-complete 已补齐 root-cause.md、workaround.md、acceptance.md 并同步为 pending_review；未执行评审、未创建 Sprint 或 OpenSpec，未修改产品实现或解除实际保护。

## 产品数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: API、execution_guard、governance_proof、request_logs、task_traces、治理操作结果和看板投影；前端交互观测由 REQ-0046 承接。

validation: 操作/应用/轮次关联、证明版本、核验原因和保护跃迁需可追溯；后台补偿不伪造用户行为。证据仅摘要化，不保存完整 Prompt、凭证、原始数据库或本机路径。本轮 API、DB schema、UI、部署、安全策略及生成客户端均未变更；实现时按实际影响同步。

## 跨入口一致性返修约定

卡片只呈现一次当前动作的阻塞摘要，历史成果、核验时间、重新核验、差异和原执行收进默认折叠的“状态详情”。运行详情仍归属于原Chat轮次。归档准入采用当前Change的结构化验收证据和明确人工签认，与CLI共用只读判定；进度统计按AC身份去重，自动通过不等于用户人工签认。旧评审历史保留，经过验证的后续合法流转可承接旧保护，真实冲突、未知占用、权限变化、缺失或过期证据仍阻断。覆盖REQ与BUG，不能按具体编号特判。

补充确认：旧评审依赖对象文档的逐字节比较仍阻断后续合法阶段；原预演只校验规格合并，不能替代产品准入。当前返修采用受验证的后续事实承接，禁止直接清空守卫。

后续补充评审仍为 approved 且对象身份一致时，只有完整评审文件被当前有效验收证据覆盖，才能承接旧评审保护；结论拒绝、未覆盖或过期仍阻断。关联解析统一支持 related_change、related_changes 与 openspec_changes 的字符串/对象形式。

## 验收后归档衔接补充

再次验收产生的报告与 trace 运行正文属于派生输出，不得使归档恢复记录自失效；交付输入、链路身份、真实证据完整性及并发变化仍受门禁保护。验收收尾后必须通过产品与 CLI 共用的正式准入，验收 passed 不等于归档 ready。错误须区分交付输入变化、旧记录过期、规格基线缺证、身份冲突和记录损坏。

关联链路先归档后，验收证据按唯一已完成归档身份定位，继续核对原内容哈希；活动目录仍存在、归档身份歧义、未完成或证据被篡改时仍阻断。

跨日归档补充：确认准备日期与实际目录日期耦合、迁移后自动验收计划仅查活动目录导致人工统计回退。由原 BUG 链路修复，验收覆盖跨日、中断重试、重复恢复及证据篡改拒绝；正式 REQ 收尾不得重复合并规格。
