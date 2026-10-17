# BUG-0026 AC-001 产品首次归档证据

- 取证时间：2026-10-12；本机 MoonBox `http://localhost:39002`，Firefox；source 模式。
- 专用虚拟样本：BUG-0042-chat-archive-issue-promote-retest-2，关联 Change `fix-chat-archive-issue-promote-retest-2`，归属 sprint-009。它仅用于 BUG-0026 AC-001，不代表新增生产缺陷。
- 对象 Chat 会话：`cdebda67-4749-5b70-b24a-b73688b43428`，主对象为 BUG-0042。首次归档轮次：`489d335c-a077-4734-b0b0-4fcc4babfb1b`。
- 产品 `chat_events`：序号 43 为 `bash scripts/archive-change.sh fix-chat-archive-issue-promote-retest-2 --finalize` started，序号 47 为同一命令 completed，`exit_code=0`。`chat_turns` 持久化状态为 `completed`，`error_code=null`；Firefox 亦显示“已完成”、退出码 0。
- 同一命令输出：规格合并新增 1 项；Change 迁至唯一 `openspec/archive/2026-10-12-fix-chat-archive-issue-promote-retest-2/`，活动目录消失；Workflow Sync `Errors: 0`；BUG-0042 promote 到 `issues/bugs/archive/`，registry / CHANGELOG 当前态更新为 done/archive。
- 规格事实：`openspec/specs/chat-archive-acceptance-evidence/spec.md` 含本样本的新增 Requirement。归档 Change `trace.md` 的 `status: applied` 保留 apply 执行事实；仓库历史归档 Change 也普遍保留此值，归档阶段由目录、Issue `done/archive` 与 Workflow Sync 共同表达。本 AC 不以该字段单独判断归档是否成功。
- 截图：`evidence/20261012-bug0042-product-archive-completed.png`。此前 BUG-0040 与 BUG-0041 轮次分别 stopped，均未计入 AC-001 成功证据；BUG-0041 后由宿主恢复，不冒充产品同轮完成。
