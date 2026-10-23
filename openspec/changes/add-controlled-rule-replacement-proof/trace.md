---
title: 受控规则替代证明追溯记录
change_id: add-controlled-rule-replacement-proof
requirement_id: REQ-0050-controlled-rule-replacement-proof
requirement: REQ-0050-controlled-rule-replacement-proof
sprint: sprint-013
iteration: sprint-013
status: applied
created_at: '2026-10-22 13:24:21'
updated_at: 2026-10-22 17:50:12
prototype_refs:
- path: issues/requirements/review/REQ-0050-controlled-rule-replacement-proof/prototype/web/prototype.html
  role: html-structure
- path: issues/requirements/review/REQ-0050-controlled-rule-replacement-proof/prototype/web/context.md
  role: ui-contract
prototype_gate:
  decomposition: done
  ui_skeleton: pending
  visual_acceptance_1440: pending
  req_final_consistency: done
knowledge_base_refs:
- docs/knowledge-base/best-practices/admin-media-upload-chain.md
- docs/knowledge-base/best-practices/governance-recovery-archive-evidence.md
- docs/knowledge-base/incidents/20261022-compatible-requirement-successor.md
- docs/knowledge-base/retrospectives/sprint-011-retrospective.md
product_data_collection_observability:
  status: applicable
  affected_layers:
  - usage_events
  - request_logs
  - task_traces
  - task_trace_spans
  - authorization_audit
  - governance_archive
  reason: 当前方案记录差异查看、请求及归档审计；旧版确认、授权与首次启用事实仅作历史保留。
  validation: AC-L01—L12 均按 v4 重新取证；当前聚焦单测通过，真实页面、MySQL、独立验收待复验。
execution:
  schema_version: 1
  started_at: 2026-10-22 13:36:07
  completed_at: 2026-10-22 17:50:12
  last_event: opsx.apply
---

# 受控规则替代证明追溯记录

## 2026-10-23 v5 已归档基线校正

BUG-0063 已归档且规则生效，不再作为待归档候选。REQ-0050 v5 只解释当前未归档对象的规则差异，复用正常验收与归档检查，不新增独立兼容证明。逐项诊断见 evidence/acceptance/20261023225114357767-f44e70ec/：AC-L12 单项通过，其余 11 项待本版产品/签署证据，整体仍未就绪；记录见 acceptance-fixes.md。

## 2026-10-23 v4 无额外确认复评与返修（历史，已由 v5 校正）

产品方案已复评通过；当前代码和验收材料正在改造。新版本不要求空间所有者额外确认规则修改；旧确认与旧证明只读保留。BUG-0063 当前草案写明“不再要求独立兼容证明”，与本需求首个允许场景冲突，故继续阻断，不扩大精确允许范围。旧版 28/28 及后续 0/12 均不代表 v4 已验收；独立签署和真实页面复验仍未完成。

## 2026-10-23 轻量方案替换状态

原方案的 `opsx.apply` 与 28 项验收通过是历史事实；新版产品方案及 AC-L01—L12 已复评，当前替换仍在研发和验证中。旧版页面与新增授权入口已停用，精确规则修改、空间所有者确认、对象阻断项和归档前重新检查已接线。详细取证与未完成项目见 `acceptance-fixes.md` 的“轻量方案替换”及新版 `acceptance-plan.json`。不得把旧版通过结论当作新版归档就绪，也不得据此归档 REQ-0050 或放行 BUG-0063。

## 来源与范围

REQ-0050-controlled-rule-replacement-proof已评审，sprint-013规划13/30人天；本Change为新增机制，保留BUG-0063与sprint-012历史范围。当前正在实施并采集隔离验证证据，未修改生效spec或正式授权。

## 就绪与原型

需求文档Ready；原型Partially Ready：结构拆解完成，UI Contract/Skeleton与冲突处理见design.md；首轮Skeleton、1440/390视觉、computed style及最终一致性待实施。选择DS复用现有Chat，不整页CSS移植。Mock只作设计输入，不证明真实权限与批准。

## 证据与门禁

20功能、4横切、4原型AC未执行；tasks 1.3建立可执行acceptance-plan，不能以文档存在声明通过。正式引导信任根及两类授权是归档/启用前置，需求批准不代替它们。BUG-0063候选基线变化时需独立返修与新批准，不修改旧证明。

## 验证记录

创建阶段已验证工件结构、中文标题、身份唯一性、Sprint与Issue绑定和CLI apply依赖就绪；当前实施验证记录见下文，完整逐AC验收尚未完成。验收失败不改写历史事实。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-10-22 13:24:21 | req.opsx | 创建提案、设计、两项能力规格与22项实施任务，执行尚未开始。 |

