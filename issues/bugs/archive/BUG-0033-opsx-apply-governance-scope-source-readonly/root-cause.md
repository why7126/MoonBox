---
bug_id: BUG-0033-opsx-apply-governance-scope-source-readonly
title: 产品内执行 opsx-apply 源码只读根因分析
status: confirmed
owner: 产品团队
created_at: 2026-10-06 22:32:47
updated_at: 2026-10-07 16:55:05
---

# 产品内执行 opsx-apply 源码只读根因分析

## 根因状态

status: confirmed

已用原失败轮次的实际 profile、产品页面、当前服务端完整策略结果和仅修改两个字段的内存对照确认根因。原轮次的服务端 `reason_code` 未单独留存，该历史字段仍标为不可直接观测。

## 现象

用户报告已纳入 Sprint 的对象执行 `/opsx-apply` 时获得治理写权限，源码只读。现已定位原失败 turn、实际 `moonbox-governance` profile、BUG-0029 的 Change 字段及原会话阻塞表现；完整策略内存对照确认字段契约不兼容。原始现象和复现步骤见[缺陷主文档](bug.md)。

## 证据链

| id | type | source | 摘要 | 支持的判断与限制 |
|---|---|---|---|---|
| E1 | reproduction | capture.md、bug.md 用户反馈 | 报告实现命令被治理权限阻断 | 尚未独立复现，无失败 turn 直接证据 |
| E2 | code_path | src/backend/app/chat/policy.py:19、:73 | 实现检查失败后可进入治理写权限分支；准备候选分支位于该检查之前 | 存在候选路径，不能证明本次命中 |
| E3 | code_path | src/backend/app/chat/relations.py:62 | REQ/BUG entry 来自注册表，直接 Change entry 的状态是 change | 对象形态可能影响实现检查，主对象已由用户确认为 BUG-0029 |
| E4 | code_path | src/backend/app/chat/app_server.py:64 | 实现与治理 scope 映射到不同 profile | 映射代码本身不证明运行时下发结果 |
| E5 | reproduction | bug.md 上轮合成验证记录 | 基准通过，来源别名、applied、直接 Change entry 不通过 | 仅函数分支验证 |
| E6 | code_path | src/backend/app/chat/execution.py:125–151 | 读取策略 write_scope，支持时调用 set_write_scope，再连接并启动 turn；执行中权限变化触发 write_permission_revoked | 补齐策略到执行器的代码链路，未证明失败 turn 的服务器类型与实际 profile |
| E7 | reproduction | 本轮内存合成验证，policy.py 原函数 AST | REQ 与 BUG 各验证基准、source_* 别名、applied、Sprint 缺少 Issue 成员，8 个断言通过 | 两种 Issue 的基准均为 True，其余均为 False；所有输入的治理资格为 True。未运行完整 write_policy 或产品端到端流程 |
| E17 | runtime_log | 原执行器 rollout 的目标 turn `turn_context` | 实际 profile 为 `moonbox-governance`，`/work` 只读且治理目录可写 | 直接证明原轮次权限边界；服务端 reason_code 未留存，详见下文补证 |
| E21 | reproduction | 当前 MoonBox 原 BUG-0029 会话，后端只读调用完整 `write_policy` | 返回 `governance_write / governance_object_writable`；Firefox 同会话显示“治理可写” | 直接确认当前服务端权限决策；不是原轮次未留存的决策日志 |
| E22 | reproduction | 同一后端进程、原会话、当前治理事实的内存对照 | 不修改磁盘与数据库，仅在读取 Change trace 时补 `bug=bug_id`、`sprint=iteration`，完整 `write_policy` 变为 `implementation_write / implementation_change_in_sprint` | 证明两个字段共同造成权限分支切换；不是修复后的产品验收 |

E7 可复核方式：从当前 policy.py 用标准库 AST 抽取 `_implementation_ready` 和 `_governance_writable` 原函数，注入内存 `_read_file`、re、yaml；不导入或改写业务模块，不连接数据库。合成对象使用 REQ-9999-synthetic / BUG-9999-synthetic，iteration 为 sprint-999、related_change 为 fix-synthetic，entry.status 为 in_sprint。基准 Change trace 使用 proposed、同一 sprint、requirement 或 bug 来源字段；Sprint 同时包含 Change 和 Issue。每次只改变表中一个条件。

