---
title: 迭代归档对象会话与命令预填设计
change_id: add-sprint-archive-chat-entry
requirement_id: REQ-0049-sprint-archive-chat-entry
created_at: '2026-10-21 18:32:37'
updated_at: '2026-10-21 18:32:37'
---

# 迭代归档对象会话与命令预填设计

## 背景与现状

REQ-0049 已评审并纳入 sprint-012，5人天。完整需求、30项AC、流程与原型位于 issues/requirements/review/REQ-0049-sprint-archive-chat-entry/。readiness 为 Partially Ready：设计输入齐全，原型运行预览因本地 URL 策略未完成；真实 Skeleton 确认和视觉证据留待实现，不伪造通过。

当前 requirement_center 服务将容量和 sign-off 纳入归档入口门禁；RequirementCenterPage 的 Sprint 动作弹窗只显示手动命令提示。governance preparation 已有对象会话选择与执行保护，relations 当前将非REQ/BUG对象按Change目录解析，需要显式分支处理 SPRINT。

## 目标与非目标

完成入口 → SPRINT 会话 → 待发送命令 → 用户发送后归档检查的闭环，保持最终权限与签署门禁。非目标：新Sprint管理页、其他Sprint命令UI、自动发送、自动签署、跨用户共享会话、重写历史成果或治理脚本通用重构。

## 设计决策

### D1：复用现有设计系统与组件

选用 DS 组件复用和局部样式对齐。原型HTML表达流程及状态，不整体移植其演示壳、模拟发送、场景选择器或模拟数据。CSS Port 整页移植会增加重复布局与样式维护；另建组件体系与当前局部增强不匹配。

### D2：入口资格与执行准入分层

服务端按授权项目加载规范 Sprint、完整 requirements/bugs/changes 与关联交付事实，复用完成状态映射，去重关联对象，未知不当作完成。非空完整范围全部完成且未归档可准备会话；已应用但未完成归档的关联Change仍阻断。容量仅展示。范围签署/最终文档和同步结果在用户发送后的执行阶段检查。

保留现有 archive_readiness 响应结构以降低客户端迁移成本，明确 can_enter_confirmation 的兼容语义为“允许准备会话”，UI 不再据字段名打开确认弹窗。reason_code 枚举补齐空范围、未知、权限等状态；sign-off 不作入口阻塞。执行期单独读取最新事实，不能复用入口缓存授权。接口文档注明兼容字段语义，后续重命名不在本范围。

### D3：SPRINT 对象与统一会话服务

保留 POST /api/v1/chat/object-sessions，action 为 sprint-archive，object_id 为规范 sprint-NNN。服务端从受信仓库根内解析 iterations/change/sprint-NNN/sprint.yaml，校验文档 ID、唯一性、状态、范围与权限；归档后现有会话只读解析可指向 iterations/archive 的唯一对应项。不能跌入Change解析分支，不能用归档事实补活动目录损坏或缺口，不跟随越界路径/符号链接。

SPRINT 主关联复用现有关系模型，明确对象类型；按当前用户、空间、仓库、类型与ID查询，保持现有只读和对象写权限。未知数据库约束先检查，优先复用文本字段；若存在枚举/索引约束则生成兼容迁移并覆盖SQLite/MySQL，不绕过约束。

先执行对象执行保护，再选会话：本人未决执行返回可访问执行入口且 can_send=false；他人占用仅给安全忙碌状态，不泄漏会话标识；未决执行不会通过新建会话规避。空闲候选排除删除/归档，按最新turn、最新消息（有值优先）、会话updated_at、created_at、ID降序。

新建和主关联使用既有事务与幂等机制；连续点击使用相同准备意图键，重试返回同一会话。不能仅使用每次点击新随机键作为并发防重复保证；以授权对象准备锁或等价事务竞争检测覆盖无会话同时创建。

### D4：导航和草稿消费

RequirementCenterPage 共用治理会话请求/导航决策，新增 Sprint 动作处理，移除该入口旧确认弹窗。准备中锁定按钮；捕获空间/仓库/Sprint身份，响应时再核对，切换项目后丢弃旧导航和预填。

