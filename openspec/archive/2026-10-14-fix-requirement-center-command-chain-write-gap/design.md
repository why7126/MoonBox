---
title: 需求中心治理命令链真实写入修复
created_at: '2026-09-29 16:07:39'
updated_at: 2026-10-07 15:35:00
---

# 需求中心治理命令链真实写入修复

## 对象读取故障隔离（AF-036）

AF-037 评审迁移收尾：标准 promote review 入口移动目录后定向执行对应 req.review/bug.review Workflow Sync，并重读注册表路径、阶段和 trace 状态。同步失败不回滚或删除已有评审文件，返回非零；相同命令对已在 review 的对象继续同步，避免直接跳过造成永久漂移。dry-run 不写，check 检测漂移，目标目录冲突仍阻断。该两阶段流程可重试，不宣称跨文件事务原子性；卡片继续读取注册表，不通过全仓扫描猜测路径。

REQ/BUG 通过对应 registry 定向解析，Change 通过精确目录匹配解析；对象选择列表只跳过单个未完成或不可读条目，不传播为整个会话无权。尚只有 .openspec.yaml 的准备态 Change 保留，直接读取缺失文档返回 503，不伪造 proposal 或删除目录。权限和安全拒绝不进入缺失文档 fallback；Change 显式 ACL 先于文档读取，REQ 短 ID 仍按完整身份校验 ACL。历史快照校验保留真实 403，但不把临时文档缺失重新包装成权限丢失。前端 2509/403 显示对象访问提示，空间 403 仍显示空间提示。

## 停止轮次与后续命令候选归属（AF-033）

AF-035 执行工具链：镜像在构建期安装固定 Node/OpenSpec/pnpm/uv 及通用文件处理工具，不由模型临时下载安装。依赖锁记录 npm 完整性摘要。非 root 构建探针与产品只读沙箱预检共用清单，工具缺失、版本不符、命令失败或超时均在启动模型前终止为 container_toolchain_unavailable；Chat 显示标准部署更新建议，失败轮次释放并发且不覆盖历史成果。已有文件系统和网络权限不变，项目依赖或浏览器并不由本清单隐式授权安装。

工作区准备与成果收集优先按当前 turn ID 选择候选。已绑定前一轮的 running 候选不得回退为当前轮候选；未绑定任何轮次的合法 prepared/running 候选继续兼容原生成入口。原候选和工作区差异保留供核对，不因新命令清除或冒充已应用；后续命令仍通过既有事实源、权限与工作区冲突门禁。

## 评审回写与恢复（AF-031）

AF-032：review.md 兼容 status 或 result 单字段；同时存在时必须相等且属于现有受支持结论，不猜测优先级。acceptance source_event 可保持原值或由对应 complete 更新为 review，其他正文不变。校验失败使用白名单 review_* error_code 显示具体原因，不暴露异常原文。rejected 原候选可由受控恢复入口重验：必须为会话最新完成轮次、无活跃操作或应用记录、绑定未变化，目标文件与原基准一致；保留 recovery-origin 私有基准，校验完整工作区差异后只合并无关事实源更新，再交现有 controller 应用。禁止强行修改状态或清空成果。

req-review/bug-review 使用当前轮候选，不复用历史 complete 的应用状态。候选准备基于当前文件快照；隔离工作区执行后由后端收集完整差异，校验评审结论、对象身份、目标目录迁移、生命周期、registry 与索引一致性。仅允许目标既有文件、review.md 与对应 registry/index；非主文档正文保持不变，允许迁移路径替换及 acceptance 的 Workflow Sync source_event/updated_at 更新。BUG 通过仍要求根因 confirmed。

应用记录以 null 显式表示旧路径删除，与空文件区分；manifest 包含删除标记。controller 先写入目标，再删除旧路径，每步重新校验源文件并保留持久化阶段记录。重启按 before/after 重放，不清空工作区或绕过冲突门禁。成功后 worker 确认应用并更新工作区 Git 基准。

遗留已完成评审仅在会话无活跃轮次、原执行身份和原始基准可确认、目标事实源未变化时恢复。复用原轮次，禁止生成第二份模型结论。模型 completed 仅表示执行结束；application applied/verified 才表示事实源写入成功，Chat 以轻量提示区分，不渲染治理面板。API 路由、DB schema 和客户端生成不变。

## 完善中卡片投影（AF-029）

AF-030 移除“完善中”标签；AF-040 进一步移除“草稿”标签。规划中卡片不显示独立状态标签；长负责人在现有标签行省略并以 title 保留全文。子文档、补证提示、继续完善与内部 enriching 门禁不变。selector `.rc-card-tags > .rc-owner-tag` 验证 nowrap、ellipsis 及父容器边界。

