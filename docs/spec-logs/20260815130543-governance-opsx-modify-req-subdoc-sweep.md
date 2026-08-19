---
purpose: 治理迭代日志
content: 为 opsx-modify 增加 REQ 子文档一致性扫尾检查
created_at: 2026-08-15 13:05:43
updated_at: 2026-08-15 13:08:30
owner: MoonBox 产品团队
---

# 为 opsx-modify 增加 REQ 子文档一致性扫尾检查

## 迭代目标

在 `/opsx-modify` 完成前增加 REQ 子文档一致性扫尾检查，避免验收返修后只更新 PRD 或单一验收文档，而遗漏业务流程、用户故事和 `prototype/**` 等事实源。

## 变更摘要

- `/opsx-modify` 增加 `REQ Subdocument Consistency Sweep` 门禁。
- REQ 来源返修必须按 linked REQ 目录实际存在的 `requirement.md`、业务流程、用户故事、`acceptance.md`、`trace.md` 和 `prototype/**` 判断是否需同步。
- 无需更新的子文档也必须在 Change `tasks.md` 验收返修记录或 `trace.md` 中记录理由。
- 若扫尾发现仍在当前 Change 边界内的漂移，必须先回填 REQ 子文档；若扩大边界，则阻断并引导新建 REQ/BUG 或 OpenSpec Change。

## 影响范围

- `.agents/skills/opsx-modify/SKILL.md`
- `AGENTS.md`
- `rules/agent-context-budget.md`
- `openspec/changes/add-opsx-modify-req-subdoc-sweep/`
- `iterations/change/sprint-003/`
- `docs/spec-logs/CHANGELOG.md`

## 更新文件

- `.agents/skills/opsx-modify/SKILL.md`
- `AGENTS.md`
- `rules/agent-context-budget.md`
- `openspec/changes/add-opsx-modify-req-subdoc-sweep/{proposal.md,design.md,tasks.md,trace.md}`
- `openspec/changes/add-opsx-modify-req-subdoc-sweep/specs/agent-workflow-tooling/spec.md`
- `iterations/change/sprint-003/sprint.yaml`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `openspec validate add-opsx-modify-req-subdoc-sweep --strict`：通过。
- `git diff --check -- <touched docs>`：通过。
- `python scripts/validate-sprint-scope.py sprint-003 --item add-opsx-modify-req-subdoc-sweep`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change add-opsx-modify-req-subdoc-sweep --sprint auto`：通过。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change add-opsx-modify-req-subdoc-sweep --sprint sprint-003 --json`：通过，`usage_mode: actual`，warning 0。
- `python scripts/validate-directory-structure.py`：未通过，根目录存在未登记 `tmp/`。该目录为本次变更前已有未跟踪目录，本次未删除。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

- API：无。
- DB：无。
- Web：无运行时影响。
- 客户端生成 / Orval：无。
- 管理端：无运行时影响。
- Docker Compose：无。

## 后续建议

- 后续可考虑将 REQ 子文档一致性扫尾检查沉淀为 Workflow Sync 或归档前自动校验脚本。
