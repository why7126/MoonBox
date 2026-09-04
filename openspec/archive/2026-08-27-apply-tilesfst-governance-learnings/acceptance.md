---
change_id: apply-tilesfst-governance-learnings
status: proposed
created_at: 2026-08-27 00:03:08
updated_at: 2026-08-27 00:03:08
---

# 验收标准

| 编号 | 验收项 | 状态 | 证据 |
|---|---|---|---|
| AC-1 | 输出契约卫生校验能识别占位模板和规范语气泄漏风险 | passed | `python scripts/validate-agent-context-budget.py` 通过，报告未发现最终输出占位模板、通用示例或规范语气泄漏风险。 |
| AC-2 | Sprint 选择门禁脚本可执行并报告当前 active Sprint 与下一个编号 | passed | `python scripts/validate-sprint-selection.py` 通过，当前 active Sprint 为 `sprint-003`，下一个编号为 `sprint-004`。 |
| AC-3 | 升级计划脚本可生成并校验安全的计划结构 | passed | `python scripts/validate-release-upgrade.py --help` 与 `env-diff` 通过；`env-diff` 仅读取可提交 env 示例。 |
| AC-4 | AI Usage 矩阵能区分未观测与真实 0 | passed | `python -m py_compile scripts/ai_usage.py scripts/generate-sprint-fact-sheet.py` 通过；矩阵新增 `cell_status`，Markdown 将 unknown 渲染为 `-`。 |
| AC-5 | 学习报告落盘且不包含本机绝对路径、学习对象源码或敏感信息 | passed | `docs/spec-logs/20260827001607-study-tilesfst-governance.md` 已落盘；上下文预算与目录结构校验通过。 |
| AC-6 | 本次学习应用未修改 `src/` 业务运行时代码 | passed | `git diff --name-only -- src` 输出为空。 |
