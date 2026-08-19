---
purpose: UI 型 opsx-modify 附件截图逐项视觉对照治理
content: 为 UI 验收返修增加附件截图逐项视觉对照表前置检查
created_at: 2026-08-15 13:20:05
updated_at: 2026-08-15 13:22:00
owner: MoonBox 产品团队
---

# UI 型 opsx-modify 附件截图逐项视觉对照治理

## 迭代目标

为 UI 型 `/opsx-modify` 增加返修前置门禁：当验收反馈包含附件截图、标注图、原型截图或实际截图时，必须先建立“附件截图逐项视觉对照表”，逐项确认期望、实际、偏差、检查方式、处置结论和证据入口；证据不足时先补证，不得直接进入 UI 返修。

## 变更摘要

- 在 `/opsx-modify` Clarify Feedback 阶段加入附件截图逐项视觉对照表。
- 在 Prototype-driven UI Gate 中明确附件截图对照是 UI 返修前置门禁。
- 在 UI 设计规则和原型驱动 UI 验收标准中定义对照表字段、阻断补证和返修后复验要求。
- 在上下文预算规则中限制 UI 返修只围绕当前附件、当前 Change/REQ 视觉证据、UI Skeleton 和对照表补证。
- 新增 OpenSpec Change `add-opsx-modify-ui-screenshot-comparison-gate` 并纳入 `sprint-003`。

## 影响范围

| 领域 | 影响 |
|---|---|
| API | 无 |
| DB | 无 |
| Web | 无运行时代码变更；仅影响 UI 返修治理流程 |
| 客户端 | 无 |
| 管理端 | 无运行时代码变更；仅影响 UI 返修治理流程 |
| Orval | 无 |
| Docker Compose | 无 |
| 安全 | 证据记录继续遵守脱敏要求，不保存隐私截图原文或敏感信息 |

## 更新文件

- `.agents/skills/opsx-modify/SKILL.md`
- `AGENTS.md`
- `rules/ui-design.md`
- `rules/agent-context-budget.md`
- `docs/standards/prototype-ui-acceptance.md`
- `docs/spec-logs/CHANGELOG.md`
- `openspec/changes/add-opsx-modify-ui-screenshot-comparison-gate/`
- `iterations/change/sprint-003/sprint.yaml`

## 验证结果

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate add-opsx-modify-ui-screenshot-comparison-gate`：通过。
- `python scripts/validate-sprint-scope.py sprint-003 --item add-opsx-modify-ui-screenshot-comparison-gate`：首次提示需刷新 `sprint.md`；Workflow Sync 后复验通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change add-opsx-modify-ui-screenshot-comparison-gate --sprint auto`：通过，Updated 2，Errors 0。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-opsx-modify-ui-screenshot-comparison-gate --sprint sprint-003 --json`：通过，usage_mode actual，warning_count 0。

## 后续建议

后续可评估是否把附件截图对照表做成校验脚本或模板片段，在 Change `tasks.md` / `trace.md` 中自动检查字段完整性。
