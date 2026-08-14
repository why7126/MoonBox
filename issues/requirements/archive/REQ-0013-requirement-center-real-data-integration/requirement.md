---
requirement_id: REQ-0013-requirement-center-real-data-integration
title: 需求中心真实数据接入
terminal: web-catalog
version: v1
status: done
owner: product
source: capture.md
priority: P1
parent_requirement: REQ-0012-frontend-requirement-center
created_at: 2026-08-10 20:10:56
updated_at: 2026-08-13 22:48:16
---

# 需求中心真实数据接入

## 背景

REQ-0012 已完成 MoonBox 前台需求中心的 UI 原型、9 阶段看板、筛选搜索、空间切换、用户菜单和交互骨架。当前页面仍以内置 Mock 数据驱动，`initialIssues`、`workspaces`、`currentUser` 均定义在前端页面内，统计、筛选、权限入口和空间设置也基于这些静态数据推导。

需求中心要成为真实的研发治理入口，必须接入项目当前事实源：REQ、BUG、Sprint、OpenSpec Change、空间和用户权限。首版不引入新的数据库事实源，采用后端 BFF 聚合接口读取治理文档、registry、OpenSpec 和 Sprint 文件，统一脱敏、映射和返回页面所需数据，替换前端 Mock 数据。

## 目标用户

- 产品负责人：需要在需求中心查看真实 REQ/BUG 流转状态、阻塞项、Sprint 归属和下一步动作。
- 项目负责人：需要按空间查看当前迭代、研发中、验收中和已完成对象的真实统计。
- 开发与测试协作者：需要通过看板识别缺失文档、OpenSpec Change 状态、任务进度和验收入口。
- 空间管理员：需要根据当前空间权限查看或管理空间设置、成员权限和治理对象可见范围。

## 范围

### 包含

- 新增需求中心 BFF 聚合接口，面向前台需求中心提供页面上下文数据。
- 首版数据源采用治理文档、`issues/*/_registry.yaml`、单条 `trace.md`、Sprint 四件套和 OpenSpec Change 文件聚合。
- 聚合 Requirement、Bug、Sprint 和 OpenSpec Change 状态，并映射到 REQ-0012 定义的 9 阶段看板。
- 返回当前用户、可访问空间、当前空间、空间角色、前台权限态和管理入口可见性。
- 替换前端 `initialIssues`、`workspaces`、`currentUser` 静态数据。
- 支持真实统计、筛选、搜索、权限态、加载态、空态和错误态。
- 保留 REQ-0012 已验收的页面布局、卡片信息、阶段动作文案、空间切换和主题切换体验。
- 覆盖前后端测试、API 文档和公开安全边界。

### 不包含

- 不在本需求内实现 req/bug/sprint/opsx 命令的在线执行。
- 不在本需求内重做 REQ-0012 的整体视觉体系、导航结构或 9 阶段定义。
- 不在本需求内建设完整产品化数据库模型或治理数据迁移任务。
- 不直接把本地文件路径、未脱敏文档全文、系统用户名、密钥、日志或内部异常暴露给前端。
- 不新增移动端、桌面端、微信小程序或管理后台需求中心页面。
- 不接入第三方权限系统、SSO、外部项目管理工具或通知渠道。

## 功能要求

### FR-001 需求中心上下文聚合接口

系统 MUST 提供面向前台需求中心的 BFF 聚合接口，用于一次性获取页面首屏所需上下文。响应至少包含当前用户、可访问空间列表、当前空间、空间权限、统计摘要、筛选选项和治理对象列表。

聚合接口 SHOULD 位于 `/api/v1/requirement-center` 能力域下，并复用项目统一响应结构、错误码、安全中间件和 API 文档约束。

### FR-002 文件事实源读取与脱敏

首版数据源 MUST 读取当前项目治理事实源，包括 `issues/requirements/_registry.yaml`、`issues/bugs/_registry.yaml`、对应 Issue `trace.md`、Sprint 四件套和 OpenSpec Change 元信息。

后端 MUST 对文件读取结果进行字段级白名单映射，不得把原始 Markdown 全文、本机绝对路径、系统用户名、未脱敏日志、密钥、访问令牌、`.env` 内容或内部堆栈透传给浏览器。

### FR-003 9 阶段状态映射

系统 MUST 将 REQ、BUG、Sprint 和 OpenSpec Change 的状态映射到 REQ-0012 定义的 9 阶段：采集池、规划中、待评审、已通过、迭代规划、待开发、研发中、验收中、已完成。

状态映射 MUST 有明确优先级：单条 Issue `trace.md` 优先于 registry 摘要；Sprint 四件套用于判断迭代归属；OpenSpec Change 用于判断待开发、研发中、验收中和已完成阶段。出现冲突时，接口 MUST 返回可展示的阻塞或漂移提示，而不是静默选择任一状态。

