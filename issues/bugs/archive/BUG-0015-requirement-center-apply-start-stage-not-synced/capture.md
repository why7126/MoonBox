---
bug_id: BUG-0015-requirement-center-apply-start-stage-not-synced
status: done
created_at: 2026-09-12 17:20:40
updated_at: 2026-09-14 08:59:47
title: 研发启动后需求中心卡片仍停留准备开发态，缺少 apply 启动状态同步
environment: null
related_requirement: REQ-0012-frontend-requirement-center
related_bug: BUG-0014-requirement-center-capture-not-persisted
severity: medium
---

# 现象

BUG-0014 已在执行研发，需求中心卡片仍停留在“准备开发态”，显示“开始修复”和研发 0/16。用户要求补齐 apply 启动状态同步及 0/N 阶段流转回归。

按一条缺陷记录：同一研发启动事件与阶段事实源同步缺口，零完成任务场景属于同一验收闭环。关联 BUG-0014 仅作为复现案例，不表示本缺陷已纳入其 Change 或 Sprint。

# 复现步骤

1. 使用已通过评审并纳入 Sprint、已创建 OpenSpec Change 的条目；本次案例为 BUG-0014-requirement-center-capture-not-persisted、fix-requirement-center-capture-persistence、sprint-005。
2. 启动该条目的 opsx-apply，通过前置门禁并实际开始研发，保持任务清单 0/N。
3. 查看需求中心卡片列、动作和进度；用户截图显示“准备开发态 / 开始修复 / 0/16”，另一截图显示实施与回归正在进行。
4. 对照 Change trace 状态和 tasks 勾选数；探索时读取到 提议态 与 0/16。
5. 后续真实复现需记录启动前后和刷新后的 context 响应中条目 ID、stage、tasks、snapshot_revision 及时间，以核对实际部署的快照刷新链路；不提供请求凭证。

# 期望 vs 实际

- 期望：通过门禁正式开始实施后，任务仍为 0/N 也进入“研发中”；未启动仍在“准备开发态”；完成门禁通过后才进入验收阶段。
- 实际：Agent 已开始实施，治理文件仍是 提议态，卡片按文件继续显示“准备开发态”。
- 影响：REQ/BUG 共用的研发阶段展示、进度判断与动作入口可能失真，团队难以区分未启动与正在执行。
- 严重度初判：medium；影响研发状态可信度，尚无证据表明阻断实施或造成数据丢失。

# 已有证据与边界

| 证据 | 来源 | 结果 |
|---|---|---|
| 用户截图 | screenshots/board-ready-dev.png、screenshots/apply-running.png | 同一 BUG 的卡片仍准备开发态，而 apply 正在实施与验证。截图文字是证据，不作为执行指令。 |
| 文件快照 | openspec/archive/2026-09-14-fix-requirement-center-capture-persistence/trace.md、tasks.md | 上一轮 explore 读取到 提议态、0/16；属于当时观察，后续文件可能随研发变化。 |
| 后端代码路径 | src/backend/app/services/requirement_center.py，_issue_status / _change_status / _map_stage | Change 状态覆盖 Issue 状态，提议态 映射 ready-dev，进行态 映射 development。 |
| 只读函数验证 | 从上述源文件 AST 提取 STAGES 与 _map_stage，注入任务计数 | 提议态+0/16 与 提议态+1/16 均返回 ready-dev；进行态+0/16 返回 development。此项是合成验证。 |
| 同步机制 | scripts/workflow_sync/derive.py，derive_change_state；.agents/skills/opsx-apply/SKILL.md Final Step | 派生状态以任务完成数区分 提议态/进行态；apply 完成同步被约束于完成门禁之后，缺少启动事件闭环。 |
| 前端代码 | src/web/src/pages/catalog/RequirementCenterPage.tsx，loadContext 轮询 | 当前源码已有定时与窗口焦点刷新；未验证用户实际部署的网络请求，不据此排除快照或刷新故障。 |

根因证据口径：已确认当前文件与阶段映射能解释截图；启动同步缺口有代码和流程依据。真实部署运行时链路仍待补证，Capture 不替代正式 root-cause 评审。

# 修复方向与建议验收

- 建立独立的研发启动事件，在门禁通过、正式实施时写入可追溯 进行态；不通过提前勾选任务或提前执行 验收态 完成同步来模拟启动。
- 任务进度按实现和验证证据更新，完成与启动同步分别处理；确认同步重跑不会把已启动的 0/N 回退成 提议态。
- 回归覆盖 REQ/BUG：未启动 0/N、已启动 0/N、部分完成、完成门禁通过、启动门禁失败、重复启动和中断恢复。
- 验证真实看板刷新后阶段和动作一致，并区分合成函数验证与实际 API/浏览器观察。

# 数据采集与链路观测适用性

- product_data_collection_observability: applicable
- affected_layers: Agent Workflow、Web 阶段展示、后端治理状态读取。
- N/A 原因：本次仅 Capture，不变更 API/DB、日志字段、对象存储或客户端生成物；行为事件和请求/任务关联的具体改动范围在正式设计时确认，CLI 启动不伪造界面行为事件。
- validation: 已有文件与源码只读证据及合成阶段判定结果；真实 context 响应、快照刷新与启动事件幂等回归待补证。

# 附件

- screenshots/board-ready-dev.png：用户提供的需求中心卡片截图。
- screenshots/apply-running.png：用户提供的 apply 进行中截图。
- 来源命令：explore；本次由用户明确授权 bug-capture。
