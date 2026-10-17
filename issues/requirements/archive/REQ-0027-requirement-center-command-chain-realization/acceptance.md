---
requirement_id: REQ-0027-requirement-center-command-chain-realization
title: 需求中心卡片全命令产品链路真实化验收标准
created_at: 2026-09-30 12:55:45
updated_at: 2026-10-17 16:45:28
acceptance_status: passed
---

# 需求中心卡片全命令产品链路真实化验收标准

2026-10-17 最终复验：功能 20/20、横切 3/3、原型 5/5，合计 28/28 通过。完整运行 `20261017155920820313-edb48ad0` 为 `passed / complete`，归档就绪检查为 `ready`。新增横切持久性证据区分不同隔离对象，不宣称单对象经历全部故障；浮层 12 格视觉矩阵已目视签认，当前隔离产品的内部点击、取消和焦点返回已复查。证据入口见 Change `evidence/acceptance/20261017155920820313-edb48ad0/summary.md`。

## 验收口径

本文件为逐项验收清单，功能 AC 已签认 20/20；AC-011 的七动作四窗口产品证据与完成门禁已逐格复验。原型 AC-PROTOTYPE-003 的当前构建视觉矩阵已签认，另计于原型验收。逐项脱敏入口见 Change `evidence/acceptance/` 下的完整运行与 `samples/`。文档完善或单项命令通过不代表产品实现整项通过。每条证据记录测试环境、对象、前置状态、操作标识、安全摘要、文件差异及结果；前端交互、后端控制器、隔离文件集成、真实界面端到端分层存证，Mock/合成测试不能替代真实链路。

2026-10-17 AC-019 签认：独立隔离产品 `REQ-9316-capture` 的正式候选生成轮次 `f8afc333-16a7-4ecd-a821-df6d14469371` 为 `applied / verified`，Workflow Sync 成功后锁内重读事实源，卡片与 draft 一致；`REQ-9317-capture` 准备后事实源改变返回 409/2606，未应用且卡片保持 captured。错误 manifest/revision 的产品 API 直接请求均拒绝且无新应用；binding、同步失败及安全恢复遮蔽由 158 项后端聚焦回归覆盖。证据见 `evidence/acceptance/samples/AC-019.md`。单项诊断 `20261017000558632518-b0dabea7` 为 AC-019 passed；完整运行 `20261017000630013086-b8428962` 为 23 passed、5 blocked，AC-019 passed。功能计数更新为 18/20，验收状态仍 pending；主产品 39002 页面尚未登录，未把文件计数写成新的页面观察。

2026-10-13 续验：当前构建的原型 AC-PROTOTYPE-003 视觉矩阵已整项签认，不计入功能卡片的 20 项分母。中断后重建独立隔离项目，API/worker/控制器就绪；侧边浏览器拒绝新回环端口，未取得新的 UI 产品轮次。完整运行 `20261013223705755855-13c1ed57` 为 `blocked / complete`，13 项命令检查通过、15 项缺同源轮次而受阻；这 13 项检查通过不构成新增功能 AC 签认。功能清单仍为 2/20。

2026-10-13 获浏览器访问授权后重试同一隔离入口，客户端仍拒绝打开。通过真实本地 Chat REST 接口补得 AC-001 只读分析轮次和 AC-002 主对象绑定前后的生成轮次，详见同名 `samples/`；两项均因子场景、页面和事实源门禁证据不全而保持未勾选。完整运行 `20261013225447679427-4bbb9780` 为 `failed / complete`：12 项检查通过、15 项受阻、AC-017 前端命令一次失败；该命令独立重跑 125/125 通过，聚焦诊断 `20261013230958439666-b808ae87` 中 AC-017 为通过。仍无新增功能 AC 整项签认，计数 2/20。

2026-10-13 续验发现 AC-019 的 source 模式失败子场景：隔离对象的 `req-complete` 候选被控制器拒绝，执行器写入的 trace 与注册表仍推进到 `pending_review`，浏览器卡片进入待评审。脱敏证据见 Change `evidence/acceptance/samples/AC-019.md`。此项需验收返修，不能因助手完成话术或当前文件状态勾选。

