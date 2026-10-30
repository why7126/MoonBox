---
title: 会话准备导航延迟调查历史原文
created_at: 2026-10-30 14:52:26
updated_at: 2026-10-30 14:52:26
---

# 会话准备导航延迟调查历史原文

本文件保存文档分层前的完整原文快照。各段 probable、待补、当前、本轮等表述均属于当时记录，不代表现在的任务或状态。当前结论统一见 [根因分析](root-cause.md)，当前修复验收见 [验收计划](acceptance.md)。截至分层时机制已限定确认为 confirmed，历史21.27秒精确归因未知；未修复、未评审。

快照保留原始 frontmatter、证据 ID、请求 ID、阶段表与结论，围栏内容可按摘要复核。BUG 主文档内微基准引用指本文件第二节；根因原文“下文”仍指第一节内部后续记录。

## 1. root-cause.md 分层前快照

SHA-256：`74a0c098ed000e06cf3c61efb56ada583ff9b8d04dec620593af31c5e44eeab8`

````markdown
---
bug_id: BUG-0057-requirement-card-chat-navigation-latency
title: 会话准备导航延迟根因分析
created_at: '2026-10-21 09:22:50'
updated_at: '2026-10-30 14:21:12'
owner: 产品团队
root_cause_status: confirmed
---

# 会话准备导航延迟根因分析

## 根因状态

status: confirmed

当前确认范围：写动作会话准备同步重复读取治理快照，前端等待该准备返回后才导航，形成进入聊天的秒级关键路径。确认依据是源码链路、两条真实线上同请求计时以及历史 bug-opsx 准入条件的隔离重构。不是确认历史21.27秒的唯一来源或精确占比。下文按时间保留的 probable 结论属于当时证据状态，以本节为当前结论。Issue 仍 enriching，本轮不推进评审。

## 现象

用户截图中的 bug-opsx 对象会话准备 POST 等待响应 21.27 秒，成功复用已有空闲会话；前端在成功回调后才跳转。范围及微基准明细见 [缺陷主文档](bug.md)。

## 证据链

| id | type | source | 摘要与支持边界 |
|---|---|---|---|
| E1 | network_request | 用户截图，bug.md E1/E2 | object-sessions POST 200，Waiting 21.27 秒；reused_conversation=true、idle。证实准备请求慢，未包含可关联的 request_id。 |
| E2 | code_path | src/web/src/pages/catalog/RequirementCenterPage.tsx，openIssueActionDialog | 请求成功后才 pushState，准备耗时位于导航关键路径。 |
| E3 | code_path | src/backend/app/governance/preparation.py，prepare_object_session/_preflight_object_session | 正常写动作路径五次 stable、至少十遍目录读取；已有会话查找在预检后。 |
| E4 | reproduction | bug.md 只读采样明细 | 容器相同调用顺序两轮 16.15/18.60 秒；独立微基准，非原请求 span。 |
| E5 | config_diff | bug.md E5 | 五个部署模块与采样时工作区内容一致，不反推截图时版本。 |
| E6 | data_sample | 本轮只读 SQLite chat_request_logs 查询 | 同接口成功请求 19.260、21.193、80.223 秒；证实后端存在长耗时样本，不能仅凭时长把 21.193 秒与截图唯一配对。 |
| E7 | data_sample | task_traces 按 parent_request_id 关联、task_trace_spans 查询 | 三个上述请求均未直接匹配 trace；一个旧请求关联的会话 trace 包含两次 prepared 状态事件，没有准备子阶段耗时。 |
| E8 | code_path | src/backend/app/governance/observability.py，trace | identity 按会话复用；已有 trace 更新状态但不更新 parent_request_id；span 未携带本次 request_id，不能用旧 parent_request_id 给后续 prepared 事件归因。 |
| E9 | reproduction | 下文授权隔离 ASGI 请求计时 | 四个独立 request_id；两个实际状态副本分支、两个 idle 夹具分支，逐请求阶段计时可复核。仅对隔离运行确认耗时归属，不冒充历史线上请求。 |
| E10 | reproduction | 下文 2026-10-30 浏览器复核 | Chrome 已登录，BUG-0057 卡片“继续完善”完成准备后进入 Chat，草稿尚未发送；确认当前导航路径仍在使用。 |
| E11 | data_sample | 2026-10-30 只读请求审计与会话 Trace 查询 | 同期 POST 5173 ms、200；对应时段 prepared 事件为复用会话，但 trace 仍关联前次请求，缺少本次分段计时。 |
| E12 | config_diff | 当前部署与工作区 preparation.py / observability.py SHA-256 | 两个模块内容一致，prepare 顺序及会话级 trace 复用机制仍存在；不代表所有模块或历史部署一致。 |
| E13 | reproduction | 2026-10-30 受控 ASGI 五请求分段计时，见下文 | 响应请求 ID 与准备函数一致，当前状态副本未经改写；五次均复用 idle 会话，快照读取占 95.85%–97.73%。 |
| E14 | runtime_log | 2026-10-30 正常浏览器请求期间内核只读采样 | 同期接口审计 6432 ms / 200；300 个样点观察数据库读写锁，未捕获内核阻塞队列，但不能排除 SQLite 用户态 busy 等待。 |
| E15 | reproduction | 授权维护重启后两条正常浏览器请求，见下文 | 原服务、真实认证与数据库；响应 ID、准备函数 ID 和审计一致。快照占 97.40% / 96.93%，已测 SQL 与提交为毫秒级，采样后原服务已恢复。 |
| E16 | reproduction | 历史 bug-opsx 准入重构及七组正反例，见下文 | 当前归档态409；仅在内存恢复阶段/Sprint条件后，两条原路由请求200、idle、reused；未改变真实对象或跳过门禁。 |

## 本轮请求级观测

只读连接运行态 SQLite（mode=ro、query_only），仅查询最近六条 object-sessions POST 的请求 ID、时间、状态、耗时及关联阶段名；不读取会话正文、凭证或业务文档。以下时间统一转为北京时间，created_at 是审计创建时间，不是客户端点击时间。

| 审计时间 | request_id | duration_ms | HTTP | 直接关联 Trace |
|---|---|---:|---:|---|
| 2026-10-21 09:17:37 | 99e282cd-f723-4b87-9fd4-e71b37e4f8a5 | 19260 | 200 | 无 |
| 2026-10-21 09:11:03 | 5ad6ce94-31f7-4e72-9089-49bbeb638078 | 21193 | 200 | 无 |
| 2026-10-21 09:09:59 | 78010b8c-021f-4e21-8e90-ac2d31a1718a | 80223 | 200 | 无 |
| 2026-10-21 08:53:29 | 61417950-e3c7-41d8-8067-314093d63d5a | 7128 | 200 | governance.operation |

旧请求 trace 中出现 08:53:29 与 09:17:37 两个 governance.prepared 事件。时间相合不等于可靠的请求关联。现有 span 记录状态而非五次读取及 reconcile 的起止耗时。新查询补足请求级审计证据，未补足同请求分段证据；本次不执行历史准备接口回放，因为准备会提交状态/会话/审计写入，也不能重建历史运行条件。

## 已排除假设

