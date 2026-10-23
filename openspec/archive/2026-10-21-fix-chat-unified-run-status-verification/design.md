---
title: 每轮统一运行状态与核验入口设计
created_at: '2026-10-20 12:58:01'
updated_at: 2026-10-20 22:45:30
---

# 每轮统一运行状态与核验入口设计

## 背景与现状

来源为REQ-0046 v2的FR-001—014、AC-001—026与四项原型AC，已通过REV-REQ-0046-002。BUG-0052的同版真实REQ/BUG首次完成样本通过，原现场存在真实依赖变化而保留保护；这些不同事实不能混成UI成功结论。

## 目标与非目标

每轮一个主状态入口，执行、正文、业务结果、读取状态分开保存；Chat、卡片、详情共享可信事实。仅消费既有恢复和核验能力，不新增后端恢复策略、DB结构、自动发送、解锁或归档能力。

## 设计决策

D1采用局部一致与产品DS复用：移植原型状态区域结构及间距，复用产品token和组件；不整页CSS复制，不将原型控制器、示例卡片或模拟数据打包到产品。

D2以纯状态投影函数输出主状态、辅助说明、完整性警告及可用动作。输入独立包含执行终态、停止请求、业务阶段/证明、正文完整性、读取状态和能力。严格按FR-008六步排序：读取覆盖层；本操作可信完成（矛盾占用则待确认并禁写）；未知/停止中/原失败停止；合法恢复阶段；正常执行及模型结束后的实际业务阶段；正文缺口独立去重。不从自然语言推断成功，output_partial不直接代表截断。普通聊天无业务六阶段。

D3关联键为conversation_id + turn_id +可信operation_id，恢复尝试保留来源及版本。缺operation_id仅展示已知执行事实；不取对象最新candidate补齐。请求响应按身份和版本隔离，切换会话取消订阅/旧确认；迟到响应不能回退新事实。已有完成快照遇读取失败保留并标记更新失败，但旧权限不授权写操作。

D4复用RecoveryOperationPanel的阶段/证据逻辑，迁入TurnActivity触发的轮次详情；ConversationMessages保留全部正文和历史，ExecutionPanel/TrajectoryView按当前轮次定位。完成默认折叠，异常原因和必要动作就地展示，预算/次数/截止时间仅适用恢复详情显示。禁止按正文关键词删除DOM。

D5核验成功使共享操作查询及卡片查询失效重读；不乐观写完成或解除保护。核验失败保留旧事实，仅更新安全原因。处理中按operation去重，版本变化使确认失效；不无限轮询或重复提醒。停止、重试沿用既有授权，不以通用重试替代resume。

## 数据与API边界

消费现有operation详情、allowed_actions、historical_result、admission_state/admission_reason及BUG提供的核验时间、原因、动作、差异字段；实施前核对生成类型并建立显式适配，不臆造字段。核验调用POST /api/v1/chat/governance-operations/{operation_id}/verifications；刷新仅查询。resume使用既有幂等与版本接口，regenerate仅写当前草稿且非空先确认。卡片生命周期与准入分别读取，approved不自动放行。

实施核对发现卡片缺少可核验的操作身份，新增只读 `verification_operation_id` 与 `view_turn_id`；仅在当前用户有权查看原会话时返回，来自原 guard 和 recovery operation 的关联查询，不选择最新候选。已同步 schema、OpenAPI 与 Orval，无新增DB字段。若发现关联字段缺口，先补当前Change契约及任务，再同步后端/OpenAPI/Orval/API文档与契约测试；不得前端猜测关联。数据库、对象存储、执行器和部署机制本REQ不变。BUG负责其迁移与部署证明。服务端权限/版本检查始终有效。

## UI Contract

事实源为已评审需求的业务及权限语义；视觉结构HTML优先于截图与context，最后落到现有token。界面状态顺序：图标/主状态、必要业务说明、工具次数、执行配置、展开；“5 次工具调用”替换“已读”。正文14px/1.5，内容最大1008px含左右24px，窄屏600px以下16px；控件圆角6px，弹窗最大520px、左右至少16px、max-height80vh可滚动。深浅主题均用产品token，状态不可只靠颜色，aria-live仅播报状态变化，按钮支持键盘。

