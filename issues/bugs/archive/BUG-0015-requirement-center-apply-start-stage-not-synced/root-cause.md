---
bug_id: BUG-0015-requirement-center-apply-start-stage-not-synced
created_at: 2026-09-12 17:45:49
updated_at: 2026-09-12 17:45:49
root_cause_status: confirmed
---

# 根因分析

## 根因状态

status: confirmed

确认范围：当前源码及 apply 契约中的启动状态缺口与状态派生分歧。实际部署是否另有快照或网络刷新问题未确认，不纳入本次已确认根因。

## 现象

用户提供 BUG-0014 的“准备开发态 / 开始修复 / 0/16”卡片截图，同时提供 apply 已实施并进行验证的截图。首轮探索文件为 提议态、0/16；后续文件已变化，截图不是实时状态承诺。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | screenshot | screenshots/board-ready-dev.png；screenshots/apply-running.png | 同一条目实际研发与卡片阶段不一致。 | 用户侧现象。 |
| E2 | code_path | src/backend/app/services/requirement_center.py：_change_status、_issue_status、_map_stage | 读取 Change trace；提议态 映射 ready-dev，进行态 映射 development。 | 看板依赖落盘状态，无法自行感知 Agent 启动。 |
| E3 | code_path | scripts/workflow_sync/derive.py：derive_change_state | 活跃 Change 零完成数派生 提议态，部分完成派生 进行态，全勾选派生 验收态。 | 任务进度不能表达已启动 0/N。 |
| E4 | code_path | scripts/workflow_sync/collect.py：load_change_record；scripts/workflow_sync/engine.py：derived_changes、patch_issue_trace | Sync 按计数派生并用于 Issue 等文档，看板另读 Change trace。 | 状态读取与派生口径分离。 |
| E5 | reproduction | logs/state-matrix.json | 从源码 AST 提取原函数，在内存注入合成任务数据；四组断言通过，附源码 SHA-256。 | 状态不一致可确定性复现。 |
| E6 | code_path | .agents/skills/opsx-apply/SKILL.md：Final Step；docs/08-command-execution-order.md：完成门禁 | 完成同步在实现、验证后，开始实施没有对应启动同步闭环。 | 不能用提前执行完成同步解决启动缺口。 |

## 已确认根因

1. 当前研发生命周期没有完整的启动事实写入契约。完成数为零既可表示未启动，也可表示正在处理首项任务；现有派生逻辑将两者都判断为 提议态。
2. 看板与 Workflow Sync 使用不同口径：前者优先读取 Change trace，后者依据任务勾选数。仅补写一个 进行态 或仅更新任务数，都不能保证所有投影一致。
3. 完成同步承担交付完成语义，不能提前调用来伪装启动；需要分离启动、进度与完成，并统一状态事实源。

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 看板完全不支持研发中 | E2、E5：进行态 + 0/16 返回 development。 |
| 勾选任意一个任务就一定能使卡片进入研发中 | E5：提议态 + 1/16 仍返回 ready-dev。 |
| 仅修改 Change trace 即可使 Sync 口径一致 | E3、E5：0/16 即使给出 进行态 输入，Sync 仍派生 提议态。 |

未排除：实际部署版本差异、context 快照过期或轮询失败。当前前端源码已有轮询，不等于实际部署刷新已验证。

## 修复方向

- 在前置门禁通过且正式实施时落盘启动事实；未启动和启动失败保持准备开发态。
- 为启动、进度和完成建立同一状态判定契约，统一 Change trace、Issue 关联状态、索引与看板投影。
- 同步幂等；保留已启动 0/N；暂停或恢复不错误降级为未启动，不用提前勾选任务伪造进度。
- 两份 apply 技能及 Sprint 编排共同接入。全勾选不替代完成门禁，未通过门禁不得宣布 验收态。

## 验证闭环

本次四组源码函数合成验证通过：0/16 + 提议态 → 提议态 / ready-dev；0/16 + 进行态 → 提议态 / development；1/16 + 提议态 → 进行态 / ready-dev；16/16 + 进行态 → 验收态 / development（前项为 Sync，后项为看板）。这证明现有机制，未证明修复成功。

复核方式：从 logs/state-matrix.json 取得源码路径及哈希；从对应源码 AST 提取 derive_change_state 和 STAGES/_map_stage，在内存构造 active Change、done/total、openspec_status=进行态，并为 _change_task_progress 注入相同计数；逐行比较返回结果。执行不调用实际同步、不写业务文件、不请求 API。正式实现后增加持久化状态与端到端回归，按 acceptance.md 验收。

## 真实部署补证

待补证项：实际 context 请求及页面阶段。用于判断是否存在附加刷新问题，并作为修复后的真实观察验收。

操作：在目标项目需求中心开启 Network 并保留记录，分别采集启动前、门禁通过开始实施后、刷新后的 context 请求。返回三行对照表，包含时间、部署方式/版本、脱敏项目标识、method/path/status、条目 ID、stage、tasks、snapshot_revision，若有 request_id 一并返回。只提供摘要，不提供 Cookie、Authorization、完整请求头或原始会话日志。

## 影响与处置级别

REQ/BUG 共享路径均受影响。保留 medium / P2，常规 fix；暂无数据丢失、研发阻断或安全事故证据。引入版本尚未定位。BUG-0014 仅为案例，本缺陷未纳入其 Sprint 或 Change。
