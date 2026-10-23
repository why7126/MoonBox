---
bug_id: BUG-0052-verified-result-execution-guard-not-released
title: 成果核验完成与执行保护未收敛根因分析
created_at: '2026-10-20 09:00:22'
updated_at: 2026-10-20 22:45:30
status: confirmed
---

# 成果核验完成与执行保护未收敛根因分析

## 根因状态

status: confirmed

此 status 仅表示根因确认程度，不表示 BUG 生命周期；当前缺陷状态以 trace.md 为准。

确认范围：当前持续阻塞机制及必要触发条件；不是首次错过确认窗口的完整历史重演。证据承接同会话 2026-10-20 bug-explore 及 bug.md，本次补齐文档不重复执行评审或恢复。

## 现象

原评审已 completed，应用 applied/verified，业务操作 completed/complete，REQ 文档与注册表 approved；执行保护仍 needs_review/result_unverified，result_revision 为空，旧 confirmed_stage=review-ready。看板覆盖为待评审且阻断加入迭代，Chat 业务面板已完成。

## 证据链

编号与 bug.md 一致，详见其“可复核证据”及只读复核步骤；不保存私有原始记录、数据库副本或本机路径。

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | screenshot | 用户附件与 Chrome 本地 /requirements；bug.md E1 | 已评审文档对应卡片显示待评审、结果待核对，加入迭代禁用 | 产品现象真实存在 |
| E2 | data_sample | canonical SQLite 原对象/轮次关联只读查询；bug.md E2 | 保护 needs_review、执行 completed、应用 applied/verified | 执行、应用与保护未收敛 |
| E3 | data_sample | backend 私有 operation 白名单字段；bug.md E3 | 轮次 operation 存在，10 个步骤 sync_succeeded=false；应用 workflow_sync 存在，req.review/对象匹配 | 需走应用证明回退，排除证明缺失 |
| E4 | reproduction | baseline.files 合并 result.after 的内存重建；bug.md E4 | 历史摘要与 proof 匹配，历史业务校验 true | 证明能证明原评审成果 |
| E5 | data_sample | 同容器 stable 快照与 validate_result；bug.md E5 | 当前业务校验 true，proof 与当前摘要不同；采样 184 项变化，目标目录外 175 项 | 当前核对被摘要条件阻断，非现有业务校验失败 |
| E6 | reproduction | 历史字典仅在内存加入无关 docs 文件；bug.md E6 | business_valid=true、hash_changed=true | 无关变更足以使全局摘要条件失败 |
| E7 | data_sample | 保护、应用与业务操作时间字段；bug.md E7 | 2026-10-19 19:33:44 保护待核对，19:33:50 应用核验及业务操作完成，保护后续仍未解除 | 完成与保护确认分离 |
| E8 | config_diff | 运行 backend 与工作区七份模块 SHA-256 对比；bug.md E8 | execution_context、execution_guard、reader、preparation、recovery_service、snapshot、execution_validation 逐项一致 | 本次分析对应当前部署路径 |
| E9 | code_path | src/backend/app/governance/execution_context.py：reconcile/reconcile_external；snapshot.py：ROOTS/digest；reader.py：_call | 全局摘要不符则 continue；旧保护阻断外部同步；confirmed_stage 覆盖卡片 | 构成持续阻塞与错误展示链路 |
| E10 | code_path | preparation.py：collect；recovery_service.py：checkpoint；execution_guard.py：terminal/confirm | source 完成更新应用/操作；保护确认另由读取/准入核对调用 | 缺少可靠完成交接及补偿闭环 |

## 已排除假设

| 假设 | 排除或限制依据 |
|---|---|
| 原评审未结束或应用尚未完成 | E2、E7：对应执行 completed、应用 verified、业务操作 complete |
| 应用完成证明丢失 | E3、E4：证明存在且匹配历史成果 |
| 当前需求未通过现有业务结构校验 | E5：validate_result=true；不等于可绕过并发安全检查 |
| 只是前端旧缓存 | E1、E2、E9：后端保护真实滞留并主动覆盖阶段 |
| 分析代码与运行版本不同 | E8 七份相关模块一致；不扩张为所有部署资产一致 |
| 一定是今天文档修改导致首次故障 | 未证实；现场无法确定第一次错过确认的文件/请求/调度顺序 |

