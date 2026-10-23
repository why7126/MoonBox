---
bug_id: BUG-0057-requirement-card-chat-navigation-latency
title: 需求卡片动作准备会话导致进入聊天工作台等待过长
severity: high
status: enriching
root_cause_status: probable
owner: 产品团队
created_at: '2026-10-21 09:17:44'
updated_at: '2026-10-21 09:30:17'
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

root_cause_status: probable。

已确认的机制是导航等待同步准备，以及写动作准备中的重复全树快照读取；独立容器采样确认该读取本身可达到十几秒。强推测其是本次 21.27 秒的重要来源，但缺少同一 request_id 下的分段计时，尚不能确认主导比例或唯一根因，不将独立采样相加或与真实请求相减进行归因。

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
