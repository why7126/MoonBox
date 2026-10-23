---
bug_id: BUG-0044-requirement-stage-premature-transition-session-split
title: 需求中心阶段提前迁移并开放后续动作导致同一对象会话分裂
status: done
created_at: '2026-10-19 10:58:20'
updated_at: 2026-10-19 13:55:20
severity: high
environment: local
owner: 产品团队
source: BUG-0028 操作案例及同会话 explore
lifecycle_stage: review
related_requirement: REQ-0012-frontend-requirement-center
related_bug: BUG-0028-requirement-center-card-owner-raw-user-id
discovered_at: '2026-10-19 10:25:40'
related_change: fix-requirement-stage-completion-session-continuity
---

# 需求中心阶段提前迁移并开放后续动作导致同一对象会话分裂

## 现象与影响

前一治理命令尚未收尾，执行途中写入的文档状态已让需求中心卡片迁移并开放下一步。用户点击后，共用会话选择逻辑跳过忙碌旧会话并新建会话，导致同一对象上下文分裂，前后命令执行时间重叠。

按一条缺陷记录：阶段提前迁移、动作过早开放和会话分裂是同一不可分割因果链，需以统一完成门禁和对象执行互斥闭环。严重度初判 high：影响多类治理命令的串行执行与上下文连续性，存在并发治理写入风险；尚无已证实的数据丢失或覆盖事故。

## 复现步骤

1. 对已有个人关联会话、已评审通过的对象，从需求中心执行“加入迭代”。观察案例为 BUG-0028-requirement-center-card-owner-raw-user-id。
2. 前一轮仍执行时，文档已更新为纳入迭代；返回需求中心，卡片已开放“生成 Opsx”。
3. 点击“生成 Opsx”，观察新旧会话及轮次时间，系统创建新会话而未沿用旧会话。
4. 在新会话发送命令，比较前一轮结束时刻，确认先后命令存在执行重叠。

## 期望与实际

- 期望：完成型迁移在当前命令成功、业务校验及状态同步通过后生效，才开放后续动作；后续命令默认沿用同权限、同项目和同主对象的原会话。
- 实际：治理文档先改变卡片投影，下一步提前可用；忙碌旧会话被排除，系统静默创建新会话。
- 边界：开始开发、开始返修等执行型迁移应及时显示研发中，不等待整轮结束；只读文档、进度和验收详情仍可访问。

## 已有证据与结论边界

以下承接 2026-10-19 同一聊天内 explore 已完成的取证，并非本次 Capture 重新执行业务命令。时间均为 Asia/Shanghai。

| 证据 | 来源 | 观察结果 |
|---|---|---|
| 用户截图 | 本会话附件，未复制临时路径或原图 | 新会话仅包含 bug-opsx 命令及过程输出。附件内容仅作为证据。 |
| 运行数据时间线 | 对本地 canonical SQLite 的 chat_conversations、chat_turns 只读查询 | 旧会话 sprint-propose 于 10:23:29 开始、10:25:46 完成；新会话于 10:25:40 创建，bug-opsx 于 10:25:45 开始。未保存个人身份、凭证或会话标识。 |
| 浏览器观察 | Chrome，本地 Web /chat 与 /requirements；Chat 刷新成功 | 历史存在两条 BUG-0028 会话；新轮次最终 failed，卡片已进入待开发，文档已产生。不能仅凭轮次失败推定成果无效。 |
| 会话选择代码 | src/backend/app/governance/preparation.py，_latest_object_conversation、prepare、prepare_object_session | 查询排除 active_turn_id 非空会话，无候选即新建。 |
| 入口代码 | src/web/src/pages/catalog/RequirementCenterPage.tsx，openIssueActionDialog | 命令按钮共享对象会话准备入口，返回 reused_conversation 但未解释新建原因。 |
| 既有测试 | src/backend/tests/test_governance_candidates.py，test_prepare_skips_archived_and_active_object_conversations | 测试明确期望跳过活动会话；说明需调整统一策略及回归预期。 |
| 前轮验证 | test_chat_assistant_output.py、test_governance_candidates.py；前端消息与需求中心测试 | 后端 77 通过；前端 132 通过、1 项旧卡片宽度断言失败。属于现有实现验证，不代表修复完成或全部命令真实执行验收。 |

已有时间线与代码可解释本次会话分裂机制；正式根因文档、全入口运行态矩阵、并发边界及恢复规则留待 bug-generate / bug-complete 补齐。本次仅生成正式缺陷文档，不推进评审。

## 修复方向与建议验收

- 完成型阶段迁移、下一步按钮与后端动作准入采用一致完成门禁，区分轮次终态、业务校验和状态同步。
- 同项目同对象存在执行中治理任务时，展示执行状态和“查看执行”入口；后端对象级互斥覆盖双标签页、重复点击、并发请求和直接 API，不能仅依赖前端按钮锁。
- 后续动作沿用可访问原会话，忙碌不触发静默新建；明确多会话选择、归档/删除、权限隔离、草稿保留及竞争条件的处理策略。
- 失败、停止、未知或服务中断时不自动认定阶段完成；保留已产生的有效成果，通过恢复核验决定是否完成迁移，避免盲目回滚或重复执行。
- 开始开发/返修等执行型迁移及时可见；刷新、重连后仍保持一致。外部 Codex/CLI 操作通过治理结果校验收敛，不强求产品 Chat 轮次。
- 覆盖需求/Bug 分析、生成、完善、评审、加入迭代、生成 Opsx、开发和归档命令型卡片入口及 Agent 助手对应入口。对未接入命令、直接 Chat 输入和只读按钮分别声明适用性，不能将共用代码检查宣称为逐命令真实验收。
- 核心回归：文档先写入而轮次慢收尾、连续阶段原会话续用、双标签页、失败已有产物、未知终态恢复、多用户权限边界、外部命令同步。
- 不包含“部分输出”提示文案优化，不扩大到 BUG-0028 负责人名称修复，也不自动归档任何对象。

