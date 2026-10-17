---
note: workflow-sync — 13/13 Change 已 archive；0 applied；待人工 sign-off
sprint_id: sprint-008
title: sprint-008 验收报告
status: completed
lifecycle_stage: archive
created_at: '2026-09-29 16:03:21'
updated_at: 2026-10-17 16:43:00
---

# sprint-008 验收报告

BUG-0025 AC-051：隔离产品首次 BUG 评审揭示 CHANGELOG 阶段与下一步未同步，原 Change AF-045 已返修。修复后 BUG-0998 与 REQ-0997 的独立产品评审均 completed、候选/应用 applied/verified，注册表、索引、目录、trace 和看板已评审状态一致；59 项聚焦回归覆盖 copy checkpoint、恢复和异常门禁。AC-051 已定向签认；[完整诊断](../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/20261014002725865559-09fdb17f/summary.md)仅此项通过，其余 51 项因输入指纹与材料缺口预检受阻，BUG 整体验收仍 pending，不归档。见 Change [AC-051 证据](../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-051-review.md)。

BUG-0025 AF-044：真实模式未知命令误建对象会话已在当前 Web 源码修正，提示完整 Codex 命令并终止产品请求；BUG/REQ Generate 入口回归保留。需求中心前端 125 项、后端相关测试 46 项通过；AC-007/008/009/010 与指纹受影响的 AC-001/025/043/044 定向通过。完整诊断为 21/52 passed、31 blocked。当前隔离产品镜像尚未包含这次 Web 修改，未记为新产品轮次；AC-006 的旧命令覆盖表述与现有能力矩阵冲突，继续待核对。Change applied、Issue pending，详见 Change 返修台账 AF-044。

BUG-0025 AF-043：隔离产品中旧未绑定候选错误阻断同会话 `bug-complete`，已修正候选选择并通过 3 项后端聚焦回归。BUG-0039 新轮次 completed、候选/application applied，文件及看板为 enriching，根因 unknown、完成时间 null。规划阶段 draft/enriching 的桌面与移动截图、computed style、文档打开证据已补；AC-038、041、043、044 定向通过。当前完整批量诊断复用 17/52，35 项仍缺证据，Issue pending，Change 未归档。镜像标准重建未完成，隔离运行时使用单文件同步；详见 Change `acceptance-fixes.md` AF-043 与验收证据包。

BUG-0026 AF-013：专用治理样本首次产品归档的前两轮在工具链冷启动预检失败，第三轮通过预检并移动到 OpenSpec CLI 旧目录、合并规格后触发 `write_permission_revoked`；唯一归档由宿主脚本迁入标准目录并完成同步，不计产品同轮通过。已修复包工具探针、部署健康探针和严格限定的旧目录迁移权限；18 项聚焦测试与标准部署通过。BUG 验收仍 0/9 pending，待全新产品样本复验。证据见 Change `acceptance-fixes.md` AF-013。

BUG-0026 替代样本产品复验：`verify-chat-archive-transition-window` 对象 Chat 轮次 `b708c17e-11f7-4fe0-95a2-183689400dc2` 已进入运行并显示“归档可写”，仅完成前置读取后 stopped / `reconciled_usage_pending`，未执行归档脚本；样本仍为活动 Change。Mac 锁屏阻断后续浏览器取证，BUG 验收保持 0/9 pending，不计产品首次归档通过。

BUG-0026 AF-014：解锁后同一样本新轮次 `5cf62853-c01e-4620-9317-c00e6ed55ab6` 已进入归档，但在标准目录创建后转 `unknown/execution_access_or_workspace_error`；trace 与 sprint-009 仍为 applied，产品同轮未完成同步。跨挂载复制中完整旧源和未完成标准目标并存的失权测试先失败后通过，目标身份冲突仍阻断。样本半归档恢复与全新产品首次归档继续分开验证；BUG 验收保持 0/9 pending。

