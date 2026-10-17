---
title: 需求中心卡片全命令产品链路真实化需求中心规格增量
created_at: 2026-09-30 18:06:35
updated_at: 2026-09-30 18:37:27
---

# 需求中心卡片全命令产品链路真实化需求中心规格增量

## MODIFIED Requirements

### Requirement: 阶段动作门禁

系统 MUST 根据治理对象类型和当前阶段提供正确主动作，并在阶段产物缺失、权限不足、版本冲突、同步失败或验收未完成时阻止错误流转。REQ 卡片的需求分析、生成需求、完善需求、发起评审、加入迭代、生成 OpenSpec、开始开发和完成归档八类动作 MUST 使用完整对象身份、授权项目和后端事实源裁判，写操作完成状态 MUST 以产物校验、Workflow Sync 成功和事实源重读为准。

#### Scenario: REQ 卡片八动作真实执行

- **GIVEN** 用户在需求中心查看一个有权访问的 REQ 卡片
- **WHEN** 用户点击需求分析、生成需求、完善需求、发起评审、加入迭代、生成 OpenSpec、开始开发或完成归档动作
- **THEN** 系统 MUST 向后端传递完整 REQ ID、授权项目、动作类型、对象版本和幂等标识
- **AND** 后端 MUST 读取最新文件事实、权限、阶段、材料和 Sprint/Change 关系后裁判
- **AND** 前端不得凭本地状态、按钮文案、短编号或客户端路径直接推进生命周期

#### Scenario: 只读分析不写治理事实

- **GIVEN** REQ 可读但尚未满足写动作材料门禁
- **WHEN** 用户点击需求分析并在 Chat 中要求生成、开发或归档
- **THEN** 系统 MUST 保持只读分析模式
- **AND** 不得修改 requirement、trace、registry、CHANGELOG、Sprint 或 OpenSpec 文件
- **AND** 不得触发 Workflow Sync 生命周期事件
- **AND** 必须提示用户使用对应受控动作完成写入

#### Scenario: 写操作完成必须重读事实源

- **WHEN** 七类写动作执行完成
- **THEN** 系统 MUST 先确认允许范围内的产物已写入并通过校验
- **AND** 必须确认对应 Workflow Sync 成功
- **AND** 必须重新读取 REQ、Sprint、Change 或归档事实源后刷新卡片和文档入口
- **AND** 请求已受理、Chat 消息发送、模型回复或任务全勾均不得单独作为完成证据

#### Scenario: 工作区与候选不得替代事实源

- **WHEN** Chat 工作台、执行工作区或治理 candidate 产生了文件差异、assistant 回复或模型完成信号
- **THEN** 系统 MUST 将这些内容视为候选或执行证据
- **AND** 必须在应用前校验 manifest、revision、binding revision 和最新事实源版本
- **AND** 应用后必须完成 Workflow Sync 并重读事实源
- **AND** 若工作区或 candidate 所基于的事实源已变化，系统 MUST 进入 conflict、stale 或待恢复状态
- **AND** 前端不得展示成功、刷新卡片阶段或更新文档入口为完成态

#### Scenario: 部分写入和同步失败可恢复

- **WHEN** 写操作在多文件写入、Workflow Sync、事实源重读或目录迁移期间失败
- **THEN** 系统 MUST 区分未执行、部分写入、同步失败、版本冲突、权限不足和已完成
- **AND** 必须保留可查询操作身份和安全错误摘要
- **AND** 重试时必须先核实已落盘步骤，再重放未完成步骤
- **AND** 不得声称全部回滚或伪造成功状态

#### Scenario: 开发启动与归档投影

- **WHEN** 用户从 REQ 卡片触发开始开发
- **THEN** 系统 MUST 在前置门禁通过并记录真实 `opsx.start` 后才展示研发中投影
- **AND** REQ canonical 状态在归档前仍保持 `in_sprint`
- **WHEN** 用户触发完成归档
- **THEN** 系统 MUST 校验任务、测试、人工验收、文档同步和 Change 归档门禁
- **AND** 所有关联 Change 归档闭环后才允许 REQ 进入 done

