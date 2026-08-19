## MODIFIED Requirements

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
