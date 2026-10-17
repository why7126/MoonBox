---
title: 需求中心治理命令链证据驱动批量验收记录
created_at: 2026-10-10 09:46:00
updated_at: 2026-10-14 17:43:06
---

# 需求中心治理命令链证据驱动批量验收记录

## 验证摘要

本记录按 BUG-0025 的 52 条 AC 逐项判断证据。只有 AC 的全部子条件均有直接回归或运行态证据时才在 Issue `acceptance.md` 勾选；合成测试不能代替 AC 明确要求的真实产品观察。早期批次的 `pending` 结论仅代表当时阶段；最终完整验收 52/52 passed、readiness ready，Change 已归档。

2026-10-10 聚焦复跑：后端 `test_governance_candidates.py`、`test_chat_preparation_failure.py`、`test_governance_review.py`、`test_governance_board.py` 共 187 passed；`test_chat_toolchain.py`、`test_chat_incomplete_objects.py`、`test_review_promotion_sync.py` 共 25 passed；Web `requirement-center.test.tsx` 117 passed。后端仅有既有 Starlette/httpx 弃用 warning。Firefox 刷新 `localhost:39002/requirements` 后，BUG-0025 仍位于验收中；运行态 backend 的 `preparation_failure.py`、`governance/preparation.py` 与工作树摘要一致。该浏览器观察只证明看板与当前部署可访问，不证明全部治理命令场景。

## 本批通过的 AC

| AC | 证据类型与入口 | 覆盖结论 |
|---|---|---|
| AC-003 | 本轮 `test_governance_candidates.py::test_bug_generate_write_set_and_next_step_rejection`；`acceptance-fixes.md` 初次 apply 验证 | 目标四文件 allowlist、越界文件和错误下一步均被断言；该项要求的是候选校验，自动化证据足够 |
| AC-040 | `acceptance-fixes.md` AF-026；本轮 `test_requirement_completion_recovery.py`、`test_governance_writer.py` | REQ-0027 原轮次真实续接，candidate/application applied，正式 PRD/trace 为 pending_review，旧文件保留；沙箱锁、缺来源、越界与冲突由回归覆盖 |
| AC-041 | `acceptance-fixes.md` AF-027；本轮 `test_bug_completion.py`、`test_governance_candidates.py` | BUG-0024 同会话真实 complete，candidate/application applied，五件套草稿正式回写，根因 hypothesis 时保持 enriching；根因及权限负向门禁由回归覆盖 |
| AC-042 | `acceptance-fixes.md` AF-028；本轮 `test_bug_completion.py`、`test_requirement_completion_recovery.py` | 原会话重复 complete 的真实候选为 unchanged，无 application，完整工作区与源文件字节未变；完整文档/状态/版本负向门禁和历史错误隔离由回归覆盖 |
| AC-046 | `acceptance-fixes.md` AF-032；本轮 `test_governance_review.py` | `status/result` 兼容及冲突拒绝有回归；BUG-0024 原 rejected 候选真实重验后 application 为 applied/verified，重复恢复未新增应用或模型轮次 |
| AC-048 | `evidence/af035-toolchain.md`；本轮 `test_chat_toolchain.py` | 实际非 root 沙箱离线执行 OpenSpec 命令、固定工具版本及缺工具执行前阻断均有直接证据；保留已有文件与权限边界 |
| AC-049 | `evidence/af036-object-isolation.md`；本轮 `test_chat_incomplete_objects.py` | Firefox 原会话刷新后对象与关联恢复；后端覆盖未就绪、真实 ACL 拒绝和符号链接边界，准备态文件保留 |
| AC-050 | `evidence/af037-review-projection.md`；本轮 `test_review_promotion_sync.py` | BUG-0033 真实迁移残留经定向同步后 registry、trace、目录和 Firefox 卡片一致，review.md 可读；临时仓库覆盖失败保留、重试、伪成功、冲突、dry-run/check |

## 本轮一次性批量复核的新增通过项

