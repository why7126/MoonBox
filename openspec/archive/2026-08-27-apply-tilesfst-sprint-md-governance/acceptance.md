---
change_id: apply-tilesfst-sprint-md-governance
status: proposed
created_at: 2026-08-27 01:02:45
updated_at: 2026-08-27 01:12:30
---

# Acceptance

- [x] AC-001：Workflow Sync 刷新 `sprint.md` 时包含 `Sprint 目标编号列表` 和每项要点段落。
- [x] AC-002：`validate-sprint-scope.py` 可校验目标编号列表、要点段落、Scope 主表和 workflow-sync 派生表。
- [x] AC-003：Sprint 技能和迭代生命周期规则说明 `sprint.md` 产品化规划面板结构与追加范围顺序。
- [x] AC-004：`sprint-exps` 与 `sprint-archive` 说明优先读取 Sprint Fact Sheet，再按 blocker/warning 定向读取原始文档。
- [x] AC-005：本次学习报告落入 `docs/spec-logs/`，不包含学习对象本机绝对路径、系统用户名、源码全文、密钥或真实客户数据。
- [x] AC-006：验证通过，且 `git diff --name-only -- src` 输出为空。
