---
change_id: fix-standalone-change-acceptance-source
source_bug: BUG-0018-standalone-change-acceptance-source-unverified
source_requirement: REQ-0026-requirement-center-standalone-change-cards
source_sprint: sprint-006
type: fix
status: archived
created_at: 2026-09-15 00:02:17
updated_at: 2026-09-17 08:12:45
owner: MoonBox 产品团队
product_data_collection_observability:
  status: applicable
  affected_layers:
    - api
    - request_logs
  validation: 直接相关 pytest 通过，22 passed；API 契约未变化，请求日志沿用既有脱敏摘要。
execution:
  schema_version: 1
  started_at: 2026-09-15 00:09:27
  completed_at: 2026-09-15 00:16:20
  last_event: opsx.archive
---

# fix-standalone-change-acceptance-source Trace

## 缺陷就绪

| 项 | 结论 | 证据 |
|---|---|---|
| BUG 状态 | ready | `BUG-0018-standalone-change-acceptance-source-unverified` 为 `in_sprint`，迭代 `sprint-006`。 |
| 文档包 | ready | `bug.md`、`root-cause.md`、`workaround.md`、`acceptance.md`、`trace.md` 均存在。 |
| 根因证据 | pass | `python scripts/validate-root-cause-evidence.py --bug BUG-0018-standalone-change-acceptance-source-unverified` 通过，confirmed，证据 6 条。 |
| Change 身份 | pass | `python scripts/validate-change-identity.py --new-id fix-standalone-change-acceptance-source` 通过。 |

## 缺陷分析报告

| 维度 | 摘要 |
|---|---|
| 现象 | 独立 Change 卡片在验收中阶段展示“验收来源待核实：未找到交付验证记录”。 |
| 复现 | 查看 `refresh-issue-index-after-archive-promotion` 或 `enhance-workflow-sync-current-status-block` 的需求中心独立 Change 卡片。 |
| 影响 | 用户会误以为该 Change 没有交付验证记录，降低需求中心验收状态可信度。 |
| 根因分类 | 后端治理聚合标题白名单漏判。 |
| 严重等级 | medium。 |

## 修复边界

- 扩展 trace 验证章节标题识别。
- 不新增独立 Change 创建、编辑、归档执行能力。
- 不改变验收通过判定，只定位验收来源。
- 不修改 `openspec/specs/` 正式规格；归档时由 OpenSpec 合并 delta spec。

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-09-15 00:02:17 | /bug-opsx | proposed | 由 BUG-0018 生成 OpenSpec Change，固化 execution schema v1。 |
| 2026-09-15 00:09:27 | /opsx-apply | in_progress | 启动实现，Workflow Sync 写入执行开始事实。 |

## 验证摘要

| 时间 | 命令 | 结果 | 覆盖 |
|---|---|---|---|
| 2026-09-15 00:11:09 | `uv run pytest src/backend/tests/test_change_visibility.py::test_standalone_action_uses_actual_document_gates src/backend/tests/test_change_visibility.py::test_change_delivery_trace_headings_are_evidence_sources src/backend/tests/test_change_visibility.py::test_change_delivery_sources_and_explicit_reference_boundaries src/backend/tests/test_change_visibility.py::test_trace_generic_heading_is_not_a_business_title -q` | 22 passed | 新增 `验证摘要`、`Validation Log`、`实施与验证记录` 标题识别；复核既有来源、显式引用失败不回退、无来源提示和业务标题过滤。 |

补充验证：`uv run pytest src/backend/tests/test_change_visibility.py -q` 当前有 1 个无关失败，失败用例为 `test_document_audit_and_collection_failure`，报错为 request log/audit 记录未写入；该用例覆盖 chat/request log 观测路径，不由本 Change 修改。

## 文档与生成物同步

- API 路径、请求字段、响应字段和错误码未变化；本次只修正既有 `disabled_reason` 的服务端计算语义。
- OpenAPI、Orval 生成物、DB schema、对象存储、部署配置和 Task Trace 不适用。
- `docs/03-api-index.md` 不适用，原因同上；产品数据采集与链路观测沿用现有 request_logs 脱敏摘要。

## 知识沉淀判断

BUG-0018 属于局部标题白名单漏判，已通过 OpenSpec delta spec、BUG 根因、Change 测试和验收记录闭环；本轮不新增 `docs/knowledge-base/incidents/`。若后续再次出现同类“验证章节表达漂移”，建议再 capture 治理项沉淀通用标题归一化规范。
