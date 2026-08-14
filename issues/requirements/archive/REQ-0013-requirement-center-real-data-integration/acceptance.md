---
requirement_id: REQ-0013-requirement-center-real-data-integration
title: 需求中心真实数据接入
acceptance_status: passed
owner: product
source: requirement.md
priority: P1
created_at: 2026-08-10 21:53:16
updated_at: 2026-08-14 16:29:34
---

# 验收标准

## 功能 AC

- [ ] AC-001 后端提供需求中心 BFF 聚合接口，返回当前用户、可访问空间、当前空间、权限态、统计、筛选选项和治理对象列表。
- [ ] AC-002 首版真实数据源来自治理文档、`issues/*/_registry.yaml`、单条 `trace.md`、Sprint 四件套和 OpenSpec Change 文件，不引入新的数据库事实源。
- [ ] AC-003 API 响应必须经过字段白名单映射，不得返回 Markdown 全文、本机绝对路径、系统用户名、密钥、token、`.env` 内容、原始日志或异常堆栈。
- [ ] AC-004 Requirement 与 Bug 必须使用同一对象结构返回，并保留类型、ID、标题、优先级、负责人或来源、阶段、文档产物、更新时间、阻塞提示、Sprint ID、关联 Change、研发/测试/验收摘要和阶段动作映射。
- [ ] AC-005 系统必须将 REQ/BUG/Sprint/OpenSpec Change 状态映射到 9 阶段看板：采集池、规划中、待评审、已通过、迭代规划、待开发、研发中、验收中、已完成。
- [ ] AC-006 状态事实源冲突时必须返回对象级阻塞或漂移提示；前端不得静默吞掉冲突，也不得用 registry 摘要覆盖 trace 事实源。
- [ ] AC-007 前端生产运行时必须移除 `initialIssues`、`workspaces`、`currentUser` 静态数据依赖，改由接口数据驱动。
- [ ] AC-008 数据请求期间必须展示加载态，且不得短暂闪现 Mock 卡片、Mock 空间或 Mock 用户。
- [ ] AC-009 接口失败时必须展示错误态和重试操作；错误文案不得暴露内部路径、堆栈或原始文件内容。
- [ ] AC-010 当前空间无对象时展示空间空态；筛选无结果时展示筛选空态；两者必须可区分，并保留 9 阶段列结构。
- [ ] AC-011 统计区必须基于真实对象和当前筛选条件计算，至少展示全部对象、需求、Bug、当前阻塞。
- [ ] AC-012 筛选必须支持对象类型、负责人、优先级和 Sprint；搜索必须支持 ID、标题、阶段产物、负责人或来源。
- [ ] AC-013 空间列表必须来自接口返回的可访问空间；本地保存空间不可访问时必须回退到默认可访问空间并更新本地选择。
- [ ] AC-013A 首版未引入 Workspace 数据库时，空间必须从 `project.yaml`、治理对象负责人和当前登录用户派生，不得返回硬编码演示空间。
- [ ] AC-014 “进入后台”“设置空间”“创建或加入空间”等入口必须由真实权限态控制；无权限时隐藏或禁用并提供可理解原因。
- [ ] AC-015 切换空间、保存空间设置或点击刷新后，页面必须重新获取 context，并保持统计、筛选项、卡片列表和用户区空间摘要一致。
- [ ] AC-016 后端聚合读取必须有边界控制，避免无界扫描 archive、generated、node_modules、dist、coverage 或其他高噪音目录。
- [ ] AC-017 必须覆盖后端接口测试、状态映射测试、脱敏安全测试、前端加载/错误/空态测试、筛选搜索测试和权限态测试。
- [ ] AC-018 如新增 API，必须同步 API 文档、OpenAPI 来源和客户端调用约束；如涉及安全边界，必须同步安全规则或相关测试。

## UI 状态 AC

- [ ] AC-UI-001 加载态应出现在统计区、筛选区和看板区域的自然位置，不得导致侧边栏、页面标题或 9 阶段列宽明显跳动。
- [ ] AC-UI-002 错误态必须提供重试主操作，并保持深色和浅色主题下文字、边框、按钮和说明清晰可读。
- [ ] AC-UI-003 空态和筛选无结果态不得删除 9 阶段列，不得展示横向滚动提示类冗余说明。
- [ ] AC-UI-004 无权限态必须使用真实权限说明，避免出现用户可见但点击后才发现无权限的高风险入口。
- [ ] AC-UI-005 真实数据字段过长时必须截断或换行，不得遮挡卡片 ID、Sprint 标签、标题、阶段动作、列头计数或更新时间。
- [ ] AC-UI-006 替换真实数据后，REQ-0012 已验收的侧边栏、用户菜单、空间切换、空间设置弹窗、主题切换和看板视觉结构必须保持一致。

## 原型驱动 UI AC

- [ ] AC-PROTOTYPE-001 原型拆解必须覆盖页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点和 1440px 验收焦点。
- [ ] AC-PROTOTYPE-002 `/req-opsx` 生成 Change 时，design.md 必须写入 UI Skeleton，覆盖真实数据状态容器、加载态、错误态、空态、无权限态、权限入口和可测选择器。
- [ ] AC-PROTOTYPE-003 `/opsx-apply` 实现阶段必须在 1440px 桌面视口验收真实数据首屏、加载态、错误态、空态、筛选无结果态、权限差异态和空间切换后刷新状态。
- [ ] AC-PROTOTYPE-004 `/opsx-archive` 前必须完成 REQ 最终一致性检查，确认 requirement.md、acceptance.md、trace.md 与最终 Change 设计、实现证据和 Mock/API 边界一致。

## 横切 AC（knowledge-base）

本 REQ 不命中 `admin-list`、`admin-form`、`admin-modal`、`media-upload` 四类管理端横切标签，因此无管理端横切 AC。

> 来源：`docs/knowledge-base/best-practices/prototype-driven-ui-gate.md` — 预防带 prototype UI 在实现阶段缺少 UI Skeleton、1440px 视觉证据和最终一致性回填。

- [ ] AC-XCUT-001 Change `design.md` 必须声明 Mock/API 边界，明确哪些数据来自真实 BFF、哪些测试 fixture 仅用于测试，不得让 Mock 进入生产运行时路径。
- [ ] AC-XCUT-002 Change `tasks.md` 中 UI Skeleton 任务必须早于真实接口接入和细节状态实现任务。
- [ ] AC-XCUT-003 1440px 视觉验收必须记录工具/命令、viewport、页面路径、截图或等价证据入口、结果摘要和例外说明。
- [ ] AC-XCUT-004 UI 返修后不得沿用旧截图或旧验收结论，必须重跑涉及状态的 1440px 验收并回填 REQ/Change 文档。
- [ ] AC-XCUT-005 归档前必须确认 linked REQ 文档与 Change 设计、最终实现、验收证据、真实数据状态和 Mock/API 边界一致。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: add-requirement-center-real-data-integration
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

