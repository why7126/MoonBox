---
title: Bug 生成准备候选复核
created_at: 2026-10-13 08:33:00
updated_at: 2026-10-13 08:33:00
---

# Bug 生成准备候选复核

- 历史 Firefox 产品入口从 BUG-0036 采集池卡片启动 `bug-generate`；原产品数据库留下该 BUG 对象的 prepared 候选。此次只读复核确认 preparation 对 BUG 对象与 action 有实际记录，不将历史候选被拒绝误写为应用成功。
- 当前聚焦回归 `test_prepare_bug_generate_uses_bug_action_and_prompt` 1 passed；候选应用成功另由 AC-004/005/015 判断。
- 依据：Change `verification.md` AC-002 行及 Issue `acceptance.md` 的历史轮次记录。此文件不包含原始 Prompt 或日志正文。
