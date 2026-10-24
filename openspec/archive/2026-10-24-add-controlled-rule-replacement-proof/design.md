---
title: 受控规则替代证明设计
created_at: '2026-10-22 13:23:26'
updated_at: '2026-10-23 08:25:00'
---

# 受控规则替代证明设计

2026-10-24 验收策略收敛：现行方案的权限、逐项证据、历史完整性、破坏性修改拒绝和写入前并发保护保持不变。真实产品观察聚焦一条成功归档、一条破坏性修改拒绝、一条预检后变化拒绝、一条页面处理链及同身份恢复；其余同类变化用针对性自动化回归覆盖。自动化结果不得冒充产品轮次，关键样本或回归缺失仍阻断归档。

## 2026-10-23 轻量方案覆盖设计

2026-10-24 v7 入口收尾：后继验收绑定失败仍拒绝归档，但返回受影响条文诊断。只有当前**未归档** Change 且规则详情可安全读取时，Chat 归档预检给出“查看修改”上下文动作；Sprint 对已归档 Change 的历史冲突保留历史核验提示，不打开仅支持活动 Change 的详情。该分流不改变验收、权限、完整链和并发门禁，错误消息仅含有界对象身份和通用处理建议。

2026-10-24 补充：`ChangeIndex.acceptance_source_reason` 优先校验显式证据引用；有结构化验收计划时直接核验当前完整证据，不再另查交付验证 Markdown。计划存在但无效或未就绪时闭锁，Markdown 不能覆盖；没有计划的历史 Change 保留原验证记录核对。归档预检、规则查看和无写入恢复使用相同判断及项目来源路径。

本节及新版 `proposal.md`、规格、REQ AC-L01—L12 是当前实施目标；下文 D1—D6 和原 UI Contract 是旧实现的历史设计，不再指导新开发。2026-10-23 第三次复评进一步移除规则修改的额外产品确认。改动顺序为：在工作区撤去旧确认按钮及新写入口，保留旧记录只读验证；不再发行新版规则修改证明；归档权限、逐项验收证据仍由共用门禁判断，不新增人员签署。未完成新版前，当前服务仍维持原门禁且不部署中间代码。

不另设规则批准权；沿用现有归档权限，拒绝 Agent 或仓库自填文本冒充验收证据。差异展示绑定项目、对象、原新规则及当前验收状态；变化后重新读取。旧版已完成边仍按原证明版本验证；若存在未完成的旧产品操作，必须先回读，不可自动转换。是否允许归档以 BUG-0063 已生效的正常验收、完整历史、当前权限和写入前复核为准；差异展示不以标题相同或自然语言相似推断许可。归档前复核与中断恢复复用原围栏和检查点。页面只在相关对象阻断项出现“查看修改”，抽屉用产品语言展示差异和验收；正式实现复用 Chat 壳和主题，按新版 `prototype/web/context.md` 核对受影响的 1440/390、深浅主题和样式。

验收以五个必要结论组织同一批证据，AC-L01—L12 保留追溯编号。BUG-0063 已归档；其早期 Codex 会话不是产品内旧进行中操作；本版对旧流程只核对已完成记录可读、旧写入入口被拒绝、现有恢复回归未退化。只有发现真实旧操作时才执行产品级续接验收。当前版本逐项测试结论和可核对证据仍是门禁；测试账号与自动化可以执行测试，但不能伪造通过结果。旧确认接口只拒绝新写入，不删除既有表、事件或已完成证明。

API、数据库和部署的旧专属写入口在新实现切换时退场，历史读取能力保留；不得删除已有数据库表、归档边或客户历史。新版规则修改接口为只读差异和检查状态；旧确认写入口返回明确拒绝。不新增规则修改证明版本；旧版证明仍按原格式只读验证。SQLite/MySQL、OpenAPI/Orval、权限、并发和恢复均须回归。观测只记录脱敏查看、请求及归档步骤，不以遥测代替权限或验收证据。

## 背景与现状

需求事实源为REQ-0050的PRD第10节、20项功能/4项横切/4项原型AC，已评审并纳入sprint-013。现有compatible_successor.verify只允许原正文/原场景保持；archive_recovery逐边核验后继链；archive-recovery-guard在写入前预检。现有项目可写角色不等于新批准权。

## 目标与非目标

目标：独立可信授权的精确规则例外、候选与历史事实分离、跨入口统一准入和可恢复提交。非目标：任意规则替代、删除重命名、弱化保护、ID特判、自动批准BUG-0063、生产启用或Sprint关闭。本Change交付后正式样本仍需独立授权。