2026-10-13 AF-036 复验：新独立对象的 `req-complete` 候选被拒绝后，事实源与卡片已恢复到 `draft` / 规划中；Chat 返修后默认折叠错误成功话术并显示拒绝结论。AC-019 该负向子场景通过，其他冲突/恢复组合及 AC-003 成功路径仍待取得，所以整体仍不勾选。证据见同一 Change 的 `evidence/acceptance/samples/AC-019.md`。

2026-10-14 AC-001 整项复验：独立隔离产品 captured、exploring、缺 `trace.md` 与聊天要求生成/归档五类轮次均保持只读，完整 ID、项目和引用版本已核对；前后治理文件 SHA-256 零差异，状态与生命周期不变。脱敏证据见 Change `evidence/acceptance/samples/AC-001.md`。本项签认后功能计数为 3/20；其余 AC 不因本项通过而自动勾选。

2026-10-14 AC-002 整项复验：独立隔离项目 captured 与 exploring 各取得 completed / candidate applied 的真实产品轮次；两轮只新增 `requirement.md` 业务产物并更新目标 trace、需求 registry、CHANGELOG，capture 哈希不变，状态 draft、generated 时间与索引同步，页面抽屉重读成功。脱敏证据见 Change `evidence/acceptance/samples/AC-002.md`。本项签认后功能计数为 4/20；其余 AC 不自动勾选。

2026-10-17 AC-016 签认：独立隔离产品 `REQ-9315-capture` 经 captured、draft、pending_review、approved、in_sprint、真实 opsx.start、applied、归档到 done；七阶段分别发起产品轮次，每步重读下一动作，同轮成功工具命令均未执行下一阶段。当前用户确认隔离样本人工验收并授权归档后，轮次 `f862bf86-ed51-4155-a95b-f8ea23b8b5b8` 完成，规范归档目录、合并规格、Issue archive、注册表 done 与产品卡片只读一致。`sprint-propose` 与 `opsx-apply` 的 Chat 轮次分别为额度停止、写权限收窄停止，文件事实和反馈状态在证据中分别记录，未把停止写成轮次成功。单项诊断 `20261017073141761125-82a5f55a` 中 AC-016 passed。脱敏证据见 `evidence/acceptance/samples/AC-016.md`。功能计数 19/20，验收状态仍 pending。

2026-10-17 AC-011 复核更正：已补齐七动作故障窗口矩阵及 `opsx-apply` 首文件中断后的同对象安全续做，命令探针为 passed；但 Change `tasks.md` 的 7.8.2d 仍未完成。旧 `req-opsx` 轮次持续 unknown，原 `sprint-propose` 无效 YAML 场景缺完成门禁复验。此前据命令探针和矩阵直接签认 AC-011 过早，现撤回勾选并保持 19/20；证据与缺口见 `evidence/acceptance/samples/AC-011.md`。

2026-10-17 AC-011 最终复验：独立隔离产品新 `req-opsx` 写前轮次 `9b249258-944e-4708-a264-543b64c4cb57` 在事实源基线未变、零步骤时中断，重启后 stopped / no_governance_write；部分落盘轮次 `f623dfdc-1742-49b8-915a-70eea82f5d6f` 重启后 stopped / partial_write，0 个同步步骤且文件保留。新 `sprint-propose` 轮次 `a2593400-4dce-4f8c-8f36-053fa3f880f2` 在正式同步退出成功但 Sprint YAML 无效时为 failed / sprint_source_invalid，未报 Chat 完成。28 格矩阵、30 个轮次前缀均有脱敏入口；旧不可读取外部轮次仍安全保持 unknown，不作为通过证据。AC-011 整项签认，功能计数 20/20；证据见 Change `evidence/acceptance/samples/AC-011.md`、`AC-011-product-recovery-20261017.json`、`AC-011-matrix-audit-20261017.json`。完整验收 `20261017083834351632-dd4c4ac9` 中 AC-011 passed、整体 22 passed / 6 blocked；横切与原型门禁仍待复验，验收状态 pending。

## 功能验收

