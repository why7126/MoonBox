---
requirement_id: REQ-0025-chat-workbench
title: Chat 工作台验收清单
owner: product
created_at: 2026-09-08 11:27:56
updated_at: 2026-09-14 00:06:38
acceptance_status: passed
---

## 当前交付事实（最终验收回填）

用户确认的单机Compose、SQLite、本地独立备份、本机Codex认证单文件和显式unlimited策略已实际部署到所选项目仓库及moonbox编码空间。用户重新登录后通过真实页面完成两轮发送，分别结算14969/15189 Tokens；刷新保留两轮回复，轮次数量2、互斥及并发占用归零、两轮Diff均为空。证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/target-deployment/account-verification.json及logged-in-acceptance.png。实际源仓库未被模型修改，工作区从已提交树初始化，当前目录未提交改动不会自动导入。

最终需求边界：无用户/空间运营配额；同会话互斥、单机顺序调度、有限结果处理缓冲和容器/协议安全边界保留。聊天和备份不自动过期；主动删除主数据、记录独立删除日志，旧备份物理expire前保持待清理，恢复前重放删除。API不挂载凭证或Docker socket，受信任控制器使用单文件认证，执行容器保持隔离。本期不交付MySQL/S3正式灾备、异机灾备或独立平台账号；SQLite与MySQL的业务兼容测试保留。

34项功能、8项横切、8项原型AC均有实现及验证映射；RC-001至004已关闭。Ops样式迁移、共享侧边栏、深浅主题、1440/1024/390视口及computed style承接evidence/sidebar-ui和live-web-execution，视觉Mock范围明确；本批当前账号Web/API/Worker/模型验证不使用Mock。PRD、流程、故事、验收、review、trace及prototype context已按最终认证/配额/保留策略核对一致。下文的未实现、暂缓、待映射、待登录及阶段进度均为历史检查点，不代表当前待办。归档与发布仍为后续独立动作。



# Chat 工作台验收清单

## 验收说明

当前已完成受控环境功能、权限、视觉与真实执行验证。以下复选框按现有证据更新；平台正式认证、并发压力、运营容量及删除时限相关项目仍保留未通过。测试使用受控仓库、合成身份与可撤权对象，不使用真实客户数据；此清单不等于生产上线批准。

## 功能 AC

- [x] AC-001（FR-001）从前台导航进入独立 Chat 路由；未登录被引导登录，无可用仓库时显示原因且不产生模拟回复；旧AI抽屉保持原行为，显式Chat入口携带授权对象且不自动执行。
- [x] AC-002（FR-001）使用两个用户和两个空间测试列表、直接会话标识、消息、Diff 与发送接口；跨用户/跨空间请求被拒绝且不泄漏摘要。
- [x] AC-003（FR-002）新建并发送两轮输入，刷新、切换后核对同一 Codex 标识、工作目录及关联，不使用最近会话猜测。
- [x] AC-004（FR-002）首次启动失败无 Codex 标识时保留未连接会话；仓库撤销或工作区丢失时阻止续写且明确原因。
- [x] AC-005（FR-003）标题和对象搜索、置顶、取消置顶、非空重命名、全部/置顶/归档筛选均更新一致，空结果可恢复。
- [x] AC-006（FR-003）归档会话只读，恢复前重验权限；运行中、停止中、等待/连接中及未知状态禁止归档和删除。
- [x] AC-007（FR-003）删除需二次确认和当前工作区变更检查；历史曾有 Diff 但已处理的会话不永久禁删，代码与业务对象不被删除。
- [x] AC-008（FR-004）关联允许零或一个主对象、多引用；选择两个主对象失败；候选对象使用真实标识并按权限过滤。
- [x] AC-009（FR-004）关联保存只影响之后轮次；对象撤权后发送与历史快照/回复/Diff读取拒绝无权内容；无法剔除执行端历史时禁止续用并引导干净会话，错误不泄漏原文。
- [x] AC-010（FR-005）发送后修改源对象，核验历史轮次仍指向当时实际版本/受控快照，不仅保存可变 ID。
- [x] AC-011（FR-005）超长上下文截断有提示；快照与聊天正文不进入通用日志，历史快照读取校验权限。
- [x] AC-012（FR-006）空输入不发送；重复点击、双标签页与请求重发只建立一个有效轮次，服务端执行互斥生效。
- [x] AC-013（FR-006）发送失败保留草稿；刷新、关闭页面及切换会话不停止后台运行，恢复后显示原运行。
- [x] AC-014（FR-007）回复、命令结果、文件事件及终态可追溯到执行端；无对应能力时不显示伪造步骤或测试百分比。
- [x] AC-015（FR-007）重复和乱序事件去重且终态不回退；消息中的脚本或 HTML 作为不可信内容处理，不执行注入。
- [x] AC-016（FR-008）两轮连续修改同一文件，分别核验执行前后基准、本轮 Diff 与累计 Diff，旧变化不算入新轮次。
- [x] AC-017（FR-008）无修改显示空态；新增、删除、重命名、二进制、超大 Diff 与基准缺失各有准确反馈。
- [x] AC-018（FR-009）确认停止后先显示停止中，收到执行端终止确认才允许新输入；终止超时进入未知。
- [x] AC-019（FR-009）浏览历史仍可停止明确的当前运行；停止与自然结束竞争遵循真实终态，已经产生的文件保留。
- [x] AC-020（FR-010）模拟网页断连但后台继续执行，重连查询原运行，不自动重复写入；无法确认终态维持互斥。
- [x] AC-021（FR-010）只对确认终止的失败/停止轮次开放手动重试；新轮次关联旧轮次，重验快照权限，内容改变不静默替换。
- [x] AC-022（FR-011）连续轮次复用会话工作区；不同会话的分支与目录独立，只允许预配置授权仓库。
- [ ] AC-023（FR-011）验证并发会话的端口、数据库、网络和凭证隔离；容量不足真实等待，配置不足时不声称 worktree 已隔离全部资源。
- [x] AC-024（FR-012）只读角色及无合规 Change 的正式开发请求不能产生越权写入；严格只读在执行端强制。
- [x] AC-025（FR-012）验证执行端工作目录、网络和凭证限制；前端无凭证，不通过全权限绕过失败，未接通审批不出现批准按钮。
- [x] AC-026（FR-012）无默认授权不能提交、合并、推送或部署；网页输入不能逃逸为宿主机任意命令；已有业务阶段不被自动完成。
- [x] AC-027（FR-013）执行中重启服务后恢复消息、轮次、事件与互斥，未确认旧执行结束前不能启动冲突新运行。
- [x] AC-028（FR-013）SQLite 与 MySQL 验证唯一性、并发状态和清理策略；删除会话不提前清除仍在保留期的审计。
- [x] AC-029（FR-013）发送/停止/重试行为关联服务端可信请求和运行标识；伪造客户端请求标识不能替代授权与可信 request_id。
- [x] AC-030（FR-013）观测失败不阻断主流程；敏感字段及本机路径过滤，日志/事件按已批准保留策略清理，业务正文不作为观测 metadata。

