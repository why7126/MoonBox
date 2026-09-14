# web-catalog-requirement-center-real-data Specification

## Purpose
定义前台需求中心基于授权空间与仓库聚合真实治理事实源、展示 REQ/BUG/Change 卡片、读取关联文档、处理阶段动作、保持稳定刷新和执行权限校验的能力边界。
## Requirements
### Requirement: 需求中心上下文聚合

系统 SHALL 基于服务端授权的 space_id 与 repository_id 提供前台需求中心上下文聚合接口，返回当前用户、可访问空间、当前空间、权限态、统计、筛选选项、治理对象列表、卡片文档入口、动作映射和进度摘要。

#### Scenario: 首屏获取真实上下文

- **WHEN** 用户进入 `/requirements` 且请求需求中心上下文接口
- **THEN** 系统返回可驱动页面首屏的用户、空间、权限、统计、筛选和治理对象数据
- **AND** 每个治理对象必须包含可展示的文档入口摘要
- **AND** 每个治理对象必须包含当前阶段允许动作及禁用原因
- **AND** 待开发、研发中、验收中或已完成对象可以包含可展示的任务进度摘要
- **AND** 采集池、规划中、待评审和已评审对象即使历史字段中存在任务进度，前端也不得展示为研发进度入口

#### Scenario: 未登录访问需求中心

- **WHEN** 未登录用户进入 `/requirements`
- **THEN** 系统先展示登录页，不渲染需求中心看板或发起需求中心上下文请求

#### Scenario: 接口使用统一响应结构

- **WHEN** 前端调用 `/api/v1/requirement-center/context`
- **THEN** 请求必须携带有效 Bearer 会话，响应使用项目统一 API 响应结构和受控错误码

### Requirement: 治理文件事实源聚合

系统 SHALL 从当前授权项目的治理文档、REQ/BUG registry、Issue trace、Sprint 四件套和 OpenSpec Change 元信息聚合首版真实数据。

#### Scenario: 聚合 REQ 与 BUG registry

- **WHEN** 后端构建需求中心治理对象列表
- **THEN** 系统读取 `issues/requirements/_registry.yaml` 与 `issues/bugs/_registry.yaml` 的白名单字段

#### Scenario: trace 优先于 registry

- **WHEN** Issue `trace.md` 与 registry 摘要状态不一致
- **THEN** 系统以 `trace.md` 为优先事实源，并返回对象级漂移提示

#### Scenario: Docker 环境读取治理事实源

- **WHEN** 后端运行在 Docker Compose 中
- **THEN** 系统通过已授权项目绑定解析治理目录，以只读方式聚合 `issues/`、`iterations/`、`openspec/`、`docs/` 和 `rules/`，不得依赖容器源码或无作用域全局目录
- **AND** 受控文档写入与治理成果应用由可信写入通道统一协调，普通聚合接口不获取任意主机写权限

#### Scenario: 完整仓库归档事实

- **WHEN** registry 中的 Issue 已完成且关联 Change 或 Sprint 已迁入归档目录
- **THEN** 聚合保留 Issue 已完成阶段并读取归档事实，不因活动目录缺项回退为待开发
- **AND** 已完成事项的历史漂移作为诊断信息，不计入当前阻塞
- **AND** 对象计数仅覆盖 registry 注册项，不自动纳入未注册基础建设目录

#### Scenario: 验收文档与卡片展示分离

- **WHEN** applied Change 的卡片展示精简 Change 文档入口
- **THEN** 系统将对象映射验收中，使用真实 Issue 文档检查 acceptance.md 存在性与非空内容
- **AND** 卡片未显示该文件不等于文档缺失

### Requirement: 9 阶段状态映射

系统 SHALL 将 REQ、BUG、Sprint 和 OpenSpec Change 状态映射到采集池、规划中、待评审、已评审、迭代规划、待开发、研发中、验收中、已完成 9 个阶段。

#### Scenario: 已纳入 Sprint 但未创建 Change

- **WHEN** REQ 或 BUG 状态为 `in_sprint` 且没有关联 OpenSpec Change
- **THEN** 系统将该对象映射到“迭代规划”阶段

#### Scenario: Change 已创建但未 apply

