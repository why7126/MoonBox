---
requirement_id: REQ-0028-chat-skill-codex
title: Chat 工作台多图片输入与 Skill 快速引用验收标准
acceptance_status: passed
created_at: 2026-09-14 23:17:57
updated_at: 2026-09-29 14:41:41
owner: product
source: requirement.md
---

# 验收标准

## 功能 AC

- [ ] AC-001 用户在创建 Chat 会话前可选择当前仓库分支；默认优先 `main`，仓库无 `main` 时优先 `master`，候选从 Git 仓库读取。
- [ ] AC-002 会话创建后分支随会话锁定，历史会话不再把仓库字段误展示为可编辑仓库选择。
- [ ] AC-003 用户可在 Chat 工作台输入区添加多张图片或受支持文件，发送前可看到稳定材料条、顺序、文件名、类型、大小或脱敏摘要。
- [ ] AC-004 用户可移除任意单个图片或文件，移除后其他材料、文字草稿和 Skill 引用不丢失。
- [ ] AC-005 图片/文件数量、格式、单项体积、总大小和文本长度由服务端能力或共享配置约束，前后端校验一致。
- [ ] AC-006 图片/文件上传失败、格式不支持、体积超限、服务端不可读或执行端不支持材料时，页面阻止发送或标记不可用，并给出可恢复提示。
- [ ] AC-007 仅材料输入策略明确：若允许，仅图片或文件发送时页面提示材料会作为本轮上下文；若不允许，发送按钮禁用并说明原因。
- [ ] AC-008 本轮发送成功后，历史轮次可追溯图片/文件数量、顺序、类型、大小和脱敏引用摘要，不展示完整图片或文件敏感内容。
- [ ] AC-009 用户可打开 Skill 快速引用入口，并查看当前会话绑定仓库中有权访问的 Skill 候选。
- [ ] AC-010 Skill 候选展示英文名和中文描述，中文描述优先来自 `SKILL.md` frontmatter `description`；仓库未绑定、无权限、读取失败或元数据缺失时展示明确空态或错误摘要。
- [ ] AC-011 用户输入 `/`、`/keyword` 或点击文件上传按钮右侧的 Skill 按钮时均打开 `.agents/skills` 候选列表；`/keyword` 按 Skill id、英文名和中文描述模糊搜索。
- [ ] AC-011A Docker 后端治理根目录可只读访问仓库 `.agents/skills`，仓库存在 Skill 时不得误显示“当前仓库暂无可引用 Skill”。
- [ ] AC-011B Skill 候选列表支持键盘操作：打开菜单后默认选中第一条可用候选，`ArrowDown` / `ArrowUp` 移动选中项，`Enter` 选中并填入输入框，`Escape` 关闭菜单，普通 Enter 发送语义不回退；由 `/` 或 `/keyword` 触发的菜单在用户删除触发查询后自动关闭，由 Skill 按钮打开的菜单不因普通文本输入误关闭。
- [ ] AC-012 用户选中 Skill 后，输入区在 rich composer 用户消息内容流内以无边框 inline chip 展示图标和 Skill 英文名，文本从 chip 后继续输入并自然换行；允许通过移除按钮、`Delete` 或 `Backspace` 在发送前移除，不展示 `context_reference_only` 等内部说明，且不把 Skill token 放入图片/文件附件材料条。
- [ ] AC-013 Skill 引用仅作为本轮上下文材料或约束提示传入执行链路，不自动执行 `/req-*`、`/bug-*`、`/opsx-*`、`/sprint-*` 或其他写入型命令。
- [ ] AC-014 Chat 页面顶栏保留会话标题、历史和新建会话入口；顶栏下方以 segmented tabs 展示【对话】/【轨迹】，并在同一 subbar 展示连接状态、主对象摘要和管理关联入口。
- [ ] AC-015 历史入口打开的弹窗支持搜索、状态筛选、置顶/最近/更早分组列表和行内图标动作，并保留会话切换、置顶、重命名、归档或恢复、删除权限语义。
- [ ] AC-016 轨迹视图采用 toolbar、状态摘要、搜索、scrub 概览和事件行列表布局，并保留事件详情、原始事件、引用快照、Diff、停止和重试语义。
- [ ] AC-019 会话创建前输入区不展示项目或仓库选择；仓库由当前空间绑定仓库自动注入会话创建、材料上传和 Skill 候选读取，用户只选择分支。
- [ ] AC-020 历史消息回显时，图片或文件摘要显示在用户消息泡上方，Skill 引用以轻量 chip 融入用户消息泡内容流，meta 与执行配置跟随消息组展示。
- [ ] AC-021 AI 运行状态块在连接中、排队中、执行中、停止中、失败或等待结果状态下，与 Composer 输入框使用同一内容轨道并左边缘对齐，内部正文保持可读宽度。
- [ ] AC-022 用户消息按附件 turn-user 结构呈现：附件缩略图在气泡上方，Skill pill 与首段正文位于同一 inline 内容流，文本从 Skill chip 后继续排版并自然换行；第二段及复杂 Markdown 保持块级阅读层级；meta 位于气泡下方并保留复制图标，不展示查看本轮轨迹入口。
- [ ] AC-023 AI 消息按附件 turn-assistant 结构呈现：avatar、assistant-col、tool-summary、bubble-assistant 和 meta 层级清晰，运行状态摘要保留点击查看轨迹能力。
- [ ] AC-024 用户消息气泡不重复展示 Skill 引用；当已存在 Skill pill 时，历史旧数据中的 `Skill 引用：xxx` 派生说明不得作为用户正文显示。
- [ ] AC-025 用户消息 meta 按参考稿呈现：模型信息与时间在同一行，模型信息位于最前并使用更亮的 mono 弱强调色；执行配置展示名统一为 `Codex`、`GPT-6 Astra`、`GPT-5.6 Sol`、`GPT-5.6 Terra`、`GPT-5.6 Luna`、`GPT-5.5`、`XHigh`、`High`、`Medium`、`Low`，模型下拉按 `GPT-6 Astra`、`GPT-5.6 Sol`、`GPT-5.6 Terra`、`GPT-5.6 Luna`、`GPT-5.5` 顺序展示，底层 payload/API/DB 继续使用原始 value；复制为图标按钮且保留可访问标签；用户消息不展示查看本轮轨迹入口。
- [ ] AC-026 AI 消息 meta 按参考稿左对齐呈现：复制图标位于第一位，Skill 图标、时间和已采集统计与 AI 正文左边缘一致；AI 正文不重复展示 Skill pill；底部 meta 不展示 `查看本轮轨迹`，上方 tool-summary 保留点击查看轨迹能力。
- [ ] AC-027 AI 耗时与 Token 统计只展示当前事件或 API 已采集字段；首 token 延时、思考/推理耗时、输入 token、输出 token 或思考 token 缺少事实源时不得伪造展示；tool-summary 仅在存在明确思考/推理耗时字段时显示 `已完成（思考 x）`。
- [ ] AC-028 用户消息与 AI 消息复制图标均执行真实复制动作：优先使用浏览器剪贴板 API，失败或不可用时回退 textarea + `execCommand`；用户消息复制过滤后的可见正文，AI 消息复制 AI 正文，并提供短暂已复制或复制失败的可访问状态。
- [ ] AC-029 用户消息正文不得展示 `图片引用：xxx`、`文件引用：xxx` 或 `Skill 引用：xxx` 派生材料说明；图片或文件材料只显示在用户消息泡上方材料区，图片材料支持点击真实图片预览，缺少 `preview_url` 但存在授权 `ref_id` 时通过受控材料内容读取接口生成预览地址；图片缩略图和预览弹窗通过带 Authorization 的前端 fetch 读取材料内容并用 object URL 渲染，不让 `<img>` 直接请求 Bearer 接口，object URL 在切换、关闭或卸载时释放；缺少授权事实源时才只展示材料摘要。
- [ ] AC-030 AI 消息不重复展示用户上传图片或文件附件；tool-summary 位于 assistant-col 第一行并与 AI 图标同组呈现，样式包含边框、状态点、模型 tag 分隔；AI 正文中的关键结论、风险/阻塞、动作结果和下一步等重点内容基于语义特征使用受控高亮样式差异化，不绑定固定示例文案，且每条消息最多高亮 1-2 个高优先级短片段，避免整句大面积高亮。
- [ ] AC-031 Composer Skill 按钮、输入区 inline chip、Skill 候选列表、用户消息 Skill chip 和 AI meta Skill 图标使用同一 Skill 图标；用户消息 Skill chip 仅显示图标和 Skill 英文名，不显示尾部 `skill` 文案。
- [ ] AC-032 复制按钮点击成功后临时切换为已复制图标，复制失败后临时切换为失败图标，并保留 aria-label / title 等可访问状态，数秒后恢复复制图标。
- [ ] AC-033 Skill 候选列表字号和密度贴近 Chat 13px 输入体系：主标题约 13px，摘要约 11.5-12px，行高约 1.45，选中态清晰但不显得过重。
- [ ] AC-034 管理关联弹窗打开时复用缓存或预取候选，候选区保持稳定，不因读取授权对象从整块 loading 跳变为完整列表；搜索、主对象和引用对象选择整合为一个可搜索候选列表；REQ 与 BUG 候选使用文字 badge 和不同低饱和颜色区分，底层保存仍使用 `primary` 与 `references[]` 语义。
- [ ] AC-035 输入区 Skill、模型和推理三类下拉面板样式一致，使用统一 popover 视觉、字号密度、hover/active/disabled 状态和外部点击或 Escape 关闭逻辑；面板打开后，点击输入框空白、Composer 工具栏空白或页面空白均自动隐藏，仅当前面板内部和对应触发按钮不按外部点击处理；切换触发器时面板互斥，Skill 保留搜索与键盘选择，模型/推理保留单选语义。
- [ ] AC-036 轨迹 Tab 按 `moonbox-chat-redesign-v3.html` 参考稿复刻：以 `trace-wrap` 承载 `trace-toolbar`、`trace-status`、`trace-card`、`trace-controls`、`scrub`、`event-list`、`disclosure/raw-events-box`、引用快照和文件变更 `section-block`；保留搜索、事件选择详情、原始事件、引用快照、Diff、停止、重试和真实 payload/API 语义，不写入参考稿 demo 文案。
- [ ] AC-037 轨迹 Tab 内容区与底部 Composer 输入框保持同一内容宽度轨道；轨迹面板不展示“仅展示实际执行产生的事件与文件变更”等解释性 footer 文案。
- [ ] AC-038 轨迹 Tab 的实际内容边缘与 Composer 输入框外边缘对齐；`trace-toolbar`、`trace-status`、`trace-card`、引用快照和文件变更区不得因外层左右 padding 相对输入框内缩。
- [ ] AC-039 轨迹 Tab 文件变更区必须区分执行快照与当前本地工作区状态：比较范围文案使用“本轮执行快照 / 会话累计快照”；新增但当前 Git 未跟踪的文件显示“新增（未跟踪）”；快照内容与当前磁盘内容不一致时展示明确提示，避免用户误以为执行快照代表本地文件实时状态。
- [ ] AC-014 Skill 内容过长时按服务端策略摘要或截断，并提示实际注入范围；历史轮次保留 Skill 名称、版本或内容摘要。
- [ ] AC-015 发送时后端重验会话所有者、空间成员、仓库授权、文件/图片引用和 Skill 读取权限；权限撤销后不得继续使用旧引用。
- [ ] AC-016 发送中、停止中、状态未知、会话归档、服务未就绪或仓库缺失时，分支、文件上传与 Skill 控件遵循既有 Chat 工作台门禁。
- [ ] AC-017 重复点击、网络重发或响应丢失时，服务端复用既有会话与轮次幂等策略，不重复创建会话或重复提交同一轮材料。
- [ ] AC-018 多文件/图片和 Skill 引用不削弱现有对话/轨迹双视图、消息复制、本轮轨迹入口、停止、重试、Diff、权限和会话历史能力。

