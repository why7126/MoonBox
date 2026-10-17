---
title: 治理候选后端命令边界回归复核
created_at: 2026-10-13 20:10:00
updated_at: 2026-10-13 20:10:00
---

# 治理候选后端命令边界回归复核

- `test_fixed_write_set_and_semantic_rejection` 覆盖 REQ Generate 固定写集及源码、已生效规格、其他注册表的越界拒绝；`test_bug_generate_write_set_and_next_step_rejection` 覆盖 BUG Generate 正向四文件写集及越界文件、错误下一步拒绝。
- 独立的 `test_governance_unsupported_action.py` 验证未知 action 返回 2604 和“尚未接入产品写入链路”；独立文件避免改动其他 AC 共用测试文件的输入指纹。`test_prepare_bug_generate_uses_bug_action_and_prompt` 与 REQ 相关回归分别覆盖准备动作和既有链路。
- 两个后端测试文件合计 46 passed；1 条现有 Starlette/httpx 弃用 warning。该项是后端合成回归，不代替真实产品写入轮次。
