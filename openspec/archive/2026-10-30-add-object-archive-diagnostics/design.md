---
title: 对象级归档查询与诊断展示设计
created_at: 2026-10-30 09:33:24
updated_at: 2026-10-30 09:33:24
---

# 对象级归档查询与诊断展示设计

## 背景

已有收尾门禁生成诊断但只抛错误码；API映射缺失，在线CLI再退化为在线服务错误。公共错误过滤未放行操作身份；Composer阻断列表仅覆盖发送失败。普通操作表已有scope_key、binding_revision、actor_id、stage、revision及manifest，无轮次精确关联。

## 目标与非目标

建立对象级单一查询入口，呈现持久操作事实、当前只读复核及当前动作资格。无数据库迁移；不保存历史失败快照、不推断轮次归属、不改变父需求部分交付策略，不扩大受控签署或用户权限。

## 决策

采用原操作查询为权威视图，现有工具完成/轮次变化只提示刷新。替代方案为新增专用事件，但事件会丢失或截断且不能反映文档修正，第一批不采用。

### API与兼容

拟新增GET /api/v1/chat/archive-operations，参数space_id、repository_id、object_id；实现前核对现有路由冲突。返回object_id、object_type、association_scope=current_object、operations与summary。每个operation包含operation_id、operation_kind、target_id、stage、revision、verification及allowed_actions/denial_reason。verification包含status、checked_at、input_fingerprint、findings；finding包含reason_code、kind、relative_path、line、message及需复核标志。无记录返回空操作和明确not_started，不生成虚拟ID。

保留现有成功响应与409错误语义，安全诊断字段增量兼容；未知异常仍脱敏兜底。同步API schema、公开错误过滤、OpenAPI、Orval及文档。字段不返回manifest、签名、围栏令牌、正文或本机路径；限定列表数量和文本长度。查询不改变治理文件、操作阶段、锁或租约；既有请求审计独立处理。

### 对象关联与一致性

服务端先验证项目和对象访问，再解析Change唯一原操作；REQ/BUG返回当前可信关联集合；Sprint关闭操作与子Change分开。历史受控操作通过提案关联解析。冲突阻断，不按时间选择最新。提取并复用archive_dispatch解析规则，不调用执行函数实现查询。当前关联集合不能冒充历史请求范围。读取期间对象绑定、操作revision或文件输入变化则返回stale，不报告通过；不持有长时间写锁扫描。

### 当前事实与授权

stage是已提交检查点，不证明进程仍活跃；活跃性不能确认时禁止并发恢复。verification是当前复核，不覆盖completed历史。无操作不得续接；已完成仅提供重新核验。未完成操作在用户明确触发后，经原执行入口重验项目权限、操作者、绑定版本、原操作身份、项目锁/围栏、验收与恢复历史。前端allowed_actions不是授权凭证，权限变化即时拒绝。多Change逐项执行，不创建新操作替代原操作。

### 前端状态与动作

复用ArchiveBlockers问题列表；在当前对象归档状态区域接入查询，不把卡片伪称为某轮结果。支持not_started、执行中、未完成阻断、可续接、completed且复核通过、completed但复核失败、review、stale/unavailable、forbidden及多操作部分完成。查看问题/刷新只读；续接显式确认；保留草稿；忙碌禁用重复提交。事件只使缓存失效，打开页面、重连、手动刷新也查询。合并请求、取消过期查询，旧响应不得覆盖新状态。

组件动作矩阵：问题列表→展开详情；刷新→只读请求；继续原操作→确认对话框→执行→重新查询；已完成→重新核验。实施前完成UI Contract、selector映射和骨架确认，覆盖桌面1440px与窄视口、焦点/键盘、长路径、错误与加载状态；无新增附件参考稿。

## 影响与可观测性

product_data_collection_observability: applicable；affected_layers: API、Web、请求封装、归档治理。复用现有request_id/审计，显式恢复点击与自动刷新分开，不伪造行为事件；诊断和遥测都不授予权限。验证脱敏和遥测降级。DB schema、对象存储、移动端、管理端独立页面不变。

## 风险与迁移

诊断扫描成本→按对象聚焦、关键时机刷新与请求合并；并发变化→输入指纹与版本复读；页面旧结果→请求序号隔离。后端先增量部署、旧客户端保持可用，前端再启用；回退前端不撤销已提交操作或放宽后端门禁。可信工具部署按现有标准流程，不能通过可写工具或替身宣称真实产品通过。

## 实施前置与开放项

依赖fix-archive-finalization-consistency已验证的共享检查器；实施前纳入Sprint并复核容量。隔离验收环境、登录身份、故障注入检查点须登记；真实归档或服务中断不由提案自动授权。暂未确定的环境信息应在执行前落实，不伪造产品证据。


## 实施 UI Contract 与骨架

用户确认主对象归档区放在执行详情侧栏顶部、轮次详情之前，与输入草稿和轮次结果独立。复用现有 ChatDialog；样式采用细边框、6px圆角、14px正文与近直角按钮，1440px及窄视口检查换行、焦点和长路径。截图附件只作问题来源，不要求复刻 Codex 交互卡片。

| 动作 | 组件与 selector | 状态 / 证据 |
|---|---|---|
| 查看问题 | object-archive-operation 内 details/summary | 展开/收起，无写入 |
| 刷新状态 | object-archive-refresh | 加载、失败、禁用；只读查询 |
| 继续原操作 | object-archive-resume → object-archive-confirm（ChatDialog） | 显式确认、取消、忙碌；服务端重新授权 |
| 页面区域 | object-archive-panel | 空、加载、阻断、完成、过期、权限失效 |

骨架为无请求、按钮禁用的示例，不计真实产品验收；证据 evidence/ui/skeleton-1440.png。首轮用户已明确选择执行详情侧栏，按该位置实施。采样 padding、border、font-size、width、overflow；实现后的测试和截图分别保留，禁止以骨架冒充产品完成。


## 实施定稿

GET `/api/v1/chat/archive-operations` 使用当前主对象关联查询；POST `/api/v1/chat/archive-operations/resume` 仅接收单个目标与原 operation_id。无记录通过 not_started_targets 表示，不创建操作。现有执行成功结构保持兼容，新增诊断只包含允许的相对路径、行号、分类及安全提示。

查询通过共享解析器区分普通与受控操作，Sprint 同时返回自身关闭与子 Change 操作。复核前后比较输入、操作 revision 和检查结果；不稳定结果为 stale。恢复资格只作提示，通过既有 OS 围栏的只读非阻塞探测核对占用，实际执行再次获取锁并验证原身份、当前权限与历史。lease 时间或阶段不作为进程存活证明。

执行详情从原中间轨迹容器调整为右侧栏；中间对话与草稿保持挂载。窄屏使用右侧全宽抽屉，提供关闭入口。对象信息位于轮次详情之前，明确当前对象与所选轮次不同，不解析工具正文决定状态或授权。

数据库和持久字段无变化，部分交付策略无变化。API 文档、OpenAPI、生成客户端与两种请求错误封装已同步。部署沿用现有后端与 Web 发布方式，无新增配置项。
