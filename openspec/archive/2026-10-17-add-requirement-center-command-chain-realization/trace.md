---
title: 需求中心卡片全命令产品链路真实化追溯记录
change_id: add-requirement-center-command-chain-realization
type: add
status: applied
source_requirement: REQ-0027-requirement-center-command-chain-realization
sprint: sprint-008
created_at: 2026-09-30 18:06:35
updated_at: 2026-10-17 16:10:00
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
    - task_trace_spans
  reason: 本 Change 将需求中心卡片八类动作变为受控 API 与多步骤 Agent Workflow，涉及文件事实源写入、Workflow Sync、执行投影、幂等恢复和归档门禁。
  validation: 已通过 `validate-product-data-observability.py --change add-requirement-center-command-chain-realization`；后端聚焦测试覆盖 usage_events、request_logs、task_traces 和失败脱敏路径，未新增对象存储或生产部署写入。
prototype_gate:
  prototype_refs:
    - issues/requirements/review/REQ-0027-requirement-center-command-chain-realization/prototype/web/prototype.html
    - issues/requirements/review/REQ-0027-requirement-center-command-chain-realization/prototype/web/context.md
  ui_contract: completed
  ui_skeleton: completed
  visual_acceptance_1440: completed
  computed_style: completed
  mock_api_boundary: synthetic_http
  req_final_consistency: completed
execution:
  schema_version: 1
  started_at: 2026-09-30 18:13:42
  completed_at: 2026-09-30 18:20:00
  last_event: opsx.modify
---

# 需求中心卡片全命令产品链路真实化追溯记录

2026-10-17 归档前复核：REQ 功能 20/20、横切 3/3、原型 5/5，完整自动验收 28/28 passed；归档就绪 ready，证据见 [`完整验收报告`](evidence/acceptance/20261017160138201174-4808ced5/summary.md)。Change 仍保持 applied，待本次归档命令完成后由 Workflow Sync 同步为 archived。2026-10-16 AC-014 隔离产品归档界面轮次与脱敏观测矩阵见 [`AC-014 观测证据`](evidence/acceptance/samples/AC-014.md)。

## 来源

| 项 | 值 |
|---|---|
| REQ | `REQ-0027-requirement-center-command-chain-realization` |
| Sprint | `sprint-008` |
| Change | `add-requirement-center-command-chain-realization` |
| 类型 | add |
| 状态 | applied |

## Requirement Readiness Report

| 项 | 结论 | 说明 |
|---|---|---|
| Readiness | Ready | requirement、user-stories、business-flow、acceptance、trace 与 prototype/web 齐全 |
| 评审门禁 | pass | REQ 状态为 `in_sprint`，已纳入 `sprint-008` |
| Prototype Gate | pass | `prototype_refs`、`prototype_gate`、AC-PROTOTYPE、1440px/390px 截图与 computed style 证据均已完成 |
| 产品数据采集与链路观测 | applicable | 覆盖 usage_events、request_logs、task_traces、task_trace_spans |

## 影响分析

```yaml
impact:
  backend: true
  web: true
  miniapp: false
  admin: false
  database: true
  storage: false
  api: true
change_type: add
capabilities:
  new: []
  modified:
    - web-catalog-requirement-center
    - web-catalog-chat-workbench
    - agent-workflow-tooling
```

## Conflict Report

| 事实源 | 优先级 | 结论 |
|---|---:|---|
| REQ 业务语义与权限门禁 | 1 | 成功必须以产物校验、Workflow Sync 和事实重读为准 |
| `prototype/web/context.md` | 2 | 提供八动作矩阵、selector 候选和局部一致合同 |
| `prototype/web/prototype.html` | 3 | 只表达交互结构，不调用 API、不写文件、不作为视觉完成证据 |
| `acceptance.md` | 4 | 18 条功能 AC、3 条横切 AC、5 条原型 AC 均待实现验证 |
| `rules/ui-design.md` / 既有页面 | 5 | 复用 Ops 系统、卡片、Modal/Drawer、Toast 和 Chat 组件族 |

## 生成产物

| 文件 | 用途 |
|---|---|
| `proposal.md` | 提案 |
| `design.md` | 设计 |
| `tasks.md` | 实施任务 |
| `specs/web-catalog-requirement-center/spec.md` | 需求中心规格增量 |
| `specs/web-catalog-chat-workbench/spec.md` | Chat 工作台规格增量 |
| `specs/agent-workflow-tooling/spec.md` | Agent Workflow 门禁规格增量 |

