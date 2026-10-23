---
created_at: '2026-10-22'
title: 同条文兼容追加实施验证记录
updated_at: '2026-10-23 21:07:37'
---

# 同条文兼容追加实施验证记录

## 首次交付批次（历史记录）

UI 骨架已获用户确认；正式 Composer 分项诊断已接入，已完成1440/390视觉与样式核对。

- 原动作签认及后继/跨入口回归：177 项通过。
- Chat 诊断过滤与 Sprint 关联回归：22 项通过。
- Composer 拒绝后保留命令、附件和 Skill，以及预填回归：4 项通过。
- TypeScript 与 Vite 构建通过；原有大 bundle 提示仍在。
- 最终核心101项、关联177项、后端诊断22项通过；前端4项通过。

## 现场只读验证

已逐条复核 BUG-0060 → BUG-0061 三项新增场景，独立证明记录绑定原文、新文、旧验收和审查/回归附件；原历史文件未改写。共享 recovery_admission 对 BUG-0060 返回 ready。Sprint 预检确认四个既有 archived Change 均无 deep blocker。

sprint-012 尚未关闭：本 Change 已完成实施和验收，尚未归档；本 Change 原正文替代触及 BUG-0062 新门禁；人工 sign-off 与五处旧路径属于独立条件。未执行正式归档或签署。

## 入口与证据矩阵

|入口|事实源与版本|正向/拒绝|探针与 AC|状态|
|---|---|---|---|---|
|共享恢复与 CLI|journal、delta、独立兼容证明|兼容/破坏/断链/并发|三组归档回归，AC-001—010|定向通过|
|产品与 Workflow Sync|共享 recovery_admission、有效 AC 投影|当前态与恢复状态独立|跨入口177项，AC-010/013/014|合成通过|
|Chat 发送|可选 archive_blockers|分项诊断与保留草稿|后端22项、前端4项，AC-011/012|定向通过|
|新部署 UI|当前源码与新镜像|1440/390展开诊断|AC-015|已采集|
|Sprint 最终预检|正式只读 sprint-012|原三项误阻断已消除，其余保留|AC-018|预检仍 blocked，符合当前事实|

product_data_collection_observability: applicable；affected_layers: API 错误诊断、Web 请求错误处理、归档恢复与工作流准入；validation: 安全字段过滤、跨入口测试及真实产品观察。数据库、对象存储 schema 与权限没有新增；不记录原始 Prompt、凭证或私有路径。

## 真实隔离 UI 观察

无有效证明时真实发送返回两项阻断，包含「能力」条文；恢复兼容证明后再发，仅保留未签署阻断。三次拒绝未创建轮次，未调用模型，命令草稿一直保留。1440×900 与390×844已核对：分项清晰、步骤可展开、文本换行，document scrollWidth 与视口宽度相等。窄屏自动收起侧栏，沿用原 Composer 滚动和按钮布局。截图与样式入口：evidence/product/。此为真实 API/浏览器上的隔离合成业务数据，不替代正向完整归档轮次；附件/Skill保留已补齐真实上传与拒绝观察，见AC-012。

## 稳定增量复验

核心24项与条文范围24项通过；OpenSpec PATH补齐后基线52项全部通过（缺CLI那次环境失败单独保留，不作产品失败）。此前299项聚焦组合通过，前端4项及构建通过。最终backend/worker/controller六个关键文件哈希与源码完全一致，健康检查通过，版本证据见 evidence/product/deployment-versions.json。

隔离真实OpenSpec CLI验证：缺证明在写入前拒绝且目录哈希未变；完整证明通过候选预检、实际合并与迁移，唯一archive及增量效果核验通过，见 ac-009.json。测试夹具Purpose与路径修正后执行，没有修改正式spec。

真实产品首轮已完成但未关闭：模型发现测试样本缺发布说明、签署含义不清并保留阻断；后续独立完整样本已通过，详见下一节。附件选择工具限制通过产品粘贴入口完成真实验证。

