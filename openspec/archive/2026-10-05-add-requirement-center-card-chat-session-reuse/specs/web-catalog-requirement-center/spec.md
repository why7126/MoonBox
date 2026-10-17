---
title: 需求中心卡片动作对象会话复用规格增量
change_id: add-requirement-center-card-chat-session-reuse
capability: web-catalog-requirement-center
source_requirement: REQ-0039-requirement-center-card-chat-session-reuse
---

# 需求中心卡片动作对象会话复用规格增量

## MODIFIED Requirements

### Requirement: 全局 AI 聊天与卡片动作反馈

系统 MUST 在需求中心提供全局 AI 聊天悬浮入口，并用右侧聊天抽屉承载用户消息、卡片动作上下文、命令执行反馈和异常分支。系统 MUST 在卡片动作触发 Chat 时基于对象类型和对象 ID 进入对象会话：同一 REQ、BUG 或 Change 优先复用最近的未归档、未删除且当前用户有权访问的会话；不存在可用会话时才新建对象会话。生成类治理动作 MUST 在同一对象会话内创建新的 turn 和新的 candidate，不得默认复用历史 candidate。

#### Scenario: 用户打开全局 AI 聊天抽屉

- **WHEN** 用户点击需求中心全局 AI 聊天悬浮按钮
- **THEN** 系统必须从右侧打开 AI 聊天抽屉
- **AND** 用户必须可以输入消息
- **AND** Enter 必须发送消息
- **AND** Shift+Enter 必须换行

#### Scenario: 卡片动作带入 AI 上下文

- **WHEN** 用户从卡片触发分析、生成、完善、评审、迭代、开发或归档动作
- **THEN** AI 聊天抽屉必须获得当前对象 ID、标题、类型、阶段和建议命令
- **AND** 系统必须展示执行中、成功或失败反馈
- **AND** 失败反馈不得自动移动卡片阶段

#### Scenario: 同一对象复用最近可用会话

- **WHEN** 用户从同一个 REQ、BUG 或 Change 卡片触发 Chat 动作
- **THEN** 系统必须按对象类型和对象 ID 查询可复用会话
- **AND** 系统只允许复用未归档、未删除、当前用户有权访问且允许继续交互的会话
- **AND** 存在多个可用会话时必须按服务端稳定事实源选择最新会话，不得依赖前端本地列表顺序
- **AND** 不存在可用会话时必须创建新的对象会话并写入对象关联

#### Scenario: 生成类动作新建本轮候选

- **WHEN** 用户从卡片触发生成、完善、评审、加入迭代、生成 OpenSpec 或等价生成类治理动作
- **THEN** 系统必须在目标对象会话内创建新的 turn
- **AND** 系统必须为本轮动作创建新的 candidate
- **AND** 历史 candidate 只能作为历史上下文或显式引用来源，不得被默认标记为本轮候选或本轮可提交结果
- **AND** 本轮 candidate 必须能追溯到本轮 turn、触发动作、对象类型、对象 ID、操作者和创建时间

#### Scenario: 失败与重复提交不流转卡片阶段

- **WHEN** 会话查找、新建会话、追加 turn、创建 candidate、权限校验或重复提交识别失败
- **THEN** 系统必须展示可区分的失败反馈
- **AND** 系统不得刷新卡片阶段
- **AND** 系统不得写入 REQ、BUG、Change、Sprint 或 OpenSpec 事实源
- **AND** 行为事件、请求日志或 Task Trace 只允许记录脱敏摘要

#### Scenario: 右侧抽屉互斥

- **WHEN** Markdown 文档抽屉、tasks 抽屉或 AI 聊天抽屉之一打开
- **THEN** 其他右侧抽屉必须关闭或收起
- **AND** 抽屉必须支持关闭按钮、Escape 和外部点击关闭
- **AND** 内部点击不得误关闭抽屉
- **AND** 外部点击应通过蒙层完成，且不得影响抽屉内编辑、保存或拖拽宽度交互