BUG-0026 2026-10-11 产品复验：已授权的 `add-git-sync-skill` 首次归档在对象 Chat 中启动并完成真实移动、三条规格合并，但轮次最终“已停止”，最后命令无完成结果且用量待核实；原轮次重试请求失败。宿主唯一归档恢复脚本完成验证和 Workflow Sync，不能替代产品轮次成功。九项 AC 仍 pending；详见 BUG acceptance 与 Change acceptance-fixes。

BUG-0026 AF-011：用户补充全仓自有目录空工具残留范围，八个空目录已确认并安全移除；目录校验和 worker 清理已扩展。单元测试 3 项、Chat 后端全套 48 passed/1 skipped、同款执行器镜像离线隔离探针 1 项通过；探针确认 12 个执行时空路径且退出后宿主清理无残留。Workflow Sync `opsx.modify` 0 errors/0 blockers，验收保持 pending。真实产品新轮次尚待复验，不以隔离探针替代。证据见 `openspec/changes/fix-chat-platform-opsx-archive-source-permission/acceptance-fixes.md` AF-011。

## 验收状态

BUG-0025 AF-040：规划中卡片移除独立“草稿”标签，内部 draft 状态、severity、负责人和动作不变；验收对照见 Change acceptance-fixes.md。AF-039：BUG-0028 生成命令准备期事实源版本变化被误记为通用失败，现已修正为可诊断的 `workspace_fact_source_stale`，保留旧候选并回归新候选续接；后端 51 项通过。真实 BUG-0028 新轮次已完成，正式 bug.md 与 draft 状态一致；标准部署后的错误提示仍待复验。

BUG-0025 AF-037：标准评审迁移入口补齐定向同步、最终注册表核验和半完成重试；BUG-0033 真实目录、registry approved/review、Firefox 已评审卡片及 review.md 读取一致。未重新评审或纳入 Sprint，未宣称 BUG-0033 实现权限缺陷已修复；证据见对应 Change evidence/af037-review-projection.md，待复验。

BUG-0025 AF-036：未完成 Change 不再阻断无关会话历史与关联读取；真实 ACL/路径安全拒绝仍生效。后端 90 passed/1 skipped、前端 7 passed，标准部署完成，真实 Firefox 原会话错误消失、关联和草稿恢复、发送可用。未触发业务模型，准备态成果保留；证据见对应 Change evidence/af036-object-isolation.md，待复验。

BUG-0025 AF-035：执行镜像补齐 Node/OpenSpec/pnpm/uv 及文件工具，构建和真实只读/治理沙箱命令回归通过，标准部署已更新；缺工具时明确终止且不调用模型。运行态 bundle、服务和镜像证据见对应 Change evidence/af035-toolchain.md。本批未发送业务模型轮次，不宣称全命令业务流转验收完成。

Agent 浏览器自主取证治理 Change 的验收返修已将规则接入全部 46 份技能，修正直接转人工补证的旧指引；8 项聚焦单元测试与治理校验通过，覆盖与校验记录见该 Change `acceptance-fixes.md`，待人工复验。

同一 Change 第二轮返修要求 BUG 探索、生成和完善在根因未确认时继续自主补证，文档落盘不结束取证；证据仍不足时保留真实状态。结果与校验见该 Change `acceptance-fixes.md`，待复验。

同一 Change 第三轮返修补齐 `/explore` 与 `/req-explore` 在必要时主动浏览产品取证的规则，保留只读探索边界；校验与证据见该 Change `acceptance-fixes.md`，待复验。

AF-042：BUG-0026 AF-008 修复跨挂载目录迁移与半归档恢复，产品仍通过对象 Chat/Agent 归档；兼容 Issue promote 迁移间隙、无 HOME 日志发现、有界队列背压，88 passed、1 skipped。真实产品恢复轮次 `12822d4c-c26d-4c3a-8ab3-8050d3103dd1` completed、结果可见、标准脚本退出码 0、最终用量 settled；BUG-0027 已由产品 Agent 推进 archive。首次跨设备迁移为合成回归，未用恢复复验冒充首次归档。

