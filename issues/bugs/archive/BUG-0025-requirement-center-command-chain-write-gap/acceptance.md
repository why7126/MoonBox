---
bug_id: BUG-0025-requirement-center-command-chain-write-gap
title: 需求中心看板治理命令真实写入链路缺口验收标准
acceptance_status: passed
created_at: 2026-09-29 15:56:27
updated_at: 2026-10-17 16:45:27
owner: user_f694abc671d548b48d9eb897f720ba4d
---

# 需求中心看板治理命令真实写入链路缺口验收标准

## 2026-10-14 AC-045 产品验收

专用隔离 REQ-0996 从产品 Chat 同会话执行 complete→review，后端为两个轮次分别生成候选并完成 `applied/verified` 应用；事实源从 draft/plan 经 pending_review/plan 到 approved/review。前两次 complete 模型轮次 completed 却被后端分别以范围与注册表门禁拒绝，未推进事实源。评审后 8 条旧目录删除记录经隔离服务重启仍在，看板“已评审”卡片的 `review.md` 可打开。结论冲突与工作区冲突保留由聚焦真实文件系统/SQLite 回归覆盖；[产品与文件证据](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-045-review.md)、[定向诊断](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/20261014082912338308-c734e5cd/summary.md)支持 AC-045 签认。最新完整诊断中 AC-045 passed，其余 51 项因共享输入指纹变化或预检材料缺口 blocked；AC-047、AC-051 保留各自独立通过的产品证据，不能把本轮 blocked 当作功能回退。其后 AC-044 在隔离产品完成两状态×双视口复验并由定向命令通过；随后 AC-043 完成当前产品子文档和继续完善入口复验；随后 AC-038 以当前隔离库 332 秒真实轮次及聚焦门禁回归通过；随后 AC-001 完成产品内命令能力矩阵逐项核对与定向回归；随后 AC-006～011 按当前命令能力、前后端回归及 API/Orval 一致性批量复验通过；当前勾选 37/52，整体验收仍 pending。

## 2026-10-14 AC-047 产品验收

隔离 SQLite 构造同一对象 Chat 的停止评审轮次与仍为 running 的旧候选；产品中从该会话发送新的 `/sprint-propose --bug BUG-0998-ac051-review-retest --sprint sprint-009`，轮次 `d5833d7f-d6e3-41fe-8411-d2bfaabcdb97` completed，当前轮次的 Sprint 选择校验命令退出码 0。旧候选仍绑定 stopped 轮次、原评审候选与 approved/review 成果保留，会话 active_turn 释放。产品容量门禁因 36.3/30 人天超过 120% 上限而阻断正式纳入；这是独立执行业务门禁后的结果，未宣称完成 Sprint 写入。见[AC-047 证据](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-047-review.md)与[定向诊断](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/20261014080813399456-f9c6c919/summary.md)。最新完整诊断中 AC-047 passed，其余 51 项因全局预检或材料/输入指纹问题 blocked，其中 AC-051 已有独立产品证据，不能把本次 blocked 误判为功能回退。当前勾选 26/52，整体验收仍 pending。

## 2026-10-14 AC-051 产品验收

专用隔离环境的首个 BUG 评审轮次暴露真实遗漏：候选和应用虽为 applied，CHANGELOG 目标行仍显示 `plan` 与旧 `/bug-review` 下一步。原 Change 内 AF-045 已补后端目标行阶段/下一步回填及完整校验。修复后 BUG-0998 与 REQ-0997 两个独立产品评审轮次均 completed，候选、应用为 applied/verified；各自 registry、trace、目录、CHANGELOG 四列及看板“已评审”状态一致。[AC-051 同轮与文件证据](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-051-review.md)及[最新完整诊断](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/20261014002725865559-09fdb17f/summary.md)支持本项签认。copy checkpoint、失败原轮次恢复、结论冲突、越权、缺文件和根因未确认使用聚焦文件系统/SQLite 回归证据；两个新产品轮次均为 source 模式，未冒称 copy 产品观察。最新完整诊断为 AC-051 通过、其余 51 项 `preflight-failed`；共享回归输入变化使旧通过指纹失效，且其余场景材料仍缺，不能将此当作 51 项功能失败。其余 AC 未自动签认，整体验收仍 pending。

## 2026-10-13 自动验收诊断

20:45 隔离测试目录及数据库意外重建后，已恢复独立产品环境并重新通过产品 UI 执行 BUG-0036 的 `bug-complete`。新 turn `d2f97c04-1278-4196-9033-fb30dd83a0d9` completed，候选和应用 applied/verified，五份草稿写入隔离源；因根因证据不足，trace 保持 enriching、完成时间为空。已保存 1440×900、390×900 的运行/完成截图和运行态 computed style，作为 AC-027/030 的 `bug-complete` 局部样本；全命令矩阵尚未齐全，不能勾选。详见[隔离产品阶段证据](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/isolated-product-20261013.md)。[本次完整诊断](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/20261013204500818933-ddb84103/summary.md)仍为 `blocked / diagnostic`，21 passed、31 blocked；其中旧产品轮次不在新 SQLite，21 项并非本次数据库的新产品通过。验收保持 pending，未运行 ready、状态同步或归档。

