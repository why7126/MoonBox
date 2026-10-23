---
title: 跨入口归档准入与卡片一致性返修台账
created_at: '2026-10-20 15:00:00'
updated_at: 2026-10-20 22:45:30
---

# 跨入口归档准入与卡片一致性返修台账

## 反馈与根因

状态：返修实现、独立回归与真实隔离归档完成，进入最终增量复验；保留首次 applied 和 completed_at。反馈已通过用户截图、当前本地产品页面、只读执行保护样本及代码确认。旧req-review完成证明依赖对象整套文档，合法后续流转触发dependency_conflict；外部核对避让旧保护，通用can_send禁用归档。卡片与CLI另有不同的Markdown勾选解析及自动验收来源，原归档预演仅证明规格合并，不代表产品准入。

## 附件截图逐项视觉对照表

|附件/页面状态|期望|实际/偏差|检查方式与selector|处置与证据|
|---|---|---|---|---|
|用户红框截图；/requirements，浅色验收列|卡片简洁，只留一次当前动作阻塞摘要|requirement-operation-status常驻历史、时间和三按钮；同一警告三处|截图、浏览器AX及OperationVerification源码|修复；用户截图与本轮只读页面观察|
|同页REQ-0046验收进度|结构化AC结果与CLI一致，人工签认独立|9/12而报告30/30，标题式AC未计入|_acceptance_readiness与验收报告|共享验收事实源，禁止按排版漏算|
|卡片动作与详情族|当前归档准入有准确原因，历史只在详情|旧评审阻断所有动作，差异只显示9+2|执行保护只读样本、相关变化浮层|按动作/阶段验证合法承接，保留真实冲突和权限保护|

## 返修契约

两条原Change内完成，不新增权限、DB表或自动模型调用。共享只读验收判定由受信任产品代码提供，CLI复用；不得执行项目提供的Python代码。历史完成证明不可改写，合法后续流转须通过结构化关联、阶段与证据校验；未知占用、真实冲突、缺证据仍拒绝。卡片改为折叠状态详情入口，展开动作族复用证据/差异/原执行；不重复横幅。最终补1440×900与390×844截图及computed style，旧卡片截图不复用签认。

## 联合验证计划

REQ与BUG参数化：产品评审→合法Sprint/Change→CLI apply/accept→产品归档预检；反向入口一致。覆盖旧回调、真实内容冲突、验收过期、失败与权限不足；区分合成全链路、现有真实样本复用与真实产品归档，不将临时预演写作实际归档。未经新授权不增加模型调用，不归档正式REQ/BUG。

## 真实归档补证发现

首个 REQ 临时归档样本未执行归档，保留为负例：产品准备入口已允许，但执行器 `_archive_ready` 遗漏 `req_id`，退回治理写权限，归档目录不可写。已复用严格别名解析，同时拒绝冲突别名；新增八种 REQ/BUG 字段别名测试。临时样本缺少交付验证引用也被发现，产品动作准备和 CLI 包装脚本现在均提前执行交付证据校验，避免模型执行后才发现已知缺口。

对于可信命令记录明确证明已结束且零治理写入的归档尝试，后续补齐材料可在当前关联、阶段、交付证据和验收结果重新核验后解除重试保护。保留原轮次终态与零写入记录，以版本比较更新守卫；没有零写入证明、当前证据失效或仍在运行时不解除。此分支不把原失败/未执行样本改写为成功。

真实样本授权：REQ 与 BUG 各一次，首个 REQ 未归档；用户另授权仅一次 REQ 补跑。成功结论等待实际归档、同步、Issue 迁移及守卫核验；模型 completed 不作为成功依据。


## 本轮实测结果与子文档检查

真实隔离归档：REQ、BUG 均由产品入口接续 CLI 验收，各执行一次成功归档；wrapper 退出码 0、归档目录唯一、Issue 迁入 archive、执行保护 validated/done、原 review.md 保留。首次 REQ 零写入作为负例保留，追加调用只使用用户明确授权的一次。脱敏事实见 [跨入口真实归档证据](evidence/cross-entry-archive-verification.json)。未归档正式对象，未手动修改保护表。