## 验证记录

2026-10-13 续验 AC-004～006：补齐独立夹具的 P2 分级后，`req-review` 轮次 `7375c67f-7a15-4fe0-a5bf-1b4cbf14f9fc` 候选 applied、应用 verified，卡片进入已评审。零 active Sprint 夹具的 `sprint-propose` 轮次 `83a18a53-6698-4087-ba64-39b621dc5f26` 创建连续 sprint-008、默认30人天并双向纳入 REQ；多 active 未选与显式超量保护轮次均无写入。`req-opsx` 就绪门禁先阻断不完整原型；补齐后生成 Change 的轮次因权限升级误判而 stopped，AF-039 修复并由轮次 `7dbf9836-33bc-4c54-8458-f54a1ad592db` 幂等收尾，最终只有一个 Change 且 schema v1 与关联一致。各 AC 仍为 partial，见 `evidence/acceptance/samples/AC-004.md`、`AC-005.md`、`AC-006.md`。

2026-10-13 AC-007 隔离续验：`opsx.start` 已在真实产品轮次落盘，0/11 时卡片显示研发中；续接后 1/11。宿主侧组件单测、编译和两入口 × 两视口 × 三状态的 12 组真实页面组件壳截图与样式采样通过，HTTP 为合成只读响应；产品 Agent 容器依赖不兼容且续接因 token 上限停止，UI Skeleton 首轮确认、已登录产品视觉、完成门禁和 `opsx.apply` 尚缺。AC-009～012、014、015、017、018 和原型 001、005 已补命令或文档回归的部分样本，不覆盖各自完整矩阵。最新完整验收诊断 `20261013150019239346-af0be59e` 为 28 项 blocked、范围 diagnostic，预检仍缺 65 个文件入口；不运行 `opsx.accept`。见 `evidence/acceptance/samples/AC-007.md` 及同目录逐项样本。

2026-10-13 AC-007 后续事实：用户确认隔离骨架，独立 Change 完成 11/11；宿主聚焦测试 7/7、TypeScript 编译、12 组合成只读 HTTP 视觉矩阵、中文及 OpenSpec 严格校验通过。独立回环服务真实登录态只读 API 返回项目已连接、REQ-9105 属 sprint-008 的 development；`opsx.apply` Workflow Sync 成功后该 Change 为 applied，需求中心卡片进入验收中。产品 Agent 续接轮次因 token 上限停止，实施完成由宿主独立副本执行并据实标注；仍缺任务全勾但门禁失败样本和已登录新构建视觉矩阵。最新完整诊断 `20261013155334416761-689f022c` 为 28 项 blocked / diagnostic，原因是全局预检证据不齐；不执行 `opsx.accept`。见 `evidence/acceptance/samples/AC-007.md`。

2026-10-13 AF-038 续验：第三隔离轮次定位评审迁移窗口的授权历史读取 503；第四隔离轮次迁移期间读取成功、执行器完成，但候选因评审范围拒绝而无应用。第五隔离轮次确认拒绝后的 plan 文件逐字节恢复，卡片仍待评审；同对象随后正常批准尝试因 `review_primary_scope` 拒绝并再次安全恢复。相关后端 62 项通过。AC-004 正向评审及其他分支仍待取证。完整诊断运行 `20261013132451887112-d9d39d46` 为 28 项 blocked、范围 diagnostic；未执行 `opsx.accept`。脱敏入口见 `evidence/acceptance/samples/AC-004.md`、`AC-019.md`、`acceptance-fixes.md`。

2026-10-13 AF-035 验收返修：HTML 预览对象 URL 清理改为可选调用；需求中心前端 122 项聚焦回归通过。隔离产品 AC-001 只取得 captured 分支的完成轮次，余项与视觉矩阵仍待证据；见 `acceptance-fixes.md` 与 `evidence/acceptance/samples/AC-001.md`。REQ 子文档一致性扫尾：需求、流程、故事、验收、trace 与 prototype 意图未因本次兼容修复改变，无需更新。

2026-10-13 逐项验收续接：隔离项目取得 AC-002 captured→draft 产品轮次；AC-003 的标题不一致负向轮次拒绝事实源写入，夹具修正后仍有执行前工作区准备失败。真实视觉矩阵已覆盖 9/37 组合，完整诊断清单 `20261013085854379101-8bb96a58` 为 28 项受阻；未运行 `opsx.accept` 状态同步，未取得归档就绪结论。脱敏入口见 `evidence/acceptance/samples/AC-002.md`、`AC-003.md` 与 `AC-PROTOTYPE-003.md`。

