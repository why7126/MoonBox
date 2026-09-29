---
created_at: 2026-09-15 09:07:02
updated_at: 2026-09-15 09:07:02
---

# 提案：统一 Change 交付验证来源契约

## 背景

需求中心已经允许独立 Change 不生成 `acceptance.md` 或 `verification.md`，但 `/spec-opt` 与 `/opsx-apply` 没有明确要求把验证结果写入 Change 内可识别证据入口，导致纯治理 Change 在 applied 后可能展示“验收来源待核实”。

## 变更内容

- 固化“证据必有，文件不固定”：所有 applied Change 必须在 Change 内保留需求中心可识别的交付验证来源。
- 明确纯治理 Change 不强制生成 `acceptance.md` 或 `verification.md`，优先使用 `trace.md` 的 `## 验证记录` 或 `## 验证摘要`。
- `/spec-opt` 完成治理优化时，必须在 Change `trace.md` 记录可识别验证章节或显式 `acceptance_refs`。
- `/opsx-apply` 完成态同步前，必须确认 Change 内存在可识别交付验证来源。
- `/opsx-archive` 归档前继续复核该证据入口，不用固定文件名替代证据判断。

## 能力影响

### 新增能力

无。

### 修改能力

- `agent-workflow-tooling`：补齐 spec-opt / opsx-apply 对 Change 交付验证来源的写入契约。
- `web-catalog-requirement-center`：明确独立 Change 阶段按钮的验收来源门禁不强制固定文件。

## 影响范围

- `.agents/skills/spec-opt/SKILL.md`
- `.agents/skills/opsx-apply/SKILL.md`
- `.agents/skills/opsx-archive/SKILL.md`
- `rules/document-governance.md`
- `docs/03-api-index.md`
- `docs/spec-logs/`
- `openspec/archive/2026-09-15-unify-change-delivery-evidence-source/`
- `iterations/archive/sprint-007/sprint.yaml`

本 Change 不修改业务 `src/`、API 实现、DB、Web UI、OpenAPI、Orval、Docker Compose 或部署配置。
