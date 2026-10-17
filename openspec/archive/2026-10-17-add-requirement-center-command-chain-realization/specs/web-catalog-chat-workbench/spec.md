---
title: 需求中心卡片全命令产品链路真实化 Chat 工作台规格增量
created_at: 2026-09-30 18:06:35
updated_at: 2026-10-04 10:43:55
---

# 需求中心卡片全命令产品链路真实化 Chat 工作台规格增量

## MODIFIED Requirements

### Requirement: 多材料观测与脱敏

系统 SHALL 为图片或文件添加/移除、Skill 选择/移除、发送结果、材料校验、对象存储写入、Skill 解析、上下文构造、执行提交和结果处理记录脱敏观测摘要。需求中心卡片触发的只读分析、治理写动作、操作查询、Workflow Sync、恢复和归档投影也 SHALL 记录脱敏观测摘要。行为事件、请求日志、Task Trace 和流程节点写入失败 SHALL 不阻断主流程，但系统 SHALL 保留脱敏降级摘要以便排障；Workflow Sync 失败 SHALL 阻断命令完成声明。

#### Scenario: 需求中心动作观测脱敏

- **WHEN** 用户从需求中心卡片触发只读分析或七类写动作
- **THEN** usage_events、request_logs、task_traces 和 task_trace_spans metadata 只允许保存对象类型、对象 ID、动作类型、状态、错误码、耗时、计数和脱敏摘要
- **AND** 不得保存完整 Prompt、文件正文、请求体、响应体、模型回复、Authorization、Cookie、Token、密钥、本机绝对路径或未脱敏治理材料
- **AND** 直接 API 调用不得伪造界面行为事件

#### Scenario: 写任务流程节点覆盖

- **WHEN** 七类写操作被提交
- **THEN** Task Trace 或等价流程节点 SHALL 覆盖门禁校验、产物写入、标题校验、Workflow Sync、事实源重读、恢复判断和结果返回
- **AND** 分析动作若保持只读且无多步骤写任务，可以只保留 Chat/请求观测并说明不接入写任务 Trace 的原因

#### Scenario: 观测 metadata 脱敏

- **WHEN** 系统记录图片、文件、Skill 或对象治理动作相关行为事件、请求日志、Task Trace 或流程节点
- **THEN** metadata 只包含事件名、对象类型、对象 ID、动作类型、会话 ID、turn ID、candidate ID、结果、数量、大小、类型、错误码、耗时和脱敏摘要
- **AND** 不包含完整图片、文件正文、完整请求体、完整 Prompt、完整回复、完整 candidate 正文、Authorization、Cookie、Token、密钥、本机绝对路径、对象存储内部完整 key 或真实客户敏感数据

#### Scenario: Task Trace 节点覆盖

- **WHEN** 一轮包含图片、文件、Skill 引用或生成类治理动作的 Chat 执行被提交
- **THEN** Task Trace 或等价流程节点覆盖材料校验、对象会话查找、新建会话、追加 turn、创建 candidate、上下文构造、执行提交和结果处理

### Requirement: 原型驱动 UI 合同与验收证据

系统 SHALL 在实现需求中心卡片动作反馈、Chat 抽屉、Action Modal、确认弹窗或执行状态容器前完成 UI Contract、UI Skeleton 和动作按钮矩阵。实现完成前 SHALL 提供 1440px 桌面视口、窄屏、深浅主题、关键交互截图或等价证据，并记录关键 computed style、Mock/API 边界和 linked REQ 最终一致性。

#### Scenario: 需求中心动作 UI Skeleton 先行

- **WHEN** Change 开始实现需求中心卡片八动作入口、Chat 抽屉或执行反馈容器
- **THEN** 先完成页面壳、卡片动作区、浮层容器、状态容器、产物入口、错误提示和可测 selector
- **AND** 未完成 Skeleton 证据前不得关闭细节实现任务

#### Scenario: 动作按钮矩阵验收

- **WHEN** UI 任务准备验收
- **THEN** 系统 SHALL 提供动作按钮、modal 类型、目标 selector、组件族、状态和证据入口的矩阵
- **AND** 同一动作族的按钮、loading、disabled、error、取消、外部点击和提交后反馈 SHALL 使用一致组件语义

#### Scenario: UI Skeleton 先行

- **WHEN** Change 开始实现 Chat 输入区、消息区、对话/轨迹切换、历史弹窗或轨迹入口 UI
- **THEN** 先完成页面壳、布局区域、组件层级、状态容器、可测选择器和 1440px 验收焦点
- **AND** 未完成 Skeleton 证据前不得关闭细节实现任务

#### Scenario: 参考稿复刻验收

- **WHEN** UI 任务准备验收
- **THEN** 提供 selector 映射、动作按钮矩阵、computed style 采样和分批截图或等价 DOM/组件证据
- **AND** 归档前确认 linked REQ 与最终 Change 设计、截图、Mock/API 边界和实现证据一致

## ADDED Requirements

### Requirement: 治理候选与事实源完成边界

Chat 工作台 SHALL 将执行工作区、assistant 输出和治理 candidate 作为候选或执行证据；卡片阶段、文档入口和完成态 SHALL 以治理事实源、Workflow Sync 结果和事实源重读投影为准。

#### Scenario: candidate 应用前版本校验

- **WHEN** 用户或后端自动应用治理 candidate
- **THEN** 系统 SHALL 校验 candidate manifest、revision、binding revision 和当前事实源版本
- **AND** 校验失败时 SHALL 返回 conflict、stale 或等价待恢复状态
- **AND** 不得把候选差异、assistant 回复或工作区文件直接展示为完成事实

#### Scenario: 应用后刷新事实源投影

- **WHEN** candidate 文件写入完成
- **THEN** 系统 SHALL 执行对应 Workflow Sync
- **AND** 同步成功后 SHALL 重读治理事实源并刷新需求中心卡片投影
- **AND** 同步失败或重读失败时 SHALL 保留操作身份和安全错误摘要
- **AND** 前端不得刷新卡片阶段为成功态

#### Scenario: 本地部署默认真实仓库工作区

- **WHEN** 本地常驻部署生成仓库绑定
- **THEN** 系统 SHALL 默认声明 `workspace_mode: source`
- **AND** 执行器 SHALL 直接使用 `source_root` 当前工作树作为工作区
- **AND** 系统 SHALL 不创建 `<workspace_root>/<conversation_id>` 会话副本、不执行副本同步、不要求候选二次应用
- **AND** 共享生产仓库、多人同时编辑或强隔离审阅场景 MAY 显式配置 `workspace_mode: copy`
- **AND** copy 模式 SHALL 保留既有隔离副本、候选应用和未应用成果保护语义