- [ ] AC-031（FR-012）单机服务端使用部署者本机Codex认证，前台用户无需个人账号绑定；按用户/空间计量；显式unlimited不按运营额度拦截，有限模式超限拒绝/等待，不泄漏凭证或改变会话私有性。
- [x] AC-032（FR-013）聊天、引用快照和 Diff 不因 90/180 天到期自动删除；归档保留，主动删除满足运行终止与无未处理变更条件。
- [ ] AC-033（FR-013）有限容量配置在上限边界阻止新增并提示清理，unlimited不按累计存储限流，均保留查看/删除；运行前预留结果处理缓冲，技术边界超限不静默丢弃内容。
- [ ] AC-034（FR-013）对业务主存储、备份和执行端会话副本验证已约定的删除范围及时限；代码不随会话删除，观测审计按独立保留策略处理。

## 横切 AC（knowledge-base）

本页为 web-catalog，未命中技能定义的 admin-list/admin-form/admin-modal/media-upload 标签；下面显式类比复用通用弹窗与反馈经验，不将前台标为管理端，也不引入上传或表格能力。

来源：`docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`（001–002）、`admin-list-page-consistency.md`（003–005）、`docs/knowledge-base/retrospectives/sprint-003-retrospective.md` 的 S3-A004/S3-A005（006–007）、`docs/knowledge-base/best-practices/prototype-driven-ui-gate.md`（008）。仅承接本需求适用内容，不变更历史行动项状态。

- [x] AC-XCUT-001 弹窗样式不让通用 modal-card 与专属宽度类冲突；采样最终 computed width 与合同一致。
- [x] AC-XCUT-002 在 1024×600 等低视口验证弹窗 body 滚动、错误提示和底部确认/取消可达，遮罩不引起背景误滚动。
- [x] AC-XCUT-003 重命名、关联、归档等反馈使用 fixed toast，出现与消失前后内容区域位置不变。
- [x] AC-XCUT-004 删除和停止使用项目设计系统确认弹窗，无 window.confirm；取消不改变业务状态。
- [x] AC-XCUT-005 会话筛选与搜索结果、计数和空态同步；管理端分页 DOM 对齐 N/A，本页没有管理端 CRUD 表格分页。
- [x] AC-XCUT-006 对每个动作族一次性验收按钮、浮层、禁用、错误与关闭路径，失败保存保留草稿。
- [x] AC-XCUT-007 执行环境只读挂载/禁止目录返回明确失败，允许目录可写；验证部署环境实际约束，不以本机成功替代。
- [x] AC-XCUT-008 视觉返修后旧截图失效，重新采样并同步 PRD、原型上下文和验收证据。

## 原型驱动 UI AC

- [x] AC-PROTOTYPE-001 原型页面、区域、组件、状态、数据依赖、断点和 1440px 焦点已拆解，trace 引用与实际文件一致。
- [x] AC-PROTOTYPE-002 Change 建立页面路由、组件插槽、状态容器及稳定 selector 的 UI Skeleton，首轮确认早于细节实现。
- [x] AC-PROTOTYPE-003 1440px 深浅主题首屏及关键交互通过截图验收，记录 viewport、页面、状态、来源与结果。
- [x] AC-PROTOTYPE-004 归档前 PRD、用户故事、业务流程、验收、prototype 与实现最终一致；所有差异有处置证据。
- [x] AC-PROTOTYPE-005 完成动作按钮→modal→selector→状态→证据矩阵，分批验收；原型紫色参考不替代 Ops 目标 Token。
- [x] AC-PROTOTYPE-006 采样字体、行高、宽高、间距、边框、背景、层级、滚动和位置；窄视口不遮挡输入与停止入口。
- [x] AC-PROTOTYPE-007 支持外部关闭的浮层覆盖内部 stopPropagation：内部操作不误关闭，外部点击仍关闭；Esc 与焦点回归正确。
- [x] AC-PROTOTYPE-008 正式产品无演示设置、固定样例和人员信息；真实接入与模拟参考明确分离。

