---
title: Chat 工作台多材料与 Skill 快速引用规格增量
created_at: 2026-09-14 23:41:49
updated_at: 2026-09-20 14:45:39
owner: product
---

# Chat 工作台多材料与 Skill 快速引用规格增量

## ADDED Requirements

### Requirement: 分支、图片与文件输入执行上下文

系统 SHALL 在 Chat 工作台会话创建前支持分支选择，候选来自当前 Git 仓库，默认优先 `main`，无 `main` 时优先 `master`，会话创建后该分支随会话锁定。系统 SHALL 在输入区支持图片和文件作为本轮上下文材料，并在发送前完成上传、预览或摘要展示、状态展示、权限校验和容量校验。系统 SHALL 保存本轮材料引用快照，包括顺序、类型、大小、上传状态、脱敏摘要和处理结果；历史轮次 SHALL 能追溯这些摘要，但不得在通用日志、请求日志、Task Trace metadata 或错误信息中保存完整图片内容、文件正文、完整 Prompt、完整回复、完整 Diff、密钥、Cookie、Authorization header、本机绝对路径、对象存储内部完整 key 或真实客户敏感数据。

#### Scenario: 会话创建前选择分支

- **WHEN** 用户在 Chat 工作台创建新会话
- **THEN** 系统展示当前仓库分支候选并默认选中 `main` 或 `master`
- **AND** 创建后的会话使用该分支作为执行上下文，历史会话不再显示可编辑分支选择

#### Scenario: 图文混合发送

- **WHEN** 用户在 Chat 工作台输入文字并添加多张有效图片后发送
- **THEN** 系统保存图片引用快照并将其纳入本轮执行上下文
- **AND** 页面展示图片数量、顺序、类型、大小和脱敏摘要

#### Scenario: 文件材料发送

- **WHEN** 用户通过文件按钮、多选或剪贴板粘贴添加图片或受支持文件后发送
- **THEN** 系统先经后端上传并返回 opaque `ref_id`
- **AND** 发送时服务端重验材料所有者、空间、仓库、状态和类型后纳入本轮执行上下文

#### Scenario: 图片失败恢复

- **WHEN** 图片格式不支持、体积超限、上传失败、服务端不可读或执行端不支持图片
- **THEN** 系统阻止发送或标记该图片不可用并展示可恢复提示
- **AND** 保留文字草稿、其他已成功图片和已选 Skill 引用

#### Scenario: 仅材料输入策略

- **WHEN** 用户只添加图片或文件且没有输入文字
- **THEN** 系统按服务端策略允许发送并提示材料会作为本轮上下文，或禁用发送并说明必须补充文字

### Requirement: 仓库 Skill 快速引用

系统 SHALL 在 Chat 工作台输入区提供当前仓库 Skill 快速引用入口，候选来源为用户有权访问的当前会话绑定仓库 `.agents/skills` 元数据或服务端索引。Skill 按钮 SHALL 位于文件上传按钮右侧；输入 `/`、`/keyword` 或点击 Skill 按钮 SHALL 打开同一候选列表，`/keyword` SHALL 按 Skill id、英文名和中文描述模糊过滤。候选项 SHALL 以无单项边框的列表行展示 Skill 英文名与中文描述，不得把 YAML frontmatter 分隔符当作说明。选中的 Skill SHALL 从图片/文件附件材料条中分离，并作为 rich composer 用户消息内容流内的 inline chip 展示图标与英文名、允许通过移除按钮、`Delete` 或 `Backspace` 删除，文本 SHALL 从 chip 后继续输入并自然换行；发送时 Skill 只作为本轮上下文材料或约束提示，不得自动执行 `/req-*`、`/bug-*`、`/opsx-*`、`/sprint-*` 或其他写入型命令。

#### Scenario: 选择 Skill 引用

- **WHEN** 用户打开 Skill 候选并选择一个有权访问的 Skill
- **THEN** 输入区在 rich composer 用户消息内容流内展示仅包含图标和 Skill 英文名的 inline chip
- **AND** 图片或文件附件材料条不承载 Skill token
- **AND** 用户文本从 Skill chip 后继续输入并按同一文本流自然换行
- **AND** 用户可通过 chip 移除按钮、chip 聚焦后的 `Delete` / `Backspace` 或文本开头处的 `Delete` / `Backspace` 移除 Skill
- **AND** 发送时系统保存 Skill 名称、版本或内容摘要、来源摘要和实际注入范围