2026-10-14 完整验收 `20261014095158402991-d9b82f81` 为 17 passed、11 blocked、0 failed，范围 complete，AC-004 passed，整体仍未归档就绪；隔离产品卡片显示 6/20，主产品 `39002` 登录页阻止页面独立核对。

2026-10-14 AC-004 四路径独立产品复验完成：通过、拒绝、延后各有已完成轮次、applied 候选及 verified 应用，review.md/主文档/trace/注册表/索引与目录阶段一致；取消未发送、无轮次，10 个文件哈希不变。拒绝首轮范围校验失败已回滚并修正后复验。聚焦验收 `20261014095143692985-044c66bb` 将 AC-004 判为 passed；详见 Change `evidence/acceptance/samples/AC-004.md`。

2026-10-13 新增隔离正向子场景：AC-004 取得 `req-review` 批准并 verified 的产品轮次；AC-005 取得零 active Sprint 连续创建、默认30人天与双向纳入轮次，并验证多 active 未选和显式超量无写入；AC-006 取得就绪阻断及中断后幂等恢复证据，最终 Change 文档、schema v1 与关联一致。三项仍缺其余分支，均未签认整项通过。证据见 Change `evidence/acceptance/samples/AC-004.md`、`AC-005.md`、`AC-006.md`。

2026-10-13 AC-007 隔离产品轮次已记录 `opsx.start`，0/11 时卡片进入研发中；续接后 1/11，未产生 `opsx.apply`。两入口 × 两视口 × 三状态的 12 组真实页面组件壳骨架截图与样式已保留，HTTP 为合成只读响应；已登录产品视觉、首轮确认及完成门禁仍缺，整项待验收。AC-009～012、014、015、017、018 及原型 001、005 已补命令或文档回归部分样本。最新完整验收诊断 `20261013150019239346-af0be59e` 为 28 项 blocked，不代表 28 项功能失败；预检仍缺 65 个证据文件入口，见 Change 同名运行目录及 `samples/`。

2026-10-13 续验：评审 plan→review 迁移窗口的 Chat 读取中断已定位并修复，独立隔离轮次证明读取可持续、执行器可完成；该轮候选因评审范围拒绝，未形成成功评审应用。第五独立产品轮次确认拒绝后原文件逐字节恢复，卡片仍待评审。完整诊断 `20261013132451887112-d9d39d46` 为 28 项 blocked；逐项证据见 Change `evidence/acceptance/samples/AC-004.md` 与 `AC-019.md`，验收状态仍 pending。

2026-10-13 侧边浏览器恢复后，`39028` 独立项目补采 AC-002 的规划中卡片与文档重读 1440/390 截图、AC-003 缺文件拒绝轮次 `061b73dc-5279-4a92-bfaa-ea208a02c0ce` 及拒绝后卡片、AC-009 查看者三视口与直接 API 403/2601、原型 003 的长文档卡片三视口。AC-003 候选为 `rejected / completion_document_format`，事实源保持 `draft`。各项仅补足部分子场景，未达到功能 AC 整项签认条件；功能计数保持 2/20。主产品 `39002` 健康检查通过，但新标签需登录，尚无该环境的最新卡片视觉复核。

2026-10-13 AC-009 查看者八动作直接 API 基线续验：隔离 `39028` 项目合成对象 `REQ-9098` 的只读 `req-explore` 返回 200/0；七个写动作分别返回 403/2601。此结果只覆盖查看者与完整 ID 组合；跨项目、短 ID、篡改字段及阶段门禁矩阵未齐，AC-009 不勾选，功能计数仍为 2/20。证据见 Change `evidence/acceptance/samples/AC-009.md`。

2026-10-13 AC-009 续验明确失败：`39028` 独立项目中，未知动作 `ac009-unknown-action` 返回 200/0 且提供对象会话，违反后端动作白名单；未发送 Chat 轮次或应用候选。错误空间返回 403/2601，错误仓库返回 503/2602；规划中对象的五个不合阶段动作返回 409/2604。仓库代码已返修白名单并通过 46 项聚焦回归，旧隔离服务尚未重建复验；AC-009 保持未勾选，功能计数仍为 2/20。脱敏明细见 Change `evidence/acceptance/samples/AC-009.md`。