最终工件检查：OpenSpec strict、当前中文/全仓残留分离、标题、身份唯一性、Sprint Scope、上下文预算与目录结构通过；目录校验仅提示既有legacy SQLite运行目录，未迁移或改动。所有22项任务未开始，CLI工件complete不表示实现完成。

## UI 骨架首轮确认

用户已确认：右侧差异抽屉、保留义务与独立签署分组、底部审批动作、首次启用独立区域，按此接入真实 Chat 页面。首轮结构截图：`evidence/skeleton/review-1440.png`（1440×900）。截图为隔离结构 Mock，不是正式 Chat、真实授权或归档证据。正式壳内状态容器、响应式、焦点及视觉证据仍待实施，不将首轮确认等同于 UI 交付完成。

## 实施与验证记录

- UI 结构确认已承接；真实 Chat Composer 已增加规则替代审阅入口，批准/拒绝/撤销复用确认组件，首次启用使用独立面板。真实视觉和完整归档产品证据仍待采集。
- 新增精确提案、外部信任、Ed25519 授权事件、项目围栏与检查点基础模块；新路径缺少权威上下文时保持拒绝。统一归档写入和自举执行器仍在实施，尚未完成 apply。
- 分类基础回归 12 项通过；首次启用用途隔离 9 项通过；SQLite 授权及真实会话 API 批次 8 项通过；一次性 MySQL 授权/领取批次 10 项通过（含并发审批唯一胜出、触发器拒绝 UPDATE/DELETE、重复迁移）。这些是命令/合成样本，不是正式归档签认。
- 原归档基线回归 52 项通过。首次运行缺 OpenSpec PATH 导致一项工具启动失败，补齐项目 Node/OpenSpec PATH 后该文件全量通过；没有通过改写断言或放宽门禁消除失败。
- 新前端审阅交互 4 项通过，类型检查通过；后续首次启用面板改动仍需增量复验。
- 已建立 28 项验收计划。全部 required_sample 保持 pending，直到对应真实/视觉/文件状态证据核验。REQ 功能 AC 补齐机器可识别的复选框 ID，未更改验收语义。

### 连续执行检查点：首次真实转换

- 当前仍为 REQ-0050-controlled-rule-replacement-proof / add-controlled-rule-replacement-proof / sprint-013 的 apply；未完成态同步、未执行正式归档、未修改 BUG-0063 或 sprint-012。
- 补齐 Chat 命令准备与 Sprint 最终门禁的权威上下文；提案并发准备使用唯一键回读；旧公开证明仅在未领取且旧签名、不可变事件均可验证时更新。提交凭据绑定原 journal 摘要、基线与目标规格树，历史核验检查前驱完整性并最终复读 journal。
- 普通协调器与历史边批次 10 项通过；证明重新批准/自举领取与用途隔离批次 17 项通过；新增首次启用执行器 6 项通过，覆盖合并、迁移、同步、签名中断及篡改拒绝。执行器测试使用真实 SQL、文件及签名，工具和独立验收为显式测试替身，不作为真实产品验收。
- 真实登录 API 批次 5 项通过：所有者批准、幂等、空间管理员拒绝、签名失败回滚；前端审阅及首次启用动作族共 8 项通过，TypeScript 与生产构建通过。分类证据在 API 权限测试中为替身，真实部署另行验证。
- 已建立无正式数据的非 root 隔离镜像及独立 Unix socket 签名容器；可信工具目录验证通过，真实 HTTP 准备两方转换清单成功。首次转换已完成实际 OpenSpec 合并、迁移与 Workflow Sync，提交阶段暴露 strict_json 局部导入遮蔽错误；回读为 activating、revision 6，未错误发布 active。错误已修复并由完整执行器回归覆盖，正在新隔离样本重新验证。
- 剩余：统一 CLI/全部写入口围栏及在线核验、独立部署正式配置、完整实际转换/替代/重启证据、真实 Chat 1440/390 深浅主题与成功附件保留、API/部署/安全及 REQ 文档同步、逐 AC 验收与完成同步。正式授权缺失只阻断正式启用/归档，不阻断上述隔离实施。

### 连续执行检查点：真实提交拒绝与重启恢复