2026-10-13 最终复跑：完整诊断清单 `20261013090213691092-cd428dae` 仍为 28 项受阻；验收状态保持 pending。

2026-10-13 source 模式续验：独立副本 `req-generate` 完成并 applied；`req-complete` 补齐文档后的候选因 `trace_scope` 拒绝，但 source 事实源与需求卡片仍推进到 pending_review。AC-019 有失败子场景；验收状态保持 pending，证据见 `evidence/acceptance/samples/AC-019.md`。

2026-10-13 AF-036 返修复验：source 模式拒绝候选后安全回退同轮治理文件；后端相关测试 99 passed，前端相关测试 42 passed，独立产品轮次确认 trace、注册表及卡片恢复 draft。Chat 修复后默认折叠被拒绝轮次的原文并显示拒绝结论；AC-019 该负向子场景通过，其余组合待证，未执行 `opsx.accept`。见 `evidence/acceptance/samples/AC-019.md`。

2026-10-13 AC-003 再尝试：轮次 `02db5a0b-4e9e-4d2c-945b-2ed1554c7717` 被控制器以 `governance_validation_failed` 拒绝，source 安全回退至 draft；通用错误码无法定位具体校验分支，停止原样重试。成功路径仍 blocked，见 `evidence/acceptance/samples/AC-003.md`。

2026-10-13 09:41 完整诊断重跑 `20261013094109254300-20abbf3a`：28 项 `blocked / diagnostic`，缺少完整产品轮次和视觉矩阵证据；验收继续 pending。

| 时间 | 命令 | 结果 | 摘要 |
|---|---|---|---|
| 2026-09-30 18:06:35 | `python scripts/validate-change-identity.py --new-id add-requirement-center-command-chain-realization` | pass | Change 身份校验通过 |
| 2026-09-30 18:15:42 | `uv run pytest src/backend/tests/test_governance_candidates.py src/backend/tests/test_governance_writer.py src/backend/tests/test_governance_review.py src/backend/tests/test_requirement_completion_recovery.py` | pass | 98 个后端治理候选、写入、评审与恢复测试通过 |
| 2026-09-30 18:15:42 | `./node_modules/.bin/vitest run src/requirement-center.test.tsx src/governance.test.tsx` | pass | 128 个前端需求中心与治理文档测试通过 |
| 2026-09-30 18:15:42 | `./node_modules/.bin/tsc -b` | pass | Web TypeScript 构建类型检查通过 |
| 2026-09-30 18:19:58 | `node tests/requirement-center-command-chain-realization.cjs` | pass | 生成 `evidence/ui/command-chain-dark-1440.png`、`command-chain-light-1440.png`、`command-chain-dark-390.png` 与 `computed-styles.json` |
| 2026-09-30 18:37:27 | `uv run pytest src/backend/tests/test_governance_writer.py src/backend/tests/test_requirement_completion_recovery.py` | pass | 25 项后端治理 writer 与恢复回归通过；覆盖 Workflow Sync 成功才 applied、sync 失败不 applied。 |
| 2026-10-04 10:43:55 | `uv run pytest src/backend/tests/test_chat_platform.py::test_platform_deployment_defaults_local_binding_to_source_mode src/backend/tests/test_governance_candidates.py::test_source_workspace_mode_generate_writes_directly_without_second_apply -q` | pass | 2 项通过，覆盖本地部署默认 source 绑定、source 模式直接应用且不走副本二次应用。 |

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-10-04 10:43:55 | opsx.modify | applied | AF-034 本地部署默认 source 工作区策略返修完成；台账见 `acceptance-fixes.md`，用户可见阶段回到验收中 / 待复验。 |
| 2026-09-30 18:37:27 | opsx.modify | applied | AF-033 事实源唯一完成门禁返修完成；台账见 `acceptance-fixes.md`，用户可见阶段回到验收中 / 待复验。 |
| 2026-09-30 18:06:35 | req.opsx | proposed | 根据 `REQ-0027` 创建 OpenSpec Change 文档与规格增量 |
| 2026-09-30 18:13:42 | opsx.start | in_progress | Workflow Sync 启动 Change 执行投影 |
| 2026-09-30 18:20:00 | opsx.apply | applied | 八动作产品链路实现与验证完成，等待归档 |