#### Scenario: Requirement 和 Bug 主动作按阶段映射

- **WHEN** 用户查看某个阶段的 Requirement 或 Bug 卡片
- **THEN** 系统必须根据对象类型与阶段映射 `req-*`、`bug-*`、`sprint-*` 或 `opsx-*` 主动作
- **AND** 卡片主动作必须展示产品化文案，例如“生成需求 →”“加入迭代 →”“开始开发 →”“完成 / 归档 →”
- **AND** 实现必须保留可追溯命令映射，避免仅以裸 `/req-*` 或 `/opsx-*` 命令作为用户可见按钮文案
- **AND** 采集池对象必须指向生成文档动作
- **AND** 待评审对象必须指向评审动作
- **AND** 已通过对象必须指向 Sprint 规划动作
- **AND** 迭代规划对象必须指向 OpenSpec Change 创建动作
- **AND** 每个动作必须声明产品真实能力状态，区分真实候选写入、真实应用写入、demo 模拟和仅展示

#### Scenario: 未接入真实链路的命令不得模拟成功

- **WHEN** 用户在非 demo 需求中心触发 `complete`、`review`、`sprint-propose`、`opsx` 系列中尚未接入真实治理写入链路的动作
- **THEN** 系统必须阻止真实流转
- **AND** 系统必须展示该动作尚未接入产品写入链路的提示
- **AND** 提示必须给出对应 Codex 命令和完整对象 ID
- **AND** 系统不得创建虚假的成功状态、不得仅通过前端临时 state 移动卡片、不得写入伪造 trace 或 registry

#### Scenario: Bug Generate 使用真实治理候选链路

