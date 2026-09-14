---
change_id: add-ui-reference-replication-governance
change_type: update
status: archived
lifecycle_stage: archive
sprint: sprint-004
source_requirement: null
source_bug: null
owner: MoonBox 产品团队
created_at: 2026-09-01 14:23:52
updated_at: 2026-09-13 23:45:17
---

# Trace

## 变更记录

- 2026-09-01 14:23:52：创建纯治理 Change，目标是建立 UI 参考稿复刻治理流程，避免 UI 一对一复刻退化为逐元素问答返修。

## 证据摘要

本次治理来源于 REQ-0023 产品工作台现代 Ops 视觉升级的验收复盘：实际返修过程中，多轮调整集中在九阶段看板列头、空列、卡片、标签、新建 Capture 按钮、sticky 边界和指标卡。问题不是单个 `opsx-modify` 流程，而是参考稿复刻缺少前置反向工程、组件级契约、selector 映射和批次验收。

## 影响面

- API：不适用，未修改接口契约。
- DB：不适用，未修改数据结构。
- Web：治理流程影响后续 Web UI Change，但不修改本轮业务代码。
- 管理端：治理流程影响后续后台 UI 对齐任务，但不修改本轮业务代码。
- 客户端生成：不适用。
- 部署：不适用。

## 验证摘要

- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：未通过；报告根目录存在既有未登记目录 `.vite`，非本次治理变更新增。
- `openspec validate add-ui-reference-replication-governance`：通过。
- `python scripts/validate-sprint-scope.py sprint-004`：通过。
- `python scripts/sync-workflow-status.py --event opsx.apply --change add-ui-reference-replication-governance --sprint auto`：通过，解析到 `sprint-004`，Updated 2，Errors 0。
- AI Usage Hook：已运行，返回 `warning/unavailable`，原因是当前会话无可持久化 command-run token 事件。

## 身份与归档状态纠正（2026-09-13 16:00:41）

原初建与强化均使用 `add-ui-reference-replication-governance`；本次保留初建身份，2026-09-02 强化独立为 `enhance-ui-reference-replication-action-matrix`。本记录是治理纠正时间，不代表实际归档时间。原 trace 状态为 applied，强化另有 lifecycle_stage: change；现按既有归档目录同步 archived/archive。原实施与验证记录保留，旧 ID 命令按当时身份解释。修正前文件校验和见 `openspec/archive/2026-09-13-repair-change-identity-uniqueness/evidence/before-sha256.json`。
