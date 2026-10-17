---
requirement_id: REQ-0039-requirement-center-card-chat-session-reuse
title: 需求中心卡片动作复用对象会话验收标准
acceptance_status: passed
created_at: 2026-09-30 08:17:31
updated_at: 2026-10-17 16:45:27
owner: product
source: requirement.md
priority: P1
parent_requirement: REQ-0027-requirement-center-command-chain-realization
---

# 需求中心卡片动作复用对象会话验收标准

## 功能 AC

- [ ] AC-001 对象会话关联：从 REQ、BUG 或 Change 卡片触发 Chat 时，请求必须携带对象类型、对象 ID、标题、阶段和动作类型，并能在后端或持久化事实源识别该会话属于当前治理对象。
- [ ] AC-002 会话复用过滤：系统只复用与当前对象匹配、未归档、未删除、当前用户有权访问且允许继续交互的会话。
- [ ] AC-003 不存在可用会话时新建：当同一对象没有可复用会话时，系统创建新的对象会话；创建失败时不得进入无关联空会话或其他对象会话。
- [ ] AC-004 多会话选择最新：同一对象存在多个可复用会话时，系统按明确排序事实源选择最新会话，并在排序字段缺失时按稳定降级策略处理。
- [ ] AC-005 生成类动作新建 turn：生成、完善、评审、加入迭代和生成 OpenSpec 等生成类治理动作进入对象会话时，必须创建新的 turn。
- [ ] AC-006 生成类动作新建 candidate：每次生成类治理动作必须创建新的 candidate；旧 candidate 只能作为历史上下文或显式引用来源，不得默认复用为本次候选。
- [ ] AC-007 candidate 追溯：本轮 candidate 必须能追溯到本轮 turn、触发动作、对象类型、对象 ID、创建时间和操作者。
- [ ] AC-008 重复点击控制：动作执行中前端必须锁定对应按钮；后端必须识别重复提交，避免多个不可区分的 turn 或 candidate。
- [ ] AC-009 明确再次发起新轮：用户明确再次发起同一动作时，系统可以创建新的 turn 和 candidate，但必须能与上一轮区分。
- [ ] AC-010 权限保护：用户无对象权限或会话权限时，不得进入会话，不得泄漏会话标题、消息摘要、candidate 内容或对象正文。
- [ ] AC-011 状态门禁保护：对象已归档、已删除或处于不可操作阶段时，卡片动作必须按门禁禁用、只读或提示异常，不得通过会话复用绕过治理流程。
- [ ] AC-012 历史 candidate 区分：Chat 内展示历史 candidate 时，必须与本轮 candidate 明确区分，不得把历史 candidate 标记为当前可提交结果。
- [ ] AC-013 失败不流转：会话查找、新建、turn 追加或 candidate 创建失败时，不得刷新卡片阶段，不得写入 REQ、BUG、Change、Sprint 或 OpenSpec 事实源。
- [ ] AC-014 异常提示：失败反馈必须区分权限不足、对象不存在、会话已归档、会话已删除、候选创建失败、重复提交、网络失败和服务端异常。
- [ ] AC-015 UI 识别：从卡片动作进入 Chat 时，Chat 顶部或上下文区必须展示当前对象标识、标题和最近动作摘要，让用户识别当前对象会话。
- [ ] AC-016 新会话空态：新建对象会话时，页面必须展示明确初始状态，不得显示其他对象的历史消息或 candidate。
- [ ] AC-017 文本溢出：长标题、长对象 ID、长 candidate 摘要必须截断或换行处理，不得撑破卡片、抽屉或聊天区。
- [ ] AC-018 观测脱敏：usage_events、request_logs、task_traces 或等价观测记录只允许保存脱敏摘要，不得保存完整 Prompt、完整回复、完整 candidate 正文、密钥、Cookie、Authorization header、本机绝对路径或真实客户敏感数据。
- [ ] AC-019 观测覆盖：卡片动作触发 Chat、复用会话、新建会话、新建 turn、新建 candidate、重复提交拦截和失败分支均应有可排障的结果状态、错误码和耗时摘要。
- [ ] AC-020 与父需求一致：本需求不得改变 `REQ-0027` 中的治理命令门禁，不得绕过评审、Sprint 纳入、OpenSpec、apply 或 archive 规则。

## 知识库承接

| 来源 | 适用结论 | 落地方式 |
|---|---|---|
| `docs/knowledge-base/README.md` | 适用 | 本验收文档记录知识库判定，并在 trace 中写入 `knowledge_base_refs` |
| `docs/knowledge-base/retrospectives/sprint-007-retrospective.md` | 适用 | 承接“需求中心卡片事实源优先”和“候选态/正式态隔离”经验 |

## 横切 AC（knowledge-base）

本需求不命中 `admin-list`、`admin-form`、`admin-modal`、`media-upload` 四个管理后台横切标签，因此不新增 AC-XCUT。后续若 OpenSpec Change 扩展到管理端列表、表单、弹窗或上传回显，必须重新读取对应 best-practices 并补充 AC-XCUT。

## 产品数据采集与链路观测 AC

- [ ] AC-OBS-001 行为事件字段只记录对象类型、对象 ID、动作类型、结果状态和数量类脱敏摘要。
- [ ] AC-OBS-002 请求日志记录服务端可信 `request_id`、路由、状态码、耗时、操作者和脱敏错误码，不保存完整请求体或响应体。
- [ ] AC-OBS-003 生成类治理动作进入 Task Trace 或等价任务链路，至少能区分会话查找、新建会话、追加 turn、创建 candidate 和返回结果。
- [ ] AC-OBS-004 Task Trace metadata 不保存完整 Prompt、完整回复、完整 candidate 正文、对象正文、密钥、本机路径或真实客户敏感数据。
- [ ] AC-OBS-005 行为事件、请求日志或 Task Trace 失败不得阻断主业务流程，但必须保留降级摘要或错误计数。

## Readiness

```yaml
readiness: Ready
knowledge_base_gate: N/A
cross_cutting_tags: []
prototype_gate: N/A
reason: requirement、user-stories、business-flow、acceptance、trace 已齐；本 REQ 无 prototype 目录，不命中管理后台横切标签。
next: /opsx-apply REQ-0039-requirement-center-card-chat-session-reuse
```

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-17 16:45:27
accepted_by: workflow-sync
source_change: add-requirement-center-card-chat-session-reuse
source_sprint: sprint-008
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```
