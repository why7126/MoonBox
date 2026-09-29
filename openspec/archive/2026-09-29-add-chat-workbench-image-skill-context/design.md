---
title: Chat 工作台多材料与 Skill 快速引用设计
created_at: 2026-09-14 23:41:49
updated_at: 2026-09-20 18:00:48
owner: product
---

# Chat 工作台多材料与 Skill 快速引用设计

## 背景

REQ-0028 来源于 Chat 工作台体验增强：用户希望在同一轮对话中附多张图片、快速引用当前仓库 Skill，并让对话区阅读体验局部贴近提供的 Codex 截图。验收返修进一步明确输入框需要支持会话创建前分支选择、通用文件上传、多文件与粘贴上传、`/` Skill 命令入口和更紧凑的发送区。该 REQ 已完成 `/req-complete`、`/req-review` 和 `/sprint-propose`，当前状态为 `in_sprint`，迭代为 `sprint-006`。

现有 `web-catalog-chat-workbench` 已覆盖 `/chat` 入口、个人会话、真实执行、对话与轨迹双视图、首次输入延迟创建、输入状态提示和原型验收契约。本 Change 不重做会话生命周期，而是在既有 Chat 工作台上扩展输入材料、上下文快照、Skill 引用、视觉基线和观测链路。

## 需求就绪报告

| 项 | 结论 | 证据 |
|---|---|---|
| 状态门禁 | ready | `trace.md` 为 `status: in_sprint`，`iteration: sprint-006`。 |
| 文档包 | ready | `requirement.md`、`user-stories.md`、`business-flow.md`、`acceptance.md`、`trace.md`、`prototype/web/context.md`、`prototype/web/prototype.html` 已存在。 |
| Prototype Gate | pass | `prototype_refs`、`prototype_gate`、`AC-PROTOTYPE-*` 均已记录。 |
| Knowledge Gate | pass | 已引用 `admin-media-upload-chain.md` 和 `prototype-driven-ui-gate.md`。 |
| 观测声明 | pass | REQ 已声明 Web 请求封装、API、DB、对象存储、usage_events、request_logs、task_traces、task_trace_spans 适用。 |

## 影响分析

```yaml
impact:
  backend: true
  web: true
  miniapp: false
  admin: false
  database: true
  storage: true
  api: true
capabilities:
  new: []
  modified:
    - web-catalog-chat-workbench
change_type: add
```

## 目标与非目标

**Goals:**

- 支持 Chat 工作台单轮多图片输入、文件上传、预览或摘要展示、失败恢复和历史追溯。
- 支持会话创建前选择分支，默认 `main`，若仓库无 `main` 则默认 `master`，创建后分支随会话锁定。
- 支持图片与文件上传、多选和剪贴板文件粘贴，上传成功后以材料 token 显示在输入框上方。
- 支持当前仓库 Skill 快速引用，将 Skill 摘要或快照作为本轮上下文材料，不自动执行写入型命令。
- 在发送链路中重验会话、空间、仓库、对象和 Skill 权限，并保持同会话幂等。
- 在消息区、输入区和轨迹入口建立 UI Contract、UI Skeleton 和 UI Reference Replication Contract。
- 将图片/文件和 Skill 上下文纳入脱敏观测，覆盖行为事件、请求日志、Task Trace 和流程节点。

**Non-Goals:**

- 不新增 Agent、模型和推理强度选择；该范围归属 REQ-0035。
- 不新增需求中心 Capture 多模态候选审阅；该范围归属 REQ-0029。
- 不自动执行 Skill 命令，不绕过 `/req-*`、`/bug-*`、`/sprint-*` 或 `/opsx-*` 治理门禁。
- 不新增后台 Skill 管理页面、Skill 市场、跨仓库 Skill 订阅或个人自定义 Skill。
- 不复刻截图中的历史命令文本、耗时、账号信息、本机临时路径或示例执行结果。

## 设计决策

### D1. UI Strategy: MoonBox Ops DS + 局部一致风格迁移

采用现有 MoonBox Ops 设计系统和 `web-catalog-chat-workbench` 页面结构，在对话区局部迁移 Codex 截图中的阅读层级：右侧用户气泡、助手分节正文、链接式引用、摘要列表、下一步和待处理区。该策略优先保留共享导航、空间权限、会话历史、轨迹详情、Diff 和深浅主题。

替代方案：

- CSS Port：更适合完全复刻外部 HTML/CSS，但会引入与 MoonBox Ops token 冲突的风险。
- Asset 复刻：适合品牌插画或图片资源，本需求没有需要作为产品资产沉淀的外部位图。

