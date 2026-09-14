---
purpose: 产品数据采集与链路观测标准
content: 行为事件、请求日志、任务链路、流程节点、脱敏、保留周期和治理门禁
source: apply-tilesfst-data-collection-governance
update_method: 数据采集、链路观测、日志审计、Task Trace、请求封装或保留周期规则变化时同步更新
created_at: 2026-09-12 17:20:59
updated_at: 2026-08-27 00:27:55
owner: MoonBox 产品团队
---

# 产品数据采集与链路观测标准

本文档定义 MoonBox 产品数据采集与链路观测的治理口径。它是设计与验收标准，不代表当前已存在全部数据表或业务实现；涉及 API、DB、Web、管理端、对象存储、Agent Workflow、日志审计、行为埋点、Task Trace 或请求封装的变更，必须在 REQ、Change、Sprint 或验收材料中声明适用层级、N/A 原因和验证摘要。

MoonBox 当前启用范围为 Web 端、管理后台、REST API、SQLite/MySQL 兼容路径、MinIO/S3 兼容对象存储、Agent Workflow 和发布部署治理。微信小程序、移动端和桌面端未启用，默认不纳入本标准落地范围；若未来启用，必须通过独立 REQ/OpenSpec 扩展。

## 1. 四层模型

```text
usage_events
  -> request_logs
      -> task_traces
          -> task_trace_spans
```

| 层级 | 事实源 | MoonBox 语义 |
|---|---|---|
| 行为事件 | `usage_events` | Web 端或管理后台的页面访问、按钮点击、搜索筛选、表单提交、上传、发布、审批等可命名行为。 |
| 请求日志 | `request_logs` | 后端业务 API 的请求摘要、状态、耗时、调用端、操作者和服务端可信 `request_id`。 |
| 任务链路 | `task_traces` | 长耗时、多步骤、批量、异步、对象存储、外部依赖或 Agent Workflow 类操作的总体链路。 |
| 流程节点 | `task_trace_spans` | 任务内部关键步骤，例如校验、持久化、对象存储读写、外部调用、Agent 节点执行、结果汇总。 |

所有业务 API SHOULD 具备请求日志；Task Trace 按分级覆盖。行为事件采集失败、请求日志写入失败或 Task Trace 写入失败不得阻断主业务流程，但必须保留错误摘要或降级记录，避免静默丢失。

## 2. 入口类型

### 2.1 界面触发入口

```text
用户行为
  -> 客户端生成 behavior_trace_id / behavior_event_id
  -> 上报 usage_events
  -> 业务 API 携带 behavior_trace_id / behavior_event_id
  -> 后端生成 request_id 并写入 request_logs
  -> 任务类请求写入 task_traces / task_trace_spans
```

规则：

- 同一次用户行为触发多个 API 请求时，共享同一个 `behavior_trace_id`。
- `behavior_event_id` 标识单条行为事件。
- `parent_behavior_event_id` 用于请求日志回指来源行为事件。
- `request_id` 由后端生成，是服务端可信单次请求 ID；客户端传入值不得覆盖。
- 行为采集失败不得阻断主业务流程。

### 2.2 直接 API 或后台入口

```text
脚本 / 内部服务 / API 客户端 / 后台任务
  -> 不伪造 usage_events
  -> 后端生成 request_id 并写入 request_logs
  -> 任务类请求或后台任务写入 task_traces / task_trace_spans
```

规则：

- 直接 API 调用允许 `behavior_trace_id` 和 `parent_behavior_event_id` 为空。
- 后台任务没有来源 HTTP 请求时，`task_traces.parent_request_id` 允许为空，但必须保留 `task_trace_id`、`task_type`、`task_name` 和节点信息。
- Agent Workflow 类任务必须能关联 workflow、node、run 或等价执行上下文，不得把完整 Prompt、密钥、客户原文或本机路径写入 metadata。

## 3. 字段语义与可信边界