| AC | 证据组合 | 判定 |
|---|---|---|
| AC-025 | `test_chat.py` 既有后端 capabilities 默认 Low 断言、本轮 `chat-composer.test.tsx` 通过；AF-011/012 记录部署后容器 `execution_config()` 默认 low | 后端默认、前端 fallback 与运行态配置一致 |
| AC-036 | AF-022 部署后 24 次真实 Worker 心跳采样最大 0.551 秒、真实会话 readiness=ready；本轮 Chat 后端聚焦回归及 `chat-capabilities-recovery.cjs` 当前 Web DOM/Network 通过 | 维护、恢复、草稿保留及发送门禁证据组合完整，UI 网络情景使用夹具 |
| AC-037 | AF-023 标准部署；本轮 `chat-live-output-width.cjs` 当前 Web 的 1440/1920/390px 共 9 个真实组件 DOM/computed width 状态通过 | 符合 AC 明定的真实组件与接口夹具验证，不采用手工拼接 DOM |
| AC-039 | AF-025 真实 DB 旧 unknown 轮次已恢复为 failed、占用释放且 8 个文件摘要不变；本轮后端准备失败回归和 `chat-preparation-failure.cjs` 当前 Web 打开/历史 DOM/Network 通过 | 后端真实恢复与前端真实组件夹具共同覆盖全部条件 |

## 当前产品真实会话新增证据

2026-10-10 11:03:56 Firefox 从 BUG-0025 原会话发送只读轮次，产品已完成并回复 12/40；刷新后用户/助手消息各保留一次。DevTools computed box：历史和 assistant 外层均 1147px，assistant column/bubble/markdown 均 1105px，用户消息 760px；工具摘要左边界与正文同为 290px，宽 348px。由此本轮追加通过 AC-017、019、028。完整读数、页面和限制见 Issue `acceptance.md`；无真实写入命令。

## 44 项集中判定矩阵

本矩阵覆盖上批剩余的全部 44 项。“待验”表示对应 AC 的某个子条件还没有足够证据，不代表实现失败。浏览器脚本中合成 API 场景单独标注。