| 假设 | 排除或限制证据 |
|---|---|
| 浏览器排队或下载主导截图中的 21.27 秒 | 图中对应阶段仅微秒/毫秒级。 |
| 本样本新建会话主导 | reused_conversation=true；已有会话查询耗时仍未知。 |
| idle 表示此前无协调工作 | 不成立；reconcile 检查作用域内多个对象，idle 是最终状态。 |
| 注册表单次 YAML 解析足以解释全部等待 | 独立采样约 74–193 ms，不支持此解释；完整对象解析仍未计时。 |

## 已确认根因

写动作 prepare_object_session 在入口一致性检查和动作预检重复读取源/投影快照；reconcile 还可触发额外读取。已有会话查询位于这些同步工作之后，前端又等待准备响应后才切换路由，因此即使复用 idle 会话也承担快照读取成本。E15 两条真实线上请求快照占97.40%/96.93%，已测 SQL、连接及提交为毫秒级；E16 在重构 bug-opsx 准入条件后复现相同返回分支与重复读取路径。由此确认该机制是本缺陷的可复现根因。历史21.27秒请求的精确分解、唯一性及版本回归仍未知，不作为确认范围。

## 修复方向

评估请求内共享有版本与写入围栏保护的快照，避免入口/预检重复扫描；评估协调目标收窄并保留跨对象恢复正确性。前端准备状态反馈可改善体验，不替代性能修复。不跳过权限、阶段、源/投影一致性、占用与幂等检查。

## 验证闭环与剩余缺口

待补证项为同一请求的响应头 request_id 与服务端阶段耗时。已有截图、源码、部署摘要、独立采样、stdout 日志和数据库审计均已检查；历史记录没有所需子阶段 span，无法事后还原，保持 probable。

在下一次自然操作或明确测试对象采样中记录 action、请求 ID、北京时间、HTTP、Waiting、总耗时，并关联授权、入口快照、对象解析、reconcile、visible_state、预检、会话查询、提交的计时及快照次数/重试数。若部署现有观测仍没有这些阶段，须在后续明确授权的诊断实现范围增加计时，不能把缺失值记为零。

返回格式：环境/版本、request_id、action、已有/新会话、各阶段毫秒、文件数量/字节数、协调对象数、重试次数、总耗时；只给派生字段，不提供 Authorization/Cookie、完整 HAR、个人标识或业务正文。截图原件不转存。验收计划见 acceptance.md。

## 授权诊断：同请求阶段计时

用户授权后，以部署代码运行独立进程内 ASGI POST /api/v1/chat/object-sessions。SQLite 通过只读连接备份到内存，所有会话/审计/协调写入限内存副本；真实文件读取保留，Python audit hook 拦截临时沙盒外写入、外部网络与子进程。未修改 src、镜像、生产进程或真实数据库，没有提交 Agent turn，也未创建正式功能 Change。会话登录依赖由现有会话所属用户的测试身份提供，业务层真实空间、对象、阶段权限检查仍执行。这不是通过真实浏览器认证/网络的在线请求。

生产容器没有 TestClient 所需 httpx2；未安装依赖，改用标准 ASGI scope/receive/send 驱动原路由。阶段包装保留原函数返回与异常；使用单调时钟记录嵌套 parent/id、inclusive/exclusive 时长。同请求比较使用不重叠顶层阶段，六个 stable 调用彼此不嵌套，不重复累加父子耗时。临时诊断脚本语法检查通过；四次请求 blocked_actions 均为空。

两种样本严格分开：

- 当前数据库副本：对象已为 needs_review，未改变状态；两轮返回 200、needs_review，分别 11379.813 / 8115.299 ms。请求标识为 1707ea62-79d8-4072-ae03-4b8c8cb971ab、5db712cc-7eed-4ab2-90cf-b84258fc78d2。入口快照为 7494.537 / 6333.413 ms，reconcile 为 2918.057 / 1470.885 ms，因占用门禁提前返回，未执行动作预检。
- idle 夹具：仅在内存副本将目标 execution guard 设为 idle、待审候选改为 rejected、关联会话 active_turn_id 清空；未改真实对象状态。两轮返回 200、idle、reused_conversation=true，执行完整准备分支。除目标夹具变化外继续使用副本中的其他对象协调状态；第二轮使用第一轮执行后的同一内存副本和进程缓存，不是独立冷启动基线。

| 非重叠阶段 | idle 轮一 ms | idle 轮二 ms |
|---|---:|---:|
| 入口授权 | 3.518 | 1.064 |
| 入口执行器快照 | 6074.184 | 5312.318 |
| 对象解析 | 189.114 | 56.781 |
| 状态协调 reconcile | 9880.360 | 1497.479 |
| 可发送状态检查 | 39.639 | 51.902 |
| 动作预检 preflight | 5755.526 | 6027.670 |
| 查找已有会话 | 6.688 | 2.142 |
| 准备状态 trace | 5.326 | 0.810 |
| prepare_total | 22072.265 | 12963.291 |
| ASGI 请求总耗时 | 22227.854 | 13027.500 |

轮一 request_id：70b7b71a-9397-4fa6-8104-b4a9dff32de2；轮二 request_id：9666dba3-68ed-446e-a650-c4eec4404de2。以上 ID 由原 ChatRoute 为本次隔离请求生成，不存在于真实业务数据库审计中。

| 快照位置（stable） | idle 轮一 ms | idle 轮二 ms |
|---|---:|---:|
| 入口投影 | 3383.242 | 1428.863 |
| 入口源目录 | 2600.294 | 3882.343 |
| reconcile 附加快照 | 9447.309 | 1236.372 |
| 预检投影 | 1998.508 | 2411.991 |
| 预检源目录 | 2377.431 | 1501.527 |
| reader 快照 | 1304.780 | 2008.733 |
| 六次 stable 合计 | 21111.564 | 12469.829 |

六次 stable 分别占本次 ASGI 总耗时约 94.98% / 95.72%，每轮记录十二次 read_once；未出现读取重试。预检内部 issue_fact_source 为 55.607 / 87.401 ms；这些是父阶段子项，不再与顶层合计相加。顶层剩余耗时包含未单独包装的逻辑、事务提交及初始化；ASGI 总耗时还含路由审计和框架开销，未声称每条 SQL 均独立计时。

### 结论与边界更新

已直接确认隔离空闲请求中全树快照读取主导准备耗时，同时确认 reconcile 可附加一次昂贵快照。真实截图 21.27 秒与隔离 22.23 秒量级一致，但时长接近不是身份匹配证据。内存数据库不保留真实锁等待/磁盘提交，夹具改变了目标执行状态，当前源树和并发负载也不是历史快照，因此不能确认历史请求的确切占比或排除真实环境其他因素。

整体 root_cause_status 保持 probable，Issue enriching，不推进评审。若要闭合在线归因，仍需在受控诊断部署中为自然请求采集相同阶段；当前持久埋点属于产品观测实现，需独立的已评审需求/Change 流程，不能借未评审 BUG 绕过门禁。已有隔离证据不应再降级描述为只有独立 stable 微基准。

复核方式：使用同版本部署代码、内存数据库副本、同 action 和明确状态分支，驱动原 ASGI 路由；以响应 X-Request-ID 绑定阶段树，确认 stable 数量、read_once 数量及父子耗时不重复统计。诊断脚本仅留临时目录，仓库保留此脱敏事实摘要；无数据库、凭证、原始会话或截图转存。

