---
title: Chat 工作台多材料与 Skill 快速引用实施任务
created_at: 2026-09-14 23:41:49
updated_at: 2026-09-20 19:10:29
owner: product
---

# Chat 工作台多材料与 Skill 快速引用实施任务

## 1. UI Contract 与 Skeleton

- [x] 1.1 在实现前确认 UI Contract、UI Skeleton 和 UI Reference Replication Contract，锁定事实源优先级、selector 映射、动作按钮矩阵和 Mock/API 边界。
- [x] 1.2 为 Chat 工作台页面壳、对话区、输入区、图片预览条、Skill token、Skill 菜单、发送/停止动作和轨迹入口建立稳定 `data-testid` 或等价选择器。
- [x] 1.3 完成 1440px Skeleton 首轮视觉证据，证明布局、密度、层级、输入区占位和轨迹入口方向正确。

## 2. 图片/文件输入与对象存储链路

- [x] 2.1 设计并实现图片/文件能力限制来源，覆盖数量、格式、单项体积、总大小和文本长度，确保前后端一致校验。
- [x] 2.2 实现图片/文件选择、预览或摘要、移除、上传中、成功、失败、重试和仅材料输入策略，不清空其他草稿材料。
- [x] 2.3 实现后端图片/文件上传、对象权限重验、脱敏摘要保存和历史轮次回显。
- [x] 2.4 补充对象存储访问、保留、清理和错误降级路径，避免日志暴露临时凭据或内部完整 key。

## 3. Skill 引用链路

- [x] 3.1 实现当前仓库 Skill 候选读取，覆盖仓库未绑定、权限不足、元数据缺失、读取失败和空态。
- [x] 3.2 实现 Skill token 选择、移除、长名称截断或 tooltip、失效检测和发送前重验。
- [x] 3.3 实现 Skill 上下文快照，保存名称、来源摘要、版本或内容摘要、实际注入范围，不自动执行写入型命令。
- [x] 3.4 实现 Skill 内容过长的服务端摘要或截断策略，并向用户展示实际注入范围。

## 4. Chat 发送、幂等与历史

- [x] 4.1 扩展 Chat 发送 API，使文本、图片/文件引用、Skill 引用和请求标识绑定为同一轮上下文快照。
- [x] 4.2 复用既有会话与轮次幂等策略，覆盖重复点击、网络重试、响应丢失和权限撤销。
- [x] 4.3 保持对话与轨迹双视图、消息复制、本轮轨迹入口、停止、重试、Diff 和会话历史能力不回退。
- [x] 4.4 历史读取展示图片/文件与 Skill 脱敏摘要，不泄露完整图片、文件正文、完整 Skill 内容、完整 Prompt 或完整回复。

## 5. 观测、安全与文档同步

- [x] 5.1 接入 usage_events，记录添加图片、移除图片、添加文件、移除文件、选择 Skill、移除 Skill 和发送结果的脱敏属性。
- [x] 5.2 接入 request_logs，记录接口状态、错误码、耗时、材料数量和脱敏摘要，不保存完整请求体或完整回复。
- [x] 5.3 接入 task_traces / task_trace_spans，覆盖材料校验、对象存储写入、Skill 解析、上下文构造、执行提交和结果处理节点。
- [x] 5.4 同步 OpenAPI、客户端生成、错误码、API 文档、数据库设计、迁移说明、对象存储策略和产品数据采集与链路观测说明。

## 6. 测试与验收证据

- [x] 6.1 补充后端接口和集成测试，覆盖图片限制、上传失败、权限撤销、Skill 候选、Skill 失效、幂等发送和历史回显。
- [x] 6.2 补充 SQLite/MySQL 兼容测试和对象存储路径测试；Docker 本地验收从环境或启动脚本解析实际 Web 端口。
- [x] 6.3 补充前端测试，覆盖图片预览状态机、Skill 菜单、token 移除、运行中禁用、归档/未知状态、窄屏布局和外部点击 capture 阶段。
- [x] 6.4 提供 1440px 桌面、窄屏、深浅主题、关键交互截图或等价证据，并记录 computed style 采样。
- [x] 6.5 回填 Change `trace.md`、REQ `acceptance.md` 或等价验收记录，确认 UI Reference Contract、Mock/API 边界和 REQ 最终一致性。

## 7. 验收返修

