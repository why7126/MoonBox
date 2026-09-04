# web-catalog-requirement-center-real-data Specification

## Purpose
TBD - created by archiving change add-requirement-center-real-data-integration. Update Purpose after archive.
## Requirements
### Requirement: 需求中心上下文聚合

系统 SHALL 提供前台需求中心上下文聚合接口，返回当前用户、可访问空间、当前空间、权限态、统计、筛选选项、治理对象列表、卡片文档入口、动作映射和进度摘要。

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

系统 SHALL 从治理文档、REQ/BUG registry、Issue trace、Sprint 四件套和 OpenSpec Change 元信息聚合首版真实数据。

#### Scenario: 聚合 REQ 与 BUG registry

- **WHEN** 后端构建需求中心治理对象列表
- **THEN** 系统读取 `issues/requirements/_registry.yaml` 与 `issues/bugs/_registry.yaml` 的白名单字段

#### Scenario: trace 优先于 registry

- **WHEN** Issue `trace.md` 与 registry 摘要状态不一致
- **THEN** 系统以 `trace.md` 为优先事实源，并返回对象级漂移提示

#### Scenario: Docker 环境读取治理事实源

- **WHEN** 后端运行在 Docker Compose 中
- **THEN** 系统通过 `MOONBOX_GOVERNANCE_ROOT` 读取只读挂载的 `issues/`、`iterations/`、`openspec/`、`docs/` 和 `rules/`，不得依赖容器内源码目录包含治理文件

### Requirement: 9 阶段状态映射

系统 SHALL 将 REQ、BUG、Sprint 和 OpenSpec Change 状态映射到采集池、规划中、待评审、已评审、迭代规划、待开发、研发中、验收中、已完成 9 个阶段。

#### Scenario: 已纳入 Sprint 但未创建 Change

- **WHEN** REQ 或 BUG 状态为 `in_sprint` 且没有关联 OpenSpec Change
- **THEN** 系统将该对象映射到“迭代规划”阶段

#### Scenario: Change 已创建但未 apply

- **WHEN** REQ 或 BUG 已关联 OpenSpec Change 且 Change 尚未完成 apply
- **THEN** 系统将该对象映射到“待开发”或“研发中”阶段，并返回任务进度摘要

#### Scenario: 已闭环对象

- **WHEN** REQ 或 BUG 状态为 `done` 或关联 Change 已归档
- **THEN** 系统将该对象映射到“已完成”阶段

#### Scenario: approved 展示为已评审

- **WHEN** REQ 或 BUG 的底层状态为 `approved`
- **THEN** 前端展示阶段必须为“已评审”
- **AND** API 可以保留 `approved` 作为机器状态，但必须提供可展示中文阶段或等价映射

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

系统 SHALL 在真实数据请求和异常场景中展示加载态、错误态、空空间态、筛选无结果态和无权限态。

#### Scenario: 请求期间不闪现 Mock 数据

- **WHEN** 需求中心上下文请求尚未完成
- **THEN** 页面展示加载态，且不展示 Mock 卡片、Mock 空间或 Mock 用户

#### Scenario: 接口失败可重试

- **WHEN** 需求中心上下文接口失败
- **THEN** 页面展示脱敏错误态和重试操作

#### Scenario: 筛选无结果保留 9 阶段

- **WHEN** 当前筛选条件没有匹配治理对象
- **THEN** 页面展示筛选无结果态，并保留全部 9 个阶段列

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

