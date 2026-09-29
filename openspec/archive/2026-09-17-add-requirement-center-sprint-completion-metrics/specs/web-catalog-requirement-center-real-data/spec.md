## ADDED Requirements

### Requirement: Sprint 指标事实源聚合
需求中心上下文聚合 MUST 提供 Sprint 数量摘要，字段来自当前项目 Sprint 生命周期事实源，并支持已完成数、累计数、口径来源和脱敏 warning。

#### Scenario: 聚合已完成与累计 Sprint
- **WHEN** 需求中心请求上下文数据
- **THEN** 响应必须包含 Sprint 数量摘要
- **AND** `total_count` 必须统计 `iterations/change/` 与 `iterations/archive/` 下可识别的有效 Sprint
- **AND** `completed_count` 必须统计已完成 Sprint
- **AND** 同一 Sprint ID 同时出现在多个来源时必须只计数一次

#### Scenario: 兼容 completed 未归档状态
- **WHEN** `iterations/change/` 中存在 `status: completed` 但尚未迁入 `iterations/archive/` 的 Sprint
- **THEN** 聚合逻辑必须明确是否计入 `completed_count`
- **AND** 若同一 Sprint 后续进入 archive，已完成数不得重复增加
- **AND** 测试必须固定该兼容口径

#### Scenario: Sprint 指标不受看板筛选影响
- **WHEN** 请求携带搜索、对象类型、负责人、优先级或 Sprint 筛选条件
- **THEN** 需求、缺陷和看板卡片聚合可以按既有规则过滤
- **AND** Sprint 数量摘要必须保持当前项目级总览口径

#### Scenario: 响应字段安全脱敏
- **WHEN** Sprint 生命周期文件读取、解析或权限检查失败
- **THEN** 接口可以返回脱敏 warning 或受控错误
- **AND** 响应不得包含本机绝对路径、系统用户名、内部堆栈、密钥、token、`.env` 内容或未脱敏治理文档全文
- **AND** 请求日志不得记录原始治理文件内容

#### Scenario: API 契约与客户端类型同步
- **WHEN** Sprint 数量摘要字段进入需求中心上下文响应
- **THEN** 后端响应 schema、OpenAPI 来源、API 文档和前端客户端类型必须同步
- **AND** 前端不得依赖原型静态数字作为生产默认值
