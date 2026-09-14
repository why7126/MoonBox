---
requirement_id: REQ-0025-chat-workbench
title: Chat 工作台原型拆解与参考契约
owner: product
created_at: 2026-09-08 11:27:56
updated_at: 2026-09-14 00:03:14
---

## 当前交付事实（最终验收回填）

用户确认的单机Compose、SQLite、本地独立备份、本机Codex认证单文件和显式unlimited策略已实际部署到所选项目仓库及moonbox编码空间。用户重新登录后通过真实页面完成两轮发送，分别结算14969/15189 Tokens；刷新保留两轮回复，轮次数量2、互斥及并发占用归零、两轮Diff均为空。证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/target-deployment/account-verification.json及logged-in-acceptance.png。实际源仓库未被模型修改，工作区从已提交树初始化，当前目录未提交改动不会自动导入。

最终需求边界：无用户/空间运营配额；同会话互斥、单机顺序调度、有限结果处理缓冲和容器/协议安全边界保留。聊天和备份不自动过期；主动删除主数据、记录独立删除日志，旧备份物理expire前保持待清理，恢复前重放删除。API不挂载凭证或Docker socket，受信任控制器使用单文件认证，执行容器保持隔离。本期不交付MySQL/S3正式灾备、异机灾备或独立平台账号；SQLite与MySQL的业务兼容测试保留。

34项功能、8项横切、8项原型AC均有实现及验证映射；RC-001至004已关闭。Ops样式迁移、共享侧边栏、深浅主题、1440/1024/390视口及computed style承接evidence/sidebar-ui和live-web-execution，视觉Mock范围明确；本批当前账号Web/API/Worker/模型验证不使用Mock。PRD、流程、故事、验收、review、trace及prototype context已按最终认证/配额/保留策略核对一致。下文的未实现、暂缓、待映射、待登录及阶段进度均为历史检查点，不代表当前待办。归档与发布仍为后续独立动作。



# Chat 工作台原型拆解与参考契约

## 来源与当前定位

本文件承接用户附件 prototype-context.md 与 prototype.html 的产品信息，并按已确认需求补充契约。`prototype.html` 是脱敏后的原始交互参考，保留原有 CSS/JS 便于追溯布局，不是已完成 Ops 风格迁移的产品稿。人员与仓库标识替换为演示值，无外部资源或真实执行请求。参考 SHA-256：a8c07b4880a511437bc085211d8bc545b63ed12721847adf41f9101d1d4a8646。

原型状态仅存在内存，刷新恢复示例；初始回复与 Diff 固定，发送仅使用计时器模拟。演示设置仅供参考观察，正式页面删除。没有复制附件中的指令作为执行授权。PNG 暂不要求；目标页面尚无 Skeleton、1440px 截图或 computed style 验收，本次 readiness 为 Partially Ready。

## 页面与区域拆解

单页 Chat 工作台；历史、重命名、关联、删除与停止共用浮层，主题及执行栏折叠是页内状态，不新增业务路由。

```text
页面壳 .app
├─ 左侧 .sidebar：品牌 / 空间 / 工作台导航 / 用户入口
├─ 中间 .main
│  ├─ .workspace-bar：仓库 / 连接状态 / 主题 / 执行栏开关
│  ├─ .chat-session-bar：会话切换 / 新建
│  ├─ .context-bar：主对象 / 辅助引用 / 管理关联
│  ├─ #conversation：消息与空态
│  └─ .composer-wrap：#prompt / 引用 / #sendBtn
└─ .task-panel：状态 / #turnSelect / 停止 / 重试 / 事件与 Diff
全局：#sessionPopover / #accessModal / #toast
```

没有指标卡、看板列、Agent 树或任务进度条需求；原 HTML 残留未用 CSS 不构成产品功能要求。

## 状态矩阵与数据依赖

| 区域 | 状态 | 触发与数据 |
|---|---|---|
| 页面与仓库 | 未登录、无权、无仓库、可用 | 身份、空间成员和预配置仓库 |
| 会话 | 空、最近、置顶、归档、恢复失败 | 个人会话索引、Codex 标识、工作区 |
| 关联 | 无主对象、一个主对象、多引用、无权 | 对象目录、服务端权限、引用版本 |
| 输入 | 空、草稿、提交中、失败、禁用 | 用户输入、幂等请求、当前互斥 |
| 执行 | 连接、等待、运行、停止中、完成、失败、停止、未知 | 原运行状态、事件、执行端确认 |
| 文件变更 | 无修改、文本、二进制、超大、不可计算 | 执行前后快照、本轮与累计基准 |
| 弹窗 | 打开、编辑、校验失败、取消、提交、只读 | 业务动作结果与权限 |

