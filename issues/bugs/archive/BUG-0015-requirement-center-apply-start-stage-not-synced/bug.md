---
bug_id: BUG-0015-requirement-center-apply-start-stage-not-synced
title: 研发启动后需求中心卡片仍停留准备开发态，缺少 apply 启动状态同步
status: done
owner: null
discovered_at: 2026-09-12 17:20:40
created_at: 2026-09-12 17:28:58
updated_at: 2026-09-14 09:00:13
environment: null
related_requirement: REQ-0012-frontend-requirement-center
related_bug: BUG-0014-requirement-center-capture-not-persisted
related_change: null
severity: medium
---

# 缺陷概述

已通过研发前置门禁并开始执行 apply 的条目，在尚未完成第一项任务时仍显示“准备开发态”和“开始修复”。研发执行状态未及时进入治理事实源，Workflow Sync 与需求中心又采用不同的阶段判定口径，使卡片阶段、任务进度和实际执行情况可能不一致。

本条承接 capture 与 bug-explore，按一个研发状态流转缺陷处理。BUG-0014 仅作为复现案例；其 fix-requirement-center-capture-persistence 与 sprint-005 是来源背景，不是本缺陷的修复 Change 或所属 Sprint。

## 现象

- 用户截图中 BUG-0014 卡片位于“准备开发态”，显示“开始修复”和研发 0/16。
- 同期 apply 截图显示 Agent 已开展实现、测试与验收工作。
- 首轮探索读取到该 Change trace 为 提议态、任务为 0/16，后端据此返回 ready-dev。
- 后续 bug-explore 读取时，该背景任务文件已更新为 进行态、16/16。此为另一次文件观察，不表示启动阶段缺口已修复，也不代表当前真实页面状态。

## 复现条件与步骤

1. 准备已完成评审、正式纳入 Sprint 且已创建 Change 的 REQ 或 BUG，任务初始为 0/N。
2. 执行其 opsx-apply，通过前置门禁并正式开始实施；第一项任务尚未满足完成条件时保持 0/N。
3. 打开需求中心，观察卡片所在列、动作名称和研发进度。
4. 对照 Change trace、Issue trace 中关联 Change 状态以及任务清单；记录是否存在实际执行中但 trace 仍为 提议态 的情况。
5. 刷新或重新进入页面，采集 context 响应中的条目阶段与任务数，核对是否仍停留准备开发态。

步骤 1—4 有用户截图、文件与源码证据；步骤 5 的实际部署网络链路尚未验证。环境部署方式、版本及项目选择信息待补充。

## 期望与实际

| 场景 | 期望 | 当前已验证行为 |
|---|---|---|
| 未启动、0/N | 保持准备开发态 | 提议态 映射准备开发态。 |
| 门禁通过并已启动、0/N | 进入研发中，完成数仍为 0 | 缺少启动同步闭环；Sync 仍按零完成数派生 提议态。 |
| 部分任务完成、trace 仍 提议态 | 状态事实源与看板一致反映研发中 | Sync 派生 进行态，看板仍返回 ready-dev。 |
| 全任务勾选、trace 仍 进行态 | 完成门禁通过后统一进入验收阶段 | 合成验证中 Sync 派生 验收态，看板返回 development；仅任务全勾选不足以证明完成门禁通过。 |
| 重复同步与中断恢复 | 保留已启动事实，不退回未启动 | 已启动 0/N 无法由当前任务计数派生逻辑保留；需正式回归。 |

## 证据与根因边界

| 编号 | 类型 | 来源 | 支持的判断 |
|---|---|---|---|
| E1 | screenshot | screenshots/board-ready-dev.png、screenshots/apply-running.png | 实际研发与卡片阶段不一致；截图内容仅为证据。 |
| E2 | code_path | src/backend/app/services/requirement_center.py：_change_status、_issue_status、_map_stage | 看板优先取 Change trace 状态，提议态 对应准备开发态，进行态 对应研发中。 |
| E3 | code_path | scripts/workflow_sync/derive.py：derive_change_state | 活跃 Change 按任务完成数派生 提议态 / 进行态 / 验收态，无法表达已启动但完成数为零。 |
| E4 | code_path | scripts/workflow_sync/engine.py：derived_changes、patch_issue_trace；scripts/workflow_sync/collect.py：load_change_record | Sync 将派生结果用于 Issue 等文档；与看板读取 Change trace 的路径不同。 |
| E5 | reproduction | bug-explore 中从当前源码 AST 提取状态判定函数并在内存注入计数 | 0/16+提议态 → Sync 提议态 / 看板 ready-dev；0/16+进行态 → 提议态 / development；1/16+提议态 → 进行态 / ready-dev；16/16+进行态 → 验收态 / development。属于合成验证。 |
| E6 | code_path | .agents/skills/opsx-apply/SKILL.md 的 Final Step；docs/08-command-execution-order.md 的完成门禁 | 完成同步位于完成门禁之后，当前契约缺少相应启动同步闭环。 |