- **GIVEN** Bug 处于采集池阶段且 `capture.md` 与 `trace.md` 均存在并非空
- **WHEN** 用户在需求中心真实模式触发 Bug Generate
- **THEN** 系统必须以 `BUG-*` 完整 ID 和 `bug-generate` action 调用治理准备链路
- **AND** Chat 输入框必须只展示简洁 `/bug-generate <BUG-full-id>` 命令，不得裸露内部治理约束、写入范围或 dry-run 规则
- **AND** Chat 历史消息展示与复制内容也必须只暴露用户可理解的短命令，不得展示隐藏执行上下文
- **AND** Chat turn 与 `chat_messages` 必须只保存用户可见短命令，执行所需内部治理约束必须由后端基于治理候选恢复，不得作为前端隐藏 prompt 或用户消息正文落库
- **AND** 用户手动编辑可见草稿后，系统不得继续追加旧治理约束
- **AND** Chat 主对话区不得展示大型治理成果面板、`查看成果`、`待应用成果` 或 `审阅治理成果` 弹窗
- **AND** Chat assistant 消息、外层消息历史轨道、正文 bubble、markdown 容器，以及 TurnActivity 的执行中 status/alert 文案必须在运行态占满对话区可用宽度展示执行摘要，用户命令消息仍必须保持右侧气泡宽度限制
- **AND** 该 assistant 满宽规则不得按命令名或 action 白名单生效；`req-generate`、`req-complete`、`bug-generate`、`bug-complete`、review、sprint、opsx 和普通 Chat 的 role=assistant running 输出必须使用同一布局规则
- **AND** 满宽回归证据必须包含运行态 DOM/computed style 命令矩阵，不得只校验 CSS 源码或只覆盖 generate 命令
- **AND** TurnActivity 的工具调用/完成状态摘要必须作为轻量 meta 左对齐到 assistant 内容列，不得漂浮到正文上方中间或被拉成满宽输出块
- **AND** 治理候选、实际 Diff、应用状态和失败原因必须通过后台应用链路、轨迹或轻量提示承载
- **AND** 合法候选通过写入边界、manifest、revision、dry-run 和冲突校验后，后端必须自动创建 application 并交由 controller 应用
- **AND** 历史打开会话时，pending 且已有后端 application 的候选必须轮询 operation，prepared 空候选不得申请 application
- **AND** 前端历史入口不得向 `/governance-candidates/{candidate_id}/applications` 发起自动 application POST
- **AND** 历史打开会话时不得恢复或渲染治理成果大面板、`待应用成果`、`查看成果` 或 `审阅治理成果`
- **AND** 自动应用失败、版本冲突、越界、恢复阻塞或校验 warning 时，系统不得展示治理成果大面板，只能展示轻量错误或轨迹提示
- **AND** 应用成功后必须重新读取需求中心 context
- **AND** 部署到产品运行态后，运行中的 Web bundle 不得包含 `待应用成果`、`查看成果`、`审阅治理成果` 或 `确认应用` 面板文案
- **AND** Web 启动时必须标记当前构建版本，并在检测到当前脚本资产不是最新 HTML 声明资产时自动刷新一次
- **AND** Chat 历史入口必须清理旧版治理成果面板 DOM，避免旧 bundle、缓存或历史节点恢复已移除的面板
- **AND** Chat 新会话默认执行配置的推理程度必须为 Low，后端 capabilities 默认与前端 fallback 必须保持一致
- **AND** 发送前必须完成执行器 sandbox/dry-run preflight，并区分 `executor_unavailable` 与 `governance_validation_failed`
- **AND** Chat 工作台必须将 chat、governance 和 events 的 `NetworkError` / `Failed to fetch` 归一化为中文局部提示，不得向用户展示浏览器原生英文错误
- **AND** 导航、历史恢复或组件卸载产生的 `AbortError` 不得渲染为错误；已有成功消息不得被 turns/events/governance 轮询失败覆盖成全局错误
- **AND** 所有写入型产品命令以当前治理文件 manifest/revision 校验；默认副本模式自动同步隔离工作区，显式本地真实仓库模式直接使用 `source_root` 当前工作树
- **AND** 治理投影不要求 .git；source_root 与投影内容实际不一致时返回 workspace_fact_source_stale / manifest_mismatch
- **AND** 显式本地真实仓库模式不得展示候选二次应用入口，命令成果直接写入真实仓库后必须刷新需求中心看板事实源投影
- **AND** Toast 提示同步事实源，无需提交 Git；不得把未提交直接解释为执行器不可见
- **AND** 写入命令仍校验完整对象 ID、registry path、trace status 和必需文档，状态或文档缺失返回 governance_validation_failed
- **AND** 看板阶段投影必须来自 `trace.md`、registry、CHANGELOG、Sprint 和 Change 事实源，而不是仅来自前端临时 state

#### Scenario: Req Generate 保持不回退

- **WHEN** 用户继续对采集池 Requirement 执行 Req Generate
- **THEN** 既有 `req-generate` 准备、候选、自动应用和刷新闭环必须保持可用
- **AND** 新增 Bug Generate 能力不得放宽 Requirement 的文件写入 allowlist 或状态门禁

### Requirement: 当前卡片增量视觉验收

系统 SHALL 将原型作为设计输入，最终验收结合 Change design、acceptance、真实截图、computed style、Mock/API 边界和 REQ 最终一致性。

#### Scenario: 八动作浮层与反馈验收

- **WHEN** 实现 REQ 卡片八动作入口和反馈容器
- **THEN** 系统 SHALL 在 Change design 中维护动作按钮到 modal 类型、selector、状态和验收证据的矩阵
- **AND** 实现前 SHALL 完成 UI Skeleton 和 1440px 首轮确认
- **AND** 实现完成前 SHALL 验证 1440px、390px、矮视口、深浅主题、权限差异、错误态、长 ID、外部点击关闭和内部 `stopPropagation` 场景
- **AND** 验收 SHALL 记录关键 computed style、Mock/API 边界和 linked REQ 文档最终一致性

#### Scenario: 实施与归档门禁
- **WHEN** 开始UI细节实现或归档
- **THEN** 系统 SHALL 先完成Skeleton和1440px首轮确认；归档前具有1440px深浅主题、关键交互、390px长ID、原ID同字号采样及REQ子文档一致性证据
- **AND** 未改区域与当前实现一致，原型演示及任务勾选不能替代真实观察