- **WHEN** REQ 或 BUG 已关联 OpenSpec Change 且 Change 尚未完成 apply
- **THEN** 系统依据统一执行事实源将未启动对象映射到“待开发”、已启动对象映射到“研发中”，并独立返回真实任务进度摘要

#### Scenario: 已闭环对象

- **WHEN** REQ 或 BUG 状态为 `done` 或关联 Change 已归档
- **THEN** 系统将该对象映射到“已完成”阶段

#### Scenario: approved 展示为已评审

- **WHEN** REQ 或 BUG 的底层状态为 `approved`
- **THEN** 前端展示阶段必须为“已评审”
- **AND** API 可以保留 `approved` 作为机器状态，但必须提供可展示中文阶段或等价映射

#### Scenario: 已启动零完成任务

- **WHEN** Change已记录启动事实且完成数为0/N
- **THEN** 系统 MUST 返回研发中阶段与真实零进度，并提供查看进度动作

#### Scenario: 执行状态刷新一致

- **WHEN** 启动、进度或完成事实变化并成功刷新context
- **THEN** 系统 MUST 返回与治理事实源一致的阶段、动作、任务数及更新后的快照标识
- **AND** 轮询、焦点刷新及手动刷新 MUST 不依赖仅存在于前端的模拟状态，项目切换后不能串卡

#### Scenario: 完成门禁后进入验收

- **WHEN** 新契约Change通过完成门禁并记录完成事实
- **THEN** 系统 MUST 映射为验收中；仅全勾选但无完成事实时保持研发中

### Requirement: 字段白名单与安全脱敏

系统 SHALL 对治理文件读取结果执行字段白名单映射和错误脱敏，不得向浏览器暴露本机路径、密钥、token、`.env` 内容、原始日志、Markdown 全文中不应公开的内容或异常堆栈。

#### Scenario: API 响应不包含敏感字段

- **WHEN** 后端从治理文件聚合需求中心数据
- **THEN** API 响应只包含设计文档声明的白名单字段
- **AND** 文档入口只包含受控文件名、类型、打开方式、预览 URL 或禁用原因
- **AND** API 响应不得包含本机绝对路径、内部目录结构、原始异常堆栈、密钥、token 或 `.env` 内容

#### Scenario: 解析失败错误脱敏

- **WHEN** 某个治理文件读取或解析失败
- **THEN** 系统返回受控错误或对象级阻塞提示，且不包含本机绝对路径、堆栈或原始文件内容

#### Scenario: 文档预览失败脱敏

- **WHEN** Markdown 读取、HTML 预览或 tasks 进度解析失败
- **THEN** 系统返回可展示的脱敏失败原因
- **AND** 系统不得把内部文件路径、原始堆栈或未脱敏文件内容返回给浏览器

### Requirement: 真实统计、筛选和搜索

系统 SHALL 基于真实治理对象支持统计、对象类型筛选、负责人筛选、优先级筛选、Sprint 筛选和关键词搜索。

#### Scenario: 统计与筛选一致

- **WHEN** 用户调整筛选条件
- **THEN** 统计区和看板卡片范围基于同一过滤结果刷新

#### Scenario: 搜索覆盖关键字段

- **WHEN** 用户输入 ID、标题、阶段产物、负责人或来源关键词
- **THEN** 看板只展示匹配的治理对象，并保留 9 阶段列

#### Scenario: 独立类型与关联搜索去重
- **WHEN** 用户选择独立 Change 类型或搜索关联 Change ID
- **THEN** 系统 SHALL 只计数独立 Change 卡片，关联 ID 搜索返回所属 Issue 卡片
- **AND** 同筛选下总数等于需求、缺陷、独立卡片数量之和，页面九阶段卡片数量等于页面总数；unknown只计入单列的数据异常数量，接口原始统计不变
- **AND** 未授权对象不参与卡片、搜索提示、统计或异常详情

### Requirement: 空间上下文与权限态

系统 SHALL 基于后台空间管理事实源和真实用户空间成员关系控制可访问空间、当前空间、空间只读状态和高权限入口展示。

#### Scenario: 前台空间列表来自后台空间事实源

