---
bug_id: BUG-0017-compose-container-name-suffix-one
title: 容器名不应自动追加 -1 后缀
review_result: approved
reviewed_at: 2026-09-15 00:02:11
reviewed_by: product
severity: medium
hotfix_required: false
created_at: 2026-09-15 00:02:11
updated_at: 2026-09-15 00:02:11
---

# 缺陷评审

## 评审结论

确认修复，评审通过。

## 评审清单

| 检查项 | 结论 | 说明 |
|---|---|---|
| 可复现或根因充分 | 通过 | `root-cause.md` 根因状态为 `confirmed`，证据链包含配置差异与运行态复现，共 5 条证据；根因门禁脚本通过。 |
| 严重等级合理 | 通过 | `medium` 合理；该问题影响 Docker/Compose 运维识别和脚本/文档引用一致性，当前未见服务不可用、数据丢失或安全风险。 |
| 回归验收明确 | 通过 | `acceptance.md` 覆盖主服务、Chat 平台、治理控制器、Chat recovery、配置解析、运行态验证和文档脚本同步。 |
| 是否需 hotfix 路径 | 不需要 | 问题影响部署体验与运维一致性，但当前无生产阻断证据；按常规 Sprint 纳入修复。 |

## 评审依据

- `bug.md` 已描述现象、复现步骤、期望/实际、影响范围和严重等级。
- `root-cause.md` 已确认根因：叠加 Compose 服务缺少显式 `container_name`，导致运行态落回 Compose 默认 `moonbox-<service>-1` 命名。
- `workaround.md` 已提供短期规避：修复前通过 Compose 服务名、label 或 `docker compose ps` 查询定位容器，不把 `-1` 运行态名称写入长期文档或自动化脚本。
- `acceptance.md` 已列出修复验收项，当前验收状态为 `passed`。

## 后续动作

无；本 BUG 已纳入 `sprint-007`，关联 Change 已归档。
