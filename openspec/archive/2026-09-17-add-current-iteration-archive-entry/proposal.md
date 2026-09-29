## 背景与动机

需求中心已经展示当前迭代容量，但迭代进入收尾阶段时缺少就近的“归档当前迭代”入口。REQ-0037 要求在当前迭代已有实际容量投入后提供归档确认入口，同时不能绕过 Sprint archive 的未归档范围、验收 sign-off、权限和 Workflow Sync 门禁。

## 变更内容

- 在需求中心当前迭代容量区域或当前迭代操作区新增“归档当前迭代”入口。
- 入口展示与启用基于 `used_capacity > 0` 和 Sprint archive readiness 汇总；当任一 REQ、BUG 或独立 Change 未归档闭环时，入口隐藏或禁用并展示安全摘要。
- 点击入口进入高风险确认流程，展示目标 Sprint、容量摘要、readiness 门禁结果和归档影响，不直接执行归档。
- 归档执行继续复用既有 Sprint archive 后端/脚本门禁、验收报告 sign-off、权限校验和 Workflow Sync，同步失败不得伪装成功。
- 补齐行为事件、请求日志与 Task Trace 复用/接入口径，确保高风险写操作具备脱敏观测摘要。
- 不新增独立 Sprint archive 状态机，不自动归档未完成 Change，不自动补签验收报告，不修改容量计算规则。

## 能力影响

### 新增能力

无。

### 修改能力

- `web-catalog-requirement-center`: 增加当前迭代归档入口、确认流程、不可用状态、权限态、刷新一致性和原型驱动 UI 验收要求。
- `web-catalog-requirement-center-real-data`: 扩展需求中心上下文或等价 API，提供 Sprint archive readiness 安全摘要，并明确权限、脱敏、观测和最终门禁仍以后端/治理命令为准。

## 影响范围

- Web：需求中心当前迭代容量区域、操作区、确认弹窗、门禁列表、禁用态、toast/inline status、深浅主题和窄屏布局。
- API / 后端：需求中心上下文需要提供 readiness 安全摘要或复用既有 Sprint archive readiness API；归档执行继续调用既有 Sprint archive 路径。
- 观测：入口点击、确认取消、权限拒绝、门禁失败、归档成功和 Workflow Sync 失败需要行为事件或等价摘要；归档执行请求需要请求日志和 Task Trace 覆盖或复用声明。
- 测试：前端状态组合、后端 readiness 权限与脱敏、OpenAPI/客户端生成影响、Workflow Sync 失败与刷新一致性、1440px/390px 视觉证据。