| 合成变体 | REQ 实现检查 | BUG 实现检查 | 解释边界 |
|---|---|---|---|
| 基准 | True | True | 排除“实现检查对全部输入恒为 False” |
| 仅来源字段改成 source_requirement / source_bug | False | False | 证明当前函数不兼容这组别名，未证明实际故障使用别名 |
| 仅 Change 状态改成 applied | False | False | 可能属于命令阶段不匹配，不直接等于应放开权限 |
| 仅从 Sprint 成员列表移除 Issue | False | False | 门禁拒绝本身合理，需要定位是否存在事实漂移 |

## 候选根因与排除条件

| 假设 | 当前依据 | 确认或排除所需证据 |
|---|---|---|
| H1 实现事实不满足，回退 governance_object_writable | E2、E3、E7 | 失败当时的主对象、注册表、Change、Sprint 摘要与 reason_code |
| H2 准备候选分支提前返回 governance_candidate_running | E2 | 同一 turn 是否绑定 running 的治理候选、候选 action 及绑定关系摘要 |
| H3 策略 scope 正确，但执行器 profile 或部署版本不一致 | E4、E6 | 同一 turn 的策略结果、实际 profile、服务器类型和运行版本 |
| H4 执行中事实变化引发权限撤销 | E6 | 同一 turn 的时间线及是否出现 write_permission_revoked；不能把撤销等同于初始治理授权 |

## 已排除假设

E21–E22 的完整策略对照排除“实现检查对目标对象永远失败”和“当前执行器映射单独造成降级”。原 turn 的候选查询无绑定行，E17 确认当时实际 profile，E15 确认当时 Change 已使用 `bug_id`、`iteration`；历史 `reason_code` 未持久化，不能作为直接观测。

## 已确认根因

已确认当前权限策略的字段契约与 BUG-0029 Change trace 不兼容：`_implementation_ready` 要求 `bug` 和 `sprint`，实际 Change 使用 `bug_id` 和 `iteration`；即使 BUG 已纳入 Sprint，检查仍返回 False，随后落入治理可写分支，使 `/work/src` 只读。原轮次实际 profile、当时 Change 字段和产品阻塞表现与该机制一致；对原会话的完整策略内存对照只补齐这两个字段即恢复实现写权限。历史 `reason_code` 未单独留存，因此只把它作为当前复现结果，不伪称原轮次日志原文。

## 自主补证与阻碍

本轮复核目标 bug/trace、策略、执行器下发及执行中检查代码，执行 8 个合成断言，并检索 logs 中与 BUG-0033、opsx-apply、governance-scope 相关的文件名，未命中。当前工具无可用浏览器能力，材料未提供产品访问入口、失败主对象及 turn 定位信息，无法在本轮自主还原运行态。当前 `/bug-complete` 会话的治理写权限符合命令用途，不能作为此前 `/opsx-apply` 错误授权的证据。

## 补证清单与返回方式

| 证据 | 为什么需要 | 操作步骤 | 返回字段 |
|---|---|---|---|
| 失败对象与环境 | 确定同一事件，避免分析错对象 | 打开原失败会话及产品版本信息，只读定位 | 脱敏 turn 标识、发生时间、版本、部署模式、主对象 ID、Change、Sprint |
| 当时权限决策与实际执行权限 | 区分 H1/H2/H3 | 查看原 turn 的受控执行记录；会话详情仅用于辅助对照 | write_scope、reason_code 或 write_reason_code、实际 profile、记录时间、服务器类型 |
| 当时治理事实及候选状态 | 找出未满足的判断条件 | 读取该事件对应的版本快照，不改注册表或 Sprint | Issue status/iteration/related_change；Change status/sprint/来源字段；Sprint 成员包含关系；候选是否存在、action/state 摘要 |
| 源码失败与执行时间线 | 验证权限决策和写入失败的因果关系 | 查看既有失败工具结果，优先不重跑生产命令 | 仓库相对路径、错误码或短摘要、发生时间、是否出现 write_permission_revoked |

统一用脱敏字段表返回，未取得填“未取得”，注明“失败当时记录”或“当前查询”。不提供原始会话、凭证、Cookie、Token、真实环境文件、客户数据或本机绝对路径。既有证据不足时，后续在已授权测试环境按 bug.md 复现步骤观察；本轮不执行生产写入。

## 修复方向

待证据确认后再选择修复面：若为字段或对象形态兼容，核实合法事实契约后设计兼容；若为治理事实缺失，明确诊断与流程恢复；若为运行态 profile 不一致，定位下发及部署边界。所有方向均保留成员授权、Sprint、Change 和只读边界，不以无条件授予源码写权限作为修复。

## 验证闭环

