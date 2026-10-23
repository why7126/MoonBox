---
bug_id: BUG-0060-direct-command-completion-proof-drift
title: 直接治理命令完成证明失效根因分析
created_at: '2026-10-21 11:28:50'
updated_at: '2026-10-21 11:28:50'
root_cause_status: confirmed
---

# 直接治理命令完成证明失效根因分析

## 根因状态

root_cause_status: confirmed

确认范围：全局指纹耦合、同步/收尾证明断裂及原执行保护不收敛的机制。历史两次摘要跳变的逐文件归因仍未确认；不将“当前业务结构有效”作为解除现场保护的充分条件。

## 现象

BUG-0055 的 bug-opsx 已创建 fix-chat-turn-message-order，Workflow Sync 成功且轮次 completed；产品卡片仍滞留迭代规划，提示结果待核对，开始修复禁用，刷新不恢复。文档投影应为 ready-dev，却被执行保护覆盖回 sprint-planning。

严重度 high：已生成成果不能进入下一动作，且对话成功提示与业务结果不一致，容易诱导重复执行。没有数据丢失证据。不把 BUG-0055 消息排序实现混入本缺陷；关联 BUG-0052-verified-result-execution-guard-not-released 的完成保护机制。

## 证据链

| ID | 类型 | 来源 | 脱敏事实与判断 |
|---|---|---|---|
| E1 | screenshot | 用户附件 2df3937f、fd432dc6 及上一轮浏览器只读观察 | Chat 已完成，BUG-0055 留在迭代规划，按钮禁用 |
| E2 | data_sample | 部署数据库只读查询摘要，capture.md | completed；guard needs_review；reason result_unverified；confirmed_stage sprint-planning |
| E3 | data_sample | direct-command journal 与工具事件关联 | 28 个边界，1 次正式同步成功；最终 sync_incomplete，无 candidate/application 替代证明 |
| E4 | code_path | src/backend/app/governance/snapshot.py：ROOTS、digest | 对 issues、iterations、openspec、docs、rules 中纳入的文件名及内容摘要计算整树指纹 |
| E5 | code_path | direct_command_journal.py：observe、terminal；execution_context.py：reconcile | 同步步骤和当前摘要相等才可继续确认；--check/--dry-run 不算正式同步成功 |
| E6 | code_path | reader.py：_call；execution_context.py：reconcile_external | 保护覆盖业务阶段，外部投影不能越过原执行保护 |
| E7 | data_sample | 原轮事件150、218—226 | 09:22:42 正式同步成功，后续摘要从 8316694e27a1 经 a03270b25664 变为 0726bc554bcd；无第二次正式同步证明 |
| E8 | data_sample | 事件225/226 的操作摘要 | 对 sprint-011/sprint.md 与 Change trace.md 执行 write_text，随后仅 --check；写回前后总摘要相同，不能将此操作认定为摘要变化原因 |
| E9 | data_sample | BUG-0057 trace 记录及子文档元数据 | 09:22:50 补齐文档，处于本轮同步后窗口；acceptance/root-cause/workaround 等文件创建时间与之相符，是无关对象并发线索 |
| E10 | data_sample | 原轮私有存储只读检查 | baseline 有4353项文件；result 不存在；同步步骤只有摘要，缺同步时逐文件结果 |
| E11 | reproduction | 同会话只读探索中的内存实验 | 原执行前基线中，仅给 BUG-0057 trace 增加换行，digest 就改变；未写文件或数据库，证明无关变化也影响全局摘要 |
| E12 | data_sample | 同会话当前快照只读校验 | validate_result 对 BUG-0055/bug-opsx 为 True；不叠加保护时 ready-dev。只证明当时结构有效，不替代完整安全恢复依据 |
| E13 | data_sample | 执行前基线与探索时当前快照比较 | 38个路径差异，包含后续 BUG-0060 创建、BUG-0046 评审及 BUG-0057 更新；不是同步到收尾的精确差异 |

E1 原始附件保留在对话，不复制聊天正文。E2—E13 为此前同会话已完成的只读/内存取证，本次复用；不声称本轮重跑产品或重新确认最新运行态。路径、角色、摘要和时间均为脱敏事实。

## 已确认根因

root_cause_status: confirmed，限于全局指纹耦合、证明留存不足以及保护不收敛的机制；本次新增结论承接 capture 中 probable 的历史文件归属判断，并未把逐文件归属升级为 confirmed。

- 同步成功证明绑定五个治理目录的完整内容摘要；任何被纳入文件的字节变化都可能失效，不限当前对象。
- 收尾及 reconcile 要求成功同步步骤摘要与终态/当前摘要匹配；本例不匹配，留下 sync_incomplete 与 needs_review。
- 卡片按旧 confirmed_stage 展示；reconcile_external 对仍有运行身份且 needs_review 的保护返回，不会仅凭当前文档结构正确自动清除。因此刷新重复相同判定。
- 工具边界只记录总摘要，没有同步成功时逐文件清单或结果快照，无法解释具体差异，也无法安全认定全部变化无关。
- 既有评审/归档专用证明不等于所有直接命令均有同等覆盖；修复须建立动作分类验证，不能统一无条件放行。