- **WHEN** 已登录用户请求 `/api/v1/requirement-center/context`
- **THEN** 系统必须从后台空间、成员和产品绑定事实源返回当前用户已加入空间
- **AND** 系统不得以 `project.yaml` 派生空间冒充生产真实空间列表
- **AND** 响应空间字段必须足够驱动前台空间切换浮层展示空间名称、角色、成员数、状态和当前项

#### Scenario: 仅展示已加入空间

- **WHEN** 后端构建当前用户可访问空间列表
- **THEN** 系统必须仅包含当前用户作为负责人或成员加入的空间
- **AND** 未加入空间、无权限空间和回收中空间不得出现在前台空间切换列表中

#### Scenario: 冻结空间可只读切换

- **WHEN** 当前用户已加入某个冻结空间
- **THEN** 系统必须在可访问空间列表中返回该空间
- **AND** 响应必须包含冻结或只读语义
- **AND** 前端必须允许用户切换查看该空间
- **AND** 前端必须显示“已冻结”或“只读”等可理解标记

#### Scenario: 本地空间不可访问

- **WHEN** 本地保存的 workspaceId 不在用户可访问空间中
- **THEN** 系统必须回退到默认可访问空间或首个可访问空间
- **AND** 前端必须更新或清理本地选择
- **AND** 前端不得短暂展示不可访问空间名称

#### Scenario: 用户无已加入空间

- **WHEN** 当前用户没有任何已加入空间
- **THEN** 前端必须展示无已加入空间空态
- **AND** 前端可以展示“创建或加入空间”入口
- **AND** 在 REQ-0019 完成前，系统不得伪造可切换空间

#### Scenario: 用户无后台权限

- **WHEN** `can_access_admin` 为 false
- **THEN** 前端不展示“进入后台”入口

#### Scenario: 用户无空间管理权限

- **WHEN** `can_manage_workspace` 为 false
- **THEN** 前端隐藏或禁用“设置空间”入口，并展示可理解原因

### Requirement: 页面加载态、错误态和空态

系统 SHALL 在真实数据请求和异常场景中展示加载态、错误态、空空间态、筛选无结果态和无权限态，并提供适合当前区域的恢复操作。

#### Scenario: 请求期间不闪现 Mock 数据
- **WHEN** 需求中心上下文请求尚未完成
- **THEN** 页面展示加载态，且不展示Mock卡片、空间或用户

#### Scenario: 首次失败可重试
- **WHEN** 首次上下文读取失败
- **THEN** 看板区域显示简洁错误态、重新加载和查看详情，保留导航和项目切换，不自动弹窗

#### Scenario: 同项目刷新失败
- **WHEN** 已有成功结果且同项目刷新失败、权限仍有效
- **THEN** 保留旧结果并标注更新失败及最后同步时间，暂停依赖最新状态的写入并保留草稿

#### Scenario: 权限失效或项目切换
- **WHEN** 会话/对象权限失效或切换项目
- **THEN** 不保留无权或其他项目内容，迟到请求不能覆盖当前状态

#### Scenario: MD抽屉失败
- **WHEN** 文档读取失败
- **THEN** 抽屉内显示错误及重试/详情，保留关闭，不误显示另一份正文，不无限loading

#### Scenario: 主动详情与关闭
- **WHEN** 用户点击查看详情
- **THEN** 打开共用弹窗显示脱敏原因、建议和可用错误标识；支持关闭、Esc和遮罩，焦点进入并限制于弹窗，关闭恢复焦点，嵌套场景只关闭最上层

#### Scenario: 重复失败与错误分类
- **WHEN** 重试或轮询重复失败
- **THEN** 不重复弹窗或抢占焦点，请求去重；仅明确分类时展示解析错误，不将通用2603推断为永久格式错误

#### Scenario: 筛选无结果保留9阶段
- **WHEN** 筛选条件没有匹配治理对象
- **THEN** 展示筛选无结果态并保留全部9个阶段列

### Requirement: Mock 数据生产路径移除

系统 SHALL 移除需求中心生产运行时对 `initialIssues`、`workspaces` 和 `currentUser` 静态数据的依赖。

#### Scenario: 生产运行时使用 API 数据

- **WHEN** 前端在生产运行时渲染需求中心
- **THEN** 用户、空间、权限、统计和卡片数据均来自需求中心数据客户端或 hook

#### Scenario: 测试 fixture 不进入生产数据路径