已完成静态代码核查与 8 个函数级合成断言。真实失败重现、根因对应、修复后同场景成功及负向权限回归均待执行，见 acceptance.md。草稿保持 enriching，lifecycle.completed 保持既有值；本轮不调用 bug.complete 完成态同步，不进入 pending_review。

## 进一步补证：真实治理输入对照

| id | type | source | 摘要 | 支持的判断与限制 |
|---|---|---|---|---|
| E8 | data_sample | issues/bugs/_registry.yaml 中 BUG-0029 条目；iterations/change/sprint-008/sprint.yaml | BUG-0029 为 in_sprint，关联目标 Change 与 sprint-008；Sprint 同时包含 BUG 和 Change | 当前仓库双向纳入条件成立，非失败时的服务端快照 |
| E9 | code_path | openspec/changes/fix-chat-workbench-nonempty-page-scroll/trace.md Frontmatter 与“实施前阻塞检查点” | trace 为 proposed，使用 bug_id/related_bug 和 iteration；已有 apply 因源码只读阻塞的文字记录 | 找到实际业务候选，记录指向样式文件及测试无法写入；不是原始 turn 日志 |
| E10 | reproduction | policy.py 原函数 + E8/E9 实际文件的内存对照 | 原输入 False；仅补 sprint 为 False；仅补 bug 为 False；同时补 sprint 和 bug 为 True，共 4 个断言通过 | 精确定位当前文件输入的两个阻断字段；未改实际文件或完成运行态全链路验证 |
| E11 | code_path | src/backend/app/chat/container_server.py:13–34 | governance profile 仅开放治理目录，write profile 开放项目源码；与 app_server.py 的 scope 映射吻合 | 能解释治理权限下源码只读的机制，不等同于确认失败 turn 使用了该 profile |

E10 读取当前注册表中 BUG-0029-chat-workbench-nonempty-page-scroll 条目、目标 Change trace 和 sprint-008 的 sprint.yaml。抽取未经修改的 `_implementation_ready` 与 `_governance_writable`，只用内存文件读取器供给上述文本。对照分别追加 `sprint = iteration`、`bug = bug_id`；不改变状态、Sprint 成员或其他字段。四次结果按序为 False/False/False/True；前三次治理回退资格为 True，最后一次不需要回退。所有实际治理文件保持只读。

这比纯合成样例更贴近业务：当前实现函数要求 `trace.sprint` 与 `trace.bug`，实际 Change 已包含同义信息但使用 `iteration` 与 `bug_id`。两处不匹配同时阻断实现资格。当前可复核结论是字段兼容缺口及其函数级因果关系；用户已确认 BUG-0033 原报告对象就是 BUG-0029；当时服务端治理根目录、版本和分支仍待证。

另检查了现有完整策略测试 `src/backend/tests/test_chat.py::test_write_policy_requires_current_role_and_sprint_change`，其辅助函数只生成规范化 requirement/sprint 字段，不能覆盖上述真实 trace 变体。本环境 Python 缺少 pytest，依赖探测返回 ModuleNotFoundError，未执行现有集成测试；没有安装依赖或读写运行数据库。当前仍无可用浏览器工具，未取得原失败事件定位信息。

## 收敛后的补证优先级

1. 已完成：用户确认原失败对象为 BUG-0029-chat-workbench-nonempty-page-scroll，无需再次询问对象身份。
2. 对同一失败 turn 获取实际 `write_scope`、`write_reason_code`/reason_code、profile、时间和部署版本，以及服务端所读治理文件的版本摘要；区分原始记录与当前查询。
3. 若原因为 governance_object_writable 且当时文件与 E8/E9 一致，再核对源码拒绝结果，即可收敛 H1；若为 governance_candidate_running、其他 profile 或撤销错误，则转查 H2–H4，不能强行套用字段问题。

不为规避而修改 BUG-0029、Sprint、Change 或源码。根因保持 probable、主状态 enriching，lifecycle.completed 原样保留。后续完成态校验与同步仍以 confirmed 和有效证据链为前提。

## 原失败对象确认补证

| id | type | source | 摘要 | 支持的判断与限制 |
|---|---|---|---|---|
| E12 | data_sample | 本轮用户明确确认 | BUG-0033 原失败对象为 BUG-0029 | 建立用户报告与 E8–E11 目标对象的关联；不提供原始 turn、reason_code、profile 或失败当时文件版本 |

对象身份缺口已消除。当前证据支持字段兼容缺口为 probable 根因；仍需原失败 turn 的实际决策与文件版本，排除准备候选提前返回及部署差异。不重复要求用户确认 BUG ID，不推进 pending_review。

