---
change_id: add-guided-feedback-dialog-copy-hierarchy
status: proposed
created_at: 2026-08-16 11:47:41
updated_at: 2026-08-16 11:47:41
---

# 设计

## 范围

本次只补充 Agent 命令引导式反馈的文案层级治理：当命令使用原生交互卡片时，顶部区域应由一处主说明承担上下文与流程意图，其他字段只承载互补信息，不重复说明同一流程。

## 规则落点

- `rules/agent-context-budget.md`：作为所有 Agent 命令 Skill 的中央契约来源。
- `.agents/skills/spec-opt/SKILL.md`：让本命令自身后续提问遵守同一约束。
- `openspec/changes/.../specs/harness-runtime/spec.md`：记录可归档到正式规格的能力变化。

## 兼容性

文本结构化选项降级路径仍保持原契约：必须包含结构化选项、推荐项和可补充说明。顶部说明层级约束主要面向原生交互卡片；文本降级输出可使用短句说明背景，但仍应避免重复文案。