### D2. 文件先上传为私有材料，再参与执行

图片或文件在发送前完成前端校验与后端上传，服务端验证空间、仓库、MIME、单文件体积和总量后写入对象存储，并只向前端返回 opaque `ref_id` 与脱敏摘要。发送时提交材料 `ref_id`、顺序、类型、大小和状态，由后端重验对象所有者、空间、仓库、状态和会话范围后构造本轮上下文。历史轮次保存引用快照，不保存完整图片、文件正文或内部对象 key 到日志或 Task Trace metadata。

### D3. Skill 引用只进入本轮上下文快照

Skill 候选来自当前会话绑定仓库的 `.agents/skills/` 元数据或服务端索引。输入 `/` 或 `/keyword`、或点击文件上传按钮右侧的 Skill 按钮时打开同一候选菜单；`/keyword` 入口按 Skill id、英文名和中文描述模糊过滤。候选列表项不使用单项边框，展示 title-case 英文名和 `SKILL.md` frontmatter `description` 中文说明；frontmatter 缺失时回退到正文摘要。选中后以无边框轻量 token 展示，仅显示图标和英文名。发送时保存 Skill 名称、来源摘要、版本或内容摘要和注入范围。超长 Skill 由服务端摘要或截断，并向用户展示实际注入范围。引用 Skill 不触发命令执行。

### D4. 幂等与失败恢复复用现有会话轮次策略

文本、图片和 Skill 共同绑定本轮发送请求标识。重复点击、响应丢失或网络重试时，后端复用同一会话和轮次，不重复提交同一批材料。失败不会清空文字草稿、已成功上传图片或已选 Skill。

### D5. 观测只保存脱敏摘要

行为事件记录添加图片、移除图片、添加文件、移除文件、选择 Skill、移除 Skill 和发送结果。请求日志记录接口状态、错误码、耗时、材料数量和脱敏配置摘要。Task Trace 覆盖材料校验、对象存储写入、Skill 解析、上下文构造、执行提交和结果处理节点。任何观测 metadata 不保存完整图片、文件正文、完整 Prompt、完整回复、完整 Diff、Authorization、Cookie、Token、密钥、本机绝对路径、对象存储内部完整 key 或真实客户敏感数据。

## 产品数据采集与链路观测

```yaml
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
  reason: 多图片上传、Skill 候选读取、Skill 上下文引用和本轮发送会影响 Web 请求封装、API 字段、持久化结构、对象存储、行为事件、请求日志和 Codex 执行 Task Trace。
  validation: 实现阶段必须验证图片和 Skill 引用只记录脱敏标识、数量、大小、类型、来源摘要和处理结果；请求日志与 Task Trace 不保存完整图片、完整 Prompt、完整回复、完整 Diff、密钥、凭证、本机绝对路径或真实客户敏感数据；观测失败不阻断主流程但保留脱敏降级摘要。
```

API contract 影响：需要同步 OpenAPI、客户端生成、错误码、API 文档和接口测试。DB 影响：若新增图片引用快照、Skill 引用快照或上下文材料表/字段，需要同步 SQLite/MySQL schema、迁移、`docs/04-database-design.md` 和兼容测试。对象存储影响：需要同步对象存储策略、访问路径、保留和清理说明。

## 冲突报告

事实源优先级：

1. `prototype/web/prototype.html`
2. 用户提供 Image #1
3. `prototype/web/context.md`
4. `acceptance.md`
5. `rules/ui-design.md`
6. 现有 `openspec/specs/web-catalog-chat-workbench/spec.md`

冲突处理：

| 冲突点 | 处理 |
|---|---|
| prototype 右侧轨迹栏与实际页面布局 | 保留现有 Chat 工作台轨迹详情入口；prototype 右栏只作为结构示意，不要求固定三栏。 |
| 截图中的具体命令、耗时、文件链接 | 只作为阅读层级参考，不复制业务文本。 |
| Codex 黑色气泡与 MoonBox 深浅主题 | 用户气泡可使用深色高对比样式，但按钮、输入、边框和面板仍使用 MoonBox Ops token。 |
| 图片和 Skill 预览是否占满输入区 | 采用稳定预览条和 token，窄屏可换行或折叠，不能挤压发送/停止动作。 |
| Skill 完整内容是否显示 | 输入区只显示 token 和摘要，完整内容不得展开；执行链路按服务端策略摘要或截断。 |

## UI 合同