20:13 继续补 AC-007/008/009/010：发现真实模式未知治理命令会误建对象会话，已在当前 Web 源码加入 Codex 命令提示与提前返回，新增未知命令无请求及 REQ Generate 不回退测试；前端完整 125 项、后端候选与独立未知命令测试合计 46 项通过。四项定向命令检查 passed，输入指纹受影响的 AC-001/025/043/044 重新执行 passed。后端新断言单列文件，保留其他 AC 的有效历史指纹。Workflow Sync 后[最新完整 52 项诊断](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/20261013201313131288-d2d63b81/summary.md)复用或通过 21 项、阻断 31 项，仍为 `diagnostic`。当前隔离产品镜像尚未更新，不把组件回归写成新产品轮次或视觉签认。AC-006 原文所列 complete/review 等动作已有真实对象会话能力，旧标准需按现行能力逐项核对，暂不签认；状态保持 pending。

19:56 已同步返修工作流并再次执行完整 `/opsx-accept`：[最新 52 项诊断证据包](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/20261013195653645136-f3e30758/summary.md)复用/通过 17 项，35 项因证据或场景不齐阻塞，范围仍为 `diagnostic`。新增真实产品闭环：BUG-0039 原会话 `bug-complete` 的 turn、candidate、application 和五件套文件状态一致；AC-041 定向通过。长运行 11 分 27 秒的轮次支持 AC-038；规划中 draft/enriching 的 1440×900 与 390×900 视觉、computed style 和子文档打开支持 AC-043、044，三项亦定向通过。详见[隔离产品阶段证据](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/isolated-product-20261013.md)与 AC 专项 review。早前失败诊断保留为历史，人工勾选数量不按机器通过数自动改写；验收状态仍为 pending。

18:10 以当前工作区再次运行完整 `/opsx-accept`：[52 项机器证据包](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/20261013181018507195-487e4498/summary.md)为 `blocked / diagnostic`，12 项通过、40 项阻塞。另已建立[当前代码与独立数据库的隔离产品环境并记录真实产品证据](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/isolated-product-20261013.md)：BUG-0039 的 `bug-generate` 同轮完成并真实应用；规划阶段 draft/enriching 的桌面、移动截图和 computed style 已保存。隔离服务重启后 Chat worker 预检及看板请求不稳定，BUG-0039 同会话 `bug-complete` 未发送成功，BUG-0037 子文档打开失败；这些检查保持待复验。下方早期 14/52 诊断及 24/52 人工勾选是历史记录，不能替代本轮 ready 结论。验收状态继续为 pending。

按 52 项 `acceptance-plan.json` 执行完整批量复验。最新[机器证据包](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/20261013165839477668-5a2608ef/summary.md)为 `blocked / diagnostic`：14 项通过（AC-001、002、003、004、005、012、021、022、025、041、042、048、050、052），38 项因逐项真实产品、视觉或文件证据不齐受阻。新增的 AC-004、012、052 使用已授权隔离样本的历史真实产品轮次和只读数据核对；旧轮次不冒充当前共享环境新发送。现有浏览器画面可访问，但未覆盖所需全部阶段×视口截图和 computed style；既有合成 API 截图只作组件回归，不作为真实业务写入证据。AC-001 使用能力矩阵源码和受控 demo 聚焦回归。机器通过数不替代下方既有 24/52 人工/历史签认。当前容器仍绑定共享事实源，未重启或重绑；最终状态保持 pending。

## 回归 AC

- [x] AC-052：`bug-generate` 候选准备后事实源版本变化时，执行前以 `workspace_fact_source_stale` 终止并展示可重试提示；旧候选与文件保留，新 idempotency key 可从当前基准续接。隔离产品 BUG-0038 旧基准被拒绝、新 key 成功续接；BUG-0039 部署后再次显示版本变化提示，后端 2606 kind 聚焦回归通过。

- [x] AC-050：评审迁移后 registry path/status/lifecycle_stage 与 trace 和目标目录一致；BUG-0033 半完成迁移可重试恢复，卡片进入已评审且 review.md 可读；同步失败、伪成功和目录冲突不报告完整成功且保留成果，dry-run/check 不写入。
- [x] AC-051：REQ/BUG 产品评审遗漏注册表和索引同步时，后端仅在完整评审门禁通过后定向补齐并回读；隔离工作区带当前迁移工具，失败原轮次可重验，应用后 checkpoint 可用；结论冲突、越权、缺文件和根因未确认仍阻断。AF-045 修复真实产品发现的阶段/下一步遗漏；REQ 与 BUG 的隔离产品评审已通过，copy checkpoint 与异常门禁由聚焦回归覆盖。

