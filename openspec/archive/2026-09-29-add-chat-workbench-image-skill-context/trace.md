---
change_id: add-chat-workbench-image-skill-context
source_requirement: REQ-0028-chat-skill-codex
source_sprint: sprint-006
title: Chat 工作台多材料与 Skill 快速引用执行轨迹
type: add
status: implemented
created_at: 2026-09-14 23:41:49
updated_at: 2026-09-22 22:44:45
owner: product
prototype_sources:
  - issues/requirements/review/REQ-0028-chat-skill-codex/prototype/web/prototype.html
  - issues/requirements/review/REQ-0028-chat-skill-codex/prototype/web/context.md
  - user-provided-image-1
ui_contract:
  status: drafted
  design: openspec/archive/2026-09-29-add-chat-workbench-image-skill-context/design.md
ui_skeleton:
  status: implemented
visual_acceptance_1440: passed
computed_style: passed
mock_api_boundary: documented
req_final_consistency: checked
product_data_collection_observability:
  status: applicable
  affected_layers:
    - web_request_wrapper
    - api
    - db
    - object_storage
    - usage_events
    - request_logs
    - task_traces
    - task_trace_spans
  validation: 后端聚焦测试、前端组件测试、Compose 挂载测试、OpenAPI/Orval生成、TypeScript编译与Playwright合成API视觉证据已完成；验收返修补充分支选择、文件上传、粘贴上传、Skill 左侧入口、Skill token rich composer inline 布局、`.agents` 只读挂载、对话/轨迹 segmented tabs、历史弹窗分组、轨迹 trace-wrap、深色 Composer Dock、自动仓库注入、消息流布局、AI 运行状态块左对齐、Composer 多余分隔线移除与字号收敛、turn-user/turn-assistant 呈现、用户消息 Skill/图片/文件派生说明去重、用户消息 meta 单行收敛、AI 消息 meta 与已采集统计收敛、用户/AI 消息复制可靠性修复、AI 不重复附件、tool-summary 移入 assistant 列、重点内容高亮语义化与密度收敛、输入框/用户消息/AI 消息正文统一 13px、历史图片材料受控内容读取预览、Skill 图标统一、Skill 菜单键盘选择、复制图标成功/失败反馈、图片缩略图/预览改为前端 Authorization fetch + object URL 且释放 URL、slash 触发 Skill 菜单删除关闭、Skill 候选字号密度收敛、用户消息 Skill chip 与首段正文同一 inline 内容流且后续 Markdown 块级渲染、Chat 执行配置展示名统一为 Codex/GPT/XHigh 等规范名称且 payload/API/DB 仍保留 raw value、AI meta 复制图标首位、tool-summary 仅在明确采集思考耗时字段时显示 `已完成（思考 x）`、管理关联弹窗候选预取稳定展示、搜索/主对象/引用对象整合为可搜索列表且 REQ/BUG 使用文字 badge 与颜色区分、轨迹 Tab 按 v3 参考稿收敛为 trace-wrap/toolbar/status/card/controls/scrub/event-list/raw-events/section-block 结构、轨迹内容区与 Composer 共享 1120px 内容轨道并移除解释性 footer 文案、轨迹实际内容边缘清除外层左右 padding、管理关联保存主对象后刷新会话写权限且运行中 Codex turn 不热切换权限、轨迹文件变更展示区分执行快照与当前工作区状态并标识 untracked/mismatch 后，观测数据仍仅保存材料数量与脱敏摘要，受控内容读取接口不返回对象 key、签名 URL 或本机路径。
execution:
  schema_version: 1
  started_at: 2026-09-14 23:51:33
  completed_at: 2026-09-15 00:08:00
  last_event: opsx.modify
---

# Chat 工作台多材料与 Skill 快速引用执行轨迹

## 需求就绪

| 项 | 结论 | 证据 |
|---|---|---|
| REQ 状态 | ready | `REQ-0028-chat-skill-codex` 为 `in_sprint`，迭代 `sprint-006`。 |
| 文档包 | ready | 六件套与 prototype 已存在。 |
| Prototype Gate | pass | `prototype_refs`、`prototype_gate`、`AC-PROTOTYPE-*` 已记录。 |
| 观测声明 | pass | 覆盖 Web/API/DB/对象存储/行为事件/请求日志/Task Trace/流程节点。 |

## 冲突处理