2026-10-13 AF-044 新构建复验：同一未知动作改为 422/2604 且无会话，合法只读探索仍为 200/0；隔离库会话、候选、轮次聚合数量均未变化。白名单失败点已修复，但 AC-009 其余权限组合未齐，整项维持未勾选，功能计数 2/20。

2026-10-13 AC-013 补得一个服务重启后的真实产品重读样本：独立 `39028` 项目中 `REQ-9098` 卡片仍为规划中，文件 trace 与注册表均为 `draft`，主文档与索引可读；七写动作完整重启矩阵未齐，不勾选。截图及摘要见 Change `evidence/acceptance/samples/AC-013.md`。

2026-10-16 AC-013 在独立 `39028` 项目补得七动作当前态投影矩阵并重启隔离 API 后复查：七个真实轮次可按 ID 查询，六个 REQ 的卡片、主文档、registry、CHANGELOG、trace 及适用 Sprint/Change 与当前文件事实相符。运行中关闭 Chat 窗口、重新进入 UI 按操作身份查询，以及各动作完成当时的逐次刷新快照仍缺真实观察；整项保持未勾选。脱敏矩阵与限制见 Change `evidence/acceptance/samples/AC-013.md`。

同日补得关闭面板与重进组件回归，4/4 通过；它是合成 UI 证据。真实浏览器仍停在隔离项目登录页，AC-013 不因该回归签认。

2026-10-16 用户登录隔离项目后，真实 Chrome Chat 标签在 `REQ-9300` 的 `req-generate` 轮次连接中关闭；产品轮次随后继续为 `running`，新标签重进同一会话可按完整 turn ID 找回“执行中”及轨迹。之后轮次报 `unknown / execution_access_or_workspace_error`，尽管 `requirement.md`、draft trace 与注册表已落盘，刷新后的需求卡片进入规划中。关窗持续性与按身份重进取得真实观察，但完成终态不一致；AC-013 仍不勾选，完整验收待整项通过后再跑。脱敏事实见 Change `evidence/acceptance/samples/AC-013-window-resume-live.json`。

2026-10-16 AC-013 续验：定位并修复缺失直接命令日志导致的恢复门禁误阻断；产品自带恢复函数按相同外部轮次的 `completed` 终态落账，未重放命令。隔离 API/Worker 重启后，Chrome Chat 与需求中心刷新仍可读同一完成轮次及卡片；七动作当前态矩阵中的轮次身份、主文档、registry、CHANGELOG、trace 和适用 Sprint/Change 均与文件事实一致。聚焦验收 `20261016180055645290-29ee8c7f` 对 AC-013 返回 `passed`；整项现签认。历史各动作完成瞬间的卡片状态仍以对应 AC 的阶段轮次为准，不由本项当前态矩阵倒推。

本次完整验收 `20261016180122592957-e4124d58` 为 `complete / blocked`：28 项中 22 passed、6 blocked，AC-013 passed；功能 AC 清单签认实数 14/20。主产品 `39002` 新标签仍停登录页，未取得登录后卡片视觉计数，不能宣称 UI 已核对。Workflow Sync `opsx.modify` errors=0，验收状态保持 pending。

2026-10-13 状态同步核对：`opsx.modify` 从最新自动验收 manifest 投影时，将此前人工整项签认的 AC-018、AC-020 暂时清空；AC-018 的边界文档与客户端形状已复核，AC-020 的 source 策略和产品轮次未受 AF-044 影响，两项依原签认证据恢复勾选。该同步投影与人工签认冲突需治理规则后续修复；不得据此推断新功能 AC 通过。当前清单保持 2/20，隔离副本卡片也显示 2/20，主产品仍待登录后现场核对。