## 2026-10-30 当前运行态复核

10 月 21 日的隔离计时保留为历史证据。本轮未找到原临时诊断脚本，不能声称原阶段树仍可由已保存脚本直接重放，也不将旧样本当作当前性能基线。

自主取证路径：侧边浏览器访问需求中心转到登录页；切换已有登录态的 Chrome 后成功加载当前看板。BUG-0057 位于规划中，显示“根因待确认”。点击“继续完善”后按钮暂时禁用，随后进入该对象 Chat，输入框预填 bug-complete 命令且发送按钮可用。本轮没有点击发送，没有运行治理 Agent 或推进评审。浏览器正常准备路径会写入 prepared 审计；本轮数据库取证连接本身为只读。

| 审计时间（北京时间） | request_id | duration_ms | HTTP | 关联情况 |
|---|---|---:|---:|---|
| 2026-10-30 12:57:13 | 58fcf8e2-e2c3-4081-a606-ee43350dc1c8 | 5080 | 200 | 会话 trace 的 parent_request_id；prepared 为 new_conversation |
| 2026-10-30 13:01:28 | c6518429-24ca-4bed-9e4f-5de25d17d943 | 5173 | 200 | 按 parent_request_id 查询为空；同会话同秒出现 reused_conversation 的 prepared 事件 |

后一条审计与本轮点击时段一致，prepared 元数据为当前 BUG、action=bug-complete、result=reused_conversation；但浏览器响应头未采集，事件也没有本次 request_id，因此记录为同期交叉证据，不宣称已完成客户端与服务端的唯一请求关联。前次请求的 parent_request_id 下包含本次 prepared 事件，再次证实会话复用会造成请求关联缺口。两条样本均没有准备子阶段起止/耗时。最近八条同接口成功审计耗时范围 5080–24746 ms，混合日期和未知动作条件，不用于前后性能对比。

部署模块与工作区内容指纹一致：preparation.py 为 `676acf7d09be945c962e93c3246b4c23c72aac48758ec8e7a155ad05022c1ddd`；observability.py 为 `36d7df7de069946e02ac4199ecfce1b93a5a0ede227bf62ba670975fd9be1658`。当前 prepare_object_session 仍按入口快照、对象解析、reconcile、visible_state、preflight、会话查找、trace、commit 顺序执行，没有请求级阶段计时。

结论：当前仍有秒级准备等待和明确的观测缺口；5.173 秒不能证明历史问题已修复，也不能证明本次快照占比约 95%。根因维持 probable。已尝试浏览器、当前源码/部署指纹、请求审计及关联事件；现有记录无法补出不存在的分段耗时。

后续补证输入：在具备请求级阶段计时的受控诊断环境，记录一次已有会话写动作的响应 X-Request-ID、action、HTTP、总耗时，以及授权、入口快照、解析、协调、可发送检查、预检、会话查询、提交的毫秒值；附快照次数、重试数和环境指纹。授权仍有效，无需重复申请诊断权限；永久产品埋点仍按项目 Change 流程实施。仅返回上述派生字段，不提交 Cookie、Authorization、完整 HAR 或业务正文。历史截图不要求重新采集。

## 2026-10-30 受控诊断补齐

本轮沿用用户明确授权，重新建立独立进程诊断采样器。使用当前 backend 容器已部署模块与原 FastAPI/ChatRoute/ASGI 路由；真实 SQLite 只读打开后备份到进程内存，所有 DB session 与路由审计重定向到该内存副本。仅认证依赖提供目标已有会话所属用户，业务授权、源/投影校验、占用检查和动作阶段检查仍执行。对象为本 BUG，action=bug-complete；没有修改副本中的对象状态，没有发送 Agent turn。真实目录读取保留，网络、子进程及临时目录以外文件写入由诊断边界拦截。

这是一组原路由的隔离 ASGI 请求，不是线上 HTTP/浏览器请求。首轮为新进程，后四轮共享内存副本与进程缓存；操作系统缓存和主机并发未固定。结果不能作为修复前后对照或线上延迟承诺。初始三轮试采未覆盖 stable_read 独立计时，仅作为采样器调试；以下五轮均使用补齐后的采样器，未合并试采数据。

每个阶段有 id、parent、name、duration_ms、exclusive_ms 和同一 request_id。响应 X-Request-ID 与准备函数收到的 request_id 全部相等。使用单调时钟，父子耗时分开，以下为 prepare 的非重叠直接子阶段；所有时间单位为毫秒。

| 阶段 | 样本1 | 样本2 | 样本3 | 样本4 | 样本5 |
|---|---:|---:|---:|---:|---:|
| 入口授权 | 1.270 | 0.234 | 0.304 | 1.374 | 0.809 |
| 入口快照检查 | 2036.785 | 1686.922 | 1753.241 | 1706.744 | 3063.485 |
| 对象解析 | 94.708 | 22.733 | 22.637 | 22.002 | 96.002 |
| 状态协调 | 1014.269 | 1034.192 | 838.655 | 990.463 | 1271.995 |
| 可发送检查 | 1.790 | 1.010 | 0.684 | 0.671 | 1.546 |
| 动作预检 | 2795.024 | 2151.509 | 1955.331 | 2913.597 | 2271.156 |
| 已有会话查询 | 2.055 | 1.609 | 1.635 | 1.939 | 1.347 |
| 准备事件 | 1.358 | 0.750 | 0.709 | 0.872 | 0.572 |
| 末尾提交（内存） | 0.030 | 0.059 | 0.034 | 0.038 | 0.030 |
| prepare 总耗时 | 5947.955 | 4899.872 | 4573.882 | 5638.863 | 6707.732 |
| ASGI 总耗时 | 5961.042 | 4902.172 | 4575.895 | 5641.524 | 6712.733 |

| 样本 | 响应 request_id | 快照合计 ms | 占 ASGI 总耗时 | 完整 read_once 次数 |
|---|---|---:|---:|---:|
| 1 | 74c12465-8f2a-441f-b7f1-b1f6caea55f3 | 5713.573 | 95.85% | 12 |
| 2 | 4b551a12-e4e6-41ed-bbcf-b9986d5db490 | 4724.342 | 96.37% | 11 |
| 3 | 72f62de3-eb88-435b-a23f-c4b9d15d7638 | 4462.112 | 97.51% | 11 |
| 4 | 9442ed95-2a62-4b04-b5cc-0f2115f93fea | 5513.275 | 97.73% | 11 |
| 5 | ee5e3654-822b-4708-b52f-9f4f3506699f | 6512.975 | 97.02% | 11 |

五次均 HTTP 200、code=0、idle、can_send=true、reused_conversation=true；总耗时中位数为 5641.524 ms。每个请求包含五次 stable（入口两次、协调一次、预检两次）和一次 reader.stable_read。六个快照阶段不互相嵌套，合计不重复计算父子耗时。每个快照覆盖 6818 个文件、20201196 字节；单请求内六次 revision 一致。首轮 reader.stable_read 为 1016.445 ms，后四轮为 336.872、267.183、787.318、363.613 ms。

当前 ProjectReader 已改用 stable_read，后续请求会以缓存内容作候选并进行一次完整独立字节读取，而写动作的五次 stable 仍各读取两遍。因此观察到首轮 12 遍、后四轮 11 遍，未出现额外完整读取；不得把历史“六次 stable / 每轮十二遍”继续描述为当前所有请求的固定行为。采样没有直接枚举协调对象数量，不能推断该数量为零或不变。