## 自动补证：原失败 turn 持久记录

本轮以 SQLite `mode=ro` 与 `query_only=ON` 只读查询允许访问的项目运行数据。仅输出目标 turn 的脱敏派生事实，不复制数据库、原始会话、工具结果正文或凭证。未访问禁止读取的系统运行目录。

| id | type | source | 取得的事实 | 证据边界 |
|---|---|---|---|---|
| E13 | data_sample | 后端运行数据库 chat_turns、chat_context_snapshots，目标主对象加 /opsx-apply 前缀过滤 | 唯一匹配 turn 为 74c3e3b9-c332-4821-8bb9-6e4aeb970cfe，开始时间 2026-10-06 21:31:22（Asia/Shanghai），状态 completed，workspace_id 为 source | completed 只表示会话结束，不代表 Change 实施完成 |
| E14 | data_sample | 同 turn 的 chat_context_snapshots | BUG-0029 主文档快照版本 7ec1a531666035a165ff104bb9f98cab6b46e23393befabfef8a7b452c969b42，status 为 in_sprint，updated_at 为 2026-10-06 01:53:52 | 该快照是主文档，不能替代注册表、Change trace 或 Sprint 快照；其中没有 related_change/iteration 不说明注册表缺失这些值 |
| E15 | runtime_log | 同 turn 的 execution.tool，sequence=61，exit_code=0 | 当时实际读出的 Change trace 为 proposed；change_id 指向 fix-chat-workbench-nonempty-page-scroll，bug_id/related_bug 指向 BUG-0029，iteration 为 sprint-008；created_at/updated_at 均为 2026-10-06 21:29:10，没有 bug/sprint 字段 | 证明字段差异在失败当时已存在；尚未证明策略决策使用的治理根目录与该工具读取位置一致 |
| E16 | data_sample | 同 turn 的事件、effective_config 及治理候选查询；执行器 state/history 索引 | 2 条 execution.state、8 条 execution.tool；事件中未命中 write_scope、moonbox-governance 或 governance_object_writable；effective_config 无权限字段；没有直接或 prepared_turn_id 关联的候选行 | 缺记录不等于没有发生；不能把缺失候选行作为历史候选不存在的证明 |

E15 中提取的 Change Frontmatter 内容（不含边界行，保留原换行）SHA-256 为 `9d18549b14d5ca0100f43ffd1529a1147ef2a99fbbef31b2080c713e646fce7f`。这是事件中 Frontmatter 片段指纹，不是完整文件 hash，也不是服务端权限判定快照版本。当前 Change 后续更新时间不同，不能再将当前全文冒充失败时版本。

## 三项请求的取证结论

- **当时治理文件版本：部分取得。** 已获得原 turn 实际读取的 Change 字段、更新时间与片段指纹，以及独立的 Issue 主文档快照版本；原注册表与 Sprint 的决策输入版本未取得。
- **原 turn 权限决策：未取得显式记录。** 持久事件未发现 scope/reason_code；当前代码结合历史字段可解释治理回退，但这是重建判断，不标作原决策日志。
- **实际 profile：未取得历史 profile 名称。** 对现存 4 份执行器 state 索引及对应 history 索引按目标 thread 精确查询均未命中，目标 rollout 文件名检索也未命中。不使用其他会话或当前 profile 代替历史值，不推断记录已被删除。

已取得的执行器 turn 标识为 01a11169-b7de-7b53-bc57-e0be1c7aa554，thread 标识为 01a10ca2-764b-73e1-ae30-d794892033c7。后续取证可用它们在保留原执行器记录的环境定点检索，无需再次确认 BUG 身份。当前工具仍没有浏览器能力；本轮已经执行数据库及历史索引自主检索，不再将查找对象和 Change 历史字段转交用户。

根因仍为 probable，主状态 enriching；已将“当前文件不兼容”推进为“原失败 turn 读到的文件已不兼容”，但不伪造权限决策/profile。尚缺原 turn 的权限启动记录以及服务端当时使用的注册表、Sprint 版本。未执行完成态同步或修改其他对象。

## 原执行器权限启动记录补证

2026-10-07 在正在运行的 Chat worker 中，以 SQLite 只读模式核对原执行器 thread 和 turn，并只读解析该 thread 保留的 rollout。以下结果更新上节“实际 profile 未取得”的历史状态描述；原始会话、凭证和完整 rollout 未复制到仓库。

