---
title: 需求中心卡片动作复用对象 Chat 会话提案
change_id: add-requirement-center-card-chat-session-reuse
source_requirement: REQ-0039-requirement-center-card-chat-session-reuse
change_type: add
created_at: 2026-09-30 08:37:58
updated_at: 2026-09-30 08:37:58
owner: MoonBox 产品团队
---

# 需求中心卡片动作复用对象 Chat 会话提案

## 背景

需求中心卡片动作正在从“打开聊天抽屉并发送命令”升级为可追溯的治理执行入口。同一个 REQ、BUG 或 Change 多次从卡片触发 Chat 时，如果每次都创建新会话，会让上下文、候选结果和后续写入依据分散，用户难以复盘同一对象的治理过程。

同时，生成、完善、评审、加入迭代和生成 OpenSpec 等生成类治理动作即使进入同一个对象会话，也必须为本轮动作创建新的 turn 和 candidate。旧 candidate 只能作为历史上下文，不得被默认复用为本轮候选。

## 变更内容

- 为需求中心卡片动作增加对象会话选择规则：按对象类型和对象 ID 优先进入最近的未归档、未删除且当前用户有权访问的会话。
- 当同一对象存在多个可用会话时，按稳定事实源选择最新会话，并保留可排障的选择依据。
- 当不存在可用会话时，创建新的对象 Chat 会话，并写入对象关联、来源和触发动作摘要。
- 对生成类治理动作统一要求在目标对象会话内创建新的 turn 和新的 candidate，不复用旧 candidate。
- 增加重复点击、幂等、权限、失败反馈和脱敏观测约束，防止阶段提前流转或治理事实源被错误写入。

## 能力影响

### 新增能力

无。本变更扩展需求中心卡片动作与 Chat 工作台既有能力，不新增独立 capability。

### 修改能力

- `web-catalog-requirement-center`：扩展卡片动作触发 Chat 的对象会话复用、生成类动作新建 candidate 与失败不流转要求。
- `web-catalog-chat-workbench`：扩展对象会话关联、最新会话选择、turn/candidate 追溯、幂等和观测脱敏要求。

## 影响范围

```yaml
impact:
  backend: true
  web: true
  miniapp: false
  admin: false
  database: true
  storage: false
  api: true
capabilities:
  new: []
  modified:
    - web-catalog-requirement-center
    - web-catalog-chat-workbench
```

- Web：需求中心卡片动作、Chat 抽屉或工作台入口、按钮 loading/禁用态、候选展示和失败反馈。
- API：卡片动作触发 Chat 的准备或执行接口需要携带对象、动作、幂等和会话上下文，并返回会话、turn、candidate 或错误摘要。
- 数据库：需要持久化或复用 Chat 会话与治理对象关联、turn、candidate、幂等键和历史 candidate 边界。
- 观测：适用 `usage_events`、`request_logs`、`task_traces`，按脱敏摘要记录触发、复用、新建、失败和重复提交分支。