规划中列保留 draft/enriching 两种事实状态，不为其渲染独立状态标签；API 原始 status 与 completion_hint 为可选兼容字段，不根据文档数量推断完成。完善中显示实际存在的业务流程、用户故事或根因/临时方案及验收文档，动作继续使用 req/bug-complete，名称为继续完善。根因未 confirmed 时提示按根因文档补证；confirmed 但仍 enriching 时提示继续完成校验。提示与动作禁用原因分离，不变更写权限或待评审门禁。

UI Reference Replication Contract：沿用现有 rc-card、rc-tag、rc-doc-group、rc-blocked 的主题和布局；selector、截图偏差、动作矩阵见 acceptance-fixes.md AF-029。不新增 modal，继续完善沿用既有 completion Chat 入口。1440px 与移动端检查提示换行、文档打开和按钮可用性；合成 API 浏览器证据与真实文件投影分开记录。

### AF-026 原成果恢复

AF-028：已接入候选的 generate/complete 对零差异执行完整文档与状态校验；收集器复核权限、binding、实时事实源 revision 和字节一致性后记录 unchanged，不创建 application，不更新完成时间或文件。源版本变化和不完整文档仍拒绝。Chat 选择当前候选或接口最新候选，不优先历史 rejected；无需更新仅通过原有轻量通知展示，不恢复面板。

AF-027：bug-complete 复用当前轮次绑定候选、工作区续接与 controller 自动应用。写权限不再读取历史已应用候选。五份目标文档、BUG 注册表及索引作为有界写集合；根因未确认时正式保存 enriching 草稿，保留 lifecycle.completed；confirmed 与证据链通过才进入 pending_review。启动、收集和应用均校验身份、版本与范围，不能用临时目录成果或模型 completed 替代事实源成功。

req-complete 发送时建立候选，已有隔离修改仅在同对象执行轮次可追溯、原始事实源基准匹配且文件均在目标 allowlist 时接管。保留文件字节，执行前再次核对恢复摘要。完整五件套、可选原型、注册表和索引经身份与 pending_review 门禁验证后进入 controller 自动应用；冲突保留成果。应用后仅在工作区摘要与已应用结果完全一致时更新 Git 基准。沙箱只新增容器临时目录写权限，启动前实际验证 tempfile 与 flock；凭证、Git 和网络边界不变。

## 根因证据

### AF-025 执行前阻断

工作区准备阶段尚未调用执行器，失败使用 failed 与具体 error_code，不得归类 unknown；仅已启动且终态无法确认的运行保留 unknown。准备失败按 generation/worker/active_turn 三重围栏释放占用，记录 execution.state 与安全阶段日志。历史准备失败仅在旧错误码及无 executor_turn_id 时恢复，不自动覆盖或应用已有成果。Chat 轻量 meta 显示执行前阻断，alert 提示原因，unknown 不展示等待结果正文。

BUG-0025 已确认：后端治理准备 API 的 action 只接受 `req-generate`，Chat 写权限策略也只认可运行中的 `req-generate` 候选；前端需求中心看板展示完整命令链，但非 demo 路径对未接入命令缺少统一不可执行反馈。该组合导致产品表现超出真实写入能力。

## 修复方案

AF-024：生产 run_claim 默认无总时长截止，max_seconds 仅供显式测试/调用限制。保留停止确认、RPC 超时、权限复查、租约与额度门禁。历史 RPC 响应允许最多 4MiB，流式事件仍为 256KiB，超过上限拒绝。恢复必须以原 thread/turn 的权威终态归并，不根据耗时猜测成功。

AF-023：尚无 assistant 消息时，TurnActivity 独立放入 turn-assistant 兄弟块，不挂在 turn-user。复用 avatar、article、assistant-col；落库后去除临时块，历史不重复渲染。UI Contract：block/article 对齐历史可用宽度，status/alert/activity 对齐扣除头像和间距后的内容列，meta 保持左对齐。测试从真实页面的 messages/events 接口驱动状态，不允许只拼接理想 DOM。

### 执行服务恢复（AF-022）

Worker 完成启动预检后每秒独立更新原子心跳，不受维护、备份和对账阻塞；退出先停止发布再清理。仍保留 5 秒有效期、配置指纹和文件权限校验。capabilities 返回安全 reason_code，区分配置无效、启动中、心跳过期、版本不一致、心跳不可校验和仓库缺失。前端未就绪或网络失败每 3 秒重探测，就绪后每 15 秒检查，不重置会话、草稿、已完成消息；不自动发送。已应用通知刷新回调保持稳定，避免渲染触发请求循环。