| AC | 本轮判定 | 可用证据 | 未关闭的条件 |
|---|---|---|---|
| 001 | 已验 | 当前产品前端命令能力矩阵逐项核对；显式 demo、真实默认与未知命令 3 项聚焦回归；AC-001 定向验收 | 生成走候选准备，对象会话写入由后端应用门禁约束，探索只读，未知命令转 Codex 提示；详见 [矩阵复核](evidence/acceptance/inputs/AC-001-review.md) |
| 002 | 通过 | BUG-0036 Firefox 真实产品入口 + `governance_candidates` 四条候选记录 | preparation 已证实；应用成功另由 AC-004/005/015 判断 |
| 004 | 通过 | 隔离 BUG-0037 真实产品 turn、application、文件及 CHANGELOG | `draft` 与下一步 `/bug-complete` 同轮一致 |
| 005 | 通过 | candidate `a58c4f0a` 与 application `ae1dadf5` 的真实数据库关联 | candidate applied、application applied/verified，非单纯 Chat 完成 |
| 006 | 已验 | 当前能力矩阵及非 demo 动作分支、完整前端回归 | complete/review/sprint/opsx 进入对象会话而不宣称应用成功；未知命令提示 Codex，见 [复核](evidence/acceptance/inputs/AC-006-review.md) |
| 007 | 已验 | 未接入命令提示聚焦断言及完整前端回归 | 提示包含原命令且对象会话请求为零，见 [复核](evidence/acceptance/inputs/AC-007-review.md) |
| 008 | 已验 | 非 demo 未接入命令聚焦断言及完整前端回归 | 原卡片保留、无模拟成功流转，见 [复核](evidence/acceptance/inputs/AC-008-review.md) |
| 009 | 已验 | BUG/REQ generate 与未知命令三类前端断言，125 项完整回归 | 三个入口与提示覆盖齐全，见 [复核](evidence/acceptance/inputs/AC-009-review.md) |
| 010 | 已验 | 后端候选及不支持动作 46 项回归 | REQ/BUG generate、越界写集和未知 action 拒绝覆盖，见 [复核](evidence/acceptance/inputs/AC-010-review.md) |
| 011 | 已验 | 当前后端 OpenAPI 与仓库契约相等；Orval 三份客户端逐字节再生成核对；API 索引审计 | API 文档、契约和客户端生成物同步，见 [复核](evidence/acceptance/inputs/AC-011-review.md) |
| 012 | 通过 | BUG-0037 隔离文件、registry、CHANGELOG 与 Firefox 看板刷新 | 刷新后转入规划中并显示 bug.md、完善 Bug |
| 013 | 待验 | 本轮 258 后端/191 前端回归、历史 AF 记录 | 当前产品输入框隐藏约束与手改续接未同轮验证 |
| 014 | 通过 | BUG-0037 prepared 空态、历史重开与复制粘贴 | 仅可见简洁命令，未见内部约束或 0 文件成果面板 |
| 015 | 通过 | REQ-0045、BUG-1001 正常应用，隔离 BUG-1002 版本冲突轻量提示、旧候选未应用及新基准恢复，63 项后端回归 | 其他异常机制由受控回归覆盖，未宣称逐分支真实产品轮次 |
| 016 | 待验 | 本轮 258 后端/191 前端回归、历史 AF 记录 | 当前产品全命令历史入口与异常轨迹矩阵未完成 |
| 017 | 通过 | Firefox BUG-0025 真实 Chat 轮次 + DevTools computed box + 历史刷新 | 当前已完成态满足本项；全命令运行态仍归 AC-027/030 |
| 018 | 待验 | 本轮 258 后端/191 前端回归、历史 AF 记录 | 历史入口 operation 只读轮询与空候选未同轮验证 |
| 019 | 通过 | Firefox BUG-0025 真实 Chat 轮次 + DevTools computed box + 历史刷新 | 当前已完成态满足本项；全命令运行态仍归 AC-027/030 |
| 020 | 通过 | 39002 Chat + governance 服务恢复健康；本机 dist、容器与浏览器均为 `index-evpnFHfi.js`，摘要一致且四类禁用文案为 0；旧 BUG Generate 历史 1440×900 DOM 无面板，既有 BUG/REQ 自动应用与事实源回读记录齐备 | 单项诊断 `20261014143738272820-64f73d0b` 中 AC-020 passed；整体仍受其他 AC 缺口阻断 |
| 021 | 通过 | 隔离 BUG-0037、REQ-0045 application + 后端访问日志 + 历史重开 | application 均 applied/verified；前端只 GET 已有 operation，未 POST 申请 |
| 022 | 通过 | BUG-0036 两次真实 turn/user message 存储值 + 后端候选恢复调用路径 | 可见 prompt 存储与执行约束恢复边界已核对；应用结果不属本项 |
| 023 | 通过 | 隔离产品执行器不可用 503、共享产品候选治理校验失败、3 项聚焦回归 | 单项 `20261014145157001497-bc131813` passed；详见 AC-023 复验记录 |
| 024 | 通过 | 39002 历史入口 1440×900 截图、DOM/资源路径、实际 bundle 摘要与 20 项前端回归 | 单项 `20261014151153988807-3a58943d` passed；旧 bundle 单次刷新由受控回归覆盖，未替换共享产品正在运行的 bundle |
| 025 | 通过 | AF 历史运行态 + 本轮聚焦回归/当前 Web 浏览器 | 已覆盖，见上表 |
| 026 | 通过 | 2026-10-11 标准 `docker-down.sh` / `docker-up.sh self-storage-sqlite --chat-platform` 配对重启，服务状态及 Firefox 刷新 | 标准运行态部署门禁满足；具体命令应用结果由其他 AC 判断 |
| 027 | 通过 | 39002 BUG/REQ Generate 历史与完成态 1440×900、390×900 computed style；隔离产品 bug-complete 执行中样本；11 项真实 CSS Playwright 矩阵、9 项真实组件合成 API 矩阵、9 项组件测试 | 单项诊断 `20261014153549406595-f0a55a03` passed；普通 Chat 与其他命令运行中由合成矩阵覆盖，证据边界见 `evidence/acceptance/inputs/AC-027-review.md` |
| 028 | 通过 | Firefox BUG-0025 真实 Chat 轮次 + DevTools computed box + 历史刷新 | 当前已完成态满足本项；全命令运行态仍归 AC-027/030 |
| 029 | 通过 | 39002 实际 Web 构建六类浏览器网络故障注入截图与可见文案，31 项前端回归 | 单项 `20261014155114961984-27d88098` passed；API 为合成数据，未中断共享后端，详见 `evidence/acceptance/inputs/AC-029-review.md` |
| 030 | 通过 | 隔离产品 BUG-0039 运行中桌面/移动截图及 computed style；11 类正式 CSS Playwright 矩阵、req-complete 截图、9 项真实组件合成 API 矩阵 | 单项 `20261014155016370675-b12c96ca` passed；req-complete 为合成 DOM 截图，详见 `evidence/acceptance/inputs/AC-030-review.md` |
| 031 | 通过 | 隔离 API/SQLite 负向门禁：ID、registry、trace、文档、revision，阻断无会话/turn；只读分析放行 | 负向路径不应生成产品 turn，详见 `evidence/acceptance/inputs/AC-031-review.md` |
| 032 | 通过 | 前端真实组件三类 stale Toast 合成响应与旧部署 fallback；126 项前端回归 | 未对共享产品制造 Git 损坏，详见 `evidence/acceptance/inputs/AC-032-review.md` |
| 033 | 通过 | BUG-0037 同会话 Generate→Complete 产品轮次；隔离副本模式的当前 manifest、无 .git 投影、冲突保护后端回归 | 两模式证据分列，详见 `evidence/acceptance/inputs/AC-033-review.md` |
| 034 | 通过 | 共享 source 模式 Generate turn；隔离 BUG-1001 事实源文件、applied/verified、无会话副本；执行器后端回归 | 两轮来自不同数据库，详见 `evidence/acceptance/inputs/AC-034-review.md` |
| 035 | 通过 | source 模式产品轮次与 Task Trace；锁、撤权、allowlist、删除、diff、未知恢复后端回归 | 并发冲突为受控回归，详见 `evidence/acceptance/inputs/AC-035-review.md` |
| 036 | 通过 | AF 历史运行态 + 本轮聚焦回归/当前 Web 浏览器 | 已覆盖，见上表 |
| 037 | 通过 | AF 历史运行态 + 本轮聚焦回归/当前 Web 浏览器 | 已覆盖，见上表 |
| 038 | 已验 | 当前隔离 SQLite 轮次 67825fa2-122c-4204-99ca-9a194f55885a；18 项停止、权限、额度、恢复与部分结果聚焦回归 | 真实轮次持续 332 秒后 completed，候选与应用 applied/verified；单项诊断 same-turn-complete，负向门禁以回归覆盖，详见 [复验](evidence/acceptance/inputs/AC-038-review.md) |
| 039 | 通过 | AF 历史运行态 + 本轮聚焦回归/当前 Web 浏览器 | 已覆盖，见上表 |
| 043 | 已验 | 隔离产品 REQ-0041 draft、BUG-0036 enriching 的四组视觉与样式；当前产品打开 root-cause.md 和继续完善会话；AC-043 聚焦回归 | 完善中展示六份子文档和具体补证提示；双视口提示无溢出，文档加载成功；root cause 仍 unknown，状态未越过 enriching，详见 [真实产品复验](evidence/acceptance/inputs/AC-043-review.md) |
| 044 | 已验 | 隔离产品 REQ-0041 draft、BUG-0036 enriching 的 1440×900 / 390×900 四组视觉和 computed style；AC-044 聚焦前端回归 | 无独立状态标签，长负责人省略且 title 完整，severity 可见；子文档、补证提示、继续完善及内部状态门禁保留，详见 [真实产品复验](evidence/acceptance/inputs/AC-044-review.md) |
| 045 | 已验 | 隔离 REQ-0996 同会话产品 complete→review；65 项聚焦及 59 项评审回归 | 两候选及 application 分别 applied/verified；原 plan 删除、review 文档与卡片一致，重启后 8 条删除记录保留；冲突由回归覆盖 |
| 047 | 已验 | AF-033/038/039 + 同会话产品轮次 d5833d7f-d6e3-41fe-8411-d2bfaabcdb97 | 旧 stopped/running 候选由隔离夹具构造；新 Sprint 轮次 completed，因既有容量硬门禁未纳入，原成果和旧候选保留 |
| 051 | 通过 | [隔离 BUG/REQ 真实产品评审与 AF-045 证据](evidence/acceptance/inputs/AC-051-review.md)、59 项评审回归 | 两类产品轮次均 completed/applied/verified，遗漏投影由后端补齐并回读；copy checkpoint 与异常门禁由聚焦回归覆盖 |
| 052 | 通过 | 隔离产品 BUG-0038/0039、AF-042、后端聚焦回归 | 旧基准阻断、原文件和候选保留，新 key applied/verified；部署后中文提示与错误 kind 已复验 |


