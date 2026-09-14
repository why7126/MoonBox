---
requirement_id: REQ-0026-requirement-center-standalone-change-cards
title: Change 可见性与关联追溯验收
owner: product
created_at: 2026-09-12 21:17:00
updated_at: 2026-09-14 09:25:34
acceptance_status: passed
---

# 验收清单

实施自验、隔离真实API和浏览器观察已执行并通过；2026-09-14 用户执行 `/opsx-archive REQ-0026`，作为本轮业务验收确认来源。HTML 为合成原型，不是权限或 API 验收证据。

## 功能 AC

- [x] AC-001 **独立卡片**（FR-001、FR-002）：构造一个无 Issue 来源的活动 Change，分别设置 提议态/进行态/验收态，读取真实项目快照后只出现一张独立卡片，ID、状态、tasks 与源文件一致；无 Sprint 不阻止展示。
- [x] AC-002 **两项卡片调整**（FR-003）：与当前 renderIssueCard 对照，仅在 REQ/BUG ID 下方新增 Change ID 行，computed font-size 与原 ID 相等（当前 10.5px）；标题文本改为同一 Change 的中文标题，仍使用原 .rc-card-title 样式与点击行为。其他标签、文档组、进度和 footer 保持；无 Change 完全保持原卡片，多关联歧义按 FR-003 降级。
- [x] AC-003 **来源和异常**（FR-001、FR-004、FR-005）：覆盖唯一归档、活动与归档同 ID、活动缺文档、多份归档、关联目标缺失、冲突来源、未知状态及 registry 不可解析；活动优先且不读旧副本，多归档禁用含糊入口，未知项可达且计数；注册表失败不把全部 Change 当独立。
- [x] AC-004 **权限与去重**（FR-001、FR-008）：两个成员拥有不同对象权限：隐藏 Issue 的 Change 不变为独立卡片；独立 Change 自身限制有效；跨项目同 ID、直接请求文档与卡片入口结果一致，无受限身份、标题或计数泄漏。
- [x] AC-005 **统计搜索**（FR-007）：全部、REQ、BUG、独立 Change、归档开关及搜索组合下，总数等于三类卡片数之和，各阶段与异常数之和等于总数；搜索关联 Change ID返回所属卡片，不返回重复独立卡片；无结果空态可恢复。
- [x] AC-006 **文档与进度归属**（FR-005、FR-006）：两个关联 Change 的任务进度分别展示，100% 不推断完成；缺 tasks 显示未知；Issue trace 与 Change trace 入口可区分；proposal 缺失不妨碍其他合法文档，specs 聚合保留来源，Sprint 核对 iteration 与成员关系。
- [x] AC-007 **刷新一致性**（FR-009）：外部新增、建立关联、归档后按既有刷新目标显示真实结果；半写入期间提示待同步，保留既有筛选与阅读状态；项目切换迟到响应不覆盖新项目，无全局或演示数据回退。
- [x] AC-008 **视觉与可达性**（FR-003、FR-006）：在 1440px 与 390px、深浅主题下检查首屏、长 ID、新增 ID 行、文档抽屉及异常集合；Tab/Enter/Esc可操作，完整 ID不依赖悬停，正文无页面级横向溢出，横向看板滚动可控。
- [x] AC-009 **观测与契约**（FR-008、FR-009）：在真实 API 中验证成功和拒绝读取的 request_id、安全日志摘要及行为关联字段；非法观测字段不成为授权凭据；采集失败不阻断读取；日志不含文档全文、凭证和主机路径。同步 API 索引、OpenAPI/客户端与后端响应契约。
- [x] AC-010 **边界防护**（FR-008）：覆盖过期或无成员空间、冻结空间只读、只读成员、路径穿越、符号链接越界、短 ID歧义及多来源权限；文档入口不能提交写入；新增阶段动作另按 AC-ACTION 验收，既有 Issue 门禁不变。
- [x] AC-011 **既有交互回归**（FR-003、FR-006）：新增 ID 是可选择复制的文本，不新增按钮或浮层；当前标题、文档、进度及 footer 动作的点击、权限和退出行为不变。长 ID 换行不缩小字号且不溢出。