- **WHEN** 前端测试需要构造需求中心数据
- **THEN** fixture 只存在于测试文件或测试 helper，不作为生产运行时 fallback

### Requirement: 原型驱动真实数据 UI 验收

系统 SHALL 按 prototype-driven UI Gate 验收真实数据首屏、加载态、错误态、空态、筛选无结果态、权限差异态和空间切换刷新状态。

#### Scenario: UI Skeleton 先于细节实现

- **WHEN** 开始实现真实数据接入
- **THEN** Change tasks 先完成 UI Skeleton 与状态容器，再进行接口接入和细节实现

#### Scenario: 1440px 视觉验收

- **WHEN** 真实数据接入实现完成
- **THEN** 系统记录 1440px 桌面视口验收证据，覆盖真实数据首屏和关键状态

### Requirement: 治理对象列表

系统 SHALL 为需求中心返回能支撑卡片文档查看、动作流转、AI 聊天反馈和任务进度展示的治理对象字段。

#### Scenario: 治理对象包含文档入口

- **WHEN** 后端返回 Requirement 或 Bug 卡片数据
- **THEN** 每个关联文档必须包含文件名、文档类型、打开方式、可访问 URL 或禁用原因
- **AND** 前端卡片必须按当前阶段可展示文档白名单渲染这些入口；采集池阶段只展示 `capture.md` 与 `trace.md`
- **AND** Markdown 文件打开方式必须可映射到右侧抽屉
- **AND** HTML 文件打开方式必须可映射到新 Tab 预览

#### Scenario: 治理对象包含动作映射

- **WHEN** 后端返回 Requirement 或 Bug 卡片数据
- **THEN** 每个对象必须包含当前阶段主动作的产品化文案、命令映射、是否需要选择弹窗、禁用状态和禁用原因
- **AND** 命令映射必须使用完整 REQ 或 BUG ID

#### Scenario: 治理对象包含任务进度

- **WHEN** 对象关联 OpenSpec Change 且存在 `tasks.md`
- **THEN** 系统必须返回任务总数、已完成数量、是否只读、是否可验收和阻塞提示
- **AND** `tasks.md` 缺失或解析失败时必须返回脱敏错误摘要，而不是误报完成

#### Scenario: 返回独立与关联 Change 身份
- **WHEN** 授权项目快照含无 Issue 来源的 Change 或 Issue 已关联 Change
- **THEN** 系统 SHALL 为独立 Change 返回 type=change 的自身身份、只读文档、状态及进度，且不伪造 Issue；阶段动作使用真实能力元数据，依据实际文档和权限给出禁用原因，不按独立Change类型固定禁用，文档仍只读
- **AND** Issue 卡片保留原 id，返回受控关联摘要及可空当前 Change，含糊时不任意选取末项或首项
- **AND** 卡片 ID、中文标题、文档和进度必须指向同一当前 Change；无分级的独立对象不得伪造默认优先级

### Requirement: 文档能力对象接口

系统 SHALL 在需求中心文档列表和文档读取相关响应中返回每个文档的结构化能力对象，并在过渡期将旧 `editable` 字段作为 `human_editable` 的兼容别名。

#### Scenario: 文档列表返回能力对象

- **WHEN** 前端请求需求中心对象的文档列表
- **THEN** 每个文档响应项 SHALL 包含 `readable`、`human_editable`、`ai_mutable`、`task_toggle_only` 和 `reason`
- **AND** `reason` SHALL 使用可展示的脱敏业务原因

#### Scenario: editable 兼容 human_editable

- **WHEN** 响应仍包含旧字段 `editable`
- **THEN** `editable` SHALL 与 `human_editable` 等值
- **AND** 新增后端和前端逻辑 SHALL 以能力对象为准

#### Scenario: trace 系统可变更但人工只读

- **WHEN** 文档名为 `trace.md`
- **THEN** `human_editable` SHALL 为 false
- **AND** `task_toggle_only` SHALL 为 false
- **AND** `ai_mutable` MAY 为 true 以表达 Workflow Sync、AI 命令和治理脚本可按门禁写入

### Requirement: 文档保存授权校验

系统 SHALL 在人工保存 Markdown 文档或提交 task toggle 时复用后端文档能力计算结果进行最终授权，不得信任前端传入的可编辑状态。