| 场景族 | AC | 现有证据及剩余缺口 |
|---|---|---|
| 初始命令能力与生成链 | 001、002、004、005、006、007、008、009、010、011、012、013、014、015、016 | 已有单元、组件和部分历史产品生成证据；尚缺逐项对应的当前版本产品轮次、数据库应用记录与完整 API/客户端核对。旧“未接入”措辞还需对照后续已实现命令，不能机械判通过 |
| Chat 宽度、历史、错误 | 018、020、021、022、023、024、027、029、030 | `acceptance-fixes.md` 有多批次 DOM、computed style、真实浏览器与部署记录；各 AC 包含多状态或负向条件，需按当前 Web bundle 重跑对应场景矩阵后逐项判定 |
| 部署与事实源工作区 | 026、031、032、033、034、035 | 历史标准部署及 source/copy 回归已记录；本批只核对服务可访问及两份后端文件摘要，未再次配对重启，也未执行事实源版本变化、权限和未应用差异矩阵 |
| 长任务 | 038 | 既有真实会话和回归分别覆盖部分场景；还需核对当前版本的恢复、维护阻塞与超时边界 |
| 命令续接与评审写入 | 045、047、051 | AC-051 已完成 BUG/REQ 两类真实产品评审与投影收尾；AC-047 已从原会话新发送并完成；容量硬门禁阻断纳入 |
| 规划中卡片 | 043、044 | 当前部署 Web 的桌面/移动浏览器夹具通过，真实规划中对象的对应观察仍待补齐 |