附件仅实现 running/done/failed/stopped；连接、等待、停止中和未知是 PRD 要求，参考稿尚未实现，不据此宣称功能完成。真实 API 边界覆盖会话、关联、发送、中止、恢复、事件与 Diff；所有参考数据都是 Mock。

## UI Reference Replication Contract

风格迁移：用户确认与 PRD 决定语义；视觉用项目 Ops Token、品牌和共享组件；附件决定区域关系及动作路径。深浅主题强调色分别为 #D8AC55 / #B9832E，背景分别 #0A0D14 / #F4F6FA，圆角按当前组件规范控制在 8px 内。字体使用 Inter + Noto Sans SC，辅助编号使用等宽字体。导航复用既有需求中心密度与用户菜单，不以附件四项导航缩减产品菜单。

## Selector 与动作按钮矩阵种子

目标 data-testid 是候选合同名，尚未创建产品组件。所有证据列均为后续验收计划。

| 动作/组件 | modal 类型 | 参考 selector | 目标候选 data-testid | 状态 | 验收证据计划 |
|---|---|---|---|---|---|
| 切换会话 | popover | #sessionPicker / #sessionPopover | chat-session-picker / chat-session-popover | open/search/empty/selected | 截图、焦点、外部点击 |
| 历史管理 | dialog | #historyBtn / #accessModal | chat-history-trigger / chat-history-dialog | filter/empty/archived | 截图、查询与权限断言 |
| 新建 | N/A | #newSessionBtn | chat-new-session | loading/error/empty | 新建唯一性与空态 |
| 重命名 | dialog | 动态历史行按钮 / #accessModal | chat-rename-trigger / chat-rename-dialog | dirty/invalid/submitting | 输入、取消、toast |
| 删除 | confirm | 动态历史行按钮 / #accessModal | chat-delete-trigger / chat-delete-confirm | disabled/open/cancel/error | 未处理变更与竞争断言 |
| 归档/恢复 | N/A | 动态历史行按钮 | chat-archive / chat-restore | disabled/loading/readonly | 状态及权限断言 |
| 关联管理/引用 | dialog | #manageRelations / #contextBtn / #accessModal | chat-relations-trigger / chat-relations-dialog | empty/multiple/forbidden | 主对象约束、快照断言 |
| 发送 | N/A | #prompt / #sendBtn | chat-prompt / chat-send | draft/disabled/sending | 幂等、失败草稿 |
| 停止当前运行 | confirm | #stopBtn / #accessModal | chat-stop-current / chat-stop-confirm | running/stopping/unknown | 终态事件与截图 |
| 重试 | N/A | #retryBtn | chat-retry | allowed/disabled/unknown | 原运行终止、快照断言 |
| 轮次选择 | select | #turnSelect | chat-turn-select | empty/history/current | 选历史仍可停当前运行 |
| 事件与 Diff | inline-expanded | #executionBody / [data-tab] | chat-execution-events / chat-diff | empty/text/large/error | 真实事件、双轮 Diff |
| 执行栏折叠/主题 | N/A | #panelBtn / #themeBtn | chat-panel-toggle / chat-theme-toggle | collapsed/dark/light | 窄视口、深浅截图 |
| 关闭/确认/取消 | dialog 共用 | #closeModal / #modalActions | chat-modal-close / chat-modal-submit / chat-modal-cancel | focus/loading/error | Esc、Tab、焦点回归 |

按钮、Modal、Confirm、Popover、Toast 按动作族复用；不逐个按钮建立互不一致组件。关闭契约：会话轻量选择即时应用并关闭；关联和重命名采用提交/取消，不静默保存未提交输入。危险确认取消不改变运行。浮层外部关闭需通过 capture 阶段或等价机制覆盖内部 stopPropagation；对有草稿的编辑弹窗明确保留/丢弃语义后验收。

## 响应式与 1440px 焦点

