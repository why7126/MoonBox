## ADDED Requirements

### Requirement: Sprint 规划文档一致性

MoonBox MUST 以 `sprint.yaml` 作为 Sprint 正式范围、容量、估算与计划时间的机器事实源，并通过 Workflow Sync 派生刷新 `sprint.md`、`release-note.md` 和 `acceptance-report.md`。`sprint.md` MUST 作为产品化规划面板，展示 Sprint 目标、正式 Scope、容量、里程碑、风险、知识库承接和横切预防信息，且不得与 `sprint.yaml` 正式范围漂移。

#### Scenario: Sprint 规划章节结构化派生

- **WHEN** Workflow Sync 刷新 Sprint 文档
- **THEN** `sprint.md` MUST 包含 `## 3. 工作量与容量`
- **AND** `sprint.md` MUST 包含 `## 4. 里程碑`
- **AND** `sprint.md` MUST 包含 `## 5. 风险与缓冲`
- **AND** `sprint.md` MUST 包含 `## 6. 知识库承接`
- **AND** 这些章节的派生内容 MUST 由 workflow-sync marker 包裹
- **AND** `validate-sprint-scope.py` MUST 校验这些章节和 marker 存在
