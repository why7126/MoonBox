---
title: Chat 大规模工作区持续执行设计
created_at: 2026-10-25 22:29:00
updated_at: 2026-10-25 22:29:00
---

# Chat 大规模工作区持续执行设计

## 背景与目标
来源 REQ-0053，承接 REQ-0025/0043/0046/0047。workspace.py 当前使用全量字典、10000文件／512MiB门槛；execution.py 将回复累加到字符串并按 reserved_bytes 截断，settings.py 要求完整限额配置。schema.py 已有事件、消息、Diff、工作区基线与计量表，ExecutionPanel 已有轮次、停止、重试和事件分页。以上是代码观察，未把设计写成已实现能力。

目标为无固定业务总量门槛、有限工作内存和可核验恢复。非目标为无穷硬件、取消上游模型限制、后台配额页面、多机调度及重做备份系统。

## 决策 D1：局部 UI 采用设计系统
沿用 Chat 组件、token、路由与权限，以局部原型为结构输入，不将评审控制器搬入产品。CSS Port 会复制独立线框样式，Asset 不适用于纯状态区域，因此选择 DS。不需要用户再次选择已确定的局部一致方向。

## 决策 D2：业务数据库分块存储
选择已有 SQLite/MySQL 作为元数据和正文分块介质。相比新增本地文件池，事务提交、授权、删除意图、备份范围更统一；相比对象存储不新增服务依赖。代价是数据库体量与备份成本增加，须通过双库容量测试。对象存储本期 N/A：不新建对象、不改变 S3 授权或生命周期；既有上传附件路径保留。

新增表命名为实施目标：
- chat_content_objects：会话作用域 object_id、format_version=2、sha256、byte_count、kind、status、created_at；不跨用户／会话去重，避免泄漏与删除耦合。
- chat_content_chunks：object_id、chunk_no、payload 二进制、byte_count、sha256；唯一(object_id,chunk_no)，每块256KiB，不把正文放进JSON索引。
- chat_snapshot_versions：conversation_id、turn_id、phase、parent_version、scan_cursor、status、manifest_hash；building/complete/abandoned，完整版本不可变。
- chat_snapshot_entries：version_id、规范相对路径的大小写敏感键、kind、mode、digest、object_id；以排序游标分批索引，避免全量字典。MySQL 使用二进制排序确保路径大小写不混淆。
- chat_result_segments：turn_id、stream_id、source_event_id、source_offset、sequence、object_id、commit_state；唯一来源偏移约束与(turn_id,sequence)索引。已有 chat_events 只保存有界摘要和内容引用。
- chat_storage_ledger：owner/space/conversation、唯一计量事件、已提交字节变化；与提交或删除引用事务一致。
沿用现有审计字段、外键和数据访问层。SQLite BLOB／MySQL BLOB 分块，摘要索引不用大 TEXT。新增列通过版本化迁移默认旧格式，SQLite/MySQL 单独验证事务、唯一键、排序、锁与重启恢复。

## 决策 D3：可信快照与差异
Git 文件枚举以 NUL 流式读取，不用 capture_output 全量收集；分批排序进入临时索引，非Git目录也使用有界目录遍历。保持受信路径、dir-fd/O_NOFOLLOW、拒绝硬链接／特殊文件，符号链接仅保存脱敏元数据，不跟随读取。
读取块64KiB，索引批次256项。每文件前后 stat 与实际读取长度、摘要比对；变化则重采，持续变化明确 incomplete。删除项通过扫描代际对照，重命名保留路径变化和内容引用，权限属性单独比较。
仅有 mtime/size 不能证明未变：无可靠文件系统版本证据时继续流式摘要校验，摘要相同才复用内容对象。该路径减少重复内容写入，不承诺所有环境省略全量读盘。可信Git不可变对象可复用，但工作区脏文件仍校验。恢复扫描后重新验证检查点前文件身份与内容，不把旧游标当完整性证明。
发布 complete 前比较完整扫描清单和摘要；并发变化用二次验证发现后重试或保持不完整。未控制外部写入时不声称跨文件原子时刻快照；检测到漂移不得作为可信基线。事务只切换有效版本指针，旧完整版本保留。
Diff 基于两版本索引归并遍历；大文件按数据库内容块索引精确比较并分页返回变化块；使用块序号而非行号，不承诺最小行级补丁，禁止调用全量 unified_diff 聚合全文。正文可按范围读取两侧快照；无改动判定须基于可信摘要，不以未加载代替无差异。