合成回归与真实观察分开：共享准入/执行保护 40 项与 6 子测试通过；准备/证明/重入 29 项通过；需求中心 137 项通过。合成矩阵覆盖 REQ/BUG 的正常承接、过期证据、评审和规则真实变更、运行中、人工未签认以及覆盖/未覆盖的范围变化。最终逐 AC 增量结果以当前 acceptance 报告为准。

REQ 子文档一致性扫尾：requirement.md、business-flow.md、user-stories.md、acceptance.md、prototype/web/context.md 与 prototype.html 均同步共享准入、折叠状态详情、人工签认与当前证据口径；trace 通过工作流同步。capture.md、review.md 为历史捕获/评审事实，无需改写；Chat 原型已有每轮状态与动作族，未修改部分保留既有视觉证据。BUG 的 bug.md、root-cause.md、acceptance.md 已同步，workaround.md 保留原临时规避说明，不作为正式放行手段。

当前截图与样式入口在 REQ Change 的 evidence/modify-card-*，覆盖 1440×900 和 390×844 的折叠、展开及差异弹窗。状态详情默认收起，卡片只保留一次当前阻断提示；相关变化继续在弹窗中查看。设备截图是 Chrome 缩放预览，CSS 尺寸以同名 JSON 为准。

规范优化建议：将“CLI 验收→产品实际归档”作为跨入口验收的常规样本，并在模型启动前验证字段别名与交付记录；本轮已落实相关实现和回归，未自动创建新 Issue/Change。

最终前端验收以同一 9 文件测试命令的输入并集进行去重：所有相关源文件和 REQ 子文档均纳入指纹，不减少验证范围；一次通过的命令结果供同组 AC 共用，逐 AC 视觉及真实样本证据仍独立核验。

最终别名一致性复核：共享判定补齐 related_bug，并拒绝多个来源字段指向不同对象；八种别名均同时验证执行器与共享 CLI 判定。该收尾发生在真实隔离归档之后，真实样本保留当时指纹，最终别名扩展通过合成回归和本地部署验证，不冒称新增模型样本。


## 部署投影根与源码根的一致性补证

最终本地 Docker 看板发现 CLI ready、产品 0/15。实测两个入口读取同一验收 manifest 且附件哈希一致，但治理投影没有 src/ 与 scripts/，20 个源码输入被作为 missing；已配置的 source_root 则具备这些文件。此为证据读取边界错误，不是验收结果失败。

修复只使用既有受信任 source_root 读取 src/、scripts/ 的指纹输入；Issue、规则、验收计划、manifest 和证据附件仍从治理根读取，治理文档缺失或变化不能回退到源码副本。没有执行计划中的代码，不扩大挂载或权限。未配置源码根仍按原根读取，缺失源码、源码变化、治理变化和治理删除均拒绝；同根与双根部署均纳入回归。卡片、归档准备、旧评审承接及零写入重试全部传递同一源码根。

真实模型归档样本使用同根隔离环境；本项双根部署由最终本地产品读取、源码哈希及合成正反例补充验证，不冒称再次运行模型。REQ 主文档/流程/故事/原型既有“当前证据与 CLI 一致”规则不变，本次属于内部证据读取修正，无需追加产品交互；文档差异记录在本台账和设计中。


## 正式入口关联与后续评审补证

最终正式入口发现 REQ 的 trace 使用 related_change，openspec_changes 为空；原解析遗漏该形式，错误退回 Markdown 13/31，而共享当前证据实际为 31/31。统一关联解析支持 related_change、related_changes、openspec_changes 的字符串与 change_id 对象；需求卡片、后续评审承接及零写入重试共用解析。不是手工补某张卡片关联。

原产品评审证明之后，正式 REQ 已追加获授权的补充范围复核，仍为 approved。旧逻辑按字节拒绝全部 review.md 变化，不能承接合法后续复核。现只在验收阶段、原评审和当前评审均 approved 且身份一致、完整当前 review.md 被当前有效验收输入覆盖时承接；未覆盖、证据过期、结论改为 rejected、规则变化及运行中仍拒绝。原操作终态与历史评审证明不改写。相关正反例同时覆盖 REQ/BUG 和四种关联表示。