AF-041：BUG-0026 source baseline 多对象会话兼容返修完成；BUG-0027 最新归档轮次在 `workspace_prepare` 阶段因 `chat_workspace_baselines.workspace_id=source` 唯一约束冲突失败。执行器现在保留 `conversation.workspace_id=source` 的运行语义，但 baseline 存储键按会话独立保存，避免多个对象会话共享同一唯一键。source 聚焦 3 项通过，Chat 平台相关套件 60 passed、1 skipped；真实产品归档需重启服务后复验。

AF-040：BUG-0026 产品归档入口语义纠正与 Agent 链路诊断返修完成；已确认需求中心卡片归档应继续通过对象 Chat 会话注入 `/opsx-archive` prompt，由 Agent 执行归档，不应改成产品后端直归档。前端归档按钮已恢复为 `/api/v1/chat/object-sessions` + `sessionStorage` prompt + Chat 跳转；setup 准备失败日志补充 `cause_type`。后端 46 项、前端 112 项、TypeScript 与 py_compile 通过；真实产品按钮归档需重启服务后复验。

AF-039：BUG-0026 旧版 `source_bug` trace 归档权限返修完成；BUG-0024 最新 archive 轮次实际执行完成但未产生可见 assistant 输出，执行摘要显示 `openspec/archive/` 与 `openspec/specs/` 仍只读。归档写策略现在兼容 `source_bug` / `source_requirement`，并同步 `archive_write` API schema 与前端“归档可写”标签。后端归档策略聚焦 3 项通过，Composer 17 项通过；真实 Docker worker 端到端归档待重建后复验。

AF-038：BUG-0026 source 模式容器 runtime 挂载重叠返修完成；BUG-0024 最新 archive 轮次进入 `container_mount_overlap`，确认旧配置将 Chat 私有执行数据目录放在 source root 内。平台预检现在拒绝 source 内私有根目录，启动脚本遇到旧配置会自动使用源仓库同级私有目录，避免 `/work` 与 `/runtime` 挂载重叠。平台与 workspace 15 项通过，`docker-up --check` 通过；真实 Docker worker 端到端归档仍待重建后复验。

AF-037：BUG-0026 source 快照容量边界返修完成；BUG-0024 最新 archive 轮次已不再是旧 binding mismatch，而是在 source 快照扫描 ignored 运行态数据时超过容量边界。Git 仓库快照现在使用 `git ls-files -co --exclude-standard`，排除 `.gitignore` 已忽略的 `data/runtime/**` 等运行数据，保留 tracked 与未忽略 untracked 文件。workspace 6 项、workspace + source run_claim 聚焦 10 项通过；真实 Docker worker 端到端归档仍待重建后复验。

AF-036：BUG-0026 旧 copy 会话迁移到 source 工作区返修完成；source root 已验证后允许历史 `workspace_id == conversation_id` 迁移为 `source` 并同步 baseline，避免重启后 BUG-0024 archive 仍在 `workspace_prepare` 命中 `workspace_binding_mismatch`。4 项聚焦 pytest 通过，Chat 平台相关套件 59 passed、1 skipped；真实 Docker worker 端到端归档仍待重建后复验。

AF-035：BUG-0026 source 工作区 `run_claim` 旧目录名前置校验返修完成；source 模式现在由 `_workspace_identity` 统一判定，新增 source 模式 `run_claim` 回归测试，3 项聚焦 pytest 通过。真实 Docker worker 端到端归档仍待重建后复验。

AF-033：REQ-0027 事实源唯一完成门禁返修完成；Chat 工作区、assistant 输出和 candidate 仅作为候选或执行证据，writer 在 applied 前执行 Workflow Sync 并重读事实源。25 项后端治理 writer 与恢复回归通过；待人工复验。

