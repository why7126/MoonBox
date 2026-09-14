---
note: workflow-sync — 8/8 Change 已 archive；0 applied；待人工 sign-off
sprint_id: sprint-005
status: completed
lifecycle_stage: archive
created_at: 2026-09-11 08:59:42
updated_at: 2026-09-14 09:25:00
---

# sprint-005 验收报告

## 当前结论

8 个 Change 均已归档，Sprint close readiness、env ignore 与 stale scan 均通过；Sprint 验收关闭通过。本轮未自动执行生产部署、数据库升级、Git 提交或推送。AI Usage Snapshot 自动发现未取得可归因 token 事件，关闭报告保留 estimated_fallback 警告。

## 验收范围

REQ-0022-local-project-import-product-iteration：16条功能、3条横切、6条原型AC；review RC-001至004逐项收口。

## 证据要求

真实浏览器、API、worker和文件证据与合成回归分开；覆盖未提交修改、授权、冲突、幂等、失败恢复、自动刷新耗时及原型视觉门禁。数据观测按REQ声明及AC-016回填，apply与本轮返修证据见关联Change trace。


## REQ-0022 看板返修

注册对象38（REQ25/BUG13），34完成、4验收中，阻塞0/漂移0；需求中心独立连接栏已移除。后端35条事实源、归档只读与验收缺项回归通过；前端初次167测试、最终聚焦65测试及TypeScript检查和1440深浅/390视觉验收通过。证据：`openspec/archive/2026-09-14-add-local-project-governance-loop/evidence/ui/modify-board-styles.json`及同目录截图。浏览器为合成HTTP，真实部署复验不在本轮通过声明中。


## 首屏加载返修

需求中心首屏改为原位骨架，加载期间不显示假零值和空态，不新增面板推低看板。后台刷新保留已有内容。验收使用延迟合成HTTP及1440深浅/390布局坐标证据，见Change evidence/ui/loading-*；未切换当前业务部署。


## trace 归属返修

需求中心所有卡片仅提供所属REQ/BUG的trace.md单入口，保持只读、缺失不回退；此前双入口方案已撤销。REQ-0022 trace最新摘要前置，历史记录保留。证据见Change evidence/ui/trace-source-*；无API schema或数据库迁移，未切换业务部署。


### REQ-0022 任务入口返修

卡片研发、测试、人工验收入口统一打开关联 tasks.md 的完整 Markdown 文档。加载完成后优先定位匹配章节，其次定位匹配任务并高亮、聚焦；不打开独立进度面板。缺少关联时提示未关联 tasks.md；文件不存在或已移动时提示读取目标缺失；章节或任务缺失时保留完整文档并提示未找到目标，不以计数、历史返修记录或其他文档伪造目标。普通 tasks.md 链接从顶部打开，既有编辑与勾选权限不变。

验证证据：关联 Change evidence/ui/tasks-navigation-*；本地源码与合成 HTTP，不声明当前部署已切换。


任务入口返修验证结果：本轮最终前端回归67项通过，TypeScript检查通过；浏览器24个生产组件场景通过，覆盖1440px深浅主题、390px、章节优先、任务回退、缺文件、缺章节、普通入口无定位；同步原型4个交互验证通过。视觉与 computed style 证据见 evidence/ui/tasks-navigation-*。OpenSpec strict、中文、目录、Sprint scope、diff检查通过。后端未改变，本轮未重跑后端测试。

## BUG-0014 新增修复验收范围

BUG-0014-requirement-center-capture-not-persisted 已纳入，状态迭代内，关联fix-requirement-center-capture-persistence已验收态；本轮回归和隔离真实观察结果见下方Capture验收。AC-001至010覆盖REQ/BUG持久化、描述保留、刷新、并发、失败恢复、权限与观测。根因门禁5条证据通过仅代表缺陷确认；其他范围的通过结果不适用于此BUG。验收事实源：issues/bugs/review/BUG-0014-requirement-center-capture-not-persisted/acceptance.md。


### REQ-0022 Sprint 文档返修

卡片 sprint.md 属于关联 Sprint，通过现有 Issue 文档读取接口按当前授权项目解析。展示、读取和缺失校验共用解析：按关联 ID 查活动目录，仅活动目录不存在时查同 ID 归档目录；活动目录缺文件不读取归档旧副本，不回退 Issue、Change 或其他 Sprint。文件缺失时保留明确提示；读取保持只读，trace.md 仍仅属于当前 REQ/BUG。


