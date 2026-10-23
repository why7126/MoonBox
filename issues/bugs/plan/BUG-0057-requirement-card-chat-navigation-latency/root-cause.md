---
bug_id: BUG-0057-requirement-card-chat-navigation-latency
title: 会话准备导航延迟根因分析
created_at: '2026-10-21 09:22:50'
updated_at: '2026-10-21 09:30:17'
owner: 产品团队
root_cause_status: probable
---

# 会话准备导航延迟根因分析

## 根因状态

status: probable

此状态描述根因确定性，不代表 Issue 生命周期。文档补齐不等于根因确认，不进入 pending_review。

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

尚无完整 confirmed 根因。已确认重复同步扫描机制与独立高成本；其对具体慢请求的主导比例仍是强推测。数据库等待、代理/线程排队、资源竞争、重试以及作用域级 reconcile 额外开销未被排除。

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