## 决策 D4：持续保存、游标与计量
单轮每条接收事件带原来源标识；无来源标识的重连数据不能凭内容猜测去重，需协议给出可证明游标，否则标记未知缺口并停止自动拼接。拆块保留 source_offset。块写入和段提交使用小事务；只有正文块校验完成且段索引提交后才推进 committed_sequence。已接收但未提交范围只存内存状态或恢复诊断，不伪称持久化。收到最终回复引用已有段或作为独立 final 流保存，不能再全量拼接；页面区分增量回复与最终更正，避免重复正文。
接收→排队→落块→提交→发布读取通知；队列按字节有界，满时暂停读取；超过背压时限则请求受控停止，等待终态，不确认时进入 unknown。进程突然退出后，以DB提交点恢复；尾部未确认范围显示 unknown，不能伪造精确丢失字节数。
内容对象在同一会话内相同摘要只物理保存一次；Chat存储计量为活跃、已提交对象的唯一正文块字节及事件实际保存UTF-8字节，不计数据库页/WAL/索引/备份物理开销。跨会话分别计量；同一会话最后一个引用删除时扣减，pending块未发布不算用户保存量，但纳入部署磁盘诊断。对账按唯一ledger事件幂等，数据库真实体积另记部署指标。
Token 无单轮预算：可信total按来源revision/轮次幂等结算，未知为null，迟到只补差额；不改写历史终态。用户／空间已有月度有限值保留，对准入按已核实累计与活动状态执行；不以单轮预留值终止运行，跨过阈值后拒绝新的轮次，已准入轮次仍正常结算。有限存储配置按新增提交批次原子检查并保留已提交结果，该运营策略与无配置的默认无限分开。

## 决策 D5：配置迁移与资源保护
MOONBOX_CHAT_LIMITS 缺省用户／空间 monthly_tokens/storage_bytes 为 null/unlimited；显式负数、零、非整数或未知策略值报配置错误，不静默无限。并发配置沿用既有有效值及同会话互斥，不把并发策略变成本期运营扩展。
旧 turn_reserved_tokens、turn_reserved_bytes 只兼容读取并产生脱敏弃用诊断；新轮次不作为终止门槛。旧活动轮次先排空或核验再切换，不混用新旧结算。固定快照／文本总量门槛从新执行路径移除。
部署参数冻结为设计初值：读块64KiB、内容块256KiB、扫描批256项、结果队列4MiB、单次API正文页256KiB/列表100项、前台同时保留最多4个正文页；这些是窗口而非总量上限。协议解析单帧8MiB，增量读取并在超界前拒绝，消息深度64；支持的普通事件和RPC响应均验证边界、UTF-8、畸形消息。此值是待测部署保护，不承诺任意单帧。合法超保护消息返回 protocol_resource_limit；禁止悄悄丢帧，保留已提交内容。
容器保持1CPU/1GiB内存/128进程、tmpfs64MiB；worker容量实验同样限制1GiB。背压持续30秒进入受控停止；DB锁按5秒超时报告可恢复存储忙，不无限占队列。磁盘预检保留256MiB部署应急余量，并持续检测ENOSPC/数据库空间错误；远程DB不能用worker本地磁盘假证据推断，使用DB错误/健康指标。错误回执也不可写时通过独立健康诊断与重启对账补事实。
这些参数仅部署配置，不能进入运营后台。调整须先改设计与测试基线再测，不可失败后临时放大以宣称原预算通过。