## 产品允许路径与恢复保护

完整预检的独立sprint-100真实轮次875f7258-04e0-4edb-9e43-c2f2e1759ec5已completed，标准sprint.archive同步退出0，迭代已迁移且status=completed，执行保护validated。两项Change均已归档，新增归档0、重复合并0。连续两次只读证明核验后规格和归档树哈希未变。前置sprint-099两轮独立文档门禁失败仍保持needs_review/direct_sync_missing，未手工清除保护；不把新样本当作旧轮次恢复成功。

允许与拒绝均为真实浏览器/API/模型执行，业务对象为一次性合成样本。证据见ac-014.json、ac-015.json和positive-sprint-closed.png。正式sprint-012没有关闭或签署。附件首个上传因隔离对象存储缺失失败，已配置独立临时MinIO；最终真实上传成功后的附件保留已通过验证。

## 首次交付自验（历史记录）

完整验收入口18/18通过，0失败、0受阻；最新运行20261022110420517973-a2b9e82d复用15项证据，执行1组命令及产品轮次核对。最后的真实附件通过产品粘贴入口上传至独立临时MinIO；未签署拒绝后命令、图片、Skill仍在，0新轮次。浏览器扩展选择文件失败与最初存储缺失均作为环境失败保留，不计通过。恢复进程后3轮次保持不变，兼容证明仍ready，没有重放模型。正式API、worker、controller哈希匹配当前源文件。

自身归档边界仍按用户决定保留：对BUG-0062的「归档连续证明的条文冲突范围」是显式替代，候选保护预检仍拒绝；功能AC通过不等于归档ready，未使用白名单或改写原约束。

最终收尾：opsx.apply 与 opsx.accept 状态同步通过；完整验收运行20261022110917925182-27460447复用18/18项有效证据，readiness为ready，临时副本归档预演通过。最终正式准入仍为archive_requirement_conflict（后继写入前兼容证明未通过），符合显式替代保留阻断的决定。


## 当前版本重复 apply 复验（2026-10-22 晚间）

共享实现经过 REQ-0050 演进，首次交付的 18 项输入指纹已失效。本次未修改业务源码，重新执行当前版本命令回归、真实产品观察与完整验收入口，保留原 implementation completed_at。

- 真实拒绝路径：隔离 sprint-099 缺兼容证明时两项阻断；恢复原证明后仅剩独立签署阻断。命令草稿保留，未创建模型轮次。1440×900 与390×844诊断展开、换行和 computed style 已复核，见 evidence/reapply/negative-observation.json、blockers/signoff 截图与 styles 文件。
- 附件观察沿用原真实上传证据，当前前端回归再次核对保留逻辑；本批没有重新上传附件，不冒充新的上传观察。
- 隔离真实 CLI：缺证明时写入前拒绝；完整兼容证明下合并、唯一归档和增量效果通过，见 evidence/reapply/cli-archive.json。
- 首个当前版本样本 sprint-101 已同步和迁移，但额外一致性检查失败且 worker 出现 OperationalError，后续宿主同步修复派生 note。该轮不计完整成功，见 interrupted-sample.json；未确认运行中断的根因。
- 用户明确授权仅把隔离环境月额度由300万提高到400万，并最多再运行一轮。sprint-102 的唯一真实轮次 140f162e-06ad-4b90-9f9f-8c0c6c0cfef6 已 completed、无错误，标准 sprint.archive 写同步退出0，执行保护 validated/done，页面显示“成果已核验”。活动目录消失且归档目录唯一；规格与既有 Change 归档树哈希均未变化，未重复合并。见 positive-observation.json 与 positive-1440/390.png。
- 用量单独报告：最终隔离轮次权威预留台账已结算538660 Token；页面展示360510，与台账口径不同，不以页面值代替结算。首轮100万未知用量预留原样保留。正式服务额度不变，见 usage-boundary.json。
- 本次部署文件一致性见 evidence/reapply/deployment.json。无新增 API、数据库、UI实现、部署配置、安全规则或客户端生成变更；证据与文档同步不扩大独立授权边界。