Sprint文档返修验证：后端58项通过（聚合、REQ/BUG活动与归档来源、缺失不回退、路径校验、作用域和HTTP接口）；浏览器6个场景通过，覆盖1440深浅与390px正常/缺失态，原型Sprint入口验证通过。证据为evidence/ui/sprint-document-*及样式JSON。OpenSpec strict、中文、目录、Sprint scope与diff检查通过。浏览器为真实仓库聚合/正文与合成HTTP，未切换业务部署。


### 主动作阻塞与消息避让返修

卡片主动作统一使用接口disabled_reason、Issue阻塞和前置文档缺失判断，阻塞提示、按钮原生禁用、title原因与执行前守卫一致；文档仍可阅读，补齐后刷新恢复按钮。Tips位于Agent助手上方并保留安全间距，提高层级；窄屏限制宽度、长词换行，超长消息在受限高度内滚动，不遮挡助手。


主动作与Tips返修最终验证：70项前端回归及TypeScript通过；12个浏览器状态通过（1440深浅、390、320；禁用/补齐恢复、短提示、长中文及无空格长词），提示矩形与Agent至少保留8px间距，无横向越界。原型禁用/恢复与长提示验证通过。证据为evidence/ui/action-toast-*和样式JSON；使用合成HTTP，只证明本地源码UI，未切换业务部署。OpenSpec strict、中文、目录、Sprint scope和diff检查通过。


### 主文档持续展示返修

REQ的requirement.md、BUG的bug.md一旦在所属Issue中生成，即在全部阶段卡片持续显示并固定文档列表首位，包括迭代规划、开发、验收和已完成。读取始终来自所属REQ/BUG当前目录，兼容Issue归档迁移；不读取Change同名文档。未生成不伪造入口，文件删除后按最新快照移除，已打开入口读取缺失明确提示。仅调整展示与排序，保留既有阶段编辑和只读权限。


主文档持续展示最终验证：后端80项、前端79项、TypeScript通过；15个浏览器场景通过（1440深浅/390，活动和归档REQ/BUG首位入口、Issue正文、只读与缺失不回退），原型主文档入口通过。证据为evidence/ui/main-document-*和样式JSON。OpenSpec strict、中文、目录、Sprint scope及diff校验通过。浏览器使用真实仓库聚合和正文配合合成HTTP，本轮未切换业务部署。


### Sprint 文档持续展示

sprint.md在关联Sprint文档出现后于所有阶段卡片持续展示，包括准备开发态、研发中、验收中和已完成；requirement.md/bug.md仍保持首位。复用关联Sprint读取、只读能力、活动/归档解析及缺失不回退。只扩大展示白名单，不将sprint.md新增为其他阶段的必需文档，不改变阻塞与权限判断。


### 卡片文档分组与排序

常驻区按所属requirement.md/bug.md、关联sprint.md、所属trace.md固定排序；阶段区按当前任务优先排序。准备开发态proposal/spec/design/tasks；研发和验收tasks/spec/design/proposal；已完成archive/tasks/spec/design/proposal；已评审review优先，其他沿阶段阅读顺序。两个分组之间仅保留4px间距，无分隔线与额外内边距，组内自然换行，单组无空白占位；来源、权限及原必需文档校验不变。

文档分组返修：前端79项回归及TypeScript通过；15个浏览器场景通过，覆盖1440深浅/390、活动与归档REQ/BUG、文档只读和缺失提示。常驻顺序与阶段顺序由九阶段参数回归验证，单组无分隔、双组细线由相邻组CSS控制；computed style记录组间距、边框及宽度，无组内横向溢出。截图见evidence/ui/document-groups-*，原型同步。OpenSpec严格/中文、目录、Sprint scope与diff检查通过。后端无变更，未重跑；浏览器为真实仓库数据配合合成HTTP，未部署。

紧凑文档区返修：移除分隔线及额外padding，双组margin-top为4px，单组0px。15个浏览器场景通过，1440深浅与390的computed style确认border/padding为0、组间距4px，顺序与只读入口回归通过；原型同步。证据见evidence/ui/document-compact-*。本轮仅CSS与原型样式修改，未重跑TypeScript及单元测试；此前79项结果为历史记录。OpenSpec严格/中文检查通过；未部署，浏览器仍为真实仓库数据配合合成HTTP。


### 文档读取与刷新性能

单次Change文档请求复用同一授权稳定快照的临时目录，避免授权和正文读取重复物化；不引入跨请求缓存，保留项目授权、写入恢复、epoch及绑定版本检查。相同项目的context刷新复用进行中请求，初始加载完成后开始轮询；切换项目及卸载取消旧请求。文档内容/草稿/版本冲突处理与原型布局不变。分段日志仅含服务端request_id、操作名、成功状态及各阶段毫秒耗时，不含文档内容或本机路径。