## 数据与 API
保留现有 /api/v1/chat 路由与鉴权封装；新增目标接口：
- GET /turns/{tid}/results：stream_id、opaque cursor，单页最多256KiB；返回段、next_cursor/resume_cursor、committed_sequence、has_final、completeness及storage_status；无可信上游重放游标时以unknown_tail表达未确认尾段，不虚构缺失区间；游标绑定轮次/流/版本，不作为授权凭证。
- GET /turns/{tid}/files：快照/差异索引页；GET /turns/{tid}/files/{file_id}/content：side、cursor，返回UTF-8安全分段或二进制元数据，不暴露宿主路径。
- POST /turns/{tid}/recovery：idempotency_key、mode=check|resume_prepare；返回原turn_id、attempt_id、eligibility、reason，不将 accepted 当执行完成。
现有 events SSE 使用已提交游标，旧消息/diff接口保持旧格式可读；新格式返回摘要、content_ref、has_more、format_version，不偷偷用截断字符串冒充全文，更新所有前台消费者。前后端同版本发布；旧客户端遇新格式明确升级要求而非无限加载。
错误字段统一 stage、stable_code、execution_started、saved_range、completeness、recovery_action、request_id。稳定分类：operating_quota_exceeded、workspace_resource_exhausted、result_persistence_failed、execution_resource_exhausted、protocol_resource_limit、upstream_error、execution_state_unknown。授权失败不泄露对象存在。同步Pydantic/OpenAPI、Orval生成物和docs/03-api-index.md，契约测试含跨空间游标与直接API。

## 恢复与迁移
复用现有治理恢复入口／互斥／阶段日志。准备失败通过原turn_id下新的attempt续接，保存旧attempt失败终态；只有证明execution_started=false才允许resume_prepare。运行中断或unknown只允许check，先查原进程/上游thread与持久化成果，无法证实保持锁和人工核验说明。确需重新执行仍沿用既有“关联原轮次的新轮次”显式重试，不把有副作用运行说成原地续跑。
迁移采用expand→双读→分批backfill→校验→切换新写，旧数据不删除、不伪造缺失全文。历史记录没有原始完整文本时标记 legacy_unavailable。迁移检查点与对象发布幂等，失败继续旧读路径。冻结写入后可回退到支持v1/v2双读的兼容版本；不直接回退到只识别v1的旧二进制。新产生v2数据保留且可读取，若必须回退更旧版本，先导出并核验可兼容表示，无法无损则阻断降级，绝不删新数据。
删除意图先检查活动/未知轮次，再事务撤销可读引用、发布删除标记、异步清理无引用块；所有读取、迁移、恢复及备份还原先检查删除日志。备份继续覆盖业务DB及其一致性WAL策略，独立审计保留，GC不删除已授权保留副本。

## 原型冲突处理（Conflict Resolution）
视觉结构按HTML→PNG（无）→context→acceptance→规则→既有spec；业务语义由已评审PRD/AC约束。context声明业务优先与上述视觉优先并不冲突。HTML含示例状态选择器、固定12段及演示恢复，不属于产品API契约：删除评审控制器、数量改真实提交量、恢复按钮受服务端准入约束。HTML缺recovering独立选项，以PRD/AC补齐忙碌状态。旧spec“缺预算未就绪”与本期默认无限冲突，以MODIFIED额度要求替换，不放宽必要认证/仓库配置。

## UI Contract
仅 /chat 既有对话／轨迹执行反馈区域；ExecutionPanel.tsx、TrajectoryView.tsx、DiffView.tsx 与chatApi消费者承接。页面壳、导航、模型选择、停止当前轮次、现有停止确认框保持；不新增配额表单。新增区域在有权限时可见，恢复必须由服务端准入，权限撤销后内容和动作同时不可用。
新增目标 data-testid：chat-storage-panel、chat-storage-stage、chat-saved-result、chat-storage-reason、chat-recovery-action、chat-result-page、chat-result-load-more。既有chat-turn-select/chat-stop-current保持；新增selector均为设计目标，未声称已存在。
正文14px/行高1.45，局部间距12/16/24px、圆角6px、最大宽960px但受既有父容器约束；浅色#F4F6FA/#FFFFFF/#202636/#B9832E/#DDE3EE，深色采用现有tokens对应值。1440与1024卡片自适应，390单列动作换行，长正文仅内部滚动；font/padding/gap/radius允许1px误差，颜色按token精确解析，页面无横向溢出。采样记录width、font、line-height、padding、gap、border、background、color、overflow、focus-visible。
前后台一致性checklist：复用字体/按钮/图标/危险色/焦点与主题；本区域无侧栏和菜单改动，菜单折叠、层级等为保持既有行为；不同阶段文字不只靠颜色。

