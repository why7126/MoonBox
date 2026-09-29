---
purpose: 记录 Change 交付验证来源校验脚本治理迭代
content: 新增脚本扫描 active applied Change 是否存在需求中心可识别验证来源
created_at: 2026-09-15 09:38:43
updated_at: 2026-09-15 09:38:43
owner: MoonBox 产品团队
---

# Change 交付验证来源校验脚本

## 迭代目标

新增脚本化门禁，扫描 active applied Change 是否存在需求中心可识别的交付验证来源，避免需求中心验收中卡片再次出现“未找到交付验证记录”。

## 变更摘要

- 新增 `scripts/validate-change-delivery-evidence.py`。
- 脚本复用需求中心 `ChangeIndex.acceptance_source_reason()` 识别口径。
- 默认扫描所有 active applied Change，支持 `--change` 聚焦目标和 `--json` 机器输出。
- 同步 `/opsx-archive` 技能和 `rules/document-governance.md`，归档前可运行该脚本。
- 新增 OpenSpec delta spec 固化脚本门禁。

## 影响范围

- 治理脚本：有影响。
- Agent 技能：`opsx-archive` 有影响。
- 文档规则：`rules/document-governance.md` 有影响。
- 业务 API / DB / Web / 客户端 / 管理端 / Orval / Docker Compose：无影响。

## 更新文件

- `scripts/validate-change-delivery-evidence.py`
- `.agents/skills/opsx-archive/SKILL.md`
- `rules/document-governance.md`
- `docs/spec-logs/CHANGELOG.md`
- `openspec/changes/add-change-delivery-evidence-source-check/`
- `iterations/change/sprint-007/sprint.yaml`

## 验证结果

- `python scripts/validate-change-delivery-evidence.py --change add-chat-agent-model-reasoning-selector`：通过。
- `python scripts/validate-change-delivery-evidence.py --json`：通过。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py --change add-change-delivery-evidence-source-check --residual-report`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate add-change-delivery-evidence-source-check --strict`：通过。
- `python scripts/validate-sprint-scope.py sprint-007 --item add-change-delivery-evidence-source-check`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change add-change-delivery-evidence-source-check --sprint auto`：通过。

## 后续建议

后续可将该脚本接入 `/opsx-archive` 的固定前置校验或 CI。