- [x] AC-049：新建 Change 仅有 .openspec.yaml 时原会话历史、主对象关联及候选列表正常读取；准备态成果保留。目标文档缺失返回尚未就绪，真实空间/对象权限撤销仍阻断，符号链接不得通过 capture/proposal fallback 绕过。

- [x] AC-048：执行镜像内 Node/npm/pnpm/OpenSpec/uv 与通用工具可用；实际产品沙箱可离线创建、读取并校验临时 Change。缺工具或固定版本不匹配时明确执行前阻断、释放并发并提示部署更新，不调用模型，不破坏已有文件与权限边界。

- [x] AC-047：评审轮次 stopped 且旧候选仍为 running 时，原会话新发送的 Sprint 命令不得复用旧候选；当前轮次准备、既有成果保护与执行状态独立，服务更新后可继续执行。隔离前置状态 + 同会话真实 Sprint 轮次 completed；容量硬门禁合法阻断纳入，见 [AC-047 证据](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-047-review.md)。

- [x] AC-045：同会话 complete→review 创建当前轮候选，评审结论和目录迁移经后端校验并自动回写；冲突保留成果，重启不丢删除记录；真实事实源应用成功后卡片进入已评审并可打开review.md，模型执行完成不可替代application成功。隔离 REQ-0996 同会话完成并自动应用，8 条删除记录经重启保留；冲突保护由聚焦回归覆盖，见 [AC-045 证据](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-045-review.md)。
- [x] AC-046：评审兼容 status/result 单字段，冲突结论拒绝且轻量提示具体原因；原 rejected 候选仅在无冲突、无后续轮次且无已有应用时可重验恢复，同会话重复恢复幂等，不清空工作区或重跑模型。

- [x] AC-044：规划中卡片不显示草稿或完善中独立状态标签；长负责人省略并可查看全文，不挤压 severity；子文档、补证提示、继续完善及内部门禁不变。

- [x] AC-043：规划中卡片区分 draft/enriching，完善中展示已生成子文档、具体补证提示及可用的继续完善动作；根因 confirmed 与证据门禁不变；桌面及移动端无提示溢出，子文档可打开。

- [x] AC-039：工作区准备失败但执行器未启动时显示执行前阻断及安全原因，释放会话占用，保留未应用文件；历史入口不得显示无限等待。旧 unknown 仅凭准备阶段错误码、无执行器 ID 和围栏匹配恢复。
- [x] AC-042：重复 complete 无新增差异时仍校验完整事实源，一致后返回无需更新；不新增 application、不改文档或状态，不复活历史失败提示；源版本变化、缺文档与状态错误仍阻断。
- [x] AC-041：同会话 generate→bug-complete 使用当前轮次候选和治理写权限；正式保存五件套草稿并自动回写，未确认根因保持 enriching 且不改完成时间，confirmed 加有效证据才允许 pending_review；历史已应用候选不得导致只读回退。
- [x] AC-040：REQ-0027 原成果保留且可续接；治理沙箱临时锁预检通过，req-complete 完整文档及状态门禁通过后自动创建 application、回写事实源并更新工作区基准；无来源、冲突、越界或文档缺失不应用，不靠删除解除阻断。

- [x] AC-038：持续执行跨越 300 秒不因默认墙钟上限中断；手动停止、权限及额度门禁保留。恢复依据原执行器权威状态，长历史在受控上限内可核对，部分成果不得被误报为完成。

- [x] AC-037：仅有用户消息的运行态，AI 输出独立占满 assistant 内容列；落库及历史重开不重复显示，用户气泡保持限宽。由真实组件与接口夹具验证 DOM/computed width，不以手工拼接 DOM 替代。

- [x] AC-036：Worker 维护阻塞不导致心跳过期；短暂不可用后 Chat 自动探测恢复，保留编辑后的草稿与已完成消息，发送重新可用；配置、版本、心跳与网络原因区分展示，不绕过后端发送门禁。

