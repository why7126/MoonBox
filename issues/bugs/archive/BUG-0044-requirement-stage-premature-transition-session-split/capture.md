---
bug_id: BUG-0044-requirement-stage-premature-transition-session-split
title: 需求中心阶段提前迁移并开放后续动作导致同一对象会话分裂
status: done
created_at: '2026-10-19 10:56:47'
updated_at: 2026-10-19 13:55:20
severity: high
environment: local
owner: 产品团队
source: BUG-0028 操作案例及同会话 explore
lifecycle_stage: plan
related_requirement: REQ-0012-frontend-requirement-center
related_bug: BUG-0028-requirement-center-card-owner-raw-user-id
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

已有时间线与代码可解释本次会话分裂机制；正式根因文档、全入口运行态矩阵、并发边界及恢复规则留待 bug-generate / bug-complete 补齐。本 Capture 不推进评审。

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
- N/A：本次 Capture 不改变 schema、保留周期、API 契约、客户端生成物、部署或对象存储；具体实现影响需在 Change 中评估。禁止记录完整 Prompt、凭证和真实用户标识。
