---
requirement_id: REQ-0039-requirement-center-card-chat-session-reuse
title: 需求中心卡片动作复用对象会话业务流程
document_status: ready
created_at: 2026-09-30 08:17:31
updated_at: 2026-09-30 08:17:31
owner: product
source: requirement.md
priority: P1
parent_requirement: REQ-0027-requirement-center-command-chain-realization
---

# 需求中心卡片动作复用对象会话业务流程

## 主流程

```text
用户在需求中心点击对象卡片动作
  -> 读取对象类型、对象 ID、标题、阶段和动作类型
  -> 校验对象权限与动作门禁
  -> 查询该对象关联的未归档、未删除会话
  -> 过滤当前用户无权访问或不可继续交互的会话
  -> 是否存在可用会话？
       ├─ 是：按排序事实源选择最新会话
       └─ 否：创建新的对象 Chat 会话
  -> 打开对象会话并追加本轮 turn
  -> 是否为生成类治理动作？
       ├─ 是：创建新的 candidate，并关联本轮 turn
       └─ 否：仅承载分析、只读上下文或普通回复
  -> 展示本轮反馈、candidate 或异常结果
```

## 生成类治理动作流程

```text
卡片触发生成类治理动作
  -> 前端锁定当前动作按钮
  -> 请求携带对象、动作、幂等标识和会话上下文
  -> 后端校验对象权限、会话权限和治理门禁
  -> 复用或创建对象会话
  -> 创建本轮 turn
  -> 创建本轮 candidate
  -> 返回 candidate 审阅入口和执行反馈
  -> 用户审阅后再进入后续治理写入链路
```

生成类治理动作包括但不限于生成需求、完善需求、评审建议、加入迭代建议、生成 OpenSpec 候选和类似会产生文件写入或状态流转建议的动作。

## 异常流程

| 异常 | 系统行为 |
|---|---|
| 对象不存在 | 阻止进入会话，提示对象不可用，不写入治理事实源 |
| 用户无对象权限 | 阻止进入会话，不泄漏对象正文、会话标题或 candidate 摘要 |
| 会话已归档 | 不自动复用；按对象状态提示新建或只读策略 |
| 会话已删除 | 不自动复用；必要时创建新会话 |
| 会话状态不可继续交互 | 阻止生成类动作，提示恢复、刷新或创建新会话 |
| candidate 创建失败 | 保留会话和 turn 状态，提示失败原因，不刷新卡片阶段 |
| 重复点击 | 返回既有处理中结果、同一幂等结果或明确重复提交提示 |

## 与父需求差异

`REQ-0027-requirement-center-command-chain-realization` 定义需求中心卡片命令真实化的总体目标，包括分析、生成、完善、评审、入迭代、生成 OpenSpec、开始开发和完成归档等动作接入后端 controller、文件事实源和 Workflow Sync。

本需求只细化其中的 Chat 会话复用和 candidate 生成策略：

- 父需求关注“动作能真实执行并写入正确事实源”。
- 本需求关注“动作进入哪个对象会话，以及每次生成类动作如何产生新的 turn 与 candidate”。
- 本需求不改变父需求中的治理门禁和阶段流转规则。

## 数据与观测流

```text
Web 卡片动作
  -> usage_events 记录脱敏行为摘要
  -> API 请求生成 request_id 并写 request_logs
  -> 生成类动作写入 task_traces
  -> 关键步骤写入 task_trace_spans 或等价节点摘要
  -> Chat 会话、turn、candidate 保存业务事实
```

观测 metadata 只保存对象类型、对象 ID、动作类型、会话 ID、turn ID、candidate ID、结果状态、错误码、耗时和数量类字段，不保存完整 Prompt、完整回复、完整 candidate 正文或敏感凭证。

## 状态块

```yaml
document_status: ready
source_material:
  - requirement.md
  - capture.md
next: /sprint-propose --req REQ-0039-requirement-center-card-chat-session-reuse
```