## 归档门禁

2026-10-10 批次已通过 15/52，待验证 37/52；当时 Firefox 看板显示 15/52。2026-10-11 依据 BUG-0036 真实产品数据库轮次补充 AC-002、AC-022，随后用标准脚本配对重启完成 AC-026，当前已通过 24/52、待验证 28/52。当时 Firefox 刷新后 BUG-0025 卡片显示“验收 18/52”；隔离产品后续新增通过项已回填文档，原项目看板尚未再次刷新。`acceptance_status: pending`，最终验收人、签收时间均为空。未通过项需继续以隔离验证环境批量生成事实源和真实产品轮次，再复核写入、异常与恢复矩阵。不得把本文件存在或测试总数视为全部验收通过。

## 2026-10-10 专用对象真实产品写入复验

Firefox `localhost:39002`，390×900，11:20:21 从需求中心 Capture 创建 `BUG-0036-bug`。产品结果页、`issues/bugs/plan/BUG-0036-bug/{capture,trace}.md`、BUG registry/CHANGELOG 和刷新后的看板相互印证：采集记录真实写入，状态为 `captured`，阶段为 `plan`，未关联 Sprint/Change。对象被明确标为验收夹具，不是新缺陷；但它仍在 MoonBox 同一项目，不能称为独立环境。

从该卡片启动 `bug-generate` 后，Chat 会话 `f44e9702-bd35-4ad4-8626-2b2ca3191d05` 显示完整主对象、简洁命令和“治理候选对象已失效”只读提示。DevTools 观察到项目 context HTTP 503。实际发送返回「项目文件已变化，请重新准备治理动作」，未持久化执行轮次；从看板再次进入仍复用失效候选。`bug.md` 不存在，registry/trace 保持 `captured`。因此只确认 Capture 写入、Bug 生成入口与 stale 阻断 UI；不能确认 Bug 候选可执行、自动应用、应用记录、历史可见命令、失败后新 key 续接或 AC-052 全部条件。对应 AC-002、004、005、012、013、014、015、022、031、032、052 均继续待验。本次真实产品行为已暴露需要定位的阻断：新建对象紧接生成时，预备候选即被判过期，重新从卡片发起也无法恢复。未绕过该门禁，也未改动 BUG-0031。

