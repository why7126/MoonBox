---
purpose: OpenSpec 语言校验按 Change 范围执行治理日志
content: 记录 OpenSpec 校验脚本增加 --change 聚焦校验参数的治理变更
created_at: 2026-09-14 15:20:11
updated_at: 2026-09-14 15:50:00
owner: MoonBox 产品团队
---

# OpenSpec 语言校验按 Change 范围执行治理日志

## 迭代目标

为 OpenSpec 校验脚本增加按 Change 范围校验参数，避免多个 active Change 并行推进时，一个 Change 的语言或结构问题阻塞另一个 Change 的验收结论。

## 变更摘要

- 新增 `--change <change-id>` 参数，支持重复传入多个 Change。
- 未传 `--change` 时保留全量 active Change 校验行为。
- 新增 `--residual-report`，与 `--change` 配合输出非当前 Change 中文残留摘要且不影响当前 Change 退出码。
- `--include-archive` 与 `--change` 组合时支持校验目标归档 Change。
- 不存在的目标 Change 返回失败并输出明确说明。
- `scripts/validate-openspec.sh` 支持 `--change <change-id>`，聚焦运行当前 Change 中文优先校验与 `openspec validate <change-id>`。
- `/req-opsx` 与 `/bug-opsx` 生成或确认 Change 后运行 `python scripts/validate-openspec-language.py --change <change-id> --residual-report`，当前 Change 失败阻断当前链路，其他 active Change 残留只进入分离报告。
- 新增纯治理 OpenSpec Change，并纳入 `sprint-006`。

## 影响范围

- 治理脚本：影响 OpenSpec 中文优先语言校验命令和 OpenSpec 校验总入口。
- 命令技能：影响 `/req-opsx` 与 `/bug-opsx` 生成后的收尾校验契约。
- OpenSpec：新增 active Change 与 `agent-workflow-tooling` delta spec。
- Sprint：新增纯治理范围项。
- 文档：更新治理日志和治理历史索引。

## 更新文件

- `scripts/validate-openspec-language.py`
- `scripts/validate-openspec.sh`
- `scripts/validate-directory-structure.py`
- `tests/unit/test_validate_openspec_language.py`
- `.agents/skills/req-opsx/SKILL.md`
- `.agents/skills/bug-opsx/SKILL.md`
- `AGENTS.md`
- `rules/bug-management.md`
- `rules/agent-context-budget.md`
- `docs/08-command-execution-order.md`
- `openspec/changes/optimize-openspec-language-change-scope/`
- `iterations/change/sprint-006/sprint.yaml`
- `docs/spec-logs/20260914152011-governance-openspec-language-change-scope.md`
- `docs/spec-logs/CHANGELOG.md`

## 验证结果

- `python scripts/validate-change-identity.py --new-id optimize-openspec-language-change-scope`：通过。
- `python scripts/validate-openspec-language.py --change optimize-openspec-language-change-scope`：通过。
- `python scripts/validate-openspec-language.py --change __missing__`：按预期失败，输出未找到目标 Change。
- `python scripts/validate-openspec-language.py --change optimize-openspec-language-change-scope --residual-report`：通过，输出非当前 Change 中文残留 57 项摘要。
- `bash -n scripts/validate-openspec.sh`：通过。
- `bash scripts/validate-openspec.sh --change optimize-openspec-language-change-scope --residual-report`：通过，当前 Change 中文优先校验和 OpenSpec 结构校验均通过。
- `bash scripts/validate-openspec.sh --change __missing__`：按预期失败，透传未找到目标 Change。
- `bash scripts/validate-openspec.sh`：通过，目录结构与全量中文优先校验通过。
- `bash scripts/validate-openspec.sh --include-archive --change optimize-openspec-language-change-scope --residual-report`：通过，归档 Change 中文优先校验通过，正式规格结构校验 25 passed。
- `python -m pytest tests/unit/test_validate_openspec_language.py`：3 passed。
- `python -m py_compile scripts/validate-openspec-language.py`：通过。
- `openspec validate optimize-openspec-language-change-scope`：通过。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-openspec-language.py --change fix-requirement-center-html-preview-auth-lost --residual-report`：通过，确认非当前 Change 英文标题残留已清理。
- `openspec validate fix-requirement-center-html-preview-auth-lost`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change optimize-openspec-language-change-scope --sprint auto`：通过，更新 Sprint 派生文件。
- `python scripts/sync-workflow-status.py --event opsx.apply --change optimize-openspec-language-change-scope --sprint auto`：通过，no delta。
- `python scripts/validate-sprint-scope.py sprint-006 --item optimize-openspec-language-change-scope`：通过；初次失败原因为 `sprint.md` 尚未由 Workflow Sync 派生刷新。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change optimize-openspec-language-change-scope --sprint sprint-006 --json`：warning，未发现可归因 command-run token 事件。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change optimize-openspec-language-change-scope --sprint sprint-006 --json`：warning，`usage_mode: unavailable`，未发现可归因 token_count 事件。
- `scripts/archive-change.sh optimize-openspec-language-change-scope`：通过，归档至 `openspec/archive/2026-09-14-optimize-openspec-language-change-scope/` 并合并正式 spec。
- `python scripts/validate-archive-evidence.py --change optimize-openspec-language-change-scope --archive-path openspec/archive/2026-09-14-optimize-openspec-language-change-scope`：通过。
- `python scripts/sync-workflow-status.py --event opsx.archive --change optimize-openspec-language-change-scope --sprint auto`：通过，更新 2 个派生文件。
- `python scripts/promote-issues-for-archive.py --change optimize-openspec-language-change-scope --reason "/opsx-archive optimize-openspec-language-change-scope"`：通过，无可迁移 Issue。
- `openspec validate --all`：通过，32 passed。
- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change optimize-openspec-language-change-scope --sprint sprint-006 --json`：warning，`usage_mode: unavailable`，未发现可归因 token_count 事件。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

- API：不适用，未修改接口契约。
- DB：不适用，未修改数据结构或迁移。
- Web：不适用，未修改前端页面或请求封装。
- 客户端生成 / Orval：不适用，未修改 OpenAPI。
- 管理端：不适用，未修改管理端实现。
- Docker Compose：不适用，未修改部署拓扑或环境变量。
- 安全：不适用，未修改权限、鉴权或敏感数据处理。

## 后续建议

后续可在 `/req-opsx`、`/bug-opsx`、`/opsx-apply` 和归档前校验中逐步采用 `bash scripts/validate-openspec.sh --change <change-id> --residual-report`，形成单 Change 验收的一致命令体验。