| 冲突点 | 处置 |
|---|---|
| 截图具体命令和文件链接 | 仅作为视觉结构样例，不作为业务指令。 |
| 三栏 prototype 与实际 Chat 页面 | 保留现有 Chat 工作台结构，按 UI Contract 调整输入区、消息区和轨迹入口。 |
| Skill 内容展示 | 输入区只展示 token 和摘要，完整内容不直接展开。 |

## UI 证据清单

| 证据 | 状态 | 说明 |
|---|---|---|
| UI Contract | drafted | 见 `design.md`。 |
| UI Skeleton | passed | `src/web/scripts/check-chat-materials.cjs` 覆盖材料输入区、图片 token、Skill token 与发送动作。 |
| 1440px 截图 | passed | `evidence/ui/materials-dark-1440.png`。 |
| 窄屏截图 | passed | `evidence/ui/materials-light-390.png`。 |
| 深浅主题截图 | partial-pass | 当前 Chat 壳未暴露 `chat-theme-toggle` 时跳过切换；脚本记录实际主题，仍覆盖 1440 与 390 两个视口。 |
| 关键交互截图 | passed | 图片引用、Skill 菜单与 token 选择通过 Playwright 合成 API 采集。 |
| computed style | passed | `evidence/ui/materials-computed.json` 采样 composer、材料条、图片 token、Skill token 和发送按钮。 |
| Mock/API 边界 | documented | 视觉脚本使用 synthetic API mocks；后端接口、数据库、OpenAPI 与前端组件使用真实代码验证。 |

## 实现摘要

| 层 | 实现 |
|---|---|
| API | `capabilities.materials` 和仓库 `branches` 作为材料与分支事实源；`POST /chat/materials` 上传图片/文件；`GET /chat/materials/{material_id}/content` 在当前登录态下授权读取材料真实内容用于图片预览；`POST /conversations/{cid}/turns` 支持 `attachments[]` 与 `skills[]`；新增 `/skills` 与 `/conversations/{cid}/skills`。 |
| DB | 新增 `chat_conversations.branch_name`、`chat_uploaded_materials` 和 `chat_turn_materials`，按会话分支、上传材料、轮次材料顺序保存图片/文件引用和 Skill 快照。 |
| Web | Composer 支持分支选择、图片/文件上传、粘贴上传、材料失败 token、材料移除、`/` Skill 菜单、Skill token、图标发送和材料请求签名；历史消息回显 `materials[]` 摘要。 |
| 观测 | `usage_events` 保存图片/文件添加移除、Skill 选择移除和发送结果的材料数量；Task Trace metadata 保存材料数量；request_logs 只保存错误码和材料数量等脱敏摘要。 |
| 对象存储 | 上传图片或文件时由后端写入对象存储，轮次只绑定 opaque `ref_id` 与脱敏摘要，不向前端、日志或 Trace 暴露内部对象 key。 |

## 验收返修摘要

