---
change_id: add-ui-reference-replication-governance
created_at: 2026-09-02 19:12:31
updated_at: 2026-09-02 19:12:31
---

# Test Plan: UI 参考稿复刻动作矩阵治理

## 必跑校验

| 命令 | 目的 |
|---|---|
| `python scripts/validate-agent-context-budget.py` | 校验技能上下文预算和命令输出契约。 |
| `python scripts/validate-openspec-language.py` | 校验 OpenSpec 中文优先和脚手架文案。 |
| `python scripts/validate-directory-structure.py` | 校验目录结构没有新增非法路径。 |
| `openspec validate add-ui-reference-replication-governance --strict` | 校验目标 Change。 |
| `python scripts/validate-sprint-scope.py sprint-004 --item add-ui-reference-replication-governance` | 校验 Sprint scope 与 Change 范围一致。 |
| `python scripts/sync-workflow-status.py --event opsx.apply --change add-ui-reference-replication-governance --sprint auto` | 同步纯治理 Change 的 Sprint 状态。 |
| `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-ui-reference-replication-governance --sprint sprint-004 --json` | 记录或报告 AI Usage hook 结果。 |

## 执行结果

| 命令 | 结果 |
|---|---|
| `python scripts/validate-agent-context-budget.py` | 通过 |
| `python scripts/validate-openspec-language.py` | 通过 |
| `python scripts/validate-directory-structure.py` | 通过 |
| `openspec validate add-ui-reference-replication-governance --strict` | 通过 |
| `python scripts/validate-sprint-scope.py sprint-004 --item add-ui-reference-replication-governance` | 通过 |
| `python scripts/sync-workflow-status.py --event opsx.apply --change add-ui-reference-replication-governance --sprint auto` | 通过，Updated 1，Errors 0 |
| `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-ui-reference-replication-governance --sprint sprint-004 --json` | 通过，usage_mode actual，warning_count 0 |

## 不适用验证

- API / DB / Web / 管理端 / Orval / Docker Compose 测试不适用，因为本 Change 不修改运行时代码、接口、schema、生成物或部署配置。
