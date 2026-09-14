---
change_id: add-local-project-governance-loop
requirement_id: REQ-0022-local-project-import-product-iteration
created_at: 2026-09-11 09:05:00
updated_at: 2026-09-13 00:57:14
---

## 设计背景

REQ-0022 已评审并纳入 sprint-005。现有需求聚合使用全局 GOVERNANCE_ROOT，Chat 使用空间/仓库绑定、已提交树初始化的独立副本。此设计增加两者之间可追溯的治理成果回流，保护原仓库未提交修改。依据 src/backend/app/services/requirement_center.py、app/chat/settings.py、workspace.py、platform_worker.py 与现有 Web 页面；本文件为待实现设计。

## 目标与非目标

目标：一个授权项目、两页共用事实源、5秒更新目标、合法 req-generate 的审阅应用闭环。保持个人会话权限、文件版本保护、幂等和故障恢复。
非目标：自动提交/推送、任意仓库导入、完整生命周期调度、业务源码合并、自动生产升级。只新增 req-generate 的成果应用适配器；原有其他 Chat 对话能力保持，不能误将任意对话差异标为受控成果。

## 设计决策

### D1 UI 策略：现有设计系统组件复用与局部 CSS 适配

采用 DS 复用，新增元素沿现有工作台 token；原型仅移植局部信息结构，不整页 CSS Port，不增加装饰素材。CSS Port 会覆盖已有侧栏和权限交互，重做设计系统成本也超出范围。沿用已评审局部一致策略，无须重新选择视觉风格。

### D2 项目身份与目录解析

引入不可变 ProjectScope 值对象，以 space_id + repository_id 为身份，复用 repository_catalog/repository_binding；首版项目等同于这一组合，不新建通用项目表。解析返回服务端私有 source_root、governance_root、workspace_root 与 binding_revision；应用前映射改变即失效。治理目录与源仓库必须由预检证明为同一事实源，不能将相同显示名称当成对应关系。

所有需求中心聚合、文档读取/预览/保存及任务勾选均接收同一 scope，移除模块级全局 root 的业务读取依赖。空间列表仍由既有成员关系提供，选定项目的数据不允许隐式跨项目回退。冻结空间只读，回收/撤权拒绝；Chat 内容同时要求本人会话所有权和对象权限。页面切换取消旧请求，并用请求代数防止迟到响应污染。

### D3 版本与稳定快照

版本是允许读取文件的相对路径、存在性、类型、内容 SHA-256 的摘要，不只用 Git HEAD 或 mtime。聚合分两次比对文件集合及摘要，变化则有限重试；解析或一致性未通过返回 stale/error，不更新最后成功快照。服务端缓存以 scope/binding_revision/权限范围为键，每次请求重新授权；不能将撤权前缓存返回给用户。

前台可见时每3秒轮询一次，不重叠请求；请求耗时计入5秒目标，连续10次真实观察。后台暂停，恢复焦点立即刷新；失败退避至6/12/30秒，保留同步时间与手动刷新。草稿保存携带文档版本；远端变化只提示，不覆盖草稿。聚合成功不是文件应用成功，两种状态分别显示。

### D4 受控治理执行基准

新建“治理动作”准备记录，允许动作首版只有 req-generate，要求对象 captured 且 capture/trace 非空。准备时由服务端解析完整 ID 和合法路径，不接收客户端命令或目录。先稳定读取原仓库治理输入，再在新建且干净的执行工作区覆盖允许的治理文件快照并创建本地基准提交；该提交仅在副本，不操作原仓库 Git。

快照清单包含目标 Issue 文档、REQ/BUG registry 与 trace、相关 Sprint/Change 的只读治理上下文、执行所需规则/技能/同步脚本。治理正文使用原仓库当前工作树版本，因此包含未提交治理修改；代码基线、技能和脚本版本单独记录。只复制清单允许的普通文件，不复制 env、凭证、运行目录、链接或任意未跟踪文件。读取发生变化则重试或阻止准备。

既有会话有未处理改动时不覆盖其文件：引导创建本人同项目的新治理会话。准备只建立上下文，不自动发消息。发送时再校验输入摘要；变化则要求重新准备。首版基准准备、执行结果收集全部经受信任控制器，模型不能伪造“可应用”标志。

### D5 不可变成果与语义校验

只有真实成功终态生成可应用候选。候选固定绑定动作、操作者、scope、conversation_id、turn_id、binding_revision、基准摘要、成果摘要和文件 manifest。文件上限、正文与Diff字节上限采用现有Chat安全处理边界；超限显示不可应用，不截断后仍允许确认。

req-generate 写集限定目标 requirement.md、trace.md、requirements registry 和 CHANGELOG。对 registry/索引做结构比对，除目标条目及允许更新时间外其他对象变化一律拒绝；trace 只允许该动作的 draft 与 generated 等字段变化，review/iteration/openspec_changes 不得越权推进。正文非空、ID一致、frontmatter与索引一致才能进入 pending。失败/停止/unknown 仅保留普通 Diff。