真实模型归档仍仅为此前授权的两个成功隔离样本；本次收尾以当前回归和正式入口准备/读取补证，不额外调用模型、不归档正式对象。


正式发送前准备补证：逐文件比较确认治理投影与源码事实源一致。随后准备入口暴露另一处仅识别 openspec_changes 对象列表的旧分支；现发送前阶段检查、验收与交付检查、归档执行器权限判定、归档完成证明均复用同一关联解析。回归由直接保护检查扩展到实际 _preflight_object_session 与执行器 _archive_ready，REQ/BUG × 四种关联表示全部覆盖；不通过修改正式对象的关联字段绕开问题。


## 本轮返修最终结论

当前逐项验收 31/31 通过，readiness ready、归档预演 passed、Issue 准入门禁通过。报告：[最终验收](evidence/acceptance/20261020174447645231-8323c712/summary.md)。正式产品准备请求与看板读取均允许归档：REQ 31/31、BUG 15/15，均无阻断原因；REQ 原保护经正常核对为 validated，原操作与终态保留，无手工数据库解除。见 [正式入口核对](evidence/final-formal-admission.json)。

最终前端 9 文件、213 项通过；跨入口矩阵 93 项通过，覆盖 REQ/BUG、四种关联表示、准备/执行器/保护、当前证据与真实冲突。最终本地后端、治理控制器、Chat 工作进程九个关键模块与工作区哈希一致；四个有健康检查的服务 healthy，Web running 且真实页面核对通过。部署证据见 evidence/modify-local-deployment.json。

实际最终页面截图及可用按钮证据在关联 REQ Change 的 evidence/modify-final-req-ready.png/json、modify-final-bug-ready.png/json；REQ 状态详情默认折叠，无重复异常提示，归档动作可用。1440 与 390 的布局/交互/样式证据沿用本轮 modify-card-*；最终状态截图为实际 1633×774 视口，未混称为双视口新采样。

此前授权的真实隔离 REQ/BUG 归档均成功，首次 REQ 零写入负例保留。随后关联解析与事实根修正由当前回归、正式准备及真实页面补证，没有追加模型调用，不宣称在最终版本重跑真实模型归档。正式 Issue/Change 仍在验收阶段，未归档、未提交 Git；Sprint 未因此自动关闭。用量 Hook 返回 unavailable，不能提供可归属 token 数。

执行链路复盘：两条链路保留 applied 和首次 completed_at，opsx.modify→opsx.accept 同步完成。中间输入变化、发送前别名遗漏、同步期 409 与 SQLite 锁等待均保留诊断；最终事实源逐文件一致，串行准备成功。建议持续保留跨入口准入矩阵与“CLI 验收→产品准备→隔离归档”分层门禁；本轮已补齐对应回归，不自动新增 Issue。

## 归档预演零退出码误判返修

根因 confirmed：OpenSpec 在不存在的 MODIFIED 标题时输出 Aborted，却返回 0；旧预演只看退出码，错误返回未变的规格哈希。两条链路均将新增的“跨入口当前动作一致性”误放在 MODIFIED。此前“预演 passed”仅为旧脚本返回值，现明确撤销其可归档证明效力，历史失败与产品样本保留。

入口矩阵：delta 分类 → 预演 expected_spec_hash → archive-change.sh 恢复日志 → 实际 OpenSpec 临时归档。修正新增分类，检查失败输出、active 消失、唯一归档、归档内容完整及 ADDED/MODIFIED/REMOVED 的实际规格效果；增加零退出码失败与旧日志安全重建正反例。

附件对照：用户截图中正文为 MODIFIED not found/尚未归档，预期失败应拦截；以临时 CLI 复现确认，归档脚本修复。顶部“已完成”属于另一项轮次展示疑点，本次不改 UI，不以本次脚本测试签认该显示正确。截图仅为故障证据，布局、样式及原型无需改变。

受影响范围：共享归档预演及两份 delta，新建聚焦 AC 核验脚本与实际临时归档；未变的产品实现、视觉和已授权隔离轮次按指纹复用，不新增模型调用，不自动归档正式对象。失败日志只在正式规格仍为原 baseline、active 唯一且新预演成功时显式 --reprepare，旧记录完整保留；规格已变化则阻断。