## UI AC

- [ ] AC-UI-001 输入区在图片/文件材料、Skill token、执行配置、状态提示和发送按钮同时存在时保持稳定布局，不挤压文本输入或造成横向溢出。
- [ ] AC-UI-002 图片/文件材料具备稳定尺寸、删除入口、上传中、成功、失败和可重试状态，并显示在输入框上方。
- [ ] AC-UI-003 Skill token 支持长名称截断或 tooltip，并作为用户消息内容流内的 inline chip 展示；不把完整 Skill 内容、注入范围或内部说明展开在输入区。
- [ ] AC-UI-004 对话区局部贴近用户提供的 Image #1：右侧用户气泡、助手分节正文、链接式文件引用、摘要列表、下一步和待处理区层级清晰。
- [ ] AC-UI-005 视觉迁移保留 MoonBox Ops 视觉系统、深浅主题、共享导航、空间权限和既有 Chat 业务语义。
- [ ] AC-UI-006 窄屏下图片预览、Skill token、文件链接、状态摘要和发送动作可换行或折叠，不产生页面横向溢出。
- [ ] AC-UI-007 菜单、Popover、上传预览浮层或 Skill 选择器支持清晰退出路径；声明支持外部点击关闭时，需覆盖内部 `stopPropagation` 后外部点击仍关闭的证据。
- [ ] AC-UI-008 输入框左下角使用文件上传图标，文件上传按钮右侧放置 Skill 图标按钮，支持图片和文件多选；发送按钮只显示发送图标并支持 Enter 发送、Shift+Enter 换行。
- [ ] AC-UI-009 Agent、模型和推理选择位于发送按钮左侧。
- [ ] AC-UI-010 Composer 输入区采用参考图深色 Dock 风格，背景、边框、圆角、分隔线和底部工具栏层级与页面主背景区分清晰。
- [ ] AC-UI-011 历史弹窗行内操作按钮默认弱化，hover 或 focus 时清晰展示，删除动作保持危险态且不削弱禁用语义。
- [ ] AC-UI-012 Composer 输入本体以及输入区与工具栏之间不显示分隔线；聊天输入框、用户消息正文和 AI 消息正文使用 13px，其中输入框保持 1.6 行高。