2026-10-13 AC-018 验收返修 AF-040：独立 MySQL 8.2.0 矩阵首次 55 passed、31 failed，确认对象会话复用查询的 `NULLS LAST` 语法不兼容；替换为 `IS NULL` 空值排序键后，同一隔离矩阵 86 passed，SQLite 聚焦 3 passed。无 API/DB schema、部署、对象存储或认证边界变化。`docs/03-api-index.md`、`docs/04-database-design.md`、`compatibility/database/test-matrix.md` 已同步；AC-018 最终文档审计仍待签认。

2026-10-13 视觉续验：隔离对象 `REQ-9105` 已登录新构建在 1440px/390px 均显示验收中，见 `evidence/acceptance/visual/AC-007-real-product/`。AC-PROTOTYPE-002 的浅色 1440px 首轮 UI Skeleton 经用户确认，单项诊断 `20261013162858595308-12121fa3` 为 passed；功能 AC-007 仍 partial。完整诊断 `20261013163003968552-ccd4d1d2` 为 blocked，缺 62 个证据入口，未执行 `opsx.accept`。

2026-10-13 AC-020 逐项签认：source 模式隔离产品轮次 `c0a0884f-db69-4e0b-a901-d116a7e590f8` 与事实源核对完成；14 项聚焦回归通过，单项诊断 `20261013170535594446-fdbd720e` 中 AC-020 passed。Issue 功能 AC 已签认 2/20。完整诊断 `20261013170724939134-115c6271` 为 3 passed、25 blocked，仍无归档就绪结论。

2026-10-13 AF-041 视觉返修：当前隔离产品在文档抽屉关闭后未恢复触发器焦点；`RequirementCenterPage` 记录触发器并在关闭后恢复，聚焦前端测试 1 passed、Web 构建通过，真实页面 Escape 与蒙层关闭两路径复验均聚焦 `requirement.md`。深浅主题看板与浅色抽屉三视口补样位于 `evidence/acceptance/visual/AC-PROTOTYPE-003-current/`；AC-PROTOTYPE-003/005 仍 partial，不勾选。

2026-10-13 AF-042 部署策略返修：worker 对缺失 `workspace_mode` 的旧绑定原先静默回退 `copy`，与 AC-020 的显式 copy 边界不一致；现启动预检只接受显式 `source`/`copy`，缺失模式拒绝并要求迁移配置。15 项 source/显式模式聚焦测试通过，部署文档同步；AC-020 保留隔离产品轮次、文件事实源和独立副本为空的证据。

2026-10-13 AC-PROTOTYPE-005 续验：新建 Capture 双视口打开、窄屏内部点击与外部关闭取得真实页面证据；外部关闭焦点缺口按 AF-041 修复，Escape 与蒙层关闭后均回到触发按钮。两个前端聚焦测试通过，Web 构建通过；取消、提交后关闭、Tab 约束及完整矩阵仍缺，保持 partial。

2026-10-13 AF-043 视觉返修：当前隔离产品证实 Capture 浮层打开后首次 Tab 跳到背景统计按钮；CaptureDialog 增加初始焦点和顶层 Tab 边界约束，聚焦测试 1 passed。真实隔离页面在 1440px 复验首次与循环 Tab 均留在浮层，Escape 返回触发按钮；深色弹窗三视口及内部/外部点击双视口证据归入 `evidence/acceptance/visual/AC-PROTOTYPE-003/` 和 `AC-PROTOTYPE-005/`。两项视觉 AC 仍 partial。完整诊断 `20261013175532818709-f6426ed3` 为 3 passed、25 blocked，readiness 仍 blocked。

2026-10-13 AF-043 嵌套弹窗续验：Capture 删除草稿确认弹窗原始焦点仍在外层；补齐顶层 Tab 循环与取消后焦点恢复。两项聚焦测试通过，真实隔离页面 1440/390 取消不删除草稿，revision 与状态保持不变。AC-001 新 captured 只读分析产品轮次 `d3a25ba9-af26-4b7a-bb2a-35a38f8bece3` 完成且目标文件、注册表、索引前后哈希一致，仍缺 exploring 与反例，故不签认。视觉 AC 与 AC-001 均保持 partial。

2026-10-13 AF-044 验收返修：AC-009 独立隔离项目中未接入动作仍可取得对象会话，真实接口返回 200/0；入口新增动作白名单后聚焦后端 46 passed。旧隔离服务未重建，新构建产品复验与角色/快照矩阵仍缺，AC-009 判 failed，功能计数仍 2/20。完整返修台账见 `acceptance-fixes.md`，脱敏失败证据见 `evidence/acceptance/samples/AC-009.md`。REQ 子文档一致性扫尾：验收条款已覆盖白名单；需求、流程、故事、trace 和 prototype 目标未改变。