前后台一致性：生命周期不被异常覆盖；历史完成不等于当前准入；原终态保留；失败不声称无正文已保留；无能力不造按钮；敏感差异只显示后端脱敏类别计数。

## UI Skeleton

页面壳与输入区不改。ConversationMessages内每轮容器包含状态触发器、反馈、正文、就地动作、内联详情；详情包含实际阶段、原终态、轨迹、证据与恢复动作。弹窗统一为只读和确认两族。先实现loading/empty/error/disabled骨架并留Mock/API标识，在1440px记录首轮确认后才细化；确认记录不伪造用户签认。

## UI Reference Replication Contract

模式为局部一致，不像素复刻问题截图。原型位于REQ prototype/web/prototype.html和context.md；用户截图用于识别旧面板与“已读”问题，不能凌驾于新需求语义。

| 原型锚点 | 产品测试selector | 组件边界 | 批次 |
|---|---|---|---|
| #current-turn | turn-status-root（data-turn-id） | ConversationMessages | 骨架 |
| #activity | turn-status-trigger | TurnActivity | 状态 |
| #feedback/#body | turn-status-feedback/turn-body | ConversationMessages | 状态 |
| #trace-detail | turn-detail-轮次ID / recovery-panel | RecoveryOperationPanel/ExecutionPanel | 详情 |
| #consistency-card | requirement-operation-status | 需求卡片共享状态适配 | 核验 |
| #action-dialog | operation-action-dialog | 共享动作弹窗族 | 动作 |

以上为计划新增data-testid，尚非产品现有selector；实施时绑定实际文件，不改变消息容器清理边界。

| 动作 | modal类型 | selector | 状态及证据 |
|---|---|---|---|
| 主状态/原执行 | 内联详情 | turn-status-trigger/operation-original-run | 开关、正确轮次、aria-expanded、焦点返回 |
| 证据/差异 | 只读dialog | recovery-evidence/operation-differences | 允许/拒绝/空数据、Esc/内外点击、双视口 |
| 继续剩余步骤 | 确认dialog | operation-resume | 可用/确认/提交/失败/冲突，版本变更失效，无重复应用 |
| 重新生成草稿 | 非空替换确认dialog | operation-regenerate | 空/非空/取消/确认，不发送、不丢取消草稿 |
| 刷新/重新核验 | 无 | recovery-refresh/operation-verify | 查询/提交去重、失败保留事实，不重跑 |
| 停止/重试 | 既有执行详情 | 复用chat-stop-current/chat-retry | 原有能力与权限回归 |

弹窗统一关闭、取消、Esc、焦点恢复；capture阶段识别外部点击，内部点击不关闭；提交中外部点击不隐式取消已提交请求。每个动作族一次性完成组件及状态测试。

## Computed style采样与分批验收

每个样本记录页面、主题、状态、视口、selector、期望、实测、容差和证据路径；当前实测均pending。上述宽度/字号/内边距采用明确CSS值核对，像素测量容差1px；颜色取产品token解析值，换行布局检查不横向溢出。采样font-size/line-height/color/background/padding/gap/width/overflow/border/z-index和dialog焦点。

批次：骨架→状态与正文→详情和动作族→卡片核验联动；每批记录非目标区域回归。1440×900与390×844覆盖完成、失败、未知、截断、拒绝、恢复确认、证据、草稿替换、差异；Chat/卡片/detail/verification-differences组合与BUG AC-010对齐。截图及样式放本Change evidence/，BUG保留可解析引用与指纹，不能用静态原型替代产品观察。

## 冲突处理（Conflict Resolution）

旧恢复spec仅约束局部界面，未要求独立底部面板；本次MODIFIED明确迁入原轮次，保留其全部门禁。原型中的六阶段和演示卡片只代表适用场景，普通聊天不展示；示例颜色以产品token映射，不引入第二套主题。历史助手“应用未确认”原文保留，结构化后续确认独立更新。

## 联合验收与观测