REQ 子文档一致性扫尾检查：requirement、business-flow、user-stories、acceptance、trace、prototype/web/context.md 与 prototype.html 的产品行为和原验收条件未改变，无需改写；本次补充的是验证实现与规格操作分类，记录在 Change 台账、设计和新验收检查。BUG 原根因为完成证明/保护不收敛仍成立，本次为归档验收补充根因，不替换旧证据。

API/DB/Web/管理端/客户端/Orval/Docker Compose 无变更；product_data_collection_observability: N/A；affected_layers: []；不新增产品采集，只改治理校验。产品浏览器/视觉复验 N/A，原相关输入未变。

本轮验证：46 项聚焦测试通过；真实 CLI 临时副本两种归档顺序均通过（evidence/archive-preview-joint.json）。完整验收 passed，运行 20261020182810727116-1a7870a0；统计 {"command_executions": 3, "deduplicated": 29, "reused": 1, "preflight_ms": 565, "duration_ms": 76757, "blocked": 0, "failed": 0}。实际报告：evidence/acceptance/20261020182810727116-1a7870a0/summary.md。无正式归档、无新增模型调用。

## 验收输入跨环境一致性返修

根因 confirmed：产品治理投影只从可信源码补读 src/scripts，新增 tests/unit 输入在产品侧变为 missing，而 CLI 完整工作区可读，阻断 AC-ARCHIVE-PREVIEW-REGRESSION。隔离只读诊断补读 tests 后两条链路均 ready。另有目录输入被当作 missing，遗漏规格内容及成员变化。

修复：仅扩展既有可信源码白名单到 tests；治理文档仍从当前投影读取，不回退其他工作区。目录采用 directory-v1 确定性成员名、类型与内容哈希，涵盖空目录、增删与重命名；拒绝内部/外部符号链接及特殊文件。原单文件指纹兼容不变，既有目录证据按新算法失效后重验。

入口矩阵：完整工作区 CLI → 分离投影共享读取器 → 部署后端 → 对象会话准备/发送预检 → 浏览器。必须核验实际产品准入，不能用 CLI ready 替代。新增 AC-INPUT-PROJECTION 覆盖正向/陈旧测试/治理文件缺失/越界/目录变更。部署后版本哈希与准入证据另存 evidence/input-projection-product.json。

附件对照：截图消息框报“验收证据缺失、过期或未全部通过”，期望有效当前验收允许发送；偏差来自后端输入读取，不是视觉布局。检查方式为部署后真实准备接口与页面状态；本轮不改前端，不触发模型消息或正式归档。

REQ 子文档一致性扫尾检查：requirement、business-flow、user-stories、acceptance、trace、prototype/web/context.md 与 prototype.html 产品行为和验收目标不变，无需重写；修复跨环境验证实现并在此回填证据。BUG 原根因保留，本次补充验收读取缺陷。

API/DB/Web/客户端/管理端/Orval 无契约变化；部署需更新后端、controller、worker 中共享读取器。product_data_collection_observability: N/A；affected_layers: []；不增加数据采集或事件字段，仅脱敏诊断。

验收读取修复完整清单：passed，运行 20261020184255924101-94846458，34 项。部署后真实后端代码哈希匹配，分离投影 readiness=ready。历史产品轮次从原隔离数据库重新核对，不追加模型调用。产品准备与界面结果见 evidence/input-projection-product.json。

部署后入口核验完成：CLI 与部署态均 ready；真实部署服务对象准备 can_send=true、idle、无 reason_code；浏览器从完成/归档进入命令草稿，发送按钮启用。BUG 在项目尚未加载及并发文档写入时的失败保留为诊断，稳定重试成功；未发送模型消息或正式归档。用量 hook unavailable，不估算 Token。

## 发送阶段快照竞争返修

偏差：准备接口 200、按钮可点，但实际发送 POST turns 在 19:00:03 返回 409。REQ 提示事实源不一致，BUG 提示治理文件已变化。前一轮仅核验准备入口的结论不覆盖发送成功。

