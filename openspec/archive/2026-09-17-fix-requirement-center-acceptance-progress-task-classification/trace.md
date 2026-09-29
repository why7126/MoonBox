---
title: 验收进度分类统计修复追溯
created_at: '2026-09-15 23:08:22'
updated_at: 2026-09-15 23:33:10
change_id: fix-requirement-center-acceptance-progress-task-classification
bug_id: BUG-0023-requirement-center-acceptance-progress-task-classification
status: applied
iteration: sprint-007
execution:
  schema_version: 1
  started_at: 2026-09-15 23:17:53
  completed_at: 2026-09-15 23:33:10
  last_event: opsx.apply
---

# 验收进度分类统计修复追溯

## 来源与边界

来源 BUG-0023-requirement-center-acceptance-progress-task-classification，已评审通过并纳入 `sprint-007`，估算 L=5 人天。根因 confirmed，证据链 8 条，验收标准 13 项。

本 Change 已通过 `/opsx-apply BUG-0023-requirement-center-acceptance-progress-task-classification` 完成实现，修改后端聚合、响应 schema、前端展示、OpenAPI / Orval 生成物、回归测试和长期 API 文档。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - request_logs
  reason: 修改需求中心 context API 响应字段、OpenAPI / 客户端类型和 Web 卡片展示口径；不新增 DB 表、行为事件、Task Trace、流程节点或对象存储写入。
  validation: 实施阶段需验证直接 API 与前端展示一致、响应字段脱敏、OpenAPI / Orval 同步和 request_logs 链路不回归。
```

## 验证记录

实施已完成。需求中心 context 现在从当前关联 Change 的 `tasks.md` 解析三类 checkbox：研发进度来自实施/研发/开发/修复/文档同步章节，测试进度来自回归验证/测试/校验/视觉证据章节，人工验收进度来自人工验收/人工复验/sign-off 章节；`/opsx-modify` 追加的“验收返修”混合章节按单条任务文本归入返修实现、返修验证或人工复验。`acceptance-fixes.md`、`acceptance.md`、`review.md` 与 `trace.md` 文件存在性不进入三类进度分母，前端也不再把缺失人工验收任务推导为 `1/1`。

验证结果：

- `python scripts/validate-root-cause-evidence.py --bug BUG-0023-requirement-center-acceptance-progress-task-classification` 通过，root_cause_status=confirmed，证据 8 条。
- `uv run pytest src/backend/tests/test_governance_board.py::test_acceptance_checks_issue_documents_not_card_display_list` 通过。
- `uv run pytest src/backend/tests/test_governance_board.py src/backend/tests/test_change_visibility.py` 中本 Change 相关三类进度回归通过；另有既存/并行标题投影用例 `test_projection_tracks_unique_proposal_and_archive_ambiguity` 失败，实际提示位于 `drift_warnings` 而旧断言期待 `title_warning`，与 BUG-0023 进度口径无关，未在本 Change 内顺手修复。
- `uv run pytest tests/integration/api/test_requirement_center.py` 通过，20 passed。
- `./node_modules/.bin/vitest run src/requirement-center.test.tsx` 通过，106 passed，覆盖测试 `3/3` 不推导人工验收 `1/1` 的等价前端场景。
- `./scripts/generate-openapi-client.sh` 已成功导出 `src/web/openapi.json`，随后因本机 Corepack `pnpm@12.4.1` shim 缺失提前退出；已使用本地 `src/web/node_modules/.bin/orval --config orval.config.ts` 完成 Orval 8.29.0 客户端生成。
- 直接解析当前 Change 得到研发 `11/11`、测试 `5/5`、人工验收无显式任务；人工验收无任务时不会展示默认完成态。

`docs/knowledge-base/incidents/` 暂不新增事故复盘：本次已在 `docs/03-api-index.md` 沉淀长期口径，且 BUG 文档和 Change trace 已记录根因、证据、修复与残余测试风险。