## UI Reference Replication Contract 种子

- 保真模式：风格迁移。
- 优先级：用户确认 > PRD 业务语义 > 项目 Ops Token/共享组件（视觉） > 附件 HTML（布局与动作参考）；原型模拟逻辑不能推翻真实执行语义。
- 组件清单：导航、仓库标题、会话选择、历史列表、关联条、消息区、输入区、执行状态、轮次选择、事件/Diff、弹窗、toast、窄视口与滚动。
- 动作矩阵、selector 候选、样式采样与批次详见 `prototype/web/context.md`。
- 非目标：不复刻蓝紫品牌、演示人员与样例，不新增任务树、审批引擎、附件、自动提交或共享会话。
- 证据边界：参考文件已入库并静态检查；原型 PNG 暂不要求，目标 Skeleton 与最终视觉证据在实现阶段生成。

## 决策与验收前置条件

已确认平台统一承担认证与额度，消息/快照/Diff 主动删除＋容量上限；具体阈值和副本删除时限见 review.md 条件通过项；路线与固定版本在 Change 设计和真实验证收敛。没有这些结果不得把相关 AC 标通过。服务端预配置仓库、个人私有会话与 Ops 风格已经确认，不重复询问。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-14 00:06:38
accepted_by: workflow-sync
source_change: add-chat-workbench-codex
source_sprint: sprint-004
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 首轮局部证据

历史阶段记录（已由当前清单及后续证据更新）：当时仅AC-PROTOTYPE-001/002完成：拆解见prototype/web/context.md；首轮骨架和样式见 openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/ui/。其他功能、权限、真实执行及完整视觉验收未通过。12个前端测试不替代后端或真实Codex证据。


### 会话管理接入阶段证据

历史执行记录（仅描述当批状态，最终交付结论见归档 Change trace）：会话管理与事件读取已接API，内部额度预留/终态结算已通过SQLite与MySQL测试；当前仅任务3.2新增完成，整体4/25。真实模型执行仍未开放；关联快照、完整清理和文件级Diff待完成。详见openspec/archive/2026-09-13-add-chat-workbench-codex/trace.md「会话管理、事件与预留增量」及evidence/session-ui/。合成视觉数据不作为模型执行或真实CRUD证据，完整AC保持当时尚需验收。


### 受控执行补证

本机专门合成仓库和测试数据库的两轮真实执行、进程重建恢复、持久化回复、本轮/累计Diff已通过。详细证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/backend/real-runner.json。平台认证代理、跨会话容器/网络隔离与正式额度未验收，包含这些组合条件的AC不整体勾选。


## 当前实现与证据映射（2026-09-08）

本表承接本轮实现状态，不替代正式接入验收。执行服务与有历史会话删除仍受未配置门禁限制；未确认项不勾选完成。

