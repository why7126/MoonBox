---
requirement_id: REQ-0039-requirement-center-card-chat-session-reuse
title: 需求中心卡片动作复用对象会话
terminal: web-catalog
version: v1
status: done
owner: product
source: capture.md
parent_requirement: REQ-0027-requirement-center-command-chain-realization
created_at: 2026-09-30 08:12:30
updated_at: 2026-10-06 00:21:08
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
  reason: 本需求改变需求中心卡片按钮触发 Chat 的会话选择、对象关联、治理动作候选创建和 turn 追加链路，涉及 Web 行为入口、后端请求日志和治理动作执行链路。
  validation: 后续 req-complete 与 OpenSpec Change 需补齐行为事件命名、请求日志字段、Task Trace 节点、脱敏 metadata、重复点击幂等和会话复用回归验证。
priority: P1
---

# 需求中心卡片动作复用对象会话

## 背景

需求中心卡片动作正在从“打开聊天抽屉并发送命令”升级为能承载对象上下文、治理候选、文件事实源写入和 Workflow Sync 的产品链路。当前同一 REQ、BUG 或 Change 如果每次点击卡片动作都新建 Chat，会导致上下文割裂、候选结果分散、用户难以追溯同一对象的治理过程。

另一方面，生成、完善、评审、入迭代和生成 OpenSpec 等治理动作虽然需要进入同一个对象会话承接上下文，但每次动作生成的 candidate 与 turn 都必须代表本次操作事实。若复用旧 candidate，会混淆用户本轮审阅结果、幂等边界和后续文件写入依据。

本需求作为 `REQ-0027-requirement-center-command-chain-realization` 的细化需求，聚焦“需求中心对象卡片动作如何选择 Chat 会话，以及生成类治理动作如何创建新的 candidate 与 turn”。

## 目标用户

- 产品负责人：从需求中心卡片连续分析、生成和完善同一对象时，希望回到同一对象会话，减少上下文重复说明。
- 项目负责人：检查 REQ、BUG、Change 的治理动作历史时，需要看到同一对象下连续 turn 与候选结果，便于复盘和追溯。
- 开发与测试协作者：围绕同一个 Change 或 Issue 讨论实现、验收、返修时，需要保留对象维度的会话连续性。
- 平台运维和治理维护者：需要明确会话复用、候选生成、幂等、观测和权限边界，避免动作重复写入或历史 candidate 被误用。

## 范围

### 包含

- 需求中心卡片按钮触发 Chat 时，按对象类型和对象 ID 查找可复用会话。
- 同一 REQ、BUG 或 Change 优先进入最近的未归档、未删除对象会话。
- 同一对象存在多个可用会话时，选择最新会话，并在 PRD 后续阶段固定排序事实源。
- 同一对象不存在可用会话时，创建新的 Chat 会话并写入对象关联。
- 生成类治理动作进入同一对象会话，但每次动作创建新的治理 candidate 和新的 turn。
- 历史 candidate 仅作为历史上下文和审阅记录，不作为本次生成、完善或流转动作的默认写入候选。
- 会话复用、candidate 新建、重复点击、权限校验和观测记录的产品约束。

### 不包含

- 不改变 REQ、BUG、Change 的评审、Sprint、OpenSpec、apply 或 archive 门禁。
- 不直接定义数据库表结构、API 字段、OpenAPI schema 或前端组件实现细节。
- 不建设完整 Chat 工作台能力，也不覆盖 Chat 工作台的通用会话管理、删除、归档和历史搜索能力。
- 不改变已归档会话、已删除会话或无权对象的访问策略。
- 不在本阶段创建 OpenSpec Change，不修改 `src/`、Sprint 四件套或正式规格。

## 功能要求

### FR-001 对象会话关联

需求中心卡片动作触发 Chat 时，系统必须基于对象类型和对象 ID 建立会话关联。对象类型至少覆盖 REQ、BUG 和 Change。对象关联不得只依赖前端临时参数；后端或持久化事实源必须能识别某个 Chat 会话属于哪个治理对象。

当用户从卡片动作进入 Chat 时，系统必须携带对象 ID、对象类型、标题、当前阶段和触发动作类型，作为会话查找、上下文注入和治理动作记录的基础。

### FR-002 优先复用最近可用会话

同一个 REQ、BUG 或 Change 通过需求中心卡片按钮触发 Chat 时，系统必须优先进入该对象最近的未归档、未删除会话。

可复用会话必须同时满足：

- 会话关联的对象类型和对象 ID 与当前卡片一致。
- 会话未归档。
- 会话未删除。
- 当前用户具备查看该对象和该会话的权限。
- 会话不处于会阻止继续交互的异常状态；异常状态的具体清单在后续设计阶段固定。

### FR-003 多会话选择最新会话

同一对象存在多个可复用会话时，系统必须选择最新会话。排序事实源在后续完善阶段固定，候选顺序为：

1. 最近 turn 更新时间。
2. 最近消息更新时间。
3. 会话 `updated_at`。

后续设计只能选择一个明确事实源或一组稳定降级顺序，不得由前端按本地列表顺序临时决定。若排序字段缺失或不可信，系统必须按明确降级策略处理，并保留可排障日志或观测记录。

### FR-004 不存在可用会话时新建

当同一对象不存在可复用会话时，系统必须创建新的 Chat 会话，并把该会话与当前对象关联。新建会话的标题、来源、首个上下文摘要和触发动作类型应能让用户识别其来自需求中心卡片动作。