## 已确认根因

RC-1：完成证明的 source_hash 与当前整个 issues/iterations/openspec/docs/rules 快照强耦合。reconcile 读取已核验应用证明后仍要求 source_hash==snapshot.revision；不符直接跳过 guards.confirm，历史证明没有安全重新核验路径。无关文件也进入摘要，E6 独立验证触发条件。

RC-2：source 应用核验、业务操作完成与保护确认不是可靠闭环。terminal 先留下 needs_review，collect/checkpoint 完成后未同步确认保护；后续读取或准入核对必须恰好满足旧全局指纹。后续变更使该条件持续不成立。

RC-3：reconcile_external 避让带 operation_id 的旧保护，无法补偿；reader 再用旧阶段覆盖生命周期。req-review 失配分支不细化原因，长期只显示 result_unverified。

因果链：完成留待保护核对 → 后续全局快照变化 → 历史证明不匹配当前摘要 → 跳过确认 → 外部同步避让 → 旧阶段覆盖且后续准入阻断。

## 不确定性与影响边界

首次未确认的具体触发时序未知，不影响当前持续阻塞机制确认。175 项目录外变化不能一概认定语义无关；真正无关修改的充分触发性由 E6 支持。已确认 source req-review 样本；其他命令需按共享路径及完成语义回归。opsx-archive 已有独立证明路径，不直接套用本例结论。

## 修复方向

1. 应用核验与保护确认建立持久、幂等交接及补偿，覆盖重启、响应丢失与提交窗口，不依赖页面访问时机。
2. 分离历史完成证明与当前准入；以操作对象、轮次、应用、成果及必要依赖界定证明范围，保留当前版本和并发围栏。不简单删除全局比较后无条件确认。
3. 对完整历史证明提供安全重核验；不重复模型调用、成果应用或迁移，不覆盖新操作，不伪造原失败/停止为首次成功。
4. 返回结构化失败原因、最近核验事实与合法动作；有界检测已完成但保护未解除、无活动执行却持续占用，避免无限重试。
5. 后端分离可信生命周期与准入投影；REQ-0046 消费统一结果，承接展示、状态说明、核验入口。不能凭 approved/applied 单字段解锁。

## 验证闭环

已完成：运行态记录、证明重建、业务校验、代码分支及纯内存触发验证。待修复后：acceptance.md AC-001—012 的自动化与真实运行证据。根因 confirmed 不等同修复成功；本次未执行端到端故障注入、恢复或 UI 产品验收。复核时按 bug.md 步骤只读关联原样本，不重放真实评审。


## 联合验收补充根因与修复

当前版本联合样本补充确认：已 validated/recovered_valid 的评审守卫若被外部快照变化直接清为 idle，会丢失原操作身份；正式重新核验若只处理 needs_review，又无法对已完成操作的相关依赖变化重新评估准入。修复在 external reconcile 保留评审原身份，正式 verify 在项目锁内按原 operation/version 执行 CAS 重新核验；历史完成证明和当前准入分别表达，不重放模型、不重复应用。

当前后端 REQ-9096 与 BUG-9097 真实成功样本均为1轮、1应用，handoff confirmed且guard validated；相关文件改变后保护生效，恢复文件后由产品核验恢复准入，次数不变。证据位于关联Change的 `evidence/live-req46-joint-verification.json` 与 REQ Change 的 `evidence/final-restored.json`。BUG-9096 的 `review_result` 字段被既有评审 schema 拒绝，是独立负向样本，不伪装为本缺陷正常完成证明。

## 跨入口一致性返修约定

卡片只呈现一次当前动作的阻塞摘要，历史成果、核验时间、重新核验、差异和原执行收进默认折叠的“状态详情”。运行详情仍归属于原Chat轮次。归档准入采用当前Change的结构化验收证据和明确人工签认，与CLI共用只读判定；进度统计按AC身份去重，自动通过不等于用户人工签认。旧评审历史保留，经过验证的后续合法流转可承接旧保护，真实冲突、未知占用、权限变化、缺失或过期证据仍阻断。覆盖REQ与BUG，不能按具体编号特判。