| 项 | 结论 | 证据 |
|---|---|---|
| 反馈批次 | completed | 输入框优化反馈已完成，台账见 `acceptance-fixes.md`。 |
| 分支选择 | completed | 会话创建前选择分支；默认 `main`，无 `main` 时使用 `master`；候选从当前 Git 仓库读取。 |
| 文件上传 | completed | 支持图片与文件、多选、对象存储上传、输入框上方材料条展示、Ctrl+C/Ctrl+V 粘贴上传。 |
| Skill 命令 | completed | `/` 与 Skill 按钮共用 `.agents/skills` 候选；`/keyword` 支持模糊搜索；选中后以无边框轻量 token 展示，不自动执行命令。 |
| Skill 候选读取 | completed | Docker 后端通过 `/app/governance/.agents` 只读挂载读取仓库 `.agents/skills`。 |
| Skill 列表展示 | completed | 候选行无单项边框，展示英文名与 `SKILL.md` frontmatter 中文描述，不再把 `---` 当摘要。 |
| Skill token 输入行布局 | completed | Skill token 从图片/文件附件材料条移出，位于 `chat-input-row` 并与用户输入同一行展示。 |
| Skill token rich composer 布局 | completed | 输入区升级为 rich composer；Skill token 作为内容流 inline chip，用户文本从 chip 后继续输入并自然换行。 |
| Skill token 键盘删除 | completed | Skill inline chip 支持 `Delete` / `Backspace` 删除，并同步 `skills[]`、草稿状态和 `chat.skill_remove` 事件。 |
| 对话/轨迹/历史布局复刻 | completed | 按 `moonbox-chat-redesign-v2.html` 参考稿完成 segmented tabs + subbar 状态区、历史分组 modal、轨迹 trace-wrap/toolbar/status/search/scrub/event row。 |
| Composer 与消息流视觉复核 | completed | 输入区改为深色 Dock，隐藏项目/仓库选择并自动注入当前空间绑定仓库，历史 action 轻量化，用户消息泡内融合 Skill chip 与正文、附件位于消息泡上方。 |
| AI 运行状态块左对齐 | completed | `TurnActivity` 外层轨道与 Composer 共享 1120px 内容宽度，内部执行状态正文保持可读宽度，避免运行状态块相对输入框左边缘右缩。 |
| 输入框与消息呈现继续复刻 | completed | Composer 去掉输入区内部与工具栏上方的多余分隔线，输入文字调整为 14px/1.6；用户消息采用 turn-user 结构，AI 消息采用 avatar + assistant-col + tool-summary + bubble-assistant 结构。 |
| 用户消息 Skill 重复展示 | completed | 用户消息气泡仅展示 Skill pill 与用户原始正文，过滤历史旧数据中的 `Skill 引用：xxx` 派生行，保留 Skill payload 和 trace。 |
| 用户消息 meta 行收敛 | completed | 用户消息模型信息与时间同一行且模型信息前置，复制为图标按钮，用户消息不展示查看本轮轨迹；AI 消息轨迹入口保留。 |
| AI 消息 meta 与统计收敛 | completed | AI 正文不重复 Skill pill；AI meta 左对齐，复制和 Skill 为图标，底部不重复展示查看轨迹；统计只展示现有事件/API 已采集字段。 |
| 消息复制可靠性 | completed | 用户消息和 AI 消息共用复制动作，优先浏览器剪贴板 API，回退 textarea + `execCommand`，并展示已复制或复制失败状态。 |
| 消息材料与 assistant 阅读层级 | completed | 用户正文过滤图片/文件/Skill 派生材料行；用户图片缩略图可点击预览；AI 不重复附件；tool-summary 位于 assistant 列第一行；重点内容受控高亮。 |
| 消息正文字号 | completed | 聊天输入框、用户消息正文和 AI 消息正文统一为 13px；meta、tool-summary 和按钮等辅助文本不随本次调整改变。 |
| AI 重点高亮语义化 | completed | 移除固定文案表，按句子语义特征识别关键结论、风险/阻塞、动作结果和下一步等重点内容，示例文案仅作为测试样例之一。 |
| AI 重点高亮密度 | completed | 每条 AI 消息最多高亮 1-2 个高优先级短片段，优先阻塞原因和动作结果，避免整句大面积高亮。 |
| 用户消息与 Skill 交互细节 | completed | 图片预览通过受控材料内容读取接口展示真实图片；Skill 图标统一为 `Sparkles`；用户消息 Skill chip 仅显示图标与英文名；`/` Skill 菜单支持键盘选择；复制成功/失败切换结果图标。 |
| 图片鉴权显示与 Skill 菜单触发态 | completed | 用户消息图片缩略图和预览弹窗通过前端 Authorization fetch 受控材料内容并转 object URL 展示真实图片；slash 触发的 Skill 菜单在删除 `/` 或查询后自动关闭；Skill 候选字体与密度收敛到 Chat 13px 体系。 |
| 用户消息 Skill 与正文 inline flow | completed | 用户消息首段正文与 Skill chip 位于同一 inline 内容流，文本从 chip 后继续排版并自然换行；第二段及复杂 Markdown 继续块级渲染。 |
| Chat 执行配置展示名与模型顺序 | completed | 消息 meta、AI tool-summary 和 Composer 兜底展示统一显示 `Codex`、`GPT-6 Astra`、`GPT-5.6 Sol`、`GPT-5.6 Terra`、`GPT-5.6 Luna`、`GPT-5.5`、`XHigh`、`High`、`Medium`、`Low`；Composer 模型下拉按 `GPT-6 Astra`、`GPT-5.6 Sol`、`GPT-5.6 Terra`、`GPT-5.6 Luna`、`GPT-5.5` 顺序展示；底层 payload/API/DB 保留 raw value。 |
| Composer 下拉面板统一 | completed | Skill、模型、推理三类面板共用 `chat-composer-popover` 与 `chat-composer-option` 基础样式，统一字号密度、hover/active/disabled 状态和外部点击/Escape/互斥切换关闭逻辑；Skill 保留搜索与键盘选择，模型/推理保留单选语义。 |
| Composer 空白区域关闭面板 | completed | Skill、模型、推理面板打开后，点击输入框空白、Composer 工具栏空白或页面空白均自动隐藏；仅当前面板内部和对应触发按钮保留点击保护。 |
| AI meta 与管理关联弹窗 | completed | AI tool-summary 在已采集思考耗时字段存在时显示 `已完成（思考 x）`，AI meta 复制图标置于第一位；管理关联弹窗预取并稳定展示候选，搜索、主对象和引用对象整合为可搜索列表，REQ/BUG 用文字 badge 与颜色区分。 |
| 轨迹 Tab v3 复刻 | completed | 按 `moonbox-chat-redesign-v3.html` 将轨迹页收敛为 `trace-wrap`、`trace-toolbar`、`trace-status`、`trace-card`、`trace-controls`、`scrub`、`event-list`、`disclosure/raw-events-box`、`section-block` 结构，保留搜索、事件详情、原始事件、引用快照、文件变更、停止、重试和真实数据语义。 |
| 轨迹 Tab 宽度与说明文案 | completed | 轨迹 Tab 内容区与底部 Composer 共享 1120px 内容轨道；移除“仅展示实际执行产生的事件与文件变更”解释性 footer 文案。 |
| 轨迹 Tab 实际内容边缘 | completed | 清除 `trace-wrap` 左右 padding，使 `trace-toolbar`、`trace-status`、`trace-card` 和 `section-block` 的实际边缘与 Composer 输入框外边缘对齐；窄屏继续保留页面安全宽度。 |
| Chat Codex 写权限门禁 | completed | 写权限拆分为 `read_only`、`governance_write`、`implementation_write`；早期 REQ/BUG 只开启治理目录写入，产品实现写入仍要求主对象 `in_sprint`、active Change 与 Sprint 双向纳入；会话响应返回 `write_scope` 与 `write_reason_code` 供前端展示。 |
| Chat 写权限状态刷新 | completed | 管理关联保存主对象后立即重新拉取会话并刷新 `write_scope` / `write_reason_code`；完全只读状态胶囊通过 hover/aria 引导先设置主对象；已有运行保持原权限，下一轮使用最新范围。 |
| 布局 | completed | 文件上传按钮右侧放置 Skill 按钮；Agent、模型、推理位于发送左侧；发送按钮为图标按钮。 |
| REQ 一致性 | checked | `acceptance.md` 已同步；`requirement.md`、`business-flow.md`、`user-stories.md` 和 prototype 无需更新，原因见返修台账。 |

