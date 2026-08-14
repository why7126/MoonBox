---
purpose: 记录原型驱动 UI 验收规范强化
content: UI Contract、前后台一致性 checklist、Skeleton 首轮确认、截图门禁、computed style、Mock/API 和图标文案一致性治理更新
created_at: 2026-08-10 20:14:00
updated_at: 2026-08-10 20:14:00
owner: MoonBox 产品团队
---

# 原型驱动 UI 验收规范强化

## 迭代目标

将带 `prototype/` 的 UI Change 从“有原型拆解和 1440px 验收”升级为可执行的 UI Contract、Skeleton 首轮确认、前后台一致性 checklist、关键交互截图、computed style、Mock/API 边界和图标/文案一致性门禁，减少类似 REQ-0012 的多轮视觉返修。

## 变更摘要

- 新增 `docs/standards/prototype-ui-acceptance.md`，沉淀 UI Contract 模板、Skeleton 首轮确认、截图矩阵、computed style、Mock/API 边界和归档门禁。
- 强化 `rules/ui-design.md` 的 Prototype-driven UI Gate，补齐前后台一致性、证据 stale、图标文案和 Mock/API 边界要求。
- 更新 `AGENTS.md` UI 读取路由和流程红线，确保带 prototype 的 UI Change 必读专项标准。
- 更新 `/req-opsx`、`/opsx-apply`、`/opsx-modify` 技能，要求生成、实现和返修阶段使用新门禁。
- 创建 active OpenSpec Change `strengthen-prototype-ui-acceptance` 并纳入 `sprint-002`。

## 影响范围

- API：无影响。
- DB：无影响。
- Web：不修改 `src/` 业务实现；后续带 prototype 的前台/后台 UI Change 需要遵守新门禁。
- 客户端：无影响。
- 管理端：不修改运行时代码；后续管理端 UI Change 若带 prototype 或参照既有页面，需要执行一致性 checklist。
- Orval：无影响。
- Docker Compose：无影响。
- 安全：无运行时安全变更；Mock/API 边界声明可减少验收误判。

## 更新文件

- `AGENTS.md`
- `rules/ui-design.md`
- `docs/README.md`
- `docs/standards/prototype-ui-acceptance.md`
- `docs/spec-logs/CHANGELOG.md`
- `.agents/skills/req-opsx/SKILL.md`
- `.agents/skills/opsx-apply/SKILL.md`
- `.agents/skills/opsx-modify/SKILL.md`
- `iterations/change/sprint-002/sprint.md`
- `iterations/change/sprint-002/sprint.yaml`
- `openspec/changes/strengthen-prototype-ui-acceptance/**`

## 验证结果

- 已运行 `python scripts/validate-agent-context-budget.py`，通过。
- 已运行 `python scripts/validate-openspec-language.py`，通过。
- 已运行 `python scripts/validate-directory-structure.py`，通过。
- 已运行 `openspec validate strengthen-prototype-ui-acceptance --strict`，通过。
- 已运行 `python scripts/validate-sprint-scope.py sprint-002 --item strengthen-prototype-ui-acceptance`，通过。
- 已运行聚焦 `git diff --check`，通过。
- 已运行 Workflow Sync：`python scripts/sync-workflow-status.py --event opsx.apply --change strengthen-prototype-ui-acceptance --sprint auto`，结果通过并解析到 `sprint-002`。
- 已运行 AI Usage hook：`python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change strengthen-prototype-ui-acceptance --sprint sprint-002 --json`，结果通过。

## 后续建议

- 后续可将 UI Contract、截图证据和 computed style 检查沉淀为半自动校验脚本，在 `/opsx-archive` 前扫描 Change `trace.md` 是否缺证据。
- REQ-0012 若继续返修，应直接按本标准回补 UI Contract 与证据，而不是继续以自然语言逐项追差异。