2026-10-14 AC-003 整项复验：独立 `39028` 项目取得 `draft`、`enriching` 两条 `req-complete` 产品成功轮次，候选和应用均为 `applied / verified`，六件套、适用 Web 原型与中文标题复核通过，事实源到 `pending_review`；缺文件、空文件和无效标题三条隔离反例均被拒绝且保持 `draft`。先前执行器停滞和 trace 越界拒绝轮次保留为失败事实。逐场景脱敏摘要见 [AC-003 证据](../../../../openspec/archive/2026-10-17-add-requirement-center-command-chain-realization/evidence/acceptance/samples/AC-003.md)，聚焦验收 manifest `20261014090214365743-8592da23` 对该项返回 `passed`。仅新增 AC-003 整项签认；其他 AC 不受此结论影响。

2026-10-14 本轮继续完成 AC-005、AC-006、AC-007 的整项复验并勾选；AC-006 正式 Sprint 范围门禁返修见 Change AF-045。AC-008 缺验收证据归档拒绝、AC-009 八动作只读权限、AC-010 七动作会话准备同键重试仅为部分证据，三项仍不勾选。完整验收 `20261014133100975058-3a527692` 为 blocked；其命令探针 passed 不等于对应 partial 样本整项通过。当前功能清单签认 9/20，主产品登录后的卡片显示仍待现场核对。

2026-10-14 后续补齐 AC-009：双隔离项目完整 ID 交叉拒绝、八动作合法与非法阶段矩阵、只读成员七写拒绝、短 ID 归一和伪造路径/状态/角色/快照版本均通过；备用生成入口与 OpenSpec Change 阶段缺口由 AF-046、AF-047 修复。聚焦验收 `20261014135154047091-b359907e` 对 AC-009 返回 passed，现签认至 10/20。AC-008、AC-010 仍未整项通过。

2026-10-14 Workflow Sync 清单投影返修 AF-049：旧逻辑把仅命令探针通过的 partial 样本勾选，又清空已签认的整项，现改为以整项样本状态约束新增勾选并保留已有有效签认；修复后同步再次运行无改动，功能清单稳定 10/20。AC-008 另修复 `requirement_id` / `bug_id` 归档验收门禁 AF-048，正向归档仍待取证。AC-010 取得七类同请求轮次重放与全治理树哈希不变证据，但实际成功 apply/archive、不同请求重复点击和冲突写矩阵未齐，不签认。