#### Scenario: 完整 Markdown 保存需要 human_editable

- **WHEN** 用户提交完整 Markdown 保存请求
- **THEN** 后端 SHALL 重新计算文档能力
- **AND** 仅当 `human_editable=true` 时保存
- **AND** 否则返回 403 或等价受限错误

#### Scenario: task toggle 保存需要 task_toggle_only

- **WHEN** 用户提交 task toggle 保存请求
- **THEN** 后端 SHALL 重新计算文档能力
- **AND** 仅当 `task_toggle_only=true` 时进入差异校验
- **AND** 否则返回 403 或等价受限错误

#### Scenario: 验收中 tasks 只允许 checkbox 差异

- **WHEN** 后端处理 `tasks.md` checkbox-only 保存
- **THEN** 后端 SHALL 比较原文与提交内容
- **AND** 仅允许 Markdown task list marker 在 `- [ ]` 与 `- [x]` 之间切换
- **AND** 对标题、任务描述、非任务行、验收记录或其他文本变化 SHALL 拒绝保存

#### Scenario: 已生效规格人工只读

- **WHEN** 用户尝试保存 `openspec/specs/**/spec.md`
- **THEN** 后端 SHALL 拒绝人工全文保存
- **AND** 错误原因 SHALL 说明已生效规格只能通过 OpenSpec Change 和 archive 合并流程修改

### Requirement: 文档操作安全与观测

系统 SHALL 对人工文档操作、task toggle、越权拒绝和系统治理写入记录脱敏摘要，并避免在 API 响应或观测 metadata 中泄漏敏感内容。

#### Scenario: 人工文档操作进入请求日志

- **WHEN** 用户打开只读文档、保存完整 Markdown、提交 task toggle 或触发越权拒绝
- **THEN** 系统 SHALL 在请求日志中记录对象 ID、文档名、操作类型、结果、错误码和脱敏原因
- **AND** 请求日志 SHALL NOT 保存完整 Markdown 内容、完整请求体、完整响应体、Authorization、Cookie、密钥、本机路径或内部堆栈

#### Scenario: 行为事件使用稳定事件名

- **WHEN** 前端记录文档打开、全文保存、checkbox-only 保存或保存失败事件
- **THEN** 行为事件 SHALL 使用稳定事件名
- **AND** 事件属性 SHALL 仅包含对象 ID、文档名、能力类型、结果和脱敏错误码

#### Scenario: Task Trace 覆盖或说明豁免

- **WHEN** task toggle 差异校验被实现为多步骤或高风险写操作
- **THEN** 系统 SHALL 接入 Task Trace 或记录不接入的具体原因
- **AND** Task Trace metadata SHALL NOT 保存完整 Markdown 内容或完整 Prompt

#### Scenario: 系统治理写入不受 UI 只读阻断

- **WHEN** Workflow Sync、AI 命令或治理脚本按既有门禁更新 `trace.md`、`tasks.md` 或其他治理文档
- **THEN** 系统 SHALL 允许该系统写入路径继续执行
- **AND** UI 只读状态 SHALL NOT 被用作禁止系统治理写入的依据

### Requirement: 独立 Change 关系与授权解析
系统 SHALL 在完整稳定项目快照中识别结构化关系后再过滤权限，文档直接API与卡片遵循同一授权。

#### Scenario: 关联对象受限或来源缺失
- **WHEN** Change 的关联 Issue 不可见、缺失或来源冲突
- **THEN** 系统 SHALL 不把该 Change 重新认作独立，保留受控异常且不泄漏隐藏身份

#### Scenario: 独立对象授权
- **WHEN** 用户读取独立 Change 或直接请求文档
- **THEN** 系统 SHALL 校验空间、项目、Change完整ID对象权限和路径白名单，拒绝跨项目及符号链接越界，新增入口只读

### Requirement: Change 版本和状态证据
系统 SHALL 精确识别活动与归档完整ID，不以任务完成推断验收或归档。

#### Scenario: 活动与归档冲突
- **WHEN** 活动和归档同ID，或存在多份归档
- **THEN** 系统 SHALL 优先活动并提示冲突，活动缺文档不读旧副本，多份归档禁用含糊入口