文件差异为实际内容；预览列出完整固定集合，客户端确认的 manifest_hash 与 candidate_revision 必须一致。后续会话变化不修改历史候选。被替代候选保留历史但不可应用；已应用候选重复请求返回原结果。

### D6 持久应用日志与写入协调

新增 governance_candidates、governance_applications 与 governance_project_locks 三表；SQLAlchemy 使用 SQLite/MySQL 通用类型。候选表含所属身份、动作、源/成果版本、manifest引用、状态及时间；应用表含 candidate_id、actor_id、idempotency_key、request_id、state、phase、error_code、时间；(actor_id,scope_key,idempotency_key)唯一，candidate_id 仅允许一个有效应用。项目锁使用唯一scope_key及fencing_token，状态记录operation_id。

只有受信任单写入控制器能修改原仓库。API 仅鉴权、入队和读结果，不挂载整仓可写权限或凭证/socket。既有需求中心保存/勾选也经该写入通道和同一项目互斥；保留接口交互但使用版本校验。旧写路径无法迁移时禁用新应用能力，不能并行留下绕过锁的写入口。

应用步骤：取得持久项目锁 → 重验权限和映射 → 校验完整读集/写集版本及语义 → 写入私有操作目录中的前后镜像与manifest、fsync → 标记prepared → 每文件写同目录临时文件并原子替换，记录phase并fsync → 验证完整集合及派生索引 → 标记applied → 释放锁并触发刷新。req-generate 的索引已在副本按受控脚本生成，原仓库不执行模型提供的脚本。读快照遇到applying/recovering时保留最后完整快照或返回503。

恢复：重启后先处理持久未终态操作，不仅凭超时释放锁；确认原控制器进程已退出才接管。文件为后镜像时可继续或按日志恢复，为前镜像时按阶段重放；两者均不匹配说明外部修改，进入 recovery_blocked，保留全部镜像和日志，禁用该项目继续写入。回滚只能覆盖仍等于本操作后镜像的文件，绝不覆盖检测到的外部内容；unknown不能重发写操作。

普通文件系统没有跨文件事务，也不能给任意外部编辑器强加互斥。每步写前/后版本检查缩小竞争窗口，不宣称消除最后一次检查与替换之间的竞争。首版自动应用要求受控维护窗口：用户停止其他编辑器/脚本写入，控制器占有已登记写入口；无法建立独占写入条件时拒绝应用。该限制必须在确认界面和部署验收明确说明。外部编辑冲突用失败注入验证；如平台无法满足这一写入前提，不得关闭RC-002或AC-010/012。

原始候选正文与前后镜像保存在受控私有业务目录，仅用opaque ID关联DB，通用日志不存正文。应用未终态或待恢复时禁止删除相关会话/成果及镜像；成功后的清理由明确保留策略和既有Chat删除/备份链路衔接，不能自动清除恢复依据。新表和业务目录纳入备份/恢复验收，不新增S3依赖。

### D7 API 契约与错误

| 操作 | 路由设计 | 关键输入/结果 |
|---|---|---|
| 项目目录 | GET /api/v1/requirement-center/projects | 授权scope及连接状态，不含路径 |
| 现有聚合/文档 | 现有requirement-center路由增加space_id、repository_id | snapshot_revision、sync_status、文档version；保存expected_version |
| 准备治理动作 | POST /api/v1/chat/governance-preparations | scope、完整object_id、action=req-generate；准备ID、兼容会话或需新会话状态 |
| 成果查询 | GET /api/v1/chat/conversations/{id}/governance-candidates | 不可变版本、状态、允许文件与完整受控Diff |
| 申请应用 | POST /api/v1/chat/governance-candidates/{id}/applications | expected_manifest_hash、candidate_revision、idempotency_key、维护窗口确认；202与操作ID |
| 结果恢复 | GET /api/v1/chat/governance-applications/{id} | pending/applying/applied/conflict/failed/recovery_blocked与脱敏原因 |

使用统一响应、Bearer及服务端request_id；401未登录、403无权/只读、404对象不可见、409版本或幂等冲突、422缺失scope/非法动作、503目录/控制器不可用。错误码按项目现有分配规则新增，不复用已有不同语义编号。契约在实施时同步OpenAPI、Orval生成客户端、docs/03-api-index.md与集成测试。身份和维护窗口确认都需后端检查，不能仅靠隐藏按钮。

## 冲突消解（Conflict Resolution）

HTML > PNG > context > acceptance > UI规则 > 旧规格用于本次新增视觉结构判断；HTML明示全部模拟，不具备改变业务安全和验收要求的效力。无PNG，不阻断设计。草图精简侧栏、两列示意看板与正式九阶段不一致：保留正式侧栏/九阶段，仅移植新增连接状态与成果动作。原型不覆盖草稿、错误全部分支，由本设计和AC补齐，不删除这些能力。