补充确认：旧评审依赖对象文档的逐字节比较仍阻断后续合法阶段；原预演只校验规格合并，不能替代产品准入。当前返修采用受验证的后续事实承接，禁止直接清空守卫。

## 真实归档补证发现

首个 REQ 临时归档样本未执行归档，保留为负例：产品准备入口已允许，但执行器 `_archive_ready` 遗漏 `req_id`，退回治理写权限，归档目录不可写。已复用严格别名解析，同时拒绝冲突别名；新增八种 REQ/BUG 字段别名测试。临时样本缺少交付验证引用也被发现，产品动作准备和 CLI 包装脚本现在均提前执行交付证据校验，避免模型执行后才发现已知缺口。

对于可信命令记录明确证明已结束且零治理写入的归档尝试，后续补齐材料可在当前关联、阶段、交付证据和验收结果重新核验后解除重试保护。保留原轮次终态与零写入记录，以版本比较更新守卫；没有零写入证明、当前证据失效或仍在运行时不解除。此分支不把原失败/未执行样本改写为成功。

真实样本授权：REQ 与 BUG 各一次，首个 REQ 未归档；用户另授权仅一次 REQ 补跑。成功结论等待实际归档、同步、Issue 迁移及守卫核验；模型 completed 不作为成功依据。


## 部署投影根与源码根的一致性补证

最终本地 Docker 看板发现 CLI ready、产品 0/15。实测两个入口读取同一验收 manifest 且附件哈希一致，但治理投影没有 src/ 与 scripts/，20 个源码输入被作为 missing；已配置的 source_root 则具备这些文件。此为证据读取边界错误，不是验收结果失败。

修复只使用既有受信任 source_root 读取 src/、scripts/ 的指纹输入；Issue、规则、验收计划、manifest 和证据附件仍从治理根读取，治理文档缺失或变化不能回退到源码副本。没有执行计划中的代码，不扩大挂载或权限。未配置源码根仍按原根读取，缺失源码、源码变化、治理变化和治理删除均拒绝；同根与双根部署均纳入回归。卡片、归档准备、旧评审承接及零写入重试全部传递同一源码根。

真实模型归档样本使用同根隔离环境；本项双根部署由最终本地产品读取、源码哈希及合成正反例补充验证，不冒称再次运行模型。REQ 主文档/流程/故事/原型既有“当前证据与 CLI 一致”规则不变，本次属于内部证据读取修正，无需追加产品交互；文档差异记录在本台账和设计中。

部署投影补证入口：[治理根缺失源码输入的哈希比对](../../../../openspec/archive/2026-10-21-fix-verified-result-execution-guard-convergence/evidence/projection-source-mismatch.json)。

后续补充评审仍为 approved 且对象身份一致时，只有完整评审文件被当前有效验收证据覆盖，才能承接旧评审保护；结论拒绝、未覆盖或过期仍阻断。关联解析统一支持 related_change、related_changes 与 openspec_changes 的字符串/对象形式。

## 历史归档基线返修确认

旧 archive-recovery 仅比较 baseline/expected 全树哈希，不识别独立归档造成的合法变化；产品归档准入未检查这份恢复记录。已核验四条归档 journal 构成旧基线到当前规格的连续边且无本链路规格重叠。修复保留整树哈希要求，通过可验证的归档连续证明承接，不直接重置 baseline；具体证据与失败用例见关联 Change acceptance-fixes.md。

## 验收后归档衔接补充

再次验收产生的报告与 trace 运行正文属于派生输出，不得使归档恢复记录自失效；交付输入、链路身份、真实证据完整性及并发变化仍受门禁保护。验收收尾后必须通过产品与 CLI 共用的正式准入，验收 passed 不等于归档 ready。错误须区分交付输入变化、旧记录过期、规格基线缺证、身份冲突和记录损坏。

关联链路先归档后，验收证据按唯一已完成归档身份定位，继续核对原内容哈希；活动目录仍存在、归档身份歧义、未完成或证据被篡改时仍阻断。

跨日归档补充：确认准备日期与实际目录日期耦合、迁移后自动验收计划仅查活动目录导致人工统计回退。由原 BUG 链路修复，验收覆盖跨日、中断重试、重复恢复及证据篡改拒绝；正式 REQ 收尾不得重复合并规格。