- [x] AC-001：产品内维护命令能力矩阵，明确每个命令当前属于仅展示、demo 模拟、真实候选写入或真实应用写入。
- [x] AC-002：采集池 BUG 卡片触发 Bug Generate 时，后端支持 `BUG-*` 和 `bug-generate` 的 governance preparation。
- [x] AC-003：`bug-generate` 候选校验只允许写入目标 BUG 的 `bug.md`、`trace.md`、BUG registry 和 BUG CHANGELOG，不允许越界改动。
- [x] AC-004：应用 `bug-generate` 候选后，目标 BUG 状态同步为 `draft`，CHANGELOG 下一步变为 `/bug-complete <BUG-full-id>`。
- [x] AC-005：产品内 Bug Generate 成功后，数据库存在对应 governance candidate 和 application 记录，不能只产生普通 Chat turn。
- [x] AC-006：未接入真实写入链路的 complete、review、sprint-propose、opsx 系列命令，不得显示为可成功执行的动作。
- [x] AC-007：若未实现命令被用户触发，产品应给出明确提示，说明该动作尚未接入产品写入链路，并提供应使用的 Codex 命令。
- [x] AC-008：前端非 demo 路径不再把未实现动作模拟成“执行成功，卡片已流转”。
- [x] AC-009：前端测试覆盖 BUG 生成入口、未实现命令提示和 req-generate 既有链路不回退。
- [x] AC-010：后端测试覆盖 REQ generate、BUG generate、不支持命令和越界写入拒绝。
- [x] AC-011：如果新增 API 字段、OpenAPI 或客户端类型，必须同步 API 文档和前端生成物。
- [x] AC-012：需求中心看板刷新后，阶段投影必须来自真实 trace / registry / CHANGELOG，而不是仅来自前端临时 state。
- [x] AC-013：产品内 Bug Generate 准备态的 Chat 输入框只展示简洁 `/bug-generate <BUG-full-id>` 命令，内部治理约束不得裸露在输入框正文；发送执行时由后端根据 governance candidate 恢复治理约束，用户手动编辑后不得追加旧治理约束。
- [x] AC-014：产品内 Bug Generate 发送后的 Chat 历史消息和复制内容只展示简洁 `/bug-generate <BUG-full-id>` 命令，不裸露内部治理约束；`prepared` 且 0 文件时不得显示大型治理成果面板或“查看成果 0 个文件”的空状态。
- [x] AC-015：所有已接入真实治理候选链路的 generate 命令通过 allowlist、manifest、revision、dry-run 和冲突校验后自动应用到项目事实源；自动应用失败、版本冲突、越界、恢复阻塞或校验 warning 时仅展示轻量错误或轨迹提示，不进入人工“待应用成果”确认流程，未接入真实候选链路的命令不得模拟自动应用。
- [x] AC-016：Chat 主对话区所有命令均不得渲染治理成果大面板、`查看成果`、`待应用成果` 或 `审阅治理成果` 弹窗；generate 命令继续后台自动应用，失败、冲突、越界、恢复阻塞或校验 warning 仅通过轻量错误或轨迹提示处理。
- [x] AC-017：Chat 对话区 assistant 消息应占满消息历史可用宽度，不再受共享 `.chat-message` 的 `720px/72%` 限制；用户消息仍保持右侧气泡宽度限制。
- [x] AC-018：Chat assistant 外层消息历史轨道也应占满对话区可用宽度；历史打开会话时仅轮询后端已创建 application operation，prepared 空候选不得申请 application，且不得恢复或渲染治理成果大面板。
- [x] AC-019：Chat assistant 正文 bubble 与 markdown 容器在运行态 computed style 中必须铺满消息历史可用宽度，布局回归不得只校验 CSS 源码规则。
- [x] AC-020：产品运行态必须使用最新 Web 构建；`localhost:39002` 的 dist/bundle 与运行态 bundle 均不得包含 `待应用成果`、`查看成果`、`审阅治理成果` 或 `确认应用`，历史入口 DOM 不得恢复治理面板；`bug-generate`/`req-generate` 完成后应自动创建 governance application 并写入事实源。
- [x] AC-021：`req-generate`/`bug-generate` 的低风险候选自动应用必须由后端 `collect`/controller 创建 application；前端历史入口只允许轮询后端已有 operation，不得发起 application POST 或恢复人工应用 UI。
- [x] AC-022：Chat turn 与 `chat_messages` 必须只保存用户可见 `display_prompt`；执行器所需内部治理约束只能由后端根据 governance candidate 恢复，不能落入用户消息历史。
- [x] AC-023：发送前必须完成执行器 sandbox/dry-run preflight；执行器不可用时返回 `executor_unavailable`，合法执行但候选不符合治理边界时返回 `governance_validation_failed`，两者不得混淆为同一类“无法生成文档”。
- [x] AC-024：产品运行态必须具备 Web 构建版本校验和旧 bundle 一次性自动刷新能力；从历史入口打开 Chat 时必须清理旧治理面板 DOM，运行态 DOM/Network 证据不得出现治理成果大面板、查看成果按钮、待应用面板或审阅弹窗。
- [x] AC-025：Chat 新会话默认推理程度必须为 Low；后端 capabilities 默认值、前端 Composer fallback 和相关回归测试必须一致，避免默认显示 High。
- [x] AC-026：BUG-0025 的 Chat + governance 产品运行态验收必须使用 `bash scripts/docker-down.sh self-storage-sqlite` 与 `bash scripts/docker-up.sh self-storage-sqlite` 配对重启；若未通过 `.env` 启用 local-codex，则使用显式 `--chat-platform` 入口。裸 `docker compose ... backend web` 只允许作为局部调试证据，不得作为产品链路已更新的最终验收依据。
- [x] AC-027：Chat 对话区所有 role=assistant / AI 输出，包括 req-generate、bug-generate、普通 Chat、执行中、完成后和历史恢复状态，外层消息 block、article、正文 bubble、markdown、TurnActivity 和执行中 status/alert 文案均应在运行态 computed width 中占满消息历史可用宽度；用户消息继续保持右侧气泡宽度限制，并保留 Playwright DOM/computed style 回归证据。
- [x] AC-028：Chat assistant 的工具调用/完成状态摘要应作为轻量 meta 左对齐到 assistant 内容列，和头像、正文左边界保持一致；该摘要不得被拉成满宽输出块，正文 bubble、markdown 与执行中 status/alert 文案仍必须保持满宽。
- [x] AC-029：Chat 工作台发送后发生 chat/governance/events fetch 网络异常时，不得向用户显示浏览器原生 `NetworkError when attempting to fetch resource.` 或 `Failed to fetch`；工作台启动、项目绑定、消息读取和执行轨迹读取应分层显示中文局部提示，导航/历史恢复 AbortError 不渲染错误，已生成成功消息不得被后续轮询失败覆盖为全局错误。
- [x] AC-030：Chat 对话区所有 role=assistant 的运行中输出不按命令名或 action 白名单生效；`req-generate`、`req-complete`、`bug-generate`、`bug-complete`、review、sprint、opsx 和普通 Chat 的 TurnActivity、status/alert、正文 bubble、markdown 和 assistant 内容列 computed width 均应等于消息历史可用宽度；用户消息继续保持右侧气泡宽度限制，并保留 req-complete 截图场景与通用命令矩阵 Playwright DOM/computed style 回归证据。
- [x] AC-031：需求中心所有写入型产品命令在创建或复用 Chat 会话前，必须以后端/执行器同一 `/work` 快照校验完整对象 ID、registry path、trace status 和关键文档存在；若治理事实源存在执行器 committed `/work` 不可见的未提交或未跟踪改动，应阻断发送并返回 `workspace_fact_source_stale`，不得进入执行；只读分析命令可继续打开 Chat。
- [x] AC-032：`workspace_fact_source_stale` 提示必须区分本地治理事实源未提交/未同步、标准部署未更新、Git 快照不可读三类原因；需求中心写入型命令按钮阻断时，Toast 必须展示阻断文件类别和处理建议，不得统一提示“确认标准部署已更新”。
- [x] AC-033：所有写入型命令使用 source_root 与治理投影当前文件 manifest/revision，未提交和无关文档修改不阻断；自动同步授权治理文件到隔离工作区。generate 应用后同会话可继续 complete，版本变化和未应用工作区修改仍阻断，不要求治理投影包含 .git。
- [x] AC-034：当仓库绑定显式配置 `workspace_mode: source` 时，Chat 执行器必须以本地真实 `source_root` 作为工作区，所有命令读取当前工作树并直接写入真实仓库；该模式不得创建会话副本、不得覆盖隔离工作区、不得在 generate 成果后再要求候选二次应用。
- [x] AC-035：本地真实仓库模式仍必须保留项目级串行写入协调、成员写权限校验、治理对象状态和产物 allowlist 校验、Task Trace/请求日志脱敏记录、看板刷新事实源投影；会话删除、diff 状态与未知任务恢复不得误认为存在 `<workspace_root>/<conversation_id>` 副本。

