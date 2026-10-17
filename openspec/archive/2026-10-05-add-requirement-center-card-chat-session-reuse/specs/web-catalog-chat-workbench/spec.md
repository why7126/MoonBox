---
title: Chat 工作台对象会话与治理候选追溯规格增量
change_id: add-requirement-center-card-chat-session-reuse
capability: web-catalog-chat-workbench
source_requirement: REQ-0039-requirement-center-card-chat-session-reuse
---

# Chat 工作台对象会话与治理候选追溯规格增量

## MODIFIED Requirements

### Requirement: 会话历史与关联

系统 MUST 支持搜索、置顶、重命名、归档恢复和受限删除；主对象零或一个，引用多个，修改只影响之后轮次。系统 MUST 支持需求中心卡片动作按治理对象复用 Chat 会话：同一 REQ、BUG 或 Change 再次触发 Chat 时，优先返回最近的未归档、未删除且当前用户有权访问的对象会话；多个可用会话按最近 turn 更新时间、最近消息更新时间、会话 `updated_at` 和稳定创建事实降级排序。

#### Scenario: 归档与恢复

- **WHEN** 用户归档已终止会话后重新恢复
- **THEN** 归档期间只读，恢复后重验权限再允许输入

#### Scenario: 变更关联

- **WHEN** 用户调整主对象或辅助引用
- **THEN** 历史快照不被重写，超过一个主对象被拒绝

#### Scenario: 从治理对象进入最近会话

- **WHEN** 用户从需求中心卡片携带对象类型、对象 ID、标题、阶段和动作类型进入 Chat
- **THEN** 系统必须校验对象权限和会话权限
- **AND** 系统必须过滤已归档、已删除、无权访问或不可继续交互的会话
- **AND** 系统必须返回最新可用对象会话或创建新的对象会话
- **AND** 返回结果不得泄漏无权会话标题、消息摘要、candidate 内容或对象正文

#### Scenario: 排序字段缺失时稳定降级

- **WHEN** 同一对象存在多个可用会话且部分排序字段缺失
- **THEN** 系统必须按明确降级顺序选择会话
- **AND** 系统必须保留可排障的脱敏选择摘要
- **AND** 前端不得用本地列表顺序覆盖服务端选择结果

### Requirement: Chat Composer 多材料状态与幂等

系统 SHALL 将文字、图片/文件引用、Skill 引用和发送请求标识绑定为同一轮上下文快照。重复点击、网络重发或响应丢失时，系统 SHALL 复用同一会话与轮次，不重复创建会话或重复提交同一批材料与 Skill 引用。会话归档、运行中、停止中、状态未知、服务未就绪、仓库缺失或权限撤销时，分支、文件上传和 Skill 控件 SHALL 遵循既有 Chat 工作台输入门禁。生成类治理动作 SHALL 在目标对象会话中为每次明确发起的新动作创建新的 turn 和新的 candidate；同一幂等请求重复提交时不得创建多个不可区分的 turn 或 candidate。

#### Scenario: 重复发送同一轮

- **WHEN** 用户重复点击发送或网络重试同一轮上下文
- **THEN** 系统复用同一会话与轮次
- **AND** 不重复创建会话或重复提交同一批材料、Skill 引用或治理 candidate

#### Scenario: 发送前权限撤销

- **WHEN** 用户发送前会话、空间、仓库、文件对象、图片对象或 Skill 权限被撤销
- **THEN** 系统拒绝提交并保留安全错误摘要
- **AND** 不泄漏无权访问的文件、图片、Skill 或会话内容

#### Scenario: 生成类治理动作创建新候选

- **WHEN** 用户明确再次发起生成、完善、评审、加入迭代、生成 OpenSpec 或等价治理动作
- **THEN** 系统必须创建新的 turn
- **AND** 系统必须创建新的 candidate
- **AND** 新 candidate 必须关联对象类型、对象 ID、动作类型、本轮 turn、操作者和创建时间
- **AND** 历史 candidate 不得被默认复用为本轮 candidate

#### Scenario: 重复提交同一生成类动作

- **WHEN** 同一用户对同一对象连续提交同一幂等标识的生成类动作
- **THEN** 系统必须返回同一轮结果或明确重复提交提示
- **AND** 系统不得悄悄创建多个等价 candidate
- **AND** 用户使用新的幂等标识明确发起新一轮动作时，系统必须创建可区分的新 turn 和新 candidate

### Requirement: 多材料观测与脱敏

系统 SHALL 为图片或文件添加/移除、Skill 选择/移除、发送结果、材料校验、对象存储写入、Skill 解析、上下文构造、执行提交和结果处理记录脱敏观测摘要。行为事件、请求日志、Task Trace 和流程节点写入失败 SHALL 不阻断主流程，但系统 SHALL 保留脱敏降级摘要以便排障。对象会话复用、新建对象会话、新建 turn、新建 candidate、重复提交拦截和失败分支 SHALL 记录脱敏观测摘要。

#### Scenario: 观测 metadata 脱敏

- **WHEN** 系统记录图片、文件、Skill 或对象治理动作相关行为事件、请求日志、Task Trace 或流程节点
- **THEN** metadata 只包含事件名、对象类型、对象 ID、动作类型、会话 ID、turn ID、candidate ID、结果、数量、大小、类型、错误码、耗时和脱敏摘要
- **AND** 不包含完整图片、文件正文、完整请求体、完整 Prompt、完整回复、完整 candidate 正文、Authorization、Cookie、Token、密钥、本机绝对路径、对象存储内部完整 key 或真实客户敏感数据

#### Scenario: Task Trace 节点覆盖

- **WHEN** 一轮包含图片、文件、Skill 引用或生成类治理动作的 Chat 执行被提交
- **THEN** Task Trace 或等价流程节点覆盖材料校验、对象会话查找、新建会话、追加 turn、创建 candidate、上下文构造、执行提交和结果处理
