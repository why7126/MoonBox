---
change_id: add-requirement-center-sprint-dropdown-status
type: update
status: proposed
requirement_id: REQ-0032-requirement-center-sprint-dropdown-status
req_id: REQ-0032-requirement-center-sprint-dropdown-status
sprint_id: sprint-006
---

## 背景

需求中心 Sprint 筛选下拉目前主要展示 Sprint ID，用户无法在选择时直接区分当前、规划中、已完成或归档迭代，容易选错范围并误读卡片统计。REQ-0032 已评审并纳入 sprint-006，本 Change 将 Sprint 状态展示纳入正式需求中心筛选契约。

## 变更内容

- 在需求中心工具栏 Sprint 筛选下拉中展示每个具体 Sprint 的状态。
- 复用 Sprint 事实源和需求中心稳定快照，不由前端临时编造状态。
- 覆盖 planning、in_progress、completed、归档和未知/冲突状态的中文映射与降级展示。
- 保持“全部 Sprint”、默认选择、手动选择、搜索筛选叠加、刷新和项目切换行为兼容。
- 补齐 UI Contract、UI Skeleton、观测声明、测试和视觉验收任务。

## 能力影响

### 新增能力

无。

### 修改能力

- `web-catalog-requirement-center`：扩展前台需求中心筛选与搜索能力，使 Sprint 筛选选项展示可追溯状态，并保持筛选行为、权限和异常降级一致。

## 影响面

- Web：需求中心 Sprint 筛选控件、筛选状态、深浅主题和窄屏展示。
- API：需核实现有需求中心上下文或 Sprint 列表响应是否已提供结构化 Sprint 状态；若缺失，需要扩展响应模型、OpenAPI 和客户端类型。
- 测试：后端聚合/响应字段测试、前端筛选控件测试、视觉或 computed style 验收。
- 文档：同步 REQ trace、Sprint scope、OpenSpec delta spec、API 文档和验收证据。
- 数据采集与观测：适用 `usage_events` 与 `request_logs`；不预期新增 DB、对象存储、Task Trace 或部署拓扑。