## 安全与观测 AC

- [ ] AC-OBS-001 行为事件只记录添加图片、移除图片、添加文件、移除文件、选择 Skill、移除 Skill 和发送结果等稳定事件名及脱敏属性。
- [ ] AC-OBS-002 请求日志只记录接口状态、错误码、材料数量、耗时和脱敏摘要，不保存完整请求体、完整 Prompt、完整图片、文件正文或完整回复。
- [ ] AC-OBS-003 Task Trace 覆盖材料校验、对象存储写入、Skill 解析、上下文构造、执行提交和结果处理节点。
- [ ] AC-OBS-004 观测 metadata 经过脱敏、截断和安全 JSON 序列化，不保存 Authorization、Cookie、Token、密钥、本机绝对路径、对象存储内部完整 key、签名 URL 或真实客户敏感数据。
- [ ] AC-OBS-005 观测失败不阻断主流程，但保留脱敏降级摘要，便于排障。
- [ ] AC-OBS-006 新增或调整 API 字段时同步 OpenAPI、客户端生成、错误码、API 文档和接口测试；新增持久化字段时同步数据库设计、迁移和 SQLite/MySQL 兼容测试。
- [ ] AC-OBS-007 Chat Codex 写权限必须区分治理写入、产品实现写入和完全只读：早期 REQ/BUG 可在受控治理目录写入对应文档，不要求主对象已处于实现阶段；产品实现文件写入仍要求主对象处于正式 Sprint 范围，且 Change 与 Sprint 双向纳入；前端需展示治理可写、实现可写或完全只读状态，管理关联保存主对象后立即刷新会话写权限状态；无主对象时通过状态胶囊 hover / aria 提示引导先设置主对象；已有运行中的 Codex turn 保持启动时权限，下一轮才使用最新范围。