2026-10-13 AF-044 隔离新构建复验：未知动作 422/2604、无会话，合法只读动作 200/0；会话、候选、轮次数未变化。该失败点修复完成，AC-009 仍因其他权限矩阵缺口保持 partial，功能签认计数 2/20。


2026-10-14 AC-002 整项签认：独立隔离产品 captured 与 exploring 两条 `req-generate` 轮次均 completed、候选 applied；各仅新增目标 `requirement.md`，同步目标 trace、需求 registry 与 CHANGELOG，`capture.md` 哈希不变，draft、`lifecycle.generated`、下一动作索引和页面文档重读均通过。证据见 `evidence/acceptance/samples/AC-002.md`。AC-001 保持签认，功能清单现为 4/20；隔离产品卡片显示 4/20。聚焦诊断 `20261014081332084893-017f20f5` 中 AC-002 passed；完整复验 `20261014081959680773-23e76a11` 为 15 passed、13 blocked、0 failed，整体尚未归档就绪。

2026-10-14 AC-003 整项签认：独立 `39028` 产品轮次分别从 `draft` 与 `enriching` 完善需求，两个候选和应用均为 `applied / verified`，六件套、适用 Web 原型、中文标题及 `pending_review` 事实源通过；缺文件、空文件、无效标题三条产品反例均被拒绝且保留 `draft`。首次执行器停滞与 trace 越界轮次按失败保留；前者停止后无文件变更，后者被控制器回滚。证据见 `evidence/acceptance/samples/AC-003.md`，聚焦诊断 `20261014090214365743-8592da23` 的 AC-003 为 passed。该诊断为单项范围，完整验收须另跑。

2026-10-14 AC-004 四路径整项签认：隔离项目 `39028` 中，批准、拒绝、延后三个独立 `req-review` 产品轮次均 completed、候选 applied、应用 verified；批准迁入 review，拒绝与延后有明确理由并保留 plan。取消未发送且无产品轮次，目标文件哈希未变。首轮拒绝候选因 `review_acceptance_scope` 回滚，收紧范围后复验成功。证据见 `evidence/acceptance/samples/AC-004.md`。聚焦诊断 `20261014095143692985-044c66bb` 的 AC-004 passed；完整复验 `20261014095158402991-d9b82f81` 范围 complete，17 passed、11 blocked、0 failed，整体仍未归档就绪。隔离产品 REQ-0027 卡片显示 6/20；主产品 `39002` 仍需登录后独立核对。

2026-10-14 AF-047 AC-011 部分返修：隔离故障矩阵发现持久写入器在同步完成、终态未提交时会重复执行同步；补同步输入/结果 hash 阶段标记，恢复时核对事实源，未知部分同步阻断重放。前三个候选动作的 `copy` 模式矩阵与相关回归共 91 passed。默认 `source` 模式和其余四个命令动作尚未取得同等级恢复证据，AC-011 不签认。证据见 `evidence/acceptance/samples/AC-011.md` 与 `acceptance-fixes.md`。

2026-10-14 AF-048 AC-011 续返修：两类 worker 增加已终态 running 候选的幂等收尾扫描，补上重启后只恢复 Chat 终态而未收集治理成果的窗口。定向重复扫描仅有一条应用记录；相关后端回归 201 passed、1 skipped，聚焦诊断 `20261014172001884989-8c58148c` 命令探针 passed。七动作完整故障矩阵仍未齐，AC-011 保持未签认。证据见 `evidence/acceptance/samples/AC-011.md` 与 `acceptance-fixes.md`；REQ 子文档一致性见返修台账。

2026-10-14 AF-049 AC-011 默认源工作区真实首文件中断：隔离轮次停止后候选虽 rejected，目标文件仍残留；定位 `collect` 未读 baseline 即处理非完成终态并完成修复。故障现场已按基线逐字节安全恢复；三候选动作六窗口隔离矩阵 18 passed，相关后端回归 206 passed、1 skipped。修复版真实复验在写前遭执行器失败，四直接命令矩阵仍缺，AC-011 不签认。证据见 `evidence/acceptance/samples/AC-011.md` 与返修台账；REQ 子文档一致性同 AF-049。