附件逐项对照：两张 Chat 浅色截图，归档草稿和发送按钮存在；期望发送通过所有门禁后入队，实际为红色快照错误。浏览器 DOM 与后台 409 日志相互印证；属于发送行为/文案偏差，布局和 computed style 无变更，不进行视觉重制。

原因：源目录与投影顺序采样、预检与发送基线分次采样；整仓治理更新会造成瞬时版本不一致。同期其他 BUG 文档更新为强关联证据，缺少当时逐文件差异，不能确认具体冲突文件。

修复策略：在任何命令记录持久化前最多三次完整读取预检；每次重新授权、检查验收及写入保护。只重试明确的版本竞争/manifest mismatch，验收失效和权限等错误立即返回。对投影前进进行一次回读确认。最终区分持续内容不一致与持续并发修改，附 reason/phase/attempts，保持原错误码及响应结构。入队仍执行执行保护检查，幂等请求不重复创建轮次。

验证边界：新增实际 POST turns 并发回归，REQ/BUG 归档均验证 queued 与同请求回放；部署验证应到真实 HTTP 入队与持久化记录，不以准备/按钮代替，不以入队冒充模型归档完成。

product_data_collection_observability: applicable；affected_layers: api；使用既有错误 details、请求日志与 trace，无新采集字段/DB schema；验证直接 API 的返回码、入队与拒绝，禁止输出凭证。前端/客户端 schema、DB、对象存储无变更，需部署后端/controller/worker。REQ 子文档与原型保留统一状态和核验目标，仅补充发送验收边界；布局无变更。

本轮发送证据：evidence/send-snapshot-http.json。128 项核心回归通过；扩大检查 201 通过、4 个旧样本失败，恢复本轮前逻辑后相同失败仍在（验收来源/恢复心跳样本缺口）。独立部署正常登录、真实 HTTP turns 两条命令均 200 queued，幂等回放同轮次，数据库各 1 条；正常中断释放测试额度，0 次模型调用。此证据不代表模型归档终态。Docker Backend 被另一轮部署替换成旧发送逻辑的版本差异已发现并重新统一部署，最终哈希核验另记。

### 附件截图逐项视觉对照表

| 附件 | 页面/状态 | 对照对象与期望 | 实际与偏差 | 检查方式 | 处置/证据 |
| --- | --- | --- | --- | --- | --- |
| REQ 报错图 | /chat，浅色，归档草稿；附件 2122×1116 像素 | #chat-prompt 与发送反馈；有效输入通过门禁入队 | 红色“治理目录与源工作区内容不一致” | 已有浏览器 DOM、19:00:03 POST turns 409、源码快照分支 | 修复发送竞争；布局、字号、间距无修改，computed style 不适用；send-snapshot-http.json |
| BUG 报错图 | /chat，浅色，归档草稿；附件 2124×562 像素 | 同一发送动作；短暂更新后重新检查 | 红色“治理文件已变化，请重试” | 已有浏览器 DOM、19:00:03 POST turns 409、预检/基线比较 | 有界重试及分类提示；纯后端行为修复，不重制 UI；send-snapshot-http.json |

REQ 子文档一致性扫尾：acceptance.md 已补实际发送验收；requirement.md、business-flow.md、user-stories.md 与 prototype/web/context.md、prototype.html 无需更新，统一状态/动作设计及服务端错误展示机制不变；trace 由 Workflow Sync 维护。此次 API details 扩展使用既有字典结构，无 OpenAPI/Orval schema 或数据库迁移；部署和错误码说明已同步，历史视觉证据不作为本次实际发送证明。

本轮追加授权的真实完整链路验收已完成：REQ、BUG 各一次，使用正常 HTTP 登录、object-sessions 与 turns 接口，串行调用当前配置模型。两轮均 completed，归档 wrapper 退出码 0，唯一归档目录存在、active Change 消失、Issue 已迁移；通过正常需求中心读取核验保护解除为 done 阶段（REQ idle，BUG validated）。未手改保护，未归档正式对象。证据：evidence/send-snapshot-real-chain.json。隔离服务已停止；此前仅入队证据继续保留，不混称真实模型验收。

