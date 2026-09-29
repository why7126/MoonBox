---
purpose: 治理迭代日志
content: 记录 Change 交付验证来源契约统一
created_at: 2026-09-15 09:07:02
updated_at: 2026-09-15 09:21:06
owner: MoonBox 产品团队
---

# Change 交付验证来源契约统一

## 迭代目标

统一 applied Change 的交付验证来源契约：纯治理 Change 不强制生成 `acceptance.md` 或 `verification.md`，但所有 applied Change 必须在 Change 内保留需求中心可识别的验证来源。

## 变更摘要

- `/spec-opt`：治理优化完成前需在 Change 内写入可识别验证来源，优先 `trace.md` 的 `## 验证记录` 或 `## 验证摘要`。
- `/opsx-apply`：完成态 Workflow Sync 前确认 Change 内存在交付验证来源，不以 tasks 全勾、Workflow Sync 成功或治理日志替代。
- `/opsx-archive`：归档复核按“证据必有，文件不固定”检查来源，接受非空验证章节、显式 `acceptance_refs` 或可选证据文件。
- 文档治理与 API 索引：固化需求中心卡片识别口径，明确 `acceptance.md` / `verification.md` 为可选入口。

## 影响范围

- 影响 `.agents/skills/spec-opt/SKILL.md`
- 影响 `.agents/skills/opsx-apply/SKILL.md`
- 影响 `.agents/skills/opsx-archive/SKILL.md`
- 影响 `rules/document-governance.md`
- 影响 `docs/03-api-index.md`
- 影响 `openspec/changes/unify-change-delivery-evidence-source/`
- 影响 `iterations/change/sprint-007/sprint.yaml`

## 更新文件

- `.agents/skills/spec-opt/SKILL.md`
- `.agents/skills/opsx-apply/SKILL.md`
- `.agents/skills/opsx-archive/SKILL.md`
- `rules/document-governance.md`
- `docs/03-api-index.md`
- `docs/spec-logs/CHANGELOG.md`
- `docs/spec-logs/20260915090702-governance-change-delivery-evidence-source.md`
- `openspec/changes/unify-change-delivery-evidence-source/**`

## 验证结果

已通过：

- `python scripts/validate-change-identity.py --new-id unify-change-delivery-evidence-source`
- `python scripts/validate-sprint-selection.py --sprint sprint-007`
- `python scripts/sync-workflow-status.py --event opsx.start --change unify-change-delivery-evidence-source --sprint auto`
- `python scripts/sync-workflow-status.py --event opsx.progress --change unify-change-delivery-evidence-source --sprint auto`
- `python scripts/validate-agent-context-budget.py`
- `python scripts/validate-openspec-language.py --change unify-change-delivery-evidence-source --residual-report`
- `python scripts/validate-directory-structure.py`
- `openspec validate unify-change-delivery-evidence-source`
- `python scripts/validate-sprint-scope.py sprint-007 --item unify-change-delivery-evidence-source`
- `python scripts/sync-workflow-status.py --event opsx.apply --change unify-change-delivery-evidence-source --sprint auto`
- `PYTHONPATH=src/backend python -c "... ChangeIndex ..."`：需求中心识别 `trace.md` 的 `## 验证记录` 后，交付验证来源与归档动作阻断原因均为 `None`。

AI Usage 已运行：

- `python scripts/extract-ai-usage.py --post-command-hook --workflow-event opsx.apply --change unify-change-delivery-evidence-source --sprint sprint-007 --json`：warning，`usage_mode: unavailable`，`command_run_count: 0`，未生成 Sprint snapshot；不阻断主流程。

业务测试不适用：本次不修改 `src/` 业务代码、API、DB、Web、客户端生成物或部署配置。

## API / DB / Web / 客户端 / 管理端 / Orval / Docker Compose 影响

不适用。本次只调整治理技能、规则、OpenSpec 契约和 API 文档说明，不修改业务 API、数据库、Web 实现、管理端、客户端生成物、Orval 配置或 Docker Compose。

## 后续建议

后续可评估为需求中心增加更细的提示文案，将“未找到交付验证记录”说明为“请在 Change 内添加验证记录、验证摘要或 acceptance_refs”，避免误解为必须补固定文件。
