---
bug_id: BUG-0060-direct-command-completion-proof-drift
title: Chat 治理命令同步后完成证明失效导致卡片滞留旧阶段
status: done
created_at: '2026-10-21 09:39:21'
updated_at: 2026-10-21 14:09:29
severity: high
environment: local docker chat-platform
related_requirement: null
related_bug: BUG-0052-verified-result-execution-guard-not-released
---

# Chat 治理命令同步后完成证明失效导致卡片滞留旧阶段

## 现象

用户在 Chat 执行 BUG-0055 的 bug-opsx，助手宣布创建 Change 并同步完成，轮次为 completed，但卡片仍在迭代规划，提示“结果待核对”，开始修复不可用；刷新未解除。用户授权独立记录并补查文件变化，不仅修当前卡片。

## 复现与期望

1. 从已纳入 Sprint 的 Issue 执行 req-opsx 或 bug-opsx。
2. 完成正式 Workflow Sync 后继续文档收尾，或其他治理内容发生变化，再结束轮次。
3. 核对同步证明的快照、终态快照和当前快照，以及卡片阶段与执行保护。

期望：相关交付仍有效时安全确认并流转；相关输入冲突时保留保护并给出具体原因、差异和核验入口。实际原始样本的文档投影为 ready-dev，却因 needs_review 保护回退到 sprint-planning；Chat 仅显示已完成，未明确业务核验未收敛。扩展命令场景尚待验证。

## 已有证据

| ID | 类型 | 来源 | 脱敏事实 |
|---|---|---|---|
| E1 | screenshot | 用户两张附件及同会话浏览器只读观察 | 对话完成；BUG-0055 卡片仍在迭代规划，按钮因结果待核对禁用 |
| E2 | data_sample | 部署数据库只读查询 | action=bug-opsx；turn=completed；guard=needs_review，reason=result_unverified，confirmed_stage=sprint-planning |
| E3 | data_sample | 原轮次 direct-command journal | 28 个工具边界记录，1 次 sync_succeeded=true；收尾 classification=sync_incomplete；同步成功指纹不等于终态或当前指纹；无 candidate/application 替代证明 |
| E4 | code_path | execution_context.py：reconcile；reader.py：_call | 直接命令要求同步成功步骤 source_revision 等于当前全局快照；不满足则不确认，卡片保持旧 confirmed_stage |
| E5 | code_path | direct_command_journal.py：observe、terminal、is_formal_workflow_sync | 步骤只保存总摘要，无逐文件清单；--check/--dry-run 不计作正式同步成功 |
| E6 | data_sample | 原轮工具事件 seq=150、151/152、218—226 与 journal 关联只读补查 | seq150 正式同步退出0；其后指纹从 8316694e27a1 经 a03270b25664 变为 0726bc554bcd；后续只记录检查，没有第二次正式同步证明 |
| E7 | data_sample | seq225/226 工具参数的脱敏操作摘要 | 对 iterations/change/sprint-011/sprint.md 和 openspec/changes/fix-chat-turn-message-order/trace.md 执行 write_text，回填创建状态及验证说明；随后 sync-workflow-status.py --event bug.opsx 带 --check；整体命令退出0 |

用户附件名：codex-clipboard-2df3937f-c537-4972-a2c0-b30e3973c2a3.png、codex-clipboard-fd432dc6-dc19-40a4-82e1-2a73694a756b.png，保留在对话，不复制原始聊天正文入仓库。

## 根因判断及补证边界

已确认阻断机制：同步确实成功过，但完成证明绑定全局快照；同步后摘要改变，收尾判为 sync_incomplete，保护未解除；刷新沿用同一判定。因此不是缺少 Change，也不是简单前端缓存。

已定位后续写回目标文件，但不能声称它们就是导致摘要变化的文件：seq225 started 与 seq226 completed 摘要一致，变更可能是无效替换或目标内容此前已存在。两次摘要变化出现在此前工具边界，相关工具为校验命令；仅凭边界无法区分校验副作用与并发写入。记录未保留同步时逐文件快照，不能从总哈希反推出完整差异。根因完整归属暂为 probable；不将所有变化判为无关或直接批准解除保护。

待补查：围绕首次不匹配边界，关联可用历史快照、文件级哈希、工具事件及并发写入来源，输出路径、变化类型、与当前动作关系及证据强度。若历史快照不足，在隔离样本记录逐文件清单并复现“同步后回填”和“其他对象并发变更”，不伪造历史差异。--check 不应被直接当作正式写入成功证明。

## 影响与严重度

初判 high：已生成成果不能进入后续修复，容易诱导重复执行；当前未证明数据丢失。涉及直接治理命令共用完成判定、终态投影及安全恢复，不限 BUG-0055、bug-opsx 或单一会话。

## 通用修复范围与建议验收

- 区分动作相关交付输入、派生输出及无关对象变化；明确证明覆盖范围，相关冲突继续拒绝，不能删除全部指纹检查或仅依据模型文字/退出码放行。
- 统一直接命令的正式同步、最终文档收尾、证明签认、产品与 CLI 准入；覆盖 req/bug generate、complete、review、opsx，sprint-propose 和 opsx apply/modify/archive 等支持路径，逐类明确适用验证器，不宣称当前每类均已复现。
- Chat 运行结束与业务交付确认分开说明；卡片阻断显示可定位原因、核验时间、差异范围与安全恢复入口；校验失败、缺证明、冲突、暂不可用分开处理。
- 已终态且交付可验证的历史执行允许只核验恢复，不重放业务副作用、不手工改库、不释放其他新运行的保护；保持权限、操作身份、版本围栏和幂等约束。
- 回归正常同步、同步后补写说明、无关对象并发变化、相关内容真实冲突、仅 --check、缺损证明、刷新、进程重启和重复恢复；验证无关变化允许继续、相关冲突仍阻断。
- 部署后验证实际发送→文档落地→同步→收尾→卡片流转→下一动作准入，结合 CLI 核验；不能只测 ready 或按钮可点，不只改当前卡片。

## 判重与关联

已核对注册表和看板。BUG-0052 已归档，处理核验结果与执行保护收敛；本条承接其直接命令证明覆盖与收尾变化边界的独立修复，用户明确要求创建关联 BUG。BUG-0049 是归档包装同步识别，原始样本本次已有成功识别；BUG-0055 是消息排序，保留其独立范围；BUG-0056—0059 为加载/提交性能，非重复。

## 临时处理与边界

保留成果、原执行和保护记录；避免重复执行 bug-opsx、手工推进阶段或删除 Change。当前未确认安全解除方案。本命令只 capture，不生成 bug.md、实施代码、恢复正式现场或创建 Change。

## 数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: Chat 终态、治理快照/证明、执行保护、卡片投影、直接命令恢复；validation: 已有只读数据库、journal、工具边界和代码证据，逐文件因果归属待补证。仅保留仓库相对路径、摘要前缀、状态及操作类型；不记录原始提示、正文、凭证或本机路径。N/A：本轮无 API/DB/UI/部署实现或权限变更，后续按实际影响同步契约与测试。