原 CSS 桌面栅格为 236px / minmax(560px,1fr) / 398px；1280px 以下左栏 210px，右栏变固定浮层。它只是参考尺寸，目标左侧复用既有 Ops 导航。1440×900 检查三栏边界、输入区可见、消息与详情独立滚动、当前停止入口及弹窗不遮挡；1024×600 验证低视口滚动，390×844 检查窄屏没有不可达输入和溢出。目标窄屏可把详情折叠为抽屉，具体宽度在 Skeleton 定稿，不将原 CSS 直接视为移动端通过。

## 样式采样与分批证据

| 批次 | selector 范围 | 属性/证据 |
|---|---|---|
| 1 页面壳 | .app/.sidebar/.main/.task-panel | width/height/grid/gap/overflow/position；1440 深浅首屏 |
| 2 会话与关联 | #sessionPopover/#accessModal/.context-bar | font-family/font-size/line-height/padding/border/background/z-index；各弹窗与空态 |
| 3 输入与反馈 | #prompt/#sendBtn/#toast | height/color/radius/position；禁用、错误、无布局位移 |
| 4 执行与 Diff | #turnSelect/#executionBody/#stopBtn | overflow/font-size/width；历史/当前运行与真实状态 |
| 5 窄视口与键盘 | 页面、所有浮层 | scroll/max-height/focus；低视口、Tab/Esc、外部关闭 |

正式实现将参考 selector 映射至目标候选 selector，并记录期望、实际、结论及截图来源。原型静态拆解已完成；所有批次截图、目标 computed style 和最终一致性均 pending。

## 原型与 PRD 的已知差异

1. stopTurn 立即结束：目标等待执行端确认，增加停止中和未知。
2. 模拟断连直接失败：目标先查询旧运行，禁止立即再次写入。
3. 删除检查历史文件数：目标检查当前未处理代码变更。
4. refs 只保存编号：目标受控版本/内容快照与重验权限。
5. 停止依赖选中轮次：目标独立停止当前运行。
6. 原稿紫色、大圆角及残余任务样式：目标 Ops 组件与 FR 边界。

这些差异是实施合同输入，未在参考 HTML 中伪装成已实现。

## 评审后补充状态

新增预算不足、并发受限、容量已满与清理提示状态，来源于服务端额度/容量检查。平台统一认证，不增加个人账号绑定 UI；容量不足保留历史查看/清理能力，归档不触发自动到期删除。对应 AC-031–034。参考 HTML 未模拟这些新增状态，目标组件及视觉验证仍 pending。

## Change设计承接

add-chat-workbench-codex 保留需求中心旧AI抽屉，新增显式入口携带授权对象进入/chat，不自动迁移模拟消息或运行代码。撤权限制覆盖历史快照、回复、Diff及执行端旧上下文；无法可靠剔除时禁止原线程续用并引导新建干净会话。目标UI、接口及验证以该Change design和tasks承接。


## Skeleton首轮证据

目标/chat已实现第一批骨架。1440深浅、1024低视口、390窄屏截图和样式见 openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/ui/。无业务API或模型调用，业务按钮禁用。此前“尚无Skeleton”描述为生成阶段快照；完整交互、真实执行与最终一致性仍pending。


2026-09-08增量：目标页面已接鉴权会话API，动作族由SessionDialogs/ChatDialog统一实现，历史/重命名/快速切换三档视口证据位于Change evidence/session-ui。执行详情支持轮次、事件、停止与可信Diff原始数据读取，消息安全纯文本展示。关联Dialog、文件级Diff和可发送状态仍未完成；参考稿不变，未把合成数据写入生产。


## 当前实现边界（2026-09-08）

已实现会话/关联管理、不可变引用快照及撤权拦截、消息和本轮/累计Diff、停止确认/显式重试、内部预留结算、治理只读策略、请求/行为/运行观测与当前代码保护删除。执行副本和备份清理分别记录pending，不代表已经完成物理删除。

用户选择先开发与隔离验证，暂不配置正式限额和删除时限；平台专用认证与正式仓库绑定待提供。当前发送/重试保持关闭，有历史会话删除也不能绕过配置门禁。真实本机双轮与合成容器隔离是两类独立证据，不合并宣称平台端到端验收通过。完整映射见acceptance.md和Change trace。

## 共享侧边栏一致性（2026-09-08）

侧边栏局部一致性以需求中心为事实源，复用 src/web/src/components/workbench/WorkbenchSidebar.tsx；账号/空间动作和主题偏好共享。两页桌面224px、折叠72px，窄屏默认折叠并允许展开。对应 selector 为 .rc-sidebar/.rc-brand/.rc-nav-group-label/.rc-nav-item/.rc-nav-icon/.rc-user-trigger；动作与浮层矩阵见 Change design.md“共享侧边栏补充合同”。旧附件只保留交互来源，不将其四项导航或独立品牌当作产品实现。