## 原型驱动 UI AC

- [x] AC-PROTOTYPE-001：核对 prototype/web/context.md 的页面、组件、状态、触发、数据、断点和验收焦点与 PRD 一致；本轮按钮拆解已完成，新动作Skeleton及确认已收口阶段补充。
- [x] AC-PROTOTYPE-002：后续 Change 先建立 UI Skeleton、selector 映射和动作矩阵，完成首轮 1440px 截图确认后再实现细节。
- [x] AC-PROTOTYPE-003：实现阶段保留 1440px 深浅主题与关键交互截图、390px 溢出检查及 computed style 记录，标注版本、视口、工具、结果；原型截图不充当生产通过证据。
- [x] AC-PROTOTYPE-004：归档前逐项核对 PRD、用户故事、业务流程、验收、trace 与 prototype；返修后重取证，旧截图不沿用为通过依据。
- [x] AC-PROTOTYPE-005：按 context.md 的局部一致契约复核现有页面选择器、动作族及样式采样；既有权限、项目切换及 Issue 动作保持有效。

## 横切 AC（knowledge-base）

本 REQ 为前台看板，不命中 admin-list、admin-form、admin-modal、media-upload 四个标签；相应管理端/上传 gate 为 N/A。主动承接以下同域经验，不套用管理端分页、表单或上传要求。

来源：docs/knowledge-base/best-practices/prototype-driven-ui-gate.md 与 docs/knowledge-base/retrospectives/sprint-003-retrospective.md。

- [x] AC-XCUT-001：既有抽屉阅读、新增 ID 行、空态、主题及溢出提供 computed style 与真实交互证据，明确 Mock/API 边界；截图与实现版本对应。
- [x] AC-XCUT-002：关闭验收前区分历史过程记录与最终结果，逐一复核 UI 返修涉及的 REQ 子文档，不以 tasks 勾选或原型演示替代真实验收。

## 证据与执行策略

功能/API 合成回归覆盖 AC-001 至 AC-007、AC-009、AC-010；真实项目手动观察覆盖创建关联、状态变更、归档刷新和多成员隔离。真实浏览器覆盖 AC-008、AC-011 与原型 AC。用专用测试项目和无敏感数据的样本，不依赖默认管理员密码。

实现后证据写入对应 Change 的 evidence 目录并由 trace 引用，记录操作者、版本、视口、结果；既有 Change 已 验收态，本轮新增动作尚未同步至 OpenSpec。本命令只校验文档映射与原型结构，不勾选业务通过项。

## UI Reference Replication Contract 种子

保真模式、事实源顺序、组件清单、动作矩阵、selector 候选、样式采样和分批验收见 prototype/web/context.md。采用局部一致，既有页面壳保持，新增 Change 信息区以 PRD 为业务事实源。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-14 09:25:34
accepted_by: workflow-sync
source_change: add-requirement-center-change-visibility
source_sprint: sprint-005
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 本轮用户反馈对照

| 用户要求 | 原型旧偏差（源码证据） | 修订与检查 |
|---|---|---|
| REQ ID 下新增同字号 Change ID | 旧 HTML 的 relations 在标题后，change-id 为 12px | 移到 rc-card-top 后；与原 ID 共用样式来源，预期 10.5px |
| 标题换成 Change 中文标题 | 旧 card(c) 始终渲染 c.title | 对照原型只替换 .rc-card-title 文本，保留 13.5px 样式 |
| 当前卡片基础上修改 | 旧 HTML 自建卡片、关联列表与抽屉 | 复用当前 globals.css 与当前卡片 DOM 顺序；删除自建关联交互 |

历史源码对照已补充真实浏览器computed style与最终截图；实测原ID/新增ID均10.5px，标题13.5px，证据见关联Change verification.md。