| 字段 | 生成方 | 语义 | 可信边界 |
|---|---|---|---|
| `behavior_trace_id` | 客户端 helper | 一次用户行为链路 ID。 | 客户端字段，仅用于归因和排障；不得作为认证、授权、审计身份或租户隔离依据。 |
| `behavior_event_id` | 客户端 helper | 单条行为事件 ID。 | 客户端字段，必须校验长度、字符集和格式。 |
| `parent_behavior_event_id` | 后端从请求头或上下文提取 | 请求来源行为事件 ID。 | 仅用于回指行为事件；缺失时允许为空。 |
| `request_id` | 后端 middleware | 服务端可信单次请求 ID。 | 可信请求日志主追踪 ID；客户端值不得覆盖。 |
| `client_request_id` | 客户端请求封装 | 客户端侧请求标识。 | 仅用于辅助排障；不得作为服务端可信身份或权限依据。 |
| `task_trace_id` | 后端 Task Trace helper | 任务链路 ID。 | 后端生成或后端校验后接受；不得信任未校验客户端值。 |

客户端传入链路字段必须做长度、字符集和格式校验。非法、超长或疑似包含敏感值的字段应被忽略，或按 API 错误规范返回文档化错误。

## 4. 最小数据结构

本标准定义最小字段语义。物理表、索引、迁移、枚举实现和归档策略必须通过对应 REQ/OpenSpec、SQLite/MySQL schema、迁移和 `docs/04-database-design.md` 落地。

### 4.1 `usage_events`

建议最小字段：

- `id`
- `behavior_trace_id`
- `behavior_event_id`
- `event_name`
- `event_category`
- `client_type`
- `page_path`
- `page_code`
- `session_id`
- `actor_user_id`
- `actor_role`
- `properties`
- `result`
- `created_at`

`event_name` 必须来自稳定事件字典，不得直接拼接临时按钮文案或用户输入。`properties` 只能保存脱敏摘要，禁止完整请求体、响应体、Token、密钥、真实客户敏感数据和本机绝对路径。

### 4.2 `request_logs`

建议最小字段：

- `id`
- `request_id`
- `behavior_trace_id`
- `parent_behavior_event_id`
- `client_request_id`
- `method`
- `path`
- `route_template`
- `status_code`
- `result`
- `duration_ms`
- `client_type`
- `actor_user_id`
- `actor_role`
- `resource_type`
- `resource_id`
- `metadata`
- `created_at`

`metadata` 只保存错误码、分页、对象类型、结果数量、脱敏错误摘要等安全 JSON。不得保存 Authorization、Cookie、完整请求体、完整响应体、数据库 DSN、对象存储完整内部 key 或真实客户敏感数据。

### 4.3 `task_traces`

建议最小字段：

- `id`
- `task_trace_id`
- `parent_request_id`
- `task_type`
- `task_name`
- `status`
- `started_at`
- `finished_at`
- `duration_ms`
- `actor_user_id`
- `client_type`
- `metadata`
- `error_code`
- `error_message`
- `created_at`

MoonBox 的 `task_type` 可以覆盖上传、导入导出、批量处理、发布、对象存储操作、Agent Workflow 执行、知识图谱同步、产品手册生成、镜像构建或升级计划验证等任务类别。

### 4.4 `task_trace_spans`

建议最小字段：

- `id`
- `task_trace_id`
- `span_id`
- `parent_span_id`
- `span_name`
- `node_label`
- `sequence`
- `status`
- `started_at`
- `finished_at`
- `duration_ms`
- `metadata`
- `error_code`
- `error_message`
- `created_at`

底层字段可使用 `span` 命名；面向中文产品、管理端和验收表达统一称为“流程节点”。

## 5. 覆盖与 N/A 规则

触发以下任一范围时，REQ、Change、Sprint 或验收材料必须声明 `product_data_collection_observability`：

- API 请求头、响应字段、错误码、OpenAPI、Orval 或客户端请求封装变化。
- 数据库表、字段、索引、迁移、保留周期、脱敏字段或链路查询路径变化。
- 日志审计、行为埋点、请求日志、Task Trace、流程节点或观测仪表变化。
- 上传、导入导出、批量处理、发布、对象存储、Agent Workflow、长耗时或多步骤操作变化。

固定声明至少包含：