| id | type | source | 取得的事实 | 证据边界 |
|---|---|---|---|---|
| E17 | runtime_log | 原 thread rollout 第 465 条 `turn_context`，与 E13 的执行器 turn 精确匹配 | `active_permission_profile.id` 为 `moonbox-governance`；`/work` 为 read，治理目录为 write；可写根不含 `/work/src` | 直接确认当时实际 profile 与源码只读；没有单独记录服务端 `write_scope` 或 `reason_code` |
| E18 | data_sample | 同一执行器 `thread_history_1.sqlite` 与 rollout | 目标 thread 保留 11 个 turn，目标 turn 唯一命中；第 461–465 条覆盖线程设置、目标 turn 启动和权限上下文 | completed 仅表示执行器轮次结束，不表示 OpenSpec apply 完成 |
| E19 | data_sample | 原 turn 工具事件、当前目标注册表与 sprint-008 事实源 | 原 turn 已读取目标 Change 的 `bug_id`、`iteration`，缺少策略要求的 `bug`、`sprint`；当前注册表为 in_sprint 且关联同一 Change，Sprint 同时包含 BUG 与 Change；Sprint 文件修改时间早于失败轮次 | 原 turn 未直接留存注册表版本；文件时间只能辅助判断，不能替代服务端当时的决策日志 |
| E20 | reproduction | Firefox 中原 BUG-0029 Chat 会话的 `/opsx-apply` 轮次及轨迹页 | 页面显示该轮次因 `/work/src` 只读阻塞，任务保持 0/7；轨迹页未展示权限决策字段 | 页面表现不能证明当时的 reason_code；当前 UI 权限标签也不能冒充历史决策 |

由 E17 与 `app_server.py` 的映射，可将当时服务端 `write_scope` **推断**为 `governance_write`，但该值未独立留存。由 E15/E19 和 `policy.py` 可重建 `_implementation_ready` 因 `bug`、`sprint` 均缺失而返回 False，随后 `governance_object_writable` 是当前策略下的合理 `reason_code`；原轮次没有显式 `reason_code`，不能把重建值写成直接观测。候选提前返回与当时注册表版本的剩余不确定性使原事件根因继续保持 probable。

后续修复需在执行器启动边界记录脱敏的 `turn_id`、`write_scope`、`reason_code`、实际 profile、服务端治理输入版本摘要及时间，并能按同一 turn 关联。留痕不得包含原始 Prompt、凭证、客户数据、本机绝对路径或完整治理文件。新增留痕后按 BUG-0029 同场景复现，对照服务端决策与执行器 profile，再复核 `reason_code` 是否为 `governance_object_writable`；若不一致，按实际记录重新分析。

## 浏览器与完整策略复现闭环

Firefox 中，原 BUG-0029 会话显示 `/opsx-apply` 因源码只读停止，任务为 0/7；同一会话当前显示治理可写。后端只读查询确认原失败 turn 没有绑定治理候选。对该会话调用未经修改的完整 `write_policy` 得到 `governance_write / governance_object_writable`；只在独立进程的内存读取结果中给目标 Change 增加 `bug`、`sprint`，再次调用得到 `implementation_write / implementation_change_in_sprint`。未发送新的 apply 命令，未修改源码、数据库或治理事实。该对照与原轮次 profile 和 Change 字段相互印证，根因由 probable 提升为 confirmed；修复及 AC-011 留痕仍待 OpenSpec 后实施。

## 本次实现与验证进度

已实现 Change 来源/Sprint 字段别名归一化、冲突/类型/来源匹配拒绝、执行器 profile 一致性检查和同 turn 脱敏权限事件。新增 test_permission_governance_contract.py 的 8 组 unittest 通过，包含完整 write_policy + 隔离 SQLite、REQ/BUG 别名矩阵、治理候选、只读成员、阶段门禁、profile 下发和事件持久化/去重/脱敏/降级。没有改变归档权限判定。

这不是修复后产品验收通过：真实 BUG-0029 场景 apply、MySQL 事件回归、既有 pytest 集成与执行中撤权全链路仍待运行。pytest/httpx 缺失，虚拟环境解释器不可用，临时安装依赖因网络 DNS 失败；当前无可用浏览器工具和可调用 Docker/MySQL 测试环境。AC-002 至 AC-009、AC-011 不因此自动通过；AC-011 仅完成隔离事件与适配器单元验证。历史 reason_code 缺失事实保持原样。

继续保持在研，未执行 opsx.apply 完成态同步；不得据源码已改或请求已确认宣称真实权限验收完成。后续先在已授权测试环境完成真实写入/拒绝和同 turn 决策事件核验，再处理归档。