旧真实数据规格称所有治理目录只读，与已有受控文档保存和本次应用冲突：MODIFIED“治理文件事实源聚合”，明确聚合只读、写入走可信控制器。无删减无关需求。REQ-0024未归档delta在合并前检查同模块冲突，保留人工编辑矩阵；REQ-0025的“Git合并后续处理”仍适用普通代码，本期新增治理动作例外单独说明。

## 界面契约（UI Contract）

局部一致：沿用 .rc-sidebar/.rc-nav/.rc-user-menu 的品牌、导航、折叠、用户菜单、主题和权限；新元素使用规则金色、14px/1.45正文、2px按钮圆角。旧组件不按简化草图重写。

| 原型selector | 目标selector候选 | 组件入口 | 状态与批次 |
|---|---|---|---|
| #project-binding、#sync-status | 需求中心工具栏刷新提示（无独立连接栏）；Chat chat-project-status | 连接栏与现有关联栏的项目状态 | 无绑定/加载/失败/只读/已连接；批次1 |
| #open-chat | issue-open-chat | RequirementCenterPage卡片动作 | focus/disabled/无权；批次2 |
| #preview、#apply-dialog | governance-result-preview、governance-apply-dialog | Chat成果组件族 | 空/待应用/展开/错误；批次3 |
| #confirm-apply、#close-dialog | governance-apply-confirm、governance-apply-close | 同一成果弹窗footer | 应用中/冲突/恢复阻塞/完成；批次3 |
| #refresh、#toast | project-sync-refresh、governance-toast | 同步反馈 | 失败/重试/已应用但刷新失败；批次4 |

动作矩阵：进入Chat为导航且不发送；查看成果打开dialog；确认应用在同一dialog固定footer，先展示完整写集、版本与暂停其他写入说明；取消/关闭/遮罩/Esc退出预览并返回焦点，内部stopPropagation不误关闭；监听capture或等价不受内部冒泡影响。应用中不允许以关闭假装停止，保留禁用关闭与真实状态；完成后可退出。刷新不打开modal。按钮族统一hover/focus/disabled/loading/error，不逐按钮返修。

尺寸：1440px侧栏沿用224px，预览880px且最大宽视口减24px；低视口正文独立scroll、footer可达。390px新增面板单列，正式侧栏沿现有断点。深浅主题沿rules/ui-design.md，采样selector对应font-size、line-height、padding、gap、width、border、background、color、position、z-index、overflow；期望宽度误差≤1px、布局间距≤2px；当前实现值待实施采样，不伪填通过。

逐批证据落未来evidence/ui/：首屏、卡片导航、预览/确认/冲突/失败/成功全动作族、移动/低高/键盘。Mock只允许Skeleton明确演示，生产与真实闭环必须接真实API、worker和文件。REQ最终一致性与AC-PROTOTYPE-001至006一起关闭。

## 界面骨架（UI Skeleton）

先建立现有两页壳的增量插槽：ToolbarRefreshStatus → IssueChatAction；Chat → CandidateSummary → CandidateDialog(header/filelist/diff/status/footer)。状态数据先使用显式fixture，生成稳定选择器，不发送请求。1440px两页首屏和预览、390px弹窗、深浅主题截图及关键样式为首轮确认材料。首轮确认后才能关闭细节实现任务；后端独立任务可按依赖继续。

## 风险与取舍

- 全局目录改为scope会破坏旧请求 → Web/API同批部署，缺scope明确拒绝，不能兼容回退泄露。
- 文件竞争和非事务文件系统 → 维护窗口、单控制器、版本检查、持久恢复；无法独占则禁用应用，记录RC-002验收限制。
- 3秒轮询加解析耗时 → 小项目缓存、无重叠请求、稳定读取；端到端5秒测试失败时优化而非改指标。
- 8人天存在恢复复杂度上浮 → sprint-005剩余12人天缓冲，不擅自扩大动作范围。

## 迁移与回退计划

先新增兼容SQLite/MySQL的候选/应用/锁表和索引，备份原数据；部署可信写入控制器及私有目录，核对所有旧写入口已统一路由，配置scope映射；Web/API同步发布，能力预检通过后对一个授权验证项目启用。既有Chat消息、会话及工作区不迁移覆盖。

回退先关闭新动作入口，等待或恢复所有未终态写操作；保留新表和恢复文件，不在自动回退中drop表或恢复整个仓库。只回退应用代码和配置，无法确认一致时保留recovery_blocked并由操作记录指导人工处理。不自动执行真实部署。

## 产品数据采集与知识库

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers: [web, api, database, request_logs, usage_events, task_traces, task_trace_spans, agent_workflow, deployment]
  reason: 新增候选与应用持久化、跨页面项目查询及可恢复写入操作。
  validation: 待实施权限、版本、幂等、恢复及AC-016验证；本次仅设计。
