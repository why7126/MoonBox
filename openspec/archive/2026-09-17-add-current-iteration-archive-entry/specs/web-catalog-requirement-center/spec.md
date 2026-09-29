## ADDED Requirements

### Requirement: 当前迭代归档入口

系统 SHALL 在前台需求中心当前迭代容量区域或当前迭代操作区提供受 Sprint archive readiness 控制的“归档当前迭代”入口，并通过确认流程复用既有 Sprint archive 门禁。

#### Scenario: 展示可进入确认的归档入口
- **WHEN** 用户打开需求中心
- **AND** 当前迭代存在
- **AND** 当前迭代 `used_capacity` 大于 0 人天
- **AND** Sprint archive readiness 汇总允许进入确认流程
- **THEN** 页面 SHALL 在当前迭代容量区域或当前迭代操作区展示“归档当前迭代”入口
- **AND** 入口 SHALL 明确绑定目标 Sprint
- **AND** 入口 SHALL 靠近容量信息展示，不得分散到每张治理对象卡片内

#### Scenario: 未归档闭环时隐藏或禁用入口
- **WHEN** 当前迭代 `used_capacity` 大于 0 人天
- **AND** Sprint 范围内任一 REQ、BUG 或独立 Change 未归档闭环
- **THEN** 页面 SHALL 隐藏归档入口或展示禁用态
- **AND** 若展示禁用态，页面 SHALL 展示安全摘要和修复方向
- **AND** 页面 MUST NOT 允许用户进入可执行归档路径
- **AND** 安全摘要 MUST NOT 泄露不可见资源细节、内部路径、堆栈、密钥或 `.env` 内容

#### Scenario: 容量或当前迭代不满足时不可执行
- **WHEN** 无当前迭代、无可见 Sprint、容量待核实、当前迭代解析失败或 `used_capacity` 等于 0
- **THEN** 页面 MUST NOT 提供可执行归档入口
- **AND** 页面 MAY 隐藏入口或展示不可用摘要

#### Scenario: 多当前迭代绑定目标 Sprint
- **WHEN** 需求中心存在多个当前迭代
- **THEN** 每个归档入口或确认流程 SHALL 明确绑定一个目标 Sprint
- **AND** 系统 MUST NOT 默认选择编号最大、更新时间最新或容量最高的 Sprint 直接进入归档
- **AND** 迟到的 readiness 或归档响应 MUST NOT 覆盖用户当前正在确认的其他 Sprint

#### Scenario: 点击入口进入确认流程
- **WHEN** 用户点击可进入确认的归档入口
- **THEN** 页面 SHALL 打开归档确认弹窗或等价 action modal
- **AND** 确认流程 SHALL 展示目标 Sprint ID、当前状态、容量摘要、门禁检查结果和归档影响
- **AND** 页面 MUST NOT 因入口点击直接执行 Sprint archive

#### Scenario: 取消确认不改变事实源
- **WHEN** 用户在归档确认流程中点击取消或按约定关闭弹窗
- **THEN** 系统 MUST NOT 改变 Sprint、REQ、BUG、Change、验收报告或 Workflow Sync 状态
- **AND** 页面 SHALL 保留当前迭代容量和卡片上下文

#### Scenario: 门禁失败阻断执行
- **WHEN** Sprint archive readiness 或执行前门禁发现未归档范围、验收报告未 sign-off、权限不足或 Workflow Sync 校验失败
- **THEN** 页面 SHALL 展示失败项和修复方向
- **AND** 页面 MUST NOT 展示“强制归档”或等价绕过按钮
- **AND** 失败项入口 MUST 遵守权限过滤和脱敏规则

#### Scenario: 后端门禁是最终裁判
- **WHEN** 用户确认执行归档
- **THEN** 服务端或既有治理命令 MUST 重新校验目标 Sprint、权限、未归档范围、验收 sign-off 和 Workflow Sync
- **AND** 服务端 MUST NOT 信任客户端传入的 readiness、权限、Sprint ID 或行为链路字段作为最终授权依据
- **AND** 前端自行判定通过 MUST NOT 直接写入归档结果

#### Scenario: 归档成功刷新需求中心
- **WHEN** Sprint archive 执行成功
- **AND** Workflow Sync 刷新成功
- **THEN** 需求中心 SHALL 刷新当前迭代列表、容量区域、Scope 投影和相关卡片状态
- **AND** 已归档 Sprint MUST NOT 继续伪装为当前迭代

#### Scenario: 执行或同步失败保留上下文
- **WHEN** 门禁检查、归档执行请求或 Workflow Sync 刷新失败
- **THEN** 页面 SHALL 保留当前迭代容量和卡片上下文
- **AND** 页面 SHALL 展示轻量失败信息或状态可能过期提示
- **AND** 页面 MUST NOT 清空看板、伪装归档成功或静默移除当前迭代

#### Scenario: 当前迭代归档入口 UI 验收
- **WHEN** 完成当前迭代归档入口 UI 实现
- **THEN** 验收 MUST 覆盖 1440px 桌面下的入口、禁用态、确认弹窗、门禁失败列表、权限态和成功/失败反馈
- **AND** 验收 MUST 覆盖 390px 窄屏、长 Sprint ID、多当前迭代和文本不重叠
- **AND** 验收 MUST 记录截图、computed style 或等价证据
- **AND** click outside 关闭若被支持，验收 MUST 覆盖弹窗内 `stopPropagation` 不误关闭、外部点击仍按约定关闭
