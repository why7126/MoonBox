---
title: 已核验成果与执行保护收敛技术设计
created_at: '2026-10-20 09:11:47'
updated_at: 2026-10-20 22:45:30
---

# 已核验成果与执行保护收敛技术设计

## 背景与现状

Readiness: Ready。BUG包齐全、已批准、in_sprint，关联 sprint-011，估算8人天。复用已归档BUG-0044/0047/0049与REQ-0047实现；REQ-0046承接展示。根因证据见BUG root-cause.md E1—E10；分析对应已比对部署模块，不能推断首次故障时序。

## 根因

RC-1：历史proof.source_hash要求等于当前issues/iterations/openspec/docs/rules全局摘要，无关变化也使确认失效。RC-2：collect/checkpoint的应用和业务完成没有可靠交接到guards.confirm，依赖读取核对。RC-3：带operation_id的旧保护被外部核对避让，reader使用旧confirmed_stage覆盖真实生命周期且只返回result_unverified。

## 修复方案

### 1. 历史证明与当前准入

保留现有source_hash用于验证原快照完整性，不再用当前全局摘要相等作为唯一放行条件。复用既有schema v1操作记录及project/object/action/run/operation/application身份关联，保留结果摘要和可信同步事件；相关依赖manifest从持久baseline/result确定性派生，不改写历史证明。按baseline与result.after重建历史结果，核对应用唯一性、业务校验及同步证明，输出historical_result=verified/unverified/conflict。

当前准入另查授权、项目绑定、对象当前版本、活动执行、守卫generation及必要依赖。source req-review/bug-review的相关集合至少包括目标Issue主文档/trace/review、生命周期目标路径及迁移来源、注册表中该对象条目、父需求关联条目、参与本次同步的Sprint条目和命令校验读取的规范版本。共享索引按对象投影摘要，不把其他对象行或更新时间直接归为冲突；真实语义字段变化仍拒绝。评审依赖收集覆盖execution_validation的注册表单对象条目、目标目录文档和规范读集，另保留该操作全部写集与父需求主文档/trace；目标CHANGELOG按对象行投影。非评审动作保持原证明分支，能力矩阵逐项回归；未知读取或无法规范化的依赖保守返回dependency_unknown，不使用文件目录外即无关的判断。

旧证明只有全局摘要时，仅在原baseline/result可完整重建且身份、同步事件、历史摘要匹配后派生依赖集合；缺失时proof_missing/unsupported_proof，不补造证明。当前相关依赖变化返回dependency_conflict，不否定已证实的历史完成，不覆盖新成果。单独删除hash比较或仅凭approved/applied放行均不采用。

### 2. 持久交接与并发保护

以project+operation+application+guard_generation为交接唯一键。应用verified持久化时原子登记待核对工作；若文件证明与DB无法同事务，先保存可恢复意图，再持久化证明，最后确认完成；启动扫描可从verified应用重建缺失交接，但必须重新验身份及证据。新增governance_completion_handoffs兼容交接表，由chat schema重复安全建表；应用verified作为可重建的持久意图，同事务登记队列，控制器补建缺失交接。

状态pending -> checking -> confirmed或blocked；保存attempt_count、next_attempt_at、last_checked_at、reason_code与证据版本。工作线程租约和CAS防止多进程重复确认。执行结束且历史证明可信、当前准入检查通过后，按守卫generation原子确认；新执行/版本变化使旧回调no-op并记录stale_operation。响应丢失重试返回同一结果。不得重复模型调用、应用、迁移或改写原failed/stopped/completed。

### 3. 收敛时限与预算

以下为新设计验收目标，不是现网SLA：正常交接即时入队；调度扫描周期不超过10秒；服务健康且无冲突时60秒内完成保护收敛。瞬态故障最多3次自动尝试，间隔5/15/30秒，预算和下一时间持久化，重启不重置；超过预算进入blocked并返回retry_exhausted。确定性权限/身份/依赖冲突立即blocked。启动后60秒内扫描并调度遗留未收敛记录；服务停机时不承诺墙钟收敛，展示最后核验时间。手动核验只重新核对原操作，鉴权、同键去重且不能清空审计；输入版本未变的确定性失败不创建无限重试。每次状态/原因变化最多通知一次。

### 4. 统一契约与展示边界

读取与准入统一使用同一核验服务。响应提供business_stage、execution_terminal、historical_result、admission_state、reason_code、last_checked_at、retry信息、operation引用和allowed_actions；已在API schema固定historical_result、admission_state/admission_reason、verification_reason、last_checked_at、verification_actions、verification_differences（脱敏类别与新增/删除/修改计数）；卡片沿用stage、execution_state、can_send和execution_reason。原因至少区分proof_missing、proof_invalid、dependency_conflict、dependency_unknown、permission_denied、active_execution、stale_operation、retry_exhausted、temporarily_unavailable。