- 修复后第二版合成部署通过实际 HTTP、OpenSpec、Workflow Sync 和签名服务完成首次启用，回读 active。先前尝试停止签名服务晚于提交完成，因此不计为中断证据。
- 第三版隔离镜像摘要 `d83b7e35ea1c3e655b180c9ba2141f81cc6b8852d24d1e2196b675bc2b853e80`。签名服务仅开放 `bootstrap.owner`，实际 confirm 返回 HTTP 409；数据库回读 `state=activating, stage=synced, revision=6, operation_id=isolated-installation`。恢复签名用途并实际重启后端后，resume 返回 HTTP 200、`state=active, revision=8`，操作 ID 保持一致。样本明确为固定合成转换，不能替代本 Change 全部 28 项 AC 或正式运维授权。
- 真实 Chat 截图已保存在 `evidence/product/bootstrap-prepared-1440.png`、`bootstrap-confirm-1440-dark.png`、`bootstrap-active-1440-dark.png`、`bootstrap-active-390-dark.png`、`bootstrap-active-390-light.png`、`bootstrap-active-1440-light.png`；390 浅色样式见 `bootstrap-390-light-style.json`。草稿保留；成功附件、普通替代全部状态以及其他视口样式证据仍待补齐。
- Composer 19 项回归通过，包含执行服务未就绪时归档草稿仍可审阅、未自动发送。签名服务 3 项测试在允许 Unix socket 的隔离测试权限下通过；沙箱内绑定失败属于运行限制，未放宽断言。恢复请求增加精确 revision 比较，归档工具超时保持安全错误，工具信任检查覆盖依赖目录。

### 连续执行检查点：跨进程权威与普通替代样本

- 普通批准增加已完成策略启用门禁；prepared/authorized/activating 均不能签发普通批准。授权/领取/刷新/API 批次 26 项通过，分类/自举/协调器/历史边批次 37 项通过；新增原操作移动后可读、其他入口仍拒绝的归档边测试通过。
- 新增可信工具子进程上下文：仅经继承管道传递项目身份、操作和围栏，子进程重新查库鉴权；不传签名私钥，不把上下文当作批准。8 项管道、错误输入、超时及描述符关闭测试通过。第四版隔离镜像 `0c198029c90eb69baea5cbd6cefe957828a09cec2f49eee1ae50472ce4be6b47` 已通过这条真实工具路径完成首次启用，回读 active/revision 7。
- 第四版固定测试夹具的首次转换实际安装独立保护条文与普通规则基线，再创建 `extend-compatible-rule` 合成候选；准备接口返回 prepared，服务端能力允许所有者批准。后续审批/普通归档/混合历史及视觉证据仍在采集。样本验收只验证固定夹具结构，未冒充本需求完整验收。
- API 索引、部署与安全边界已同步；OpenAPI/Orval 重新生成，TypeScript 通过。统一 CLI/全部写入口、最终文档和逐 AC 收尾仍待完成，不执行 opsx.apply 完成事件。

### 2026-10-22 真实普通替代归档与界面批准续接

- 用户确认的抽屉已接入真实 Chat；隔离页面验证批准、撤销、拒绝、签名服务不可用后的同请求重试，原草稿与拒绝原因保持。失败尝试未追加授权事件，批准未创建 Chat 轮次或自动归档。
- 首次普通归档预演被 OpenSpec 拒绝：合成样本错误地将空白规范化摘要写成规格文件，场景标题不再独立成行。修正合成文件格式、重算验收与提案摘要并重新批准，没有复用旧批准。
- 新隔离版本 v5 的真实首次启用达到 active，普通替代完成领取、OpenSpec 合并、唯一归档迁移、Workflow Sync、提交验签。归档操作 completed/revision=5，提案 completed/revision=3，活动目录不存在且归档目录唯一；Task Trace 包含 prepared/approved/claimed/merge_verified/move_verified/synced/completed。
- 增量验证：旧证明安全刷新 10 项；提交、协调器及认证 API 18 项通过。新增保护覆盖不同提案的旧 sidecar 只能在无领取、无归档日志、无历史迁移且原签名/不可变事件完整时更新；其他情况继续拒绝。
- 当前仍在 apply；跨入口共同提交、真实成功附件保留、完整逐 AC 证据与收尾尚未完成。上述隔离合成规格不等同正式 BUG-0063 或本 Change 的人工签署；未启用正式策略或归档正式对象。

### 统一写边界补充实施

