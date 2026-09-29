## 背景与原因

需求中心已经作为 REQ、BUG、Sprint 与 OpenSpec Change 的治理看板入口，但当前指标区缺少项目级 Sprint 完成情况。产品负责人进入需求中心时无法直接判断项目已经完成多少个 Sprint、历史累计规划过多少个 Sprint，只能从 Sprint 文档或局部筛选结果中间接推断，容易造成口径漂移。

REQ-0030 已完成需求补齐、评审通过并纳入 `sprint-006`。本 Change 将把 Sprint 已完成数与累计数纳入需求中心事实源聚合和前台指标卡，保持与 Sprint 生命周期文件一致。

## 变更内容

- 在需求中心指标区新增 Sprint 指标，展示已完成 Sprint 数与总体 Sprint 数。
- 在需求中心上下文聚合接口中补充 `sprint_metrics` 摘要字段，统一从 `iterations/change/` 与 `iterations/archive/` 聚合。
- 明确已完成 Sprint、累计 Sprint、兼容 `status: completed` 未归档 Sprint 的去重口径。
- 明确 Sprint 指标为项目级总览，不随搜索、对象类型、负责人、优先级或 Sprint 筛选改变。
- 补充加载、空态、错误态、脱敏、安全展示、OpenAPI/客户端类型和视觉验收要求。

## 能力影响

### 新增能力

无。本 Change 扩展既有需求中心能力，不新增独立能力域。

### 修改能力

- `web-catalog-requirement-center`：新增 Sprint 数量指标的 UI、筛选解耦、状态展示和视觉验收要求。
- `web-catalog-requirement-center-real-data`：新增 Sprint 指标事实源聚合、响应字段、安全脱敏和统计口径要求。

## 影响范围

```yaml
requirement: REQ-0030-requirement-center-sprint-completion-metrics
sprint: sprint-006
change_type: add
impact:
  backend: true
  web: true
  miniapp: false
  admin: false
  database: false
  storage: false
  api: true
affected_layers:
  - request_logs
  - usage_events
product_data_collection_observability:
  status: applicable
  reason: 需求中心上下文请求会返回 Sprint 指标，页面加载、手动刷新和空间切换可能产生请求日志与行为事件。
  validation: 实现阶段需验证请求日志和行为事件只记录脱敏摘要，不记录治理文档全文、本机绝对路径或内部堆栈。
```

预期需要同步后端聚合逻辑、接口响应 schema、OpenAPI 来源、前端类型/客户端调用、需求中心 UI 和测试。无数据库迁移、对象存储、移动端、微信小程序、桌面端或管理后台改动。