- [x] AC-001 需求分析：captured/exploring 的可读 REQ 打开标识“只读分析”的 Chat，携带完整 ID、项目和引用版本；缺主动作材料仍可分析。比较前后治理文件哈希及生命周期，包括聊天中要求生成/归档的反例，均无治理写入。
- [x] AC-002 生成需求：准备非空 capture/trace，从 captured 和 exploring 分别执行；只生成 requirement.md 业务产物，req.generate 同步 draft、generated 时间及索引，文档可重读。
- [x] AC-003 完善需求：从 draft/enriching 分别执行；六件套、适用原型与中文标题校验通过，req.complete 后 pending_review；缺文件、空文件或无效标题不推进。
- [x] AC-004 发起评审：确认通过、拒绝、延后三条路径分别产生 review.md 结论并同步对应状态；拒绝/延后有理由；取消无写入，通过才按治理迁入 review 阶段。
- [x] AC-005 加入迭代：仅 approved 且评审通过时执行；0/1/多个 active 分别验证默认下一个连续编号/当前/显式选择；扫描 active 和 archive 最大编号；默认30人天且不覆盖有效容量；关闭 Sprint 被拒绝；四件套与 REQ 双向一致。
- [x] AC-006 生成 OpenSpec：仅 in_sprint 且正式范围含该 REQ；创建 proposal/design/tasks/增量 specs/trace，检查活动与归档身份唯一、中文校验、同 Sprint Change 关联及 execution.schema_version=1、两个执行时间均 null。
- [x] AC-007 开始开发：请求受理不等于启动；真实 opsx.start 后0/N也显示研发中，REQ 保持 in_sprint；任务全勾选但门禁未过不报告 applied；完成验证和文档后 opsx.apply 显示验收中，不自动归档。
- [x] AC-008 完成归档：缺人工验收证据拒绝；门禁通过才合并规格、归档 Change、同步并迁移 Issue；多 Change 仅部分归档时 REQ 不 done；全部完成后 done 且详情与迁移后索引可读，不要求整个 Sprint 先完成。
- [x] AC-009 身份与权限：八动作逐一检查完整 ID、授权项目、白名单和后端阶段门禁；短编号、任意客户端路径、跨项目 ID、篡改状态/角色/快照不能扩大权限；只读账号不能写，直接调用 API 也不能越级。
- [x] AC-010 幂等并发：七写动作分别重复点击、相同请求重试、断线重连，返回同一操作结果且无重复产物；同对象冲突写串行；过期版本/外部编辑返回冲突并保留已有文件。
- [x] AC-011 故障注入：七写动作逐一在写前、部分文件完成、同步前后注入故障；准确区分未执行/部分写入/同步失败/完成。重启后核对落盘步骤再恢复，不伪造回滚，不盲目重放已完成步骤。
- [x] AC-012 归档恢复：分别在规格合并、Change 迁移、同步、Issue 迁移后中断；重试不得重复合并、丢失目录或提前 done；未知外部修改时阻塞并保留安全证据。
- [x] AC-013 结果反馈：关闭窗口不取消任务；再次进入能按操作身份查询。七写动作完成后刷新页面及重启服务，卡片、最新文档、registry、CHANGELOG、trace、适用 Sprint/Change 均与文件事实一致。
- [x] AC-014 观测：八动作界面行为来自稳定字典，可信 request_id 由服务端生成；写任务关联 operation/workflow/run/节点；直接 API 不伪造界面行为；纯读取无额外写任务 Trace，Chat 模型观测沿用现有机制。
- [x] AC-015 脱敏降级：日志和行为/任务节点不保存 Prompt、文件正文、请求响应正文、密钥或本机路径；非法链路字段受控处理；采集失败不阻断业务，Workflow Sync 失败阻断完成；请求/终态任务90天、行为180天，未终态恢复证据不因观测清理丢失。
- [x] AC-016 完整主链：使用隔离项目，从 captured 经 draft、pending_review、approved、in_sprint、真实启动、applied、archive 到 done；每步断言下一动作重算，不自动推进下一命令。
- [x] AC-017 错误文案：缺材料、阶段不符、无权限、版本冲突、同步失败分别采用 PRD 指定文案；无内部路径/堆栈/他项目数据泄漏，认证失效走既有登录流程。
- [x] AC-018 边界同步：Change 明确实际 API/OpenAPI/客户端和产品说明更新；持久化结构变化补 DB 设计与迁移及兼容验证，未变化写明依据；不新增生产部署、对象存储维护或认证体系。当前代码隔离 MySQL 8.2.0 矩阵 86 passed，入口对照 3/3，证据见 Change `evidence/acceptance/samples/AC-018.md`。
- [x] AC-019 事实源唯一完成门禁：Chat 工作台执行工作区、assistant 输出和 candidate 只能作为候选或执行证据；写操作完成前必须校验 manifest、revision、binding revision，完成 Workflow Sync，重读治理事实源并刷新卡片投影。若候选或工作区基于的事实源已变化，必须进入 conflict/stale 或待恢复状态，不得展示成功或更新卡片阶段。
- [x] AC-020 本地部署真实仓库默认策略：本地常驻部署生成的仓库绑定默认包含 `workspace_mode: source`，执行器直接使用 `source_root` 当前工作树并直接写入治理事实源；`copy` 仅作为共享、多人或强隔离场景的显式模式保留，且不得再让本地默认会话副本产生事实源漂移或空间放大。

## 横切 AC（knowledge-base）

本需求为 Web 卡片/Chat/确认弹窗，不命中 admin-list、admin-form、admin-modal、media-upload 四个后台/上传标签；无该标签组横切 AC。仍承接以下同域知识库条目。

