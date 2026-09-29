---
created_at: 2026-09-15 00:02:17
updated_at: 2026-09-15 00:11:09
owner: MoonBox 产品团队
source_bug: BUG-0018-standalone-change-acceptance-source-unverified
acceptance_status: passed
---

# 验收标准

## 功能验收

- [x] AC-001：当独立 Change trace 存在非空 `## 验证摘要` 章节时，需求中心卡片不展示“验收来源待核实：未找到交付验证记录”。
- [x] AC-002：当独立 Change trace 存在非空 `## Validation Log` 章节时，需求中心卡片不展示“验收来源待核实：未找到交付验证记录”。
- [x] AC-003：既有来源继续有效，包括非空 `acceptance.md`、非空 `verification.md`、非空 `## 验证记录`、非空 `## 验收记录`、非空 `## 验证结果` 和非空 `## 验收结果`。
- [x] AC-004：显式 `acceptance_refs` 的无效、越界、缺失或空文件继续展示具体待核实原因，不回退到其他来源掩盖错误。
- [x] AC-005：验收来源存在不等于自动验收通过；tasks 全勾、`applied` 状态或文件存在不得单独推断归档可通过。
- [x] AC-006：对 `refresh-issue-index-after-archive-promotion`、`enhance-workflow-sync-current-status-block` 或等价合成样本，页面卡片不再误报“未找到交付验证记录”。

## 验证记录

| 时间 | 验证 | 结果 |
|---|---|---|
| 2026-09-15 00:11:09 | `uv run pytest src/backend/tests/test_change_visibility.py::test_standalone_action_uses_actual_document_gates src/backend/tests/test_change_visibility.py::test_change_delivery_trace_headings_are_evidence_sources src/backend/tests/test_change_visibility.py::test_change_delivery_sources_and_explicit_reference_boundaries src/backend/tests/test_change_visibility.py::test_trace_generic_heading_is_not_a_business_title -q` | 22 passed，覆盖新增 `验证摘要`、`Validation Log`、`实施与验证记录`、既有来源、显式引用边界和业务标题过滤。 |

补充说明：`uv run pytest src/backend/tests/test_change_visibility.py -q` 当前存在 1 个无关失败，失败用例为 `test_document_audit_and_collection_failure`，证据显示 request log/audit 写入不可用；该路径不由本 Change 修改，未纳入本轮修复范围。

## 不适用说明

- API 路径、请求字段和响应字段未变化；仅修正既有 `disabled_reason` 的服务端计算语义，因此不需要更新 OpenAPI、Orval 生成物或 `docs/03-api-index.md`。
- 该缺陷为局部标题白名单漏判，根因和回归已在 BUG 与 Change 文档中闭环；暂不新增 `docs/knowledge-base/incidents/` 长期事故沉淀。