AF-034：REQ-0027 本地部署工作区策略返修完成；常驻部署默认输出 `workspace_mode: source`，执行器直接使用 `source_root` 当前工作树，copy 保留为共享/强隔离显式模式。聚焦测试与文档同步见 Change acceptance-fixes.md；待人工复验。

AF-049：REQ-0027 AC-011 默认 source 首文件故障注入暴露非完成轮次未安全恢复的问题，已按真实隔离轮次修复并用三候选动作六窗口集成矩阵复验。修复版产品轮次在写前执行器失败，四个直接 Chat 命令的恢复矩阵仍缺；AC-011 未签认，见 Change `acceptance-fixes.md` 与 `evidence/acceptance/samples/AC-011.md`。

AF-050：REQ-0027 AC-011 四直接命令新增私有步骤 hash 与终态分类，4×6 隔离故障窗口及同步失败样本通过，扩展回归 172 passed、1 skipped。真实产品故障轮次和动作语义验证未齐，AC-011 不签认，功能清单仍 12/20。

AF-051：隔离 REQ-9204 真实产品轮次在首业务文件写入后终止 worker，重启后候选拒绝、零应用、全治理树与不可变基线逐字节一致。该窗口通过，AC-011 整项仍待七动作其余真实故障轮次，清单保持 12/20。

AF-052：独立隔离项目补采七动作的写前、首文件、同步中与同步后真实轮次；`opsx-archive` 规格合并及目录迁移后中断的部分现场被安全阻断并保留，尚不能安全续做。治理快照已纳入活动 Change 控制文件 `.openspec.yaml`，相关回归 156 passed、1 skipped。AC-011 继续 partial，功能清单 12/20 不变。

AF-053：隔离归档部分现场经唯一性与 hash 核对后走后置恢复分支，规格未重复合并；Workflow Sync 现接受合法无缩进 Sprint YAML 列表、拒绝无效语法，聚焦回归 20 passed。旧产品轮次曾出现 `sprint-propose` 同步成功但 YAML 无效；`req-opsx` 中断后长期 unknown。七动作矩阵仍不齐，AC-011 不签认，12/20 不变。

AF-032：评审结论兼容、冲突拒绝、验收事件保持与更新、拒绝原因持久化及原候选重验回归通过，后端114项、前端17项、TypeScript通过。真实恢复及标准部署结果见 BUG-0025 Change acceptance-fixes.md；仍待人工复验。

AF-031：REQ-0027 同会话 complete→review 历史成果经新候选和controller真实应用，DB verified、本地review目录、registry/trace approved及浏览器已评审卡片一致；未重跑模型。合成回归覆盖REQ/BUG评审结果、越界/冲突、删除重放。保留人工复验门禁，详见Change返修台账。

AF-030：移除完善中独立标签并验证长负责人显示；不变更业务状态，证据见 BUG-0025 Change 返修台账。

AF-029：完善中卡片事实展示返修，后端 91、前端 111 项通过；标准部署后真实文件投影与 1440/390px 浏览器 DOM、Network、截图验证通过。全仓 DS 存量违规未纳入本次修复；完整证据边界见 BUG-0025 Change acceptance-fixes.md，待人工复验。

AF-028：重复完善零差异幂等核验与历史旧错误隔离；79 项后端、15 项前端通过。标准部署后真实同会话 complete 返回 unchanged，无 application 且完整文件不变；真实组件合成 API 的浏览器打开/历史 DOM、Network、截图通过，证据见 BUG-0025 Change 台账。

AF-027：135 项后端回归通过、1 项跳过；包含同会话 generate→bug-complete、本轮写权限、草稿与确认状态、自动回写及冲突边界。标准部署后 BUG-0024 原会话真实验证 candidate/application applied，正式文档 enriching，根因 hypothesis、完成时间 null，原 capture 保留、工作区基准自动更新。详见 BUG-0025 Change 台账；待人工复验，不将业务根因待补证视作回写失败。