- [x] AC-XCUT-001 来源 docs/knowledge-base/incidents/20260912-capture-persistence.md：202仅受理，未知超时复用操作身份；刷新及重启后读取真实文件；外部变更阻断恢复而非强制覆盖。
- [x] AC-XCUT-002 来源 docs/knowledge-base/incidents/20260912-apply-start-stage.md：启动、任务进度、完成分离；0/N已启动显示研发中；保留旧终态，不编造历史启动时间。同对象产品轮次与旧状态兼容复验见 Change `evidence/acceptance/samples/AC-XCUT-002.md`。
- [x] AC-XCUT-003 来源 docs/knowledge-base/retrospectives/sprint-007-retrospective.md：归档入口复用后端治理门禁；标题、进度、文档入口可回溯事实源；合成与真实验收分别记载。隔离产品门禁、归档与重启后投影见 Change `evidence/acceptance/samples/AC-XCUT-003.md`。

## 原型驱动 UI AC

- [x] AC-PROTOTYPE-001 复核 prototype/web/context.md 拆解与八动作矩阵，Change design 承接 UI Contract 和 selector 映射；本项只签认原型契约，不代替运行态视觉验收。当前 DOM 映射与 130 项组件回归见 Change `evidence/acceptance/samples/AC-PROTOTYPE-001.md`。
- [x] AC-PROTOTYPE-002 先完成 UI Skeleton，并对1440px首轮证据确认后再进行细节实现。浅色 1440px 首轮结构已由用户确认；合成只读 HTTP 边界与截图/样式见 Change `evidence/acceptance/samples/AC-PROTOTYPE-002.md`。
- [x] AC-PROTOTYPE-003 在1440px、窄屏390px和矮视口验证深浅主题、弹窗/抽屉、焦点、取消、加载、错误、权限和溢出，记录截图与 computed style；返修使旧证据失效。当前构建八阶段×三视口及焦点/取消复核已通过，证据见 Change `evidence/acceptance/samples/AC-PROTOTYPE-003.md`。
- [x] AC-PROTOTYPE-004 归档前核对 PRD、用户故事、业务流程、验收、trace、prototype 与实现一致，明确 Mock/API 边界并回填全部证据。
- [x] AC-PROTOTYPE-005 支持外部关闭的浮层验证内部 stopPropagation 不误关闭、外部点击仍关闭；显式取消不写入，提交后关闭只隐藏反馈；Tab焦点约束、Esc关闭、关闭后焦点回到触发器。

2026-10-16 AC-014 整项复验：独立隔离产品新增 `REQ-9314` 从需求中心卡片发起的归档轮次。首轮被交付验证记录门禁拦下，补齐夹具后第二轮 completed，Issue/Change/规格落盘事实与已完成卡片一致；八动作稳定事件字典与服务端请求、七写动作运行和节点、直接 API 无界面事件、纯 GET 无新增写任务 Trace、Chat 模型用量沿用机制均核对。脱敏矩阵见 Change `evidence/acceptance/samples/AC-014-observability-matrix.json`。本项现签认，功能清单 15/20；其余项目保持原结论。

## AC-011 本轮结论（2026-10-14）

在隔离临时仓库复验三个候选动作的 `copy` 模式持久写入器：写前、首文件落盘后、同步前、同步完成而终态未提交及部分同步窗口均有故障注入；发现同步重复执行缺口并完成返修，相关后端回归 91 passed。聚焦自动验收 `20261014171038417344-b9cbedfb` 的 AC-011 命令探针 passed。真实隔离产品默认运行 `source` 模式，抽样三个候选应用没有持久写入器操作记录；另外四个命令动作缺相同的逐步注入与恢复证据。详见 Change `evidence/acceptance/samples/AC-011.md` 与 `AC-011-fault-matrix.json`。因此 **AC-011 不签认**，功能清单保持 12/20。

同日续验：补充默认工作区“外部终态已确认、候选尚未收尾”窗口的重启恢复扫描；定向测试确认重复扫描不重启外部轮次且只有一条应用记录，相关回归 201 passed、1 skipped。该修复只覆盖一个恢复窗口，四个直接命令及七动作完整故障矩阵仍缺证据，故本项继续不签认。

聚焦自动验收 `20261014172001884989-8c58148c` 对 AC-011 命令探针返回 passed，但整体为 diagnostic / blocked；AC-011 仍未签认，功能清单保持 12/20。