## 横切 AC（knowledge-base）

> 来源：`docs/knowledge-base/best-practices/admin-media-upload-chain.md`、`docs/knowledge-base/retrospectives/sprint-005-retrospective.md` — 预防上传链路、事实源漂移和状态假成功类缺陷。

- [ ] AC-XCUT-001 图片/文件上传组件具备 `idle -> uploading -> done/failed` 状态机，状态在 UI、请求和本轮上下文记录中一致。
- [ ] AC-XCUT-002 上传中禁用重复提交和重复选择触发；失败后允许单项重试或移除，不清空其他材料。
- [ ] AC-XCUT-003 上传成功后同一会话立即回显材料预览或摘要和引用状态，不依赖刷新页面。
- [ ] AC-XCUT-004 上传成功后的 URL、对象 key 或临时引用不得写入日志敏感上下文，不泄露临时凭据。
- [ ] AC-XCUT-005 Docker 本地验收必须从环境或启动脚本解析实际 Web 端口，完成图片上传、读取和回显验证，不硬编码默认端口。
- [ ] AC-XCUT-006 Docker 或本地验收脚本需准备一次性测试身份、测试会话或可回收 fixture，不依赖持久库默认管理员密码。
- [ ] AC-XCUT-007 卡片、消息和历史状态必须以服务端事实源为准；前端临时预览不得冒充已持久化或已进入执行上下文。
- [ ] AC-XCUT-008 Sprint 容量或实现范围收敛时，图片上传、Skill 引用、视觉基线和观测验收不可被无说明地拆走；延期项需在 Change/Sprint 文档中显式记录。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 `/req-complete` 已完成原型拆解，覆盖页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [ ] AC-PROTOTYPE-002 `/req-opsx` 必须在 Change `design.md` 写入 UI Contract 与 UI Skeleton，覆盖页面壳、输入区、图片预览、Skill 菜单、消息区和轨迹入口。
- [ ] AC-PROTOTYPE-003 `/opsx-apply` 完成 UI 任务前必须提供 1440px 桌面视口、窄屏、深浅主题和关键交互截图或等价证据。
- [ ] AC-PROTOTYPE-004 `/opsx-archive` 前必须确认 linked REQ 与最终 Change 设计、截图、computed style、Mock/API 边界和实现证据一致。