验证通过：五次请求 ID 一致、状态分支一致、阶段父子引用有效、exclusive 耗时非负、prepare 子树独占耗时合计与 prepare 总耗时误差小于 0.05 ms；五次 blocked_actions 均为空。Python 语法检查通过。未创建临时容器、网络或卷；临时 Docker 到期预览为 clean 35 / not_due 3，未清理其他任务资源。进程已退出，内存副本随之销毁；没有保存数据库、会话正文或凭证。

可复核本地产物为 `logs/bug0057-20261030/probe.py` 与 `logs/bug0057-20261030/result.json`，均受 Git 忽略，仅供本地诊断；长期事实由本节脱敏表格保存。复跑命令为 `docker exec -i moonbox-backend python -B - < logs/bug0057-20261030/probe.py`，依赖该容器与目标现有会话，输出为新的诊断样本，不能覆盖历史样本。采样器没有长期产品埋点，也不改变 API、DB schema、UI、部署、安全或客户端生成。

产物 SHA-256：

- probe.py：`2c25fcadfdf76f91b07116e4a7a132dd30a51ff87d810a67b0ebe79520f71a51`
- result.json：`f60355efa0d2bd2ea8d0bc382be9859192329911ef5d0d78d76732886aa85e4d`

部署模块 SHA-256（采样进程实际导入文件）：

- app.governance.preparation：`676acf7d09be945c962e93c3246b4c23c72aac48758ec8e7a155ad05022c1ddd`
- app.governance.execution_context：`416986f9701d8892ccd9a66599b3a416023dab1c75feacdf4df5835afda9d139`
- app.governance.reader：`863965a37843aec6091490ca1234ea4c8c5c8b5ec7d15f03b5ab771f34af0732`
- app.governance.snapshot：`0454d93fec7f74af86fd5b5cca85e35a1eb2f0b6e08e5d8573c995fa29ce03ac`
- app.governance.read_snapshot：`a88ab1bddb7b23b7e0dfa2b5fcad20ab9362c4958a2bf955c14383c3ea163a13`
- app.governance.observability：`36d7df7de069946e02ac4199ecfce1b93a5a0ede227bf62ba670975fd9be1658`

**结论边界**：本轮已补齐当前受控请求的分段计时，直接确认这些请求的准备耗时由快照读取主导，已有会话查找与内存提交不是主要成本。未经过真实认证、网络/代理和线上数据库锁/磁盘提交，也未重建历史 BUG-0055 的 bug-opsx 状态与负载；这些差异不能被隔离数据排除。整体根因继续 probable，Issue enriching，不推进评审。剩余缺口收敛为自然线上请求关联及真实数据库/排队因素，不再笼统描述为“没有同请求分段计时”。

product_data_collection_observability: applicable；affected_layers: API、请求审计、准备函数阶段观测（仅诊断进程）。validation: 五请求身份、阶段树、独占耗时和隔离边界校验通过。持久观测存储、Web 行为采集、DB schema、权限和部署变更为 N/A，原因是本轮只进行隔离采样及文档补证。

## 2026-10-30 自然请求与数据库等待核对

本节“线上”指用户此前截图相同的本地运行服务，并非远程生产 MySQL。Chrome 已登录需求中心，点击本 BUG 的“继续完善”，成功进入原有 Chat；命令保留为草稿，未发送 turn。同期最新 object-sessions POST 审计：request_id=`bfdcb9c5-678a-4b9c-8e31-dc46f4aadb34`，created_at=2026-10-30 13:54:35 北京时间，duration_ms=6432，HTTP 200。没有采集浏览器响应头，因此仍属于时间窗关联，不能冒充浏览器到服务端的唯一请求关联。

与点击并行运行只读探针，每约 100 ms 读取数据库文件对应的 /proc/locks 记录和 PID 1 的线程等待通道。核对 PID 1 为 uvicorn，数据库 journal_mode=delete。采样窗口为 13:54:24.472–13:54:55.131，共 300 个样点；全窗口读锁记录出现 9 次、写锁记录出现 3 次，未出现标记为阻塞等待者的记录。这些次数是离散采样记录数，不是事务次数、锁持续时间或独立持锁者数量。

审计创建时间精度为秒；按总耗时反推并向前后放宽约 1 秒的近似窗口 13:54:27.568–13:54:36，共 82 个样点，其中 3 个样点存在数据库锁，阻塞队列记录为零。该窗口不是精确的请求开始/结束 span。全窗口可见 futex_wait、epoll、可运行/不可解析的 0 通道，以及一个 hrtimer_nanosleep 样点；线程未绑定 request_id，不能将睡眠通道归因于当前 SQL。

证据限制：SQLite busy handler 可采用非阻塞加锁失败后睡眠重试，不必出现在内核阻塞锁队列；100 ms 间隔也可能遗漏短等待。故“未捕获内核等待者”不等于 SQL 等待 0 ms，不排除真实磁盘提交、连接池等待或其他线程竞争。本次没有发起测试写锁、BEGIN IMMEDIATE、checkpoint 或改动 PRAGMA，避免人为制造争用。

当前源码核对：object-sessions 准备函数没有请求阶段计时；ChatRoute 的 Server-Timing 依赖 governance_reader.timings，不能自动覆盖本接口。数据库连接配置 busy_timeout=30000 仅为等待上限配置，不是当前请求实际等待。运行环境没有 py_spy/debugpy 模块；本轮未安装调试器、注入正在运行的进程或重启服务。

本地产物：`logs/bug0057-20261030/live_wait_probe.py` 和 `logs/bug0057-20261030/live_wait.json`，受 Git 忽略，内容仅为派生锁类型、采样时间和等待通道，不包含 SQL 文本、参数、凭证、会话或文件正文。

**剩余阻碍与执行条件**：在现有进程没有阶段/SQL 计时的条件下，继续查审计或重复内核采样无法还原精确的同请求 SQL 等待。需要当前后端通过受控启动加载临时诊断钩子：请求 ID 贯穿准备阶段，分别计量 SQL 执行、连接获取和事务提交；SQL 只记类型/耗时/错误类别，不记语句或参数。数据库执行耗时包含执行与等待，未取得 busy-handler 或等价直接证据前不能全部命名为锁等待。诊断授权继续有效，但加载方式涉及当前服务短暂重启，运行安排已向用户提出，未擅自中断其他任务。恢复步骤为移除临时启动钩子并重启原服务，检查健康及业务入口。根因保持 probable、状态 enriching，不推进评审。

## 2026-10-30 授权临时钩子的线上同请求计时

用户明确选择短暂维护重启。维护前查询无 queued/running Chat turn，备份容器原 main.py；仅在现有容器可写层临时添加启动导入及计时模块，仓库 src、正式镜像、Compose、API schema 和 DB schema 未修改。原 Uvicorn 启动命令不变。临时钩子通过 ContextVar 关联实际响应 X-Request-ID 与准备函数请求 ID，计量各准备阶段、SQLAlchemy Session.execute、Engine.connect、Session.commit，以及 cursor_execute 前后耗时。SQL 文本、参数、用户身份、认证信息与业务正文不进入日志。