- v5 同一真实归档请求再次调用返回 completed/replayed=true，原操作标识不变。
- 新增在线只读 admission 与 CLI 客户端：精确版本、策略、输入指纹及安全原因码；只读候选核验使用数据库签名记录且不创建 sidecar。撤销后的最终复读拒绝继续。CLI 不提供批准入口，不读取私钥，不执行本地归档；会话配置限仓库外私有文件，拒绝非本地明文 HTTP 与重定向。
- 普通归档增加独立持久检查点，共用项目 OS 锁、数据库 fence 与租约；普通路径不能消费替代批准。为此新增 governance_archive_operations 加法表，2.2 重新保持未勾选，等待更新后的 MySQL 及迁移批次验证。
- 增量回归：普通归档中断恢复与可信子进程上下文 14 项通过；只读准入、替代协调器、提交、证明刷新、自举及认证 API 42 项通过。还需真实跨入口接入和完整稳定批次，未宣称交付完成。

### Chat 共同提交与键盘交互增量

- Chat `/opsx-archive` 在项目存在可信策略记录时接入后台共同提交，不再构造模型执行器；用原对象/精确提案恢复原操作。无此策略的既有部署保留旧路径。成功/失败均有独立可信零模型 token 事件，并修复结算读取；相关 Chat 与原结算回归 13 项通过。
- 普通对象归档提供共同 API 和在线 CLI；已有受控历史的项目禁止旧离线 shell 入口直接写规格。Sprint 写入编排仍待接入，当前不得将此项标为完成。
- 真实 DOM 取证确认 Esc 焦点偏移根因是工作台全局 Escape 监听器把焦点移到用户菜单。ChatDialog 现在消费自身 Escape（繁忙时保持弹窗），并以入口 ref 恢复焦点。实际复验 focus=replacement-review、dialogCount=0、归档草稿原样保留；证据见 evidence/product/ordinary-escape-focus.json 与 ordinary-escape-preserves-draft.png。弹窗与审阅组件 10 项回归通过。

### 共享关闭入口真实复验与修复

- 真实隔离 Chat + local worker + MinIO：69 字节无敏感附件为 ready；携带 Skill 和 `/opsx-archive REQ-9001-synthetic` 被独立验收门禁拒绝后，三者均保留，chat_turns 为 0。证据 `evidence/product/attachment-skill-rejection.json` 与同名 PNG。
- 最新共享入口回归 216 passed、1 skipped；补充 Node/OpenSpec PATH 后被跳过的真实 CLI 合并测试单独通过。
- v6 隔离镜像完成首次可信启用、候选只读准入、CLI 受控替代和普通独立条文归档；Sprint 缺独立签署返回 409 missing_signoff。所有身份、签署与数据均为合成样本，不代表正式授权。
- Sprint 原操作停在 move_verified：先发现隔离镜像漏装既有 title_gate 的只读依赖；补齐后真实 Workflow Sync 自动添加旧文档时间戳，触发 sprint_inputs_changed。保留原阻断与检查点，不改写它的批准或清单。
- 修复仅归一化 Sprint 文档自动 note/时间戳及前导空行；签署、手工内容与其他元数据仍绑定。完成历史重放绑定关闭文档及完整历史准入，不因后续独立归档误判。Workflow Sync 已签署摘要保持已完成；对应 7 项回归通过。完整一致版本重建复验中。

### 最终实施与证据收敛

- 最新后端 v8 镜像 `917cc1f7f2d34fd03ebef1b73cecee39df57accd87d2a84b3e23e1dd50fd5f19`：实际控制器队列/领取/执行完成 Sprint 合成样本，零模型调用与用量结算；只截取受控治理目录，快照失败保留原归档操作并报告证据不可用。
- 同版本普通替代在签名器停机后停留 synced；API 重启、签名器恢复后，同一 operation 完成，规格哈希未变，再次调用 replayed=true。证据见 recovery-v8 三份脱敏 JSON。
- 本 Change 两份精确规格增量在另一个 v8 镜像隔离项目完成首次转换，active/revision7；exact-change-bootstrap.json 绑定完整文件哈希，不只验证简化规则。
- 真实管理员账号审批403；所有者确认族、取消/Esc/焦点及1440/390深浅主题完成核对。最终确认弹窗新增目标项目、条文、24小时期限与不发送/不归档说明，新增四组合截图。过期/部分状态为显式投影夹具；真实审批与自然时间语义由 API/可控时钟另证。
- REQ requirement/acceptance/trace 更新当前实施事实；业务流程/故事/原型与批准策略一致，历史评审记录保持原事实。API/DB/部署/安全/客户端和测试映射已同步，公开手册待发布说明在 usage-notes.md。
- 前端29项通过、TypeScript通过、Vite生产构建通过（555kB包体警告）；当前中文与全仓残留、目录、上下文预算校验通过。目录仅有既存 legacy SQLite 提示，未动运行数据。
- 逐 AC 验证计划已映射完整源码与28项证据，视觉阶段×视口明确，正在执行机器证据包。计划预检首次发现 argv 应为数组列表，已修正；这是计划格式错误，不作产品功能失败。
- 正式 sprint-012 只读仍有 BUG-0063 验收证据与5处历史路径阻断。未启用正式策略、未替代正式条文、未关闭 Sprint。

