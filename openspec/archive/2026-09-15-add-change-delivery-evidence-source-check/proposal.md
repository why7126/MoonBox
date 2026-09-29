---
created_at: 2026-09-15 09:38:43
updated_at: 2026-09-15 09:38:43
---

# 提案：新增 Change 交付验证来源校验脚本

## 背景

需求中心卡片已经按 Change 内交付验证来源决定验收中归档入口是否可用。近期多个 applied Change 因 `trace.md` 存在验证材料但标题不被识别，仍展示“验收来源待核实：未找到交付验证记录”。人工返修后还需要一个脚本化门禁，避免新的 applied Change 再次遗漏可识别验证来源。

## 变更内容

- 新增 `scripts/validate-change-delivery-evidence.py`。
- 脚本默认扫描所有 active applied Change，复用需求中心 `ChangeIndex.acceptance_source_reason()` 识别口径。
- 支持 `--change <change-id>` 聚焦校验和 `--json` 机器可读输出。
- 同步 `/opsx-archive` 归档复核说明和文档治理规则，归档前可用该脚本验证目标 Change。
- 写入治理日志和 OpenSpec delta spec，固化该脚本作为交付验证来源门禁。

## 影响范围

- `scripts/validate-change-delivery-evidence.py`
- `.agents/skills/opsx-archive/SKILL.md`
- `rules/document-governance.md`
- `docs/spec-logs/`
- `openspec/archive/2026-09-15-add-change-delivery-evidence-source-check/`
- `iterations/archive/sprint-007/sprint.yaml`

本 Change 不修改业务 `src/`、API、DB、Web UI、OpenAPI、Orval、Docker Compose、部署配置或权限边界。

## 验收标准

- 脚本能扫描 active applied Change，并在缺少需求中心可识别验证来源时返回非零退出码。
- 脚本能用 `--change` 聚焦目标 Change，且对已补齐验证来源的 Change 返回通过。
- `/opsx-archive` 与文档治理规则明确归档前可运行该脚本。
- 治理日志写入 `docs/spec-logs/` 并更新索引。
- OpenSpec、目录结构、上下文预算、脚本自身和 Workflow Sync 校验通过。