```yaml
product_data_collection_observability:
  status: applicable | not_applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
    - task_trace_spans
  reason: "<适用或不适用的具体原因>"
  validation: "<已完成或计划完成的验证摘要>"
```

若 `status: not_applicable`，`reason` 必须说明为什么不影响 API、DB、请求日志、行为事件、Task Trace 或端请求封装；不得只写“无”“不涉及”或 “N/A”。

## 6. Task Trace 分级覆盖

满足以下任一条件的接口或任务 SHOULD 进入 Task Trace 候选清单；影响关键数据、安全、发布、审批或 Agent Workflow 的高风险操作 MUST 优先接入：

| 条件 | MoonBox 示例 |
|---|---|
| 长耗时 | 大文件上传处理、产品手册生成、镜像构建、复杂知识图谱同步。 |
| 多步骤 | 空间申请审批、需求流转、OpenSpec Change 应用、发布准备。 |
| 批量 / 异步 | 批量归档、批量同步、导入导出、后台 worker。 |
| 外部依赖 | MinIO/S3、外部模型服务、远端 Git/文档站点、第三方 API。 |
| 失败需定位节点 | 单条请求日志无法说明失败阶段、慢节点或部分成功明细。 |
| 高风险写操作 | 权限、空间成员、发布状态、审计、真实环境配置或数据库升级。 |

普通简单查询或低风险写操作可以只保留 `request_logs`，但设计或验收材料必须说明不接入 Task Trace 的理由。

## 7. 数据保留周期

默认保留周期：

| 数据 | 默认周期 | 处理方式 |
|---|---:|---|
| `request_logs` 明细 | 90 天 | 超期删除或匿名化。 |
| `usage_events` 明细 | 180 天 | 超期删除或匿名化。 |
| `task_traces` / `task_trace_spans` 明细 | 90 天 | 超期删除或匿名化。 |
| 聚合数据 | 1 年 | 可用于长期趋势分析。 |

调整保留周期必须记录原因、影响范围、审批依据、存储成本、排障窗口、隐私和合规影响。不得为了长期趋势分析无限期保留敏感明细。

## 8. 安全与脱敏

禁止采集、持久化或展示：

- Authorization、Cookie、Token、密码、真实密钥。
- 数据库 DSN、MinIO/S3 AccessKey 或 SecretKey。
- 完整请求体、完整响应体、完整 Prompt、完整模型输出。
- 本机绝对路径、用户主目录、系统用户名。
- 完整内部对象 key、未授权对象存储地址。
- 真实客户敏感数据、个人身份信息和未经授权的业务原文。

前端脱敏只能作为展示优化。后端持久化前的敏感字段过滤、长度截断和安全 JSON 序列化才是安全边界。

## 9. 验收清单

涉及本标准的变更验收至少检查：

- 行为事件字典、事件名、分类和禁止属性。
- 前端或管理端请求封装是否生成并透传链路字段。
- 后端是否生成可信 `request_id` 并记录请求摘要。
- Task Trace 是否按分级标准接入或给出具体 N/A 原因。
- metadata 是否脱敏、截断并避免保存完整 payload。
- API、DB、OpenAPI、Orval、测试和文档是否同步。
- 保留周期、归档或匿名化策略是否声明。

## 10. 相关事实源

- `docs/standards/task-trace-coverage.md`
- `docs/standards/api-governance.md`
- `docs/03-api-index.md`
- `docs/04-database-design.md`
- `rules/api.md`
- `rules/database.md`
- `rules/testing.md`
- `scripts/validate-product-data-observability.py`

## Capture 实现映射（BUG-0014）

Capture沿用ChatRoute：请求层物理表为chat_request_logs；Web标记X-Chat-Client=web时写governance.capture至usage_events，仅允许operation_id关联属性。直接API不模拟页面行为。任务类型governance_application以governance前缀关联操作ID，节点沿用queued/applying/prepared/recovering/applied/conflict/recovery_blocked阶段，详细逐文件阶段保留在私有操作记录。沿用请求/已完成任务90天、行为180天保留清理；未终态恢复证据不自动清理。采集故障降级，表单正文、凭证和本机路径不得进入这些事件。