后端准备返回既有 conversation_id、object_id、object_type=SPRINT、action、reused_conversation、can_send、execution_state、reason_code 等结果。仅准备，不调用发送、创建candidate/turn或启动Worker。前端根据确定目标生成完整单行命令。

待预填记录绑定项目、会话、对象与一次性意图标识。Chat 和 Composer 中唯一消费点负责填入：空值直接填、相同值不重复、不同文本保持原文并显示inline选择。用户明确填入才替换文本，附件/Skill等上下文保留；保留或填入后删除待消费意图。忙碌/待核对不注入。刷新重挂载不能重新覆盖，失败不将旧命令投向新会话。

### D5：发送后执行与结果回读

扩展命令准入、对象快照、路由和执行保护以识别 SPRINT/sprint-archive；不能只放开命令白名单而遗漏任务执行/结果消费。用户主动发送后执行既有 Sprint 归档技能，重新检查完整范围、权限、签署、文档与Workflow Sync。权限在准备和发送两端都校验。

完成证明必须关联 Sprint 与实际操作，不能仅凭模型文字、退出码或命令前缀投影 completed。中断/恢复沿用既有机制，不重复已经成功的归档副作用，不追认原失败历史。回到需求中心重新读服务端事实，刷新失败显示过期提示。真实样本使用独立可写项目，不用 sprint-012 自归档作为唯一验收。

## 原型冲突处理（Conflict Resolution）

| 事实源冲突 | 决策 |
|---|---|
| 旧规格要求容量>0、签署readiness与确认modal | 本次已评审要求优先，以 MODIFIED 完整替换旧入口需求；签署保留在执行期 |
| HTML 有模拟发送/审阅场景控件 | 仅审阅工具，不进入产品，实际只通过用户发送触发任务 |
| 原型概览未完成场景仍显示示意完成数 | 示意数据不作为状态计算，产品只使用服务端完整范围 |
| 旧Chat要求生成类动作新turn/candidate | 归档会话准备不是生成类动作；预填阶段不产生轮次，新增专项规格明确边界 |
| 新动作可能缺数据库约束/执行准入支持 | 先验证完整调用链再实现，不以跳转成功代替能力完成 |

同一业务行为优先采用用户明确确认与已评审PRD。无业务冲突时，参考视觉优先级为HTML、PNG（当前无）、context、acceptance、UI规则与旧规格；局部位置沿用附件标注。保留现有非本次能力。

## UI 契约（UI Contract）

页面范围为需求中心容量条归档入口和Chat输入保护。前后台一致性：本次无管理端改动；按钮、字体、图标、focus、提示复用前台设计token及现有组件。附件只规定位置，不复制固定Sprint/容量/数量。

容量条保留原字号、间距、图标与圆角。Chat复用Composer，命令输入可编辑。归档可用、禁用、加载、失败均有可访问名称及原因；不新增强制归档按钮。截图目标为1440×900以及768×900、390×844。所有原型数据为Mock；实现读真实API，Mock控制器与模拟结果不进入生产。

## UI 骨架（UI Skeleton）

```text
RequirementCenterPage
  当前迭代容量区域
    Sprint身份 / 容量条 / ArchiveButton / 原因提示
  prepareSprintSession（loading/error/identity guard）
ChatWorkbenchPage
  项目与SPRINT会话身份 / 历史与执行状态
  DraftConflictInline（保留 / 填入）
  Composer（文本、附件、Skill、主动发送）
```

先落结构和状态容器，接入可测selector，以真实边界替换Mock前完成首轮Skeleton确认。依赖为完整范围、权限、会话结果、执行状态、现有草稿；数据未就绪不闪现可执行状态。1440px重点是图标与容量行对齐、提示不挤压、Chat身份及命令完整；窄屏允许合理折行且不遮挡。

## UI 参考复刻契约（UI Reference Replication Contract）

保真为局部一致。组件清单：页面壳/品牌标题/指标筛选/列头空列/任务卡标签保持既有；本次变更按钮动作与Chat草稿inline区域。响应式、滚动和sticky沿用既有页面，避免新覆盖层。