2026-10-14 AF-050 AC-011 四直接命令补私有逐步 hash 日志和重启分类，4×6 隔离故障窗口及同步失败回归通过；同步退出码为 0 仍仅标为业务待核验。真实产品注入及动作语义门禁未齐，AC-011 不签认。证据见 `evidence/acceptance/samples/AC-011.md` 与 `acceptance-fixes.md`；REQ 子文档一致性：仅 acceptance 追加进展，其余文档无行为变化。

2026-10-14 AF-051 AC-011 修复候选动作因直接命令日志目录缺席而提前停止的回归；隔离 `REQ-9204` 真实轮次已在首业务文件写入后强制中断，重启核对 stopped / rejected、零应用和 2,212 文件全树恢复至不可变基线。此为一个真实窗口，七动作其余窗口未齐，AC-011 不签认。证据见 `evidence/acceptance/samples/AC-011-source-restart-9204.json` 与返修台账。

2026-10-14 AF-052 AC-011 补七动作真实中断轮次与重启观察：前三候选动作取得写前、部分文件和同步后样本，四直接命令取得首文件或同步中样本；归档规格合并与目录迁移后中断时保留部分现场并安全阻断，不虚报 done。修复治理快照遗漏活动 Change `.openspec.yaml` 的缺口，相关回归 156 passed、1 skipped。矩阵未齐，AC-011 不签认；REQ 子文档仅 acceptance 增补，其他业务文档无行为变化。证据见 `evidence/acceptance/samples/AC-011.md` 与返修台账。

2026-10-14 AF-053 AC-011 对保留的隔离归档部分现场执行既有跳过再合并的恢复分支，正式规格 hash 与归档目录唯一性前后不变，后置证据门禁通过。Workflow Sync 改用完整 Sprint YAML 解析，合法无缩进列表可自动定位、无效语法报错，20 项聚焦回归通过。新增真实写前轮次中 `req-opsx` 长期 unknown，`sprint-propose` 同步后 Sprint YAML 无效，均不作通过证据；AC-011 未签认。证据见 `evidence/acceptance/samples/AC-011.md` 与返修台账。

2026-10-14 AF-054：第二独立隔离项目补采七动作写前、正式同步中和同步后产品轮次，`req-opsx` 部分同步现场只续做目标 Workflow Sync，重复 dry-run 无核心更新；直接归档脚本成功归档且目录唯一。`--dry-run` 误判为正式同步的日志分类已修复。归档正式同步中断等格子仍缺，AC-011 未签认；见 `evidence/acceptance/samples/AC-011.md`。

2026-10-16 AF-055：AC-012 归档脚本新增规格预览指纹与安全重试护栏，修复合并后、迁移前重试可能再次合并的反例。真实 OpenSpec CLI 分段、Change 迁移保留现场、Workflow Sync 与 Issue 迁移进程中断及外部编辑阻断均有隔离证据；完整产品对象轮次未齐，AC-012 不签认。证据见 `evidence/acceptance/samples/AC-012.md`。

2026-10-16 AC-012 产品轮次补证：首次归档在容器指纹写入权限处被拒绝，修正私有日志位置后第二轮归档命令退出 0；同轮后置直接编辑正式规格，重试被指纹护栏阻断并保留现场。归档技能和治理日志已补边界，完整四阶段产品中断轮次仍缺，不签认。

2026-10-16 AF-056：AC-012 在独立隔离产品对象补齐规格合并、Change 迁移、Workflow Sync、Issue 迁移四个中断及同对象恢复轮次；四个恢复命令成功，归档目录唯一、各轮次规格指纹匹配。归档后规格漂移的产品轮次以 `failed / archive_recovery_blocked` 阻断成功误报；既有未知外部修改仍保留安全现场。关联 REQ 多 Change 部分归档未提前 done 复用 AC-008 的产品证据。AC-012 已单项签认，证据见 `evidence/acceptance/samples/AC-012.md` 与 `AC-012-product-four-windows-and-completion-gate-20261016.json`；其他 AC 不随之签认。REQ 子文档一致性：验收清单和 trace 已更新，requirement、business-flow、user-stories、prototype 的业务目标与视觉边界未变。

AC-012 签认后聚焦验收 `20261016163308188999-c93ae0bc` 的本项为 passed（诊断报告整体 blocked 属 `--only` 范围）；完整验收 `20261016163345834948-e224d841` 为 complete / blocked，28 项中 13 passed、15 blocked，AC-012 passed 且证据复用。功能清单实数 13/20。Workflow Sync `opsx.modify` errors=0、验收状态 pending，未触发 `opsx.accept`；AI Usage 为 unavailable warning。主产品浏览器当前停在登录页，未取得登录后卡片视觉核对，不能宣称卡片 UI 已刷新。