1. 后端治理准备扩展 action 能力矩阵，允许 `bug-generate` 与 `BUG-*` 对象进入治理准备流程。
2. 候选收集和应用校验按 action 分流：`bug-generate` 只允许目标 BUG 的 `bug.md`、`trace.md`、`issues/bugs/_registry.yaml` 和 `issues/bugs/CHANGELOG.md` 发生受控变化。
3. 应用 `bug-generate` 成功后同步 BUG 状态为规划中事实源所需状态，CHANGELOG 下一步指向 `/bug-complete <BUG-full-id>`，并写入治理 candidate/application 与 Task Trace。
4. 前端维护产品命令能力矩阵；真实模式下只有已接入真实链路的动作进入准备和应用，其余动作展示明确提示与对应 Codex 命令，不再模拟卡片流转成功。
5. 保留 demo 模式独立模拟能力，但必须在状态和文案上与真实模式隔离，不能写入或冒充治理事实源。
6. 产品准备态必须区分“用户可见命令草稿”和“执行用治理上下文”：Chat 输入框、turn 记录和历史消息气泡只保存并展示简洁 `/req-generate <REQ-full-id>` 或 `/bug-generate <BUG-full-id>`；内部治理约束、写入范围和 dry-run 约束由后端基于 governance candidate 在执行时恢复，不作为用户消息正文或前端隐藏 prompt 落库。若用户手动编辑输入框，后端不得把该输入识别为准备态短命令并追加旧治理约束。
7. Chat 主对话区不得展示治理成果大面板、`查看成果`、`待应用成果` 或 `审阅治理成果` 弹窗；治理候选自动应用、状态轮询、失败提示和轨迹查看应作为后台控制器与轻量反馈处理，不占用对话主区域。
8. 已接入真实治理候选链路的 generate 命令统一采用低风险自动应用策略：候选通过 allowlist、manifest、revision、dry-run、controller-ready 和冲突校验后，由后端 `collect` 创建 application 并交给 controller 串行写入项目事实源；前端只轮询已有 operation。自动应用失败、版本冲突、越界、恢复阻塞或校验 warning 时只展示轻量错误或轨迹提示，不再进入人工“待应用成果”面板。未接入真实候选链路的 complete、review、sprint-propose、opsx 系列仍不得模拟自动应用。
9. Chat 消息布局必须区分角色和内容层级：assistant 输出、外层消息历史轨道、正文 bubble、markdown 容器，以及 TurnActivity 的执行中 status/alert 文案都应在运行态铺满对话区可用宽度，用于承载多段文本、列表、执行摘要和命令运行中输出；该满宽规则必须以 `role=assistant` 和渲染形态为准，不得按 `req-generate`、`bug-generate`、`req-complete`、`bug-complete`、review、sprint、opsx 或普通 Chat 命令名分支生效；TurnActivity 的工具调用/完成状态摘要应作为轻量 meta 左对齐到 assistant 内容列，不得漂浮到正文上方中间或被拉成大块输出；user 消息继续保持右侧气泡宽度限制，避免短命令或用户输入横向铺满。
10. 历史打开已存在治理候选的会话时，前端只恢复后台轮询能力，不得恢复治理成果大面板；pending 且有后端 application 的候选必须轮询 operation，pending 但无 application 的旧候选只给轻量提示，不得由浏览器补发 application。
11. 发送前必须在后端完成执行器 sandbox/dry-run preflight；执行器不可用、namespace/bwrap 失败或 dry-run 未能启动时使用 `executor_unavailable`，模型已完成但成果越界、缺文件、标题或状态不合规时使用 `governance_validation_failed`。
12. Web 启动时必须具备运行态构建版本识别：当前 bundle 与最新 HTML 资产不一致时自动刷新一次；Chat 历史入口还必须清理旧版治理成果面板 DOM，避免活跃旧 SPA 实例或浏览器缓存把已移除的 GovernanceResult 大面板恢复到对话区。
13. Chat 新会话默认执行配置的推理程度为 Low；后端 capabilities 默认值和前端 Composer fallback 必须一致，避免接口加载前后默认显示不一致。
14. Chat 工作台必须分层处理网络与轮询异常：`fetch` 原生 `NetworkError` / `Failed to fetch` 不得裸露给用户；导航、历史恢复或组件卸载导致的 `AbortError` 不渲染错误；工作台启动失败、项目绑定失败、消息读取失败和执行轨迹读取失败分别使用中文局部提示。已有成功消息或已生成文档结果不得被后续 turns/events/governance 轮询失败覆盖为全局错误。
15. 所有写入型对象命令使用当前治理文件 manifest/revision 校验，未提交、未跟踪文件和无关文档修改本身不构成阻断。对象 ID、registry path、trace status 和必需文档仍需校验；只读分析保持原行为。
16. source_root 与 governance_root 的内容 revision 不一致时返回 workspace_fact_source_stale / manifest_mismatch；错误只包含安全原因与同步建议，不要求用户提交 Git，不暴露路径或文档正文。
17. source_root 是真实源目录，governance_root 可为无 .git 的投影。默认副本模式下，发送时保存私有当前文件基线，worker 执行前校验绑定、两侧 revision 并同步到隔离工作区，同步后再次校验。普通 complete/review/sprint/opsx 与 generate 均可读取未提交治理文件。既有工作区额外修改拒绝覆盖；只有精确匹配已应用 candidate 完整 manifest 的成果允许建立隔离 Git 基线后继续下一命令。
18. 本地真实仓库模式必须由仓库绑定显式声明 `workspace_mode: source`。该模式下执行器工作区就是 `source_root` 当前工作树，所有命令直接读写真实仓库；系统不创建会话副本、不覆盖隔离工作区、不在 generate 成果后再进行候选二次应用。项目级串行执行、空间成员写权限、对象状态门禁、产物 allowlist、Task Trace、请求日志和看板刷新仍沿用同一后端控制链路。