| 参考锚点 | 产品/测试selector | 文件 | 状态/批次 |
|---|---|---|---|
| 附件容量条右侧图标、原型#archive | [data-testid=current-iteration-archive-action] | RequirementCenterPage.tsx | default/hover/focus/disabled/loading/error；A |
| 原型#reason | [data-testid=current-iteration-archive-summary] | RequirementCenterPage.tsx | 未完成/未知/无权；A |
| 原型#prompt | [data-testid=chat-prompt] | components/chat/Composer.tsx | empty/prefilled/existing/busy；B |
| 原型#conflict | [data-testid=sprint-archive-draft-conflict]（新增） | ChatWorkbenchPage.tsx及Chat组件 | open/closed；B |
| #keep / #replace | sprint-archive-draft-keep / sprint-archive-draft-replace（新增data-testid） | 草稿inline组件 | focus/selected；B |

| 动作按钮 | modal类型 | 组件族 | 状态与验收证据 |
|---|---|---|---|
| 归档 | N/A，直接导航 | 既有图标Button及Toast | loading/disabled/error/default；DOM、截图、请求与会话计数 |
| 保留/填入草稿 | inline-expanded | 共用Button与Inline提示 | open/closed/focus；两分支截图、输入值与意图消费 |
| Chat发送 | N/A | 既有Composer发送 | busy/idle；仅主动触发有turn与任务 |

| 采样对象 | 属性 | 期望、当前值与容差 | 证据入口 |
|---|---|---|---|
| 容量条与归档按钮 | width/height/padding/gap/color/border/radius/outline | 当前值待实现前采样；期望既有token与布局，无无关视觉变化，尺寸容差经基线确认 | evidence/acceptance/ 下截图和computed-style记录 |
| Chat输入 | font-family/font-size/line-height/white-space/overflow-wrap | 复用Composer实际基线，长命令可读且不横向溢出 | 同上，阶段B各视口 |
| 草稿提示 | background/border/gap/position/z-index | inline占位，无遮挡，无新增modal覆盖层 | 同上，冲突与关闭状态 |

不得用待采样值宣称视觉完成。批次A验证入口族；B验证输入/冲突/执行保护；C验证真实归档与刷新。1440×900覆盖全关键状态，768×900与390×844覆盖默认、禁用、草稿冲突；每批保留截图/样式及非目标无误改检查。

## 数据与 API、观测和安全

product_data_collection_observability: applicable；affected_layers: web、api、usage_events、request_logs、task_traces、task_trace_spans。依据 docs/standards/product-data-collection-observability.md。validation: REQ AC-020/021与XCUT，入口事件→准备请求→会话关联；主动发送后才有归档任务和流程节点。直接API不伪造行为事件，服务端生成request_id；客户端链路ID不作权限依据。脱敏记录对象、动作、结果、请求/会话/任务标识，不保存完整草稿、Prompt、凭证或本机路径，采集失败不阻断主流程。

OpenAPI/Orval/API索引与接口测试随准入reason_code和SPRINT类型同步。数据库默认复用关联/会话结构，实现前审计 schema 与枚举；如改动，SQLite/MySQL迁移和回滚测试、数据库设计文档同步。日志保留周期、对象存储、管理端、移动端及部署拓扑N/A：不新增其资源或策略，沿用既有规则。执行器运行版本需核对，不能将旧部署截图当新实现证据。

## 风险与回滚方案

- 现有归档执行链路不识别SPRINT：先端到端审计与测试，避免仅UI可点。新增适配超出5人天时重估Sprint，不静默扩容；当前26/30人天，缓冲13.33%。
- 同期BUG-0062修改归档冲突判定：该Change只消费既有协议，不重写条文冲突规则；合并后聚焦回归二者交界。
- 路径迁移、权限或范围变化：准备与发送两次校验，状态未知拒绝；已有会话历史仍可安全解析。
- 回退仅撤销本Change入口与能力适配，不删除新建会话、历史消息或实际归档成果；如有迁移需先验证回滚兼容。关闭入口不重放归档。

## 验证与交付边界

后端聚焦范围准入、SPRINT解析/权限、会话事务与并发、发送执行链路；前端聚焦导航竞态、一次性输入、草稿保护和忙碌分支。正式30项AC逐条映射至执行计划，保留真实UI与隔离产品轮次证据。合成回归、真实发送、视觉和部署指纹分别报告。完成后同步REQ全部子文档及原型，按opsx-accept取得ready才可按授权归档。