## 2026-10-11 现有真实产品轮次补证

- AC-002：Firefox 当前需求中心可见专用 `BUG-0036` 的 Bug Generate 后续状态；本地产品数据库 `governance_candidates` 对 `BUG-0036-bug`、`bug-generate` 有 2 条 `prepared` 候选和 2 条后续 `rejected/governance_validation_failed` 候选。这证明 `BUG-*` 对象的 preparation 确实创建候选；被拒绝的应用仍归 AC-004/005/015 待验，不以准备成功冒充应用成功。
- AC-022：该对象的两次真实 Chat turn `9c06a865-0e53-4fde-910c-45dd953041c4`、`b8167dd1-c682-44b7-8a1b-039f3adf4411` 均为 `completed`，`chat_turns.prompt` 与各自 `chat_messages` 的 user 内容均为 22 字符的 `/bug-generate BUG-0036`，未包含内部治理约束。`app.chat.service.request_turn` 将可见 prompt 传给 `admission.enqueue` 保存；`app.governance.preparation.execution_prompt_for_turn` 在后端根据已绑定 candidate 恢复执行约束，`app.chat.execution` 在执行时调用该函数。该项仅判断存储与恢复边界，不判断候选是否成功应用。
- 07:13 Firefox 刷新后的 BUG-0025 卡片显示“验收 17/52”，与 Issue 复选框一致。其余 35 项的完整条件尚无新增闭环证据，保持未勾选。
- AC-026：07:15 先运行 `bash scripts/docker-up.sh self-storage-sqlite --chat-platform --check`，配置预检通过；确认无 queued/connecting/running/stopping 轮次，保留一条历史 unknown。随后依次运行 `bash scripts/docker-down.sh self-storage-sqlite --chat-platform` 与 `bash scripts/docker-up.sh self-storage-sqlite --chat-platform`，均 exit 0。标准启动重建 Web、backend、Chat executor 和 worker，并启动 governance controller；Docker 显示 backend、chat-worker、governance-controller、MinIO 为 healthy，Web running。07:16 Firefox 重新加载 `localhost:39002/requirements` 后 BUG-0025 仍在验收中并显示 17/52。该项只证明标准部署路径与服务运行，不代替具体命令的 application 成功。
- 07:18 再次刷新需求中心，BUG-0025 卡片显示“验收 18/52”，与本文件复选框一致；剩余 34 项保持待验证。
- 重启后从专用 BUG-0036 采集池卡片重新准备 `bug-generate` 候选 `f57afab3-ad05-5e0b-af25-8ae9343f69a3`；发送时产品提示“项目文件已变化，请重新准备治理动作”，数据库候选仍 prepared 且无 turn/application。候选基准对比只有另一个 Change 的两份验收文档在准备与发送间并行变化。此为 source 工作区版本门禁的真实产品证据，不满足自动应用或失败后完整续接的 AC，完整明细见 Change `verification.md`。
- 经用户授权，建立本机隔离验收仓库 `/private/tmp/moonbox-bug0025-acceptance-isolated`，将当前治理文件复制为独立快照。Compose 覆盖配置检查显示 backend、chat-worker、governance-controller 的 `issues/`、`openspec/`、`iterations/`、`docs/`、`rules/` 和 `.agents/` 均指向该快照；容器实际挂载核对确认三者的 `/app/governance/issues` 来源一致。产品 Firefox 需求中心从隔离快照读取到 captured 的 BUG-0036，并准备候选 `9c199aa3-7ee3-5aaa-8e88-aa86db823416`。原会话由于旧绑定版本被标成完全只读，故该对象未发送。已从产品新建 Capture 以取得全新隔离对象；整理任务仍在运行。隔离环境就绪不等于任何待验 AC 通过，通过数保持 18/52。

