---
purpose: 原型驱动 UI 开发门禁治理迭代日志
content: 记录 prototype 页面原型拆解、UI Skeleton、1440px 视觉验收和 REQ 最终一致性回填机制的规范更新
created_at: 2026-08-08 21:57:40
updated_at: 2026-08-08 21:57:40
owner: MoonBox 产品团队
---

# 原型驱动 UI 开发门禁治理迭代日志

## 迭代目标

建立带 `prototype/` 页面从需求完善到归档的连续门禁，确保原型拆解、UI Skeleton、1440px 视觉验收和 REQ 文档最终一致性检查不会在实现和归档阶段遗漏。

## 变更摘要

- `/req-complete`：新增 prototype 拆解、`AC-PROTOTYPE-*` 和 `prototype_gate` 要求。
- `/req-opsx`：要求 Change 承接原型拆解，生成 UI Skeleton、任务和冲突处理。
- `/opsx-apply`：实现 UI 任务前先完成 Skeleton，完成任务前必须有 1440px 视觉验收证据。
- `/opsx-modify`：UI 返修后重新执行 1440px 视觉验收，并回填 Change/REQ 文档。
- `/opsx-archive`：新增 prototype final consistency gate，归档前复核 REQ 与最终实现证据一致。
- Workflow Sync：只同步已有 prototype 验收证据和最终一致性状态，不替父命令推断视觉通过。
- `rules/ui-design.md` 与 knowledge-base：沉淀 Prototype-driven UI Gate。

## 影响范围

- Agent 技能门禁和输出契约。
- UI 设计规则和知识库最佳实践。
- OpenSpec active Change 与 `sprint-001` 范围。

## 更新文件

- `.agents/skills/req-complete/SKILL.md`
- `.agents/skills/req-opsx/SKILL.md`
- `.agents/skills/opsx-apply/SKILL.md`
- `.agents/skills/opsx-modify/SKILL.md`
- `.agents/skills/opsx-archive/SKILL.md`
- `.agents/skills/workflow-sync/SKILL.md`
- `AGENTS.md`
- `rules/agent-context-budget.md`
- `rules/ui-design.md`
- `docs/knowledge-base/README.md`
- `docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`
- `openspec/changes/enforce-prototype-driven-ui-gate/**`
- `iterations/change/sprint-001/sprint.yaml`

## 验证结果

- 已运行 Workflow Sync：`python scripts/sync-workflow-status.py --event opsx.apply --change enforce-prototype-driven-ui-gate --sprint auto`，结果通过。
- 已运行 AI Usage hook：`python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change enforce-prototype-driven-ui-gate --sprint sprint-001 --json`，结果通过。
- 后续已运行项目治理校验，详见本次命令最终回复。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

- API：不涉及。
- DB：不涉及。
- Web：不修改运行时代码；仅新增 UI 开发与验收门禁。
- 客户端生成 / Orval：不涉及。
- 管理端：不修改运行时代码；后续带 prototype 的管理端页面需遵守该门禁。
- Docker Compose：不涉及。

## 后续建议

- 后续可将 `prototype_gate` 检查沉淀为脚本级校验，在 `/opsx-archive` 前自动扫描 1440px 证据与 REQ 一致性。