机制层结论：启动事实缺失、任务计数与 Change trace 两种口径并存，已由源码及合成验证确认。实际部署是否还有缓存、快照或网络刷新问题尚未确认，不能作为已排除项。根因文档 root-cause.md 已补齐并通过证据门禁；规避方案见 workaround.md，11项修复验收见 acceptance.md，评审通过并已纳入 sprint-005，已创建修复 Change fix-requirement-center-apply-lifecycle-sync，当前待实施。

## 影响范围与严重等级

- 严重等级 medium，优先级 P2：影响研发状态可信度与协作判断，暂无阻断研发、数据丢失或安全事故证据，建议常规修复。
- 涉及 REQ/BUG 共用的需求中心看板、后端阶段读取、Workflow Sync 状态派生，以及两份 apply 技能和 Sprint 编排入口。
- 卡片列、动作和进度可能失配；用户可能误以为尚未启动而重复发起操作，重复执行后果尚未验证。
- 尚未定位引入该行为的具体提交，不认定为某次版本回归。
- 本阶段只生成缺陷文档，不变更 API、DB、UI、部署、安全或客户端生成物。后续设计需按实际变更范围同步相关契约与测试。

## 修复方向与建议验收

1. 前置门禁通过、正式实施时记录独立启动事实，使 0/N 也进入研发中；门禁失败不产生虚假启动状态。
2. 启动、进度、完成使用一致的状态事实源与判定规则；不能仅在一个 trace 中手工写入 进行态。
3. 保持任务完成与开始执行的语义区分，不提前勾选，不提前执行 验收态 完成同步。
4. 两份 apply 技能与 Sprint 编排使用相同启动契约，状态同步可幂等重跑，中断恢复不丢失已启动事实。
5. REQ/BUG 均覆盖未启动 0/N、已启动 0/N、部分完成、启动门禁失败、重复启动、中断恢复和完成门禁通过场景。
6. 在真实 API/浏览器中核对阶段、动作、进度及刷新结果，合成测试与真实观察分别记录。

## 待补证操作

目的：核对实际部署快照与刷新链路是否存在附加问题，不影响本次草稿生成。

1. 在目标项目需求中心打开开发者工具 Network，保留请求记录。
2. 记录启动前、通过门禁开始实施后、手动刷新后的 context 请求。
3. 返回时间、部署方式与版本、脱敏项目标识、请求路径/状态码、目标条目的 ID、stage、tasks，以及 snapshot_revision；若响应包含 request_id，可一并提供。
4. 返回格式采用三行对照表或最小 JSON 摘要，不提供 Authorization、Cookie、完整请求头、用户私密信息或原始会话日志。

## 数据采集与链路观测

- product_data_collection_observability: applicable
- affected_layers: Agent Workflow、后端治理状态读取、Web 看板阶段展示。
- N/A 原因：本阶段仅生成文档，不新增 usage_events、request_logs、task_traces、task_trace_spans 字段，不涉及数据库迁移、对象存储、部署或客户端生成；具体实现适用性在 Change 设计中确认。CLI 启动不伪造界面行为事件。
- validation: 已完成用户截图核对、代码路径分析及四组合成函数验证；真实部署请求、快照刷新、启动幂等与完整端到端验收待补齐。

## 附件与追溯

- 原始记录：capture.md。
- 截图：screenshots/board-ready-dev.png、screenshots/apply-running.png。
- 来源流程：explore → bug-capture → bug-explore → bug-generate。
- 关联需求：REQ-0012-frontend-requirement-center。
- 复现案例：BUG-0014-requirement-center-capture-not-persisted。

## BUG-0015 修复反向追溯

fix-requirement-center-apply-lifecycle-sync 已实现启动事实同步与0/N阶段流转；验证见 openspec/archive/2026-09-14-fix-requirement-center-apply-lifecycle-sync/verification.md。父需求保持历史归档状态，本次交付由BUG-0015与sprint-005承接。
