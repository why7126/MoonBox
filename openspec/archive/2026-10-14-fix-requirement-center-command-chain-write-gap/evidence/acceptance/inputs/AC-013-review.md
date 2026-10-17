---
title: "缺陷生成命令展示与后端约束复验"
created_at: 2026-10-14 10:03:00
updated_at: 2026-10-14 10:03:00
---

# 缺陷生成命令展示与后端约束复验

结论：通过。

真实产品：隔离 BUG-1001 的准备态 Chat 输入框仅显示 `/bug-generate BUG-1001-bug-0025`，未显示内部治理约束；1440×900 截图与样式采样已保存。发送后 turn `6a66a033-9e73-425b-9458-0f36f8318091` completed，candidate `6de047fa-0eb6-5278-8669-b41c7e5fd51c` applied，application `7695e2fd-c475-4ecd-adbe-f0fd8525b737` applied/verified。

后端断言：`test_prepare_bug_generate_uses_bug_action_and_prompt` 验证展示 prompt 只含完整命令，未编辑的发送路径恢复治理约束，编辑后的 prompt 原样交给执行器、不追加旧约束；目标测试 1 passed。

数据边界：专用隔离项目，无正式 BUG 对象写入。