AF-026：后端 115 passed、1 skipped，包含文件保留、冲突、缺少来源、越界、完整文档、controller 回写和基准同步；真实 REQ-0027 续接轮次 completed，candidate/application applied，本地 trace/PRD pending_review。REQ 功能验收不等于本次文档恢复；详细证据见 Change 台账。

AF-025：工作区准备失败终态、历史安全恢复及文件保留，后端 88 passed/1 skipped，前端 14 passed；部署与 DOM 证据见 BUG-0025 Change 返修台账。REQ-0027 上轮完成不代表已应用，未自动覆盖隔离成果。

BUG-0025 AF-024：原超时轮次归并停止、取消默认 300 秒限制，44 项后端回归通过；真实续接不以合成时钟测试替代，证据见 Change 台账。

BUG-0025 AF-023：未落库运行输出满宽返修；新增真实组件的运行/落库/历史宽度断言，证据见关联 Change acceptance-fixes.md。

BUG-0025 AF-022：心跳与能力探测恢复返修，后端 5 项及前端 29 项回归通过；真实运行态验收见 Change acceptance-fixes.md，本项仍待复验。

not_started；Sprint 刚进入规划，范围项待后续 Change 实现、验证和归档闭环。

## Scope 验收

| 范围项 | 状态 | 验收入口 |
|---|---|---|
| BUG-0027-page-scroll-bottom-light-background-exposed | in_sprint / 待创建 Change | `issues/bugs/review/BUG-0027-page-scroll-bottom-light-background-exposed/acceptance.md` |

## 验收计划

- [ ] BUG-0025：产品内命令展示与真实治理写入链路一致，未实现命令不再模拟成功。
- [ ] BUG-0025：`bug-generate` 产品链路可生成 `bug.md`、同步 trace/registry/CHANGELOG，并产生 governance candidate/application。
- [ ] BUG-0025：`bug-generate` 产品准备态 Chat 输入框、turn 和消息历史仅展示或保存简洁命令，内部治理约束由后端按 candidate 恢复。
- [ ] BUG-0025：`bug-generate` 发送后的历史消息不裸露内部治理约束，且 `prepared` / 0 文件时不显示大型治理成果面板。
- [ ] BUG-0025：已接入真实治理候选链路的 generate 命令校验通过后自动应用；只有冲突、越界、失败、恢复阻塞或校验 warning 才进入人工确认。
- [ ] BUG-0025：Chat 主对话区所有命令不显示治理成果大面板、查看成果按钮或审阅治理成果弹窗；异常仅通过轻量提示或轨迹入口处理。
- [ ] BUG-0025：Chat assistant 消息占满消息历史可用宽度，用户消息继续保持右侧气泡宽度限制。
- [ ] BUG-0025：历史打开治理会话时不恢复治理成果面板，pending 候选只轮询后端 operation；低风险 generate 候选由后端 controller 自动创建 application 并刷新事实源。
- [ ] BUG-0025：生成命令发送前完成 executor sandbox/dry-run preflight，并区分 `executor_unavailable` 与 `governance_validation_failed`。
- [ ] BUG-0025：Chat assistant 正文 bubble 与 markdown 容器运行态铺满消息历史可用宽度，并有 computed style 回归证据。
- [ ] BUG-0025：所有 AI/assistant 消息在 req-generate、bug-generate、普通 Chat、执行中、完成后和历史恢复状态均满宽，覆盖 TurnActivity 与 status/alert 文案 computed width；用户消息仍保持右侧气泡限制。
- [ ] BUG-0025：Chat assistant 工具调用/完成状态摘要作为轻量 meta 左对齐到 assistant 内容列，不漂浮到正文上方中间；正文和执行输出继续满宽。
- [ ] BUG-0025：Chat assistant 运行中满宽规则不按命令场景生效，覆盖 req-complete 截图场景以及 generate、complete、review、sprint、opsx 和普通 Chat 命令矩阵。
- [ ] BUG-0025：Chat 工作台网络异常分层展示，NetworkError/Failed to fetch 不裸露，AbortError 不渲染，已成功消息不被轮询失败覆盖。
- [ ] BUG-0025：Chat 新会话默认推理程度为 Low，后端 capabilities 默认和前端 Composer fallback 保持一致。
- [ ] BUG-0025：运行态部署验收使用项目标准 `scripts/docker-down.sh` / `scripts/docker-up.sh self-storage-sqlite` 配对入口，服务集合覆盖 Web、backend、chat-worker 与 governance-controller；裸 compose 仅作为局部调试。
- [ ] BUG-0025：相关 API、DB、前端类型、Workflow Sync 和观测链路验证闭环。
- [ ] BUG-0027：深色主题下 `/chat`、`/requirement-center` 的 `html`、`body`、`#root` 与工作台根容器背景一致，向上滑动或宿主 overscroll 不露出浅色根层背景。
- [ ] BUG-0027：浅色主题、登录页、官网首页和管理后台背景不被深色工作台修复误污染；保留 computed style 与 1440px 浏览器截图证据。

