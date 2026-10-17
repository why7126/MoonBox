---
title: 需求中心卡片动作复用对象 Chat 会话设计
change_id: add-requirement-center-card-chat-session-reuse
source_requirement: REQ-0039-requirement-center-card-chat-session-reuse
created_at: 2026-09-30 08:37:58
updated_at: 2026-09-30 08:37:58
owner: MoonBox 产品团队
---

# 需求中心卡片动作复用对象 Chat 会话设计

## 背景与现状

现有需求中心已经具备卡片阶段动作、AI 聊天抽屉和 Chat 工作台对象关联能力，但卡片动作触发 Chat 时缺少统一的对象会话复用策略。REQ、BUG、Change 的同一对象多次执行生成类治理动作时，容易出现多个会话分叉，或者旧 candidate 被误认为本轮候选。

本 Change 聚焦对象维度的会话选择和生成类治理动作候选边界：会话可以复用，turn 和 candidate 必须按动作轮次新建。

## 目标

- 同一 REQ、BUG 或 Change 从需求中心卡片触发 Chat 时，优先进入该对象最近的未归档、未删除且用户有权访问的会话。
- 多个可用会话存在时，使用服务端稳定排序选择最新会话，不依赖前端本地列表顺序。
- 不存在可用会话时，新建对象 Chat 会话并写入对象关联。
- 生成类治理动作进入同一对象会话，但每次创建新的 turn 和 candidate。
- 旧 candidate 仅用于历史上下文或用户显式引用，不作为本次动作默认写入候选。
- 权限、对象状态、会话状态、幂等和观测脱敏在接口与验收中有明确边界。

## 非目标

- 不改变 REQ、BUG、Change、Sprint 或 OpenSpec 的评审和流转门禁。
- 不建设完整 Chat 工作台历史管理能力。
- 不改变已归档、已删除或无权会话的访问策略。
- 不在本 Change 中落地真实执行实现；实现阶段由 `/opsx-apply REQ-0039-requirement-center-card-chat-session-reuse` 执行。

## 设计方案

### 对象会话选择

卡片动作触发 Chat 时，前端请求必须携带对象类型、对象 ID、标题、当前阶段、触发动作类型和幂等标识。服务端以对象类型和对象 ID 查询对象会话关联，并过滤：

- 会话未归档。
- 会话未删除。
- 当前用户具备对象和会话访问权限。
- 会话不处于阻断继续交互的异常状态。

排序事实源采用稳定降级顺序：

1. 最近 turn 更新时间。
2. 最近消息更新时间。
3. 会话 `updated_at`。
4. 会话创建时间或 ID 作为最后稳定降级，不得使用前端本地列表顺序。

命中可用会话时返回会话 ID 和对象上下文摘要；未命中时创建新的对象会话，并写入来源为需求中心卡片动作。

### turn 与 candidate 策略

分析、普通问答或只读上下文动作可以只追加普通 turn。生成、完善、评审、加入迭代、生成 OpenSpec 等会产生治理候选、文件写入建议或状态流转建议的动作必须：

- 在目标对象会话内创建新的 turn。
- 创建新的 candidate，并关联本轮 turn、对象类型、对象 ID、动作类型、操作者和创建时间。
- 保留旧 candidate 为历史上下文或显式引用来源。
- 禁止默认把旧 candidate 标记为本轮候选或本轮可提交结果。

重复点击时，前端必须锁定动作按钮；后端必须用幂等键识别同一轮请求。若同一轮 candidate 已创建，返回同一轮结果或重复提交提示。用户明确再次发起新一轮动作时，必须使用新的幂等键并创建新的 turn 与 candidate。

### UI Contract

- Chat 顶部或上下文区展示当前对象类型、对象 ID、标题和最近动作摘要。
- 复用已有会话时，不显示其他对象上下文；新建会话时展示明确空态。
- 本轮 candidate 与本轮 turn 贴近展示，历史 candidate 使用历史标签、时间和来源 candidate ID 区分。
- 卡片动作进行中显示 loading 并禁用本动作按钮；失败时不刷新卡片阶段。
- 长标题、长对象 ID 和长 candidate 摘要需要截断或换行，不得撑破卡片、抽屉或聊天区。
- 本 REQ 无 prototype 目录，不触发原型拆解、UI Skeleton 首轮确认或 UI Reference Replication Contract；实现阶段仍需按需求中心和 Chat 既有 Ops 视觉系统验证深浅主题、窄屏和文本溢出。

### 异常与权限

对象不存在、对象无权、会话无权、会话已归档、会话已删除、会话状态不可继续、candidate 创建失败、重复提交、网络失败和服务端异常必须返回可区分错误码或错误摘要。失败分支不得写入 REQ、BUG、Change、Sprint 或 OpenSpec 事实源，不得移动卡片阶段。

## 数据与 API

接口设计需覆盖以下语义，字段命名由实现阶段结合现有 schema 固化：

- 输入：对象类型、对象 ID、标题、阶段、动作类型、幂等键、当前会话上下文、行为链路字段。
- 输出：会话选择结果、新建或复用标识、turn ID、candidate ID、历史 candidate 摘要、本轮 candidate 状态、错误码和脱敏提示。
- 持久化：对象会话关联、turn、candidate、幂等记录、来源 candidate ID 和状态时间。
- OpenAPI / Orval / API 文档：若新增或修改 REST API、请求头、响应字段或错误码，必须同步 OpenAPI、前端客户端生成物和 `docs/03-api-index.md`。
- 数据库：若新增或修改表、字段、索引、迁移或保留周期，必须同步 SQLite/MySQL schema、迁移脚本、`docs/04-database-design.md` 和相关测试。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers:
    - usage_events
    - request_logs
    - task_traces
  reason: 本变更改变需求中心卡片按钮触发 Chat 的会话选择、对象关联、治理动作候选创建和 turn 追加链路，涉及 Web 行为入口、后端请求日志和治理动作执行链路。
  validation: 实现阶段需验证卡片动作触发、复用会话、新建会话、新建 turn、新建 candidate、重复提交拦截和失败分支均记录脱敏摘要；metadata 不得保存完整 Prompt、完整回复、完整 candidate 正文、对象正文、密钥、Cookie、Authorization header、本机绝对路径或真实客户敏感数据。
```

## 冲突处理

本 REQ 无 prototype、附件 HTML、截图或参考稿；冲突优先级为 `acceptance.md` > `requirement.md` > `rules/ui-design.md` > 已生效 OpenSpec。若实现中发现既有 Chat 工作台会话历史策略与本 Change 冲突，以本 Change 的对象会话复用和 candidate 新建要求作为增量约束，不覆盖通用 Chat 会话历史能力。

## 风险

- 会话排序事实源不一致 → 服务端固定排序降级顺序，并在 request_logs 或 Task Trace 中记录脱敏选择摘要。
- 重复点击产生多个不可区分 candidate → 前端按钮锁定与后端幂等键双重控制。
- 权限错误导致会话摘要泄漏 → 对象权限和会话权限分别校验，失败时只返回受控错误码。
- 历史 candidate 被误提交 → UI 明确区分历史与本轮，提交 API 只接受本轮 candidate 或显式引用生成的新 candidate。
- 观测误存敏感内容 → 只记录 ID、类型、数量、状态、错误码和耗时等脱敏摘要。

## 回滚方案

若实现阶段出现严重问题，可临时回退到“按动作打开普通 Chat 入口但不自动执行生成类治理动作”的保守模式，并禁用生成类动作的 candidate 写入入口；不得继续复用不可验证的旧 candidate，也不得绕过治理门禁。