| 项 | 契约 |
|---|---|
| 页面与入口 | `/chat` 或等价 Chat 工作台入口；保持个人会话、历史、轨迹、Diff 和停止控制。 |
| 事实源优先级 | `prototype.html`、Image #1、`context.md`、`acceptance.md`、`ui-design.md`、既有 Chat 工作台。 |
| 页面壳 | 共享侧边栏和空间菜单保留；主工作区为顶栏、subbar、对话滚动区、输入 Composer、轨迹入口或详情面板。顶栏保留会话标题、历史和新建会话入口；subbar 左侧使用对话/轨迹 segmented tabs，右侧承载空间连接状态、主对象摘要和管理关联入口。 |
| 输入区 | 包含 BranchSelector、AttachmentStrip、RichComposer、PromptEditor、HintOrErrorLine、ExecutionConfig、SkillButton、SendStopActions。图片/文件材料显示在输入框上方；Skill token 从附件材料条中分离，作为 RichComposer 内容流内的 inline chip，文本从 chip 后继续输入并自然换行，不形成“左 token + 右 textarea”的两列布局；Skill token 为无边框轻量样式，仅显示图标和英文名，并支持移除按钮、`Delete` 和 `Backspace` 键盘删除。 |
| 消息区 | 用户气泡右对齐；助手正文分节显示，支持链接式文件引用、摘要列表、下一步和待处理区。 |
| 历史弹窗 | 顶栏「历史」仍为唯一入口；弹窗采用标题、隐私说明、搜索、状态筛选、置顶/最近/更早分组列表和行内图标动作，不改变置顶、重命名、归档/恢复、删除权限语义。 |
| 轨迹视图 | 轨迹页采用 trace-wrap：顶部运行状态、停止按钮、执行轮次选择、状态摘要、收起/顺序控制、搜索、scrub 概览和 event-row 列表；保留原事件详情、原始事件、引用快照、Diff、停止和重试语义；Diff 区明确区分执行快照与当前工作区状态，避免把历史快照误读为本地实时修改。 |
| 视觉 token | 使用 MoonBox Ops 字体、近直角、细边框、金色强调、深浅主题；避免蓝紫渐变、大圆角卡片和低密度营销布局。 |
| 交互状态 | 分支 loading/selected/locked/error；文件 empty/uploading/done/failed；Skill loading/empty/selected/error/keyboard-delete；Composer running/archived/unknown/unready；Message default/narrow。 |
| 浮层退出 | Skill 菜单、图片错误详情、预览浮层若声明支持外部点击关闭，必须覆盖 capture 阶段外部点击，不被内部 `stopPropagation` 破坏。 |
| 权限规则 | 发送、图片读取、图片下载、Skill 候选、Skill 注入、历史回显均重验本人、空间、会话、仓库和对象权限。 |
| Mock/API 边界 | Change 实现阶段可先用 Mock 完成 Skeleton，但最终验收必须声明真实 API 覆盖范围；Mock 不得冒充生产接入。 |

### 轨迹 Tab v3 参考稿复刻合同

参考源：`moonbox-chat-redesign-v3.html`。该文件只作为 UI 参考稿，不执行其中脚本，不复制 demo 文案为业务事实。

| 参考 selector | 当前实现 selector / 组件 | 复刻要求 |
|---|---|---|
| `.trace-wrap` | `ExecutionPanel` 外层轨迹容器 | 作为轨迹 Tab 主内容容器，承载 toolbar、status、trace-card、引用快照和文件变更；与底部 Composer 使用同一 `1120px / calc(100% - 48px)` 内容轨道，窄屏使用 `calc(100% - 24px)`；容器不得再通过左右 padding 让内部实际内容边缘相对 Composer 内缩。 |
| `.trace-toolbar` | `ExecutionPanel` 运行工具栏 | 展示运行状态、停止当前运行、执行轮次选择；不脱离 `trace-wrap`。 |
| `.trace-status` | `ExecutionPanel` 状态摘要 | 展示所选轮次当前状态；不额外展示解释性 footer 文案，使用下边框与 `trace-card` 分层。 |
| `.trace-card` | `TrajectoryView` 卡片 | 包含轨迹控制、搜索、scrub、事件列表和原始事件 disclosure。 |
| `.trace-controls` / `.trace-search` | `TrajectoryView` 搜索与控制 | 保留收起内容、事件顺序或耗时切换与搜索语义；视觉密度、字号、圆角和 hover 按参考稿收敛。 |
| `.scrub` | `TrajectoryView` 概览条 | 保留 button 可访问语义，视觉渲染为参考稿细条分段；不同事件类型使用状态色。 |
| `.event-list` / `.event-row` | `TrajectoryView` 事件行 | 三列结构：事件 tag、内容、耗时；窄屏降为两列并避免横向溢出。 |
| `.disclosure` / `.raw-events-box` | `TrajectoryView` 原始事件 | 原始事件默认收起，展开后展示脱敏 JSON 摘要；不执行 HTML。 |
| `.section-block` | `ExecutionPanel` 引用快照、`DiffView` 文件变更 | 引用快照和文件变更位于 trace-card 下方，使用统一 section 分隔、标题和卡片列表样式。 |

