---
title: 统一主源码目录与交付链路工作区及模块化执行架构变更追溯
created_at: '2026-10-29 06:51:35'
updated_at: 2026-10-29 12:49:12
change_id: update-unified-workspace-runtime
requirement_id: REQ-0042-agent-runtime-version-space-isolation
status: applied
type: update
iteration: sprint-015
knowledge_base_refs:
- docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md
- docs/knowledge-base/retrospectives/sprint-013-retrospective.md
prototype_refs:
- path: issues/requirements/archive/REQ-0042-agent-runtime-version-space-isolation/prototype/web/prototype.html
  role: html-structure
- path: issues/requirements/archive/REQ-0042-agent-runtime-version-space-isolation/prototype/web/context.md
  role: decomposition
prototype_gate:
  decomposition: done
  ui_skeleton: pending
  visual_acceptance_1440: pending
  req_final_consistency: pending
product_data_collection_observability:
  status: applicable
  affected_layers:
  - web
  - api
  - db
  - agent_workflow
  - usage_events
  - request_logs
  - task_traces
  - task_trace_spans
  reason: 统一工作区、调度、看板投影与环境诊断影响执行和可观测链路。
  validation: 已定义功能、数据观测、权限和失败恢复 AC；当前仅文档检查，产品与视觉验收待实现。
dependencies: []
execution:
  schema_version: 1
  started_at: 2026-10-29 08:18:40
  completed_at: 2026-10-29 12:49:12
  last_event: opsx.apply
---

# 统一主源码目录与交付链路工作区及模块化执行架构变更追溯

## 来源与边界

来源 REQ-0042-agent-runtime-version-space-isolation，已评审并纳入sprint-015；已启动实施，当前未完成全部任务与验收，尚无完成事实。

## 原型承接与冲突

原型拆解完成，D1采用DS组件；HTML为Mock评审示意，业务矩阵优先于演示行为的例外已写design.md。UI Contract已定义，Skeleton、PNG、1440px/关键交互截图、computed style、真实API与REQ最终一致性均待实施。

## 验证计划

执行中文标题、当前Change中文规范、OpenSpec严格校验和Sprint关联检查；产品验收未运行。业务测试、真实模型/浏览器与双库证据在apply/accept完成。

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-29 06:51:35 | req.opsx | proposed | CLI创建并生成设计与验收材料，未启动实施。 |

## 实施检查点（2026-10-29）

实现路径：src/backend/app/moonbox_core、src/backend/app/moonbox_worktree。已实现主工作区登记、Git身份、唯一交付预留、不可变会话绑定、平台worker路径解析与工作区队列互斥。主目录API与OpenAPI/Orval基础契约已加入。

旧source/copy迁移、会话产品绑定入口、独立树沙箱、运行环境固定、模块入口拆分、治理投影和UI尚待完成。

验证：新增底层聚焦回归65项通过，主工作区API集成1项通过；既有权限回归9项及21个子场景通过。Chat回归批次包含1条旧测试模拟入口失配，已定位并修正为当前函数入口后权限批次通过。真实模型/容器用例未启用，不能替代真实产品证据。初次Docker扫描因沙箱socket权限失败；授权只读检查后确认daemon可用。登记独立MySQL 8.2.0环境完成新增主工作区API及队列回归2项，cleanup与check均为clean，容器/网络零残留；该样本不代表全部双库AC完成。

任务清单保持未完成，当前没有完整FR或UI验收闭环，不运行opsx.apply完成事件、不归档、不推送。下一实施阶段继续上述未完成项。

### UI 骨架与后续接入

共用骨架入口为src/web/tests/workspace-skeleton.html，使用合成空数据，不调用API。1440×900深浅主题及390×844浅色截图位于update-unified-workspace-runtime/evidence/ui；移动端computed style为14px正文、16px内边距，宽390px且无横向溢出。桌面检查为32px内边距、216px侧栏。这里只确认结构，浮层组件族、1024×600、多状态和真实产品全流程仍待验收，任务1.2不勾选。

Chat工作台加入WorkspacePanel，只读请求真实受鉴权工作区列表；无Mock回退。迟到响应、权限撤销后清空旧身份及Esc关闭合成测试通过。独立工作区、恢复与合入写动作仍关闭。源码入口src/web/src/components/workspaces和src/web/src/pages/catalog/ChatWorkbenchPage.tsx。

## 本轮入口矩阵与稳定批次

| 入口 | 当前事实与环境 | 正向/拒绝探针 | 关联验收 |
|---|---|---|---|
| 工作区 API / 非交互服务 | 同一 core；临时 SQLite/MySQL、合成身份、真实 Git | 唯一主目录、跨空间拒绝、只读拒绝 | AC-001、AC-008 |
| 执行准备 / 执行器 | 主工作区固定绑定、不可变镜像、现有 Chat worker | 合成回归已通过；下一探针为一个临时仓库内的有界真实模型写轮次 | AC-004、AC-009、AC-010 |
| 恢复 / 清理 | 独立清单引用、持久操作与原占用 | 后续编辑冲突、删除历史仍保留被引用内容、断点续接 | 0054 AC-006 至 AC-010 |
| Web 工作区详情 | 当前源码、真实 API、合成临时 Git/SQLite | 六组主题/视口、权限拒绝、恢复成功、冲突及 Esc | UI AC |
| 合入 | 固定双父候选、当前迭代权限、持久确认 | 真实 Git/双库测试；供应器为明确标注的合成测试适配 | 0055 AC-001 至 AC-007 |
| 正式联合开放 / 归档 | REQ-0048 尚无固定候选验收供应接口 | 门禁保持关闭；未执行正式归档、生产部署或推送 | 联合门禁 |

真实模型探针仅使用合成身份、临时仓库与临时数据库、已有本地登录；不挂载业务数据库或本项目源码，不修改正式对象。最多一个写轮次，180 秒执行上限，沿既有测试配额预留，失败保留脱敏原因而不自动重复发送。临时容器沿已登记 run 标签管理，完成证据与恢复核对后清理。该探针不能替代正式部署或 REQ-0048 的组合环境。

## 历史批次记录（最终结果见实施验证）

已完成任务勾选仅代表对应实现与聚焦回归通过；联合开放、完整真实场景及自动验收未完成项保留。基础 SQLite 批次 165 通过/1 条显式可选跳过，实际 MySQL 8.2 回归25通过；该 MySQL 结果不替代新依赖要求的8.4。真实模型隔离样本成功改文件、采集两点、关闭执行器并释放锁。视觉与样式证据见 update-unified-workspace-runtime/evidence/ui，详细验收归属在最终逐项证据包补齐。

## 最终实施结果

实现、双库、真实候选与界面验收已完成，详见 implementation-verification.md。逐AC正式结论由本轮自动验收回填；历史“待实施”描述仅代表当时阶段。

## 正式验收与闭环

逐AC 23/23 通过，证据、归档预演与共享归档准入均ready；报告：[20261029124936930594-377f0a36](evidence/acceptance/20261029124936930594-377f0a36/summary.md)。Workflow Sync 已回填，临时Docker容器与网络零残留。AI Usage完成hook自动发现本地会话并回填actual记录；治理run自身仍无完整边界token测量，不估算收益。