通过正常已登录 Chrome 在需求中心点击本 BUG 的“继续完善”，由原前端、代理、后端和真实数据库执行；两轮均进入既有 Chat，未点击发送。首轮诊断尝试因短对象 ID 未匹配而未产生计时，修正目标匹配并重启后取得以下两个有效样本；未将未记录样本伪装成成功采样。

| 样本 | 响应/准备函数/审计共同 request_id | 完成时间（北京时间） | HTTP | 审计耗时 ms | 中间件总耗时 ms |
|---|---|---|---:|---:|---:|
| 1 | 38992a67-f143-4d26-90dd-ed4ec0b33606 | 2026-10-30 14:07:14 | 200 | 7033 | 7045.404 |
| 2 | abb3e7b8-6888-47ac-a0d0-953507321dcc | 2026-10-30 14:08:03 | 200 | 6372 | 6380.159 |

响应 ID 在服务端实际发送响应时捕获，并与准备函数参数、真实 chat_request_logs 唯一匹配，不再依靠相近时间猜测请求归属。中间件时间包含响应发送与路由结束开销，审计是在其内部创建，因此两种总耗时不要求相等；未测量浏览器点击前或请求到达中间件前的网络/代理排队。

| prepare 直接子阶段（不重叠，ms） | 样本1 | 样本2 |
|---|---:|---:|
| 入口授权 | 1.517 | 2.348 |
| 入口快照检查 | 2568.123 | 2776.553 |
| 对象解析 | 22.859 | 32.519 |
| 状态协调 | 901.407 | 1034.729 |
| 可发送检查 | 2.073 | 2.512 |
| 动作预检 | 3510.161 | 2491.707 |
| 已有会话查询 | 5.734 | 5.817 |
| 准备事件 | 6.937 | 6.542 |
| prepare 末尾提交 | 0.045 | 0.074 |

六个不嵌套快照阶段（五次 stable 加一次 stable_read）分别合计 6862.394 / 6184.268 ms，占中间件总耗时 97.40% / 96.93%；read_once 次数为 12 / 11。两次均 action=bug-complete、idle、can_send=true、reused_conversation=true。该结果直接确认当前两条真实服务请求的主要耗时来自快照读取，且与隔离五样本方向一致。

| 数据库测量（ms） | 样本1合计 | 样本1最大 | 样本2合计 | 样本2最大 |
|---|---:|---:|---:|---:|
| cursor_execute（各33次） | 15.224 | 3.757 | 20.531 | 4.195 |
| Session.execute | 18.739 | 4.643 | 25.700 | 4.490 |
| Engine.connect | 0.581 | 0.148 | 1.626 | 0.776 |
| Session.commit（含请求内其他提交） | 5.354 | 3.563 | 8.250 | 5.892 |

这些测量存在嵌套，不能相加冒充数据库总耗时。cursor_execute 包括执行及其内部等待，不能把全部时长命名为锁等待；本轮未安装 SQLite busy handler，不报告“锁等待精确为零”。独立 Result.fetch 调用未逐一包装，连接获取包含在 Engine.connect 中但未单拆池等待。已测执行/连接/提交均为毫秒级，且快照已解释约97%的请求时间，因此不支持数据库长等待主导这两个样本；不能排除其他负载下或历史请求中发生锁争用。

恢复与验证：导出脱敏 JSONL 后，先比较当前 main.py 与本次临时版本指纹，确认未被他人修改，再恢复原文件。清理临时模块时因 docker cp 属主触发一次权限失败，随后仅针对本次模块及其 pycache 使用容器 root 清理并核验。原启动文件 SHA-256 恢复为 `207e7e4cc9b322a63292e3a8050a2e4f26d3a38990ef6c1fbaafdcdaa0dea046`。服务再次重启，/health 返回200；诊断中间件、模块和容器临时日志均无残留，导出样本保留在本地 Git 忽略目录。没有创建新容器、网络或卷。

本地产物：`logs/bug0057-live/hook.py`、`results.jsonl`、`main.original.py` 和 `main.instrumented.py`，仅供本地复核，不能作为永久功能部署。导出样本有2个请求，身份一致性、阶段 ID 唯一及独占耗时非负检查通过。长期脱敏事实由本节表格保存。

- hook.py SHA-256：`be337f1318e5b95a29b1e5724b56561907eb51e8c483fff857c303e9bf5e25e0`
- results.jsonl SHA-256：`d0f4c390fdeb598ff390c5c00863ae811fdd2d6425849651f00e94929f14bc29`

**状态与边界**：当前两条线上请求中“重复快照读取主导准备耗时”已取得直接证据，不再把当前线上阶段归因写成待采集。整体 BUG 根因仍保留 probable：原截图对象 BUG-0055 的 bug-opsx 请求为历史21.27秒，未取得同一历史请求的阶段记录，也未重建其动作、负载及全部状态；不将当前约97%的比例外推到该历史请求。未进入 pending_review、Sprint 或 Change。后续若继续调查，范围应是历史触发条件/其他写动作的复现或修复方案验证，而非再次重复要求本轮已获得的在线分段计时。

product_data_collection_observability: applicable；affected_layers: API、请求审计、准备阶段与数据库调用（临时诊断）。validation: 两请求响应/准备/审计 ID 一致，阶段与数据库计时完成，原服务指纹和健康恢复通过。永久存储、API 契约、客户端生成、DB schema 和权限策略为 N/A，未发生变更。

## 2026-10-30 历史 bug-opsx 触发条件可复现性

只读核对历史对象 BUG-0055：当前 registry/trace 均 done、目录 archive、iteration=sprint-011；sprint-011 已 completed 并位于 iterations/archive。trace 记录2026-10-21 08:52:20评审通过，随后进入 sprint-011，17:13:02归档；与用户截图中 bug-opsx 返回200相容，但不足以重建该时刻全部环境。聚焦 Git 历史未找到 plan/review 阶段 trace 提交；当前 archive 路径可追溯到7c18373f（2026-10-23），已是归档状态，不能将其称为截图时精确版本。该提交的准备代码仍具有入口快照、reconcile、preflight、已有会话查询的相同顺序，只用于机制连续性佐证。

### 准入条件正反例

直接调用现有 _require_issue_fact_source，构造纯内存最小事实源，未连接或改写数据库。七组结果均符合预期：

| 条件 | 结果 |
|---|---|
| 对象已归档 done | 拒绝，2604 |
| 仅 approved，尚未 in_sprint | 拒绝，2604 |
| registry 与 trace 阶段不一致 | 拒绝，2604 |
| 缺少活动 Sprint 文件 | 拒绝，2604 |
| Sprint 正式 bugs 范围不包含对象 | 拒绝，2604 |
| Sprint 已 completed | 拒绝，2604 |
| registry/trace 均 in_sprint，归属活动 Sprint 且列入正式范围 | 通过 |

因此直接在当前归档对象上再次点击/提交 bug-opsx 不能代表历史场景；也不能为复现而把真实归档对象回退。

### 原路由受控复现

复用已验证 ASGI 诊断脚本，读取当前部署代码，真实数据库只读备份到内存；将目标改为 BUG-0055、action=bug-opsx，不改数据库副本中的 guard、候选或会话状态。基线使用当前真实事实源，得到 request_id=6acbecee-2e60-4e8e-aa3e-5d6f5aeb3e99，HTTP409/code2604/governance_validation_failed，8619.774 ms。它证明当前条件不满足，不是历史响应复现。

