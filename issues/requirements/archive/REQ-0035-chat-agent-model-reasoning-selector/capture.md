---
requirement_id: REQ-0035-chat-agent-model-reasoning-selector
title: 聊天框新增 Agent、模型和推理程序选择
status: done
created_at: '2026-09-14 09:05:04'
updated_at: 2026-09-29 14:22:21
recorded_by: product
owner: 产品团队
source: 用户反馈
lifecycle_stage: plan
parent_requirement: REQ-0025-chat-workbench
captured_via: capture
classification_rationale: 用户要求聊天框新增 Agent 选择、模型选择和推理程序选择，属于 Chat 工作台输入区能力增强。
priority: P1
---

# 一句话

聊天框新增 Agent 选择，并提供模型和推理程序选择能力；当前 Agent 列表有且只有 Codex。

# 原始描述

用户反馈：“聊天框新增Agent选择（当前有且只有一个 Codex），新增模型和推理程序的选择（类似Codex聊天框）”。

# 初步范围

- 聊天框增加 Agent 选择控件，当前可选项只有 Codex。
- 增加模型选择能力。
- 增加推理程序或推理强度选择能力，交互参考 Codex 聊天框。
- 选择结果应进入后续对话执行配置，不能仅是前端静态控件。

# 待澄清

- [ ] 模型与推理程序的可选项来源、默认值和可用性约束。
- [ ] 当前仅 Codex 时是否显示为禁用选择、只读标签，还是仍可展开。
- [ ] 已存在会话切换模型或推理程序时是否影响后续消息、整个会话，或需要创建新会话。

# 建议验收要点

1. 聊天框可见 Agent 选择入口，当前仅 Codex 时状态清晰。
2. 用户可选择模型和推理程序，选项、默认值、禁用态与实际可执行能力一致。
3. 发起对话时，Agent、模型和推理程序选择被正确传入执行链路并可追溯。
4. 选择控件在窄屏、长模型名和禁用态下不遮挡输入框与发送动作。

# 探索结论

尚未执行 `/req-explore`；本记录仅完成轻量采集。