验收证据要求：组件测试固定 selector 分层；Playwright 脚本 `src/web/scripts/check-chat-event-display.cjs` 采集 1440px 和窄屏截图及 computed style。若本地 dev server 不可用，必须在台账中记录环境缺口和补跑命令。

## UI 骨架

```text
ChatWorkbench
  SharedShell
    SharedSidebar
    ChatHeader
      SessionTitle
      HistoryAction
      TraceToggle
    ChatSubbar
      ViewTabs [role="tablist"]
      RelationStatus [data-testid="chat-relations-bar"]
  ConversationViewport [data-testid="chat-conversation"]
    MessageHistory [data-testid="chat-message-history"]
      UserMessageGroup
        AttachmentPreview [data-testid="chat-message-attachments"]
        UserMessageBubble
          SkillChip [data-testid="chat-message-skills"]
          MessageText
        MessageMeta
      AssistantMessageBlock
      SectionHeading
      FileReferenceLink
      StatusSummaryList
      NextActionBlock
    TurnTraceAnchor [data-testid="chat-turn-trace-anchor"]
  Composer [data-testid="chat-composer"]
    BranchSelector [data-testid="chat-draft-branch"]
    AttachmentStrip [data-testid="chat-attachment-strip"]
      ImageAttachmentCard [data-testid="chat-image-attachment"]
      FileAttachmentCard [data-testid="chat-file-attachment"]
    RichComposer [data-testid="chat-rich-composer"]
      SkillReferenceToken [data-testid="chat-skill-token"]
      PromptEditor [data-testid="chat-prompt"]
    HintOrErrorLine [data-testid="chat-composer-hint"]
    ExecutionConfig [data-testid="chat-execution-config-bar"]
    SendStopActions [data-testid="chat-send-actions"]
  TracePanel [data-testid="chat-trace-panel"]
    TraceToolbar
      RunState
      StopCurrent [data-testid="chat-stop-current"]
      TurnSelect [data-testid="chat-turn-select"]
    TraceStatus [data-testid="chat-turn-status"]
    TraceWrap
      TraceControls
      TraceScrub
      EventRow
  HistoryDialog [data-testid="chat-history-dialog"]
    HistorySearch
    HistoryFilter
    HistoryGroup
    HistoryRow
```

1440px 验收焦点：

- 对话阅读区、输入区、图片预览和 Skill token 同屏可读。
- 用户气泡右对齐，长文本可换行。
- 助手正文标题、正文、链接引用和列表层级清晰。
- 图片和文件材料卡 uploading/done/failed 不导致布局跳动。
- Skill token 长名称截断后仍可识别，并可查看摘要。
- Agent、模型、推理、发送、停止、错误提示、历史入口和轨迹入口同时存在时互不遮挡。
- 对话/轨迹 tabs 与连接状态位于同一 subbar，历史入口保留在顶栏右侧，不作为第三个 tab。
- 历史弹窗分组、搜索、筛选和行内动作可读，长标题不撑破弹窗。
- 轨迹页 trace toolbar、状态摘要、scrub 和 event row 层级清晰，事件详情不遮挡事件列表。

## UI 参考稿复刻合同

