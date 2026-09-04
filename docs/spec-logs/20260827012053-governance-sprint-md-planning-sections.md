---
created_at: 2026-08-27 01:20:53
updated_at: 2026-08-27 01:25:00
---

# sprint.md 规划章节结构化派生治理日志

## 迭代目标

将 `sprint.md` 的工作量与容量、里程碑、风险与缓冲、知识库承接章节纳入 Workflow Sync 结构化派生，减少人工维护漂移。

## 变更摘要

- 新增 Workflow Sync 派生章节：`## 3. 工作量与容量`、`## 4. 里程碑`、`## 5. 风险与缓冲`、`## 6. 知识库承接`。
- 新增 `workflow-sync:sprint-*-section` marker，派生内容由脚本覆盖，人工补充保留在 marker 外。
- 增强 `validate-sprint-scope.py`，校验规划章节和 marker。
- 同步 Sprint 生命周期规则、workflow-sync 技能、sprint-propose 和 sprint-apply 技能。

## 影响范围

- API：不影响。
- DB：不影响。
- Web：不修改业务运行时代码。
- 客户端：不影响。
- 管理端：不影响。
- Orval：不需要。
- Docker Compose：不影响。
- 测试：新增/增强治理脚本校验；业务测试不适用。

## 更新文件

| 文件 | 说明 |
|---|---|
| `scripts/workflow_sync/patch.py` | 派生 `sprint.md` 规划章节，并修复 Scope 摘要刷新正则。 |
| `scripts/validate-sprint-scope.py` | 校验规划章节与 marker。 |
| `rules/iterations-lifecycle.md` | 固化规划章节由 Workflow Sync 派生维护。 |
| `.agents/skills/workflow-sync/SKILL.md` | 同步 marker 与刷新范围说明。 |
| `.agents/skills/sprint-propose/SKILL.md` | 明确追加范围后由 Workflow Sync 派生规划章节。 |
| `.agents/skills/sprint-apply/SKILL.md` | 将规划章节纳入紧凑读取面板。 |
| `openspec/changes/derive-sprint-md-planning-sections/` | 承载本次治理变更。 |
| `iterations/change/sprint-003/` | 纳入纯治理 Change，并刷新 Sprint 派生文档。 |

## 验证结果

| 命令 | 结果 |
|---|---|
| `python -m py_compile scripts/workflow_sync/patch.py scripts/validate-sprint-scope.py` | 通过 |
| `python scripts/sync-workflow-status.py --event opsx.apply --change derive-sprint-md-planning-sections --sprint auto --dry-run` | 通过，预计更新 2 处 |
| `python scripts/sync-workflow-status.py --event opsx.apply --change derive-sprint-md-planning-sections --sprint auto` | 通过 |
| `python scripts/validate-sprint-scope.py sprint-003 --item derive-sprint-md-planning-sections` | 通过 |
| `python scripts/validate-sprint-scope.py sprint-003` | 通过 |
| `openspec validate derive-sprint-md-planning-sections` | 通过 |
| `python scripts/validate-agent-context-budget.py` | 通过 |
| `python scripts/validate-openspec-language.py` | 通过 |
| `python scripts/validate-directory-structure.py` | 通过 |
| `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change derive-sprint-md-planning-sections --sprint sprint-003 --json` | warning；本地会话无 command-run token 事件，usage mode 为 `unavailable`，不阻塞治理应用 |
| `git diff --name-only -- src` | 通过；输出为空 |

## 后续建议

- 后续可继续把横切预防清单和依赖 ASCII 树纳入可验证派生，但应先确认人工补充边界。