重构样本只修改 read_once 返回的内存字节映射：目标 registry 与 trace 改为 in_sprint、iteration=sprint-011；由归档 Sprint YAML 派生活动路径副本，状态设 active，并保留正式 bugs 范围。保留当前归档目录路径和其他当前内容，故它是准入条件重构，不是历史目录/代码/数据规模的完整还原。snapshot 校验、权限、版本一致性和原动作门禁仍执行；不 mock 返回200，不跳过 preflight。新增逻辑路径仅补齐内存 identities 映射，使缓存校验能够处理夹具；真实磁盘不写入。首次夹具尝试因该映射缺失失败，修正后下列样本才有效。

| 指标 | 样本1 | 样本2 |
|---|---:|---:|
| HTTP / code | 200 / 0 | 200 / 0 |
| ASGI 总耗时 ms | 8555.143 | 7318.448 |
| 快照阶段合计 ms（含夹具转换） | 8222.836 | 7140.644 |
| 其中夹具字节转换 ms | 772.339 | 703.557 |
| 完整 read_once 次数 | 12 | 11 |
| 入口快照检查 ms | 3207.424 | 2833.421 |
| reconcile ms | 1361.946 | 1257.110 |
| preflight ms | 3870.122 | 3184.672 |
| 已有会话查询 ms | 4.151 | 1.728 |

样本1 request_id=dd3b67a6-f7dc-46d5-9859-da33b3a31989；样本2=b1e5655c-349f-4bf5-885e-7aed9322ca8d。响应 ID 均与准备函数 ID 一致，两次均 action=bug-opsx、idle、can_send=true、reused_conversation=true，blocked_actions 为空。第二轮共享内存副本/进程缓存，不是独立冷启动。夹具转换开销已单列，不用相减结果冒充线上净耗时；更不以8.56/7.32秒替代历史21.27秒。

### 确认依据与未确认事项

E1提供实际症状和成功复用分支；E2/E3提供前端等待及后端同步路径；E15直接量到真实线上请求中快照读取约占97%，排除这些样本被已测数据库长调用主导；E16验证历史动作需要的准入条件，并在未绕过门禁的原路由中复现相同 idle/reused 分支和重复读取。因此根因确认范围可收敛为“重复同步快照读取处于导航关键路径”，无需以无法回溯的历史精确占比作为该机制确认的前提。

仍未确认：历史请求独有的代理/线程排队、磁盘/锁争用、准确数据规模与并发、精确各阶段占比，以及是否某版本引入。上述未知不被置零，也不扩张为“所有延迟都来自快照”。当前未实施请求内快照共享或性能修复，不声称验收通过。

本轮未重启服务、修改真实数据库、回退BUG-0055/Sprint或执行治理命令；仅写入本BUG证据文档及Git忽略的本地诊断产物。产物位于 logs/bug0057-historical/：probe.py、current.json、reconstructed.json、gates.py、gates.json。原路由隔离请求与纯函数准入验证分别标注，不把后者当线上证明。

- probe.py SHA-256：`1df5b5c8261865de2bf7ce8a744f95c47c3c8f860b0bf5101845deb5c14666f4`
- current.json SHA-256：`ff2711095758540c1b80e30d6a84ec85ebf3fbcd07d87cdd6063b21f4748f34a`
- reconstructed.json SHA-256：`023bbf4f1c28c2413f2e47751332e63d7cc14399caae14727944486024dddc66`
- gates.py SHA-256：`575c05f799b8153b3903cc097124a041a2c7ef21aaea7c7d7eaf8f79e3ce5311`
- gates.json SHA-256：`e14a239fc236eb5d0fdca03e285342e7d1dfe516e7137633e0b0326dbee7cf6f`

结论：root_cause_status=confirmed（上述限定机制）；Issue仍enriching，reviewed/approved保持null，不推进评审、Sprint或Change。product_data_collection_observability: applicable；affected_layers: API准备链路诊断；validation: 七组准入正反例及两条隔离原路由请求通过。API/DB schema/UI/部署/安全/客户端生成无实现变更。
````

## 2. bug.md 分层前快照

SHA-256：`aabe3dbf635d01bc59d72a194d55bb04c54d0753494f5c87b5e67cd5071cbced`

````markdown
---
bug_id: BUG-0057-requirement-card-chat-navigation-latency
title: 需求卡片动作准备会话导致进入聊天工作台等待过长
severity: high
status: enriching
root_cause_status: confirmed
owner: 产品团队
created_at: '2026-10-21 09:17:44'
updated_at: '2026-10-30 14:21:12'
discovered_at: '2026-10-21 08:50:06'
environment: local
source: capture、用户提供的浏览器截图与同会话容器只读采样
related_requirement: null
related_change: null
iteration: null
---

# 需求卡片动作准备会话导致进入聊天工作台等待过长

## 现象与范围

需求中心治理卡片动作在进入 Chat 工作台前等待过长。已取得 BUG 对象执行 bug-opsx 动作的真实样本：POST /api/v1/chat/object-sessions 返回 200，Waiting for server response 为 21.27 秒，响应下载仅 4.39 ms。响应为 reused_conversation=true、execution_state=idle、can_send=true，说明复用已有会话也存在准备延迟，并非该样本在创建新会话或执行 Agent 命令。

本 BUG 覆盖点击动作至准备返回、路由切换的阶段；进入后的历史加载属于 BUG-0058，消息提交 POST /conversations/.../turns 属于 BUG-0059，不混用它们的时长。截图中的对象 BUG-0055 是采样业务对象，不是本缺陷的修复链路。

## 复现步骤与结果

1. 在本地需求中心选取已满足 bug-opsx 前置条件、已有对应会话的 BUG 对象；保留 DevTools Network 记录。
2. 点击该对象的治理动作，观察 POST /api/v1/chat/object-sessions；本次用户提供样本的 action 为 bug-opsx。
3. 记录点击、请求发出、响应完成、路由切换、聊天页面可交互时刻；查看 Timing、状态码和脱敏响应。
4. 实际：该 POST 等待响应 21.27 秒，成功返回已有空闲会话。前端在请求成功后才执行 pushState，因此准备等待处于导航关键路径。截图不包含完整点击至可交互计时，不能将 21.27 秒当作全部页面加载时长。
5. 期望：及时反馈准备状态，在保留权限、版本和执行占用门禁的前提下减少不必要的重复准备，尽快进入正确会话。量化性能门槛待后续验收设计明确，不伪造已有 SLA。

真实慢请求目前为单个完整截图样本；重复只读采样证明快照成本可重复出现，不等同于两次真实接口复现。

## 证据摘要