- [x] 7.1 按验收反馈补齐会话创建前分支选择，默认 `main` 或 `master`，候选来自当前 Git 仓库。
- [x] 7.2 将 Agent、模型、推理配置移动到发送按钮左侧，并将发送按钮收敛为图标按钮。
- [x] 7.3 统一 `/` 命令入口与 Skill 按钮入口，候选来自 `.agents/skills`，选中后以 Skill token 展示且不自动执行。
- [x] 7.4 将图片入口升级为文件上传入口，支持图片和文件、多选、对象存储上传、输入框上方回显和剪贴板粘贴上传。
- [x] 7.5 更新返修台账、Change/REQ/Sprint/长期文档和验证证据；完整台账见 `acceptance-fixes.md`。
- [x] 7.6 将 Skill 图标按钮移动到文件上传按钮右侧，并补齐 `.agents` 到 `/app/governance/.agents` 的只读部署挂载，确保 Skill 候选不因治理根目录投影缺失而为空。
- [x] 7.7 按验收反馈调整 Skill 列表与 token 展示：候选项无边框、展示英文名与中文描述，输入 `/bug` 可模糊搜索，选中后 token 仅显示图标与英文名。
- [x] 7.8 按验收反馈将 Skill token 从附件材料条移出，改为与用户输入同一输入行展示；完整台账见 `acceptance-fixes.md`。
- [x] 7.9 按验收反馈将输入区升级为 rich composer，使 Skill token 成为用户消息内容流内的 inline chip，文本从 chip 后继续输入并自然换行；完整台账见 `acceptance-fixes.md`。
- [x] 7.10 按验收反馈补齐 Skill inline chip 键盘删除，支持 `Delete` / `Backspace` 同步移除 Skill、草稿状态和 `chat.skill_remove` 事件；完整台账见 `acceptance-fixes.md`。
- [x] 7.11 按附件 `moonbox-chat-redesign-v2.html` 复刻 Chat 页面【对话】/【轨迹】/【历史】布局：对话/轨迹 segmented tabs 与 subbar 状态区、历史分组 modal、轨迹 trace-wrap/toolbar/status/search/scrub/event row；完整台账见 `acceptance-fixes.md`。
- [x] 7.12 按验收反馈收敛 Composer 与消息流：输入区改为深色 Dock，隐藏项目/仓库选择并自动注入当前空间绑定仓库，历史 action 轻量化，用户消息中 Skill chip 与正文同属消息泡、附件位于消息泡上方；完整台账见 `acceptance-fixes.md`。
- [x] 7.13 按验收反馈修正 AI 运行状态块与输入框左对齐：`TurnActivity` 外层轨道与 Composer 共享 1120px 内容宽度，内部执行状态正文保持可读宽度；完整台账见 `acceptance-fixes.md`。
- [x] 7.14 按附件继续收敛 Composer 与消息呈现：去掉输入区与工具栏之间的多余分隔线，输入字号调整为 14px/1.6，用户消息采用 turn-user 结构，AI 消息采用 avatar + assistant-col + tool-summary + bubble-assistant 结构；完整台账见 `acceptance-fixes.md`。
- [x] 7.15 按验收标注移除 Composer 工具栏上边界横线，使输入区与底部工具栏保持同一 Dock 面；完整台账见 `acceptance-fixes.md`。
- [x] 7.16 按验收反馈修正用户消息中 Skill 重复展示：用户气泡仅显示 Skill pill 与用户原始正文，过滤历史旧数据中的 `Skill 引用：xxx` 派生行；完整台账见 `acceptance-fixes.md`。
- [x] 7.17 按参考稿继续收敛用户消息 meta：模型信息与时间同一行且模型信息前置，复制改为图标按钮，用户消息不再展示查看本轮轨迹；完整台账见 `acceptance-fixes.md`。
- [x] 7.18 按验收反馈收敛 AI 消息：缩小 tool-summary 与正文间距，AI 正文不重复 Skill pill，AI meta 左对齐并使用复制/Skill 图标，移除底部查看轨迹，统计仅展示现有事件已采集字段；完整台账见 `acceptance-fixes.md`。
- [x] 7.19 按验收反馈修复用户消息和 AI 消息复制功能：共用可靠复制动作，优先 `navigator.clipboard.writeText`，失败或不可用时回退 textarea + `execCommand`，并展示可访问成功/失败状态；完整台账见 `acceptance-fixes.md`。
- [x] 7.20 按验收反馈修正消息材料与 AI 阅读层级：用户正文过滤图片/文件引用派生行，图片缩略图支持预览弹窗，AI 不重复展示用户附件，tool-summary 移入 assistant 列并高亮关键结论；完整台账见 `acceptance-fixes.md`。
- [x] 7.21 按验收反馈将聊天输入框、用户消息正文和 AI 消息正文字号统一从 14px 调整为 13px；完整台账见 `acceptance-fixes.md`。
- [x] 7.22 按验收反馈修正 AI 正文重点高亮：移除固定文案表，改为基于句子语义特征识别关键结论、风险/阻塞、动作结果和下一步等重点内容；完整台账见 `acceptance-fixes.md`。
- [x] 7.23 按验收反馈收敛 AI 正文重点高亮密度：每条消息最多高亮 1-2 个高优先级短片段，避免整句大面积高亮；完整台账见 `acceptance-fixes.md`。
- [x] 7.24 按验收反馈修正用户消息图片真实预览、Skill 图标统一、用户消息 Skill chip 去尾部 `skill` 文案、`/` Skill 菜单键盘选择和复制图标成功/失败反馈；完整台账见 `acceptance-fixes.md`。
- [x] 7.25 按验收反馈修正用户消息图片鉴权显示、`/` 删除后 Skill 面板关闭和 Skill 候选字号密度：图片缩略图与预览使用 Bearer fetch + object URL，slash 触发菜单随查询删除关闭，按钮触发菜单保留，候选字号收敛到 13px 体系；完整台账见 `acceptance-fixes.md`。
- [x] 7.26 按验收反馈修正用户消息 Skill chip 与正文布局：首段正文与 Skill chip 位于同一 inline 内容流，文本从 chip 后继续排版并自然换行，第二段及复杂 Markdown 继续块级渲染；完整台账见 `acceptance-fixes.md`。
- [x] 7.27 按验收反馈统一 Chat 执行配置展示名：消息 meta、AI tool-summary 和 Composer 兜底展示统一显示 Codex、GPT-6 Astra、GPT-5.6 Luna、GPT-5.6 Terra、GPT-5.6 Sol、GPT-5.5、XHigh、High、Medium、Low，底层 payload/API/DB 保持原始 value；完整台账见 `acceptance-fixes.md`。
- [x] 7.28 按验收反馈收敛 AI 消息 meta 与管理关联弹窗：AI tool-summary 仅在已采集思考耗时字段存在时展示 `已完成（思考 x）`，AI meta 复制图标置于第一位，管理关联弹窗预取并稳定展示候选对象，搜索、主对象和引用对象整合为一个候选列表，REQ/BUG 使用文字 badge 与颜色区分；完整台账见 `acceptance-fixes.md`。
- [x] 7.29 按验收反馈调整 Composer 模型列表顺序为 GPT-6 Astra、GPT-5.6 Sol、GPT-5.6 Terra、GPT-5.6 Luna、GPT-5.5，前端按 capabilities 顺序渲染，底层 value 不变；完整台账见 `acceptance-fixes.md`。
- [x] 7.30 按验收反馈统一 Composer 下拉面板：Skill、模型、推理共用 popover 基础样式、候选项密度、hover/active/disabled 状态和外部点击/Escape/互斥切换关闭逻辑；完整台账见 `acceptance-fixes.md`。
- [x] 7.31 按验收反馈修正 Composer 内空白点击关闭：Skill、模型、推理面板打开后，点击输入框空白、Composer 工具栏空白或页面空白均自动隐藏，仅当前面板内部和对应触发按钮保留点击保护；完整台账见 `acceptance-fixes.md`。
- [x] 7.32 按附件 `moonbox-chat-redesign-v3.html` 一对一复刻 Chat 轨迹 Tab：轨迹页收敛为 trace-wrap、trace-toolbar、trace-status、trace-card、trace-controls、scrub、event-list、disclosure/raw-events-box、section-block 的结构，并保留事件详情、引用快照、文件变更、停止、重试和 payload 语义；完整台账见 `acceptance-fixes.md`。
- [x] 7.33 按验收反馈修正轨迹 Tab 内容宽度与文案：轨迹内容区与 Composer 使用同一 1120px 内容轨道，并移除轨迹面板底部说明文案；完整台账见 `acceptance-fixes.md`。
- [x] 7.34 按验收标注修正轨迹 Tab 实际内容边缘：移除 `trace-wrap` 左右 padding，使 `trace-toolbar`、`trace-status`、`trace-card` 和 `section-block` 边缘与 Composer 输入框外边缘对齐；完整台账见 `acceptance-fixes.md`。
- [x] 7.35 按验收反馈修正 Chat Codex 写权限门禁：执行权限拆分为治理文档写入、产品实现写入和完全只读，早期 REQ/BUG 可在治理目录写入对应文档，产品实现写入仍要求主对象 in_sprint、活动 Change 与 Sprint 双向纳入；完整台账见 `acceptance-fixes.md`。
- [x] 7.36 按验收反馈修正写权限状态不可切换体验：管理关联保存主对象后立即刷新会话 `write_scope` / `write_reason_code`，状态胶囊展示可读只读原因，已有运行保持原权限且下一轮使用最新范围；完整台账见 `acceptance-fixes.md`。
- [x] 7.37 按验收反馈修正轨迹文件变更展示语义：区分本轮执行快照与当前本地工作区状态，对 untracked 文件显示“新增（未跟踪）”，快照内容与当前磁盘内容不一致时展示提示；完整台账见 `acceptance-fixes.md`。
