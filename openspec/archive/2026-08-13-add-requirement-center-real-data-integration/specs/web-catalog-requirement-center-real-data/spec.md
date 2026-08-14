## ADDED Requirements

### Requirement: 需求中心上下文聚合

系统 SHALL 提供前台需求中心上下文聚合接口，返回当前用户、可访问空间、当前空间、权限态、统计、筛选选项和治理对象列表。

#### Scenario: 首屏获取真实上下文

- **WHEN** 用户进入 `/requirements` 且请求需求中心上下文接口
- **THEN** 系统返回可驱动页面首屏的用户、空间、权限、统计、筛选和治理对象数据

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

系统 SHALL 将 REQ、BUG、Sprint 和 OpenSpec Change 状态映射到采集池、规划中、待评审、已通过、迭代规划、待开发、研发中、验收中、已完成 9 个阶段。

#### Scenario: 已纳入 Sprint 但未创建 Change

- **WHEN** REQ 或 BUG 状态为 `in_sprint` 且没有关联 OpenSpec Change
- **THEN** 系统将该对象映射到“迭代规划”阶段

#### Scenario: Change 已创建但未 apply

- **WHEN** REQ 或 BUG 已关联 OpenSpec Change 且 Change 尚未完成 apply
- **THEN** 系统将该对象映射到“待开发”或“研发中”阶段，并返回任务进度摘要

#### Scenario: 已闭环对象

- **WHEN** REQ 或 BUG 状态为 `done` 或关联 Change 已归档
- **THEN** 系统将该对象映射到“已完成”阶段

### Requirement: 字段白名单与安全脱敏

系统 SHALL 对治理文件读取结果执行字段白名单映射和错误脱敏，不得向浏览器暴露本机路径、密钥、token、`.env` 内容、原始日志、Markdown 全文或异常堆栈。

#### Scenario: API 响应不包含敏感字段

- **WHEN** 后端从治理文件聚合需求中心数据
- **THEN** API 响应只包含设计文档声明的白名单字段

#### Scenario: 解析失败错误脱敏

- **WHEN** 某个治理文件读取或解析失败
- **THEN** 系统返回受控错误或对象级阻塞提示，且不包含本机绝对路径、堆栈或原始文件内容

### Requirement: 真实统计、筛选和搜索

系统 SHALL 基于真实治理对象支持统计、对象类型筛选、负责人筛选、优先级筛选、Sprint 筛选和关键词搜索。

#### Scenario: 统计与筛选一致

- **WHEN** 用户调整筛选条件
- **THEN** 统计区和看板卡片范围基于同一过滤结果刷新

#### Scenario: 搜索覆盖关键字段

- **WHEN** 用户输入 ID、标题、阶段产物、负责人或来源关键词
- **THEN** 看板只展示匹配的治理对象，并保留 9 阶段列

### Requirement: 空间上下文与权限态

系统 SHALL 基于真实用户和空间权限控制可访问空间、当前空间和高权限入口展示。

#### Scenario: 首版空间来自项目治理元数据

- **WHEN** 系统尚未引入 Workspace 数据库事实源
- **THEN** 需求中心 BFF 从 `MOONBOX_GOVERNANCE_ROOT/project.yaml` 派生当前项目空间
- **AND** 成员数由治理对象负责人和当前登录用户计算
- **AND** 空间角色由当前登录用户角色派生
- **AND** 系统不得返回硬编码演示空间

#### Scenario: 本地空间不可访问

- **WHEN** 本地保存的 workspaceId 不在用户可访问空间中
- **THEN** 系统回退到默认可访问空间并更新本地选择

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