完整验收 `20261014172107427737-32f65690` 返回 complete / blocked；AC-011 命令探针通过不改变上述整项缺口。复核功能清单 12/20。

后续真实故障注入：隔离 `req-generate` 轮次 `2aa5fecb-7d9a-445f-9091-8fe88456e451` 首业务文件落盘后强制中断，重启发现文件残留；按该轮不可变基线安全恢复并修复 `collect` 的非完成终态分支。默认 source 三候选动作六窗口集成矩阵 18 passed，相关后端回归 206 passed、1 skipped。修复版产品重试在写前遇执行器失败；四个直接命令的完整矩阵仍缺。证据见 Change `evidence/acceptance/samples/AC-011.md`。AC-011 保持未签认，功能清单 12/20。

聚焦验收 `20261014174153329267-339ee146` 的 AC-011 命令探针为 passed、整体 diagnostic / blocked；其通过范围不包含剩余真实产品矩阵。清单与卡片计数不应据此增加。

四个直接命令已新增私有逐步 hash 记录及重启终态分类，4×6 隔离故障窗口和同步失败样本通过；分类不会自动重放命令，也不会把同步成功等同业务完成。真实产品故障轮次和动作语义复核仍缺，**AC-011 保持未签认，12/20 不变**。证据见 Change `evidence/acceptance/samples/AC-011.md`。

修复版真实轮次 `c9613032-01d1-40b1-9681-cbd000e2edd5` 到达执行器，但命令工具失败且业务文件未生成；聚焦验收 `20261014175621089182-47e401e8` 的命令探针 passed，整体 diagnostic / blocked。该轮不满足故障注入证据，AC-011 仍未签认。

隔离 `REQ-9204` 的修复版真实轮次 `dea734a8-4334-4a98-b34d-eda5966c39cd` 在首份 4,682 字节 `requirement.md` 落盘且仍 running 时中断 worker；重启后 stopped / rejected、应用记录 0，文件清除，全治理树 2,212 文件与该轮不可变基线逐字节一致。该单一窗口通过，其他动作与同步窗口未齐，**AC-011 仍未整项签认，12/20 不变**。证据见 Change `evidence/acceptance/samples/AC-011-source-restart-9204.json`。

聚焦验收 `20261014181634305607-0539f7f8` 的 AC-011 命令探针 passed，整体 diagnostic / blocked；未据此勾选 AC-011 或重跑完整验收。

后续独立隔离项目又取得七动作的真实中断与重启轮次：候选动作覆盖写前、部分文件和同步后；四直接命令覆盖首文件或同步中。归档在规格合并及目录迁移后中断时只安全阻断并保留部分现场，尚不能证明可安全续做；每个动作的全部故障窗口仍未齐。脱敏摘要见 Change `evidence/acceptance/samples/AC-011.md`。**AC-011 仍未整项通过，不勾选，功能清单保持 12/20。**

聚焦验收 `20261014190030940681-bb44d269` 的 AC-011 命令探针 passed，但整体为 diagnostic / blocked。随后 `opsx.modify` 同步更新 0 项，验收状态 pending；未据此签认 AC-011 或重跑完整验收。

归档部分现场已通过“跳过再次合并”的后置恢复分支验证：正式规格 hash 不变、归档目录唯一、证据门禁通过。另补三候选动作写前产品轮次；`sprint-propose` 同步后产生无效 YAML、`req-opsx` 写前中断后长期 unknown，均为未通过或待核验事实。详见 Change `evidence/acceptance/samples/AC-011.md`。**AC-011 不勾选，功能清单仍为 12/20；完整验收待整项通过后重跑。**

聚焦验收 `20261014192456103962-4edfc4f5` 的 AC-011 命令探针通过、整体 diagnostic / blocked；未据此勾选或运行完整验收。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-17 16:45:28
accepted_by: workflow-sync
source_change: add-requirement-center-command-chain-realization
source_sprint: sprint-008
evidence: [openspec/archive/2026-10-17-add-requirement-center-command-chain-realization/evidence/acceptance/20261017161704392258-c1a6bad7/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```