## 证据边界

- [ ] REQ-0027 AF-035：HTML 预览对象 URL 清理兼容修复后，前端聚焦回归 122/122 通过；隔离项目已取得 AC-001 captured 分支、AC-002 captured→draft 分支的完成轮次和九组真实看板/抽屉视觉证据。AC-003 完善需求在标题门禁得到负向观察，夹具修正后仍遇工作区准备失败；其余分支及 28 个视觉组合仍缺证据。完整验收清单 28 项 `blocked / diagnostic`，保持 pending；详见 Change `acceptance-fixes.md` 与 `evidence/acceptance/samples/`。
- [ ] REQ-0027 source 模式续验：新隔离项目的 `req-generate` 产品轮次 applied；`req-complete` 续接轮次因 trace 越界字段被控制器 rejected，执行器直写后的 trace、注册表和浏览器卡片仍显示 pending_review。AC-019 已出现失败子场景，须返修并使用新对象复验；验收继续 pending，见 Change `evidence/acceptance/samples/AC-019.md`。
- [ ] REQ-0027 AF-036 复验：拒绝候选后源治理文件和需求卡片已回退到 draft / 规划中；Chat 返修后默认折叠错误成功话术并显示拒绝结论。后端相关测试 99 项、前端相关测试 29 项通过。AC-019 该负向子场景通过，其余组合、AC-003 成功路径及完整视觉矩阵仍待补证；验收继续 pending。

- [ ] BUG-0025 AF-038：后端评审投影收尾、隔离工具同步、原轮次恢复和 checkpoint 已通过 128 项回归；未部署、未执行真实模型评审，产品复验待完成。证据见对应 Change evidence/af038-review-finalization.md。

- [ ] BUG-0025 AF-020：未提交治理文件和无关文档不阻断写入型命令；当前 manifest/revision 一致时自动同步隔离工作区，generate 后同会话继续 complete；内容版本冲突和额外工作区修改仍保护。合成回归证据见 Change acceptance-fixes.md，真实业务复验待完成。
- [ ] BUG-0025 AF-021：本地真实仓库模式下，`workspace_mode: source` 使执行器直接使用 `source_root` 当前工作树；命令直接写真实仓库，保留项目锁、权限、产物校验和看板刷新，且不再走副本同步或候选二次应用。合成回归证据见 Change acceptance-fixes.md，真实业务复验待完成。
- [ ] REQ-0027 AF-034：本地常驻部署默认绑定 `workspace_mode: source`；copy 仅作为共享、多人或强隔离场景显式配置。聚焦测试通过后需真实业务复验确认不会再为本地默认会话创建副本或产生事实源漂移。
- [ ] BUG-0027：验收证据以 BUG acceptance 与后续修复 Change 为准；本次 sprint-propose 只完成规划纳入，不代表 UI 修复已实现。