reader保留可信生命周期，异常作为独立叠加；后续发送在事务内再次校验准入，前端展示不能授权。旧operation_id保护进入该服务，不直接跳过也不无条件释放。REQ-0046消费此契约实现Chat/卡片/详情同源说明与入口；本Change不改视觉原型。未支持动作明确unsupported，不假定opsx-archive证明结构与评审相同。

## 测试策略

AC-001/002：无页面访问、提交窗口故障、重启及CAS竞争；AC-003/004：无关文件/共享索引其他条目变化实际放行，目标语义和必要依赖变化拒绝。AC-005—008：重复请求、响应丢失、撤权、跨项目、缺损/篡改、迟到回调及原终态保留。AC-009：假时钟与真实工作线程证明60秒目标、3次预算、重启预算和通知去重。AC-010：后端契约加REQ-0046真实双视口视觉证据，不能用Mock关闭。AC-011：原现场正式核验及安全拒绝/收敛结论单独记录。AC-012：source req-review/bug-review、共享入口能力矩阵及opsx-archive独立分支回归。

采用治理恢复与归档验收证据分层实践：合成、真实首次成功、历史恢复、部署指纹、UI证据分别签认，共享治理写入串行。所有产品证据仍待实施；局部UI依赖仅阻断对应AC，不阻断后端实现。

## 迁移、风险与回滚

证明追加版本兼容旧读者；先迁移再部署生产者与补偿消费者，SQLite/MySQL验证唯一键、事务、租约和重启行为。依赖漏记导致误放行风险以读集完整性、负向样本和未知拒绝控制；过宽依赖导致假冲突通过对象条目规范化验证。启动扫描分页并限流，避免全量快照风暴；预算耗尽可诊断不无限调度。回滚先停止新调度，保留交接与证明数据，旧版本不能理解时保持安全阻断，不清库解锁。

## 产品数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: API、DB、request_logs、task_traces、task_trace_spans、execution_guard、governance_proof及Web契约。validation: 请求关联原operation/run/application；后台补偿不伪造usage_events，字段脱敏不含文档原文/本机路径/凭证，权限不变。同步API索引、OpenAPI/Orval生成物、DB设计与迁移、部署启动补偿和保留周期；行为ID透传由REQ-0046入口承接并联合验证。当前文档生成无运行态数据写入。

## 跨入口一致性返修约定

卡片只呈现一次当前动作的阻塞摘要，历史成果、核验时间、重新核验、差异和原执行收进默认折叠的“状态详情”。运行详情仍归属于原Chat轮次。归档准入采用当前Change的结构化验收证据和明确人工签认，与CLI共用只读判定；进度统计按AC身份去重，自动通过不等于用户人工签认。旧评审历史保留，经过验证的后续合法流转可承接旧保护，真实冲突、未知占用、权限变化、缺失或过期证据仍阻断。覆盖REQ与BUG，不能按具体编号特判。

实现将验收readiness、指纹与证据匹配抽入src/backend/app/governance/acceptance_evidence.py；archive_admission.py供产品与CLI复用，不执行计划命令。review_successor.py核对历史证明、未改变的评审决定和规范、合法Sprint/Change关联及当前完成证据，并CAS提升保护版本，保留原操作身份。后续实质文档变化必须被当前验收输入覆盖。

## 真实归档补证发现

首个 REQ 临时归档样本未执行归档，保留为负例：产品准备入口已允许，但执行器 `_archive_ready` 遗漏 `req_id`，退回治理写权限，归档目录不可写。已复用严格别名解析，同时拒绝冲突别名；新增八种 REQ/BUG 字段别名测试。临时样本缺少交付验证引用也被发现，产品动作准备和 CLI 包装脚本现在均提前执行交付证据校验，避免模型执行后才发现已知缺口。

对于可信命令记录明确证明已结束且零治理写入的归档尝试，后续补齐材料可在当前关联、阶段、交付证据和验收结果重新核验后解除重试保护。保留原轮次终态与零写入记录，以版本比较更新守卫；没有零写入证明、当前证据失效或仍在运行时不解除。此分支不把原失败/未执行样本改写为成功。

真实样本授权：REQ 与 BUG 各一次，首个 REQ 未归档；用户另授权仅一次 REQ 补跑。成功结论等待实际归档、同步、Issue 迁移及守卫核验；模型 completed 不作为成功依据。


## 部署投影根与源码根的一致性补证

最终本地 Docker 看板发现 CLI ready、产品 0/15。实测两个入口读取同一验收 manifest 且附件哈希一致，但治理投影没有 src/ 与 scripts/，20 个源码输入被作为 missing；已配置的 source_root 则具备这些文件。此为证据读取边界错误，不是验收结果失败。