本机隔离验收补充（2026-09-08）：使用真实登录和受控仓库完成Web发送、双轮修改、刷新恢复、worker重启及真实停止。刷新通过不透明会话标识重新鉴权恢复，运行终态后同步解除输入区旧活动状态；缺失用量显示待核实且不零结算。临时服务、认证副本、仓库及数据库已清理。此为用户授权的测试部署，不替代正式共享平台认证或正式限额/删除时限决策。证据与边界统一见acceptance.md「五步隔离执行闭环」及Change evidence/live-web-execution/verification.json。


### 异常恢复与清理证据更新（2026-09-09）

承接本地凭证＋受控仓库方案。新增进程组故障回收、清理失败重试/当前权限复核、真实线程历史删除及独立镜像重启证据；未知运行保持互斥，未知用量保持预留。代码和凭证不随线程历史删除。实际备份与正式平台认证、限额、删除时限仍未闭环，不改变页面布局、动作语义或正式发送门禁。详细结果见本REQ acceptance.md及Change trace.md“异常恢复、清理与部署补验”；整体未进入applied或归档。


### 推荐组合落地同步（2026-09-09）

用户选择的当前验证方案已实现：SQLite一致性备份与独立删除日志，恢复旧备份前重放删除；每会话独立Linux容器接入worker，真实双轮/恢复/停止及Diff、用量结算通过。空会话同样记录删除；代码和审计独立保留，旧备份正文须实际清理，恢复过滤不代表物理删除。正式方向保留为独立对象存储备份＋会话容器，S3/MySQL恢复、共享认证、正式额度和时限仍未开启。页面布局及动作合同不变；新证据见本REQ acceptance.md与Change trace.md，整体状态仍in_progress。


### 部署脚本接入补充（2026-09-09）

本批只增加部署脚本入口与私有测试控制器，UI组件、布局和交互合同不变。--chat-test测试页面取自本次Web镜像构建，默认回环18121；沿用现有视觉验收证据，无新一轮视觉变更。


### 终态并发释放补充（2026-09-09）

本批无UI组件/样式变化。真实网页已验证停止确认弹窗、停止后可发送和刷新恢复；并发修复仅影响后端资源账本，原视觉合同保持。新增截图见Change evidence/concurrency-release/。


### 受控范围收口（2026-09-09）

本批无UI结构/样式变化；输入执行区既有实现的22项前端回归和真实双标签页交互通过，任务4.3完成。原型001/002/003/005/006/007/008与横切8项已有证据，原型004整体归档一致性仍待正式范围完成。


### 单机常驻方案确认（2026-09-09）

用户已明确采用单机 Docker Compose、SQLite、本地独立备份、本机 Codex 认证单文件，取消用户/空间额度、并发和存储运营上限。显式 unlimited 与缺失配置区分，仍计量结算；同会话互斥、权限、未知态和单轮结果处理技术边界保留。历史及备份不自动过期；主动删除仍记录和跟踪主存储/执行线程/备份，副本无固定删除截止时间，旧备份物理移除前保持待清理。单机控制器顺序处理持久队列，容量不足不绕过隔离。正式仓库路径及空间映射尚待提供，当前不宣称正式服务已开放。方案细节以 docs/02-deployment.md 的单机常驻章节为准，替代此前“认证、限额和期限尚未决定”的当前态描述；历史证据保留。


实际部署续接（2026-09-09）：用户指定的项目仓库和唯一moonbox编码空间已映射，常驻API/Worker及本地独立备份已部署健康，整体28/29。当前只待用户重新登录完成该账号发送/刷新验收及最终同步，原“仓库映射待提供”已解除。详见acceptance.md实际单机部署检查点。

## 2026-09-10 执行展示返修

连续相邻、同消息和同执行轮次的文字事件归并显示；工具/状态/消息身份变化及序号缺口保留边界。原始事件默认折叠，保留最近1000条窗口说明。所选轮次当前状态单独展示，时间线状态明确标为历史。安全Markdown新增表格（表头、对齐、转义管道、行内代码、空单元格），窄屏在表格内滚动，保持HTML/图片/危险链接不可执行。旧事件缺少消息身份时仅按连续区段归并，不伪造缺失边界。