2026-10-16 AC-013 续验：Chrome 中 `REQ-9300` 真正关窗后轮次继续执行，重进按同一 turn ID 找回。完成结果曾滞留 `unknown`；定位缺失直接命令日志在 `archive_completion_blocked` 中抛 `WorkspaceError`，修复缺席记录的安全判定后，产品按相同外部 completed 轮次恢复，未重放治理动作。API/Worker 重启与需求中心刷新后，七动作当前态投影和文件一致；聚焦报告 `20261016180055645290-29ee8c7f` 中 AC-013 passed。完整报告 `20261016180122592957-e4124d58` 为 complete / blocked：28 项 22 passed、6 blocked，AC-013 passed；功能清单签认 14/20。Workflow Sync `opsx.modify` errors=0、验收状态 pending，未触发 `opsx.accept`。主产品 `39002` 浏览器仍停登录页，卡片 UI 计数尚未能现场确认。REQ 子文档一致性：本轮更新 acceptance，requirement、business-flow、user-stories、prototype 的业务与视觉目标未变。

2026-10-16 AC-015 自主验收：修复治理 Trace 链路字段白名单与请求日志异常告警脱敏；隔离产品四层观测表只读扫描 24,114/93/173/557 条，无本机路径、密钥形态或敏感正文键命中。非法字段、采集故障、Workflow Sync 失败门禁、90/180 天及未终态恢复保留聚焦回归 7 passed，相关四组测试 131 passed、1 skipped。证据见 `evidence/acceptance/samples/AC-015.md`；单项诊断 `20261016185602649468-4eedc7a3` AC-015 passed，完整验收 `20261016185737918032-e2f1cdc4` 为 22 passed、6 blocked，AC-015 passed。功能清单签认 16/20，Change 保持 applied、验收 pending；Workflow Sync `opsx.modify` 0 errors。REQ 子文档一致性：仅验收清单结论变化，requirement、business-flow、user-stories、prototype 的需求与视觉目标未变。
主产品 `39002/requirements` 登录后页面已现场核对：REQ-0027 卡片显示“验收 16/20”，说明文字明确计数依据 Issue `acceptance.md` 的已勾选项；与文件签认数一致。

2026-10-17 AC-019 自主验收：source 模式补齐候选 revision、正式 Workflow Sync 一致性校验、锁内事实源重读及恢复阻断时的项目读取遮蔽。隔离产品 `REQ-9316-capture` 的候选生成轮次 `f8afc333-16a7-4ecd-a821-df6d14469371` 为 `applied / verified`，同轮同步退出码 0，文件与卡片均为 draft；错误 manifest/revision 的产品 API 拒绝且无新增应用，`REQ-9317-capture` 准备后事实源变化返回 409/2606，卡片仍 captured。四组后端回归 158 passed；脱敏证据见 `evidence/acceptance/samples/AC-019.md`。单项诊断 `20261017000558632518-b0dabea7` 中 AC-019 passed，完整运行 `20261017000630013086-b8428962` 为 23 passed、5 blocked，AC-019 passed。功能清单 18/20；AC-011、AC-016 仍未整项签认，Change 保持 applied、验收 pending。主产品 39002 当前浏览器停登录页，卡片 18/20 尚待登录后现场核对。REQ 子文档一致性：本轮仅调整验收结论与 Change 设计，业务流程、用户故事和原型目标未变。

2026-10-17 AC-016 自主验收：独立隔离产品 `REQ-9315-capture` 经 captured、draft、pending_review、approved、in_sprint、真实 opsx.start、applied、归档到 done。当前用户确认独立样本人工验收并授权归档后，产品归档轮次 `f862bf86-ed51-4155-a95b-f8ea23b8b5b8` completed，归档脚本退出 0；规范归档目录、合并规格、Issue archive、注册表 done 与产品卡片只读一致。每阶段轮次均未执行下一阶段命令。`sprint-propose` 和 `opsx-apply` Chat 轮次各因额度与权限收窄停止，文件事实独立核验，未伪称轮次成功。证据见 `evidence/acceptance/samples/AC-016.md`；单项诊断 `20261017073141761125-82a5f55a` 中 AC-016 passed，完整运行 `20261017073218909905-37eeeeaa` 为 25 passed、3 blocked（横切三项）。功能清单 19/20；AC-011 仍未整项签认，Change 保持 applied、验收 pending。主产品 39002 当前浏览器停登录页，卡片 19/20 尚未现场核对。REQ 子文档一致性：本轮仅更新验收清单，业务流程、用户故事及原型目标未变。