```

依据docs/standards/product-data-collection-observability.md：用户行为、请求与任务分层记录，轮询不伪造usage_events；Task Trace覆盖准备、验证、应用、恢复阶段，只有摘要和opaque ID。数据库新增schema、索引、迁移、备份恢复同步docs/04-database-design.md、SQLite/MySQL测试。对象存储N/A：无新增对象存储依赖，保留本地受控业务目录。

knowledge_base_refs：docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md、docs/knowledge-base/retrospectives/sprint-003-retrospective.md。承接S3-A004动作矩阵、S3-A005写入权限和失败草稿保护，不宣布通用行动项完成。

## 待验证事项

无阻断文档生成的产品选择。维护窗口独占写入能否在目标环境成立、控制器中断恢复、所需权限与新schema兼容性属于实施必须验证项；验证失败不降低门禁或自动改为直接写原仓库。review RC-001/002已有设计承接但验证未关闭，RC-003/004等待真实证据。


## 验收返修：看板事实源与连接栏（2026-09-11）

本次范围为 REQ-0022 既有项目治理快照在完整仓库上的正确聚合，以及用户明确要求移除需求中心独立连接栏；不改变 API schema、数据库、权限、部署或成果应用边界。applied 仍映射验收中，in_progress 映射研发中；完成以 Issue 终态及归档事实为准，未知 Change 不得臆测为 proposed。registry 作为对象清单，三份未注册 REQ-0000 不自动加入计数。

### 附件截图逐项视觉对照表

| 编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户附件1 | 需求中心、深色、2830×1628原图、首屏 | 指标与阶段卡片 | 38对象、25REQ、13BUG；已归档34条完成；4条applied验收中 | 阻塞38；33条回退待开发 | 阶段/阻塞语义 | 仓库解析复现、卡片DOM、1440px截图 | 本次修复 | 本节及返修测试报告 |
| 用户附件1 | 同上 | moonbox 已连接独立栏 | 整块移除，标题后直接指标 | 独立连接栏占据一行 | 组件层级/间距 | .rc-content > .pg-binding不存在、grid computed style | 本次修复 | 返修UI截图及styles JSON |
| 用户附件2 | 文件树、bugs/archive | BUG-0001～0013 | 13条完成 | 12条回退、全部阻塞 | 归档解析 | registry/Issue/Change/Sprint对照 | 本次修复 | 后端整库回归 |
| 用户附件3 | 文件树、requirements/archive | REQ-0000～0021 | 注册的21条完成；3份0000不在注册计数中 | 21条回退 | 数量口径/归档解析 | registry对照、精确ID路径核对 | 本次修复，不自动注册0000 | 后端整库回归 |
| 用户附件4 | REQ-0022 trace预览 | apply完成待archive | applied显示验收中，实际存在的acceptance不误报缺失 | 卡片报缺少acceptance.md | 校验事实源 | 检查Issue真实文件与Change展示列表 | 本次修复；保留九阶段定义 | Issue/Change trace与单测 |

### UI Reference Replication Contract 补充与冲突消解

最新用户反馈优先于原型中的需求中心独立连接栏。移除 RequirementCenterPage 的 ProjectBinding 插槽及其专用grid行；不改变Chat的内联项目状态。需求中心刷新按钮保持原selector `[aria-label="刷新需求中心"]`，title呈现最后同步状态，失败仍用现有toast/错误态；不增加新横栏。原型项目连接仅在Chat页展示，需求中心身份仍由已授权scope选择确定。

动作矩阵本次触达一族：工具栏刷新 → 无modal → `[aria-label="刷新需求中心"]` → 默认/刷新中/失败可重试 → 浏览器点击、筛选保留和请求次数证据。其他成果modal动作族未变，沿用原矩阵。

UI Skeleton更新为：标题 → 指标 → 搜索筛选及刷新 → 九阶段看板。批次：先修后端及回归，再1440px深浅色首屏/筛选刷新和390px布局验收。采样 `.rc-content` 的 gridTemplateRows、gap、overflow；`.rc-stats` 的top/width；刷新按钮的fontSize、padding、disabled。无绑定和权限错误保留原有错误态。本轮视觉使用仓库解析数据的受控HTTP fixture，明确为合成浏览器验收，不宣称真实部署观察。

返修视觉复核补充：首次新截图发现前端blockedTip仍给已完成项强制补验archive.md。已完成项没有待执行动作，现取消该终态重复校验，补充已完成卡片无rc-blocked提示的浏览器断言；重拍后证据覆盖此偏差。


## 首屏原位骨架返修契约

### 附件截图逐项视觉对照表

| 编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户附件34c55de6 | 需求中心、深色、刷新加载中，原图2380×1456 | 红框加载面板 | 原位加载，阶段列位置不变 | rc-state-panel占位并推低整个看板 | 布局高度/跳动 | 代码分支和截图确认；1440慢请求前后DOM位置采样 | 本次移除加载面板 | 本节、loading-*截图/styles |
| 同附件 | 指标/列头/空列 | 未返回数据状态 | 骨架占位，不假报零值或空态 | 四个0、阶段00和暂无需求同时显示 | 状态语义 | 延迟响应时文本/DOM断言 | 本次修复 | 慢请求浏览器断言 |

根因confirmed：isLoadingContext分支插入普通流面板，但rc-board始终渲染空数组，统计也按空数组计算。保留现有壳和九列网格，骨架只替代数字与列内卡片位置。无新增modal，刷新动作族继续使用工具栏原按钮；初始loading禁用、后台refresh仅按钮busy，既有数据/筛选保留。

UI Reference Replication Contract增补：`.rc-stat strong`内数字骨架、`.rc-column-head`计数骨架、`.rc-column-body`卡片骨架；看板容器aria-busy标识加载，提供不占布局的读屏提示。深浅主题使用现有border/token，无额外动效；骨架不成为可点击控件。采样`.rc-stats`、`.rc-toolbar`、`.rc-board`及列头/列体的top和height，加载完成前后位移≤1px；1440深浅和390验证。加载期间不渲染rc-empty-stage和独立rc-state-panel，正常空数据仍显示原空态。

本次Mock/API边界不变：浏览器以延迟合成HTTP响应验证首次加载与后台刷新，不宣称当前业务部署已更新。原型增加可模拟的原位加载状态；最终文字、流程和验收同步。

首屏契约验收结果：loading-styles.json中1440深浅/390的maxTopShift均0px，未出现独立加载面板、假零值或暂无空态，后台刷新保留卡片。截图已人工复核，证据为延迟合成HTTP，不是当前业务部署观测。


## 同名 trace 文档归属返修契约（历史双入口方案，已被单入口最终契约替代）

### 附件截图逐项视觉对照表

| 编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| aa14241e | 需求中心REQ-0022抽屉、深色、1498×1496截图 | trace入口/标题/正文 | 区分需求与Change归属 | 标题REQ-0022·trace.md但正文为Change实施记录 | 同名文档来源不清 | 后端URL映射、文件正文与截图对应 | 本次修复 | trace-source浏览器与后端回归 |
| 同附件 | trace首屏 | 最新摘要/历史记录 | 最新结论置顶、旧结论明确历史 | 失效路径及连接栏旧记录在前，最新返修在后 | 时间语义/阅读顺序 | 两份trace正文对照 | 本次整理 | REQ/Change trace及新截图 |

根因confirmed：阶段优先展示Change文档，而label和抽屉只显示REQ编号及文件名；后续返修追加记录但未更新顶部摘要。保留文件名trace.md、既有API路由与权限契约，用现有document_entries的label/url分别表示来源。需求/缺陷trace与Change trace分别提供入口，React key按URL区分；两种入口复用同一只读抽屉，标题/来源行说明完整对象身份。不同URL的同名文件不得混淆。

动作矩阵：需求追踪/Change实施记录按钮 → Markdown抽屉 → `.rc-doc-item button`及`.rc-drawer-crumb/.rc-document-source` → 加载/读取/关闭/全屏/失败 → 各点击一次核对请求URL、正文、标题、只读。无新增modal族；现有抽屉样式和行为复用。样式采样来源行fontSize/overflowWrap、标题宽度，1440深浅与390长Change ID无溢出。

REQ-0022 Change trace重排为最新摘要→待验收→历史记录（注明首次apply与历次返修）；不删除已有证据或改变历史测试结果。需求trace当前状态仍由Workflow Sync维护，新增当前阅读摘要并保留生命周期。浏览器证据使用实际文档与合成HTTP，未切换业务部署。


## trace 单入口最终契约

最新用户指令覆盖此前双入口设计：所有REQ/BUG卡片、所有阶段，trace.md仅指向所属Issue目录，标签统一trace.md；不展示Change trace，不作缺失回退。其他Change文档和内部阶段计算不变。既有同名截图aa14241e和双入口截图作为历史对照，当前验收改为单入口。

| 附件/截图 | 页面/状态 | 对照对象 | 期望 | 实际 | 偏差 | 检查方式 | 处置 | 证据 |
|---|---|---|---|---|---|---|---|---|
| aa14241e及trace-source历史截图 | 需求中心/深色/trace抽屉 | trace链接与标题 | 唯一Issue trace、普通文件名 | Change正文及后续双入口 | 来源/标签 | 所有阶段REQ/BUG参数回归、点击URL | 单入口修复 | issue-trace截图和回归 |

沿用只读Markdown抽屉族：trace.md按钮→原抽屉→加载/成功/404→明确缺失且不回退。恢复普通标题，取消额外来源行和拆分标签。1440深浅/390检查标题、正文、关闭和缺失态；样式采样标题字号/宽度/换行。REQ/BUG trace不存在时入口仍指向Issue路由并给出不可用反馈，不造文档、不引用Change内容。


### 任务入口统一文档返修契约

证据状态 confirmed：RequirementCenterPage 三个进度按钮直接设置 tasks 抽屉，抽屉仅使用卡片计数，未调用文档读取。此次无新增附件，承接历史卡片截图；偏差为交互而非截图尺寸。

| 对照对象/状态 | 期望 | 实际及偏差 | 检查与处置 | 证据入口 |
|---|---|---|---|---|
| 历史卡片截图中的研发、测试、人工验收按钮 | 完整 tasks.md 内定位 | 独立统计面板 | 三入口统一 Markdown 阅读器，DOM 与浏览器验证 | RequirementCenterPage.tsx；新 tasks-navigation 证据 |
| 文件加载/缺失、章节缺失 | 加载后定位；缺失明确提示 | 原面板无文件读取，无法反映缺失 | 复用授权读取；不伪造正文与目标 | 回归测试及错误态截图 |

动作矩阵：研发→Markdown→任务研发章节/实现任务；测试→Markdown→测试章节/测试任务；人工验收→Markdown→人工验收章节/人工任务。共用 .rc-markdown-view、[data-task-navigation] 与 .rc-task-navigation-target，覆盖加载、成功、缺文件、缺目标。明确章节优先，任务文本其次；历史返修记录与代码块不参与定位。不扩大勾选、编辑权限；普通 tasks.md 链接仍从顶部打开。

视觉验收：1440px 深浅主题及390px；检查目标位于抽屉滚动视口，目标高亮、正文完整、提示可读，记录 computed style。使用合成 HTTP，不能替代真实部署观察。


任务入口返修验证结果：本轮最终前端回归67项通过，TypeScript检查通过；浏览器24个生产组件场景通过，覆盖1440px深浅主题、390px、章节优先、任务回退、缺文件、缺章节、普通入口无定位；同步原型4个交互验证通过。视觉与 computed style 证据见 evidence/ui/tasks-navigation-*。OpenSpec strict、中文、目录、Sprint scope、diff检查通过。后端未改变，本轮未重跑后端测试。


### Sprint 文档归属返修契约

附件截图逐项视觉对照表（confirmed，用户截图70ef85a1）：

| 页面/状态与对象 | 期望 | 实际偏差 | 检查方式与处置 | 证据入口 |
|---|---|---|---|---|
| 需求中心深色、迭代规划BUG-0014卡片，截图为局部裁剪 | sprint-005关联文档可读 | 已有Sprint徽标但缺sprint.md按钮且误报阻塞 | registry、Sprint文件及聚合读取代码已确认；修复来源解析 | 用户截图；requirement_center.py |
| sprint.md打开/缺失/归档 | 完整关联Sprint正文、只读；缺失明确提示 | 原读取固定Issue目录 | 共用解析，复用Markdown抽屉；1440深浅/390及错误态DOM、截图、样式采样 | evidence/ui/sprint-document-* |

动作矩阵：卡片sprint.md → 现有Markdown抽屉 → .rc-docs button / .rc-markdown-view；trace.md仍是Issue，其他Change文档不变。相同Sprint ID优先活动目录，仅活动目录不存在时解析归档目录；活动目录缺文件不退到旧归档副本，更不退到Issue/其他Sprint。校验项目作用域、关联和Sprint成员关系；只读，不扩展写入与授权边界。测试使用真实仓库数据及合成HTTP，不声明运行部署已经更新。


Sprint文档返修验证：后端58项通过（聚合、REQ/BUG活动与归档来源、缺失不回退、路径校验、作用域和HTTP接口）；浏览器6个场景通过，覆盖1440深浅与390px正常/缺失态，原型Sprint入口验证通过。证据为evidence/ui/sprint-document-*及样式JSON。OpenSpec strict、中文、目录、Sprint scope与diff检查通过。浏览器为真实仓库聚合/正文与合成HTTP，未切换业务部署。


### 主动作阻塞与 Tips 避让返修契约

附件截图逐项视觉对照表（confirmed；附件cd8d69e9，需求中心深色局部裁剪）：

| 对照对象/状态 | 期望 | 实际偏差及证据 | 检查/处置 | 验收入口 |
|---|---|---|---|---|
| BUG-0014迭代规划卡片、缺sprint.md | 生成Opsx禁用且原因一致 | blockedTip包含前端缺失但按钮仅检查接口disabled_reason | 共用blockedTip，原生disabled和执行守卫同步 | .rc-card footer button.primary、.rc-blocked |
| 右下角Tips与Agent按钮同时可见 | 提示全文可读、互不遮挡 | Tips bottom24/z50与Agent bottom28/height48/z65重叠 | Tips放按钮上方，留安全间距，约束宽高并换行 | .rc-toast、.rc-agent-fab |
| 390px/长文案 | 不越界、不遮挡按钮 | 原Tips无窄屏宽度或换行约束 | 1440深浅/390及320长文案测量 | evidence/ui/action-toast-* |

动作族矩阵：卡片各阶段主动作 → 当前合法动作弹窗/执行入口；有阻塞时不进入弹窗、不发起请求，已有文档阅读继续可用。接口原因、Issue阻塞与前端必需文档使用同一判断，不增加新的服务端权限或开放未支持动作。Tips作为现有状态提示，消息容器与助手按钮矩形不相交；computed style采样disabled、opacity、position、bottom、z-index、width、overflow-wrap。参考图仅修正这两项偏差，原卡片布局保留。


主动作与Tips返修最终验证：70项前端回归及TypeScript通过；12个浏览器状态通过（1440深浅、390、320；禁用/补齐恢复、短提示、长中文及无空格长词），提示矩形与Agent至少保留8px间距，无横向越界。原型禁用/恢复与长提示验证通过。证据为evidence/ui/action-toast-*和样式JSON；使用合成HTTP，只证明本地源码UI，未切换业务部署。OpenSpec strict、中文、目录、Sprint scope和diff检查通过。


### 主文档持续展示返修契约

证据confirmed：阶段白名单在迭代规划后排除requirement.md/bug.md；后端Change文档聚合只补Issue trace。此次无新增附件，承接历史卡片与代码证据。

| 对照对象/状态 | 期望 | 实际偏差 | 检查与处置 | 证据 |
|---|---|---|---|---|
| 各阶段REQ/BUG卡片 | 已生成主文档始终首位 | 后续阶段被过滤 | 后端保留真实Issue主文档，前端跨阶段优先排序 | 聚合/组件回归 |
| 主文档阅读与编辑 | 所属Issue正文，原阶段权限 | 展示缺失导致无法阅读 | 复用文档抽屉与能力矩阵 | evidence/ui/main-document-* |

动作矩阵：requirement.md/bug.md → 现有Markdown抽屉 → .rc-docs button、.rc-markdown-view；覆盖生成前无入口、生成后全阶段、归档、只读/可编辑、读取缺失。不会用Change同名文件替代。1440深浅/390验收入口排序、正文、样式与权限，合成HTTP和真实仓库文档分清证据边界。


主文档持续展示最终验证：后端80项、前端79项、TypeScript通过；15个浏览器场景通过（1440深浅/390，活动和归档REQ/BUG首位入口、Issue正文、只读与缺失不回退），原型主文档入口通过。证据为evidence/ui/main-document-*和样式JSON。OpenSpec strict、中文、目录、Sprint scope及diff校验通过。浏览器使用真实仓库聚合和正文配合合成HTTP，本轮未切换业务部署。


### Sprint 文档持续展示返修契约

confirmed：后端已聚合关联Sprint，前端白名单仅迭代规划显示。此次无新增附件，承接已有Sprint卡片证据。

| 对照对象/状态 | 期望与偏差 | 处置/检查 | 证据入口 |
|---|---|---|---|
| 各阶段REQ/BUG文档列表 | sprint.md出现后持续显示，实际后续阶段被过滤 | 展示白名单加入sprint.md；主文档排序不变 | .rc-docs button；阶段回归 |
| 活动/归档Sprint阅读 | 原来源、只读、不扩大必需校验 | 复用现有接口与能力矩阵，缺失不新增其他阶段阻塞 | .rc-markdown-view；sprint-persistent视觉证据 |

动作矩阵：sprint.md→现有只读Markdown抽屉；主文档仍首位，其他文档原规则不变。1440深浅/390检查入口、正文、只读和computed style；合成HTTP与真实仓库正文，不代表已部署。


### Sprint 跨阶段展示返修契约

confirmed：后端已经返回真实关联Sprint文档，前端stageVisibleDocs仅在迭代规划展示。此次无新增附件，沿用历史Sprint卡片和源码证据。

| 对照对象/状态 | 期望 | 实际偏差 | 处置/检查 | 证据 |
|---|---|---|---|---|
| 各阶段REQ/BUG卡片 | sprint.md出现后持续显示，主文档仍首位 | 后续阶段白名单排除Sprint文档 | 只调整展示白名单，不改requiredDocs | 组件回归及sprint-persistent截图 |
| 活动/归档Sprint阅读 | 原关联文档，只读 | 既有解析已满足 | 复用.rc-docs button→.rc-markdown-view，验证正文和权限 | evidence/ui/sprint-persistent-* |

UI契约：1440深浅与390px验证入口、主文档顺序及抽屉；缺文件仍沿用原处理，不把sprint.md新增为其他阶段必需项。保持原布局与编辑权限，使用仓库聚合/正文和合成HTTP。


### 卡片文档分组排序返修契约

依据：用户本轮文字确认及历史 sprint-persistent 截图；当前 visibleIssueDocuments 仅将主文档提前，rc-docs 混排，偏差 confirmed。无新附件，采用局部一致。

|页面/状态|期望|实际与偏差|检查方式|处置与证据|
|---|---|---|---|---|
|需求中心1440深浅/390，卡片文档|常驻主文档、Sprint、trace在前；阶段任务优先；双组才分隔|当前混排，数据顺序决定其他文档顺序|DOM顺序、截图、computed style|统一修改rc-docs组件族；evidence/ui/document-groups-*|

常驻组固定主文档、sprint.md、trace.md；阶段组沿规划/评审阅读顺序，待开发proposal/spec/design/tasks，研发和验收tasks/spec/design/proposal，完成archive/tasks/spec/design/proposal。仅双组非空显示细线；空组不占空间；组内自然换行。同样链接样式，来源、编辑权限、缺失校验不变。按钮继续原openDocument→原文档抽屉，所有文档动作共用，无新modal。采样.rc-doc-group的gap、border、宽度，1440深浅和390截图验收。原型旧混排由本契约替代，保留模拟边界。


### 文档区紧凑换行契约（替代分隔线）

本轮无新增附件，沿用document-groups-card截图及用户文字确认；偏差confirmed，CSS相邻组为8px margin + 8px padding + 1px border，占用17px。

|参考证据|页面/状态|期望|实际/偏差|检查方式|处置|
|---|---|---|---|---|---|
|document-groups-card历史截图|需求中心1440深浅/390，单组/双组|无边框，双组4px，单组无占位|双组有线与17px留白|.rc-doc-group相邻组computed style、截图|本次统一CSS修复，document-compact证据|

动作与抽屉矩阵沿用上轮，排序/来源/权限均不变。原型同步移除线，组间4px。样式采样marginTop/paddingTop/borderTopWidth及实际组间距，1440深浅与390验证；不改变Mock/API边界。


### 文档读取与刷新性能返修契约

证据confirmed：reader.call读取Change时authorize_object与正文解析重复materialize；本机1002文件stable约913ms，materialize/cleanup分别1227/1002ms。此为局部基线，不代表截图20.81秒全部归因；生产队列/DB耗时unknown。采用一次物化复用，稳定双读、授权、写入epoch、绑定版本检查不变，无跨请求缓存。分段性能日志仅包含服务端request_id、操作名、耗时和成功状态，不记录正文/路径/身份。

|附件|页面/状态|期望|实际/偏差|检查与处置|证据|
|---|---|---|---|---|---|
|3794273f耗时截图|文档GET等待响应|避免重复I/O|等待20.81秒|分段计时、同快照复用，本次优化|reader性能日志与测试|
|9514d6cb网络截图|context取消|同项目刷新合并|NS_BINDING_ABORTED，代码每次abort|延迟context+focus/visibility/轮询复现并验证|refresh-performance浏览器证据|

文档按钮→原抽屉矩阵不变；首次骨架/后台保留卡片/草稿冲突继续沿用。相同项目刷新进行中复用Promise，项目切换或卸载才取消；初始化完成后再启动轮询。1440深浅/390观察抽屉与刷新，采样布局，模拟HTTP仅证明调度，不代表真实部署时延。


### 卡片更新时间完整日期返修契约

confirmed：_updated_at仅strftime(%H:%M)/切片，日期在API返回前丢失。本轮无新附件，沿用document-compact卡片截图为实际参考；用户确认YY/MM/DD HH:mm。保留源时间的年月日时分，不擅自转换无时区日期；只有日期、无效或缺失值不补造时分，显示更新时间未知。

|参考|页面/状态|期望|实际偏差|检查与处置|证据|
|---|---|---|---|---|---|
|历史卡片截图|所有阶段REQ/BUG，1440深浅/390|更新26/09/12 17:30或更新时间未知|只有时分|后端格式参数测试、前端共享footer与布局边界检查|updated-date截图及样式|

selector .rc-updated、footer；沿用所有动作→原modal矩阵，不改交互；footer允许必要换行，时间不拆分。原型同步文案，Mock/API边界不变。


### 原型HTML常驻返修契约

confirmed：后端只扫描Issue顶层，Change阶段覆盖原型；前端仅planning白名单接受prototype.html。用户文字确认，无新附件，参考既有updated-date卡片截图。

|参考|状态|期望|实际偏差|检查/处置|证据|
|---|---|---|---|---|---|
|既有卡片与需求prototype目录|1440深浅/390、活动/归档|主文档后显示原型，多端标识|嵌套原型缺失，后续阶段隐藏|共享安全路径发现和预览读取，前端常驻排序|prototype-persistent测试与截图|

读取所属REQ目录顶层prototype.html及prototype/**下HTML，拒绝符号链接与目录逃逸。多端标签以相对路径区分；不存在无入口，不增加必需文档。原型按钮→已有受保护HTML预览新页，沿用项目权限及安全响应头，不开放静态源目录。组间4px不变。


### 原型入口标签精简

confirmed：后端label拼接“原型 · ”，本轮按用户文字确认移除；无新附件，参考prototype-persistent截图。

|参考|状态|期望|实际偏差|检查/处置|证据|
|---|---|---|---|---|---|
|prototype-persistent截图|1440深浅/390，活动/归档|web/prototype.html、admin/prototype.html|额外“原型 · ”前缀|label聚焦校验、截图、组间距检查|prototype-label-*|

仅label文案变化，端目录保留；主文档后常驻、读取URL、权限、预览动作矩阵与4px间距不变。