### 完成门禁

28/28 AC 完整证据包通过，run_id=20261022174854361280-cdc430f3；24项由本次稳定批次的有效检查点复用，未重复执行同组成功测试。当前 --readiness 返回 ready/stale=[]。归档临时副本 --preview 通过，未写正式规格或 journal。最后一项收尾进入串行完成同步；正式归档准入另行只读复核，不能由预演替代可信启用授权。

### 完成同步与正式准入

- opsx.apply 与 opsx.accept 均 exit0，REQ acceptance_status=passed，Change execution.completed_at 已由 Workflow Sync 维护，22/22任务完成。
- 最终验收28/28 ready，临时副本归档预演 passed；正式只读准入仍为 archive_requirement_conflict / policy_not_trusted。见 evidence/product/final-admission.json。该阻断对应未执行的正式首次可信转换，不能用隔离批准冒充。
- AI Usage apply hook 成功记录1条可归因运行，warning0；治理计时记录独立标记 usage-unavailable/slow-run，不将墙钟耗时换算模型成本或收益。
- 执行链路复盘：源规格拒绝所有同名修改，而本能力需要有证明的例外；以独立部署引导器承接精确机制转换，避免自证。发现的样本格式、依赖打包、派生字段指纹和焦点问题已在当前 apply 修复。未自动创建 follow-up Issue/Change；后续建议把各入口最小探针纳入发布前检查。

清理完成：本次隔离 API/签名器/MySQL/MinIO 容器和签名卷已移除，Web/附件/骨架测试进程已停止，一次性凭据已删除，脱敏证据保留。opsx.accept 用量 Hook 同样成功，warning0。清理后只读 readiness 仍 ready；需要重新采集时须重建隔离环境，不能把已停止服务写成在线。

## 首次启用产品闭环返修

台账：acceptance-fixes.md；证据：evidence/modify-bootstrap。完成部署、精确清单、独立运维审阅/收据导入、所有者详情/确认、结果和恢复入口。REQ 子文档与原型已一致性扫尾。当前规格副本在隔离真实页面执行，正式项目没有启用或归档。原型旧阶段描述为创建时历史记录；最新视觉与执行事实以本节和验收包为准。

返修完整验收 28/28 通过，run 20261022201403331050-96f89e7c；opsx.modify 与 opsx.accept 已同步，AI Usage hook 为 actual、无 warning。规格临时副本预演通过；正式可信启用仍需独立制品与两类授权，正式归档不在本次执行范围。

## Chat 治理入口位置返修

反馈：原审阅按钮位于 Composer 输入区；现移到项目操作区，并从兼容证明阻断项打开同一抽屉。未改变批准、签署或归档门禁。完整对照、REQ 子文档扫尾及验证见 `acceptance-fixes.md`；已在更新后的正式可登录产品页取得浅色证据，并在恢复的隔离页补齐深浅主题 1440×900/390×844、计算样式及抽屉证据，不沿用旧截图。

本轮验收重跑 24 项通过、4 项因历史隔离视觉服务离线而阻断，0 项失败；证据 `evidence/acceptance/20261022220211759075-1a3bb200/`。正式服务 39002 的真实页面观察不代替隔离视觉前置检查。

隔离 39041/39045 环境已以合成身份与测试信任根恢复；项目入口和同一抽屉的 1440×900/390×844 深浅主题截图、计算样式及关闭焦点证据见 `evidence/modify-bootstrap/entry-isolated-*`。任务 7.3 完成；完整验收 28/28 passed，run `20261022221747288100-4ea3ff82`。正式授权与归档仍由独立门禁决定。

`opsx.accept` 已同步为 passed；归档共享准入返回 `archive_requirement_conflict`（后继写入前兼容证明未通过），Change 保持 active/applied，未归档。

## 最小闭环验收收敛

2026-10-23 根据产品效率反馈，将新版 AC-L01—L12 组织为五类必要结论，复用有效样本；BUG-0063 不存在产品内旧进行中操作，不再要求其产品级旧操作恢复样本。确认、独立验收、写入前复核及破坏性修改拒绝保持不变。返修台账与 REQ 子文档一致性检查见 `acceptance-fixes.md`。当前部分样本与独立签署未齐，Change 仍为 applied/待验收，未归档。