## 设计方案

### D1 复用设计系统与局部扩展

采用DS策略，复用Chat、Composer、现有分项诊断及确认组件。拒绝CSS整页移植和新建平行Chat壳。先完成UI Skeleton与首轮确认再实现细节。原型仅结构Mock，不能直接作为鉴权或审批逻辑。

### D2 版本化替代提案与共享验证器

新增治理模块职责：提案规范化、证明核验、授权状态、引导转换与提交协调；compatible_append保留独立语义。提案schema v1采用稳定键序规范化JSON摘要，绑定project/binding revision、目标Change、predecessors、capability/requirement、before/after、delta、交付投影、验收manifest与附件、策略和验证器版本、义务映射。拒绝重复键、未知schema、越界路径、符号链接、超限内容和歧义身份。

首版classification=guarded_exception_extension：每条改写映射旧拒绝条件、新默认拒绝条件及唯一受支持例外compatible_append_verified。不接受自定义代码表达式；逐项检查未映射差异为零、不可豁免义务保持，并要求独立审查和完整回归哈希绑定。文本和模型观点不能替代证明，不确定返回unsupported_replacement。保护清单本身不能由当前提案修改。

统一admission返回decision、reason_code、safe blockers、proposal revision、policy version、input fingerprint。产品、CLI、Sprint预检和Workflow Sync复用；只读核验不运行仓库命令、不写授权、不隐式刷新历史记录。

### D3 服务端授权与审计

准备权限复用项目可写；批准/拒绝/撤销仅有效空间所有者的认证人类会话。平台管理员无隐式跨空间批准权；Agent/worker服务身份不能调用人的批准端点。相同所有者可准备并批准，仍须单独确认准确版本。每个操作重新核验空间状态、归属和绑定。

授权存储独立于可写仓库，数据库保存提案修订、不可变授权事件、当前状态投影、领取操作与围栏序号；使用唯一(project_id, request_key)和proposal revision比较。签发收据包含actor、purpose、project、revision、digest、issued/expires、policy、key id，默认24小时。建议复用受维护库的Ed25519实现，密钥通过受控部署注入且Agent无法读取，历史公钥保留；算法与依赖锁定在实施入口确认。公开仓库只存安全引用/哈希或无秘密签名收据，不含私钥、会话凭证。

批准/撤销追加事件，当前投影可用条件更新维护；禁止覆写批准内容。CLI提交须在线核验权威撤销及权限，离线只读验签不能获取新写资格。过期/撤销/内容或所有权变化只阻断未领取授权，已提交合法历史保留；伪造或信任撤销阻断依赖恢复。授权服务不可用fail closed，普通遥测失败不伪造业务失败。

### D4 提交协调与中断恢复

围栏作用域为project规格树，所有归档写入口共用；持久单调fence与lease防旧执行者提交。事务内比较批准状态/版本并绑定operation id与输入摘要，从approved到claimed只有一次。撤销先赢则领取失败，领取先赢则撤销返回operation_started，不能报告已经回滚。

阶段：prepared→claimed→merge_verified→move_verified→synced→completed。每步保存预期效果与回读摘要；文件写入和DB不假定原子。写前复读全部指纹、权限、策略、租约及fence；写后回读一致才能推进。领取后未确认写入的恢复先核验现场，不能因授权过期或超时重新创建操作；重新合并必须证明原操作未合并且原版本/围栏仍可安全使用，否则阻断。已合并只迁移和同步，不重放模型。外部非受控文件变化通过指纹检测隔离，不声称能阻止宿主任意写入。

归档完成凭据关联授权收据与原/目标spec树、delta、唯一归档身份和journal；不回写旧manifest/journal证明。proof edges区分disjoint、compatible_append、controlled_replacement，逐边更新保护视图，结尾验证当前有效spec与链效果。所有证据依赖与归档集合最终复读；未完成候选不可作历史边。

### D5 首次可信启用与归档自举

信任根来自既有可信部署运维边界，不能来自待执行仓库。最小引导校验器作为经独立制品审查的部署组件，其输入是签名release摘要、精确旧新policy版本、验证器摘要、机制Change的精确delta/验收、项目与绑定、不可豁免义务清单、授权及转换操作ID。运维确认制品、空间所有者确认项目转换，两类凭据用途隔离，不能互签代替。信任锚缺失返回policy_not_trusted，不生成默认批准。