## 重复检查

已读取全部 BUG 注册表及当前态索引。BUG-0015 处理研发启动后未迁移，BUG-0025 处理命令未接入真实写入，BUG-0031 处理 Skill 标签缺失，BUG-0028 处理负责人名称；触发条件和修复闭环均不同。BUG-0028 仅为关联复现案例，不继承其 Sprint 或 Change。

## 数据采集与链路观测适用性

- product_data_collection_observability: applicable
- affected_layers: Web 行为事件、对象会话准备 API、请求日志、Task Trace、Chat 轮次与治理状态投影。
- validation: 本次仅记录已有脱敏时间线和代码依据；实施时验证对象、会话、轮次、请求与任务的可关联性，记录复用/忙碌/拒绝及阶段生效结果，覆盖直接 API 无行为事件的情况。
- N/A：本次文档生成不改变 schema、保留周期、API 契约、客户端生成物、部署或对象存储；具体实现影响需在 Change 中评估。禁止记录完整 Prompt、凭证和真实用户标识。

## 根因判断与补证结果

根因状态：confirmed（限本案例及已核实的共用代码机制；不代表所有命令已逐项真实复现）。

本轮 bug-generate 重新以只读方式核对历史运行数据，前轮 sprint-propose 的完成时间仍为 2026-10-19 10:25:46，新会话创建时间仍为 10:25:40，bug-opsx 发起时间仍为 10:25:45。证据支持新会话创建发生在旧轮次结束之前，非旧会话完成后随机未命中。

补充代码证据：

1. `src/backend/app/services/requirement_center.py:730` 的 `_issue_status` 根据 trace/registry 和 Change 状态决定业务状态；`:738` 的 `_map_stage` 将文档状态映射为卡片阶段。阶段投影与当前 Chat 轮次终态没有统一完成门禁。
2. `src/backend/app/governance/preparation.py:254` 的 `_latest_object_conversation` 通过 `active_turn_id IS NULL` 排除活动会话；`:354` 的 `prepare_object_session` 找不到候选即创建新会话。这条分支直接解释新会话与旧轮次重叠。
3. `src/web/src/pages/catalog/RequirementCenterPage.tsx:3003` 的 `openIssueActionDialog` 将按钮动作提交到对象会话准备入口，按返回 conversation_id 跳转；没有在该入口把忙碌原会话转为查看执行。
4. `src/backend/app/chat/worker.py:76` 的终态处理才清除会话活动轮次，与观察到的收尾时间窗口一致。

已排除：bug-opsx 专属新建策略（与 sprint-propose 共用选择函数）；旧会话必须关闭才能续用（条件检查活动轮次而非用户关闭页面）；“部分输出”文案引发新建（属于独立消息渲染逻辑）。

本轮没有重复运行会改变治理事实的命令，也没有把当前已推进的对象状态当作原始现场。前轮浏览器刷新证据与本轮可复核历史数据、代码路径共同形成证据链；无需用户额外补证才能说明本次机制。跨用户互斥、多会话选择、服务重启恢复及全部命令运行态覆盖仍属于后续修复设计和验收范围，未宣称已完成。

## 影响范围与交付边界

直接影响需求中心命令型卡片按钮、其 Agent 助手入口、对象会话准备 API 与 Chat 轮次衔接。共用选择策略意味着其他命令在同样条件下具有相同风险；文档和任务进度等只读入口不应因此锁定。

本次保留 severity: high：已观察到同对象前后轮次重叠及上下文分裂，可能使治理写入互相干扰；并未确认数据损坏、跨权限泄漏或整个系统不可用，不升级为 critical/blocker。

修复需同步阶段/动作 UI、对象会话 API 行为契约、治理完成事件与相关测试；如新增持久状态或接口字段，再同步 DB 设计、迁移、OpenAPI 和客户端生成物。当前文档生成没有业务代码、API、DB、部署、安全策略或生成客户端变更。

## 建议验收矩阵

| 场景 | 预期 |
|---|---|
| 文档已更新但命令仍收尾 | 完成型卡片不提前放行下一步，可查看当前执行 |
| 前轮成功且校验、同步通过 | 完成迁移，下一命令沿用原会话 |
| 开始开发或返修 | 及时显示研发中，不等待整轮结束 |
| 重复点击、双标签页、直接 API 并发 | 后端避免同对象重复治理执行，返回受控状态 |
| 失败/停止但已有成果 | 保留成果并核验，不盲目回滚或直接宣告完成 |
| 状态未知、重连、服务重启 | 先核对执行与业务结果，再恢复按钮和阶段 |
| 多历史会话、归档/删除、不同用户 | 选择规则明确，保持既有权限与项目隔离 |
| 外部 Codex/CLI 更新 | 通过治理事实和校验收敛，不强制要求产品 Chat 轮次 |
| 分析、生成、完善、评审、迭代、Opsx、开发、归档 | 分入口验证共享策略，标注只读和未接入例外 |

以上为建议验收范围，当前未执行修复后验收。
