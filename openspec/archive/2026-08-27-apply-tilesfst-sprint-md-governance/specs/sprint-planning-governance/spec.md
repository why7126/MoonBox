## MODIFIED Requirements

### Requirement: Sprint 规划文档一致性

MoonBox MUST 以 `sprint.yaml` 作为 Sprint 正式范围机器事实源，并通过 Workflow Sync 派生刷新 `sprint.md`、`release-note.md` 和 `acceptance-report.md`。`sprint.md` MUST 作为产品化规划面板，展示 Sprint 目标、正式 Scope、容量、里程碑、风险、知识库承接和横切预防信息，且不得与 `sprint.yaml` 正式范围漂移。

#### Scenario: Sprint 目标区覆盖正式范围

- **WHEN** Workflow Sync 刷新 Sprint 文档
- **THEN** `sprint.md` 的 `## 1. Sprint 目标` MUST 包含 `Sprint 目标编号列表`
- **AND** 列表 MUST 覆盖 `sprint.yaml` 中的 REQ、BUG 和无 Issue 来源的纯治理 Change
- **AND** 每个正式范围项 MUST 有 `### <id> 要点` 段落
- **AND** `validate-sprint-scope.py` MUST 校验目标编号列表、要点段落、Scope 主表和 workflow-sync 派生表共同覆盖正式范围
