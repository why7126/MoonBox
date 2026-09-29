## ADDED Requirements

### Requirement: 当前迭代归档 readiness 上下文

系统 SHALL 在需求中心上下文或等价 Sprint archive readiness 接口中提供当前迭代归档入口所需的安全摘要，确保前端入口状态与 Sprint archive 事实源一致，并保持权限、脱敏、观测和最终门禁边界。

#### Scenario: 返回归档 readiness 安全摘要
- **WHEN** 已登录用户请求需求中心上下文或当前迭代归档 readiness
- **AND** 当前用户有权查看目标 Sprint
- **THEN** 响应 SHALL 为每个可见当前迭代返回归档 readiness 安全摘要
- **AND** 安全摘要 SHALL 包含目标 Sprint、入口展示模式、是否允许进入确认、原因码和可展示的阻塞摘要
- **AND** 安全摘要 SHALL 基于 Sprint archive 事实源，不得由前端卡片数量或临时文案推断

#### Scenario: 汇总未归档范围阻塞
- **WHEN** 当前 Sprint 范围内存在未归档闭环的 REQ、BUG 或独立 Change
- **THEN** readiness SHALL 标记归档入口不可执行
- **AND** 响应 SHALL 返回安全的阻塞类型、可见对象标识或数量摘要
- **AND** 响应 MUST NOT 返回当前用户无权查看的对象 ID、路径、文档正文或内部错误详情

#### Scenario: 汇总验收 sign-off、权限和 Workflow Sync 阻塞
- **WHEN** 验收报告未 sign-off、当前用户无归档权限或 Workflow Sync 校验失败
- **THEN** readiness SHALL 标记归档入口不可执行
- **AND** 响应 SHALL 提供可展示原因码和修复方向
- **AND** 权限失败时响应 SHALL 使用安全摘要，不泄露不可见 Sprint、Change 或验收报告详情

#### Scenario: 容量为零或待核实时不允许执行
- **WHEN** 当前迭代 `used_capacity` 等于 0、容量事实源缺失或容量状态待核实
- **THEN** readiness SHALL 标记归档入口不可执行
- **AND** 响应 SHALL 保留可安全展示的解释
- **AND** 系统 MUST NOT 用伪造 `0/0` 或默认通过状态掩盖异常

#### Scenario: 归档执行重新校验
- **WHEN** 用户从需求中心发起 Sprint archive 执行请求
- **THEN** 后端或既有治理命令 SHALL 重新校验目标 Sprint、范围闭环、验收 sign-off、权限和 Workflow Sync
- **AND** 客户端传入的 readiness、权限状态、Sprint ID 或链路字段 MUST NOT 替代服务端校验
- **AND** 校验失败 SHALL 返回脱敏错误摘要和稳定错误码或原因码

#### Scenario: readiness 与归档观测
- **WHEN** 用户查看、点击、取消或执行当前迭代归档流程
- **THEN** 行为事件 SHOULD 记录入口点击、确认取消、权限拒绝、门禁失败、归档成功和 Workflow Sync 失败的脱敏摘要
- **AND** 归档执行请求 MUST 写入请求日志摘要，包含服务端可信 `request_id`、结果、耗时和脱敏错误码
- **AND** Sprint archive 多步骤执行 MUST 复用或补齐 Task Trace，以定位校验、归档、同步和失败节点
- **AND** 观测数据 MUST NOT 保存完整文档正文、本机路径、Authorization、Cookie、密钥、真实 `.env`、完整请求体或未脱敏错误堆栈

#### Scenario: API 与客户端契约同步
- **WHEN** 实现新增或调整 readiness 字段、归档执行响应、错误码或请求封装
- **THEN** 系统 MUST 同步 OpenAPI 来源、前端生成类型、API 文档和相关测试
- **AND** 若完全复用既有 Sprint archive API 与观测链路，Change trace 和验收记录 MUST 说明复用边界、不新增字段的原因和验证摘要