- BUG-0037 独立事实源真实轮次：Firefox 从隔离看板采集池进入 `bug-generate`，全新会话 `6686ecd2-3054-4170-bc29-740fe0130fe5` 发送可见命令，turn `bfaba014-622d-4099-8fe4-0aebeb4524e6` 为 completed；candidate `a58c4f0a-a28b-5d2b-a512-a1b2b18e8461` 为 applied，application `ae1dadf5-b3b5-4cc3-8c61-1d0659858af1` 为 applied/verified、无错误。隔离仓库实际生成 `bug.md`，trace 与 registry 为 draft，CHANGELOG 下一步为 `/bug-complete BUG-0037-acceptance-isolated-generate`。Firefox 重新进入需求中心后，BUG-0037 出现在规划中，展示 `bug.md` 与“完善 Bug”动作。AC-004、005、012 因同轮数据库、文件和刷新后产品投影一致而通过；其余 31 项待验。

- AC-014：BUG-0037 新会话在 candidate prepared 且尚无文件时，Chat 主对话区没有治理成果面板或“查看成果 0 个文件”空态。完成后从历史入口重新打开会话，用户消息仅显示 `/bug-generate BUG-0037`；点击该消息“复制消息”并粘贴到未发送的 Composer，内容仍仅为 `/bug-generate BUG-0037`，随后清空草稿。不存在内部治理约束外露。

- AC-021：隔离 BUG-0037 和 REQ-0045 的真实产品轮次分别产生 `applied/verified` application `ae1dadf5-b3b5-4cc3-8c61-1d0659858af1`、`cabd516b-16a3-485c-9c6a-a6615b3aba09`。同轮后端访问日志可见前端 GET application 状态；自 23:34 UTC 起不存在治理 candidate/application 的 POST。前端 `GovernanceResult` 只轮询现有 operation，历史重开后也未产生新的 application。
- REQ-0045 隔离生成补证：candidate `8291d21e-acf7-5d4f-941c-7c9ee40ce5ad`、turn `4770287b-fbbb-4b3d-ba66-29b39550c89a` 完成并应用，application `cabd516b-16a3-485c-9c6a-a6615b3aba09` 为 applied/verified；`requirement.md`、trace、registry 和 CHANGELOG 均为 draft，Firefox 重新进入需求中心后显示规划中 REQ-0045、requirement.md 和完善需求动作。AC-015 仍需异常分支完整复验，不因正常路径判通过。
- BUG-0037 第三次 `bug-complete` candidate `4fcd5d44-903f-5f56-8bcd-7aab88c4ffec` 为 unchanged；同轮无 application，八份相关文件摘要全部与事前基线相同，状态保持 enriching。第二次重复完善曾真实修改 root-cause.md 并应用，未被误称为无差异。此为已通过 AC-042 的产品补证。