最终增量复验：REQ 35 项、BUG 19 项均通过，复用未变化证据；部署三个服务 preparation 哈希一致。归档边界另记：REQ 历史 archive-recovery journal 的正式规格 baseline 已因其他链路归档而变化，--reprepare 正确拒绝（reprepare rejects changed formal specs）；未删除、篡改或重置该记录。因此验收 ready 不等同于该历史归档恢复门禁已解除，正式归档仍需核对恢复基线。

## 历史归档恢复基线衔接返修

期望：其他链路合法归档后，当前 REQ/BUG 的产品与 CLI 按同一恢复证据判定准入，不删除旧记录、不重复合并自身规格。实际：旧 journal 只比较全树哈希，--reprepare 拒绝 changed formal specs；产品先前只检查验收 ready，无法提前显示这一恢复阻断。

根因已确认：旧基线 5c99c51de4df 到当前规格之间存在 fix-deployed-acceptance-input-resolution、fix-change-card-blocked-reason、fix-archive-usage-attribution、optimize-governance-feedback-loop 四条连续完成的归档边，且规格范围与本链路不相交。旧算法未消费这些证据。原记录与归档文件均保留。

实现：共享只读 archive_recovery 判定核对 before/after 全树哈希、唯一已归档目录、完成态、增量效果与不相交的 capability；新记录另绑定 delta 哈希。未知改动、缺边、规格重叠、重复目录、未完成归档、符号链接、错误结果和并发输入变化继续拒绝。显式 reprepare 仅承接 baseline 路径，保留 previous_record 与 baseline_transition；已经合并后的路径只允许 move-only/archived 恢复，不能重置为 merge。产品、CLI、归档终态漂移检测共用事实判定，读取不写 journal 或执行仓库脚本。

验证：新增 tests/unit/test_archive_baseline_transition.py，覆盖 REQ/BUG、历史记录、两跳归档、失败现场保持、已合并/已移动恢复，以及真实 OpenSpec 隔离归档。完整入口最终核验包含部署后的对象准备接口、发送使用的同一预检与 CLI 准入；正式对象不提交模型、不执行正式归档。本轮无新增模型调用。

product_data_collection_observability: applicable；affected_layers: api/governance；沿用既有 2604 与错误文本、请求审计，无新采集字段/DB/客户端 schema。UI 布局和核验动作族不变，未使用旧视觉证据冒充本轮后端准入验证。REQ 子文档一致性：需求、流程、故事和原型保留统一准入与历史证据目标，无新布局或动作；acceptance 增补本次边界，trace 记录证据，生命周期继续由 Workflow Sync 维护。

边界补证：独立归档之间可顺序修改同一外部 capability，按连续路径合成最终 Requirement 效果再核验，避免把已被后续合法覆盖的中间正文误判为篡改；与当前 Change 的范围重叠仍一律拒绝。新增专门回归通过。

正式现场兼容：canonical archive 的 trace 保留首次 applied/execution.completed_at，不要求改写成 archived。连续证明接受唯一归档目录中的已完成 apply 与全勾选任务，同时校验身份、规格哈希和增量；缺执行完成事实、待办任务和身份不符仍拒绝。真实 CLI 回归也保留 applied 元数据，避免仅用合成 archived 标志代替项目约定。

本轮最终结论：REQ 36 项、BUG 20 项当前验收通过；21 项基线专项和 94 项跨入口套件通过。部署后正式 REQ/BUG 两者 CLI ready、产品归档准备 HTTP 200/can_send=true、实际发送使用的部署预检通过且没有新增 turn；恢复前 REQ 两入口一致拒绝，衔接后同时放行。完整证据：evidence/archive-baseline-admission.json。三个服务模块哈希匹配且 healthy。正式对象未归档，模型调用 0。Workflow Sync 无阻塞；BUG root-cause 的 status=confirmed 是已声明根因语义，保留该既有提示，不将其改为生命周期状态。文档与证据收尾后再按同一门禁刷新活动内容哈希并只读复核，保留四条历史衔接证据。

## 再次验收导致恢复记录自失效返修