## 实施自验与人工验收边界

以上勾选代表实施自验、隔离真实观察与归档验收确认通过。详细证据：openspec/archive/2026-09-14-add-requirement-center-change-visibility/verification.md。18102本地容器未部署本轮源码，运行容器更新不作为本次归档通过条件。

## 2026-09-13 验收返修约定

独立Change使用主题info蓝色左边框，REQ金色、BUG红色保持。移除九阶段之外的“状态待核实”卡片区；unknown对象仅通过默认收起的数据异常入口查看只读ID/说明，不计入页面业务统计，接口原始unknown和授权保持兼容。搜索/类型过滤同时约束诊断集合，零正常对象时业务总数为0而诊断仍可达。重复归档已核对为不同内容复用ID，保留冲突事实，不按日期任取版本、不删除历史。

验收覆盖1440/390深浅主题、九阶段DOM、三类边框颜色、收起/展开键盘操作、仅异常筛选及正常文档入口；证据见Change返修记录和logs/req0026-modify/。

## 已完成独立变更的迭代归属补充

独立 Change 的 Sprint 标签优先使用合法 iteration 并核对 Sprint changes 成员关系；iteration 缺失、null 或空串时反查活动及归档 Sprint，仅唯一 Sprint ID 可关联。多个成员关系不猜测并提示待核实；显式错误不被反查覆盖。同 ID 活动 Sprint 优先，不从归档补活动缺口。标签不依赖 sprint.md 存在，文档入口仍要求文件可读。

## 新增阶段动作 AC（本轮自验完成）

- [x] AC-ACTION-001：准备开发态、研发中、验收中使用阶段矩阵对应按钮；已完成与未知状态不新增主按钮，REQ/BUG行为无回归。
- [x] AC-ACTION-002：按钮位置、文案、弹窗族和进度阅读复用当前实现；Change 使用完整自身ID，关联Issue仍使用完整REQ/BUG身份。
- [x] AC-ACTION-003：无读取权限不泄漏；只读/冻结不能写，仍可查看授权进度；缺Sprint、任务、测试或人工验收证据时按动作显示具体阻塞原因。
- [x] AC-ACTION-004：真实能力未接入禁用并说明，不发送虚假执行请求；Demo标记清楚、不写真实数据；真实执行需服务端重新验证权限与前置条件。
- [x] AC-ACTION-005：取消/关闭/键盘退出有效；提交防重入、失败不丢上下文、成功刷新稳定快照；项目切换不串对象。
- [x] AC-ACTION-006：1440/390深浅主题及可执行/禁用/加载/失败状态截图，采样footer按钮和弹窗computed style；旧截图不作为新动作通过依据。
- [x] AC-XCUT-003：按动作族一次覆盖按钮→弹窗→状态→证据矩阵，明确Mock与真实API边界，防止逐按钮补漏（来源Sprint-003复盘）。

## 阶段按钮实施与证据

阶段按钮已接入：准备开发态开始开发、研发中查看进度、验收中完成/归档，已完成与未知无阶段主按钮。后端沿用action字段提供完整Change命令和禁用原因；前端同样保守禁用未接入执行能力，不能由响应中伪造action解除门禁。冻结空间返回只读原因；进度按读取权限打开当前tasks，只读文档不允许编辑。无tasks保留现有缺失反馈。

当前独立Change没有真实开发/归档执行服务，因此相关按钮禁用；不开放Demo模拟写入或伪造成功。矩阵中开发/归档modal、提交防重入/成功刷新在本轮不可执行分支为N/A，原因是已批准的能力门禁禁止进入执行分支；不以禁用按钮宣称真实开发或归档已实现。既有REQ/BUG弹窗族与执行交互保持，78项前端回归覆盖其行为。进度复用.rc-drawer、关闭按钮和Escape退出。