| AC | 当前结果 | 证据或限制 |
|---|---|---|
| AC-001 | 已实现，入口和回归通过 | ChatWorkbenchPage、RequirementCenterPage；79项Web回归与视觉证据 |
| AC-002 | 接口授权通过，实际业务配置待接入 | test_chat owner/space/repository/object ACL |
| AC-003 | 受控网页真实双轮及刷新通过，正式入口仍关闭 | live-web-execution/verification.json；同线程0→1→2 |
| AC-004 | 仓库撤销与工作区检查通过，平台续接待验证 | repository_revocation、workspace tests |
| AC-005 | 通过 | history_filters_all_and_pinned、CRUD、关联对象搜索 |
| AC-006 | 通过 | active/unknown锁、归档/恢复接口与动作族 |
| AC-007 | 受控主存储、代码保护及真实执行历史删除通过 | 新增备份恢复防复活，含空会话；正式删除期限暂缓 |
| AC-008 | 通过 | relations_snapshots_and_revocation、RelationsDialog tests |
| AC-009 | 服务端撤权及执行门禁通过，平台执行端验收待接入 | 列表/详情/快照/回复/Diff拒绝；owned与write policy |
| AC-010 | 通过 | immutable snapshot与retry快照断言 |
| AC-011 | 通过 | 48KB总量、truncated展示、日志正文排除 |
| AC-012 | 内部事务通过，正式发送待配置 | admission/concurrent enqueue/Composer幂等 |
| AC-013 | 受控网页刷新/断连恢复通过 | live-web-execution/verification.json；无新轮次自动重放 |
| AC-014 | 受控真实执行和事件链路通过 | live-web-execution/verification.json；正式平台尚未开启 |
| AC-015 | 通过 | fencing/cursor/terminal测试、SafeMarkdown注入断言 |
| AC-016 | 真实内部双轮通过 | real-runner本轮1→2、累计0→2 |
| AC-017 | 通过 | workspace difference tests、DiffView元数据/范围 |
| AC-018 | 真实网页停止确认通过，失联维持unknown | live-web-execution与recovery-cleanup；未从进程消失推断终态 |
| AC-019 | 通过 | 历史轮次停止、确认框固定原活动轮次竞争测试 |
| AC-020 | 受控网页与恢复worker通过 | 网页恢复原轮次；deployment.json重复恢复不领取unknown |
| AC-021 | 内部重试通过，正式接口保持门禁 | retry_reuses_snapshot_and_queued_stop_settles |
| AC-022 | 目录与真实线程复用通过，平台预配置仓库待提供 | workspace tests、real-runner |
| AC-023 | 独立Linux会话容器与真实模型执行通过 | recommended-deployment；无DB/peer/socket挂载，工具凭证/网络拒绝；正式平台压力测试未完成 |
| AC-024 | 角色门禁、原生与Linux严格只读预检通过 | 两个独立容器预检及既有write_policy测试 |
| AC-025 | 原生与Linux真实运行隔离通过；共享认证未接入 | 专用seccomp、非root/no-new-privileges；个人测试凭证不等同平台认证 |
| AC-026 | 保持审批/正式执行门禁 | 容器Git元数据只读；无自动commit/merge/push/deploy |
| AC-027 | 受控worker重启、进程组故障与镜像恢复通过 | SIGTERM真实轮次、SIGKILL合成执行器；unknown保留锁 |
| AC-028 | SQLite/MySQL业务矩阵通过，新增SQLite恢复删除通过 | backup-verification.json；MySQL/S3恢复未验证 |
| AC-029 | 通过 | 可信request_id、稳定usage_events、turn Task Trace |
| AC-030 | 通过 | trace故障降级与正文/凭证不采集 |
| AC-031 | 待平台认证与正式容量配置验收 | 用户明确暂不配置正式额度，平台专用认证未提供 |
| AC-032 | 主存储策略与删除检查通过 | 观测清理不删业务正文；归档保留；当前代码检查测试 |
| AC-033 | 历史阶段记录：内部容量预留通过，正式配置与超限处置当时尚需验收 | 预留/结算/超限断言，未知用量不释放预算 |
| AC-034 | SQLite本地备份、恢复删除重放及真实执行副本删除通过 | 物理expire与恢复过滤分别验证；正式S3/MySQL备份及约定时限未闭环 |

横切AC-XCUT-001/002：弹窗尺寸/低视口滚动与footer证据见session-ui；003：共用fixed toast，关联保存已接通；004：删除/停止均为DS确认，取消测试通过；005：服务端授权后计数/分页及all/pinned测试通过；006：动作族错误、草稿、关闭及disabled测试通过；007：双合成容器实际只读挂载/工作区可写通过，正式模型容器待验证；008：本轮重新生成截图，不沿用旧视觉结论。原型AC-PROTOTYPE-001/002保留通过；003/005/006/007/008使用本轮动作族截图、computed和注入/关闭测试补证，004最终一致性仍等待正式接入结果。证据目录：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/session-ui 与 evidence/backend。

## 共享侧边栏验收与部署（2026-09-08）

本批共享侧边栏已完成并部署：WorkbenchSidebar 统一品牌、版本、八项导航、折叠、用户/空间动作；useWorkbenchTheme 统一持久化与跨页主题。个人私有说明仅保留在会话区。需求中心原有账号和空间操作由共享模块承接，Chat 的空间选择限定于其授权目录，设置空间和进入后台分别遵循空间与账号权限。

验证：9个测试文件87项通过；实际18102构建页面52张截图、12组双页computed style完全一致（1440×900/1024×600/390×844，深浅×展开/折叠），16份账号/空间弹窗样式样本；跨页导航、主题持久化、只读空间、取消与Esc焦点返回通过，pageerror=0。另重新生成23张会话/关联/执行/停止截图，避免沿用旧CSS证据。所有浏览器业务响应均为合成API，不等同真实平台执行通过。证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/sidebar-ui/{computed.json,verification.json,*.png} 与 evidence/session-ui。

源码证据确认根因：原Chat独立导航缺少分组、版本、折叠和账号菜单，通用按钮选择器覆盖rc样式。本轮浏览器又验证并修复390px空间浮层越界、空间设置遮罩留白/分列越界，以及CSS收敛造成的执行栏select颜色回归。最终导航展开224px/折叠72px，导航行高40px、padding=0 12px、gap=11px、font-size=13px，分组标题padding=16px 12px 7px；两页同状态值一致。

门禁：Cross-cutting tags=无admin-*（前台复用账号动作），AC-XCUT/knowledge_base_refs=pass，prototype与modal CSS经验已承接，PROCEED；本批Prototype Gate=pass，既有Skeleton承接，1440px/关键动作/computed=pass，Mock/API边界已声明；UI Reference Replication Gate=pass（共享壳、导航、账号动作、响应式）。REQ六件套及prototype context完成本批一致性回填，整体归档一致性仍待其他任务完成。

影响面：Web页面、共享组件、CSS、前端测试及验收脚本；复用已有鉴权API，不新增接口、DB迁移、客户端生成、部署变量或权限政策。product_data_collection_observability：本批not_applicable、affected_layers=[]，API/DB/请求日志/usage_events/Task Trace及请求封装字段未改变，详情见design补充合同。仅重建Web，后端与recovery镜像保持原值；健康接口ok、Chat页面200，镜像指纹见verification.json。


## 本地凭证与受控仓库真实执行验证（2026-09-08）