本次只改变Web展示，事件持久化、SSE、API、DB、鉴权、停止/重试、Token计量不变，无需迁移或客户端生成。文件路径链接不在本次范围。


## 2026-09-11 验收返修：Harness 对话与轨迹

以本机 DeepSeek Harness 的对话/轨迹结构为新参考，保持 MoonBox 共享导航与空间/对象权限。对话为右侧用户气泡、无边框助手正文、紧凑自适应输入、消息复制与本轮轨迹入口；Enter发送、Shift+Enter换行、中文输入法不误发送。活动轮次显示过程摘要，失败附着轮次。消息历史加载更早页，滚动阅读不强制跳底；轨迹标签隐藏保留阅读状态。

轨迹包含按原标识配对的工具节点、搜索、内容折叠、事件概览与可调整宽度的详情。详情提供概述、参数、结果、Schema可用性及计时；窄屏上下排列。现有停止确认、原轮次重试、引用快照及Diff保留。事件每窗口最多1000条，可以读取后续窗口或从头查看；窗口边界缺少工具开始记录时不伪造开始时间。旧数据未采集字段明确显示不可用。耗时概览按对数缩放并显示说明，不冒充模型请求计时。

新增工具详情仅存于本人会话事件JSON：白名单参数、截断输出、退出码、状态、记录时间和耗时来源。先脱敏再限长；不新增表/接口/认证/部署范围。平台日志与审计不记录这些正文。明确final_answer可用时最终消息使用最终正文，其余过程留在轨迹；旧协议保持兼容。Schema、模型请求层级、缓存率、内部推理不编造，也不增加模型切换、附件、分支入口。

验证：前端31项聚焦回归通过；后端工具/权限/结算聚焦回归与构建记录见本批最终验证摘要。真实组件+合成API在1440桌面和390窄屏深浅主题观察；样式与无横向溢出记录于 openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/harness-trajectory/verification.json。未宣称与参考逐像素相同，原始参考截图含私人路径而未落盘。新一轮真实模型执行与合成视觉验收明确区分。


## 首次输入冲突处理（2026-09-11）

原prototype.html保留历史参考；本次用户授权覆盖前置新建弹窗，当前契约如下：

进入工作台即可编写本地草稿，首次发送自动创建个人会话再提交轮次；单仓库自动选择，多仓库在输入区选择。新建会话只打开新草稿，无前置弹窗、无空会话写入。服务未就绪仍可编辑，发送继续校验认证、仓库及执行能力。

创建和发送分别使用稳定请求标识；创建响应丢失重放得到同一会话，创建成功后发送失败复用已有会话与轮次请求，连续点击不重复提交。创建幂等按用户隔离并重验权限；参数冲突拒绝、删除记录不复活。草稿仅内存驻留并按空间/实例隔离，刷新不保证保存未发送内容。首次未关联会话仍遵循原只读策略；需要写入时按既有流程关联对象与Change。

selector：chat-new-session、chat-draft-repository、chat-prompt、chat-send；新建及仓库选择无需modal，历史/重命名/归档/删除动作族保留。


## 顶部精简验收调整（2026-09-11）

Chat移除顶部空间工具栏和项目连接栏；会话标题行仅承接原展开/收起按钮，历史和新建动作保留。空间和主题通过共享侧边栏菜单切换。当前唯一授权仓库自动选中，首次发送创建会话；多仓库保留输入区选择，无仓库仍显示真实不可用原因，不硬编码仓库路径或绕过权限。消息区填满剩余空间、输入卡居中，切换轨迹不丢草稿。


## 会话标题与历史入口返修（2026-09-11）

已创建会话的标题及编辑图标作为重命名入口，复用既有弹窗；空草稿显示“新会话”，首次发送创建后才可改名。删除标题下拉及快速切换弹窗，其他会话统一从历史弹窗选择。移除对话/轨迹栏常驻“个人会话”标签，权限说明保留在历史弹窗：仅本人可查看，同时遵循空间、仓库与关联对象权限。保存成功同步标题及历史，空白禁用保存，失败保留编辑内容，取消不修改。后端权限校验及接口无变化。


### 输入框提示精简验收

输入框正常就绪时不显示常驻执行说明或空提示节点；仅保留服务未就绪、归档、原运行未终止、缺少仓库及发送失败提示。发送按钮在有无提示时均右对齐，权限校验与请求流程不变。