创建失败时，系统不得静默打开无关联空会话，也不得把用户带入其他对象会话；必须展示失败原因，并允许用户重试。

### FR-005 生成类治理动作新建 candidate 与 turn

生成、完善、评审、加入迭代、生成 OpenSpec 等会产生治理候选、文件写入建议或状态流转建议的卡片动作，必须在目标对象会话内创建新的 turn。

其中生成类治理动作必须创建新的 candidate。系统不得默认复用旧 candidate 作为本次动作候选；旧 candidate 只能作为历史上下文、参考材料或用户显式选择的比较对象。

本轮 candidate 必须能追溯到本轮 turn、触发动作、对象 ID、对象类型和创建时间。

### FR-006 幂等与重复点击控制

同一用户对同一对象连续点击同一治理动作时，系统必须防止重复创建不可区分的 candidate 或重复 turn。前端必须在动作进行中锁定触发按钮；后端必须具备请求幂等或重复提交识别能力。

若重复请求已经创建了本轮 candidate，系统应返回同一轮结果或明确提示重复提交，不得悄悄生成多个等价候选。若用户明确再次发起新一轮动作，则必须生成新的 turn 和 candidate，并能与上一轮区分。

### FR-007 权限与状态边界

会话复用必须遵守对象权限、会话所有权或可见性规则。用户无权访问对象或会话时，不得进入该会话，不得泄漏会话标题、消息摘要、candidate 内容或对象正文。

已归档或已删除会话不得被自动复用。若对象自身已归档、已删除或处于不可操作阶段，卡片动作必须按对象状态展示只读、禁用或异常提示，不得通过会话复用绕过治理门禁。

### FR-008 历史 candidate 展示与使用边界

对象会话中可以展示历史 candidate，但必须区分历史结果和本轮结果。用户查看历史 candidate 时，系统不得把历史 candidate 标记为当前可提交结果，除非用户明确选择“基于历史结果重新生成”或等价动作。

若后续允许用户引用历史 candidate 作为新动作输入，必须生成新的 turn 和 candidate，并记录来源 candidate ID；不得直接修改历史 candidate 的审阅状态或写入结果。

### FR-009 异常与降级反馈

会话查找、新建、candidate 创建或 turn 追加失败时，系统必须给出明确反馈。反馈应区分权限不足、对象不存在、会话已归档、会话已删除、候选创建失败、重复提交、网络失败和服务端异常。

失败时不得误导用户认为治理动作已执行成功，不得刷新卡片阶段，不得写入需求、BUG、Change、Sprint 或 OpenSpec 事实源。

### FR-010 观测与审计

卡片动作触发 Chat、复用会话、新建会话、新建 turn、新建 candidate、重复提交拦截和失败分支都应具备可排障的观测记录。

观测记录必须遵守脱敏规则：不得写入完整 Prompt、完整回复、完整 candidate 正文、密钥、Cookie、Authorization header、本机绝对路径或真实客户敏感数据。允许记录对象类型、对象 ID、动作类型、会话 ID、turn ID、candidate ID、结果状态、错误码和耗时等脱敏摘要。

## UI 约束

- 从卡片动作进入 Chat 时，用户应感知自己进入的是当前对象会话，而不是普通空会话。
- 若复用已有会话，Chat 顶部或上下文区应展示当前对象标识、标题和最近动作摘要。
- 若创建新会话，应有明确的新会话初始状态，不得显示其他对象的历史消息。
- 生成类动作完成后，本轮 candidate 应与本轮 turn 贴近展示，并与历史 candidate 形成清晰区分。
- 按钮 Loading、禁用态和失败反馈不得造成卡片阶段提前流转。
- 长标题、长对象 ID、长 candidate 摘要必须截断或换行处理，不能撑破卡片、抽屉或聊天区。
- 归档、删除、无权或异常会话不得被隐藏式复用；需要在用户可理解的位置提示原因。

## 关联需求

- `REQ-0027-requirement-center-command-chain-realization`：父需求，定义需求中心卡片命令产品链路真实化。
- `REQ-0025-chat-workbench`：提供 Chat 工作台通用会话、消息、执行与权限能力背景。
- `REQ-0020-requirement-center-card-document-actions-ai-chat`：定义需求中心卡片动作、文档入口和 AI 聊天增强的基础交互。
- `REQ-0029-capture-multimodal-candidate-review`：提供 candidate 审阅、确认创建和幂等采集的相关经验背景。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
  reason: 本需求改变需求中心卡片按钮触发 Chat 的会话选择、对象关联、治理动作候选创建和 turn 追加链路，涉及 Web 行为入口、后端请求日志和治理动作执行链路。
  validation: 后续 req-complete 与 OpenSpec Change 需补齐行为事件命名、请求日志字段、Task Trace 节点、脱敏 metadata、重复点击幂等和会话复用回归验证。
```

## 状态块

```yaml
status: done
generated_at: 2026-09-30 08:12:30
completed_at: 2026-09-30 08:17:31
reviewed_at: 2026-09-30 08:24:32
approved_at: 2026-09-30 08:24:32
source_material:
  - capture.md
  - related_requirement: REQ-0027-requirement-center-command-chain-realization
  - related_requirement: REQ-0025-chat-workbench
  - related_requirement: REQ-0020-requirement-center-card-document-actions-ai-chat
next: /opsx-apply REQ-0039-requirement-center-card-chat-session-reuse
iteration: sprint-008
openspec_change: add-requirement-center-card-chat-session-reuse
```