修复只使用既有受信任 source_root 读取 src/、scripts/ 的指纹输入；Issue、规则、验收计划、manifest 和证据附件仍从治理根读取，治理文档缺失或变化不能回退到源码副本。没有执行计划中的代码，不扩大挂载或权限。未配置源码根仍按原根读取，缺失源码、源码变化、治理变化和治理删除均拒绝；同根与双根部署均纳入回归。卡片、归档准备、旧评审承接及零写入重试全部传递同一源码根。

真实模型归档样本使用同根隔离环境；本项双根部署由最终本地产品读取、源码哈希及合成正反例补充验证，不冒称再次运行模型。REQ 主文档/流程/故事/原型既有“当前证据与 CLI 一致”规则不变，本次属于内部证据读取修正，无需追加产品交互；文档差异记录在本台账和设计中。


## 正式入口关联与后续评审补证

最终正式入口发现 REQ 的 trace 使用 related_change，openspec_changes 为空；原解析遗漏该形式，错误退回 Markdown 13/31，而共享当前证据实际为 31/31。统一关联解析支持 related_change、related_changes、openspec_changes 的字符串与 change_id 对象；需求卡片、后续评审承接及零写入重试共用解析。不是手工补某张卡片关联。

原产品评审证明之后，正式 REQ 已追加获授权的补充范围复核，仍为 approved。旧逻辑按字节拒绝全部 review.md 变化，不能承接合法后续复核。现只在验收阶段、原评审和当前评审均 approved 且身份一致、完整当前 review.md 被当前有效验收输入覆盖时承接；未覆盖、证据过期、结论改为 rejected、规则变化及运行中仍拒绝。原操作终态与历史评审证明不改写。相关正反例同时覆盖 REQ/BUG 和四种关联表示。

真实模型归档仍仅为此前授权的两个成功隔离样本；本次收尾以当前回归和正式入口准备/读取补证，不额外调用模型、不归档正式对象。

## 归档预演结果契约补充
预演同时检查进程、失败输出、目录迁移、完整归档内容和增量规格实际效果；退出码 0 不单独证明成功。详见 acceptance-fixes.md。

## 验收输入跨环境契约
可信源码补读范围为 src/scripts/tests；治理文档不跨根回退。目录输入确定性包含成员路径、类型、内容与空目录，拒绝符号链接和特殊文件。最终核验部署后产品发送准入。

## 发送快照竞争处理

命令持久化前，瞬时治理快照竞争最多执行三次完整预检，重新授权并校验当前验收。持续不一致与持续更新分别提示；其他门禁失败不可重试放行。准备成功不等于发送成功，实际 turns 入队及幂等回放为验收证据。

## 归档基线连续证明

共享只读 archive_recovery 判定核对 before/after 全树哈希、唯一已归档目录、完成态、增量效果与不相交的 capability；新记录另绑定 delta 哈希。未知改动、缺边、规格重叠、重复目录、未完成归档、符号链接、错误结果和并发输入变化继续拒绝。显式 reprepare 仅承接 baseline 路径，保留 previous_record 与 baseline_transition；已经合并后的路径只允许 move-only/archived 恢复，不能重置为 merge。产品、CLI、归档终态漂移检测共用事实判定，读取不写 journal 或执行仓库脚本。

## 交付输入与验收输出边界

schema v4 将交付输入指纹与完整复制指纹分开。仅排除 evidence/acceptance/ 生成目录和 trace.md 的正文、updated_at；trace 的身份、状态、首次执行事实、其他未知文件、验收计划、任务、规格和其他证据继续受保护。符号链接即使位于派生目录也拒绝。验收附件完整性和输入有效性继续由验收门禁独立核对。旧记录仅在证明自身尚未合并的显式迁移中更新，保留 previous_record；已合并、并发变化、未知规格漂移不得借迁移绕过。

验收报告发布后返回独立 archive_ready 与完整准入结果；收尾同步和用量完成后再执行 --archive-readiness，共用产品与 CLI 的正式准入。验收 passed 不再单独代表可以归档。错误区分交付输入变化、旧记录过期、身份冲突、规格基线缺证和记录损坏。

执行边界补充：若只读准入证明 merge 基线存在独立归档链，实际归档分类器须在自身合并前刷新 expected_spec_hash，保留历史且通过输入竞争检查；避免把 S+A+B 与旧 S+B 预期比较。move-only/archived 不执行此迁移。

联合归档证据定位：关联 Change 先归档时，原 evidence 引用可按唯一完成的归档身份读取；保持原路径身份与内容哈希，不通过路径迁移豁免证据内容变化或验收输入过期。

## 跨日归档恢复
准备日期与实际迁移日期分离。迁移后的准入使用唯一归档计划与保留的自动验收证据，校验完整覆盖及附件哈希，不回退人工勾选。只在规格和交付输入证明通过后记录实际日期；重复恢复只执行尚未完成的收尾。

规格完成证明兼容 OpenSpec 对代码块外重复空行的规范化；不忽略正文或代码示例变化，重复 Requirement 标题拒绝。共享证据定位也用于跨链路验收前置检查。
