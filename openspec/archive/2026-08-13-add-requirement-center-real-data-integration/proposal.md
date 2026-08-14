## 背景

REQ-0012 已完成前台需求中心页面骨架和交互，但运行时仍依赖 `initialIssues`、`workspaces`、`currentUser` 等静态 Mock 数据。需求中心要成为真实研发治理入口，必须从后端聚合 REQ、BUG、Sprint、OpenSpec Change、空间和用户权限事实源，并以安全脱敏的数据契约驱动页面。

## 变更内容

- 新增需求中心 BFF 聚合能力，提供 `/api/v1/requirement-center/context` 首屏上下文接口。
- 首版从治理文档、`issues/*/_registry.yaml`、Issue `trace.md`、Sprint 四件套和 OpenSpec Change 文件聚合真实数据。
- 将 REQ/BUG/Sprint/OpenSpec 状态映射到 9 阶段看板，并返回对象级阻塞或事实源漂移提示。
- 替换前端生产运行时 `initialIssues`、`workspaces`、`currentUser` 静态数据。
- 增加加载态、错误态、空态、筛选无结果态、无权限态和空间切换后的刷新行为。
- 同步 API 文档、OpenAPI 来源、前后端测试和安全脱敏约束。

## 能力范围

### 新增能力

- `web-catalog-requirement-center-real-data`: 前台需求中心真实数据聚合、状态映射、空间权限和页面状态能力。

### 修改能力

- 无。当前 `openspec/specs/` 尚无已生效的需求中心规格；REQ-0012 仍是 active Change，当前变更以新增规格承接真实数据能力。

## 影响范围

- Backend: 新增 requirement-center API、schema、service/repository 或等价聚合模块，读取治理事实源并做字段白名单映射。
- Web: 更新需求中心页面数据获取、状态容器、筛选统计和权限入口渲染。
- API: 新增 `/api/v1/requirement-center/context`，可能预留 `/api/v1/requirement-center/issues`。
- Security: 增加本地路径、密钥、日志、Markdown 全文和异常堆栈脱敏测试。
- Tests: 新增后端接口/状态映射/脱敏测试与前端 loading/error/empty/permission/filter 测试。
- Docs: 同步 API 索引、OpenAPI 来源和 Sprint/REQ 验收证据。