#### Scenario: 状态映射与缺失
- **WHEN** 活动trace为proposed/in_progress/applied，或唯一归档，或未知状态
- **THEN** 系统 SHALL 分别映射待开发/研发中/验收中、已完成或默认收起的数据异常诊断入口；未知对象不渲染卡片、不计入页面业务统计
- **AND** 缺tasks显示未知，任务全部勾选不自动改为已完成；Sprint信息不覆盖trace

#### Scenario: 稳定快照失败
- **WHEN** registry解析失败、迁移半写入或项目切换发生
- **THEN** 系统 SHALL 保留受控同步失败状态，不能把全部Change判成独立，不能将旧项目迟到响应覆盖新项目

### Requirement: 独立变更交付验收来源
系统 SHALL 按独立Change交付证据定位验收来源，不套用Issue的固定acceptance.md要求。

#### Scenario: 历史验证记录
- **WHEN** 无显式acceptance_refs且没有acceptance.md或verification.md
- **THEN** 系统 SHALL 接受trace中非空验证记录、验收记录、验证结果或验收结果章节作为证据入口；无来源时提示待核实
- **AND** 证据存在 SHALL 不被解释为自动验收通过

#### Scenario: 显式来源
- **WHEN** trace声明acceptance_refs
- **THEN** 系统 SHALL 校验每个Change内相对Markdown引用，拒绝越界，缺失或空文件明确提示，不回退掩盖错误

### Requirement: 稳定读取性能与授权一致性

系统 SHALL 降低未变化快照和单文档读取的重复处理，同时保留文件变更可见性、成员与对象授权、项目绑定、写入围栏及缓存隔离。

#### Scenario: 成功暖读性能对照
- **WHEN** 对同一有效快照及环境的基线和修复版分别预热并对context和MD各采样30次
- **THEN** 两类暖读p95均较成功基线降低至少50%，冷读单列，不以503快速失败作为基线

#### Scenario: 文件与权限变化
- **WHEN** 文件新增删除重命名修改（含同尺寸快速修改）、权限撤销或绑定/围栏变化
- **THEN** 下一次有效同步读取反映变化或安全拒绝，不能返回跨用户越权内容或混合版本

#### Scenario: 持久解析失败恢复
- **WHEN** 注册表语法错误后被纠正
- **THEN** 读取先返回安全错误，纠正后重试恢复成功；不得永久缓存失败或绕过校验读取

### Requirement: 项目作用域及版本校验

系统 SHALL 在所有需求中心数据、文档与保存入口重新验证项目权限和版本，拒绝隐式跨项目回退。

#### Scenario: 缺少或无权项目身份
- **WHEN** 请求缺少空间仓库身份或用户无权访问
- **THEN** 系统拒绝请求，不返回全局治理数据或其他项目缓存

#### Scenario: 保存旧文档基准
- **WHEN** 文档内容已被外部更新而用户携带旧版本保存
- **THEN** 系统返回冲突并保留外部文件，页面保留用户草稿

### Requirement: 项目快照自动刷新

系统 SHALL 在服务正常、前台可见及文件稳定可读条件下于5秒内反映治理变化，异常保留最后完整快照。

#### Scenario: 正常轮询与页面恢复
- **WHEN** 本地治理文件稳定落盘或页面恢复可见
- **THEN** 前台主动刷新当前项目，保留筛选和草稿，在工具栏刷新按钮提示中显示成功同步时间，需求中心不显示独立项目连接栏

#### Scenario: 解析失败与迟到响应
- **WHEN** 文件写入中、解析失败或响应属于已离开的项目
- **THEN** 系统不呈现部分快照或旧项目内容，失败显示状态并可手动重试

#### Scenario: 首屏加载与后台刷新分离

- **WHEN** 首屏快照尚未返回
- **THEN** 指标、阶段计数和卡片位置显示骨架，不呈现假零值、空态或独立加载面板
- **AND** 标题、工具栏与阶段列在加载完成前后保持位置稳定
- **WHEN** 已有快照时手动刷新或轮询
- **THEN** 保留已有数据与筛选，只显示刷新按钮忙碌状态

#### Scenario: 卡片追踪文档固定所属Issue

