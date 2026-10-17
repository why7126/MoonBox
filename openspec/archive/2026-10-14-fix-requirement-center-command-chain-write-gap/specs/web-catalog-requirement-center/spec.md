---
title: 需求中心治理命令链真实写入修复
created_at: '2026-09-29 16:07:39'
updated_at: 2026-09-30 15:59:01
---

# 需求中心治理命令链真实写入修复

## ADDED Requirements

### Requirement: 完善中事实可见

系统 SHALL 在规划中卡片按内部 draft 与 enriching 状态提供相应文档和动作，但不显示独立“草稿”或“完善中”标签；展示已存在的完善子文档、未完成提示及继续完善动作，不得以文档齐全替代根因确认门禁。

#### Scenario: 缺陷草稿已保存但根因未确认

- **WHEN** BUG 状态为 enriching 且根因未 confirmed
- **THEN** 卡片不显示独立“完善中”标签，但保留实际存在的根因/临时方案/验收文档及补证提示；长负责人名称省略显示并保留全文提示
- **AND** 继续完善仍调用 bug-complete，不自动进入待评审，不扩大文档编辑权限

#### Scenario: 草稿与完善完成状态

- **WHEN** 状态为 draft 或 pending_review
- **THEN** 分别保持规划中完善入口或待评审入口，不显示草稿状态标签或错误的完善中补证提示

### Requirement: 完善成果安全续接

系统 SHALL 保留可追溯的 req-complete 隔离成果，校验通过后由后端自动应用，不要求用户删除文件解除阻断。

#### Scenario: 原轮次留下部分文档

- **WHEN** 同对象原始基准未变化且未应用文件均在允许范围，执行器临时锁预检通过
- **THEN** 在原工作区继续完善并校验，成功后自动回写事实源、同步状态与工作区基准
- **AND** 版本冲突、越界或文档门禁未通过时保留成果且不强制流转

### Requirement: 运行消息独立内容列

系统 SHALL 将尚未落库的 assistant 运行输出放置于独立 assistant 内容区，不继承用户气泡宽度限制。

#### Scenario: 运行输出转为已保存消息

- **WHEN** 仅存在用户消息时产生运行输出，随后 assistant 消息落库或用户从历史重开会话
- **THEN** 运行输出与已保存正文均铺满 assistant 内容列，临时块在落库后移除，用户气泡保持原宽度限制

### Requirement: 已评审对象的加入迭代命令保持类型参数

系统 SHALL 在已评审需求与缺陷卡片生成带对象类型参数和完整 ID 的 Sprint 命令，并将同一命令带入 Chat Prompt。

#### Scenario: 从卡片进入 Chat

- **WHEN** 用户点击已评审 REQ 或 BUG 卡片的“加入迭代”
- **THEN** REQ Prompt 为 `/sprint-propose --req <完整REQ-ID>`，BUG Prompt 为 `/sprint-propose --bug <完整BUG-ID>`

## MODIFIED Requirements

### Requirement: 阶段动作门禁

系统 MUST 根据治理对象类型和当前阶段提供正确主动作，并在阶段产物缺失、真实写入能力未接入或验收未完成时阻止错误流转。

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