## 变更记录

| 时间 | 事件 | 状态 | 说明 |
|---|---|---|---|
| 2026-09-15 00:08:00 | /opsx-apply | implemented | 完成 Chat 多图片引用登记、Skill 快速引用、材料快照、历史回显、观测脱敏、OpenAPI/Orval、测试与视觉证据。 |
| 2026-09-17 09:20:00 | /opsx-modify | pending_recheck | 按验收反馈补齐分支选择、通用文件上传、对象存储上传、剪贴板上传、`/` 命令入口和发送区布局，等待人工复验。 |
| 2026-09-17 09:35:00 | /opsx-modify | pending_recheck | 按验收反馈移动 Skill 按钮到上传按钮右侧，并补齐 `.agents` 只读挂载以恢复 Skill 候选读取。 |
| 2026-09-17 10:19:10 | /opsx-modify | pending_recheck | 按验收反馈调整 Skill 候选列表、`/bug` 模糊搜索和选中后轻量 token 展示，等待人工复验。 |
| 2026-09-18 17:27:45 | /opsx-modify | pending_recheck | 按验收反馈将 Skill token 从附件材料条移出，改为与用户输入同一输入行展示，等待人工复验。 |
| 2026-09-18 17:52:49 | /opsx-modify | pending_recheck | 按验收反馈将输入区升级为 rich composer，使 Skill token 作为用户消息内容流内的 inline chip 展示，等待人工复验。 |
| 2026-09-18 18:05:15 | /opsx-modify | pending_recheck | 按验收反馈补齐 Skill inline chip 的 `Delete` / `Backspace` 键盘删除，等待人工复验。 |
| 2026-09-18 18:23:36 | /opsx-modify | pending_recheck | 按附件 HTML 参考稿复刻 Chat 页面【对话】/【轨迹】/【历史】布局，等待人工复验。 |
| 2026-09-18 18:52:20 | /opsx-modify | pending_recheck | 按验收反馈收敛 Composer 深色 Dock、自动仓库注入、历史 action 和消息流布局，等待人工复验。 |
| 2026-09-18 23:14:21 | /opsx-modify | pending_recheck | 按验收反馈修正 AI 运行状态块与输入框左对齐，等待人工复验。 |
| 2026-09-20 08:14:30 | /opsx-modify | pending_recheck | 按附件继续修正 Composer 分隔线、输入字号、用户消息和 AI 消息呈现，等待人工复验。 |
| 2026-09-20 08:25:45 | /opsx-modify | pending_recheck | 按验收标注移除 Composer 工具栏上边界横线，等待人工复验。 |
| 2026-09-20 08:29:54 | /opsx-modify | pending_recheck | 按验收反馈修正用户消息中 Skill 重复展示，等待人工复验。 |
| 2026-09-20 08:37:25 | /opsx-modify | pending_recheck | 按参考稿收敛用户消息 meta 行、复制图标和用户轨迹入口，等待人工复验。 |
| 2026-09-20 08:58:02 | /opsx-modify | pending_recheck | 按验收反馈收敛 AI 消息 meta、Skill 图标、tool-summary 间距和已采集统计展示，等待人工复验。 |
| 2026-09-20 09:19:16 | /opsx-modify | pending_recheck | 按验收反馈修复用户消息和 AI 消息复制功能，覆盖 clipboard、fallback、成功和失败状态，等待人工复验。 |
| 2026-09-20 10:40:16 | /opsx-modify | pending_recheck | 按验收反馈修正用户材料派生行、图片预览、AI 不重复附件、assistant 内 tool-summary 和重点结论高亮，等待人工复验。 |
| 2026-09-20 10:52:09 | /opsx-modify | pending_recheck | 按验收反馈将聊天输入框、用户消息正文和 AI 消息正文字号统一调整为 13px，等待人工复验。 |
| 2026-09-20 11:05:00 | /opsx-modify | pending_recheck | 按验收反馈将 AI 正文重点高亮从固定文案表改为语义特征识别，等待人工复验。 |
| 2026-09-20 11:18:00 | /opsx-modify | pending_recheck | 按验收反馈收敛 AI 正文重点高亮密度，限制为少量高优先级短片段，等待人工复验。 |
| 2026-09-20 11:41:34 | /opsx-modify | pending_recheck | 按验收反馈修正用户消息真实图片预览、Skill 图标统一、Skill 菜单键盘选择和复制图标结果反馈，等待人工复验。 |
| 2026-09-20 12:05:59 | /opsx-modify | pending_recheck | 按验收反馈修正用户消息图片缩略图和预览弹窗的鉴权显示、slash Skill 菜单关闭规则和候选列表字号密度，等待人工复验。 |
| 2026-09-20 13:58:00 | /opsx-modify | pending_recheck | 按验收反馈修正用户消息 Skill chip 与首段正文的 inline 内容流布局，等待人工复验。 |
| 2026-09-20 14:08:00 | /opsx-modify | pending_recheck | 按验收反馈统一 Chat 执行配置展示名，等待人工复验。 |
| 2026-09-20 14:45:39 | /opsx-modify | pending_recheck | 按验收反馈收敛 AI 消息 meta 与管理关联弹窗，等待人工复验。 |
| 2026-09-20 15:20:00 | /opsx-modify | pending_recheck | 按验收反馈调整 Chat 模型列表顺序，等待人工复验。 |
| 2026-09-20 15:35:00 | /opsx-modify | pending_recheck | 按验收反馈统一 Composer Skill、模型、推理下拉面板样式和关闭逻辑，等待人工复验。 |
| 2026-09-20 15:42:00 | /opsx-modify | pending_recheck | 按验收反馈修正 Composer 输入区和工具栏空白点击关闭下拉面板，等待人工复验。 |
| 2026-09-20 17:30:39 | /opsx-modify | pending_recheck | 按附件 `moonbox-chat-redesign-v3.html` 一对一复刻 Chat 轨迹 Tab，等待人工复验。 |
| 2026-09-20 17:43:14 | /opsx-modify | pending_recheck | 按验收反馈修正轨迹 Tab 内容区与 Composer 同宽，并移除轨迹面板说明文案，等待人工复验。 |
| 2026-09-20 18:00:48 | /opsx-modify | pending_recheck | 按验收标注修正轨迹 Tab 实际内容边缘内缩，等待人工复验。 |
| 2026-09-20 18:55:28 | /opsx-modify | pending_recheck | 按验收反馈将 Chat Codex 写权限拆分为治理写、实现写和完全只读，等待人工复验。 |
| 2026-09-20 19:10:29 | /opsx-modify | pending_recheck | 按验收反馈修正 Chat 写权限状态刷新、只读原因提示和运行中权限不热切换，等待人工复验。 |
| 2026-09-22 22:44:45 | /opsx-modify | pending_recheck | 按验收反馈修正轨迹文件变更展示语义，区分执行快照与当前工作区状态，等待人工复验。 |
| 2026-09-14 23:41:49 | /req-opsx | proposed | 由 REQ-0028 生成 OpenSpec Change，固化 execution schema v1。 |