#### Scenario: Skill 候选模糊搜索

- **WHEN** 用户在输入框输入 `/bug`
- **THEN** 系统展示匹配 `bug` 的 Skill 候选
- **AND** 候选行展示 Skill 英文名与中文描述且不显示 `---`

#### Scenario: 部署投影读取仓库 Skill

- **WHEN** 后端在 Docker 治理根目录下读取 Skill 候选
- **THEN** `.agents/skills` 目录以只读方式投影到治理根目录
- **AND** 仓库存在 `SKILL.md` 时系统不得返回空候选误导用户

#### Scenario: Skill 候选不可用

- **WHEN** 仓库未绑定、用户无权限、Skill 元数据缺失或候选读取失败
- **THEN** 系统展示明确空态或脱敏错误摘要
- **AND** 不暴露内部绝对路径、凭证、宿主机配置或完整 Skill 敏感内容

#### Scenario: Skill 不自动执行命令

- **WHEN** 用户引用的 Skill 描述了写入型命令或治理流程
- **THEN** 系统仅将其作为本轮上下文材料或约束提示
- **AND** 不自动创建 REQ、BUG、Sprint、OpenSpec Change 或代码修改

### Requirement: Chat Composer 多材料状态与幂等

系统 SHALL 将文字、图片/文件引用、Skill 引用和发送请求标识绑定为同一轮上下文快照。重复点击、网络重发或响应丢失时，系统 SHALL 复用同一会话与轮次，不重复创建会话或重复提交同一批材料与 Skill 引用。会话归档、运行中、停止中、状态未知、服务未就绪、仓库缺失或权限撤销时，分支、文件上传和 Skill 控件 SHALL 遵循既有 Chat 工作台输入门禁。

#### Scenario: 重复发送同一批材料

- **WHEN** 用户重复点击发送或客户端重试同一请求标识
- **THEN** 系统复用同一会话与轮次
- **AND** 不重复提交相同文件、图片和 Skill 引用

#### Scenario: 权限撤销后发送

- **WHEN** 用户发送前会话、空间、仓库、文件对象、图片对象或 Skill 权限被撤销
- **THEN** 系统拒绝继续使用旧引用并说明原因
- **AND** 不泄漏无权访问的文件、图片、Skill 或会话内容

### Requirement: Codex 截图基线的对话阅读体验

系统 SHALL 基于用户提供的 Codex 截图与 HTML 参考稿进行局部一致 / 风格迁移，优化 Chat 工作台对话阅读层级、对话/轨迹切换、历史弹窗和轨迹阅读层级。页面 SHALL 保留 MoonBox Ops 视觉系统、共享导航、空间权限、会话历史、轨迹详情、Diff 和治理边界。截图或 HTML 中的具体历史命令、耗时、文件路径、账号信息和执行结果 SHALL 只作为视觉结构样例，不得复制为产品事实。

#### Scenario: 对话阅读层级