已确认：旧记录全目录指纹包含 evidence/acceptance 新报告和 trace 运行正文；22:23 再次验收后，正式规格与增量规格仍一致，但发送被误判为规格基线变化。附件 57791cb0：Chat 亮色输入框，期望验收后能按统一门禁发送；实际提示规格不一致。检查方式为截图文案、目录指纹、共享准入与实际发送接口。处置为后端恢复投影及错误分类修复，无布局、按钮或 modal 变化。

实现契约：schema v4 将交付输入指纹与完整复制指纹分开。仅排除 evidence/acceptance/ 生成目录和 trace.md 的正文、updated_at；trace 的身份、状态、首次执行事实、其他未知文件、验收计划、任务、规格和其他证据继续受保护。符号链接即使位于派生目录也拒绝。验收附件完整性和输入有效性继续由验收门禁独立核对。旧记录仅在证明自身尚未合并的显式迁移中更新，保留 previous_record；已合并、并发变化、未知规格漂移不得借迁移绕过。

验收报告发布后返回独立 archive_ready 与完整准入结果；收尾同步和用量完成后再执行 --archive-readiness，共用产品与 CLI 的正式准入。验收 passed 不再单独代表可以归档。错误区分交付输入变化、旧记录过期、身份冲突、规格基线缺证和记录损坏。

验证计划：先创建恢复记录，再重复执行验收、追加运行 trace，检查产品实际 POST turns 入队及 CLI 真实归档；REQ、BUG 两个授权隔离模型样本串行运行至归档终态，正式对象不归档。保留其他归档改变基线、实质输入变化、证据篡改和并发发送的负例。结果待本轮补齐。

product_data_collection_observability: applicable；affected_layers: governance/api；沿用请求日志与轮次事件，证据只保留状态、ID、退出码和效果，不记录密钥或原始消息。无 DB schema、权限边界或客户端类型变更。

REQ 子文档一致性扫尾：需同步归档准入说明与验收条件；原型布局、动作族和样式不变，不重用旧图片冒充本轮运行证据。

完整 CLI 顺序预演补充：首次双样本在第二条链路合并后发现旧 expected_spec_hash 未随已证明的独立归档衔接，失败副本保留。执行端在 merge 模式且存在完整不相交归档链时，先通过真实预演更新预期结果并保留 previous_record；产品读取不迁移记录，move-only 不重新合并。回归覆盖两条链路先建记录、先后真实归档至终态。

运行证据：evidence/reaccept-archive-real-chain.json。REQ/BUG 两个授权模型轮次均 completed，同轮归档 wrapper 退出 0，各有唯一归档、Issue 迁入 archive、保护经正常产品读取收敛至 done。另两个 CLI 副本完整 finalize 退出 0。正式对象未归档。核心最终34项与实际发送101项回归覆盖本次门禁；模型样本后仅补充非法 YAML 拒绝分支，正常样本依照受影响范围复用，最终产品/CLI准入和验收结果另由 trace 链接生成报告。REQ 子文档已同步需求、流程、故事、验收和原型 context；prototype.html 的布局、动作与样式无需修改，因为本轮只改变后端准入与错误来源。

正式材料交叉证据补充：两条链路引用彼此的活动 evidence 路径；任一先归档会导致另一条原证据路径失效。共享证据解析仅在源活动 Change 不存在、唯一同身份归档且有完成事实时定位原文件，继续核对原清单 SHA-256；有活动目录、重复归档、未完成、篡改和符号链接不获豁免。验收复用、重新采集与归档证据校验共用解析。最终顺序回归使用完整正式材料副本，不只最小样本。实现输入变化后重新建立本轮起点，再次验收和收尾期间不重建记录。

预演输入精确化：规格合并 AC 仅绑定本 Change 增量涉及的正式 capability 目录，避免另一条不相交归档令该 AC 无效；共享归档恢复仍核对完整规格基线、连续归档证明和真实合并预演，未放宽未知规格写入保护。完整正式材料副本验证先后归档及证据哈希保持。

完整材料副本确认关联验收附件还包括 verification.md；路径迁移解析覆盖清单明确声明的 Change 内附件，而不局限 evidence 子目录。唯一完成身份、归档目录边界和原内容哈希均保留，未更改原证据清单。实际 HTTP 成功用例同时覆盖这一类文档附件。