| 动作 | 原型→目标selector | 浮层与状态 | 验收 |
|---|---|---|---|
| 查看保存结果 | #saved → chat-saved-result | inline-expanded；loading/loaded/error | 真实分页与键盘 |
| 查看原因 | #reason → chat-storage-reason | details；closed/open | 脱敏类别、焦点 |
| 检查/续接 | #recover → chat-recovery-action | 原位；enabled/busy/disabled/error | 重复请求仅一次有效attempt |
| 读后续 | #content → chat-result-load-more | 无浮层；idle/loading/end/error | 不丢游标，可重试读取 |
| 停止当前运行 | 既有chat-stop-current | 既有ChatDialog确认 | 当前运行目标与关闭路径回归 |

Mock/API边界：原型全Mock；Skeleton允许明确标记fixture，正式交付全部真实API。恢复与加载先作为一个动作族实现，不逐按钮补丁。截图仅为历史故障证据，不是一对一复刻来源。

## UI Skeleton
先在现有页面壳插入状态区、保存摘要、原因折叠、结果页容器及动作插槽；用覆盖preparing/running/blocked-before-start/interrupted/unknown/recovering/completed的标记fixture验证结构。截图1440浅深主题并取得首轮确认后才能做UI细节；该确认未发生，不能代填。后端独立任务可继续。最终补齐1440/1024/390 × 深浅主题 ×准备失败/运行中断/未知/完成/加载失败关键状态，computed style与键盘一起验收。

## 容量验证基线（RC-002）
独立测试环境目标：4vCPU、8GiB内存、SSD剩余20GiB；记录实际OS、镜像/commit、数据库版本、磁盘与并发数，实际环境不满足则标记blocked。SQLite及MySQL8各执行同一套关键持久化/迁移/并发测试；容量样本串行，单Chat worker、单执行容器，避免压其他项目。
至少12000文件/600MiB及48000文件/2.4GiB；输出32MiB与128MiB；单文本128KiB、合计8MiB。固定窗口下worker峰值RSS≤512MiB，4倍输出RSS增量≤64MiB；首次600MiB快照≤180秒，32MiB保存≤60秒，已提交256KiB页读取P95≤1秒；API/DB健康采样每秒一次，压力期间99%探测≤2秒、无不可恢复错误。均为实施前冻结的验收目标，尚未实测，不是产品承诺或业务上限。
协议矩阵：普通事件256KiB与1MiB、RPC4MiB与7MiB通过；8MiB边界、8MiB+1拒绝、深度64/65、UTF-8边界、半帧与畸形帧。真实上游最小轮次记录实际协议版本，合成消息不能代替兼容结论。
故障注入含提交前/后崩溃、ENOSPC、DB断连/锁、队列满、容器OOM、停止超时、重复恢复、迁移中断、备份恢复后删除意图重放。无法取得外部终态时如实unknown。

## 观测、文档与风险
product_data_collection_observability:
- status: applicable
- affected_layers: [web, api, db, usage_events, request_logs, task_traces, task_trace_spans]
- reason: 快照、保存、分页、恢复和计量均跨请求与worker；admin及其他客户端无新增入口，对象存储无新对象。
- validation: Web recovery_check/recovery_resume/result_page行为经helper关联behavior_trace_id；API生成可信request_id，worker保留turn/attempt/task_trace_id；snapshot_scan/result_commit/resource_guard/recovery_check span记录计数、字节、耗时、错误。直接API不伪造usage_events。日志不得含prompt、回复、正文、凭证或宿主路径；观测失败可降级，业务结果保存失败必须停止/核验。
同步docs/03-api-index.md、04-database-design.md、02-deployment.md、数据库兼容目录、Chat模块说明、安全和Mintlify受影响页面；规则只在契约真实改变时同步，不为任务重写无关规则。
RC-001/003的设计选择已明确，测试仍待执行；RC-002参数已冻结，环境实测待验证；RC-004契约已定义，Skeleton确认与视觉/真实恢复证据未完成。不勾选产品验收、不声明开发完成。主要风险为DB体积、外部并发写、上游无法重放和性能不足，分别以分块事务/一致性拒绝/unknown核验/固定基线验证处理。


## 文件查看动作补充

`chat-file-content` 按 file_id 关联当前快照文件；`chat-file-read` 原位加载执行前/后正文，`chat-file-compare` 原位显示块差异，两者共享忙碌禁用与错误反馈，不新增弹窗。内容区最大高度360px，保留浏览器键盘焦点；比较范围切换取消旧请求并清空旧页。块编号明确区别于行号。