## 历史归因缺口

| 类别 | 具体路径/变化 | 证据强度与处理 |
|---|---|---|
| 当前命令文档收尾 | iterations/change/sprint-011/sprint.md；openspec/changes/fix-chat-turn-message-order/trace.md 的创建状态和验证说明写回 | 已确认操作；该边界摘要相同，可能为无效替换，不认定是失效来源 |
| 无关对象并发 | issues/bugs/plan/BUG-0057-requirement-card-chat-navigation-latency/ 下 acceptance.md、root-cause.md、workaround.md 创建及其他子文档更新 | 文档记录在时间窗口内；缺同步时快照，无法将具体文件逐一归因到某次摘要跳变 |
| 更晚变化 | BUG-0060 文档、BUG-0046 评审迁移等 | 已包含在执行前到当前差异中；不能解释原始收尾失效，不混入历史因果 |
| 真实交付冲突 | 本例未发现当前结构性冲突 | 当前结构有效不足以排除全部历史相关输入变化；禁止据此直接解除保护 |

总哈希不可逆，缺失的历史逐文件状态不能从当前文件还原。此前工具边界观察到摘要变化不证明该校验工具是写入者；并发任务同样可能造成变化。后续若有可用历史文件清单再补齐，不伪造完整差异。隔离回归可证明机制和修复行为，不能代替历史归因。

历史缺口不阻止评审已确认的机制缺陷，但限制对原现场执行安全恢复：不能靠假定所有变化无关来放行。继续补证优先查可用历史文件清单与写入记录；没有原始快照时明确不可还原，不用当前差异或隔离实验冒充历史事实。

## 已排除假设

| 假设 | 排除依据与边界 |
|---|---|
| 没有创建 Change | 原 Change proposed、文档存在且不叠加保护时 ready-dev |
| 完全没有执行正式同步 | E3/E7 已记录1次正式同步成功 |
| 只是前端缓存 | E2/E6 后端保护仍 needs_review，刷新重复同一判定 |
| 最后的两文件写回必然造成摘要变化 | E8 该工具前后摘要相同，不能这样归因 |
| 当前38个差异路径均导致原始失败 | E13 包含后来变更，不是同步到收尾差异 |
| 当前业务校验通过就能直接解锁 | E12 仅结构性验证，未证明原执行身份、权限、依赖、版本围栏均有效 |

## 修复方向

1. 每类直接命令声明动作身份、对象、操作版本、输入依赖、预期输出与业务验证器。保存同步和最终签认的逐文件哈希清单及必要字段投影，供差异分类；最小化保存敏感内容。
2. 对共享注册表、Sprint 文档按当前对象条目/依赖验证，避免无关条目使证明失效；同时保留唯一性、引用完整性和容量等适用全局约束。不是简单忽略整个共享文件。
3. 分离交付输入、派生说明和无关内容。仅经过明确策略及业务校验的说明回填可重新签认；任务、规格、身份、状态、验收要求等实质变化仍按相关冲突处理。
4. 完成最后文档回填后统一执行最终核验与证明签认，持久交接到保护确认；签认与释放之间复读相关指纹并用版本围栏防竞态。崩溃后可从持久证明恢复，不重做业务写入。
5. --check 保持只读检查语义，退出0不等于已生成新的正式同步证明。模型声明、单个命令退出0、静态 ready 均不能单独放行。
6. 建立支持动作矩阵：req/bug generate、complete、review、opsx，sprint-propose，opsx apply/modify/archive；逐类保留自己的门禁和输出要求，复用已有可靠证明而非覆盖已有归档/评审保护。

## 安全恢复边界

区分运行结束和业务确认。原因至少区分证明缺失/损坏、同步后相关变化、无关变化待重核、结构校验失败、权限或绑定变化、暂不可用和新执行占用；提供核验时间、脱敏差异类别和原执行入口，不继续只显示结果待核对。

恢复前验证原执行终态、操作与对象身份、权限/绑定、当前相关交付及同步一致性，确认没有更新运行占用；相关哈希复读稳定后按 operation/version 条件更新保护和投影。重复恢复幂等，延迟回调不能释放新保护。

历史证据不足时明确“需重建核验依据”，以受控流程重新验证当前成果并签发可追溯的新核验记录，保留旧记录，不伪造原同步结果。无法满足门禁则继续阻断并说明缺口。具体恢复实现须经后续 Change 与验收，不在本轮解除现场。

不重放 bug-opsx、不重复创建 Change、不手改数据库、不直接改卡片阶段、不绕过权限或冲突门禁。BUG-0055 现场是兼容恢复样本，不能成为硬编码特例。

## 验证闭环

已有产品截图、数据库终态、journal、工具边界、当前结构校验和内存实验共同解释机制；内存实验只验证无关文件也参与全局摘要，不证明历史具体写入者。证据复用自同会话只读探索，未重放原命令。

实现后按 [验收标准](acceptance.md) 完成正反例、支持动作矩阵和部署全链路；当前均未执行。缺证据继续阻断、安全核验恢复和当前相关冲突是三个不同结果，不用“全部拒绝”冒充修复。

