---
requirement_id: REQ-0035-chat-agent-model-reasoning-selector
title: Chat 输入区执行配置选择原型拆解
status: pending_review
created_at: 2026-09-14 23:18:06
updated_at: 2026-09-14 23:18:06
---

# Chat 输入区执行配置选择原型拆解

## 1. 原型目的

本原型是 Chat 工作台输入区的执行配置选择契约种子，用于后续 `/req-opsx` 写入 UI Contract 与 UI Skeleton。它不代表最终视觉稿或实现代码，不接入真实 API，不改变 REQ-0025 已有 Chat 工作台页面结构。

## 2. 页面清单

| 页面 | 路由候选 | 说明 |
|---|---|---|
| Chat 工作台 | `/chat` 或既有 Chat 路由 | 在既有对话输入区上方或输入框内缘新增执行配置栏 |

## 3. 关键区域

| 区域 | 内容 | 约束 |
|---|---|---|
| 执行配置栏 | Agent、模型、推理配置三个控件 | 靠近输入框，视觉权重低于输入和发送 |
| 输入主体 | 多行输入框、发送/停止按钮 | 不被配置控件遮挡；运行中状态清晰 |
| 配置菜单 | 模型菜单、推理菜单、禁用原因 | 支持外部点击、Esc、键盘焦点和长文本 |
| 轮次配置摘要 | 本轮实际生效配置 | 可在执行详情或轮次元信息中展示 |

## 4. 组件层级

```text
ChatWorkbench
  -> ConversationPane
  -> PromptComposer
       -> ExecutionConfigBar
            -> AgentSelector
            -> ModelSelector
            -> ReasoningSelector
       -> PromptInput
       -> ComposerActions
            -> SendButton
            -> StopButton
  -> ExecutionDetailPanel
       -> TurnMetadata
            -> EffectiveExecutionConfig
```

## 5. 状态矩阵

| 状态 | Agent | 模型 | 推理配置 | 输入/发送 |
|---|---|---|---|---|
| loading | 占位或默认 Codex | 骨架/禁用 | 骨架/禁用 | 保持布局稳定 |
| ready | Codex | 可选默认值 | 可选默认值 | 可输入发送 |
| single-agent | 只读或禁用 | 可选 | 可选 | 正常 |
| unavailable-option | Codex | 禁用项带原因 | 禁用项带原因 | 不能发送非法值 |
| running | 当前值只读 | 禁用或标注下一轮 | 禁用或标注下一轮 | 禁止重复发送 |
| stopping | 当前值只读 | 禁用 | 禁用 | 显示停止中 |
| unknown | 当前值只读 | 禁用 | 禁用 | 阻止新发送 |
| archived | 只读 | 只读 | 只读 | 不允许发送 |
| narrow | 紧凑换行或更多菜单 | 不溢出 | 不溢出 | 发送按钮可见 |
| error | Codex 或默认值 | 错误提示/重试 | 错误提示/重试 | 按策略禁用或默认继续 |

## 6. 交互触发

| 触发 | 预期 |
|---|---|
| 打开模型菜单 | 显示模型名、可用状态、禁用原因；点击外部或 Esc 关闭 |
| 选择模型 | 更新下一轮配置；菜单关闭；不影响已发出的运行 |
| 打开推理菜单 | 显示推理选项和说明；不可用项禁用 |
| 选择推理配置 | 更新下一轮配置；菜单关闭 |
| 发送消息 | 当前配置随请求提交；后端返回实际生效配置 |
| 查看历史轮次 | 展示该轮实际配置，不使用当前选择覆盖 |
| 运行中点击控件 | 默认不可修改，或明确只影响下一轮 |

## 7. 数据依赖

| 数据 | 来源 | 说明 |
|---|---|---|
| agent_options | 服务端能力配置 | 首版只有 Codex |
| model_options | 服务端能力配置 | 含 display_name、value、available、disabled_reason |
| reasoning_options | 服务端能力配置 | 含 display_name、value、available、disabled_reason |
| default_config | 服务端配置 | 新建会话和配置加载 fallback |
| requested_config | 发送请求 | 用户发送时选择的配置 |
| effective_config | 轮次事实源 | 后端实际生效配置与降级原因 |

## 8. 响应式断点

| 视口 | 约束 |
|---|---|
| 1440px | 三个控件同排展示，输入框宽度仍为主视觉；菜单不遮挡发送按钮 |
| 1024px | 控件可压缩宽度或换行，长模型名截断 |
| 390px | 控件可进入更多菜单或两行紧凑布局；发送、停止、输入仍可操作 |

## 9. 1440px 验收焦点

- 配置栏与输入框垂直间距、边框、背景和字号符合 Ops 视觉体系。
- Agent 单项状态不会显得像可用多 Agent 列表。
- 模型和推理控件长文本截断后仍可通过菜单或 tooltip 识别。
- 菜单层级、边框、z-index、hover、focus、disabled 和错误态清晰。
- 运行中禁用态不会让用户误以为已改变当前执行。

## 10. Mock/API 边界

- `prototype.html` 使用静态示例数据，只验证结构、状态和交互意图。
- 最终实现必须由真实配置 API 或服务端能力配置驱动。
- 原型不代表模型列表、推理选项、错误码或降级策略最终值。

## 11. UI Reference Replication Contract 种子

| 项 | 结论 |
|---|---|
| 保真模式 | 局部一致：参考 Codex 聊天框的紧凑配置选择体验，迁移到 MoonBox Ops 视觉体系 |
| 事实源优先级 | 业务语义与 REQ-0025 > 本 REQ acceptance > MoonBox UI token > Codex 聊天框交互参考 > prototype.html 静态示例 |
| 组件清单 | ExecutionConfigBar、AgentSelector、ModelSelector、ReasoningSelector、PromptInput、SendButton、EffectiveExecutionConfig |
| 动作按钮矩阵 | Agent/模型/推理控件触发 popover；发送按钮触发执行；停止按钮沿用父 REQ |
| 验收证据 | 后续需要 1440px 截图、窄屏截图、菜单 open 状态、disabled/loading/error 状态、computed style 和外部点击证据 |
| 非目标 | 不复刻 Codex 原生品牌视觉；不新增其他 Agent；不牺牲 Chat 现有会话、权限、停止和执行详情能力 |