- 2026-10-14 隔离复验（AC-013/015/016/018/020）：在 `39102` 新 Web bundle 上，专用 BUG-1001 的 Chat 准备态显示完整 `/bug-generate BUG-1001-bug-0025`，隐藏治理约束；turn `6a66a033-9e73-425b-9458-0f36f8318091` completed、candidate `6de047fa-0eb6-5278-8669-b41c7e5fd51c` applied、application `7695e2fd-c475-4ecd-adbe-f0fd8525b737` applied/verified，隔离事实源 bug.md、trace、registry、CHANGELOG 均为 draft。1440×900 的助手消息外层与历史轨道宽度均为 1168px，当前 DOM 无治理成果面板。此前旧构建 BUG-1000 轮次显示短 ID，虽生成文件却无 application，保留为失败对照。当前浏览器登录会话在重开历史前过期；用户手动编辑分支、AC-015 异常矩阵、AC-016 失败提示及 AC-020 指定的 18102 端口与最新 bundle 一致性仍未形成完整证据，AC-013 后续由产品轮次与后端断言闭环并已勾选；AC-018 亦结合既有隔离历史轮次与本轮 computed style 通过；AC-016 结合真实正常路径与异常组件回归通过；AC-015 和 AC-020 保持未勾选。详见 Change `evidence/acceptance/inputs/AC-013-review.md` 等逐项记录。

- 2026-10-14 完整验收诊断：运行 `opsx_acceptance.py --change fix-requirement-center-command-chain-write-gap --db <隔离数据源>`，证据包 `evidence/acceptance/20261014100845520192-6fbaf085/`；本轮 52 项中 11 项可复用通过、41 项因计划预检与证据缺口 blocked，整体仅为 diagnostic，不是 ready。目标五项中 AC-013、AC-016、AC-018 为 passed；AC-015 缺异常矩阵，AC-020 缺 18102 端口与对应视觉证据。Issue 累计复选框为 40/52。

- 2026-10-14 AC-015 补验：隔离 BUG-1002 的 prepared 候选遭遇专用 capture.md 版本变化，产品只显示“项目文件已变化，请重新准备治理动作”的轻量 alert；旧候选无 turn/application/bug.md。重新准备的新候选 `005d0174-3cae-5245-abb2-ce4a9d391e73` 由 turn `d2ab9252-bbf1-4597-a589-9e0b5900ccdb` 完成，application `5d73ebed-ed3c-4711-a0fc-3a45ea3349d9` applied/verified，事实源与看板 draft/规划中一致。与既有 REQ、BUG 正常轮次及 63 项后端回归合并，单项验收脚本显示 AC-015 passed；证据见 `evidence/acceptance/inputs/AC-015-review.md`。

- 2026-10-14 最新完整验收诊断：`evidence/acceptance/20261014125006387433-712620b2/`，52 项中 12 项通过、40 项因证据或预检缺口受阻，整体仍为 diagnostic。AC-015 为 passed；AC-020 等待 39002 共享产品当前构建下的历史会话 DOM 复核，累计复选框 41/52。

- 2026-10-14 AC-020 登录后复核：Chrome `localhost:39002/chat` 加载当前 `index-zZOrD37_.js`，当前可见按钮与弹窗无四类治理面板文案。所登录空间 `AI原生软件工厂` 未配置仓库，Chat 新会话禁用，历史筛选“全部”仍为 0 个会话；因此未能打开已有 Generate 会话核对历史入口 DOM。阻塞截图 `evidence/acceptance/inputs/AC-020-shared-unbound-history.png`，单项诊断 `evidence/acceptance/20261014141052921655-f4a19b90/` 为 blocked；AC-020 保持未勾选，累计 41/52。

- 2026-10-14 AC-020 恢复复验：经授权使用 Chat + governance 部署脚本恢复共享后端仓库绑定，相关服务健康。`localhost:39002` 运行 bundle 与本机 dist 的 `index-evpnFHfi.js` 摘要一致，四类禁用文案计数为 0。产品历史入口重新出现会话，打开旧 BUG-0036 Generate 轮次，1440×900 DOM 无治理成果面板或按钮；既有 BUG/REQ 自动应用与事实源回读证据见 `AC-020-review.md` 和 `AC-015-review.md`。单项脚本 `evidence/acceptance/20261014143738272820-64f73d0b/` 中 AC-020 passed；累计 42/52。