## API 与数据

若请求或响应 schema 需要新增 action 枚举、能力字段或不可执行原因字段，应同步 OpenAPI、Orval 生成物和 `docs/03-api-index.md`。治理候选、应用、请求日志与 Task Trace 复用现有表；若实现阶段发现必须新增字段，应补充迁移、数据库设计说明与回滚策略。

## 产品观测

Web 触发准备与应用时继续使用 `X-Chat-Client=web` 关联 `governance.prepare`、`governance.apply` 和 `governance.capture`。未实现命令的拒绝提示可以记录脱敏行为事件或请求日志，但不得保存文档正文、用户输入全文、本机路径或堆栈。

## 验证策略

- 后端评审收尾不依赖模型主动同步投影：完整迁移与结论通过校验后，允许仅补齐仍为旧值的目标 registry/索引，再完整校验。索引目标行须同时回读状态、阶段、下一步命令和 trace 路径；仅改状态与路径不算完成。冲突、缺失目录、根因未确认、越权及越界不能自动修复为通过。source 用条件写入与回读保留失败续接；copy 同步工作区投影后走既有 controller 应用和 checkpoint。无候选/基准不伪造应用。新建隔离评审工作区同步当前迁移、Workflow Sync 和校验工具，恢复有成果工作区不覆盖控制基准。

- 后端覆盖 `req-generate` 保持可用、`bug-generate` 成功、BUG 越界写入拒绝、不支持 action 拒绝和应用后状态同步。
- 前端覆盖 Bug Generate 真实入口、未实现命令提示、非 demo 不模拟成功和 `req-generate` 不回退。
- 前端覆盖运行态 build-id 校验、旧 bundle 自动刷新、历史入口旧治理面板 DOM 清理和 dist/运行态 bundle 禁用文案断言。
- 前端和后端覆盖 Chat 新会话默认推理程度为 Low，包括 capabilities 默认和 Composer fallback。
- 前端覆盖 Chat、governance 和 events 请求的 NetworkError 归一化、AbortError 静默、历史会话已完成消息不被 turns 轮询失败覆盖，以及错误提示不包含浏览器英文原文。
- 前端覆盖 assistant 满宽命令矩阵，至少包括 `req-generate`、`req-complete`、`bug-generate`、`bug-complete`、review、sprint、opsx、普通 Chat 的 running 输出，以及完成态和历史恢复态；回归必须读取运行态 DOM/computed style，而不只校验 CSS 源码。
- 后端覆盖所有产品写入型对象命令共享 stale fact source 门禁、只读 explore 例外、缺主文档拒绝和 clean draft fact source 正常创建会话。
- 后端覆盖无 .git 投影、未提交事实源、无关文档、全写入命令同步、generate 应用后同会话 complete、revision 变化与工作区冲突保护，以及 `workspace_mode: source` 直接真实仓库写入、候选已应用记录、会话清理和 diff 状态。
- 需求中心真实浏览器验证刷新后阶段投影来自 `trace.md`、registry、CHANGELOG、Sprint 和 Change 事实源。
- 如涉及 OpenAPI 或 Orval，同步生成并运行 API/前端客户端回归。

## 风险与回滚

主要风险是扩展 `bug-generate` 与自动应用时放宽治理写入边界。实现必须沿用 allowlist、manifest、revision、controller-ready、冲突预检和幂等键检查；普通文档保存与未接入命令仍保留维护窗口门禁；失败或冲突时整体拒绝并只做轻量提示，不得部分应用后宣称成功。回滚时可关闭自动应用入口或 `bug-generate` 能力矩阵入口，保留既有 `req-generate` 链路。
已评审卡片的 Sprint 命令由服务端按对象类型生成：REQ 使用 `--req`，BUG 使用 `--bug`，均保留完整对象 ID。前端卡片动作优先采用服务端 `action.command`，因此服务端命令必须与前端兜底格式一致。