用户授权采用本地登录与可丢弃测试仓库，正式限额及删除时限继续暂缓。本批新增显式开启的 local_probe 认证工厂；仅复制登录文件到0700临时目录，文件0600，不加载个人配置、插件或历史。测试结束删除临时认证与执行历史；原登录文件不由测试写入。令牌刷新和异常宕机后的残留清理未在本次验证覆盖。

真实 codex-cli 0.153.4 通过后端 claim/run_claim 完成 counter.txt 的0→1→2修改、进程重建后同线程恢复、本轮及累计Diff和真实中止终态。原生命名权限配置隔离模型工具：凭证、相邻工作区与测试DB读取拒绝，仓库允许写入、.git禁止写入、工具外连拒绝；只读配置拒绝工作区写入。安装版本要求 initialize.experimentalApi，首次RPC拒绝经此修正后通过；增加读写降级回归。

真实测试1项通过（27.12秒）；后端回归41项通过、2项显式真实执行测试默认跳过。两轮完成用量分别22500和1455，均已结算；立即中止轮次未返回用量，标记usage_unavailable并保留reserved，不能按零消耗释放，实际用量对账仍未闭环。

证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/backend/local-credential-execution.json。使用合成API身份和独立SQLite，内部enqueue入队；本机原生执行不是已部署Docker worker或浏览器发送端到端证据。服务发送/重试仍503，未改真实环境、正式限额、删除期限或已有部署镜像。RC-001仅补齐本地正常路径及隔离子证据，进程异常/全链路部署等门禁不据此关闭。

影响：后端执行适配器、显式测试认证工厂、测试和部署说明。API契约、DB结构、UI、客户端生成均无变化。product_data_collection_observability=applicable；affected_layers=[api,db,task_traces]，沿用现有事件及额度持久化；validation=真实两轮、恢复、中止及保留未知用量预留通过，证据只保存状态和计量数值，不保存凭证或完整对话。

历史执行记录（仅描述当批状态，最终交付结论见归档 Change trace）：执行链路复盘：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004，保持in_progress、13/26项，未标记整体实施完成态或归档。此前“缺少本地执行认证授权”的依赖已解除；正式共享平台认证与完整部署验收仍独立待完成。建议沿用本批显式开启、默认跳过的真实执行回归，不另建治理Issue。


## 五步隔离执行闭环（2026-09-08）

用户本批明确授权执行到测试清理。已完成：有界接收终态后用量、单调去重及可信记录幂等补结算；受配置与有效期保护的独立常驻worker；真实登录后的测试账号/空间/仓库入队门禁；回环地址18121上的构建Web与真实API验收；最终停止服务并删除测试数据。正常部署仍默认关闭发送/重试，正式认证、运营限额和删除时限继续暂缓。

实际四轮：完成0→1、worker重启后同线程完成1→2、网页停止、运行中SIGTERM重启worker后停止。恰好四轮，无自动重放；两轮修改与第三轮停止已按33873/2489/28778 tokens结算，第四轮停止没有权威用量，保持usage_unavailable与reserved，未按零消耗释放。整个临时测试DB随后按用户授权删除，不能把删除测试DB表述为该轮已对账。缺失用量的处理路径是保留预留、读取待对账清单，只有可信执行端结算凭据可用时才补结算；无自动推算或手填零值接口。

真实浏览器通过：创建会话、鉴权发送、刷新恢复、停止确认、历史读取、本轮/累计Diff、其他账号访问404及执行白名单拒绝；没有业务API Mock。初次刷新丢失选中会话与终态后输入区旧活动状态，分别通过URL保存不透明会话标识后重新鉴权读取、活动会话轮询修复。第一次停止观察90秒超时，退出浏览器没有停止后台运行；重新连接同一轮次后停止确认通过，未新建重复任务。截图及最终样式采样覆盖1440×900；本批没有布局/CSS改动，深浅/窄屏基线承接此前共享侧边栏验收。

实际原生权限探针通过：凭证、相邻种子仓库和测试DB读取拒绝，.git写入拒绝，模型工具网络拒绝，只读配置禁止写入。API仅回环监听且仍使用正常登录验证；私有配置需isolated-test、独立临时SQLite、指定身份/空间/仓库、有效期与新鲜worker心跳。配置不包含可由浏览器传入的路径或执行命令。异常worker租约与fencing由单元测试覆盖；本轮实际重启使用SIGTERM，不宣称已做SIGKILL全链路验收。

证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/live-web-execution/verification.json、computed.json及7张真实页面截图。四条Task Trace均关联真实请求ID，事件source_id无重复，行为与节点记录存在，页面pageerror=0。临时认证、仓库、SQLite和线程历史目录均已删除，服务停止、18121端口释放已核验；运行端原登录缓存未由测试写入。保留的证据没有凭证、原始执行会话文件或真实客户数据。

影响面：后端执行/结算/隔离配置及worker、网页会话恢复、测试启动器与验收脚本。API字段和OpenAPI schema比较不变，不需重新生成Orval；API能力和发送行为、DB持久化语义、安全/部署边界均已同步文档，无新表字段或迁移。product_data_collection_observability：status=applicable；affected_layers=[usage_events,request_logs,task_traces,task_trace_spans]；validation=真实请求与Task Trace关联、可信用量去重/恢复、所有者拒绝及脱敏摘要通过。UI Reference Replication Gate承接既有合同，本批真实交互及computed样式通过。