后续重新准备的 11:28:10 轮次成功发送并写出 draft 文件，但同轮治理 candidate 为 `rejected/governance_validation_failed`，无 application；首轮 baseline 对比发现 `capture.md` 被 Workflow Sync 的分级字段重排额外改写。AF-041 改为已正确分级时原样保留 capture，聚焦测试 6 passed。11:43:40 再次执行时 capture 已保持不变，然而同一源工作区另有 BUG-0026 acceptance 和关联 Change 台账并行写入，后端仍拒绝候选，未产生 application。两轮的 assistant“已生成”及看板 draft 仅说明文件已写，不能证明受控应用成功。需在独占或专用验证环境重跑；其余 AC 勾选与总数不变。

## 2026-10-11 现有产品轮次补证

Firefox 当前需求中心仍可见 BUG-0036 规划中卡片与 BUG-0025 验收中卡片。对当前本地产品数据库做只读核对：BUG-0036 的 `bug-generate` 候选有两条 prepared 和两条 rejected，证实 AC-002 的 `BUG-*` preparation；两个真实 completed turn 的 `chat_turns.prompt` 与各自 user `chat_messages.content` 均仅保存 `/bug-generate BUG-0036`。后端 `request_turn`/`enqueue` 保存可见命令，`execution_prompt_for_turn` 根据绑定候选恢复内部约束，worker 执行路径调用该函数，满足 AC-022。候选 rejected 且无 application 的结论不变，AC-004/005/015 仍待验证。已通过数由 15 增至 17，其余 35 项保持未勾选。

标准部署补证：`docker-up.sh self-storage-sqlite --chat-platform --check` 通过；确认没有活跃 Chat 轮次后，按顺序执行 `docker-down.sh self-storage-sqlite --chat-platform` 和 `docker-up.sh self-storage-sqlite --chat-platform`，均 exit 0。Web 与 backend 重建，五项服务运行；backend、chat-worker、governance-controller、MinIO 报 healthy，Web 运行且 Firefox 重新加载看板成功。历史 unknown 轮次未被改写为完成。AC-026 因而勾选；此部署不证明自动应用链路已成功。

重启后的新轮次：专用 BUG-0036 夹具备份到被忽略的私有运行目录后，仅目标对象的 trace、registry、CHANGELOG 恢复至 captured，并移除该夹具的生成文档；Firefox 从其采集池卡片重新进入 Bug Generate，后端创建 prepared 候选 `f57afab3-ad05-5e0b-af25-8ae9343f69a3`。发送时产品提示“项目文件已变化，请重新准备治理动作”；候选仍 prepared、`turn_id` 为空，未创建新 turn/application。候选 baseline 与当前工作树对比仅发现另一个 Change 的 `acceptance-fixes.md`、`trace.md` 在准备与发送间发生并行写入。该结果再次证实共享 source 工作区版本门禁正在阻断真实自动应用；AC-004/005/015/052 等完整条件仍未满足。夹具保留 captured，不再在并发写入期间重复重置。

隔离项目续验：用户授权建立专用隔离项目后，将当前仓库克隆到本机私有临时目录，并复制当前治理文件，作为独立事实源。产品三服务使用临时 Compose 覆盖将治理目录挂载到该快照；`docker compose config` 和容器实际挂载均核对 backend、chat-worker、governance-controller 指向同一 `issues/` 来源。原共享产品出现一条其他对象的执行轮次时先等待其停止，确认无 queued/connecting/running/stopping 后才切换；三个服务恢复 healthy。Firefox 需求中心显示隔离快照中的 captured BUG-0036；新 prepared 候选 `9c199aa3-7ee3-5aaa-8e88-aa86db823416` 因复用旧 Chat 会话绑定而被标成完全只读，故未发送。随后从产品新建隔离 Capture，候选整理任务仍在运行。此阶段只证明隔离挂载与只读保护，不将它计入 52 项 AC 的通过数。

BUG-0037 隔离产品成功轮次：07:35:04 从采集池启动 Bug Generate，turn `bfaba014-622d-4099-8fe4-0aebeb4524e6` 完成；candidate `a58c4f0a-a28b-5d2b-a512-a1b2b18e8461` 与 application `ae1dadf5-b3b5-4cc3-8c61-1d0659858af1` 分别为 applied 与 applied/verified，无错误。隔离事实源的 bug.md、trace、registry、CHANGELOG 已互相核对；Firefox 再次进入需求中心看到规划中 BUG-0037、bug.md 和“完善 Bug”动作。AC-004、005、012 通过，总数 21/52。

