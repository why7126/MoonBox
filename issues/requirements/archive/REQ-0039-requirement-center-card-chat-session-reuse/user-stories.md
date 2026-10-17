---
requirement_id: REQ-0039-requirement-center-card-chat-session-reuse
title: 需求中心卡片动作复用对象会话用户故事
document_status: ready
created_at: 2026-09-30 08:17:31
updated_at: 2026-09-30 08:17:31
owner: product
source: requirement.md
priority: P1
parent_requirement: REQ-0027-requirement-center-command-chain-realization
---

# 需求中心卡片动作复用对象会话用户故事

## 用户故事

### US-001 复用同一对象会话

作为产品负责人，我希望从同一个 REQ、BUG 或 Change 卡片再次触发 Chat 时，优先回到该对象最近的可用会话，以便继续承接上下文，而不是每次都从空会话开始。

验收要点：

- 同一对象再次触发 Chat 时，系统按对象类型和对象 ID 查找会话。
- 未归档、未删除且有权限的最近会话被优先打开。
- 不存在可用会话时才新建对象会话。
- 被归档、删除或无权访问的会话不会被自动复用。

### US-002 多会话选择最新会话

作为项目负责人，我希望同一对象存在多个可用会话时，系统稳定进入最新会话，以便减少上下文分叉和误操作。

验收要点：

- 系统使用明确排序事实源选择最新会话。
- 排序字段缺失时有稳定降级策略。
- 选择结果不依赖前端本地列表顺序。
- 会话选择结果可通过日志或观测摘要排查。

### US-003 生成类动作创建新候选

作为治理执行者，我希望生成、完善、评审、入迭代或生成 OpenSpec 等动作进入同一对象会话，但每次生成新的 candidate 和 turn，以便每次动作都有独立审阅和写入依据。

验收要点：

- 每次生成类动作都会创建新的 turn。
- 每次生成类动作都会创建新的 candidate。
- 旧 candidate 不会被默认复用为本次动作候选。
- 新 candidate 能追溯到本轮 turn、对象、动作和创建时间。

### US-004 防止重复点击造成重复候选

作为用户，我希望动作执行中按钮被锁定，重复点击不会产生多个不可区分的候选，以便避免重复审阅和错误写入。

验收要点：

- 前端在动作执行中禁用对应按钮并展示处理中状态。
- 后端能识别重复提交或幂等键。
- 重复提交不会悄悄创建多个等价 candidate。
- 用户明确再次发起新一轮动作时，新 turn 与新 candidate 可与上一轮区分。

### US-005 保持权限与状态边界

作为空间成员，我希望系统只复用我有权访问的对象会话，并且不会通过 Chat 入口绕过需求、缺陷或 Change 的治理门禁。

验收要点：

- 无对象权限或会话权限时，不进入会话且不泄漏摘要。
- 对象处于不可操作阶段时，卡片动作按门禁禁用或只读。
- 会话复用不改变 REQ、BUG、Change、Sprint 或 OpenSpec 状态。
- 失败分支不刷新卡片阶段，不写入治理事实源。

### US-006 保留可排障观测

作为平台运维和治理维护者，我希望会话复用、新建会话、新建 turn、新建 candidate 和失败分支都有脱敏观测记录，以便定位问题而不泄漏敏感内容。

验收要点：

- 观测记录包含对象类型、对象 ID、动作类型、会话 ID、turn ID、candidate ID、结果状态、错误码和耗时等脱敏摘要。
- 不记录完整 Prompt、完整回复、完整 candidate 正文、密钥、Cookie、Authorization header、本机绝对路径或真实客户敏感数据。
- 行为事件、请求日志和 Task Trace 的适用范围在后续 Change 中继续细化。

## 状态块

```yaml
document_status: ready
source_material:
  - requirement.md
  - capture.md
next: /sprint-propose --req REQ-0039-requirement-center-card-chat-session-reuse
```