历史执行记录（仅描述当批状态，最终交付结论见归档 Change trace）：执行链路复盘：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004。RC-001受控接入Spike通过，对应任务1.4完成，整体14/26；本次用户指定的五步已处理，整个Change仍in_progress、当时验收尚未结束，不执行整体实施完成态或归档。正式共享平台认证、生产限额/删除期限和完整部署矩阵仍独立待完成。建议保留真实网页回归与故障场景的显式测试入口，无额外治理Issue/Change自动创建。

历史执行记录（仅描述当批状态，最终交付结论见归档 Change trace）：本批最终验证：后端45 passed、2个显式真实探针默认skipped；前端7文件28 passed；构建通过。真实四轮与原生隔离证据独立记录，不以默认跳过替代。OpenSpec strict、中文、目录、Sprint scope、观测门禁、上下文预算、git diff --check通过；Workflow Sync仅dry-run，errors/warnings/blockers均0，7个子文档检查通过。整体Change未完成，不执行实施完成态同步及其完成AI Usage钩子。

## 本批50项验收覆盖复核（2026-09-09）

34条功能AC逐项映射已更新；本批新增证据集中在AC-007/018/020/027/028/034，AC-003/013/014/023/024承接真实网页与原生权限证据。其余功能AC承接原映射，不扩大为正式平台全部通过。AC-031/033依赖暂缓的正式认证/运营配置，AC-034实际备份与正式删除时限未闭环。

8条横切AC：001–006和008承接共享侧边栏及动作族视觉/样式证据；007新增只读非root部署探针，与原生工具权限分开记录，实际模型容器尚未完成。8条原型AC：001/002已完成；003/005/006/007/008承接既有共享侧边栏和真实网页证据；004整体文档最终一致性仍为归档前门禁。本批没有UI改动，不重用旧截图声称验收新视觉修改。全部正式AC勾选继续以最终验收为准。

新增证据入口：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/recovery-cleanup/。新增清理状态撤权测试2项通过；真实历史删除不等同备份删除，未知用量继续保留预留。

## 推荐组合验证补充（2026-09-09）

当前验证方案已完成：SQLite独立备份/删除日志/恢复重放/物理清理；Linux会话容器真实双轮、重建续接、运行中停止和后端claim/Diff/用量结算。AC-XCUT-007新增实际Linux容器与工具权限证据，生产认证/正式限额时限仍未完成。原型8项承接既有证据，本批未改变UI；整体最终一致性与上线验收不因此自动通过。证据见Change evidence/recommended-deployment/，具体测试数量和边界见Change trace。


### 部署脚本接入补充（2026-09-09）

任务6.3部署脚本验收通过：11项脚本、5项控制通道、5项备份/隔离测试；完整真实启动、真实登录、备份删除重放和worker清理通过。测试端口释放，常规Web/API HTTP 200。本批0模型轮次，不能替代此前容器真实执行证据或正式上线验收。


### 终态并发释放补充（2026-09-09）

并发占用返修通过：旧终态释放并发但Token保留、重复释放/迟到结算不影响新轮次、未知状态保留占槽、SQLite/MySQL迁移与竞争通过。真实网页命令启动后停止确认通过，随后消息完成并刷新恢复。证据见Change evidence/concurrency-release/；正式上线验收仍pending。


## 当前验收映射收口（2026-09-09）

已将34项功能、8项横切、8项原型逐项映射到本文件既有证据表和当前复选框。此映射工作对应任务5.5完成，不把未通过项改为通过。当前功能30项通过，AC-023（正式并发容量/压力）、031（平台统一认证及正式限额）、033（正式容量边界）和034（正式副本/备份删除范围时限）未通过；原型004整体归档一致性待正式范围完成，其余7项及8项横切通过。历史阶段段落为时间线，当前清单优先。

权限证据补充：运行中对象撤权使执行器关闭、状态unknown、预留和锁保留，无撤权后输出落盘，消息/引用/Diff继续403；SQLite/MySQL均覆盖。对应任务2.3完成。接口已覆盖会话、关系、发送、停止、重试、事件及Diff；OpenAPI路径和schema与已生成客户端一致，任务3.1完成。

双标签页真实同时发送：HTTP 200/409，各页面刷新及worker重启后数据库仍仅一轮，确认无重放；新进程Token实际10582，按app_server_process_v1结算。并发、幂等、fencing、用量及重启证据闭合，任务2.4完成。输入、消息、安全Markdown、容量/用量反馈、历史选择下停止、未知/空/二进制/大Diff分别由7文件22项Web测试、workspace测试及现有截图证明，任务4.3完成。

计量更正：此前跨进程使用历史token_total相减存在少计/漏计；旧多轮测试材料的结算数值仅为旧算法记录，不再作为计量准确性通过依据。新证据为evidence/usage-scope/protocol-totals.json、real-accounting.json和dual-tabs.json：恢复同一线程、重建进程时total重置，持久化实际值逐轮等于进程累计最大值。旧无scope待结算receipt保持预留，已结算旧记录不自动覆盖，无法取得原始可信事实时不推算金额。


### 单机常驻方案确认（2026-09-09）