AC-014 补证：BUG-0037 新会话的 prepared/0 文件状态无治理成果面板；历史重开后的用户消息及“复制消息”粘贴结果都仅为 `/bug-generate BUG-0037`，内部约束未外露。当前 22/52。

REQ-0045 隔离生成：candidate `8291d21e-acf7-5d4f-941c-7c9ee40ce5ad`、turn `4770287b-fbbb-4b3d-ba66-29b39550c89a`、application `cabd516b-16a3-485c-9c6a-a6615b3aba09` 均成功；文件与刷新后看板 draft 一致。BUG-0037 第三次 complete candidate `4fcd5d44-903f-5f56-8bcd-7aab88c4ffec` 为 unchanged，无新 application，八份文件摘要与事前一致。23:34 UTC 后访问日志只有 application GET，无 candidate/application POST；AC-021 通过。AC-015 的异常分支仍待验，当前 24/52。

### AC-052 隔离部署后真实产品复验

BUG-0038 旧候选准备后修改目标 capture，Firefox 发送前阻断，旧候选 prepared、文件保留、无 turn/application；新 key 从当前基准完成，application applied/verified。发现 `check_send` 的 2606 响应缺少约定 kind，已补 `workspace_fact_source_stale` 并新增聚焦断言，1 passed；隔离 backend/worker/controller 重建健康。BUG-0039 复验同一“准备后修改目标 capture”情景，Firefox 再次显示「项目文件已变化，请重新准备治理动作」，候选仍 prepared，零执行轮次与应用。此项满足旧候选保留、新 key 续接及部署后错误态，内部 kind 由同一路径回归断言。当前 24/52，余 28 项，验收仍 pending。

### AC-023 执行器预检错误分类复验

隔离产品专用 BUG-1003 候选 `1913da4c-1e2b-5192-9c5e-d1458b6e9d2a` 在 Worker 停止时发送，HTTP 503 返回 `executor_unavailable`；候选保持 prepared、无 turn。隔离 Worker 和测试管理员原密码哈希已恢复。共享产品 BUG-0036 turn `9c06a865-0e53-4fde-910c-45dd953041c4` 已完成，但对应 candidate `a4a6c11f-7232-5a37-8e94-607d2e3bf31c` 为 `rejected/governance_validation_failed`。聚焦回归 3 passed；单项验收 `20261014145157001497-bc131813` 中 AC-023 passed。详情见 `evidence/acceptance/inputs/AC-023-review.md`。

### AC-024 Web 构建版本与历史入口清理复验

共享产品 39002 已登录浏览器从历史列表重开 BUG-0036 Generate 会话，当前脚本与服务端 `/chat` HTML 同为 `index-evpnFHfi.js`，运行 bundle 含构建 ID 与单次刷新标识，四类旧面板文案均为 0。1440×900 DOM 的旧治理面板、禁用按钮与 dialog 计数均为 0；浏览器资源清单可见脚本、CSS、`/chat` 及历史消息/轮次/候选读取路径。截图和 computed style 见 `evidence/acceptance/inputs/AC-024-review.md`；`runtimeBuild` 与治理 UI 聚焦回归 20 passed。旧 bundle 差异自动刷新通过受控回归验证；本轮未在共享运行态故意替换 bundle。

### 2026-10-14 最终自动验收与 readiness

当前完整验收证据包 `evidence/acceptance/20261014174148087312-8bde8c1a/summary.md`：52/52 passed，scope=complete；readiness=ready，stale=[]。前端真实组件浏览器取证覆盖 1440、1920、390 视口的运行、落库和历史恢复共 9 状态；前端 126 项、验收工具 20 项、执行前失败 9 项及不完整 Change 5 项聚焦回归通过。AC-040 对照已授权隔离 REQ-0996 的 complete 应用，正式 REQ-0027 未写入；AC-041 为隔离 BUG-1001 同会话 Generate→Complete 当前产品轮次及五件套文件回读。隔离管理员原密码哈希已恢复，临时会话已注销。Workflow Sync `opsx.accept` 成功，Issue acceptance_status=passed；root-cause/workaround 的 frontmatter.status 语义提示为人工审阅 warning，非阻断。