- **WHEN** 用户在任一阶段查看REQ或BUG卡片
- **THEN** 卡片仅提供一个标签为trace.md的入口，读取所属Issue目录的trace.md
- **AND** 不提供Change trace入口，文件缺失时明确不可用且不回退Change trace
- **AND** Change仍用于内部阶段计算，其他文档入口和原授权边界保持

#### Scenario: 卡片进度入口定位任务文档

- **WHEN** 用户点击 REQ 或 BUG 卡片的研发、测试或人工验收入口
- **THEN** 系统 SHALL 通过当前卡片关联文档入口读取完整 tasks.md，在加载后优先定位对应章节、其次定位匹配任务并高亮，不打开独立进度面板，不改变文档权限
- **AND** 关联或文件缺失时 SHALL 明确提示；目标章节或任务缺失时 SHALL 展示完整文档并说明未找到目标，不回退其他文档或历史返修任务

#### Scenario: 卡片读取关联 Sprint 计划

- **WHEN** 用户查看已关联 Sprint 的 REQ 或 BUG 卡片并打开 sprint.md
- **THEN** 系统 SHALL 在授权项目内根据关联和成员关系解析 Sprint 文档，卡片展示、文档读取和缺失校验共用该解析，提供完整只读正文
- **AND** 系统 SHALL 兼容同 ID 的活动和归档目录，仅活动目录不存在时查归档目录；关联或文件缺失时明确提示，不回退 Issue、Change、其他 Sprint 或活动目录缺文件时的旧归档副本

#### Scenario: 主动作阻塞提示与禁用一致

- **WHEN** 卡片存在接口阻塞、Issue阻塞或缺少当前阶段前置文档
- **THEN** 系统 SHALL 使用同一原因显示阻塞提示并禁用主动作，执行前再次检查，不打开动作弹窗或提交操作；已有文档仍可阅读
- **AND** 前置条件补齐并刷新后 SHALL 根据新结果恢复主动作

#### Scenario: Tips 避让 Agent 助手

- **WHEN** Tips与Agent助手同时显示，包含窄屏及长文案场景
- **THEN** 系统 SHALL 在助手上方显示Tips并保留间距，保证可读层级、边界内宽度及长词换行，超长内容允许容器内滚动

#### Scenario: Issue 主文档生成后持续展示

- **WHEN** REQ的requirement.md或BUG的bug.md已在所属Issue目录生成
- **THEN** 系统 SHALL 在所有阶段卡片保留该主文档并优先显示，包括已完成阶段；读取所属Issue当前或归档目录的实际正文，保留既有编辑权限
- **AND** 系统 SHALL 不使用Change同名文件补齐；未生成不伪造入口，后续删除按快照反映，读取缺失时明确提示

#### Scenario: Sprint 文档跨阶段持续展示

- **WHEN** 卡片已具备关联Sprint的sprint.md文档入口
- **THEN** 系统 SHALL 在后续全部阶段持续展示该入口，包括已完成；主文档requirement.md或bug.md仍优先
- **AND** 系统 SHALL 保留关联来源、只读权限、归档兼容与缺失不回退，不因展示范围扩大而新增其他阶段必需文档校验

#### Scenario: 卡片文档按用途分组
- **WHEN** 卡片存在常驻文档或阶段文档
- **THEN** 常驻文档按主文档、Sprint、trace排序，阶段文档按当前任务优先排序
- **AND** 双组以4px紧凑换行区分，无分隔线，单组无占位，来源、权限、必需文档校验不变

#### Scenario: 完整卡片更新时间
- **WHEN** 展示任一阶段REQ或BUG卡片
- **THEN** 有效更新时间显示YY/MM/DD HH:mm，缺失或无效显示更新时间未知，不补造日期或时分
- **AND** 窄屏时间不拆分，必要时footer动作换行

#### Scenario: 所属需求原型持续展示
- **WHEN** 所属REQ存在安全可读的原型HTML
- **THEN** 所有阶段主文档之后展示原型入口，多端标识区分，兼容归档
- **AND** 缺失不占位、不新增必需文档，保留项目授权和HTML预览安全策略

#### Scenario: 原型标签仅保留相对路径
- **WHEN** 卡片显示原型HTML入口
- **THEN** 标签为区分多端所需相对路径，不附加“原型 · ”前缀，排序与预览行为不变