- 2026-10-14 最新完整验收诊断：先聚焦复验 AC-015、AC-020 均 passed，再执行全量 `opsx_acceptance.py`；证据包 `evidence/acceptance/20261014144105669235-3c8f465a/` 为 13 passed、39 blocked，范围 diagnostic。AC-020 与 AC-015 均复用通过；其余缺口集中于未完成的逐 AC 产物及环境预检。Issue 复选框为 42/52，Change 尚未 ready。

- 2026-10-14 AC-023 复验：隔离产品专用 BUG-1003 的 prepared 候选在 Worker 不可用时，发送 API 返回 HTTP 503、`kind=executor_unavailable`，无 turn；共享产品 BUG-0036 的已完成执行轮次对应 `rejected/governance_validation_failed` 候选。聚焦回归 3 passed；单项验收 `evidence/acceptance/20261014145157001497-bc131813/` 中 AC-023 passed。详情见 `openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-023-review.md`。累计 43/52，整体仍待验收。

- 2026-10-14 AC-023 后完整诊断：`evidence/acceptance/20261014145327516789-1298eee8/` 为 14 passed、38 blocked，AC-023 保持 passed；其余 9 项复选框尚未完成，Change 未达到归档就绪。

- 2026-10-14 AC-024 复验：39002 Chrome 从历史入口重开 BUG-0036 Generate 会话，1440×900 截图与 DOM 均无旧治理大面板、按钮或弹窗；浏览器资源清单记录当前脚本、`/chat` 与历史读取路径。服务端 HTML 与运行脚本一致，实际 bundle 含构建校验及单次刷新标识；与本机 dist 只差随机构建 ID。`runtimeBuild`/治理 UI 回归 20 passed，单项脚本 `20261014151153988807-3a58943d` 中 AC-024 passed；证据见 `openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-024-review.md`。最新完整诊断 `20261014151200457000-7e609a53` 为 15 passed、37 blocked。累计 44/52，Change 尚未归档就绪。
- 2026-10-14 AC-027 复验：39002 的 BUG-0036 Generate 历史在 1440×900 与 390×900，REQ-0041 Generate 完成及 alert 在 1440×900，assistant block/article 均等于历史轨道宽度，内容列、Activity、正文和提示均填满 assistant 可用宽度；用户气泡继续右侧限宽。隔离产品既有 bug-complete 执行中样本经复核；普通 Chat 与其他命令运行中由 11 项真实 CSS Playwright 矩阵及 9 项真实组件合成 API 矩阵覆盖，组件测试 9/9。单项诊断 `20261014153549406595-f0a55a03` 中 AC-027 passed；证据边界与文件见 [AC-027 复验记录](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-027-review.md)。[最新完整诊断](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/20261014153628122351-f9d9f9ae/summary.md)为 16 passed、36 blocked，累计 45/52，Change 尚未归档就绪。
- 2026-10-14 AC-029/030 复验：39002 实际 Web 构建通过六类受控浏览器网络故障注入，页面无原生 fetch 错误、已生成消息保留；31 项前端回归通过，详见 [AC-029 复验记录](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-029-review.md)。运行中宽度由隔离产品 BUG-0039 桌面/移动样本、11 类正式 CSS Playwright 矩阵及指定 req-complete 截图支撑，详见 [AC-030 复验记录](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-030-review.md)。故障注入使用合成 API；req-complete 截图为合成 DOM，不记作共享后端真实轮次。AC-029 单项 `20261014155114961984-27d88098`、AC-030 单项 `20261014155016370675-b12c96ca` 均 passed；AC-027 因共用脚本指纹更新已重验 passed。[最新完整诊断](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/20261014155200394744-042a94bd/summary.md)为 18 passed、34 blocked；Issue 累计 47/52，Change 仍未归档就绪。
- 2026-10-14 AC-031～035 复验：隔离 API 负向测试验证对象 ID、registry path、trace status、关键文档与投影 revision 门禁，阻断时无会话或 turn；只读分析可继续。[AC-031 证据](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-031-review.md)；[AC-032 证据](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-032-review.md)记录三类 Toast 合成响应矩阵。共享本地产品 BUG-0037 同会话 generate→complete 轮次、隔离 source 模式 BUG-1001 真实轮次及无会话副本/事实源文件核对，结合后端回归支撑 [AC-033](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-033-review.md)、[AC-034](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-034-review.md)、[AC-035](../../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-035-review.md)。五项定向诊断 `20261014170151035465-9ffd00d7` 均 passed；14 项既有输入指纹重验中，AC-013 使用隔离 SQLite 单项 `20261014170647402038-9614a8d0` passed。当前完整诊断 `20261014170654068934-ef757e75` 为 23 passed、29 blocked；清单累计 52/52 不等于归档就绪。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-17 16:45:27
accepted_by: workflow-sync
source_change: fix-requirement-center-command-chain-write-gap
source_sprint: sprint-008
evidence: [openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/20261014174148087312-8bde8c1a/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```