- **WHEN** 用户查看包含文本、图片、文件和 Skill 引用的对话轮次
- **THEN** 用户消息右对齐并可换行，图片或文件缩略图显示在用户消息泡上方，并支持点击打开材料预览；历史材料缺少 `preview_url` 但仍有授权 `ref_id` 时，系统 SHALL 通过受控材料内容读取接口生成可预览地址，不得伪造不存在的图片地址
- **AND** 图片缩略图和预览弹窗 SHALL 通过带当前登录态 Authorization 的前端 fetch 读取受控材料内容，并使用 object URL 渲染真实图片；不得让原生 `<img>` 直接请求需要 Bearer 鉴权的材料接口；切换材料、关闭弹窗或组件卸载时 SHALL 释放 object URL
- **AND** Skill 引用以轻量 chip 融入用户消息泡内容流，chip 仅展示统一 Skill 图标和 Skill 英文名，不展示尾部 `skill` 文案、内部注入范围说明、`Skill 引用：xxx`、`图片引用：xxx` 或 `文件引用：xxx` 派生说明
- **AND** 用户消息首段正文 SHALL 与 Skill chip 位于同一 inline 内容流，文本从 Skill chip 后继续排版并自然换行；第二段及复杂 Markdown 内容 SHALL 保持块级阅读层级
- **AND** 用户消息 meta 显示在消息泡下方，模型信息与时间位于同一行且模型信息在最前，复制为图标按钮，不展示查看本轮轨迹入口
- **AND** 用户消息 meta、AI tool-summary 和 Composer 配置控件 SHALL 使用统一执行配置展示名：`Codex`、`GPT-6 Astra`、`GPT-5.6 Sol`、`GPT-5.6 Terra`、`GPT-5.6 Luna`、`GPT-5.5`、`XHigh`、`High`、`Medium`、`Low`；模型下拉 SHALL 按 `GPT-6 Astra`、`GPT-5.6 Sol`、`GPT-5.6 Terra`、`GPT-5.6 Luna`、`GPT-5.5` 顺序展示；API payload、DB 字段和执行配置快照 SHALL 继续保存原始 value
- **AND** 助手消息以 avatar、assistant 列、tool-summary、正文气泡和左对齐 meta 呈现，并以分节标题、段落、链接式引用、摘要列表、下一步和待处理区展示
- **AND** tool-summary SHALL 位于 assistant 列第一行，与 AI 图标同组，使用带边框摘要样式；当 assistant 正文尚未产生时，运行状态仍可在用户消息下方展示
- **AND** Composer Skill 按钮、输入区 inline chip、Skill 候选列表、用户消息 Skill chip 和 AI meta Skill 图标 SHALL 使用同一 Skill 图标
- **AND** Composer 中 Skill、模型和推理三类下拉面板 SHALL 使用统一 popover 基础样式、字号密度、hover、active、disabled 状态和外部点击或 Escape 关闭逻辑；三类面板打开后，点击当前面板外和对应触发按钮外的任意空白区域 SHALL 自动隐藏，包括输入框空白、Composer 工具栏空白和页面空白；三类面板 SHALL 在切换触发器时互斥展示；Skill SHALL 保留搜索与键盘上下/Enter 选择，模型和推理 SHALL 保留单选语义
- **AND** 助手正文不重复展示 Skill pill，使用统一 Skill 图标 hover 展示本轮 Skill；复制为图标按钮，底部 meta 不重复展示查看本轮轨迹入口
- **AND** 助手正文不重复展示用户上传图片或文件附件；材料上下文仅保留在本轮 payload、trace 或用户消息材料区
- **AND** 助手正文中的关键结论、风险/阻塞、动作结果和下一步等重点内容 SHALL 基于句子语义特征使用受控样式差异化强调，并限制为每条消息最多 1-2 个高优先级短片段，不允许通过固定单一文案表、整句大面积高亮或原始 HTML 注入实现
- **AND** 助手 meta 只展示当前事件或 API 已采集的耗时与 Token 字段，不伪造首 token 或分项 Token
- **AND** 用户消息和助手消息复制按钮 SHALL 优先使用浏览器剪贴板 API，失败或不可用时回退到 textarea + `execCommand`；成功和失败都提供短暂且可访问的状态反馈
- **AND** 复制按钮在复制成功后 SHALL 短暂切换为已复制图标，复制失败后 SHALL 短暂切换为失败图标，数秒后恢复复制图标

#### Scenario: AI 运行状态块对齐

- **WHEN** 会话轮次处于连接中、排队中、执行中、停止中、失败或等待结果状态
- **THEN** AI 运行状态块外层轨道与 Composer 输入框使用同一内容宽度和左边缘对齐
- **AND** 状态块内部正文保持可读宽度，窄屏下不产生横向溢出
- **AND** 运行状态摘要以 tool-summary 风格展示状态点、工具调用数量、轮次状态、执行配置摘要和查看本轮轨迹入口
- **AND** 保留失败提示和运行中状态文案

#### Scenario: 会话创建前输入 Dock

- **WHEN** 用户在未创建会话状态下输入消息、选择 Skill 或添加附件
- **THEN** 输入区以深色 Dock 形态展示，并只暴露分支选择
- **AND** 输入本体以及输入区与工具栏之间不显示分隔线，输入文字使用 13px / 1.6 的阅读密度
- **AND** 用户输入 `/` 或 `/keyword` 打开 Skill 菜单时，默认选中第一条可用候选；上下键移动选中项，Enter 将选中 Skill 填入输入框，Escape 关闭菜单且不影响普通 Enter 发送语义
- **AND** 由 `/` 或 `/keyword` 触发的 Skill 菜单 SHALL 在用户删除触发查询后自动关闭；由 Skill 按钮打开的菜单不因普通文本输入误关闭
- **AND** Skill 候选列表字号和密度 SHALL 与 Chat 13px 输入体系一致，主标题约 13px，摘要约 11.5-12px，行高和间距保持紧凑可读
- **AND** 系统从当前空间绑定仓库自动注入会话创建、材料上传和 Skill 候选读取所需仓库
- **AND** 页面不得把仓库或项目展示为用户可编辑选择项

