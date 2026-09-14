---
purpose: Change 身份唯一性治理日志
created_at: 2026-09-13 16:06:17
updated_at: 2026-09-13 23:45:17
---

# Change 身份唯一性与历史纠正

## 迭代目标

保留初建 add-ui-reference-replication-governance；强化更名为 enhance-ui-reference-replication-action-matrix，消除同 ID 双归档歧义。

## 变更摘要与影响范围

重命名 2026-09-02 归档，更新文档身份、当前 trace 归档状态、Sprint 范围与日志索引；原历史 ID 和验证上下文在纠正说明中保留。修正前逐文件 SHA-256 见本 Change evidence/before-sha256.json。未删除初建或强化内容，未虚构归档时刻。

## 更新文件

- `openspec/archive/2026-09-01-add-ui-reference-replication-governance/trace.md` 与重命名的强化归档。
- `scripts/change_identity.py`、`scripts/validate-change-identity.py`、`scripts/validate-directory-structure.py`、`scripts/archive-change.sh`、`tests/unit/test_change_identity.py`。
- `rules/document-governance.md`、`rules/agent-context-budget.md`、`AGENTS.md`、`docs/README.md`。
- `.agents/skills/` 下 spec-opt、opsx-propose、openspec-propose、req-opsx、bug-opsx、opsx-archive、openspec-archive-change 入口。
- `iterations/change/sprint-004/`、原强化治理日志、治理日志索引、独立 Change 可见性设计中的历史冲突补记。
- `openspec/archive/2026-09-13-repair-change-identity-uniqueness/`。

## 验证结果

- 7 项 unittest 回归通过，包含跨日期重复归档、活动/归档冲突、已归档 ID 创建拒绝、身份不一致，以及归档修改前阻断。
- 实际仓库 ChangeIndex 只读验证：初建与强化分别解析为唯一 archive/done，无 conflict。
- 唯一性脚本、上下文预算、目标 Change strict validate、两项 Sprint scope、bash 语法检查通过。
- 全局中文校验仍被既有 fix-requirement-center-apply-lifecycle-sync 的 6 处英文标题阻断；本 Change 已修正并无剩余命中。
- 目录校验身份部分通过，整体仍被既有根目录 logs 未登记阻断；未改动该运行时目录。
- Workflow Sync：sprint-004，更新 2 项，跳过 7 项，错误 0。
- Sprint 显式容量仍为 30 人天；补登记强化和本次修复各 1 人天后为 32 人天（106.67%），处于容量风险区间而未超过 120% 硬门禁。估算不代表历史实耗。

## API/DB/Web/客户端/管理端/Orval/Docker Compose 影响

全部 N/A：未修改业务代码、接口、schema、请求封装、授权、安全边界或部署。product_data_collection_observability: not_applicable；affected_layers: []；validation：离线脚本测试与真实仓库只读解析。

## 后续建议

归档本次治理 Change 前处理全局中文与目录校验既有失败。未自动创建后续 Issue/Change。

收尾：再次 Workflow Sync 更新 0、跳过 9、错误 0；初建项 Sprint scope 同样通过。AI Usage Hook：warning / unavailable，command_run_count=0，Sprint snapshot skipped；当前未发现可归因的 token_count 事件，不补造用量。初建治理日志的当前归档入口也已纠正。