顺序：制品核验及验收→两类精确授权→项目围栏内旧策略/身份/链/证据/签署复核→仅对清单列明的机制策略转换执行写入→回读及完成机制归档记录→发布项目策略active。中途是activating且普通替代不可用，按bootstrap operation恢复；最终active写入失败只回读续接，不重复合并。新策略不得批准本次引导。引导器仅接受versioned policy installation转换，不是可被业务提案调用的通用豁免；其实现必须通过同样安全负例和独立评审，证据不足阻断。

本Change修改旧受保护条文，归档时必须走上述精确转换，而不是由尚未启用的新验证器自证。实施阶段可以在隔离部署完整验收此流程，正式根及授权缺失不阻止交付验证，但阻止正式启用/归档。批准需求和本次创建Change均不构成这两类真实凭据。

### D6 与BUG-0063的顺序及冲突处理

本Change正式转换生效后才能为BUG-0063生成新的精确替代提案。BUG-0063现有delta以旧基线写成，不能在新策略生效后原样合并导致删除新保护。届时必须只读比较新基线，若原候选与现行条文不一致，回到该BUG的受控返修/重新验收，重新绑定准确内容并取得独立批准；不在本Change修改其delta或复用已过期批准。原18项AC按受影响指纹保留或增量复验，不伪造原交付失败。新机制不依赖BUG-0063先归档，避免跨Sprint环依赖。

## 数据与 API

建议在既有governance路由增加项目作用域提案读取/准备、批准/拒绝/撤销及能力预检；首次启用使用独立运维制品确认与项目确认入口，不能和一般approve共用purpose。写请求携带expected_revision、idempotency_key、proposal_digest；操作者、项目权限和期限由服务端确定。读取屏蔽无权对象，错误通过现有安全结构传播，禁止客户端路径决定仓库。

新增数据库实体为 replacement_proposals、replacement_authorization_events、policy_activation_operations、replacement_archive_operations 和 governance_archive_operations；提案状态保存在 replacement_proposals，不另建授权状态表。字段及索引以 replacement_schema.py 为准。事件不可变，状态投影版本CAS；SQLite事务与MySQL行锁路径均验证并发唯一性。提供幂等迁移、备份/回退说明，不自动修改真实数据库。API同步docs/03-api-index.md、OpenAPI、Orval与请求测试；DB同步docs/04-database-design.md、SQLite/MySQL迁移和测试。授权凭据/历史公钥/恢复记录在仍被引用时不可清理，首版不新增自动销毁。

## 界面契约（UI Contract）

事实源：REQ prototype.html结构→context.md交互→acceptance→ui-design token；业务安全以PRD/本设计/spec约束为准，HTML演示不覆盖权限。局部一致模式，仅审批区；旧问题截图不作为新UI像素参考。Mock原型缺真实加载、错误、权限和已领取状态，由本设计补齐，不修改既有Chat壳或Composer行为。

保留品牌、侧栏密度、导航、对象会话、草稿及原附件/Skill。Ops字体Inter/Noto Sans SC，14—16px、1.45行高、细边框、圆角≤8px，金色主按钮，深浅主题token。抽屉最大720px、确认520px且不超视口，768px以下全宽、差异两列改单列，390×844无页面横向溢出。确认外部点击不关闭，取消/Esc及焦点归还明确；提交中防重复，结果未知先回读。

| 动作/组件族 | 弹层与selector | 状态 | 证据 |
|---|---|---|---|
| 查看/关闭审阅 | Drawer；replacement-review/drawer/close | 加载、空、错误、打开/关闭 | 1440/390截图、焦点 |
| 展开差异 | Details；replacement-diff | 长文、展开/折叠 | 换行、overflow |
| 批准 | Confirm；replacement-approve/confirm | 待审、无权、过期、冲突、提交中 | 真实请求、取消与零自动归档 |
| 拒绝 | 同一Confirm+原因；replacement-reject | 必填、失败、成功 | 校验与保留输入 |
| 撤销 | 同一Confirm；replacement-revoke | 未领取、已领取、竞争 | 版本竞争与准确文案 |
| 首次启用 | Panel；replacement-bootstrap | 缺根、缺一类授权、activating、active | 两类用途及真实隔离启用 |

selector继承REQ原型，正式组件入口在src/web/src/components/chat新增审阅组件并接入ArchiveBlockers。原型按钮仅演示，不复制其中Mock成功提示作为业务结果。

## 界面骨架（UI Skeleton）