用户已明确采用单机 Docker Compose、SQLite、本地独立备份、本机 Codex 认证单文件，取消用户/空间额度、并发和存储运营上限。显式 unlimited 与缺失配置区分，仍计量结算；同会话互斥、权限、未知态和单轮结果处理技术边界保留。历史及备份不自动过期；主动删除仍记录和跟踪主存储/执行线程/备份，副本无固定删除截止时间，旧备份物理移除前保持待清理。单机控制器顺序处理持久队列，容量不足不绕过隔离。正式仓库路径及空间映射尚待提供，当前不宣称正式服务已开放。方案细节以 docs/02-deployment.md 的单机常驻章节为准，替代此前“认证、限额和期限尚未决定”的当前态描述；历史证据保留。


### 单机常驻实现验收（2026-09-09）

按用户本轮决定，认证、运营策略和备份范围已明确。AC-031/033/034通过：常驻Docker Worker真实两轮10569/10769 Tokens，零Token预留而实际结算，重启不重放；主动删除后离线恢复不复活，显式移除测试备份后执行线程/备份状态均purged、无伪造截止时间，源仓库及会话代码保留。无限额度SQLite/MySQL回归和既有有限边界兼容通过。证据为Change evidence/platform-local/verification.json；当前33/34项功能通过，AC-023保留实际目标部署验收，原型004最终归档一致性仍待完成。

本轮根因证据：独立工作区仅git init导致导入源文件全为未跟踪，新增clean-status断言并建立会话初始基线；容器Worker main:49报FileNotFoundError且镜像内无docker命令，改用独立docker-cli包后真实探针通过。以上均在当前apply内修复，不新增Issue。

整体27/29项，剩余5.4实际指定仓库/空间部署、5.6最终交付同步。没有修改真实env或现有正式服务，不能把临时验证环境视作目标部署已经完成。先前“运营配置尚未决定”的历史描述不再作为阻塞理由。


### 实际单机部署检查点（2026-09-09）

用户指定当前MoonBox项目仓库及MoonBox空间。读取实际后端确认唯一空间编码moonbox对应显示名“AI原生软件工厂”，未新建或重命名空间。私有env保存仓库/空间映射、local-codex和unlimited策略，原env有私有备份；路径、ID与凭证不复制到治理证据。根up/down可根据已保存执行模式自动加载常驻Compose覆盖文件，脚本4项回归通过。

实际根up部署完成，API、Web、MinIO、Chat Worker均healthy；控制器非root，单认证文件只读挂载，API无认证文件及Docker socket，后台就绪摘要/空间权限/未配置仓库拒绝和独立备份日志核验通过。所选仓库已提交树1573文件、38876348字节成功初始化干净独立基线，源目录未改动，未提交代码不自动导入。证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/target-deployment/。

历史执行记录（仅描述当批状态，最终交付结论见归档 Change trace）：任务5.4完成，整体28/29；5.6最终当前账号端到端验收和完成同步仍待登录。现有浏览器会话失效，使用已配置初始密码的一次登录返回401，不再重试、不重置账号、不伪造会话；已打开正常登录页并请求用户自行登录。独立环境的真实双轮/重启/删除恢复证据承接上一批，不冒充本次用户账号下的实际发送。常驻服务保留运行，不清理业务数据；下一动作是在当前有效登录下验证发送与刷新恢复，再执行最终完成同步。未执行实施完成态/归档及完成AI Usage钩子。

product_data_collection_observability：status=applicable；affected_layers=[request_logs,task_traces,task_trace_spans,db]；reason=实际部署接入和身份验收；validation=仅保存部署布尔结果和计数，初始密码及日志未外泄；后台只读检查不伪造用户行为，尚无本批真实用户轮次。不涉及公开API字段、业务schema或客户端重生；UI布局不变，既有原型证据继续适用。

执行链路复盘：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004，in_progress/acceptance=pending。仓库和空间依赖已解除，剩余是当前有效账号登录；建议以空间唯一编码辅助解析显示名称，本批已交叉核对，未自动创建Issue/Change。

## 2026-09-10 执行展示返修

连续相邻、同消息和同执行轮次的文字事件归并显示；工具/状态/消息身份变化及序号缺口保留边界。原始事件默认折叠，保留最近1000条窗口说明。所选轮次当前状态单独展示，时间线状态明确标为历史。安全Markdown新增表格（表头、对齐、转义管道、行内代码、空单元格），窄屏在表格内滚动，保持HTML/图片/危险链接不可执行。旧事件缺少消息身份时仅按连续区段归并，不伪造缺失边界。

本次只改变Web展示，事件持久化、SSE、API、DB、鉴权、停止/重试、Token计量不变，无需迁移或客户端生成。文件路径链接不在本次范围。

### 本次返修验证结果

8个测试文件27项通过，TypeScript及Vite生产构建通过；Web已重新构建部署。合成API搭配实际部署Web的1440/390深浅主题8张截图、computed style及无页面溢出检查通过，12个原始事件显示为5组，原始事件默认折叠/展开通过。首轮截图发现深色表格文字被全局样式覆盖，已显式继承rc-text并重新构建复验。证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/event-display/verification.json、events-dark-1440.png及同目录其余截图。附件对照三项均已修复；无新增modal，原停止/重试测试通过。

当前应用内浏览器认证失效，未读取现有真实会话；视觉数据为合成，不声称本批真实模型执行通过。数据层与执行协议未变，现有消息及事件在重新登录并刷新后使用新渲染。未请求重新登录作为修复阻塞；无发消息或模型用量。