#### Scenario: 对话与轨迹切换

- **WHEN** 用户查看 Chat 工作台顶栏下方的视图切换
- **THEN** 系统以 segmented tabs 展示「对话」和「轨迹」
- **AND** 同一 subbar 展示空间连接状态、主对象摘要和管理关联入口
- **AND** 顶栏「历史」保持独立动作入口，不作为第三个视图 tab

#### Scenario: 历史弹窗

- **WHEN** 用户打开会话历史
- **THEN** 系统展示搜索、状态筛选、置顶/最近/更早分组列表和行内图标动作
- **AND** 行内动作默认弱化，hover 或 focus 时清晰展示，删除动作保持危险态
- **AND** 保留会话切换、置顶、重命名、归档或恢复、删除权限和活动轮次禁用语义

#### Scenario: 轨迹阅读层级

- **WHEN** 用户打开轨迹视图
- **THEN** 系统展示运行状态、停止按钮、执行轮次选择、当前状态摘要、搜索、scrub 概览和事件行列表
- **AND** 保留事件详情、原始事件、引用快照、Diff、停止和重试语义
- **AND** 文件变更区区分执行快照与当前本地工作区状态；新增但当前 Git 未跟踪的文件显示“新增（未跟踪）”，快照内容与当前磁盘内容不一致时展示明确提示

#### Scenario: 窄屏阅读

- **WHEN** 用户在窄屏查看对话、文件材料、Skill token、历史弹窗、轨迹事件和状态摘要
- **THEN** 文本、文件链接、材料卡和 Skill token 不产生页面横向溢出
- **AND** 发送、停止、错误提示和轨迹入口互不遮挡

### Requirement: 多材料观测与脱敏

系统 SHALL 为图片或文件添加/移除、Skill 选择/移除、发送结果、材料校验、对象存储写入、Skill 解析、上下文构造、执行提交和结果处理记录脱敏观测摘要。行为事件、请求日志、Task Trace 和流程节点写入失败 SHALL 不阻断主流程，但系统 SHALL 保留脱敏降级摘要以便排障。

#### Scenario: 观测 metadata 脱敏

- **WHEN** 系统记录图片、文件或 Skill 相关行为事件、请求日志、Task Trace 或流程节点
- **THEN** metadata 只包含事件名、结果、数量、大小、类型、错误码、耗时和脱敏摘要
- **AND** 不包含完整图片、文件正文、完整请求体、完整 Prompt、完整回复、Authorization、Cookie、Token、密钥、本机绝对路径、对象存储内部完整 key 或真实客户敏感数据

#### Scenario: Task Trace 节点覆盖

- **WHEN** 一轮包含图片、文件或 Skill 引用的 Chat 执行被提交
- **THEN** Task Trace 或等价流程节点覆盖材料校验、对象存储写入、Skill 解析、上下文构造、执行提交和结果处理

### Requirement: 原型驱动 UI 合同与验收证据

系统 SHALL 在实现多图片与 Skill 引用前完成 UI Contract、UI Skeleton 和 UI Reference Replication Contract。实现完成前 SHALL 提供 1440px 桌面视口、窄屏、深浅主题、关键交互截图或等价证据，并记录关键 computed style、Mock/API 边界和 linked REQ 最终一致性。

#### Scenario: UI Skeleton 先行

- **WHEN** Change 开始实现 Chat 输入区、消息区、对话/轨迹切换、历史弹窗或轨迹入口 UI
- **THEN** 先完成页面壳、布局区域、组件层级、状态容器、可测选择器和 1440px 验收焦点
- **AND** 未完成 Skeleton 证据前不得关闭细节实现任务

#### Scenario: 参考稿复刻验收

- **WHEN** UI 任务准备验收
- **THEN** 提供 selector 映射、动作按钮矩阵、computed style 采样和分批截图或等价 DOM/组件证据
- **AND** 归档前确认 linked REQ 与最终 Change 设计、截图、Mock/API 边界和实现证据一致