| ID | 类型 | 来源 | 结果与边界 |
|---|---|---|---|
| E1 | network_request | 用户提供的四张 object-sessions 截图：请求列表、Timing、Headers、Response | POST /api/v1/chat/object-sessions，200；Waiting 21.27 秒；Queueing 1.15 ms、Stalled 0.41 ms、DNS 14 μs、连接 0.32 ms、发送 0.11 ms、下载 4.39 ms。 |
| E2 | data_sample | 同组 Response 截图 | action=bug-opsx；reused_conversation=true；execution_state=idle；can_send=true；reason_code=null。不保存会话标识和凭证。 |
| E3 | code_path | src/web/src/pages/catalog/RequirementCenterPage.tsx，openIssueActionDialog | object-sessions 成功回调后才保存命令草稿并 pushState 跳转；响应等待阻塞导航。 |
| E4 | code_path | src/backend/app/governance/preparation.py，prepare_object_session、_ensure_executor_snapshot、_preflight_object_session | 写动作入口先执行一致性检查，预检中重复检查，然后 reader.snapshot；已有会话查找位于预检之后。正常无重试路径至少五次 stable、十遍目录读取。 |
| E5 | config_diff | 同会话后端容器与工作区内容摘要比较 | preparation、execution_context、reader、snapshot、chat/relations 五个模块内容一致；仅确认采样时部署与工作区一致，不反推截图时镜像版本。 |
| E6 | reproduction | 同会话后端容器 python -B 只读快照采样 | 按投影、源目录、投影、源目录、投影的顺序调用部署代码 stable，两轮累计 16.15 秒、18.60 秒；4350 个文件、14977965 bytes。未调用业务 API、未创建会话、未写业务数据。 |
| E7 | runtime_log | 同会话后端容器近两小时日志聚焦筛选 | 找到三条 object-sessions POST 200 记录；输出未提供同请求分段耗时，不能与截图精确关联。 |
| E8 | code_path | src/backend/app/governance/execution_context.py，reconcile | 查询当前用户在项目作用域下 running/needs_review 对象，未按本次 object_id 限定；符合终态恢复条件时可能追加快照与校验。实际样本处理了哪些对象未知。 |

截图仅作为本会话用户提供的证据，仓库保留上述脱敏摘要，未复制原始截图。Headers 原图含凭证，不落盘、不转录；原始临时图片不是长期证据文件引用。采样输出也只保留文件数量、字节数、阶段耗时等派生事实。

生成后补证：继续检查 `src/backend/app/chat/api.py` 的 `ChatRoute`、`src/backend/app/governance/api.py` 的 `create_object_session` 和 `src/backend/app/governance/observability.py`。当前路由审计记录 request_id 与整体 duration_ms；治理 trace 记录 prepared 等状态事件，所检查的准备函数没有覆盖上述五次快照及 reconcile 的独立计时。因此整体审计可作为后续关联入口，但不能替代同请求阶段耗时；本轮未查询原请求审计行，不声称已取得其 duration_ms。根因保持 probable。

## 只读采样明细

| 阶段 | 次数 | 第一轮 ms | 第二轮 ms |
|---|---:|---:|---:|
| 入口一致性检查：投影 | 1 | 2613.96 | 4999.81 |
| 入口一致性检查：源目录 | 1 | 3375.48 | 2261.16 |
| 预检一致性检查：投影 | 1 | 3509.42 | 3136.74 |
| 预检一致性检查：源目录 | 1 | 4640.82 | 4856.76 |
| reader 稳定快照读取部分：投影 | 1 | 2011.88 | 3344.75 |
| 合计 | 5 | 16151.56 | 18599.22 |

该采样仅执行 stable，未执行完整 prepare_object_session、数据库围栏、权限检查、对象解析、reconcile 或会话查询；表中阶段名表示代码顺序映射，不是原请求的埋点 span。单独 BUG 注册表 yaml.safe_load 为 73.60 / 192.88 ms，也不能代表完整 resolve_object 耗时。采样时树规模与之前 BUG-0059 的 4342 文件不同，不混用数据规模或直接推算占比。

## 根因判断与排除边界

root_cause_status: confirmed。

根因已确认，范围限定为：写动作准备重复同步读取治理快照，前端等待准备响应后才导航。两条真实线上同请求计时显示快照占97.40%/96.93%；历史bug-opsx准入重构复现相同复用空闲会话分支。未确认历史21.27秒的精确占比、唯一来源或版本回归，不将隔离样本替代历史请求。详见root-cause.md E15/E16。

- 本样本浏览器排队、连接、发送及下载为微秒/毫秒级，不支持它们是主要耗时来源。
- reused_conversation=true 排除本样本由创建新会话主导的解释；不排除已有会话查询耗时。
- idle 仅为最终状态，不排除 reconcile 先处理其他对象或恢复状态的耗时。
- 等待响应包含服务器、代理和服务排队等时间，尚未排除数据库锁、资源竞争及源目录读写变化。
- 同屏 conversations 18.25 秒、objects 13.59 秒仅为关联线索；context canceled 不等于服务端报错或超时。
- 是否版本回归未知；没有同规模旧版本对照。只读动作和“查看执行”直接导航分支不同，不将所有按钮一概判为同一机制。

## 待补同请求计时与操作指引

已尝试用户自然操作截图、源码调用链、部署内容对比、容器快照采样、后端请求日志；仍缺原请求的 request_id、完整服务端阶段耗时与当时并发状态。不要为补证在真实业务对象重复执行治理命令。

后续在获授权测试对象或下一次自然操作中：

1. 在 Network 定位 object-sessions POST，从响应头读取可用的 request_id；记录时间、环境版本、action、HTTP 状态、Waiting 与总时长。不要采集 Authorization、Cookie、请求正文原文或完整 HAR。
2. 由可用服务端观测按同一 request_id 关联：授权、入口快照、对象解析、reconcile（对象计数/分支）、visible_state、动作预检快照、版本重试、已有会话查询、提交及总耗时。
3. 若现有观测没有这些阶段，不将缺失视为零；在后续获准的实现/测试范围补分段计时，再做同规模对照。本命令不修改运行服务或新增埋点。
4. 返回格式：时间、环境/版本、action、request_id、状态码、Waiting/total_ms、各阶段 ms、快照次数/重试次数、文件数量/字节数、reconcile 对象计数、已有/新会话。对象及个人标识用匿名标签，禁止凭证和原始业务文档。

## 影响范围与严重等级

severity: high。核心治理入口存在 21 秒级等待，影响用户进入聊天并继续研发工作。当前直接样本为已有会话的 bug-opsx；其他写动作共享部分准备路径，但需分别验证。无数据丢失、安全事故、全站不可用或必须紧急上线的证据，建议常规修复。

## 修复方向与回归建议

优先评估单请求复用已验证快照，减少入口与预检重复全树读取；保持写入围栏、源/投影版本一致性、权限、对象阶段、占用及幂等约束。评估 reconcile 是否可以收窄到目标对象，同时防止遗漏跨对象恢复义务；前端准备反馈只能改善可感知性，不能替代性能修复。

后续回归覆盖已有/新会话、只读/写动作、执行占用、版本推进和持续变更、无权限、失败重试、重复点击；验证不会重复创建会话、绕过门禁或错配命令草稿。点击至路由、接口准备、路由至历史可见分别计时；同规模多样本验证性能，不能用一次微基准替代接口验收。

## 关联与观测声明

关联调查：BUG-0056（看板上下文）、BUG-0058（历史读取）、BUG-0059（消息提交）；共享成本尚不代表共同根因确认。当前无关联 REQ、Sprint、OpenSpec Change；本命令仅生成主文档并同步 draft，不生成 root-cause.md 或推进评审。