验收证据应保留在关联 BUG、OpenSpec Change 和本 Sprint 四件套中。本 Sprint 关闭不代表生产升级或对外发布授权；发布链路需另行执行 `/release-propose`、`/release-prepare` 和 `/release-publish`。
BUG-0025 AF-034：已评审 REQ/BUG 加入迭代命令补齐 `--req`/`--bug`；后端两类生成与前端两类点击跳转回归通过。真实部署浏览器复验待进行，详见 Change acceptance-fixes.md。

BUG-0025 AF-041：BUG-0036 专用夹具的两次真实 `bug-generate` 轮次都写出 draft 文件，但候选均 rejected 且无 application。首轮无语义改写 capture 的问题已修复，6 项聚焦回归通过；第二轮因共享项目并行写入其他治理文档仍被正确阻断。验收保持 15/52，待在独占或专用验证环境核对自动应用与看板，详见 Change `acceptance-fixes.md`、`verification.md`。

BUG-0026 AF-009：REQ-0043 的 Chat 归档截图显示 Change 已移动而目录校验阻断，Issue 尚未完成同步。新增 worker 沙箱外真实目录预检、执行沙箱空挂载点精确判定与归档前预校验，15 项聚焦测试及同款归档沙箱隔离探针通过；真实产品端仍待复验。证据见 BUG-0026 Change `acceptance-fixes.md` AF-009。

BUG-0026 AF-009 部署补证：标准部署完成，五个服务健康，运行中 chat-worker 已加载预检；Chat 模块 46 passed、1 skipped。REQ-0043 半归档收尾与产品端到端复验仍待执行。

- [ ] BUG-0026 AF-010：17:33 产品归档重试仍因命令环境丢失 `CODEX_HOME` 与四个空目录残留失败；已改用私有 Chat 命令标记并清理空残留。60 passed、1 skipped，标准部署健康；REQ-0043 宿主标准脚本续跑完成归档，产品新轮次仍待复验。

- [ ] BUG-0026 AF-012：Issue 验收文档已把原表格 AC-001～007 和两个待复验范围整理为九条未勾选核对项；需求中心现显示“验收 0/9”并可打开文档。表格内既有测试结果不等于验收签认，真实产品新轮次与最终结论仍待复验，归档保持阻断；详见 Change `acceptance-fixes.md` AF-012。

- [ ] BUG-0026 AF-015：用户授权的纯治理样本在产品对象 Chat 首次归档成功，标准脚本退出 0、规格合并、Workflow Sync 0 errors、轮次 completed；截图已转存 Change `evidence/`。Issue 验收现为 6/9，AC-001 仍缺关联 Issue 首次归档与 promote 同轮证据，AC-003 缺普通命令产品拒绝证据，AC-005 缺 copy 模式独立产品轮次；BUG Change 归档继续阻断。详见 BUG `acceptance.md` 本日逐项判定。

BUG-0025 隔离项目真实产品复验：BUG-0037 生成/完善、REQ-0045 生成与 BUG-0038/0039 版本冲突及恢复已留 candidate/application、文件和 Firefox 证据；当前 24/52，28 项待验。AF-042 修复 2606 缺失 `workspace_fact_source_stale` kind，聚焦 1 passed，隔离部署后中文错误态复验。仍 pending，不归档；详情见 BUG acceptance 与 Change verification/acceptance-fixes。

REQ-0027 AC-009 续验：隔离项目对未接入动作仍返回对象会话，违反后端动作白名单；AF-044 已补入口校验，46 项后端聚焦测试通过。新构建产品复验及其余权限矩阵未完成，AC-009 failed、功能清单保持 2/20；详见目标 Change `acceptance-fixes.md` 与 `evidence/acceptance/samples/AC-009.md`。

REQ-0027 AF-044 新构建复验：独立 `39028` API 重启后，未知动作返回 422/2604 且无会话，合法只读动作仍可进入，隔离会话/候选/轮次聚合数量不变。AC-009 其他角色、事实源、跨项目组合尚未覆盖，状态转回 partial、不勾选；功能清单仍 2/20。

