---
title: 生成命令可见消息与执行约束边界复核
created_at: 2026-10-12 23:54:00
updated_at: 2026-10-12 23:54:00
---

# 生成命令可见消息与执行约束边界复核

- 使用隔离验收对象 BUG-0037 的已完成产品轮次 `bfaba014-622d-4099-8fe4-0aebeb4524e6`。只读数据库检查：`chat_turns.prompt` 为 22 字符，同轮 `chat_messages` 的 user 消息也是 22 字符且与 prompt 相等；未命中内部治理约束标记。未复制或保存消息正文。
- 同轮 `execution.tool` 中 `bug.generate` 完成且退出码为 0。候选绑定存在且状态 applied；后端 `execution_prompt_for_turn` 由 candidate 恢复执行约束，相关实现入口见 `src/backend/app/governance/preparation.py` 与 Chat 执行模块。
- 此项只判断用户可见消息持久化和后端执行约束恢复，不由这份证据推断其他命令的应用成功或 UI 宽度。