正式 sprint-012 及 BUG-0063 未归档；显式替代证明、可信启用、人工签署与旧引用检查仍独立执行，功能验收通过不解除这些条件。

当前完整验收运行 `20261022212413802824-ada289f5`：18/18通过，5组命令、11项去重，0复用、0失败、0阻塞；正式准入仍为 archive_requirement_conflict，原因“后继写入前兼容证明未通过”。

收尾复核：opsx.apply、opsx.accept 同步均退出0；证据readiness为ready且无stale，临时副本归档预演通过。正式sprint-012仍有本Change显式替代门禁及5处归档前路径残留（REQ-0049三处、BUG-0060两处），见formal-sprint-readonly.json；未改写既有归档材料。Apply用量Hook为estimated_fallback并有1项warning，Accept Hook为actual且无warning，两者不与隔离产品轮次Token混算。


## 历史引用修复后的当前准入（2026-10-22）

已将归档 REQ-0049 三份子文档的验收证据目录、归档 BUG-0060 两份文档的具体验收报告从旧 active Change 路径改为对应 archive 路径，并逐项核对目标存在。`validate-sprint-archive-readiness.py --sprint sprint-012 --json` 的路径残留阻断从5降至0；完整验收证据仍为ready且无stale。当前剩余唯一深层阻断为本Change的 `archive_requirement_conflict`（后继写入前兼容证明未通过）；不据此归档或放宽证明。见 evidence/reapply/formal-sprint-after-reference-fix.json。上方旧预检记录保留为修复前事实。

## 2026-10-23 验收反馈调整（当前策略）

取消后继写入前兼容证明硬性限制：产品预检、CLI 和归档执行不再要求独立兼容或规则替代证明；已完成后继仍核验正常验收、唯一身份、连续归档哈希链、交付增量、最终规格效果和并发变化。历史 journal、manifest 与证明保留，不自动归档或代替独立签署。

本节取代前文将兼容证明作为硬门禁的描述；证明工具保留为可选审查工具。

## 隔离页面歧义消除与真实产品补证

2026-10-23：新数据库没有已确认历史阶段时，外部结果未核验产生 unknown，原投影覆盖了 Change 的验收中事实。reader 仅在 confirmed_stage 已知时覆盖；结果未核验和动作阻断保留。32项相关回归通过。目标卡片1440px证据见 evidence/proof-optional/card-1440.png，确认位于验收中且无旧兼容证明阻断。

独立容器使用当前后端源码与当前前端构建，浏览器发送 /sprint-archive sprint-103，随后点击核验当前成果，显示成果已核验。轮次 14a64cb2-3319-4ca6-b163-e04c6615bcb2 completed、无错误，唯一持久归档操作 completed，guard recovered_valid（产品核验后），规格和既有归档树哈希不变。1440×900、390×844截图与样式、脱敏回读见 evidence/proof-optional/。旧真实轮次不再承担新版验收依据。

边界：样本使用一次性测试签署及完整复制的历史 Change，仅证明真实 Sprint 关闭、同步与成果核验；同条文后继取消独立证明由当前回归和真实临时 CLI 归档验证。Chat 仍保留“未收到最终答复”的输出分类提示，和明确的“成果已核验”业务结论分别记录，本轮未改动消息分类。正式环境、正式 Sprint 和历史归档未执行写入。

product_data_collection_observability: applicable；affected_layers: governance_reader、product_turn_evidence；validation: 同轮身份、持久操作、guard 与受保护树交叉核对。N/A：无 API schema、DB 迁移、客户端生成、采集字段或对象存储变化；部署仅新增一次性验证实例。