BUG-0025 AC-047：专用隔离 SQLite 的 stopped 评审/running 旧候选前置状态下，原产品会话新 Sprint 轮次 completed，当前轮次独立通过选择预检；既有评审事实保留。sprint-009 容量超硬上限，合法阻断正式纳入。定向验收 passed，整体验收 pending；见 Change [AC-047 证据](../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-047-review.md)。

BUG-0025 AC-045：专用隔离 REQ-0996 同会话 complete→review 真实产品轮次及后端 application 均已验证；评审目录迁移、8 条删除记录、看板“已评审”和 review.md 入口经隔离服务重启保持。两轮 complete 后端拒绝表明模型完成不能替代应用成功；冲突由聚焦回归覆盖。见 Change [AC-045 证据](../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/inputs/AC-045-review.md)。整体验收 pending。

BUG-0025 最终归档：当前输入的完整验收 52/52 passed，readiness ready（`20261014174148087312-8bde8c1a`）；OpenSpec 两项能力规格已合并，Change 已移入[归档目录](../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/)，Issue 已移入 `issues/bugs/archive/`，Workflow Sync 与阶段迁移通过。上文待复验条目均为当时的阶段性记录；最终逐项结论以[验收证据包](../../../openspec/archive/2026-10-14-fix-requirement-center-command-chain-write-gap/evidence/acceptance/20261014174148087312-8bde8c1a/summary.md)和归档 Issue 的 `acceptance.md` 为准。

AF-054：第二隔离项目补采七动作真实故障窗口，`req-opsx` 部分同步现场经文件、身份门禁核对后安全续做；另有产品归档脚本成功路径。`--dry-run` 同步误判已修复。归档正式同步中断等格子尚缺，AC-011 仍 partial，REQ-0027 功能清单 12/20。

AF-055：REQ-0027 AC-012 的规格合并重试反例已用归档预览指纹护栏修复；真实 CLI 分段及独立隔离项目的 Sync、Issue 迁移中断续做和未知外部编辑阻断已记录。完整对象 Chat 四阶段轮次仍缺，AC-012 partial，REQ-0027 功能清单 12/20 不变。

AC-012 产品补证：隔离对象轮次归档命令成功后出现直接规格编辑，安全重试识别未知差异并阻断；已调整私有日志可写路径和归档技能边界。四阶段完整产品故障矩阵仍缺，AC-012 未签认，12/20 不变。

2026-10-16 AC-012：独立隔离产品对象四个归档中断窗口均确认 stopped 后从原对象安全续做，规格指纹和目录唯一性逐轮通过；归档命令后规格漂移被产品轮次完成门禁标为 failed。功能清单仅签认 AC-012，REQ-0027 为 13/20。聚焦诊断 `20261016163308188999-c93ae0bc` 本项 passed；完整验收 `20261016163345834948-e224d841` 为 complete / blocked（13 passed、15 blocked），仍非归档就绪。脱敏证据见 Change `evidence/acceptance/samples/AC-012.md`。

## Sprint 关闭验收结论

2026-10-17 16:43:00（Asia/Shanghai）关闭检查：13/13 Change 均已归档，252/252 项任务完成；8 个范围 Issue 已关闭且 Workflow Sync 预演验收投影均为 passed。Sprint 归档就绪、陈旧扫描（60 文件、0 blocker）、目录结构和 env ignore 策略均通过。BUG-0025 AC-003 归档后单项附件变化已按原计划命令复验，并以独立补证绑定原 manifest、输入指纹及附件旧/新哈希；原 52/52 完整清单未改写。

最终结论：Sprint 关闭门禁通过。AI Usage 快照为 `estimated_fallback`：自动发现未找到可归属的本地会话 token 事实，不能作为实际用量或覆盖率证据；后续若需审计实际用量，应提供可归属的本地 session 文件并重新生成快照。本结论不代表生产发布、镜像构建或升级授权。