文档性能与刷新返修验证：后端72项、前端80项及TypeScript通过；15个浏览器文档场景通过，1440深浅/390下4.2秒context延迟配合focus/visibility事件仅产生一次初始context请求，卸载取消由单元测试覆盖。权限隔离、写入恢复、草稿冲突回归通过。真实仓库1002文件快照817ms；同快照对照两次物化894/1534ms，一次569/720ms，详见evidence/read-performance.json；仅文件系统对照，不含DB授权/HTTP排队，不能宣称原20.81秒已解决。截图/样式见evidence/ui/refresh-performance-*，合成HTTP，未部署。OpenSpec严格/中文、Sprint scope与diff检查通过。

## BUG-0014 Capture验收

BUG-0014-requirement-center-capture-not-persisted：新建REQ/BUG由服务器锁内编号并写入目录、capture/trace、注册表与索引，页面等已验收态后刷新事实源。SQLite Capture/writer 21 passed；共享ChatRoute 31 passed/1 skipped；MySQL 8.2.0矩阵34 passed；Vitest79 passed；TypeScript与Vite构建通过；真实浏览器REQ/BUG创建、刷新、文档及1440/390焦点通过；临时Compose权限通过。证据见fix-requirement-center-capture-persistence/trace.md。未切换生产部署，Sprint整体签收与发布状态沿用原流程。


### 卡片更新时间格式

所有阶段REQ/BUG卡片统一显示“更新 YY/MM/DD HH:mm”，保留真实日期及源时间时分，各字段补零；缺失、无效或仅有日期/时分时显示“更新时间未知”，不补造日期和时间。footer必要时换行，时间自身不拆分，避免窄屏挤压动作。

卡片日期返修验证：后端65项、前端80项与TypeScript通过；15个浏览器场景覆盖1440深浅/390，完整日期与未知值、活动/归档REQ/BUG，以及时间与动作矩形无重叠。证据evidence/ui/updated-date-*。九阶段共享卡片日期断言通过。OpenSpec严格/中文、目录、Sprint scope及diff检查通过。原型与REQ子文档已同步；浏览器使用合成日期与HTTP，未部署。旧Capture测试“更新刚刚”已改为缺失真实日期时“更新时间未知”。

## BUG-0015 计划范围

BUG-0015-requirement-center-apply-start-stage-not-synced 已纳入本Sprint，状态迭代内，严重度medium，估算3人天；计划补齐研发启动0/N状态流转与统一状态投影。修复Change尚待创建，AC-001至011及真实API/浏览器刷新验收尚未执行，不作为已发布或已验收成果。事实源：issues/bugs/review/BUG-0015-requirement-center-apply-start-stage-not-synced/acceptance.md。


## BUG-0014 部署返修进度

Capture常驻配置、controller心跳与创建前就绪提示已接入当前本地部署，服务健康与重启恢复通过；自动回归及隔离视觉通过。用户登录后在当前部署真实创建REQ-0027-capture与BUG-0016-capture；整页刷新后均保留在采集池，两份capture.md可从页面打开且描述完整。文件系统交叉核对两套capture.md、trace.md、注册表与CHANGELOG均已持久化，status=captured且未进入Sprint/开发。两条明确标记的部署验收记录保留。返修M4已完成，可进入归档。证据见fix-requirement-center-capture-persistence/trace.md部署返修检查点。

## Capture 类型分级返修

REQ仅选择并保存priority P0/P1/P2/P3；BUG选择并保存五档severity。切换保留各自选值，API拒绝缺失/混用/非法等级，各事实源一致。历史记录不批量迁移。本轮验证证据见Capture Change trace的分级返修记录。

## 弹窗与说明返修

Capture桌面宽度840px，REQ支持P0-P3；BUG中文标签致命/严重/高/中/低映射blocker/critical/high/medium/low。共用说明支持Hover、键盘聚焦、Escape及触屏选择后持续说明。API、工作流分级校验与规范一致支持P3。 验证证据见关联Change trace。

## 提示去重返修

移除分级Hover/焦点浮层，只保留下方当前选中说明和原生键盘选择；ready成功状态不渲染文案及容器，检查中/异常提示、刷新和提交二次校验保留。 覆盖此前浮层交互，最新证据见Change trace。


### 所属需求原型常驻入口

所属REQ的prototype.html及prototype目录内HTML存在时，在主文档后常驻展示；多端以相对路径区分，兼容活动/归档目录。发现与读取共用安全解析，缺失无占位、不回退其他Issue/Change、不扩大必需文档校验。维持项目授权、只读预览和4px紧凑分组。


## REQ-0026 验收计划

