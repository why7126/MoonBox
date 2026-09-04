---
change_id: update-markdown-editor-human-edit-permission-matrix
type: update
status: applied
requirement: REQ-0024-markdown-editor-human-edit-permission-matrix
sprint: sprint-004
created_at: 2026-09-04 08:15:46
updated_at: 2026-09-04 08:51:35
source_requirement: issues/requirements/review/REQ-0024-markdown-editor-human-edit-permission-matrix/
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
  reason: "本 Change 影响 Web 端文档编辑行为、REST API 响应字段、保存接口授权校验和系统治理链路写入边界，需要记录人工编辑、checkbox-only 操作、越权拒绝和系统修改入口的脱敏摘要。"
  validation: "已验证前端能力对象驱动、后端保存授权、越权保存错误、task toggle 差异校验、脱敏操作日志、OpenAPI 合约导出、聚焦后端测试、前端测试、Web 构建、OpenSpec 校验和中文优先校验；当前通用 request_logs 持久化与 usage_events 上报尚未在项目内落地，未在本 Change 扩展数据库表。"
---

# Change Trace

## 来源

- REQ：REQ-0024-markdown-editor-human-edit-permission-matrix
- Sprint：sprint-004
- Change 类型：update
- 相关父需求：REQ-0021-markdown-editor-vditor-enhancement

## Requirement Readiness Report

| 项 | 结果 | 说明 |
|---|---|---|
| Readiness | Ready | requirement、user-stories、business-flow、acceptance、trace、review 齐全 |
| 评审门禁 | Passed | REQ trace 状态为 `in_sprint`，已纳入 `sprint-004` |
| Prototype Gate | N/A | REQ-0024 无 `prototype/` 目录 |
| UI Explore Gate | N/A | 无 prototype，不需要策略选择 |
| 产品数据采集与链路观测 | applicable | 覆盖 Web 行为、API 响应/保存授权、请求日志和 Task Trace 候选 |

## 影响分析

```yaml
impact:
  backend: true
  web: true
  miniapp: false
  admin: false
  database: false
  storage: false
  api: true
capabilities:
  new: []
  modified:
    - web-catalog-requirement-center
    - web-catalog-requirement-center-real-data
```

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-09-04 08:51:35 | opsx.modify | 验收返修：修复 workflow demo/fallback 文档能力仍沿用旧 `capture.md` 逻辑，导致规划中 `requirement.md` 显示只读的问题。 |
| 2026-09-04 08:39:40 | opsx.apply | 已实现 Markdown 文档能力矩阵、后端授权校验、验收中 `tasks.md` checkbox-only 保存、前端能力对象驱动渲染、脱敏操作日志、API 文档与 OpenAPI 合约同步；等待 Workflow Sync 回填 Issue/Sprint 状态。 |
| 2026-09-04 08:15:46 | req.opsx | 创建 OpenSpec Change 文档，等待 Workflow Sync 回填。 |

## 验收返修记录

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| Image #1 | 需求中心 workflow demo，规划中阶段，`DEMO-REQ-PLANNING-READY · requirement.md` 抽屉 | REQ-0024 人工编辑能力矩阵 | 规划中 REQ 的 `requirement.md` 应显示编辑/分栏/Vditor/保存能力 | footer 显示“当前阶段只读”，未出现编辑入口 | demo/fallback 文档能力未按阶段矩阵生成 | 用户截图、代码路径、前端测试 | 本次修复 | 用户提供截图；`src/web/src/pages/catalog/RequirementCenterPage.tsx` |

### 根因与调整

| 项 | 结论 |
|---|---|
| 根因状态 | confirmed |
| 根因证据 | 截图显示规划中 demo `requirement.md` 只读；代码中 `workflowDemoDocuments()` 仅按 `editableCapture && capture.md` 生成可编辑能力，未按阶段矩阵处理规划中主文档。 |
| 调整内容 | 新增前端 `capabilityForStage()`，demo/fallback 文档能力与阶段流转临时文档统一按对象类型、阶段和文档名生成；workflow demo 可从 `DEMO-*` ID 推断阶段和类型。 |
| 影响范围 | Web 端 workflow demo 与无后端 `documentEntries` 时的 fallback 能力生成；后端能力模型、API 合约和权限边界不变。 |
| REQ 子文档一致性扫尾检查 | 无需更新 `requirement.md`、`business-flow.md`、`user-stories.md`、`acceptance.md`，原因是验收标准未变化，返修只纠正 demo/fallback 实现偏差。 |