2026-10-17 AC-011 复核纠正：七动作故障矩阵及新隔离 `opsx-apply` 部分写入、重启、受控续做轮次均保留在 `evidence/acceptance/samples/AC-011.md`；单项命令诊断 `20261017075031016140-034250e5` 为 passed。但 `tasks.md` 7.8.2d 所记旧 `req-opsx` 轮次仍为 unknown / worker_heartbeat_lost，且原无效 Sprint YAML 的同步完成门禁缺少针对原条件的复验证据，因此 AC-011 整项未通过。已撤回过早签认，功能清单为 19/20；Change 保持 applied、验收 pending。主产品 39002 卡片尚未在登录后现场核对。REQ 子文档一致性：仅纠正验收事实，业务流程、用户故事及原型目标未变。

2026-10-17 完整验收重跑 `20261017080020216943-730aae92`：结论 blocked。报告仍将 AC-011 的命令与文件入口探针标作 passed，该标记不覆盖样本自身的 partial 状态及任务 7.8.2d 的缺口；Issue 清单继续保持 19/20，待故障条件实际复验后才可签认。

2026-10-17 AF-057 AC-011 返修：针对隔离 `sprint-propose` 正式同步退出 0 但 Sprint YAML 无效的失败事实，在 Chat 正常终态及可信 unknown 终态恢复处增加源文件完成门禁；无效 YAML、Sprint 身份或目标正式范围返回固定 `sprint_source_invalid`，私有日志标记 `blocked_invalid_sprint_source`。聚焦后端 88 passed、1 skipped。旧 `req-opsx` unknown 仍保留；隔离入口当前健康探测不可连接，修复版真实产品轮次未取得。AC-011 仍 partial，功能清单 19/20。返修台账见 `acceptance-fixes.md` AF-057，API 语义同步见 `docs/03-api-index.md`。本轮不改 REQ 业务目标与原型，子文档清单仍一致。

2026-10-17 AC-011 验收器修正：`required_sample.status=partial/pending` 现在阻断命令探针的通过与复用，聚焦回归 21 passed；诊断 `20261017081303746139-e4eb3609` 中 AC-011 为 `blocked / sample-incomplete`。规范同步 `docs/standards/opsx-acceptance.md`；Issue 仍 19/20。

2026-10-17 完整验收重跑 `20261017081405723872-4df67216`：范围 complete，21 passed、7 blocked；AC-011 为 `blocked / sample-incomplete`，另有三项横切检查和三项原型样本未就绪。故 Change 仍不 ready，Issue 功能清单 19/20；未运行 `opsx.accept` 同步或归档。

2026-10-17 AC-011 最终产品复验：独立隔离环境修复版 API/Worker ready；新 `req-opsx` 写前轮次 `9b249258-944e-4708-a264-543b64c4cb57` 重启后 stopped / no_governance_write、事实源基线不变，部分写入轮次 `f623dfdc-1742-49b8-915a-70eea82f5d6f` 为 stopped / partial_write、文件保留。新 `sprint-propose` 轮次 `a2593400-4dce-4f8c-8f36-053fa3f880f2` 在正式同步成功但 Sprint YAML 无效时 failed / sprint_source_invalid，没有 Chat 成功声明。七动作四窗口 28 格、30 轮次前缀证据入口逐项核对；旧外部不可读轮次继续 unknown 安全阻断，不作为通过样本。AC-011 整项签认、功能清单 20/20；证据见 `evidence/acceptance/samples/AC-011.md` 与两份 20261017 脱敏 JSON，返修台账见 `acceptance-fixes.md` AF-057。REQ 子文档一致性：本轮仅更新验收清单与证据，业务流程、用户故事及原型目标未变。

2026-10-17 完整验收重跑 `20261017083834351632-dd4c4ac9`：范围 complete，22 passed、6 blocked；AC-011 passed。剩余为横切三项及原型样本三项，与本轮功能签认分开；Change 仍不 ready，未执行 `opsx.accept` Workflow Sync 或归档。主产品卡片本轮未取得登录后页面观察，文件清单 20/20 不冒充视觉核对。