## 2026-09-11 验收返修：Harness 对话与轨迹

以本机 DeepSeek Harness 的对话/轨迹结构为新参考，保持 MoonBox 共享导航与空间/对象权限。对话为右侧用户气泡、无边框助手正文、紧凑自适应输入、消息复制与本轮轨迹入口；Enter发送、Shift+Enter换行、中文输入法不误发送。活动轮次显示过程摘要，失败附着轮次。消息历史加载更早页，滚动阅读不强制跳底；轨迹标签隐藏保留阅读状态。

轨迹包含按原标识配对的工具节点、搜索、内容折叠、事件概览与可调整宽度的详情。详情提供概述、参数、结果、Schema可用性及计时；窄屏上下排列。现有停止确认、原轮次重试、引用快照及Diff保留。事件每窗口最多1000条，可以读取后续窗口或从头查看；窗口边界缺少工具开始记录时不伪造开始时间。旧数据未采集字段明确显示不可用。耗时概览按对数缩放并显示说明，不冒充模型请求计时。

新增工具详情仅存于本人会话事件JSON：白名单参数、截断输出、退出码、状态、记录时间和耗时来源。先脱敏再限长；不新增表/接口/认证/部署范围。平台日志与审计不记录这些正文。明确final_answer可用时最终消息使用最终正文，其余过程留在轨迹；旧协议保持兼容。Schema、模型请求层级、缓存率、内部推理不编造，也不增加模型切换、附件、分支入口。

验证：前端31项聚焦回归通过；后端工具/权限/结算聚焦回归与构建记录见本批最终验证摘要。真实组件+合成API在1440桌面和390窄屏深浅主题观察；样式与无横向溢出记录于 openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/harness-trajectory/verification.json。未宣称与参考逐像素相同，原始参考截图含私人路径而未落盘。新一轮真实模型执行与合成视觉验收明确区分。


### 本批最终验证与一致性扫尾

后端48 passed、1 skipped（需显式启用的真实模型测试）；前端31 passed，TypeScript及生产构建通过。工具详情通过模拟App Server→Worker→真实测试数据库的入库、脱敏、结果、退出码及耗时断言；不冒充本轮真实模型验证。Web与Worker按原Compose配置更新并健康，更新前活动运行数为0；运行Worker的execution.py和tool_record.py摘要与工作树一致。原有recovery容器保留。

REQ 子文档一致性扫尾：requirement、business-flow、user-stories、acceptance、prototype/web/context已同步；trace由工作流同步。prototype.html保留原始历史参考，不覆盖附件来源，新基线冲突与覆盖范围记录在context和design。Schema、模型请求级分组、内部推理、附件与分支不属于本批；界面明确不可用，不伪造采集。产品数据采集影响声明承接本次design契约，无新表或OpenAPI结构变化，不需迁移或Orval再生成。既有SSE payload为开放JSON，本次字段说明同步API索引和DB设计。

本Change严格规格、中文优先、目录、Sprint scope与上下文预算检查通过。全仓中文优先校验被另一活动Change的既有英文标题阻断，未修改无关Change。浏览器验收为合成API配合真实组件，1440/390深浅截图已在工具输出中观察，脱敏样式摘要为长期证据；尚未进行与DSH逐像素差异断言。


## 首次输入返修验收（2026-09-11）

- 进入页面可编辑，不点击新建；仅打开/离开不创建记录。
- 单仓库自动、多仓库显式选择；未就绪可编写但不能发送。
- 首次发送依次创建和提交；新建无弹窗并清除旧conversation_id。
- 创建/发送丢响应分别保留稳定标识和草稿；并发创建仅一条记录。
- 重放仍检查成员和对象权限，不复活已删除会话；空间草稿不串用。
- 深浅1440与390视口截图观察、computed style及合成接口首次发送见 evidence/first-send/verification.json（相对Change目录）。浏览器验证使用真实组件和合成接口，不代表新增真实模型执行。


## 顶部精简验收调整（2026-09-11）

Chat移除顶部空间工具栏和项目连接栏；会话标题行仅承接原展开/收起按钮，历史和新建动作保留。空间和主题通过共享侧边栏菜单切换。当前唯一授权仓库自动选中，首次发送创建会话；多仓库保留输入区选择，无仓库仍显示真实不可用原因，不硬编码仓库路径或绕过权限。消息区填满剩余空间、输入卡居中，切换轨迹不丢草稿。


## 会话标题与历史入口返修（2026-09-11）

已创建会话的标题及编辑图标作为重命名入口，复用既有弹窗；空草稿显示“新会话”，首次发送创建后才可改名。删除标题下拉及快速切换弹窗，其他会话统一从历史弹窗选择。移除对话/轨迹栏常驻“个人会话”标签，权限说明保留在历史弹窗：仅本人可查看，同时遵循空间、仓库与关联对象权限。保存成功同步标题及历史，空白禁用保存，失败保留编辑内容，取消不修改。后端权限校验及接口无变化。


### 输入框提示精简验收

输入框正常就绪时不显示常驻执行说明或空提示节点；仅保留服务未就绪、归档、原运行未终止、缺少仓库及发送失败提示。发送按钮在有无提示时均右对齐，权限校验与请求流程不变。