页面壳→项目操作区常驻入口或Composer分项诊断中的兼容证明快捷入口→同一审阅Drawer（身份/差异/保留义务/证据/授权/独立签署）→共用确认族；首次启用独立面板。先提供安全Mock状态容器、selectors及后端能力接口占位；1440首轮确认后才细化。实施批次：壳与诊断→抽屉与差异→整个动作族→权限错误/响应式。样式采样selector为drawer/diff/confirm/按钮，记录font、line-height、width/height、gap/padding、border/background/color、z-index/overflow/position；每批截图归属Change evidence。

## 原型冲突处理（Conflict Resolution）

原型为结构示意而不是生产鉴权：仅显示待审/批准等少数样本状态，生产补齐后端权威状态与首次启用动作；“批准完成”不等于归档，“已领取”不可撤销为回滚。Skeleton 已获用户确认，真实视觉按 evidence/product 的阶段与视口矩阵回填。不以HTML脚本通过替代真实API。REQ最终一致性在交付前回填，其他UI无复刻目标。

## 验证与观测

逐项映射REQ 20+4+4 AC，建立acceptance-plan后按隔离样本取证。分类与义务映射、签名/身份/重放、24小时边界、SQLite/MySQL竞争、引导循环/未知版本、多跳/断链/并发/中断均有正负例。真实首次成功、拒绝、原操作恢复分别记录；真实上传成功后门禁拒绝保留附件，非失败附件。API/worker/controller/CLI策略版本一致，1440/390深浅主题及computed style明确。

product_data_collection_observability: applicable；affected_layers: usage_events、request_logs、task_traces、task_trace_spans、authorization_audit、governance_archive；reason: 授权和引导跨请求/执行阶段；validation: AC-003/004/019/020及跨入口。遵循docs/standards/product-data-collection-observability.md，事件字段不得作为鉴权；直接CLI不伪造UI事件。凭据、Prompt及私有路径不进入公开证据。对象存储产品schema不变（复用附件），移动端/桌面/小程序N/A（未启用）。已实现 API、授权持久化、归档控制器与 Chat 局部审阅；OpenAPI/Orval 同步，隔离验收证据持续回填。

## 风险与回退

引导信任根是正式部署前置条件，不能用测试密钥或手填JSON替代。发布回退停止新授权/激活，保留历史验证器、公钥和记录；旧执行端对未知schema只读。跨存储故障靠检查点与回读恢复，不盲目DB恢复/逆合并。代码交付通过与正式归档ready独立报告，失败保留全部证据。

## 文档与治理收尾

同步安全规则、归档准入/验收标准、部署密钥与版本协商说明、测试映射和使用文档适用部分；若触及治理脚本/规则，实施阶段生成docs/spec-logs治理日志与索引。不得仅修改说明不接入产品与CLI共同写边界。


## 共享入口实现与恢复补充

`archive_dispatch` 将对象解析、当前权限和精确提案解析汇入共同控制器。已批准替代走 replacement_coordinator；普通 Change 和已全量归档的 Sprint 使用 governance_archive_operations，并共享项目 OS 锁及数据库 fencing token。Sprint 不因替代批准跳过独立签署，也不自动扩大到未归档的范围。

CLI 通过仓库外私有会话配置调用在线接口，不持有签名私钥，不直接写规格。Chat 对可信策略已启用的归档命令交由控制器执行，模型调用为零，独立记录归档执行和用量结算。尚未可信启用的既有部署保留原执行路径，但不能消费新的受控替代边。

候选预检可以只读解析唯一有效批准，无需提前写证明文件。领取后凭同一操作检查合并、迁移和同步结果；结果未知时保留围栏。完成重放核验原交付、证据及完整历史，不要求全局规格永远停留在该操作完成时的版本。Sprint 关闭指纹保留手工内容和签署，仅归一化既有同步器产生的 note、时间戳及前导空行。

## 首次可信启用闭环返修

原部署和审阅路径缺少接线及准备入口，现补齐同一授权模型。只读 preview API 在临时目录归档预演并绑定当前验收/交付/规格；返回全文与摘要供独立复核。离线工具校验审阅包、可信公钥用途和显式批准摘要，签发 24 小时运维收据，不调用 API。产品导入仍经现有 prepare，所有者经原 confirm 执行，恢复经原 resume，保留乐观版本和项目围栏。部署显式 overlay 提供固定工具链、只读根和在线签名 socket；运维私钥不进入在线服务。

UI 继续复用已确认 720px 抽屉和 520px ChatDialog；新动作族与截图对照见 acceptance-fixes.md。Mock/API 边界：结构原型不证明权限；真实页面使用隔离真实会话和数据库，状态不得以 mock 结果冒充真实归档。验收涵盖新生成、独立运维导入、所有者确认、结果与原操作恢复。
