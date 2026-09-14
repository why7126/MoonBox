---
change_id: add-chat-workbench-codex
created_at: 2026-09-08 12:13:33
updated_at: 2026-09-11 09:06:21
---

## 背景与约束

来源 REQ-0025-chat-workbench，已 approved 并纳入 sprint-004，当前 in_sprint。PRD、13 条故事、34 条功能 AC、8 条横切 AC 和8条原型 AC齐全；Readiness 为 Partially Ready，目标截图和接入验证不是已经完成的事实。

现有 React/Vite Web、FastAPI后端和SQLite/MySQL可复用。需求中心导航未提供独立Chat路由，AI抽屉是固定反馈。新增能力按两份 delta spec 定义；不重写既有需求中心抽屉、卡片阶段动作及人工/系统文档权限。

## 目标与非目标

目标：个人会话持续执行、真实事件与Diff、可恢复和受限中止、平台额度与容量控制。非目标：自研Agent循环、TASK状态机、本机执行桥、个人账号绑定、附件、共享会话和默认Git发布操作。范围详情引用来源PRD第3节。

## 设计决策

### D1 复用 Ops 设计系统

采用DS组件与共享Token实现，依据用户已确认的风格迁移，无需再次选择CSS Port。原稿CSS不整段移植到全局样式；保留参考区域与交互。CSS Port会引入紫色渐变、残余任务样式与现有组件冲突；纯截图资产不能实现状态和可访问性。

### D2 服务端执行适配

采用API服务＋独立执行worker，浏览器只访问MoonBox鉴权接口。优先验证Python SDK/App Server，CLI JSONL仅在前者不能满足已承诺能力时作为备选；实施第一阶段固定单一路线、版本及协议事件，不同时生产化两套适配。具体版本不能凭文档推定为验证通过。

适配边界为start/resume、start_turn、interrupt、query/reconcile与事件归一化。worker持有执行会话映射，客户端不能指定任意宿主机目录或命令。首次无Codex标识失败保留未连接会话。运行端缺少查询能力时需由worker持久化执行事实补足；无法确认原执行终止保持unknown，不能以新执行代替恢复。

平台统一服务端认证与费用承担。凭证由受控进程或代理使用，不能直接暴露给仓库测试脚本环境；不复制宿主个人认证目录作为多租户方案。容器/worktree/进程隔离的具体组合在接入前验证，单独worktree不构成网络、端口、数据库和凭证隔离。

### D3 业务存储与互斥

候选表如下，最终字段通过迁移与API模型统一；不创建TASK或AgentRun树。

| 表 | 核心事实与索引 |
|---|---|
| chat_conversations | owner_id、space_id、repository_id、workspace_id、codex_thread_id、title、pinned、archived_at、deleted_at、last_activity_at；用户空间与最近活动索引 |
| chat_turns | conversation_id、client_request_id、status、retry_of、执行端轮次标识、worker fencing generation、开始/结束时间；会话+请求幂等唯一约束 |
| chat_messages | conversation_id、turn_id、role、受控正文与时间；会话读取顺序索引 |
| chat_context_snapshots | turn_id、对象类型/标识/版本、受控内容或快照引用；读取时再次授权 |
| chat_events | turn_id、本地递增序号、原事件标识/类型、脱敏载荷；作用域去重键与断点读取索引 |
| chat_diff_snapshots | turn_id、前后基准标识、文件元数据和受控Diff；本轮与累计基准分开 |
| chat_execution_locks | conversation_id唯一、worker generation、租约与状态；租约过期不等于旧进程已终止 |
| chat_usage_reservations | 用户/空间预算、存储预留与结算关联；原子预留/释放与幂等结算 |

同会话互斥覆盖连接、排队、运行、停止中和未知；数据库事务与唯一约束防双标签重入。MySQL可使用行锁，SQLite用兼容事务和条件更新；不依赖仅某数据库支持的部分索引。旧worker被fencing隔离后仍须确认外部进程结束，才能允许新代码写入。

上下文撤权不能仅隐藏引用chip：历史回复或Diff若可能包含被撤权原文，需限制对应轮次内容；执行端历史上下文不能可靠剔除时禁止继续原线程并引导创建干净会话，不把撤权对象残留在下一轮Codex上下文。

### D4 API与事件传输

所有请求使用既有前台登录令牌，服务端同时核验owner、space和对象权限。路由候选如下；普通响应沿用ApiResponse，错误码在项目错误码表分配，不在设计中虚构已存在编号。

| 接口 | 语义 |
|---|---|
| GET/POST /api/v1/chat/conversations | 分页搜索本人当前空间会话/创建，仓库从授权配置选择 |
| GET/PATCH/DELETE /api/v1/chat/conversations/{id} | 查看、标题/置顶/归档/恢复、受限删除 |
| PUT /api/v1/chat/conversations/{id}/relations | 至多一个主对象和多个引用，保存时校验 |
| POST /api/v1/chat/conversations/{id}/turns | 输入+client_request_id；事务预留和排队，重复返回原轮次 |
| GET /api/v1/chat/conversations/{id}/turns | 轮次历史与当前运行，分页 |
| GET /api/v1/chat/turns/{id} | 查询真实状态、引用快照访问边界及恢复结果 |
| POST /api/v1/chat/turns/{id}/interrupt | 接受停止请求，不立即返回已停止 |
| POST /api/v1/chat/turns/{id}/retries | 明确终止后新轮次，关联retry_of并重验快照权限 |
| GET /api/v1/chat/turns/{id}/events?after=序号 | 游标读取/恢复事件流，过滤原文敏感字段 |
| GET /api/v1/chat/turns/{id}/diff | 可信基准、文件差异，支持大内容边界 |

实时展示采用fetch读取SSE格式流以携带Authorization，不把凭证放URL或无鉴权EventSource。OpenAPI声明流式媒体类型，专用流解析器与普通生成客户端分开；重连按游标重放已落盘事件。超时/断连只改变连接状态，不伪造运行失败。错误至少区分无权、仓库不可用、运行冲突、状态未知、额度不足、容量不足、基准不可用。

### D5 执行、Diff和重试

每会话复用独立代码工作区与分支，不逐消息建分支。启动前记录可信工作区内容基准，结束后计算本轮差异；未跟踪文件、删除、重命名与二进制均有元数据，不只比较HEAD。限制路径逃逸与符号链接越界。大Diff可截断展示但保持准确元数据与原因，不能伪造可读内容。

状态机：connecting/queued/running → stopping → stopped，或completed/failed；断连/中止超时进入unknown，恢复可信状态后更新。终态按执行端确认，前端计时器不得决定终态。手动重试复用原输入和仍有权访问的原快照，改用最新内容需新输入；重试不自动进行。

