---
title: Chat 工作台多材料与 Skill 快速引用变更提案
created_at: 2026-09-14 23:41:49
updated_at: 2026-09-20 14:45:39
owner: product
---

# Chat 工作台多材料与 Skill 快速引用变更提案

## 背景与动机

Chat 工作台已具备真实 Codex 会话、执行轨迹、Diff 和权限边界，但当前输入能力仍以文本为主，难以承载多张界面截图、文件材料、仓库 Skill 约束和用户提供的 Codex 阅读体验基线。REQ-0028 已完成评审并纳入 `sprint-006`，需要把分支选择、多图片/文件输入、Skill 快速引用、材料/Skill 执行上下文追溯和原型驱动 UI 验收转为 OpenSpec Change。

## 变更内容

- 在 Chat 工作台会话创建前增加分支选择，候选来自 Git 仓库，默认优先 `main` 或 `master`。
- 在 Chat 工作台输入区增加图片/文件选择、粘贴、多选、预览或摘要、移除、重试、上传状态和发送前校验。
- 将图片/文件引用与 Skill 引用纳入本轮执行上下文快照，历史轮次可追溯脱敏摘要、顺序、状态和引用版本。
- 增加当前仓库 Skill 候选读取、选择、token 展示、移除和上下文注入；首版不自动执行 Skill 命令。
- 对话消息区按用户提供的 Codex 截图做局部一致 / 风格迁移，保留 MoonBox Ops 视觉系统、共享导航、权限、轨迹和 Diff。
- 补齐 API、DB、对象存储、行为事件、请求日志、Task Trace 和流程节点的脱敏观测要求。
- 将 prototype、UI Reference Replication Contract、1440px/窄屏/深浅主题截图、computed style 和 Mock/API 边界作为实现与验收门禁。

## 能力范围

### 新增能力

- 无。

### 修改能力

- `web-catalog-chat-workbench`: 扩展 Chat 工作台分支选择、输入区、消息展示、执行上下文、对象存储/Skill 引用、权限、观测和原型驱动 UI 验收要求。

## 影响范围

- Web 前台：Chat 工作台输入区、消息区、附件预览、Skill 菜单、状态提示、历史回显、轨迹入口和响应式布局。
- API：Chat 分支能力、材料上传、Chat 发送、Skill 候选读取、历史消息读取、能力限制查询和错误码。
- 数据库：会话分支、上传材料记录、会话轮次中的图片/文件引用快照、Skill 引用快照、上下文构造状态、幂等请求标识和脱敏摘要字段。
- 对象存储：图片/文件对象写入、读取、权限校验、清理与保留策略。
- 观测：usage_events、request_logs、task_traces、task_trace_spans 覆盖材料校验、对象存储写入、Skill 解析、上下文构造和执行提交。
- 测试与文档：OpenAPI/客户端生成、接口测试、SQLite/MySQL 兼容测试、对象存储策略、UI 视觉证据、产品数据采集与链路观测文档同步。