REQ-0026-requirement-center-standalone-change-cards：迭代内，acceptance_status 为 not_started。验收源为 issues/requirements/review/REQ-0026-requirement-center-standalone-change-cards/acceptance.md；覆盖11项功能、5项原型和2项横切AC。重点检查同字号、Change中文标题、真实1440px/390px、独立对象授权、活动归档去重和多关联降级。静态原型不代表业务验收通过。

原型常驻返修：后端76项回归通过，补充嵌套预览HTTP授权用例单独通过；TypeScript通过；九阶段常驻前端9项及HTML新页交互聚焦验证通过，浏览器15场景通过（1440深浅/390、多端标识、活动/归档、紧凑布局），证据evidence/ui/prototype-persistent-*。后端覆盖符号链接、越界、缺失路径，预览沿用授权入口。浏览器是合成HTTP，不代表业务部署。
完整套件限制与全仓中文校验外部失败详见Change trace，本轮不宣称全量通过。

### REQ-0026 验收返修

独立Change卡片使用蓝色左边框；移除看板下方待核实卡片区，未知状态仅在折叠的数据异常入口可达且不计入页面业务统计。原九阶段、文档读取和权限保持；重复归档身份冲突保留诊断，未删除历史。验证入口：add-requirement-center-change-visibility返修记录。


原型入口标签仅显示区分多端所需相对路径（如web/prototype.html、admin/prototype.html），移除“原型 · ”前缀；常驻位置、排序、URL与预览权限不变。

原型标签精简验证：后端label/URL/新页模式聚焦检查通过，15个浏览器场景通过（1440深浅/390，活动/归档、多端相对路径、原有文档交互）；证据evidence/ui/prototype-label-*。本轮只改label与原型文案，未重跑全量测试或类型检查；前轮测试限制保留。OpenSpec strict通过；全仓中文校验仍被其他Change英文标题阻断，本Change无报错。未部署归档。

## REQ-0026 Sprint 标签返修

修复已完成独立 Change 在缺少 iteration 时不显示 Sprint 标签的问题，支持唯一成员关系反查，标签与文档存在性分离；不改变卡片布局与权限。真实仓库40项恢复；聚焦回归及1440px深浅主题验证见 Change verification.md 与 evidence/sprint-tag/。

## REQ-0026 阶段按钮增补规划

本轮已评审范围纳入：准备开发态“开始开发”、研发中“查看进度”、验收中按门禁“完成 / 归档”；已完成无阶段主按钮。复用现有REQ/BUG组件、权限和真实能力，不新增执行服务。新增3人天，REQ总计8人天；Sprint总计31/30人天，103.33%，剩余机动0，未触及120%硬门禁。建议后续低优先体验优化延后，不压缩权限与视觉验收。

交付状态：增补待req-opsx同步与实施，当前派生表的apply 21/21和待archive仅代表旧Change任务，不覆盖新增动作，不能据此归档。验收覆盖AC-ACTION-001至006、AC-XCUT-003及新范围原型门禁。承接Sprint-003的S3-A004动作矩阵经验，不宣称通用治理行动项完成。

product_data_collection_observability: applicable；affected_layers: web、api。验证行为关联、请求日志、拒绝路径和现有Task Trace；DB、部署、对象存储、保留周期无新增变化。真实执行能力缺失时禁用并说明，Demo不替代真实验收。

## 阶段按钮实施与证据

阶段按钮已接入：准备开发态开始开发、研发中查看进度、验收中完成/归档，已完成与未知无阶段主按钮。后端沿用action字段提供完整Change命令和禁用原因；前端同样保守禁用未接入执行能力，不能由响应中伪造action解除门禁。冻结空间返回只读原因；进度按读取权限打开当前tasks，只读文档不允许编辑。无tasks保留现有缺失反馈。

当前独立Change没有真实开发/归档执行服务，因此相关按钮禁用；不开放Demo模拟写入或伪造成功。矩阵中开发/归档modal、提交防重入/成功刷新在本轮不可执行分支为N/A，原因是已批准的能力门禁禁止进入执行分支；不以禁用按钮宣称真实开发或归档已实现。既有REQ/BUG弹窗族与执行交互保持，78项前端回归覆盖其行为。进度复用.rc-drawer、关闭按钮和Escape退出。

用户已确认1440px Skeleton布局；evidence/actions/skeleton-dark-1440.png与skeleton-light-1440.png为首轮证据。最终1440/390深浅主题4组截图、进度抽屉截图及computed style见evidence/actions/，真实浏览器组件+合成API夹具，非部署观察。仓库实际索引只读核验48个独立对象、2个有阶段动作、0个写动作开放。

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

证据：change_index.py 与 test_change_visibility.py；浏览器 title-fallback 四组1440/390深浅主题截图及styles.json。使用合成API验证组件，未部署18102，人工验收仍待确认。