用户已确认1440px Skeleton布局；openspec/archive/2026-09-14-add-requirement-center-change-visibility/evidence/actions/skeleton-dark-1440.png与skeleton-light-1440.png为首轮证据。最终1440/390深浅主题4组截图、进度抽屉截图及computed style见openspec/archive/2026-09-14-add-requirement-center-change-visibility/evidence/actions/，真实浏览器组件+合成API夹具，非部署观察。仓库实际索引只读核验48个独立对象、2个有阶段动作、0个写动作开放。

验证：后端93项（含HTTP权限、冻结只读、日志拒绝与采集失败）、前端78项、TypeScript、浏览器4组通过。未部署、未进行真实开发/归档执行。接口schema未变，无需重新生成OpenAPI/Orval；API行为说明已同步。DB、部署、对象存储、安全策略不变。

## 固定禁用提示返修结论

本节替代上一轮独立Change一律禁用的结论。后端复用REQ/BUG阶段必需文档与非空门禁，并核对唯一Sprint；缺失/空文档/只读才返回相应原因，不再固定生成测试核对或能力未接入提示。文档存在不代表测试执行通过；前端复用已有testProgress/manualAcceptanceCount判断，数据不存在不伪造检查结论。

独立Change与REQ/BUG进入同一动作处理器：研发中读取tasks；真实模式中当前未支持的开发/归档动作点击后显示现有统一能力提示，不执行写入；Demo沿用现有弹窗和模拟流转，不接入真实执行。取消、提交防重入和刷新行为复用当前组件，未新增服务或权限。

验证：后端94项、前端79项、TypeScript通过；1440/390深浅主题4组真实组件合成API浏览器验收通过，截图和computed style位于evidence/action-gates/。非部署观察，未执行真实开发/归档。保留现有权限和真实能力限制；新证据替代旧固定禁用截图。

## 独立交付验收来源返修（当前结论）

验收中不再固定要求acceptance.md：优先校验trace.acceptance_refs声明的Change内相对Markdown路径；显式引用无效、缺失或为空返回具体待核实原因，不回退。未声明时查现有acceptance.md、verification.md，再识别trace中非空“验证记录/验收记录/验证结果/验收结果”章节。不得跨Change或通过绝对路径、父路径、符号链接越界读取。没有证据来源提示待核实，不补建文件；本机制定位证据，不自动判断验收通过，验收态和tasks全勾均不代替验收。

真实仓库样本standardize-sprint-default-capacity以trace验证记录作为来源；unify-issue-classification-metadata使用acceptance.md，两者当前源码均无来源阻塞。后端95项回归通过，包含显式引用、缺失、空源、越界与历史trace来源；浏览器复用真实组件+合成API在1440/390深浅主题验收，证据evidence/action-gates，非部署验收。

运行页面核对：用户地址localhost:18102对应moonbox-web，加载index-y8JI4bjc.js，其中无旧能力提示；moonbox-backend镜像动作函数也无旧提示，但仍采用上一版固定acceptance.md清单，尚未部署本次解析。未对运行容器做重建或重启，截图旧提示的实际响应来源仍未取得，不断言缓存根因。

REQ主文档、故事、流程、验收、trace、原型context及HTML已核对同步；capture/review保留历史，不需改写。API既有action字段形状不变，无需OpenAPI/Orval生成；product_data_collection_observability为applicable，affected_layers为api，复用请求日志/授权，验证无越界；无新增DB、部署配置、存储、保留周期或Task Trace。

## 中文标题来源返修

标题来源保留既有优先级：trace显式中文标题或标题字段、proposal/design有效业务标题，最后回退trace正文一级业务标题；过滤追溯、背景与动机、验证记录、验收结果等通用章节名，全部缺失才显示完整Change ID。

证据：change_index.py 与 test_change_visibility.py；浏览器 title-fallback 四组1440/390深浅主题截图及styles.json。使用合成API验证组件，未部署18102；归档确认来源为 2026-09-14 用户执行 `/opsx-archive REQ-0026`。
