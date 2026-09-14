---
bug_id: BUG-0014-requirement-center-capture-not-persisted
created_at: 2026-09-11 19:02:39
updated_at: 2026-09-14 09:25:34
acceptance_status: passed
related_requirement: REQ-0012-frontend-requirement-center
---

# 回归验收

## 验收范围

REQ 与 BUG 两种创建入口都需验证。使用隔离测试项目和合成数据，记录项目别名、版本、角色与结果；不修改真实生产数据。以下AC已由自动回归和隔离环境真实观察验证，生产环境部署与用户最终签收不在本次通过声明中。

| 编号 | 场景与操作 | 通过条件 | 验证方式 | 状态 |
|---|---|---|---|---|
| AC-001 | 分别提交 REQ 与 BUG，有标题和描述 | 服务端返回完整唯一 ID；对应 plan 目录、capture、trace、注册表和 CHANGELOG 均存在且状态 captured、路径与编号一致 | 隔离项目 API 集成检查真实文件，并验证前端使用返回结果 | pass |
| AC-002 | 填写描述、优先级、负责人、来源，包含中文和换行 | 有效字段在持久化文档中保留，非法值得到明确拒绝；空标题不产生文件 | 字段往返与输入校验测试 | pass |
| AC-003 | 创建成功后完整刷新、离开后重新进入 | 同一 ID 与内容仍可读取，文档可打开，无重复卡片 | 真实浏览器加服务端重新读取 | pass |
| AC-004 | 两个客户端同时创建同类型条目 | ID 不冲突、不覆盖旧文档，next_id 与实际分配一致 | 隔离后端并发测试 | pass |
| AC-005 | 双击、超时后重试同一次提交 | 按设计的去重或幂等策略返回可解释结果，不静默重复或覆盖 | API 重试及前端提交状态测试 | pass |
| AC-006 | 分别注入目录、文档、注册表或索引写入失败 | 不返回成功；没有不可恢复的半成品或错误编号状态；重试与恢复有明确结果，旧条目不受损 | 隔离文件系统故障注入与恢复验证 | pass |
| AC-007 | 接口拒绝、网络失败或项目切换时提交 | 无虚假成功；输入保留，可重试；结果归属原授权项目，不污染新项目卡片 | 前端失败、异步切换测试 | pass |
| AC-008 | 无写权限、跨项目、伪造项目标识或危险路径输入 | 服务端拒绝越权/路径逃逸，未经授权的目录与文件无变动；错误信息不泄漏本机路径 | 安全集成测试 | pass |
| AC-009 | 创建成功和失败分别观察请求 | 请求可通过 request_id 关联到脱敏日志，行为关联字段按标准传递；无表单原文、凭证或本机路径泄漏 | API 与观测检查 | pass |
| AC-010 | 检查完整交付与治理边界 | API 文档、OpenAPI、客户端生成物与测试一致；创建仅 captured，不自动评审、入 Sprint 或建 Change | 契约与治理状态验证 | pass |

## 观测与边界说明

结构化 `product_data_collection_observability` 声明见同目录 `bug.md`；本文件以 AC-009 承接验证。

依据 `docs/standards/product-data-collection-observability.md`。DB schema、对象存储和部署拓扑当前没有已确定的调整；本缺陷以项目文件持久化为目标。若设计引入数据库记账、异步任务或 Agent Workflow，补充相应 affected_layers、Task Trace 分级与测试后再验收，不能直接视为不适用。

此修复针对持久化交互，不涉及参考稿视觉复刻；若 Change 扩展为视觉改版，再按 UI 参考稿治理补充契约与证据。

## 真实观察补证操作

用于修复验收及部署影响确认，不阻断当前代码根因确认：

1. 在隔离项目记录环境、版本与账号角色，Network 勾选 Preserve log。
2. 用合成内容分别创建 REQ/BUG，记录请求 method、path、status、request_id 和脱敏结果摘要。
3. 核对目标项目四类落盘产物：目录、文档、注册表、索引；记录存在性和 ID/状态一致性。
4. 完整刷新页面并打开文档，记录是否恢复；错误时仅保留相关 Console 摘要。
5. 返回格式：`环境；版本；角色；类型；请求方法/路径/状态/request_id；完整ID；文件一致性；刷新结果；错误摘要`。项目用别名，不提供凭证、真实客户数据或本机绝对路径。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-14 09:25:34
accepted_by: workflow-sync
source_change: fix-requirement-center-capture-persistence
source_sprint: sprint-005
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 本轮验证证据

SQLite Capture/writer 21 passed；共享ChatRoute 31 passed/1 skipped；MySQL 8.2.0矩阵34 passed；Vitest79 passed；TypeScript与Vite构建通过；真实浏览器REQ/BUG创建、刷新、文档及1440/390焦点通过；临时Compose权限通过。

逐AC实现与用例映射、截图和文件清单位于Change trace及evidence/browser-observed.json；evidence/observability-observed.json记录4次真实创建请求、3条Web行为（含一次503）、3条任务链及21节点，直接API已确认不新增页面事件。目录故障时recovery_blocked保护旧文档并保留恢复镜像；自动进程中止恢复及外部冲突分开验证。全库Design System遗留106项，当前Capture范围0项，未修改无关UI。


## 本轮部署返修验收

补充检查：当前部署加载治理服务/私有目录；GET就绪与真实提交二次校验；controller过期/绑定变化拒绝，重启恢复；continuous不依赖维护窗口且不开放其他写动作；1440/390提示和按钮状态。后端合并26项与前端80项回归通过，当前容器健康与重启就绪已观察。用户登录后在当前部署真实创建REQ-0027-capture与BUG-0016-capture；整页刷新后均保留在采集池，两份capture.md可从页面打开且描述完整。文件系统交叉核对两套capture.md、trace.md、注册表与CHANGELOG均已持久化，status=captured且未进入Sprint/开发。两条明确标记的部署验收记录保留。

## Capture 类型分级返修

REQ仅选择并保存priority P0/P1/P2/P3；BUG选择并保存五档severity。切换保留各自选值，API拒绝缺失/混用/非法等级，各事实源一致。历史记录不批量迁移。本轮验证证据见Capture Change trace的分级返修记录。

## 弹窗与说明返修

Capture桌面宽度840px，REQ支持P0-P3；BUG中文标签致命/严重/高/中/低映射blocker/critical/high/medium/low。共用说明支持Hover、键盘聚焦、Escape及触屏选择后持续说明。API、工作流分级校验与规范一致支持P3。 验证证据见关联Change trace。

## 提示去重返修

移除分级Hover/焦点浮层，只保留下方当前选中说明和原生键盘选择；ready成功状态不渲染文案及容器，检查中/异常提示、刷新和提交二次校验保留。 覆盖此前浮层交互，最新证据见Change trace。