product_data_collection_observability:
- status: applicable
- affected_layers: Web、API、request_logs、Task Trace
- reason: 后续归因需要请求与阶段耗时关联；本次仅整理证据，不变更采集契约。
- N/A: DB schema/索引、对象存储、部署、安全权限和客户端生成均未修改，当前没有扩大这些变更范围的依据。
- validation: 截图 Timing/响应、聚焦源码、部署内容摘要一致性、两轮容器只读采样和日志筛选；同请求分段计时待补。

## 补齐进展

已补齐 [根因分析](root-cause.md)、[临时规避](workaround.md)、[验收计划](acceptance.md)。本轮审计取得请求级耗时与 Trace 关联缺口，详见根因分析 E6–E8；此前“未查询审计行”仅描述 generate 阶段。状态 enriching、根因 probable，不推进评审。

## 请求级诊断进展

用户授权后完成隔离 ASGI 请求阶段计时：idle 夹具两轮 22.23/13.03 秒，六次 stable 占约 94.98%/95.72%；当前状态副本为 needs_review，另行记录。详见 root-cause.md 的“授权诊断”。这是同请求计时，区别于此前微基准，也不冒充原截图线上请求。生产代码、服务、数据库未修改，整体 probable/enriching，不推进评审。

2026-10-30 续查：通过已登录 Chrome 对 BUG-0057 点击“继续完善”，成功进入 Chat，命令未发送。同期审计为 5173 ms / 200，复用会话的 prepared 事件仍关联前次请求，缺少本次阶段耗时；两个相关部署模块与当前源码指纹一致。旧隔离样本不作为当前性能基线，当前仍保持 probable/enriching。完整证据和采样缺口见 root-cause.md 的“当前运行态复核”。本轮仅补证与文档更新；API、DB schema、UI、部署、安全和客户端生成无实现变更。

2026-10-30 13:44:24 续查已补齐五个当前受控 ASGI 请求阶段计时，耗时中位数 5.642 秒，快照占 95.85%–97.73%；当前读取器缓存使完整读取从首轮 12 次变为后续 11 次。原请求阶段身份、隔离边界及剩余线上因素见 root-cause.md。整体 probable/enriching 保持。

2026-10-30 13:56:26：自然浏览器请求同期审计 6432 ms / 200；并行 300 点只读内核采样观察到数据库读写锁，但未取得同请求 SQL 等待时长，不能排除 SQLite 用户态重试。精确线上分段仍需当前进程加载诊断钩子，服务运行安排待明确。

2026-10-30 14:10:41：完成两条正常浏览器线上请求分段计时，响应/准备函数/真实审计 ID 一致。快照占 97.40% / 96.93%，已测 SQL 执行、连接与提交为毫秒级。临时钩子已移除、原服务恢复且健康通过。当前样本归因已直接证实；历史21.27秒请求归因仍未闭合，整体 probable/enriching。

2026-10-30 14:21:12：历史触发条件核对完成，当前归档态拒绝、内存恢复准入条件后两次bug-opsx成功复用idle会话，七组门禁正反例通过。机制根因确认为confirmed；本轮仍保持enriching，不推进评审。
````

## 3. acceptance.md 分层前快照

SHA-256：`f7fe6cbad0783cfe182ce8de9c0551d57ddda0163fd8a95400359e776e6edb84`

````markdown
---
bug_id: BUG-0057-requirement-card-chat-navigation-latency
title: 会话准备导航延迟验收计划
created_at: '2026-10-21 09:22:50'
updated_at: '2026-10-30 14:21:12'
owner: 产品团队
acceptance_status: not_started
---

# 会话准备导航延迟验收计划

## 验收状态

acceptance_status: pending

以下为待实施、待执行计划，不表示测试通过；未创建 Change，无性能修复实现。

| AC | 验收内容 | 证据与通过条件 |
|---|---|---|
| AC-01 | 同请求耗时归因 | 一个 request_id 可关联浏览器与所有准备阶段；解释主要耗时、读取次数及重试；缺失阶段显式报告，不能以独立微基准替代。 |
| AC-02 | 已有会话的写动作性能 | 同部署、同数据规模、同并发条件前后各至少五个样本，比较中位数与最大值；性能阈值在修复方案评审时确定，禁止仅凭主观变快通过。 |
| AC-03 | 新会话与已有会话 | 已有会话保持复用，新会话不重复创建，返回目标与命令草稿一致。 |
| AC-04 | 一致性与并发 | 源/投影不一致、读取中写入、持续更新、版本推进时按契约重试或阻断，禁止复用过期快照。 |
| AC-05 | 权限和流程门禁 | 无权限、错误阶段、执行占用、待审候选仍正确拒绝或引导，不因减少读取绕过检查。 |
| AC-06 | 幂等与失败交互 | 重复点击、网络失败、重试不产生重复会话/动作；准备状态可辨识，失败提示可恢复。 |
| AC-07 | 只读与直接查看入口回归 | 只读动作、“查看执行”不误走写动作门禁；准备导航与历史加载分别测量。 |
| AC-08 | 状态协调与观测 | 如收窄 reconcile，目标与相关对象恢复语义不回退；复用会话的每次请求均可独立归因，日志不包含凭证/业务正文。 |

## 验收结果回填

```yaml
acceptance_status: not_started
accepted_at: null
accepted_by: null
source_change: null
source_sprint: null
evidence: []
failed_items: []
source_event: bug.enrich
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 观测声明

product_data_collection_observability: applicable；affected_layers: Web、API、request_logs、Task Trace。validation: 已有请求级观测和采样，阶段证据待补。DB schema、部署、权限策略、对象存储及客户端生成未变更，暂为 N/A；后续方案若触及须重新评估。

## 诊断证据补充

AC-01 已取得隔离 ASGI 同请求阶段树，尚未取得线上原请求全阶段计时；不得标记修复验收通过。完整数据及夹具差异见 root-cause.md。其他 AC 未执行，未实现性能修复。

2026-10-30 复核：当前浏览器准备导航成功、命令未发送；同期请求审计 5173 ms，仍缺本次 request_id 的子阶段计时。AC-01 未闭合，AC-02 无同条件前后样本，均不得判为通过。历史临时诊断脚本本轮未找到，后续重放需重新建立受控采样并保存脱敏可复核产物。其他 AC 仍未执行。

2026-10-30 13:44:24 受控诊断补证：五个原 ASGI 路由请求的响应 ID 与阶段树绑定验证通过，当前状态副本不改写；分段归因已补齐，快照占 95.85%–97.73%。AC-01 的线上关联部分仍未闭合；AC-02 未形成修复前后同条件对照，不宣称性能修复验收通过。详见 root-cause.md“受控诊断补齐”。

2026-10-30 13:56:26：补入正常请求与内核锁采样，AC-01 线上阶段/SQL 计时仍未闭合；零内核阻塞队列不作为零数据库等待证据。

2026-10-30 14:10:41：AC-01 当前线上请求阶段关联与计时已补齐（两条响应/准备/审计 ID 一致），数据库执行/连接/提交已计时但未直接计量 busy-handler 等待。未实现性能修复，AC-02 前后对照及其他修复验收仍未执行；历史原请求仍不能回溯归因。

2026-10-30 14:21:12：历史bug-opsx准入重构两次成功，七组正反例符合预期；仅证明触发条件和原准备机制，未实现性能修复。AC-01诊断机制确认完成，历史精确比例保留未知；其余修复验收不因此转为通过。
````