REQ AC-023—026与BUG AC-010/任务3.5共享同操作、同版本、同部署指纹。分别验证正常首次完成、历史可信但依赖变化、证明缺失、权限拒绝、占用未知、读取失败、核验防重复及多轮迟到。BUG已有同版模型证据按输入指纹复用；新样本如涉及模型传输，沿用适用授权边界，不把此前限定两次授权扩大。真实恢复观察与合成回归分别标记。

product_data_collection_observability: applicable

affected_layers: web、api、request_logs、task_traces。
reason: 状态及用户核验操作需要正确关联原轮次，后台核对不得伪造用户事件。
validation: AC-010/012/014/023—026；复用请求封装和trace关联，记录脱敏动作及结果，不记录Prompt、凭证、内部堆栈。DB、存储及新增保留周期为N/A，因本REQ仅消费现有契约。

## 风险与回滚

多轮误绑通过严格身份/版本测试防护；未知能力默认只读；UI回滚可恢复前一版本组件布局，但不得回滚BUG证明事实、关闭权限或修改历史终态。联合验收失败仅阻断对应AC，其他展示任务可继续。无新增发布版本承诺。

## 跨入口一致性返修约定

卡片只呈现一次当前动作的阻塞摘要，历史成果、核验时间、重新核验、差异和原执行收进默认折叠的“状态详情”。运行详情仍归属于原Chat轮次。归档准入采用当前Change的结构化验收证据和明确人工签认，与CLI共用只读判定；进度统计按AC身份去重，自动通过不等于用户人工签认。旧评审历史保留，经过验证的后续合法流转可承接旧保护，真实冲突、未知占用、权限变化、缺失或过期证据仍阻断。覆盖REQ与BUG，不能按具体编号特判。

实现将验收readiness、指纹与证据匹配抽入src/backend/app/governance/acceptance_evidence.py；archive_admission.py供产品与CLI复用，不执行计划命令。review_successor.py核对历史证明、未改变的评审决定和规范、合法Sprint/Change关联及当前完成证据，并CAS提升保护版本，保留原操作身份。后续实质文档变化必须被当前验收输入覆盖。

## 真实归档补证发现

首个 REQ 临时归档样本未执行归档，保留为负例：产品准备入口已允许，但执行器 `_archive_ready` 遗漏 `req_id`，退回治理写权限，归档目录不可写。已复用严格别名解析，同时拒绝冲突别名；新增八种 REQ/BUG 字段别名测试。临时样本缺少交付验证引用也被发现，产品动作准备和 CLI 包装脚本现在均提前执行交付证据校验，避免模型执行后才发现已知缺口。

对于可信命令记录明确证明已结束且零治理写入的归档尝试，后续补齐材料可在当前关联、阶段、交付证据和验收结果重新核验后解除重试保护。保留原轮次终态与零写入记录，以版本比较更新守卫；没有零写入证明、当前证据失效或仍在运行时不解除。此分支不把原失败/未执行样本改写为成功。

真实样本授权：REQ 与 BUG 各一次，首个 REQ 未归档；用户另授权仅一次 REQ 补跑。成功结论等待实际归档、同步、Issue 迁移及守卫核验；模型 completed 不作为成功依据。


## 部署投影根与源码根的一致性补证

最终本地 Docker 看板发现 CLI ready、产品 0/15。实测两个入口读取同一验收 manifest 且附件哈希一致，但治理投影没有 src/ 与 scripts/，20 个源码输入被作为 missing；已配置的 source_root 则具备这些文件。此为证据读取边界错误，不是验收结果失败。

修复只使用既有受信任 source_root 读取 src/、scripts/ 的指纹输入；Issue、规则、验收计划、manifest 和证据附件仍从治理根读取，治理文档缺失或变化不能回退到源码副本。没有执行计划中的代码，不扩大挂载或权限。未配置源码根仍按原根读取，缺失源码、源码变化、治理变化和治理删除均拒绝；同根与双根部署均纳入回归。卡片、归档准备、旧评审承接及零写入重试全部传递同一源码根。