## 实现摘要

- 后端新增 `RequirementCenterDocumentCapability`，并在需求中心文档列表中返回 `readable`、`human_editable`、`ai_mutable`、`task_toggle_only` 与 `reason`；兼容字段 `editable` 等价于 `human_editable`。
- 需求中心服务统一计算 REQ、BUG、OpenSpec Change 与已生效规格边界的人工编辑能力；`trace.md` 人工始终只读，系统治理链路仍可按既有命令写入。
- 新增 Change 文档读取、完整保存和 `tasks.md` 勾选专用 API；待开发阶段仅允许当前 Change 下 `proposal.md`、`spec.md`、`design.md`、`tasks.md` 全文编辑，验收中 `tasks.md` 只允许 checkbox 状态变化。
- 前端 Markdown 抽屉改为能力对象驱动：可编辑文档保留 Vditor/分栏/保存/脏状态保护，checkbox-only 文档仅暴露任务勾选操作，只读文档展示受限原因。
- API 侧记录稳定脱敏操作事件：`requirement_center.document.open`、`requirement_center.document.save`、`requirement_center.document.task_toggle`、`requirement_center.document.reject`，metadata 仅包含对象 ID、文档名、操作类型、结果、错误码和脱敏原因。

## 产品数据采集与链路观测结论

| 项 | 结论 |
|---|---|
| usage_events | 本 Change 定义了稳定事件名与脱敏属性边界；项目当前无通用前端 usage_events 上报仓储，本次不新增数据库表。 |
| request_logs | API 侧新增脱敏操作日志，覆盖打开、全文保存、checkbox-only 保存和拒绝分支；不记录 Markdown 正文、请求/响应体、Prompt、Authorization、Cookie、本机路径或内部堆栈。 |
| task_traces | `tasks.md` 勾选差异校验为单次同步低风险文本标记校验，不涉及长耗时、多步骤、外部依赖或异步批处理，本 Change 不接入 Task Trace。 |
| request_id | 当前项目仅有 admin 审计类 request_id，未落地通用业务 API request_logs middleware；本 Change 不扩展 DB schema，后续如建设通用观测链路需独立 REQ/OpenSpec。 |

## 验证摘要

| 命令 | 结果 |
|---|---|
| `uv run pytest tests/integration/api/test_requirement_center.py` | 通过，16 passed |
| `corepack pnpm@11.2.2 --dir src/web exec vitest run src/requirement-center.test.tsx --reporter=dot` | 通过，59 passed |
| `corepack pnpm@11.2.2 --dir src/web build` | 通过，TypeScript 与 Vite 构建成功 |
| `openspec validate update-markdown-editor-human-edit-permission-matrix --strict` | 通过 |
| `python scripts/validate-openspec-language.py` | 通过 |
| `python scripts/validate-sprint-scope.py sprint-004 --item REQ-0024-markdown-editor-human-edit-permission-matrix` | 通过 |

## API / Orval 同步

- 已重新导出 `src/web/openapi.json`。
- 已同步 `docs/03-api-index.md` 的需求中心文档能力、Change 文档读写与 `tasks.md` 勾选专用接口说明。
- 当前仓库缺少 `src/web/orval.config.ts`，且 `src/web/package.json` 未声明 Orval；因此本次仅同步 OpenAPI 合约，不生成 Orval 客户端。

## REQ 子文档一致性检查

| 文档 | 结果 |
|---|---|
| `requirement.md` | 一致，能力模型、阶段矩阵、`trace.md` 只读、待开发 Change 文档和验收中 tasks checkbox-only 均已覆盖。 |
| `acceptance.md` | 一致，功能 AC 已由后端/前端测试覆盖；观测 AC 中通用 request_logs/usage_events 持久化作为项目现状限制写入本 trace。 |
| `trace.md` | 一致，REQ trace 仍保持 `in_sprint`，等待 Workflow Sync 根据 `opsx.apply` 回填 Change 状态。 |