### D6 额度、容量和删除

平台按用户/空间计量，先检查预算、并发与存储预留，再启动。未配置必要限额时服务返回未就绪，不视为无限额度。预算、容量数值及结算周期为RC-002设计配置项，在开放执行前填写配置表并验证；不得用默认任意数值冒充产品确认。

聊天、引用快照与历史Diff保留至主动删除，无90/180天到期清理；归档只读保留。满额停止新增并保留查看/清理。先预留运行结果空间；超出预留时暂停或请求中止并保留已落盘内容，不能静默丢弃或无限写满磁盘，具体边界在真实运行验证中固定。

删除先确认没有活动/未知运行和未处理代码变更，逻辑隐藏与主存储物理清理、执行端副本清理、备份到期分别记录清理状态。备份删除时限和执行端可删除能力未验证时不得宣称彻底删除。代码独立保存，审计沿用观测标准保留。恢复备份应重放删除标记，避免恢复已删除历史。

## Conflict Resolution

| 参考差异 | 目标处理 | 规格承接 |
|---|---|---|
| 紫色/渐变/大圆角 | 用户已确认优先用Ops Token与共享组件 | 新增工作台视觉契约 |
| stopTurn立即停止 | 增加停止中与终止确认 | 新增运行状态要求 |
| 断连立即失败重试 | unknown先查询旧运行 | 新增恢复重试要求 |
| 历史文件计数禁止删除 | 检查当前未处理变更 | 新增历史保留要求 |
| refs只有ID | 受控版本/内容快照和授权 | 新增上下文要求 |
| 选历史后失去停止入口 | 当前运行独立停止入口 | 新增执行呈现要求 |
| 演示结果与人员信息 | 正式页面不显示 | 新增Mock边界要求 |

来源是尚未生效的参考HTML，不是已有业务规格；使用ADDED Requirements表达新的正式行为，无需删除或篡改openspec/specs中的现有要求。UI优先级为用户已确认选择 > 来源PRD及评审 > Ops视觉规范（样式）/附件（布局），不能用技能默认HTML优先级推翻用户选择。

## UI Contract

主路由拟定 /chat，查询参数仅提供已授权对象定位提示，不作为授权依据。现有需求中心导航接通该路由；保留原AI抽屉，并为其增加“在Chat工作台继续”显式入口，携带对象标识，用户选择已有会话或新建个人会话，不自动迁移旧模拟消息或运行任何代码。此为RC-003的设计收敛，不新增第二套执行后端。

布局复用现有导航宽度，右侧详情桌面398px作为初始目标，主内容flex可收缩；1440×900下导航、输入、当前停止和消息/详情滚动均可达。主题取共享Token：深色背景#0A0D14/主强调#D8AC55；浅色#F4F6FA/#B9832E，圆角不超过8px，正文Inter+Noto Sans SC，编号等宽。不能复制原稿品牌和四项导航覆盖现有八项。

前后台一致性checklist：品牌位图、导航密度和active态、用户菜单、空间切换、图标尺寸、主次按钮、危险色、fixed toast、浮层层级与关闭行为。截图、computed style、空态/错误/只读/满额/未知状态共同验收，具体字体尺寸和容差以现有共享组件采样基线冻结。

## UI Skeleton

候选实现入口：src/web/src/pages/catalog/ChatWorkbenchPage.tsx，组件目录src/web/src/components/chat/。结构为ChatShell → SessionBar/RelationsBar/Conversation/Composer/ExecutionPanel，覆盖全局HistoryDialog、RelationsDialog、RenameDialog、DeleteConfirm、StopConfirm、Toast与当前运行状态容器。

先实现路由壳、区域插槽、空/运行/错误/未知状态容器、稳定选择器与明确标注的开发占位数据；1440px Skeleton首轮确认后才进入各组件细节。页面壳不能启动模型或显示伪造成功。真实API未接入时只显示未连接；占位数据不进入生产。

## UI Reference Replication Contract

保真模式为风格迁移；来源为需求目录prototype/web/prototype.html与context.md，已完成静态反向工程。页面壳、标题、会话过滤、关联、空态、消息、输入、执行栏、Diff、动作和浮层全部纳入。指标卡/看板列/任务树不适用，因为首版不包含这些组件。



目标 data-testid 是候选合同名，尚未创建产品组件。所有证据列均为后续验收计划。

| 动作/组件 | modal 类型 | 参考 selector | 目标候选 data-testid | 状态 | 验收证据计划 |
|---|---|---|---|---|---|
| 切换会话 | popover | #sessionPicker / #sessionPopover | chat-session-picker / chat-session-popover | open/search/empty/selected | 截图、焦点、外部点击 |
| 历史管理 | dialog | #historyBtn / #accessModal | chat-history-trigger / chat-history-dialog | filter/empty/archived | 截图、查询与权限断言 |
| 新建 | N/A | #newSessionBtn | chat-new-session | loading/error/empty | 新建唯一性与空态 |
| 重命名 | dialog | 动态历史行按钮 / #accessModal | chat-rename-trigger / chat-rename-dialog | dirty/invalid/submitting | 输入、取消、toast |
| 删除 | confirm | 动态历史行按钮 / #accessModal | chat-delete-trigger / chat-delete-confirm | disabled/open/cancel/error | 未处理变更与竞争断言 |
| 归档/恢复 | N/A | 动态历史行按钮 | chat-archive / chat-restore | disabled/loading/readonly | 状态及权限断言 |
| 关联管理/引用 | dialog | #manageRelations / #contextBtn / #accessModal | chat-relations-trigger / chat-relations-dialog | empty/multiple/forbidden | 主对象约束、快照断言 |
| 发送 | N/A | #prompt / #sendBtn | chat-prompt / chat-send | draft/disabled/sending | 幂等、失败草稿 |
| 停止当前运行 | confirm | #stopBtn / #accessModal | chat-stop-current / chat-stop-confirm | running/stopping/unknown | 终态事件与截图 |
| 重试 | N/A | #retryBtn | chat-retry | allowed/disabled/unknown | 原运行终止、快照断言 |
| 轮次选择 | select | #turnSelect | chat-turn-select | empty/history/current | 选历史仍可停当前运行 |
| 事件与 Diff | inline-expanded | #executionBody / [data-tab] | chat-execution-events / chat-diff | empty/text/large/error | 真实事件、双轮 Diff |
| 执行栏折叠/主题 | N/A | #panelBtn / #themeBtn | chat-panel-toggle / chat-theme-toggle | collapsed/dark/light | 窄视口、深浅截图 |
| 关闭/确认/取消 | dialog 共用 | #closeModal / #modalActions | chat-modal-close / chat-modal-submit / chat-modal-cancel | focus/loading/error | Esc、Tab、焦点回归 |