真实模型归档样本使用同根隔离环境；本项双根部署由最终本地产品读取、源码哈希及合成正反例补充验证，不冒称再次运行模型。REQ 主文档/流程/故事/原型既有“当前证据与 CLI 一致”规则不变，本次属于内部证据读取修正，无需追加产品交互；文档差异记录在本台账和设计中。


## 正式入口关联与后续评审补证

最终正式入口发现 REQ 的 trace 使用 related_change，openspec_changes 为空；原解析遗漏该形式，错误退回 Markdown 13/31，而共享当前证据实际为 31/31。统一关联解析支持 related_change、related_changes、openspec_changes 的字符串与 change_id 对象；需求卡片、后续评审承接及零写入重试共用解析。不是手工补某张卡片关联。

原产品评审证明之后，正式 REQ 已追加获授权的补充范围复核，仍为 approved。旧逻辑按字节拒绝全部 review.md 变化，不能承接合法后续复核。现只在验收阶段、原评审和当前评审均 approved 且身份一致、完整当前 review.md 被当前有效验收输入覆盖时承接；未覆盖、证据过期、结论改为 rejected、规则变化及运行中仍拒绝。原操作终态与历史评审证明不改写。相关正反例同时覆盖 REQ/BUG 和四种关联表示。

真实模型归档仍仅为此前授权的两个成功隔离样本；本次收尾以当前回归和正式入口准备/读取补证，不额外调用模型、不归档正式对象。

## 归档预演结果契约补充
预演同时检查进程、失败输出、目录迁移、完整归档内容和增量规格实际效果；退出码 0 不单独证明成功。详见 acceptance-fixes.md。

## 验收输入跨环境契约
可信源码补读范围为 src/scripts/tests；治理文档不跨根回退。目录输入确定性包含成员路径、类型、内容与空目录，拒绝符号链接和特殊文件。最终核验部署后产品发送准入。

## 发送快照竞争处理

命令持久化前，瞬时治理快照竞争最多执行三次完整预检，重新授权并校验当前验收。持续不一致与持续更新分别提示；其他门禁失败不可重试放行。准备成功不等于发送成功，实际 turns 入队及幂等回放为验收证据。

## 归档基线连续证明

共享只读 archive_recovery 判定核对 before/after 全树哈希、唯一已归档目录、完成态、增量效果与不相交的 capability；新记录另绑定 delta 哈希。未知改动、缺边、规格重叠、重复目录、未完成归档、符号链接、错误结果和并发输入变化继续拒绝。显式 reprepare 仅承接 baseline 路径，保留 previous_record 与 baseline_transition；已经合并后的路径只允许 move-only/archived 恢复，不能重置为 merge。产品、CLI、归档终态漂移检测共用事实判定，读取不写 journal 或执行仓库脚本。

## 交付输入与验收输出边界

schema v4 将交付输入指纹与完整复制指纹分开。仅排除 evidence/acceptance/ 生成目录和 trace.md 的正文、updated_at；trace 的身份、状态、首次执行事实、其他未知文件、验收计划、任务、规格和其他证据继续受保护。符号链接即使位于派生目录也拒绝。验收附件完整性和输入有效性继续由验收门禁独立核对。旧记录仅在证明自身尚未合并的显式迁移中更新，保留 previous_record；已合并、并发变化、未知规格漂移不得借迁移绕过。

验收报告发布后返回独立 archive_ready 与完整准入结果；收尾同步和用量完成后再执行 --archive-readiness，共用产品与 CLI 的正式准入。验收 passed 不再单独代表可以归档。错误区分交付输入变化、旧记录过期、身份冲突、规格基线缺证和记录损坏。

执行边界补充：若只读准入证明 merge 基线存在独立归档链，实际归档分类器须在自身合并前刷新 expected_spec_hash，保留历史且通过输入竞争检查；避免把 S+A+B 与旧 S+B 预期比较。move-only/archived 不执行此迁移。

联合归档证据定位：关联 Change 先归档时，原 evidence 引用可按唯一完成的归档身份读取；保持原路径身份与内容哈希，不通过路径迁移豁免证据内容变化或验收输入过期。