## 验证记录

| 命令 | 结果 | 说明 |
|---|---|---|
| `uv run --project src/backend pytest src/backend/tests/test_chat.py -q` | pass | 36 passed, 1 skipped；覆盖材料快照、历史摘要、图片/文件限制、对象存储上传、分支候选、Skill 候选、行为事件、Trace 脱敏与既有 Chat 回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-composer.test.tsx` | pass | 10 passed；覆盖图片/文件上传入口、仅材料发送、幂等重试、仓库/分支选择、`/bug` Skill 模糊搜索、中文描述展示、轻量 token、rich composer inline chip 布局和 Skill 键盘删除。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-workbench.test.tsx src/chat-sessions.test.tsx src/chat-trajectory.test.tsx src/chat-execution.test.tsx` | pass | 21 passed；覆盖对话/轨迹 segmented tabs 与 subbar 状态区、历史弹窗分组和行内动作、轨迹 trace-wrap/scrub/event-row、停止与历史动作回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-composer.test.tsx src/chat-messages.test.tsx src/chat-sessions.test.tsx src/chat-workbench.test.tsx src/chat-trajectory.test.tsx src/chat-execution.test.tsx` | pass | 32 passed；覆盖 Composer 自动仓库注入、消息流 Skill chip/附件布局、历史 action、subbar、轨迹与执行回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-activity.test.tsx src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-workbench.test.tsx` | pass | 21 passed；覆盖运行状态块、消息布局、Composer 和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-activity.test.tsx src/chat-composer.test.tsx src/chat-workbench.test.tsx` | pass | 22 passed；覆盖用户消息 turn-user、assistant avatar/column、tool-summary、Composer 与 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-composer.test.tsx src/chat-messages.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 22 passed；覆盖移除 Composer 工具栏分隔线后的 Composer、消息、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 22 passed；覆盖用户消息 Skill 去重、附件、Skill pill、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 22 passed；覆盖用户消息 meta、复制图标、无用户轨迹入口、附件、Skill pill、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 22 passed；覆盖 AI Skill 去重、复制图标、Skill 图标、无底部轨迹入口、Token/耗时展示、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 24 passed；覆盖用户消息/AI 消息复制、clipboard 成功、textarea fallback 成功、fallback 失败、消息布局、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 24 passed；覆盖用户材料派生行过滤、图片预览弹窗、AI 不重复附件、assistant 内 tool-summary、重点内容高亮、复制、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 24 passed；覆盖消息、Composer、运行状态和 Chat 页面壳回归；CSS 检查确认 Composer、用户消息正文、AI 消息正文为 13px。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 24 passed；覆盖语义高亮、普通说明不高亮、消息布局、复制、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx` | pass | 4 passed；覆盖短片段高亮、最多 2 个高亮、低优先级候选不高亮、普通说明不高亮和消息布局回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx` | pass | 4 passed；覆盖用户消息 Skill chip 与首段正文同一 inline flow、第二段 Markdown 块级渲染、复制正文、图片 object URL、assistant 布局和 meta 回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 26 passed；覆盖消息、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx` | pass | 15 passed；覆盖图片 preview URL fallback、Skill 图标统一、用户消息 Skill chip 去尾部 `skill` 文案、AI meta Skill 图标、复制成功/失败图标和 Skill 菜单键盘选择。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx` | pass | 16 passed；覆盖图片缩略图和预览通过 Authorization fetch 转 object URL、object URL 释放、slash 触发菜单删除关闭、按钮触发菜单保持和既有键盘选择。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-execution-labels.test.ts src/chat-messages.test.tsx src/chat-activity.test.tsx src/chat-composer.test.tsx` | pass | 20 passed；覆盖全部规范执行配置展示名、消息 meta、AI tool-summary、Composer 兜底展示和发送 payload raw value。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-execution-labels.test.ts src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 27 passed；覆盖执行配置展示名、消息、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-workbench.test.tsx` | pass | 26 passed；覆盖消息、Composer、运行状态和 Chat 页面壳回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx src/chat-activity.test.tsx src/chat-relations.test.tsx` | pass | 11 passed；覆盖 AI meta 复制图标首位、思考耗时展示、管理关联合并列表、稳定刷新和 REQ/BUG badge。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-execution-labels.test.ts src/chat-messages.test.tsx src/chat-composer.test.tsx src/chat-activity.test.tsx src/chat-relations.test.tsx src/chat-workbench.test.tsx` | pass | 31 passed；覆盖 Chat 消息、Composer、运行状态、管理关联和页面壳回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-execution.test.tsx src/chat-trajectory.test.tsx` | pass | 6 passed；覆盖 v3 trace shell、toolbar/status/card/scrub/raw events、引用快照、文件变更和既有事件详情。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-execution.test.tsx src/chat-trajectory.test.tsx src/chat-workbench.test.tsx src/chat-sessions.test.tsx src/chat-composer.test.tsx src/chat-messages.test.tsx src/chat-activity.test.tsx` | pass | 43 passed；覆盖 Chat 页面壳、会话、Composer、消息、运行状态、执行面板和轨迹回归。 |
| `uv run pytest tests/unit/test_chat_platform_script.py -q` | pass | 5 passed；覆盖 Chat/Governance Compose `.agents` 只读挂载。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |
| `./scripts/generate-openapi-client.sh` | partial | 已导出 `src/web/openapi.json`；脚本在 pnpm/corepack 版本检查处因本机缓存缺失退出。 |
| `./src/web/node_modules/.bin/orval --config src/web/orval.config.ts` | pass | 使用同一份 OpenAPI JSON 生成 Chat/Governance 客户端。 |
| `node scripts/check-chat-materials.cjs http://127.0.0.1:18112 ../../openspec/archive/2026-09-29-add-chat-workbench-image-skill-context/evidence/ui` | pass | 2 screenshots + computed style；synthetic Chat API mocks，真实前端组件和样式；覆盖 Skill token 位于 `chat-rich-composer` 内容流、`chat-prompt` 为 inline 且不进入附件材料条；本轮复验重新生成 `materials-dark-1440.png`、`materials-light-390.png` 与 `materials-computed.json`。 |
| `node scripts/check-chat-materials.cjs http://127.0.0.1:18112 ../../openspec/archive/2026-09-29-add-chat-workbench-image-skill-context/evidence/ui` | pass | 2 screenshots + computed style；synthetic Chat API mocks，真实前端组件和样式；覆盖本轮 Composer 与消息样式回归。 |
| `node scripts/check-chat-materials.cjs http://127.0.0.1:18112 ../../openspec/archive/2026-09-29-add-chat-workbench-image-skill-context/evidence/ui` | pass | 2 screenshots + computed style；synthetic Chat API mocks，真实前端组件和样式；覆盖用户消息 inline flow 返修后的页面渲染。 |
| `node scripts/check-chat-materials.cjs http://127.0.0.1:18112 ../../openspec/archive/2026-09-29-add-chat-workbench-image-skill-context/evidence/ui` | pass | 2 screenshots + computed style；synthetic Chat API mocks，真实前端组件和样式；覆盖执行配置展示名返修后的页面渲染。 |
| `node scripts/check-chat-materials.cjs http://127.0.0.1:18112 ../../openspec/archive/2026-09-29-add-chat-workbench-image-skill-context/evidence/ui` | pass | 2 screenshots + computed style；synthetic Chat API mocks，真实前端组件和样式；覆盖 AI meta 与管理关联返修后 Chat 页面视觉回归；管理关联弹窗由 `chat-relations.test.tsx` 组件测试覆盖。 |
| `node scripts/check-chat-materials.cjs http://127.0.0.1:18112 ../../openspec/archive/2026-09-29-add-chat-workbench-image-skill-context/evidence/ui` | pass | 2 screenshots + computed style；synthetic Chat API mocks，真实前端组件和样式；覆盖 Composer 下拉面板统一后的 Chat 页面视觉回归。 |
| `node scripts/check-chat-event-display.cjs http://127.0.0.1:18112` | blocked | 脚本已更新为轨迹 v3 视觉验收；本地 dev server 因 corepack/pnpm 缓存缺失和 `data/runtime` 工作区副本依赖解析 warning 未稳定提供页面，本轮未生成截图，需环境恢复后补跑。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-workbench.test.tsx src/chat-execution.test.tsx src/chat-trajectory.test.tsx` | pass | 14 passed；覆盖轨迹面板 footer 文案移除、trace-wrap 与 Composer 共享 1120px 内容轨道、v3 trace shell 回归。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-workbench.test.tsx src/chat-execution.test.tsx src/chat-trajectory.test.tsx` | pass | 14 passed；覆盖 trace-wrap 清除左右 padding、桌面内容边缘与 Composer 对齐、窄屏保留 24px 页面安全边距和 v3 trace shell 回归。 |
| `uv run pytest src/backend/tests/test_chat.py::test_write_policy_requires_current_role_and_sprint_change src/backend/tests/test_chat.py::test_conversation_read_includes_write_scope src/backend/tests/test_chat_app_server.py::test_named_profile_downgrades_write src/backend/tests/test_chat_app_server.py::test_named_profile_supports_governance_scope` | pass | 4 passed；覆盖无主对象完全只读、早期 REQ 治理可写、Sprint/Change 双向纳入后实现可写、角色撤销和 App Server governance profile。 |
| `./node_modules/.bin/vitest run src/chat-composer.test.tsx` | pass | 14 passed；覆盖 Composer 权限状态展示、既有提示、上传、Skill、下拉和发送回归。 |
| `./scripts/generate-openapi-client.sh` | partial | 已导出 `src/web/openapi.json`；脚本包装层因本机 pnpm/corepack 缓存缺失在版本检查处退出。 |
| `./node_modules/.bin/orval --config orval.config.ts` | pass | 本地 Orval 8.29.0 已基于最新 OpenAPI JSON 生成 Chat/Governance/Capture 客户端。 |
| `./node_modules/.bin/tsc -b tsconfig.json` | pass | 前端类型检查通过。 |
| `uv run pytest src/backend/tests/test_chat.py::test_write_policy_requires_current_role_and_sprint_change src/backend/tests/test_chat.py::test_conversation_read_includes_write_scope src/backend/tests/test_chat.py::test_running_turn_keeps_original_read_only_scope_after_primary_object_added -q` | pass | 3 passed；覆盖无主对象完全只读、关联 BUG/REQ 后治理可写、运行中 Codex turn 保持启动时只读 scope，下一轮会话策略刷新为治理可写。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-composer.test.tsx src/chat-relations.test.tsx` | pass | 18 passed；覆盖 Composer 权限状态 hover/aria、管理关联保存回传关系并触发父级刷新、既有上传/Skill/下拉回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |
| `uv run pytest src/backend/tests/test_chat.py::test_diff_marks_workspace_snapshot_status -q` | pass | 覆盖轨迹 diff 返回当前工作区状态：未跟踪文件标记 `untracked`，快照内容与磁盘内容不一致标记 `mismatch`。 |
| `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-rendering.test.tsx src/chat-execution.test.tsx` | pass | 覆盖文件变更快照文案、`新增（未跟踪）`、快照不一致提示和轨迹文件变更回归。 |
| `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass | 前端类型检查通过。 |

## 边界与残余风险

| 项 | 结论 |
|---|---|
| 上传内容读取 | 本轮实现文件和图片上传及上下文绑定；历史消息仍展示脱敏摘要，不直接公开对象存储内部 key。 |
| MySQL 实机 | 本轮未配置独立 MySQL 测试库；新增表使用既有 SQLAlchemy 通用类型与 create_all 迁移路径，SQLite 聚焦回归通过。 |
| Docker 本地完整上传 | 本轮未启动 Docker 矩阵；已通过后端对象存储假实现覆盖上传与重验路径，后续 Docker 验收需按对象存储策略解析实际端口并准备一次性测试身份。 |
