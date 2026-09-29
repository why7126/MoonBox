---
purpose: 治理迭代日志
content: 记录 opsx-modify 验收返修台账文档结构优化
created_at: 2026-09-15 08:47:46
updated_at: 2026-09-15 09:01:13
owner: MoonBox 产品团队
---

# opsx-modify 验收返修台账结构优化

## 迭代目标

将完整验收返修台账从 `tasks.md` 调整到 `acceptance-fixes.md`，让 `tasks.md` 回归任务清单职责，`trace.md` 保留摘要和证据入口。

## 变更摘要

- `/opsx-modify`：完整返修台账写入 `acceptance-fixes.md`；`tasks.md` 只保留返修任务勾选和台账链接；`trace.md` 保留摘要、证据入口和验证结果。
- `/opsx-archive`：归档复核读取返修台账，若台账缺失、证据 stale 或与 trace 摘要不一致，应阻断或要求补齐。
- 文档治理规则：明确 Change 推荐结构中 `acceptance-fixes.md` 的职责，并固化新旧返修记录兼容策略。
- 2026-09-15 09:01:13 返修：将最初讨论中的 `implementation/acceptance-fixes.md` 收敛为 Change 根目录 `acceptance-fixes.md`，降低路径层级和目录语义成本。

## 影响范围

- 影响 `.agents/skills/opsx-modify/SKILL.md`
- 影响 `.agents/skills/opsx-archive/SKILL.md`
- 影响 `rules/document-governance.md`
- 影响 `openspec/changes/optimize-opsx-modify-acceptance-fix-ledger/`
- 影响 `iterations/change/sprint-007/sprint.yaml`

## 更新文件

- `.agents/skills/opsx-modify/SKILL.md`
- `.agents/skills/opsx-archive/SKILL.md`
- `rules/document-governance.md`
- `docs/spec-logs/CHANGELOG.md`
- `docs/spec-logs/20260915084746-governance-opsx-modify-acceptance-fix-ledger.md`
- `openspec/changes/optimize-opsx-modify-acceptance-fix-ledger/**`

## 验证结果

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py --change optimize-opsx-modify-acceptance-fix-ledger --residual-report`：通过，未发现非当前 Change 中文残留。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate optimize-opsx-modify-acceptance-fix-ledger`：通过。
- `python scripts/validate-sprint-scope.py sprint-007 --item optimize-opsx-modify-acceptance-fix-ledger`：通过。
- `git diff --check -- <本次治理文件>`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change optimize-opsx-modify-acceptance-fix-ledger --sprint auto`：通过，更新 3 个投影。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change optimize-opsx-modify-acceptance-fix-ledger --sprint sprint-007 --json`：warning，`usage_mode: unavailable`，未生成 command run；不阻断父命令。
- 2026-09-15 09:01:13 路径返修后重新运行上下文预算、当前 Change 中文、目录结构、OpenSpec validate、Sprint scope、聚焦 diff whitespace、Workflow Sync 和 AI Usage hook：除 AI Usage `usage_mode: unavailable` warning 外均通过；Workflow Sync 无新派生差异。

## API / DB / Web / 客户端 / 管理端 / Orval / Docker Compose 影响

不适用。本次只调整治理技能和文档结构规则，不修改业务 API、数据库、Web 实现、管理端、客户端生成物、Orval 配置或 Docker Compose。

## 后续建议

后续 `/opsx-modify` 真实执行时观察新台账位置是否降低 `tasks.md` 噪音；如需要，可再补充脚本检查 `tasks.md` 是否保留台账链接。