### FR-004 治理对象列表

接口返回的治理对象 MUST 至少包含：ID、类型、标题、优先级、负责人或来源、阶段、阶段产物、更新时间、阻塞提示、Sprint ID、关联 Change、研发任务进度、测试或验收摘要，以及当前阶段主动作所需的命令映射。

Requirement 与 Bug MUST 使用同一返回结构，并保留类型字段，便于前端沿用 REQ-0012 的卡片视觉差异和阶段动作映射。

### FR-005 真实统计、筛选和搜索

需求中心 MUST 基于真实返回数据展示统计，包括全部对象、需求、Bug、当前阻塞等首版指标。统计结果 MUST 与当前搜索和筛选条件一致。

筛选 MUST 支持对象类型、负责人、优先级和 Sprint。搜索 MUST 支持 ID、标题、阶段产物、负责人或来源。首版 MAY 由前端对已加载数据进行筛选，但接口响应字段必须完整支撑后续服务端分页和服务端筛选演进。

### FR-006 空间上下文与权限态

接口 MUST 返回当前用户可访问的空间列表、当前空间、空间角色和关键权限态。前端 MUST 使用真实权限决定“进入后台”“设置空间”“创建或加入空间”等入口是否可见或可操作。

当前空间选择 SHOULD 继续支持本地最近选择；当本地保存的空间不在用户可访问范围内时，系统 MUST 回退到默认可访问空间，并清理或覆盖无效选择。

### FR-007 加载态、错误态、空态和无权限态

前端 MUST 在数据请求期间展示加载态，避免用 Mock 数据短暂闪现。

接口失败、数据解析失败、权限不足、当前空间无对象、筛选无结果等场景 MUST 有清晰状态展示，并提供可恢复操作，例如重试、清空筛选或切换空间。

错误态不得展示内部文件路径、堆栈、原始异常、密钥、token 或治理文档全文。

### FR-008 前端数据替换与兼容

前端 MUST 移除页面内硬编码的 `initialIssues`、`workspaces`、`currentUser` 作为运行时数据源，改为通过数据客户端或 hook 获取真实数据。

页面 SHOULD 保留少量类型定义、空态占位和测试 fixture，但这些 fixture 不得参与生产运行时路径。

### FR-009 缓存、刷新和一致性

后端 SHOULD 以文件更新时间、registry 更新时间或等价机制支持轻量缓存，避免每次请求都进行无边界全目录扫描。

当用户切换空间、保存空间设置或执行刷新操作后，前端 MUST 重新获取需求中心数据，并保持统计、筛选项、卡片列表和当前空间摘要一致。

### FR-010 测试与文档

本需求 MUST 覆盖后端聚合接口测试、状态映射测试、脱敏安全测试、前端加载/错误/空态测试、筛选搜索测试和权限态测试。

如新增或修改 API，MUST 同步 API 文档、OpenAPI 来源和客户端调用约束；如涉及安全边界，MUST 同步安全规则或相关测试。

## UI 约束

- 页面整体布局、侧边栏、品牌区、用户菜单、空间切换、空间设置弹窗、主题切换和 9 阶段看板视觉 MUST 延续 REQ-0012。
- 加载态应放在统计区、筛选区和看板区域的自然位置，不得造成布局大幅跳动。
- 错误态和空态应保持前台需求中心的深浅主题可读性，并提供明确主操作。
- 无权限态应弱化不可操作入口或隐藏高风险入口，不得只依赖按钮禁用而缺少原因说明。
- 真实数据字段过长时必须截断或换行，不能挤压卡片标题、标签、阶段动作或列头。
- 过滤后仍必须保留 9 个阶段列，不得因某阶段无数据而删除列。

## 关联需求

- REQ-0012-frontend-requirement-center：本需求承接其页面骨架、9 阶段看板、空间切换和 UI 约束，将 Mock 数据替换为真实聚合数据。
- REQ-0008-prototype-driven-page-acceptance-gate：本需求若引发 UI 状态新增，仍需满足原型驱动页面验收门禁。
- REQ-0005-admin-auth-system：当前用户与权限态可复用既有认证能力，前台权限模型不足部分由本需求补齐或定义最小可用返回字段。

## 状态块

```yaml
status: archived
generated_at: 2026-08-10 20:10:56
completed_at: 2026-08-10 21:53:16
reviewed_at: 2026-08-10 22:01:53
approved_at: 2026-08-10 22:01:53
source_material:
  - capture.md
  - req-explore: REQ-0013 是 REQ-0012 的后续真实数据增强需求，不并回父需求
  - user-confirmed: 数据接入路线采用需求中心 BFF 聚合接口
  - user-confirmed: 首版数据源采用治理文档、registry、OpenSpec 和 Sprint 文件聚合
next: /req-opsx REQ-0013-requirement-center-real-data-integration
iteration: sprint-002
```