按钮、Modal、Confirm、Popover、Toast 按动作族复用；不逐个按钮建立互不一致组件。关闭契约：会话轻量选择即时应用并关闭；关联和重命名采用提交/取消，不静默保存未提交输入。危险确认取消不改变运行。浮层外部关闭需通过 capture 阶段或等价机制覆盖内部 stopPropagation；对有草稿的编辑弹窗明确保留/丢弃语义后验收。


### 目标组件文件映射

所有候选data-testid同时是实现与测试selector，采用[data-testid="名称"]定位。

| 动作族 | 文件（均位于src/web/src/components/chat/） | 批次 |
|---|---|---|
| 会话选择、新建、历史、重命名、归档、删除 | SessionBar.tsx、HistoryDialog.tsx、SessionActions.tsx | 2 |
| 关联与引用 | RelationsBar.tsx、RelationsDialog.tsx | 2 |
| 输入、发送、额度容量反馈 | Composer.tsx、ChatStatus.tsx | 3 |
| 当前停止、重试、轮次、事件与Diff | ExecutionPanel.tsx、RunActions.tsx、DiffView.tsx | 4 |
| 共用浮层与反馈 | ChatOverlays.tsx，优先复用既有DS primitive | 2–4 |

这些是设计路径，不表示文件已经存在；实现可聚合文件，但需同步selector映射与设计，不改变动作契约。

### Computed style采样与分批实现

| 批次/页面 | selector | 视口与状态 | 属性/期望 | 当前值与容差 | 证据 |
|---|---|---|---|---|---|
| 1 页面壳 | chat-shell/chat-execution-panel | 1440×900深浅 | grid/width/height/overflow；DS导航，右栏398px初值 | 未实现；尺寸±1px，最终Skeleton冻结 | evidence/ui/batch-1 |
| 2 历史/关联/确认 | chat-history-dialog/chat-relations-dialog/chat-stop-confirm | 1440×900、1024×600 | width/padding/gap/border/z-index；DS弹窗且低视口滚动可达 | 未实现；尺寸±1px，无遮挡容差 | evidence/ui/batch-2 |
| 3 输入和toast | chat-prompt/chat-send/chat-toast | 草稿/错误/满额 | font-family/size/line-height/color/position；Token一致，toast不位移 | 未实现；色值精确，布局位移0 | evidence/ui/batch-3 |
| 4 执行和Diff | chat-stop-current/chat-diff/chat-turn-select | 运行/未知/空/大内容 | overflow/width/font-size；停止始终可达 | 未实现；不能裁切关键动作 | evidence/ui/batch-4 |
| 5 窄视口 | chat-shell及全部浮层 | 390×844，键盘/触控 | position/max-height/overflow；详情抽屉可收起 | 未实现；无不可达内容 | evidence/ui/batch-5 |

首次实现前采样既有DS作为具体字体/间距基线；不根据原HTML任意字号猜测。每批记录期望、实际、pass/fail和非目标未改，截图与JSON路径只是计划，尚未创建证据。所有动作族统一实现loading/disabled/error/focus、提交反馈及取消。外部点击关闭采用capture阶段或等价机制，覆盖内部stopPropagation；编辑草稿关闭明确放弃或保留，不静默提交。Esc、Tab焦点限制与返回触发器纳入测试。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers: [web_request_wrapper, api, db, usage_events, request_logs, task_traces, task_trace_spans]
  reason: "会话写入、长耗时执行、额度容量、停止和恢复涉及业务请求、外部依赖与执行链路。"
  validation: "计划覆盖AC-029/030及权限、恢复和容量测试；本次仅设计与规格校验，真实采集未实现。"