## UI Reference Replication Contract 种子

| 项 | 验收要求 |
|---|---|
| 保真模式 | 局部一致 / 风格迁移；不逐像素复刻整页。 |
| 参考事实源 | 用户提供 Image #1、`prototype/web/context.md`、本验收文档、`rules/ui-design.md`、既有 Chat 工作台。 |
| 组件清单 | 页面壳、对话滚动区、右侧用户气泡、助手正文块、分节标题、链接式文件引用、状态摘要、下一步区、待处理区、分支选择、图片/文件材料条、Skill 引用 token、输入区、执行配置、发送/停止动作。 |
| 动作按钮矩阵种子 | 分支选择、文件添加、文件移除、文件重试、Skill 打开选择、`/` 选择 Skill、Skill 移除、发送、停止。 |
| 证据要求 | 后续 Change 需补 selector 映射、动作按钮矩阵、computed style 采样、分批截图和关键交互证据。 |
| 非目标 | 不复刻截图中的具体历史命令、耗时、路径、账号信息或执行结果；不取消现有轨迹详情、权限、Diff、历史和治理边界。 |

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-29 14:41:41
accepted_by: workflow-sync
source_change: add-chat-workbench-image-skill-context
source_sprint: sprint-006
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 实现验收证据

| 类别 | 证据 | 结论 |
|---|---|---|
| 后端 | `uv run --project src/backend pytest src/backend/tests/test_chat.py -q` | 36 passed, 1 skipped；覆盖材料快照、历史摘要、图片/文件限制、对象存储上传、受控材料内容读取、分支候选、Skill 候选、行为事件、Trace 脱敏与既有 Chat 回归。 |
| 前端 Composer | `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-composer.test.tsx` | 12 passed；覆盖文件上传入口、Skill 按钮位于上传按钮右侧、`/bug` 模糊搜索、中文描述展示、Skill token 作为 rich composer inline chip 且不进入附件材料条、`Delete` 删除同步 `chat.skill_remove` 和 payload、Skill 菜单键盘选择、删除 slash 查询自动关闭、按钮触发菜单保留、材料发送、幂等重试、自动仓库注入、分支选择、Composer 执行配置展示名和发送 payload 继续使用 raw value。 |
| 前端消息布局 | `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-messages.test.tsx` | 4 passed；覆盖用户消息 turn-user、Skill chip 与首段正文同一 inline 内容流、第二段 Markdown 块级渲染、图片/文件/Skill 派生行过滤、附件在用户消息泡上方、真实图片通过 Authorization fetch + object URL 渲染、object URL 释放、统一 Skill 图标、用户消息 Skill chip 去尾部 `skill` 文案、assistant avatar/column/tool-summary/body/meta、AI 不重复附件、重点内容语义高亮、用户/AI 消息复制图标成功/失败反馈、clipboard 成功、fallback 成功和失败状态。 |
| 前端执行配置展示名 | `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-execution-labels.test.ts src/chat-messages.test.tsx src/chat-activity.test.tsx src/chat-composer.test.tsx` | 20 passed；覆盖 Codex、GPT-6 Astra、GPT-5.6 Luna、GPT-5.6 Terra、GPT-5.6 Sol、GPT-5.5、XHigh、High、Medium、Low 展示名，以及消息 meta、AI tool-summary 和 Composer 兜底展示。 |
| 前端运行状态 | `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-activity.test.tsx` | 4 passed；覆盖 tool-summary 运行状态块、失败态、授权失败、思考耗时展示和执行配置摘要回归。 |
| 前端管理关联 | `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-relations.test.tsx` | 4 passed；覆盖管理关联候选列表稳定刷新、搜索与主对象/引用对象整合、REQ/BUG 类型 badge、保存失败草稿保留，以及保存后回传关联结果供上层刷新会话写权限。 |
| 前端轨迹布局 | `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-execution.test.tsx src/chat-trajectory.test.tsx` | 6 passed；覆盖 v3 trace shell、toolbar/status/card/scrub/raw events、引用快照、文件变更和既有事件详情。 |
| 前端轨迹宽度与文案 | `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-workbench.test.tsx src/chat-execution.test.tsx src/chat-trajectory.test.tsx` | 14 passed；覆盖轨迹面板 footer 文案移除、trace-wrap 与 Composer 共享 1120px 内容轨道、v3 trace shell 回归。 |
| 前端轨迹内容边缘 | `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-workbench.test.tsx src/chat-execution.test.tsx src/chat-trajectory.test.tsx` | 14 passed；覆盖 trace-wrap 清除左右 padding、桌面内容边缘与 Composer 对齐、窄屏保留 24px 页面安全边距。 |
| 轨迹文件变更快照语义 | `uv run pytest src/backend/tests/test_chat.py::test_diff_marks_workspace_snapshot_status -q` + `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-rendering.test.tsx src/chat-execution.test.tsx` | 后端覆盖 `untracked` / `mismatch` 当前工作区状态；前端覆盖“本轮执行快照 / 会话累计快照”、`新增（未跟踪）` 和快照不一致提示。 |
| Chat 写权限门禁 | `uv run pytest src/backend/tests/test_chat.py::test_write_policy_requires_current_role_and_sprint_change src/backend/tests/test_chat.py::test_conversation_read_includes_write_scope src/backend/tests/test_chat.py::test_running_turn_keeps_original_read_only_scope_after_primary_object_added -q` | 3 passed；覆盖无主对象完全只读、早期 REQ 治理可写、Sprint/Change 双向纳入后实现可写、角色撤销，以及运行中的 Codex turn 不从 read-only 热升级为治理写。 |
| 前端权限状态 | `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-composer.test.tsx src/chat-relations.test.tsx` | 18 passed；覆盖 Composer 展示治理可写/完全只读状态、可读只读原因 hover/aria、既有上传/Skill/下拉/发送回归，以及管理关联保存后回传刷新会话写权限所需事实。 |
| 前端布局回归 | `./src/web/node_modules/.bin/vitest run --environment jsdom --root src/web src/chat-execution.test.tsx src/chat-trajectory.test.tsx src/chat-workbench.test.tsx src/chat-sessions.test.tsx src/chat-composer.test.tsx src/chat-messages.test.tsx src/chat-activity.test.tsx` | 43 passed；覆盖对话/轨迹 segmented tabs 与 subbar 状态区、会话、Composer、消息、运行状态、执行面板和轨迹回归。 |
| 部署 | `uv run pytest tests/unit/test_chat_platform_script.py -q` | 5 passed；覆盖 Chat/Governance Compose `.agents` 只读挂载。 |
| 类型 | `./src/web/node_modules/.bin/tsc -b src/web/tsconfig.json` | pass。 |
| API | OpenAPI JSON + 本地 Orval 8.29.0 | `src/web/openapi.json` 与 `src/web/src/api/generated/chat.ts` 已同步，包含受控材料内容读取接口；pnpm/corepack 本机缓存缺失导致包装脚本未能完成后续 Orval 调用，已直接调用本地 Orval。 |
| UI | `src/web/scripts/check-chat-materials.cjs` | 生成 1440px 与 390px 截图及 computed style；使用 synthetic API mocks，真实前端组件和样式；覆盖 Skill token 位于 `chat-rich-composer` 内容流内、`chat-prompt` 为 inline 且不进入附件材料条。 |
| UI 轨迹 v3 | `src/web/scripts/check-chat-event-display.cjs` | 脚本已更新为轨迹 v3 视觉验收，采样 `trace-wrap`、`trace-card`、`event-row`、`raw-events-box` 和 `section-block`；本地 dev server 因 corepack/pnpm 缓存缺失和 `data/runtime` 工作区副本依赖解析 warning 未稳定提供页面，本轮未生成截图，需环境恢复后补跑。 |

## 实现边界

- 当前材料能力已接入后端对象存储上传；历史消息仍只展示 opaque 引用和脱敏摘要，不暴露内部对象 key 或签名 URL。
- Skill 引用只作为 `context_reference_only` 快照保存名称、相对来源、摘要和 digest，不自动执行写入型命令。
- MySQL 实机矩阵本轮未连接配置库；新增表使用既有 SQLite/MySQL 通用 SQLAlchemy 类型，SQLite 聚焦回归通过。
