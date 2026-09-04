---
purpose: Task Trace 覆盖清单
content: MoonBox 任务链路候选场景、接入优先级、流程节点策略和 N/A 记录要求
source: apply-tilesfst-data-collection-governance
update_method: 任务链路、长耗时流程、批量/异步任务或 Agent Workflow 观测范围变化时同步更新
created_at: 2026-08-27 00:27:55
updated_at: 2026-08-27 00:27:55
owner: MoonBox 产品团队
---

# Task Trace 覆盖清单

通用字段、可信边界、脱敏、保留周期和声明格式见 `docs/standards/product-data-collection-observability.md`。本文只维护 MoonBox 的 Task Trace 候选场景与接入策略。

## 1. 判定标准

满足以下任一条件的接口、脚本或后台任务 SHOULD 进入 Task Trace 候选清单；影响关键数据、安全、发布、审批或 Agent Workflow 的高风险操作 MUST 优先接入。

| 条件 | 示例 |
|---|---|
| 长耗时 | 大文件上传、产品手册生成、镜像构建、复杂知识图谱同步。 |
| 多步骤 | 空间创建/加入审批、需求流转、OpenSpec Change 应用、发布准备。 |
| 跨服务 / 外部依赖 | MinIO/S3、模型服务、远端 Git、Mintlify、第三方 API。 |
| 异步或后台任务 | 导入导出、批量归档、后台同步、计划任务。 |
| 批量处理 | 批量关闭 Sprint、批量归档 Issue/Change、批量同步状态。 |
| 失败需精确定位 | 单条请求日志无法说明失败节点、慢节点或部分成功明细。 |
| 安全审计价值高 | 权限、成员、空间、发布、数据库升级、真实环境配置。 |

## 2. 首批候选清单

| 场景 | 候选接口 / 任务 | 任务类型 | 优先级 | 关键步骤 | 预期流程节点 | 首批结论 |
|---|---|---|---|---|---|---|
| 空间创建与加入申请 | 前台申请、后台审批、状态流转 | `space_application_flow` | P1 | 接收请求、权限校验、申请校验、持久化、通知/状态刷新 | `api_receive`、`auth_check`、`business_validate`、`business_persist`、`state_transition`、`api_response` | 有正式业务 Change 时评估接入 |
| 文件与图片上传 | 管理端/前台上传、对象存储读取回显 | `media_upload` | P1 | 校验、对象存储写入、元数据提取、DB 关联、响应 | `validate_file`、`storage_put_object`、`metadata_extract`、`db_persist`、`api_response` | 对象存储链路变更时优先接入 |
| 需求与 OpenSpec 工作流 | REQ/BUG 状态同步、Change apply、Workflow Sync | `agent_workflow_governance` | P1 | 读取事实源、执行校验、写入治理文档、同步状态、生成复盘 | `load_context`、`validate_scope`、`apply_governance`、`workflow_sync`、`usage_hook` | 治理脚本先以日志/报告声明，运行时实现另走 Change |
| 产品手册生成 | Mintlify 元数据生成、公开安全校验、站点投影 | `usage_docs_generation` | P2 | 读取文档、生成投影、校验导航、安全检查 | `read_docs`、`generate_projection`、`validate_manifest`、`security_check` | 产品手册链路增强时评估接入 |
| 发布与镜像 | release-prepare、image-build、upgrade-plan | `release_operation` | P1 | 版本读取、环境差异、镜像构建、升级计划、回滚检查 | `version_resolve`、`env_diff`、`image_build`、`upgrade_validate`、`rollback_check` | 发布治理变更时优先接入 |
| 知识图谱同步 | 产品知识节点/边同步、批量重建 | `knowledge_graph_sync` | P2 | 输入校验、批量处理、冲突检测、持久化、结果汇总 | `input_validate`、`batch_process`、`conflict_detect`、`db_persist`、`result_summary` | 等正式能力成熟后接入 |

## 3. 接入约束

- 业务实现必须通过统一 helper 或服务封装写入 `task_traces` 和 `task_trace_spans`；路由层不得直接拼 SQL 或绕过脱敏 helper。
- 前端、管理端或子请求传入的链路 ID 只在格式合法时用于归因和排障，不得作为认证、授权、租户隔离或审计身份依据。
- Task Trace 写入失败必须降级，不得覆盖主业务错误。
- metadata 必须经过统一脱敏、截断和安全 JSON 序列化。
- 新增响应字段、请求头、查询参数、存储字段或索引时，必须同步 API 文档、OpenAPI/Orval、数据库设计和测试。

## 4. 后续排期建议

| 后续项 | 建议来源 | 原因 |
|---|---|---|
| 空间申请审批 Task Trace | 新 REQ 或既有空间流程 Change 返修 | 审批流影响权限与空间切换，排障价值高。 |
| 文件上传对象存储 Task Trace | 上传或对象存储增强 Change | 对象存储失败、回显失败和 metadata 脱敏需要节点级证据。 |
| Workflow Sync 执行链路 Task Trace | 治理脚本增强 Change | 目前已有命令复盘和 AI Usage，后续可补运行时链路事实源。 |
| 发布升级 Task Trace | 发布治理增强 Change | 发布、镜像、升级、回滚属于高风险运维链路。 |