```

依据docs/standards/product-data-collection-observability.md。通用request_logs/usage_events持久化不可假定现有系统已完整具备；实施先盘点实际表/中间件，缺少本能力必需链路时在本Change最小范围内补齐并测试，不虚构已采集。保留原执行事件标识不等于原样保存包含敏感内容的事件载荷。

行为只记稳定事件名、结果和关联标识，不记录Prompt/完整回复/Diff；服务端可信request_id独立生成，Task Trace按轮次关联。采集失败保留脱敏降级摘要但不阻断主业务。普通历史查询仅请求日志，不创建长任务链路。无附件上传与管理端新页面，相关采集N/A；不使用对象存储承载附件，本版业务快照默认受控数据库存储，若改变存储方案先同步边界。

API同步OpenAPI媒体类型与错误、Orval配置/客户端、docs/03-api-index.md和集成测试。DB同步SQLite/MySQL schema、迁移与docs/04-database-design.md。知识库承接来源REQ trace中的4份文档，重点AC-XCUT-001至008、AC-PROTOTYPE-001至008。

## 风险与权衡

- [版本/中止恢复能力未验证] → RC-001在细节开发前验证；不支持承诺能力时调整路线并重估，而不是隐藏核心功能。
- [仅剩2人天缓冲，排期紧] → 沿用13人天估算，不重复计算两份spec；上浮重跑Sprint容量门禁，不无声扩容。
- [数据库锁不能杀死旧进程] → 明确worker generation与终态确认，未知状态保持禁止新写入。
- [撤权后Codex历史残留敏感上下文] → 对受影响会话禁止续用或建立经权限过滤的新会话，不只过滤新引用。
- [长历史/输出耗尽存储] → 原子预留、限额、明确超限处置；备份与执行端副本删除单独验证。
- [任意代码执行危及宿主] → 隔离和凭证代理、仓库白名单、权限与治理门禁；无法验证时保持执行禁用。

## 迁移与回退计划

1. 增量迁移Chat表/索引与必要观测结构，验证SQLite/MySQL；不改现有需求中心状态。
2. 部署独立worker和版本固定的执行端、受控仓库挂载与平台认证；默认执行禁用，配置与最小真实链路通过后开放。
3. 接通API/客户端与Ops页面，灰度至受控测试空间，验证两轮Diff、中止恢复与权限；无生产凭证写入本仓库。
4. 回退先禁止新提交，协调停止或等待现有执行并保留数据/工作区，再回退应用；不自动删除Chat表或恢复生产数据库。数据库恢复与正式生产操作另按发布升级计划执行。

## 待验证事项

RC-002具体预算/并发/容量数值、结果预留与副本删除时限需在开放服务前冻结；SDK和运行时版本、执行端清理能力需真实验证。RC-003已选择保留旧抽屉并增加显式Chat入口；RC-004截图与样式验收尚未开始。以上在tasks中给出前置门禁，不把待验证结果写成完成。


## 首轮实施与采样结论

接入验证路线固定为Codex App Server stdio，候选运行时codex-cli 0.153.4。已导出本地协议schema，在独立临时CODEX_HOME下执行initialize、account/read、thread/start（read-only、ephemeral、approvalPolicy=never）。无平台账号、未启动模型轮次，不能据此关闭RC-001。Python SDK未安装，本轮不引入第二套适配；隔离worker须验证同版本。

FastAPI尚无Chat路由，SQLAlchemy支持SQLite/MySQL；部署未发现独立Codex worker。Docker daemon 29.4.0可用，仅代表容器运行时可访问，不代表跨会话网络、凭证隔离已验证。

Skeleton聚合在ChatWorkbenchPage.tsx、ChatStatus.tsx、chat-workbench.css。直接/chat沿用登录门禁；无API请求、模型调用、创建/发送/停止副作用。导航入口与旧抽屉尚未修改。桌面224px侧栏、398px执行栏，窄屏56px侧栏。底部暂显示私有性说明，账号/空间动作仍待真实数据阶段。

DS采样见evidence/ui/ds-baseline.json。字体Inter/Noto Sans SC；既有DS预览按钮为13.3333px、padding 1px 6px、圆角8px。Chat沿用需求中心13px正文/1.45行高，按钮4px、输入8px圆角，扩大可点击内边距；不继承预览页浏览器默认padding。实际值见skeleton-computed.json。本轮仅batch-1，细节组件路径仍为候选。

RC-002建议值已询问用户但未确认：用户/空间并发1/2，月Token总预算200万/1000万，历史100MiB/1GiB，每轮预留10MiB，主存储及执行副本24小时、备份最长30天。仅为待确认建议，未写入执行配置或作为上线授权。


## 第二批实现映射与验证边界

会话动作族实际落在`SessionDialogs.tsx`，共用`ChatDialog.tsx`的capture外部关闭、Esc、焦点限制与忙碌门禁；数据状态位于`useChatWorkbench.ts`。历史、重命名、新建、删除、快速切换沿用既定testid，关联动作族已实现RelationsBar/RelationsDialog；保存只影响下一轮，取消丢弃草稿。执行详情由`ExecutionPanel.tsx`读取授权轮次、事件和Diff，消息由`ConversationMessages.tsx`分页读取，SafeMarkdown仅渲染安全子集、不执行HTML；DiffView支持本轮/累计、重命名、二进制/大文件元数据；ExecutionPanel展示不可变引用快照和停止确认。

固定顺序更新usage_accounts与usage_reservations提供内部入队/结算事务，active_turn_id/generation承载锁及fencing，不额外创建重复锁事实源。尚未从POST turns开放调用内部入队，因为模型worker、授权快照及硬容量中止仍未验证。

会话动作族1440深浅、1024低视口及390窄屏截图和computed样式见evidence/session-ui。浏览器场景仅拦截合成API数据；实际部署登录态另行确认空间读取、历史空列表与无仓库门禁，两类证据不互相替代。任务3.2可完成，其余大项保留未完成子能力。


执行增量落地：工作区基准由workspace_baselines保存，active_turn_id/generation继续作为唯一锁事实源。App Server适配固定0.153.4，中止不阻塞等待ACK，终态必须匹配线程及轮次；工作区副本只导入提交树，新建独立未提交分支，不自动提交/推送。可信快照以dir-fd/O_NOFOLLOW读取，符号链接不跟随、硬链接/特殊文件拒绝。该文件边界不是凭证/网络容器隔离，真实平台入口保持关闭。


用户最新决策（2026-09-08）：先完成开发与隔离验证，暂不配置正式限额和删除时限。RC-002保持开放，生产配置为空；测试数值仅存在合成环境。当前业务和观测实现见trace连续apply检查点；平台专用认证、执行副本真正删除、独立墓碑恢复及正式容量验收仍是待验证门禁。

## 共享侧边栏补充合同（2026-09-08）

用户确认以需求中心既有侧边栏为局部一致性基线。已确认根因：Chat 独立导航结构缺少分组、版本、折叠和用户菜单；chat-shell 通用按钮规则覆盖共享样式。提取 WorkbenchSidebar 与账号/空间动作族，两页使用同一品牌、导航、权限判断、主题偏好和浮层；私有会话说明留在会话区。需求中心看板、原 AI 抽屉和执行后端不在本批修改范围。

| 动作 | 浮层/selector | 状态与验收 |
|---|---|---|
| 折叠/展开 | 无 / .rc-collapse | 深浅主题、1440/1024/390，图标与品牌可达 |
| 用户头像 | menu / .rc-user-trigger、.rc-user-menu | 展开/折叠均可打开，外部点击/Esc关闭、焦点返回 |
| 切换空间 | popover / .rc-space-popover | 加载/空/错误/只读/当前空间；仅使用授权返回值 |
| 个人资料/修改密码 | dialog / .rc-profile-modal、既有密码弹窗 | 打开、取消、错误及原鉴权接口保持 |
| 设置/创建空间 | dialog / .rc-space-settings、.rc-space-application | 管理权限可见性、取消、低视口滚动 |
| 主题/后台/退出 | switch/导航 / #themeSwitch、用户菜单 | 偏好持久化、权限过滤、会话清理 |

实施批次：共享结构及控制器 → 两页接入与CSS作用域 → 交互和双页样式回归。采样 .rc-sidebar、.rc-brand、.rc-nav-group-label、.rc-nav-item、.rc-nav-icon、.rc-user-trigger 的宽高、padding、gap、字体、行高、颜色、边框、背景和overflow；同状态两页相同，几何容差1px。新增证据保存 evidence/sidebar-ui/，旧全页截图不再证明当前侧边栏一致性。生产复用现有鉴权API；自动视觉验收用合成账号空间及API响应，不启动模型。

本批 product_data_collection_observability: status=not_applicable；affected_layers=[]。只提取现有前端账号/空间动作及样式，复用原鉴权请求语义；不改变 API/DB、request_logs、usage_events、Task Trace、请求封装或采集字段。validation：两页权限和请求回归、主题与菜单交互、computed style对照。

## 本地认证真实执行验证（2026-09-08）

用户授权本地Codex凭证与受控测试仓库，用于真实执行验证；此前平台专用认证未提供不再阻塞本地验证。正式共享部署认证、限额及删除时限仍未配置。仅建立可丢弃仓库、独立测试DB、显式测试额度和独立Codex运行目录；凭证不写入仓库、日志或受治理证据。认证进程和仓库工具使用不同权限边界，先以合成哨兵验证读取隔离，再验证真实双轮修改、恢复、停止及事件/Diff。

本地Codex版本0.153.4，通过其实际生成协议核实named permissions profile，不能仅靠workspace-write宣称凭证读取受限。本批运行证据明确区分原生macOS执行隔离和Docker合成容器探针，不把任何一种等同正式多用户Linux部署认证完成。观测承接原applicable声明，affected_layers=[api,db,request_logs,task_traces]；测试采用合成身份和业务目录，验证持久化轮次、Diff、终态及保留预算，证据不含Prompt全文或凭证内容。


## 五步隔离验证实施合同（2026-09-08）

用户授权完成用量处理、常驻worker、受限网页入口、真实网页验收和清理。本批仅在显式isolated-test环境、独立临时SQLite、有效期内的私有测试配置、指定账号/空间/仓库及活跃worker下允许入队；原平台环境仍关闭。API与静态Web同源且仅监听回环地址，沿用真实登录、所有者/空间/对象鉴权，不使用身份覆盖或业务响应Mock。worker工作区从合成种子仓库建立，绝不接受浏览器路径；临时认证在模型工具读范围外，原生权限读写每轮重新选择。配置与工作目录由测试启动器创建，最终停止子进程并清理全部临时数据。

用量事件按线程和轮次匹配，累计值单调去重；终态后增加有界用量接收窗口。以持久化可信用量记录支持幂等补结算；没有权威用量继续待对账，不伪造零值。worker重启只接收queued任务，unknown原轮次只查询、不自动重放。窗口和故障恢复通过单元测试及真实网页执行交叉验证。

product_data_collection_observability：status=applicable，affected_layers=[usage_events,request_logs,task_traces,task_trace_spans]；reason=真实发送与后台执行恢复及用量持久化语义变化；validation=计划覆盖真实登录/发送/中止/权限、可信请求ID、事件重放、用量去重与脱敏。API字段不新增，能力状态及发送行为变更同步API索引；无DB表字段变更，同步持久化语义；UI布局沿用已验收共享组件，仅补真实API交互截图。

门禁：Sprint inclusion=pass；Cross-cutting tags无admin-*，承接AC-XCUT与原型既有合同，PROCEED；本批不修改页面布局，原型验收补真实交互证据。生产认证、正式限额和副本删除时限仍按用户决定暂缓，不据隔离测试关闭整体上线门禁。

## 异常恢复、清理与兼容性补验（2026-09-09）

用户授权连续完成异常恢复、用量与清理、部署兼容性及完整验收。本批先以受控子进程建立worker强制退出/执行端断连证据：App Server由独立守护进程持有，worker死亡或协议进程退出时清理其专属进程组；终态仍以执行端确认或原轮次查询为准，不因进程清理推断模型用量或自动重放。新增副本清理适配只作用于独立会话执行历史目录，保留认证与代码；无法验证备份或副本归属时保持pending。失败重试幂等，不以到期时间代替物理删除证据。

兼容性使用独立MySQL测试容器与合成数据，真实密码随机生成仅存临时配置；不使用其他项目数据库。Docker隔离探针与平台模型运行分别记录。product_data_collection_observability：status=applicable；affected_layers=[request_logs,task_traces,task_trace_spans]；reason=恢复和清理持久化语义及工作进程生命周期变化；validation=计划验证故障恢复、未知用量保留、清理重试、SQLite/MySQL及隔离部署，API字段变化时同步OpenAPI。Cross-cutting承接既有AC-XCUT，无新增UI动作族，PROCEED。正式运营配置继续暂缓。


## 推荐组合实施合同（2026-09-09）

用户选择当前验证采用一致性本地备份＋每会话独立执行容器。首版正式方向为独立对象存储备份＋每会话容器；本批不连接真实备份桶，不设正式限额或删除时限。备份模块通过SQLite在线备份生成独立副本；删除日志独立于恢复目标保存且先于主存储删除落盘。恢复仅生成新的离线文件，核验备份清单与摘要，应用最新删除记录及运行状态隔离后才交付；缺少删除日志、校验失败或存在输出文件时拒绝恢复。日志仅存不透明会话ID和时间，不保存正文。不能以恢复过滤证明备份物理删除。

每会话独立容器使用固定Codex 0.153.4 Linux二进制、非root/只读根文件系统、资源限制、独立工作区和运行目录；只挂载该会话目录。控制进程需要模型服务网络；仓库工具通过执行端权限禁止网络、读取凭证和写入.git。真实凭证只在合成隔离探针通过后复制到临时目录，不放入镜像、环境变量或工作区。限制不满足则关闭执行，不使用privileged或全权限配置绕过。恢复复用显式线程与工作区，容器销毁不推断模型用量。

product_data_collection_observability：status=applicable；affected_layers=[db,task_traces,task_trace_spans]；reason=备份恢复删除语义与执行资源生命周期；validation=计划验证一致性备份、恢复删除重放、损坏/缺失日志拒绝、真实容器双轮及权限/停止恢复。现有UI合同承接，本批不修改UI；Cross-cutting tags无新增admin-*，PROCEED。API契约保持，正式MySQL/S3恢复不由SQLite探针替代。

实施结果：本地备份与会话容器完成，实际Linux命名空间需专用seccomp；新增构建白名单排除本机缓存/环境/认证文件。控制UID/GID取非root宿主worker身份以兼容私有bind挂载。目录、权限、资源与网络细节见src/backend/container/README.md，结果见trace.md“推荐组合落地验收”。


## 日常部署脚本接入合同（2026-09-09）

用户要求完善scripts/docker-up.sh与docker-down.sh。保留六种常规部署模式，统一根目录、env传递和Compose参数；down识别模式并保留卷数据。显式--chat-test仅支持self-storage-sqlite，使用独立回环Chat验证环境与已验证的容器执行器，不把个人凭证接入现有业务账号或生产发送。启动前检查Docker、Python依赖、认证文件、端口和已有实例；先构建镜像再启动；失败不声称就绪。测试Web从本次Web镜像导出到私有控制目录，避免要求宿主机另行构建Web。

Chat控制器使用仅当前用户可访问的Unix socket和文件锁，启动幂等；停止通过控制通道而非持久化PID杀进程，等待worker/API及临时凭证清理。stop不删除常规SQLite/MinIO数据；Chat验证会话随显式停止/一小时有效期结束清理。失联控制端拒绝覆盖状态，不自动杀不明进程。生产持久化执行和S3备份不在本批静默开启。

product_data_collection_observability：status=applicable；affected_layers=[task_traces,task_trace_spans]；reason=启动/停止执行worker生命周期；validation=计划覆盖脚本路由/env/失败退出、真实控制器启动幂等与停止清理。无API/业务DB/UI字段改变，备份与真实执行链路承接既有证据。Cross-cutting无新增admin-*，Prototype承接既有证据，PROCEED。


## 已终态轮次释放并发（2026-09-09）

用户真实网页续执行暴露：usage_unavailable时settle不执行，active_runs仍为1，已完成轮次阻止下一次发送。证据见evidence/user-browser-continuation/，并发占用根因confirmed，用量缺失原因不在本修复中臆断。

在既有任务2.4范围内将并发释放与用量结算拆分。预留表新增concurrency_released幂等标志；SQLite/MySQL重复执行增量迁移，既有settled预留标为已释放。可信终态事务内释放并发；旧版本留下的终态reserved由worker对账循环幂等修复。未知/运行/停止中继续占槽，未核实Token及容量预留保留。迟到用量结算仅更新Token/容量，不再次递减并发。

API字段/UI布局不变，无Orval重新生成。Cross-cutting无新增admin标签，UI Contract承接已有证据，PROCEED。product_data_collection_observability：status=applicable；affected_layers=[db,task_traces,task_trace_spans]；reason=终态资源与账本事务语义；validation=计划验证迁移、重复终态、迟到结算、新轮次与旧轮次竞争、未知状态保留以及真实网页停止。


## App Server进程计量范围修复（2026-09-09）

三轮真实隔离探针每轮重建App Server并恢复同一线程：各轮total与last分别同为10598、10801、11005，而不是跨进程累计。原实现用上一进程累计值相减，导致少计或新值较小时usage_unavailable；根因confirmed，旧临时测试数据已到期不能伪造回填。

每次run_claim新建独占App Server进程，唯一轮次仅采纳匹配threadId/turnId的非负total，单进程范围取单调最大值，重复不累加。历史workspace token_total不再作为扣减基线。新可信receipt标记usage_scope=app_server_process_v1；无此范围的旧receipt不得自动补结算，历史已结算记录不直接覆盖。保留缺失用量与额度预留，禁止用last单次模型调用数替代多工具轮次累计。

本批无UI或API字段变更；Cross-cutting无新增admin标签，UI合同承接，PROCEED。product_data_collection_observability：status=applicable；affected_layers=[db,task_traces,task_trace_spans]；reason=可信用量结算范围与审计证据；validation=真实三轮协议数值、跨进程降低累计值、多工具递增/重复/乱序/迟到和旧receipt拒绝自动结算。


## 单机常驻执行决策（2026-09-09）

用户明确选择单机 Docker Compose、SQLite、本地独立备份，正式凭证来源为部署机当前 Codex 登录文件。仅受信任执行控制器读取认证文件，仓库工具仍拒绝读取运行目录；不挂载整个个人 Codex 目录。源仓库及空间映射待提供，未映射前不开启该仓库发送。

用户/空间 Token、并发、存储配额显式配置为 unlimited，保持计量而不以大整数模拟无限；单会话互斥、权限、未知态、容器资源和协议消息安全边界保持。单轮 Token 预留允许显式 unlimited（内部零预留、按实际结算），结果处理仍采用独立技术缓冲边界，不等同用户存储配额。

历史不自动过期；执行副本与备份删除期限 unlimited 表示无固定时限，不是跳过主动删除。主动删除仍记录独立删除日志、即时尝试副本清理、未核实前保持 pending/retry。已有有限配置继续兼容，缺失或非法配置依旧失败关闭。

product_data_collection_observability：status=applicable；affected_layers=[db,request_logs,task_traces,task_trace_spans]；reason=显式无配额策略与常驻执行接入；validation=补充无限配额记账、互斥、删除无期限及就绪门禁测试，实际部署证据待验证回填；不新增凭证或正文日志。

## 2026-09-10 事件展示返修：附件截图逐项视觉对照表

证据：用户本轮标红附件，原图2822×1416，深色/chat，选中已完成轮次，执行详情展开；代码路径ExecutionPanel、SafeMarkdown确认根因。局部一致模式，保留Ops和原UI Skeleton。

| 附件/状态 | 对照对象与期望 | 实际/偏差 | 检查方式与selector | 处置/证据入口 |
|---|---|---|---|---|
| 附件1右侧红框 | 同一消息连续输出拼接 | 每个delta单独一行 | chat-execution-events、DOM与事件归并测试 | 本次修复；ExecutionPanel事件map直接渲染 |
| 附件1完成轮次 | 当前状态与历史分明 | 历史运行中易误认当前 | chat-turn-status、历史状态标签 | 本次修复；selectedTurn与execution.state分别展示 |
| 附件1左侧回复 | Markdown语义表格 | 管道符原样显示 | .chat-markdown table、th、td | 本次修复；SafeMarkdown无表格分支 |

组件契约：连续相邻且item_id/executor_turn_id一致的output合并，状态/工具/身份变化为边界；旧无身份事件仅按连续区段合并并说明无法恢复缺失边界。保留最近1000事件窗口提示与原始事件折叠，不能误称完整日志。重复游标按sequence去重；断序不合并。Markdown表格继承安全inline、不执行HTML/图片/非HTTP链接，表格内部横向滚动。
动作矩阵：原始事件→native details→chat-raw-events→关闭/展开→DOM及截图；停止/重试沿用既有confirm矩阵不改。样式采样：事件font-size/line-height、状态color、table border/padding/overflow；1440深浅及390窄屏。视觉采用合成事件/API，部署回归读取现有会话，不发起模型任务。

### 本次返修验证结果

8个测试文件27项通过，TypeScript及Vite生产构建通过；Web已重新构建部署。合成API搭配实际部署Web的1440/390深浅主题8张截图、computed style及无页面溢出检查通过，12个原始事件显示为5组，原始事件默认折叠/展开通过。首轮截图发现深色表格文字被全局样式覆盖，已显式继承rc-text并重新构建复验。证据：evidence/event-display/verification.json、events-dark-1440.png及同目录其余截图。附件对照三项均已修复；无新增modal，原停止/重试测试通过。

当前应用内浏览器认证失效，未读取现有真实会话；视觉数据为合成，不声称本批真实模型执行通过。数据层与执行协议未变，现有消息及事件在重新登录并刷新后使用新渲染。未请求重新登录作为修复阻塞；无发消息或模型用量。


## UI Reference Replication Contract：Harness 对话与轨迹（2026-09-11）

用户确认以本机 DeepSeek Harness 对话和轨迹为基线；参考仓库仅只读检查，不移植运行时或插件依赖。此契约覆盖原需求的回复、执行过程、历史轮次、可信 Diff，保持身份、配额、部署与保留策略。工具事件在现有 JSON payload 内向后兼容补充，接口路径、认证、表结构不变。

### 附件截图逐项视觉对照表

|编号/状态|期望|实际/偏差|检查方式与证据|处置|
|---|---|---|---|---|
|REF-DSH-01 浅色桌面对话|用户右侧气泡、无边框助手正文、紧凑输入|历史截图及源码显示双方矩形卡片、欢迎状态常驻|本轮浏览器截图与 ConversationMessages / chat-workbench.css|修复|
|REF-DSH-02 轨迹|顶部工具栏、分类行、时间线、点击详情|ExecutionPanel 为单列事件文本|本轮浏览器轨迹截图、参考 TrajectoryTable/Toolbar CSS|修复|
|REF-DSH-03 工具详情|概述、参数、结果、计时|执行采集仅有类型及阶段|实际展开详情与 execution.py 代码路径|修复，新记录采集；旧记录注明未采集|
|REF-MB-01 错误态|错误归属明确、历史状态独立|认证与服务未就绪文案混淆|用户错误截图、当前请求封装|区分状态；权限撤销清除内容|

参考原始画面含本机目录与历史会话，不复制进证据目录；保留脱敏结构摘要及实现后合成验收截图。当前只确认桌面浅色静态及历史交互；深色和窄屏以相同组件结构适配，并单独验证，不宣称参考逐像素一致。

### Selector 映射与样式采样

|参考锚点|MoonBox selector|采样/验收|
|---|---|---|
|对话/轨迹标签|.chat-view-tabs|字号、间距、底边、选中状态|
|用户消息/助手正文|.chat-message-user / .chat-message|最大宽度、对齐、背景、行高|
|底部输入|.chat-composer|宽度、圆角、padding、自动高度|
|轨迹工具栏/分类行|.chat-trajectory-toolbar / .chat-trajectory-row|sticky、overflow、行高、颜色|
|事件详情|.chat-event-detail|宽度、滚动、tab、窄屏堆叠|

参考源码采样：轨迹根 flex、min-height:0、overflow:hidden；tablePane flex:1、min-width:0、overflow-y:auto；toolbar sticky/top:0；工具按钮高20px、padding 0 7px、gap4px、12px字号。MoonBox 保留共享侧栏金色品牌，内容使用现有深浅 token，尺寸按参考结构落地。

### 动作与状态矩阵

标签/搜索/选择事件/关闭详情即时生效，无确认弹窗；工具展开不执行命令。停止沿用确认弹窗及原活动轮次锁；重试沿用原快照和幂等请求。历史、新建、关联沿用现有弹窗。运行/连接/排队/停止中/未知/完成/失败/已停止均单独标示；未知不解锁，完成不代表需求验收完成。查看历史不会将停止目标改为历史轮次。

### 数据与冲突处理

补充工具白名单参数、输出摘要、退出码、执行状态、记录时间、配对耗时与截断标记。采集前脱敏且限制大小，内容仅通过现有个人会话权限访问，不写入通用审计 metadata。缺失 Schema、模型请求层级、内部推理、缓存率不伪造；不新增模型切换、附件、分支或执行权限选择器。旧事件保持可读且标注缺失字段。时间概览默认事件顺序，有可靠耗时才使用实际时长。当前原型被用户新基线覆盖，对应原型说明同步；不改平台共享侧栏。

### 分批门禁

1. 契约和脱敏参考摘要完成后实现对话骨架及双视图。
2. 工具采集、配对、旧数据、截断、安全与停止测试通过。
3. 1440px及390px、深浅主题、轨迹详情、表格、错误/历史/运行状态截图和样式采样；记录合成 API 与真实执行边界。

product_data_collection_observability: applicable；affected_layers: Web、API事件payload、DB既有JSON、Agent执行适配；沿用现有请求日志与Task Trace，不将命令正文写入观测metadata；对象存储/新表/权限变更 N/A，因本次无变化。validation 在返修完成后回填。

参考源码版本：5dda764ed3。用户气泡参考22px圆角、10px/16px padding、默认14px/22px行高；内容宽度按MoonBox容器适配。完整参考功能（请求分层、分支、插件）未纳入当前执行端能力边界。


### 动作组件族验收映射

|动作|浮层类型|selector|状态与证据|结论|
|---|---|---|---|---|
|对话/轨迹|无|.chat-view-tabs [role=tab]|选中、切换保留；浏览器实测|复用标签族|
|工具节点/概览定位|详情分栏|.chat-trace-select / .chat-event-detail|展开、关闭、参数/结果/计时；组件测试及浏览器|实现|
|搜索/收起内容/耗时|无|.chat-trajectory-toolbar|空结果、折叠、真实计时缺失说明|实现|
|调整详情宽度|无|.chat-detail-resize|键盘可调，窄屏隐藏并堆叠|实现|
|停止当前运行|确认框|chat-stop-current / chat-stop-confirm|disabled、确认、旧目标锁定；已有回归通过|复用ChatDialog|
|重试原轮次|无|chat-retry|失败/停止可用，活动轮次禁用|保留|
|历史/新会话/关联|对话框或弹出层|chat-history-trigger / chat-new-session / RelationsBar|沿用原流程，不新增权限|保留|
|发送|无|chat-send / chat-prompt|幂等、失败草稿、Enter/Shift/IME；测试通过|实现|


## 2026-09-11 首次发送契约补充

本次是既有会话创建与发送的验收调整，不新增业务能力、权限、部署或数据库表。首次进入使用内存草稿，不创建空会话；首次发送先创建再提交轮次。创建接口增加可选client_request_id，用户与请求标识派生稳定会话ID并使用原主键约束处理竞争；旧客户端不传仍兼容。每次重放仍检查空间、仓库及会话权限；同标识不同空间或仓库冲突，删除会话不复活。轮次继续原幂等机制。失败保留草稿和创建/发送标识，已创建会话不重复创建；成功后进入历史与地址栏。

### 交互逐项对照与动作族

本轮无新增附件，使用当前源码和上一批对话证据定位交互，历史截图不作为修改后视觉通过证据。

|参考/页面状态|期望|实际及偏差|检查方式与证据入口|处置|
|/chat 无选中会话，深浅/1440及390|立即输入|Composer以无conversation禁用输入，SessionDialogs要求确认创建|Composer、SessionDialogs源码；聚焦行为测试；本批视觉证据|修复|
|新建会话|切换本地空白草稿，无弹窗|chat-new-session打开chat-new-dialog|按钮到空态、无创建请求断言|修复|
|首次发送/错误重试|同一次意图仅一个会话和轮次|会话创建无请求标识，轮次已有|后端重放/权限/冲突测试；前端丢响应测试|修复|

|动作|modal|selector|状态与验收|
|新建|无|chat-new-session|空草稿，不写DB|
|仓库选择|无，输入区select|chat-draft-repository|单仓库自动、多仓库显式选择；发送尝试后锁定，切换需新草稿|
|发送|无|chat-send / chat-prompt|可编辑与可发送分离；发送忙碌时阻止切换；失败保留；重试幂等|
|历史/重命名/删除/关联|沿用既有Dialog|既有testid|不改变权限与动作|

草稿以空间/草稿实例或会话ID隔离，仅驻留内存；刷新不承诺恢复未发送内容。选择历史不继承新草稿。输入服务未就绪时仍可编辑，发送仍受服务及仓库检查。对照原prototype.html中的前置新建，以本次用户确认覆盖，原资产保留历史来源。样式复用输入卡，采样宽度、padding、font-size及横向溢出；验证1440深浅和390关键状态，合成API与真实执行明确区分。

product_data_collection_observability: status=applicable；affected_layers=[web_request_wrapper,api,db,request_logs,usage_events]；reason=创建请求幂等及发送入口调整，沿用可信身份和既有请求观测，不采集额外正文；validation=创建重放/隔离/删除与发送失败回归、OpenAPI生成检查。Task Trace及执行span结构无变化；无DDL迁移、认证、配额或存储保留变化。


## 顶部精简返修契约（2026-09-11）

证据confirmed：本轮用户截图顶部两行与ChatWorkbenchPage中的chat-workspace-bar、固定loading的ProjectBinding一致。当前授权仓库唯一时沿用自动选择，不硬编码本机路径或跳过授权目录；多仓库仍在输入区选择，缺配置仍提示真实原因。

### 附件截图逐项视觉对照表

|截图/状态|对照对象|期望|实际/偏差|检查方式|处置|证据入口|
|用户红框截图，/chat深色，原图2382×1646（实际CSS视口未提供）|顶部空间工具栏|整行移除|空间/仓库/主题重复占行|截图和chat-workspace-bar源码；1440/390新验收|本次修复|本轮附件、ChatWorkbenchPage|
|同图项目连接栏|project-binding|整行移除|固定loading、刷新禁用，不是真实连接状态|源码state=loading与缺少onRefresh|本次修复|ProjectBinding及调用处|
|同图右上角按钮|chat-panel-toggle|放会话标题行右侧|按钮独占顶部行|DOM归属、键盘与切换测试|保留功能并移动|本批测试与视觉JSON|

UI Reference Replication Contract补充：本次用户明确覆盖原顶部壳布局；空间与主题沿用共享侧边栏菜单。仅移除Chat调用处，不删除共用ProjectBinding。历史/新建/展开动作族同一标题行，无新增modal；历史保留Dialog，新建仍为本地草稿，展开按钮仍控制原panelOpen，保留aria-expanded/aria-controls。selector包括chat-session-bar、chat-panel-toggle、chat-view-tabs、chat-composer。采样标题行位置/高度、输入宽度及溢出；1440深浅及390窄屏检查，确保不留空行、消息区伸展、输入不被挤出。截图CSS视口缺失不影响确认结构性冗余，修改后按规定视口补证。

product_data_collection_observability: status=not_applicable；affected_layers=[]；reason=只调整已有组件位置，不改变API/DB/请求封装/行为事件/Task Trace及存储策略；validation=UI动作、单仓库默认选择及空间权限入口回归。无API/数据库/客户端生成变化。


## 标题编辑与历史入口契约（2026-09-11）

本次无新附件，沿用上一轮截图与当前源码确认：标题触发picker，历史另有切换入口，个人会话为固定标签。当前用户要求覆盖这些交互，属于原会话管理范围。

|参考/状态|期望|实际/偏差|检查方式|处置/证据|
|上一轮会话截图及/chat已选中状态|标题打开重命名|标题打开快速切换，动作重复|ChatWorkbenchPage、SessionDialogs源码/交互测试|confirmed，本次修复|
|空草稿|新会话文字，不提前创建|显示工作台并可选择|DOM、无POST断言|本次修复|
|对话/轨迹栏|移除个人会话标签|固定权限文案常驻|源码和新1440/390截图观察|本次修复，仅移除展示|

UI Reference Replication Contract动作矩阵：chat-title-edit→既有chat-rename-dialog→编辑/空白/失败/保存/取消；chat-history-trigger→chat-history-dialog→选择、搜索及原管理动作；chat-session-picker和picker弹窗删除。新草稿标题只读显示“新会话”，第一次发送创建后可编辑。保存沿用既有PATCH与权限校验，不新增接口。标题长文本省略，编辑图标保留可访问名称；1440深浅及390测量标题宽度、溢出和弹窗可见性。个人会话权限说明移入历史弹窗，明确仅本人且需空间/对象权限，产品UI不承诺端到端加密。原prototype.html保留历史参考，以本契约覆盖。

product_data_collection_observability: status=not_applicable；affected_layers=[]；reason=复用现有重命名和历史API，仅调整入口，不改变请求封装/DB/采集/权限；validation=既有重命名失败、历史切换和默认草稿回归。保留上一轮顶部精简，若集成代码重新加入项目连接行，移除其Chat展示，相关后台连接逻辑不变。

### 输入框常驻说明精简（2026-09-13）

证据 confirmed：Composer 默认 hint 分支固定显示执行说明；actions 使用 space-between，直接移除左侧节点会使发送按钮左移。
本次无新增附件，沿用历史输入框截图与源码核对，不复刻其他区域。

| 参考/状态 | 期望 | 实际及偏差 | 检查方式/selector | 处置/证据 |
| --- | --- | --- | --- | --- |
| 历史输入框截图/正常就绪 | 无常驻执行说明 | 默认 hint 固定显示说明 | Composer.tsx / #chat-composer-hint | 移除默认文案及空节点 |
| 正常及异常/桌面窄屏深浅主题 | 发送始终右对齐 | 删除左节点后 space-between 不足 | .chat-send / computed margin与边界 | 自动左外边距，重新视觉采样 |
| 服务不可用、归档、运行中、缺仓库、失败 | 保留可行动提示 | 已有状态与错误分支 | textarea aria-describedby、role=alert | 保留并测试 |

UI Reference Replication Contract 增量：仅修改 Composer 文案节点和发送对齐；发送动作及无弹窗流程不变。提示存在时才关联 aria-describedby；默认无替代文案。1440与390深浅主题采样，合成API验证真实组件，不触发模型。product_data_collection_observability: N/A；affected_layers: web；请求封装、权限和采集边界不变。
