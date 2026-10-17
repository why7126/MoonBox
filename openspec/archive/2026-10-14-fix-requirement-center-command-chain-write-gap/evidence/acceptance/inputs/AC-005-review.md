---
title: Bug 生成候选与应用记录复核
created_at: 2026-10-12 23:53:00
updated_at: 2026-10-12 23:53:00
---

# Bug 生成候选与应用记录复核

- 样本：隔离验收对象 BUG-0037-acceptance-isolated-generate；不属于正式缺陷。
- 产品轮次 `bfaba014-622d-4099-8fe4-0aebeb4524e6` 为 completed；同轮 `execution.tool` 中 `bug.generate` 完成且退出码为 0。
- 候选 `a58c4f0a-a28b-5d2b-a512-a1b2b18e8461` 当前为 applied；应用 `ae1dadf5-b3b5-4cc3-8c61-1d0659858af1` 当前为 applied/verified，无错误码。
- 隔离事实源实际存在该对象的 `bug.md`；此前 Firefox 看板刷新后展示规划中卡片和“完善 Bug”动作。后续 `bug-complete` 已将该对象推进 enriching，不把当前状态冒充为生成时 draft。
- 复核入口：本地产品 SQLite 的 `chat_turns`、`chat_events`、`governance_candidates`、`governance_applications` 只读状态；原隔离事实源文件；本 Change `verification.md` 的 BUG-0037 轮次记录。未保存原始消息或事件正文。