| 项 | 内容 |
|---|---|
| 保真模式 | 局部一致 / 风格迁移，不逐像素复刻整页。 |
| 业务语义保留 | MoonBox 共享导航、空间权限、会话历史、轨迹详情、Diff、OpenSpec 治理边界、深浅主题。 |
| 参考稿反向工程 | 顶栏、对话/轨迹 segmented tabs、subbar 状态区、历史弹窗搜索/筛选/分组/行内动作、轨迹 trace-wrap、右侧用户气泡、助手分节正文、链接式文件引用、状态摘要列表、下一步区、图片预览条、Skill token、输入区动作。 |
| Selector 映射 | `chat-conversation`、`chat-message-history`、`chat-message-attachments`、`chat-message-skills`、`chat-draft-branch`、`chat-attachment-strip`、`chat-image-attachment`、`chat-file-attachment`、`chat-rich-composer`、`chat-prompt`、`chat-skill-token`、`chat-execution-config-bar`、`chat-send-actions`、`chat-history-dialog`、`chat-history-trigger`、`chat-relations-bar`、`chat-execution-panel`、`chat-turn-select`、`chat-turn-status`。 |
| 动作按钮矩阵 | 选择分支、自动注入当前空间绑定仓库、添加文件、文件按钮右侧打开 Skill 菜单、`/keyword` 模糊搜索并选择 Skill、移除文件、重试文件、移除 Skill、发送、切换对话/轨迹、打开历史、历史搜索、历史筛选、历史置顶、历史重命名、历史归档/恢复、历史删除、选择执行轮次、停止；modal 类型分别为 select、implicit-binding、file-picker、popover、inline-combobox、inline-card、inline-card、inline-token、N/A、tabs、modal、input、select、inline-icon、modal、inline-icon、modal、select、confirm。 |
| Computed style 采样 | 1440px、1024px、390px；深浅主题；采样深色 Composer Dock、气泡、用户消息 Skill chip、消息附件预览、助手块、文件链接、图片卡、输入区 Skill token、发送区、segmented tabs、subbar 状态区、历史弹窗 action、轨迹 toolbar、scrub、event row。关键属性包括字体、字号、行高、padding、gap、border、background、color、z-index、overflow。 |
| 分批验收 | Skeleton、输入材料区、Skill 菜单、消息阅读层级、对话/轨迹 tabs、历史弹窗、轨迹视图、窄屏/主题、观测与权限。 |

## API、数据与对象存储边界

- 分支能力接口：仓库候选返回分支列表与默认分支，会话创建接收 `branch_name` 并在服务端校验。
- 文件能力接口：提供上传、删除/撤销、重试、能力限制查询、历史读取和权限校验。
- Skill 能力接口：提供当前仓库 `.agents/skills` Skill 候选、摘要读取、版本/mtime 或内容 hash、失效检测和发送前重验；Docker 部署必须把 `.agents` 只读投影到 `governance_root`。
- Chat 发送接口：接受文本、图片/文件引用列表、Skill 引用列表和幂等请求标识；后端构造本轮上下文快照。
- 数据库：保存会话分支、上传材料记录和轮次材料快照，包括图片/文件引用摘要、顺序、大小、类型、状态、Skill 名称、来源摘要、版本或 hash、注入范围和处理结果。
- 对象存储：保存图片或文件对象，历史展示只暴露授权后的摘要或代理入口，不在日志中暴露完整内部 key。

## 风险与取舍

| 风险 | 缓解 |
|---|---|
| 文件上传引入对象存储、DB 和 API 同步成本 | tasks 明确 OpenAPI、DB、对象存储、SQLite/MySQL 和接口测试，不允许只做前端预览。 |
| Skill 内容可能过长或包含敏感信息 | 服务端摘要/截断，并在历史中保存引用快照和注入范围，不保存完整敏感内容到日志。 |
| 截图参考被误当成新业务指令 | design 和 spec 明确 Image #1 只是视觉结构样例，不复制其中命令文本、耗时、路径或执行结果。 |
| Sprint 容量缓冲不足 | `sprint-006` 当前容量占用约 85%，后续 apply 需避免无说明拆分核心验收；若拆分必须回填 Sprint/Change 文档。 |
| UI 视觉验收证据不足 | tasks 将 UI Skeleton、1440px、窄屏、深浅主题、关键交互截图和 computed style 作为先行/完成门禁。 |

## 迁移计划

1. 先补 UI Skeleton 与数据/接口边界，确保 Chat 工作台现有文本发送不回退。
2. 增加图片/文件上传和 Skill 候选读取的后端能力与测试。
3. 接入 Composer 和消息历史回显，覆盖失败恢复和幂等。
4. 接入观测链路并验证脱敏。
5. 完成视觉证据、computed style、Mock/API 边界和 REQ 最终一致性回填。

回滚策略：可通过前端能力开关或服务端能力限制关闭图片/Skill 新入口，保留既有文本 Chat 工作台；已登记图片和 Skill 引用保留历史只读追溯。

## 待确认问题

- 图片限制的最终数值需要实现阶段结合服务端能力和对象存储配置确定。
- 仅图片输入默认允许，但执行端不支持图片时必须阻止发送或提示降级；最终策略需由实现验收确认。
- Skill 来源首版优先当前仓库 `.agents/skills/` 元数据或服务端索引；跨仓库和个人 Skill 不在本 Change 范围。
