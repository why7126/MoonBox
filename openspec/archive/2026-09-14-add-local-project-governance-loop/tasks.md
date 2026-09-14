---
change_id: add-local-project-governance-loop
created_at: 2026-09-11 09:08:07
updated_at: 2026-09-13 00:57:14
---

## 1. 前置设计与 UI Skeleton

- [x] 1.1 核对实际绑定、现有写入口及依赖版本；验证维护窗口独占写入可行性，不能满足则保留RC-002阻塞（AC-001、007、010、012）。
- [x] 1.2 冻结参考稿反向工程、selector映射、动作按钮矩阵和computed style采样清单，承接design UI Contract（AC-PROTOTYPE-001、006）。
- [x] 1.3 建立两页增量UI Skeleton与显式Mock状态，提供1440px首轮截图及确认；通过后再完成UI细节（AC-PROTOTYPE-002）。

## 2. 项目查询与版本基础

- [x] 2.1 实现ProjectScope与服务端授权，覆盖空间/仓库/对象、只读及撤权，移除聚合与文档的隐式全局目录读取（AC-001、002）。
- [x] 2.2 实现稳定文件manifest、聚合快照和文档版本，覆盖迁移、删除、解析异常及过期缓存（AC-003、005）。
- [x] 2.3 新增候选、应用和项目锁schema及迁移；验证SQLite/MySQL、唯一键和重启恢复字段（AC-011、012、016）。

## 3. 准备与候选

- [x] 3.1 实现req-generate准备、允许治理快照和干净副本基准；未提交内容和已有成果不丢失（AC-007）。
- [x] 3.2 连接卡片到本人兼容Chat，保持进入不发送；真实成功轮次触发受信任候选收集（AC-006、008）。
- [x] 3.3 实现固定manifest、Diff与动作语义校验，拒绝其他对象、越界文件、失败轮次及生效规格写入（AC-008、009、014）。

## 4. 受控写入与恢复

- [x] 4.1 建立可信写入控制器与项目串行锁，将既有文档保存/勾选统一路由；缺维护窗口或旧写入口绕过时禁用应用（AC-005、011、016）。
- [x] 4.2 实现应用前授权/内容版本/成果校验、幂等入队及不可变操作结果（AC-009、010、011）。
- [x] 4.3 实现前后镜像、fsync日志、阶段写入与最终一致性校验，禁止读半成品（AC-003、012）。
- [x] 4.4 实现中断接管、前后镜像恢复及recovery_blocked；不能覆盖检测到的外部改动，未终态恢复文件不得清理（AC-012、013）。

## 5. 前端动作族与刷新

- [x] 5.1 在Skeleton确认后接入项目绑定与3秒刷新，覆盖焦点恢复、退避、迟到响应、筛选/滚动/草稿保留（AC-002、004、005）。
- [x] 5.2 一次性交付成果摘要、完整预览、维护窗口提示、显式确认、冲突/失败/恢复阻塞/已应用动作族（AC-008、009、013）。
- [x] 5.3 完成深浅主题、390px和低视口、键盘/遮罩capture、固定toast及样式采样（AC-XCUT-001至003、AC-PROTOTYPE-003、005、006）。

## 6. 契约、部署和验证

- [x] 6.1 同步OpenAPI、Orval、API索引、数据库文档和schema兼容测试；验证新旧Web/API协同升级及无scope拒绝（AC-002、016）。
- [x] 6.2 接入脱敏行为/请求/Task Trace关联与失败降级；轮询不伪造用户行为，禁止日志正文或路径（AC-016）。
- [x] 6.3 同步Compose可信写权限、私有成果目录、备份保留和回退说明，执行目标环境预检及恢复验证（AC-012、016）。
- [x] 6.4 运行后端接口/并发/幂等/失败注入和前端回归，覆盖16条功能AC，记录合成结果而非真实观察。
- [x] 6.5 真实账号与授权验证对象完成req-generate到原仓库应用，看板更新连续10次均满足5秒目标，留存浏览器/worker/文件证据（AC-004、015）。
- [x] 6.6 回填25条AC、review RC-001至004、REQ子文档及原型最终一致性；完成视觉与computed style证据后关闭UI门禁（AC-PROTOTYPE-004）。

执行依赖：1.1先于写入实现，1.2/1.3先于UI细节；2→3→4→真实闭环，后端独立工作不受UI确认局部阻塞。实现与验证完成；真实观察、合成回归及运行边界见 trace.md。


## 验收返修记录

- 反馈：用户4张附件显示38项全部阻塞、归档卡片回退、验收文件误报缺失，并要求移除需求中心项目连接栏。
- 根因 confirmed：活动Change缺失时默认proposed覆盖done；Sprint仅查活动目录；精简展示文档用于验收检查；6条registry路径与实际归档目录不符。修复前整库复现为33待开发/4验收/1完成、阻塞38。
- 调整：终态优先；Change/Sprint按完整身份解析活动与归档；归档Change只读；验收检查真实Issue文件；按精确完整ID修正6条已验证路径。未扩大查询scope和写入权限。
- UI：移除需求中心独立连接栏与专用grid行，保留工具栏刷新、同步title、轮询、筛选与草稿。Chat未调整。applied维持验收中语义。
- 整库结果：38对象=25REQ+13BUG；21REQ与13BUG完成、4REQ验收中；blocked=0、drift=0。三份REQ-0000未注册，不自动计入。
- 验证：最终后端5文件35 passed；首轮新增测试的2个调用参数顺序错误已修正并在最终运行通过。前端初次18文件167 passed，最后终态提示调整后聚焦2文件65 passed；TypeScript构建检查通过；视觉证据为evidence/ui/modify-board-*，1440深浅/390/筛选刷新，浏览器pageerror为0。
- 证据边界：浏览器采用仓库解析数据与合成HTTP，只证明当前源码UI；没有切换当前业务部署，不把历史真实闭环证据宣称为本轮真实部署复验。
- REQ 子文档一致性扫尾检查：已同步requirement.md、business-flow.md、user-stories.md、acceptance.md、prototype/web/context.md、prototype.html；trace当前结果由本记录和Workflow Sync承接。capture.md、review.md为历史采集/评审事实，无需重写；旧截图为历史证据，已提供替代截图。
- 文档同步：design、delta spec、API索引、Sprint验收/发布说明已更新。DB、部署、安全规则、客户端生成和成果应用文档无需更新，原因是schema、部署方式、授权边界和成果应用行为未变。
- product_data_collection_observability：affected_layers=[web, api]；本轮仅修正聚合派生值和布局，未新增行为事件、请求封装、日志、Task Trace、DB或存储字段；其余层N/A。validation：接口/权限/写入回归，轮询不新增用户行为埋点，OpenAPI/Orval schema不变。

返修视觉复核补充：首次新截图发现前端blockedTip仍给已完成项强制补验archive.md。已完成项没有待执行动作，现取消该终态重复校验，补充已完成卡片无rc-blocked提示的浏览器断言；重拍后证据覆盖此偏差。


### 首屏骨架返修记录

用户附件34c55de6确认独立加载面板推低看板，并同时显示假零值/空态。已移除加载面板，新增指标/计数/卡片原位骨架及不占布局的读屏状态；首次慢请求与后台刷新分离。需求中心显式引入骨架样式，统计数字保持固定行高；首轮浏览器测得指标高度变化，修正样式引用后重验。

REQ子文档一致性扫尾：更新PRD、流程、故事、验收、原型context及HTML；trace状态由Workflow Sync维护。capture/review为历史材料无需修改。API、数据库、权限、部署及客户端生成无需更新，本轮仅UI加载展示。product_data_collection_observability：affected_layers=[web]；请求、日志、事件、Task Trace和存储N/A（未变更请求行为或采集字段），validation为慢请求与刷新合成浏览器回归。

首屏返修验证：延迟合成HTTP下1440深浅主题和390px，指标/工具栏/看板/列头/列体maxTopShift均为0px，pageerror=0；后台刷新卡片和筛选保留。证据evidence/ui/loading-styles.json及loading-*.png。TypeScript检查通过；聚焦前端测试结果见最终门禁回填。OpenSpec严格与中文校验、Sprint scope通过。


### trace 归属返修记录

来源为用户截图aa14241e：同名trace标题与实际Change正文归属混淆，旧实施记录位于最新结论之前。已分别提供Issue追踪和Change实施记录入口；后端复用现有label/url字段，前端按URL区分key并显示来源，沿用只读权限。REQ-0022 Change最新摘要置顶、历史完整保留；需求trace新增阅读摘要，机器状态经Workflow Sync维护。

REQ子文档一致性扫尾：PRD、流程、故事、acceptance、trace阅读摘要、原型HTML/context均已同步；capture/review历史事实无需更新。API索引补充同名条目按URL识别；DB、部署、安全规则和客户端生成无需更新，原因是schema、授权和运行边界未变。product_data_collection_observability：affected_layers=[web,api]；日志/事件/Task Trace/数据库N/A（未新增字段或请求封装），validation为来源路由、只读权限和抽屉浏览器回归。最新UI证据为仓库文档+合成HTTP，不代表业务部署复验。

同名trace返修验证：后端22通过、前端65通过、TypeScript通过；1440深浅与390共6个浏览器用例，来源URL/标题/正文一致，两种trace只读，来源行无溢出，错误0。首次浏览器脚本点击蒙层中心被正文拦截，改用可见关闭按钮后通过。证据evidence/ui/trace-source-styles.json及截图。OpenSpec严格/中文、目录结构、Sprint scope和空白检查通过。


### trace 单入口返修记录

用户明确收敛为所有REQ/BUG卡片仅展示所属Issue trace.md。本轮取消Change trace入口、拆分标签与额外来源行；所有阶段固定Issue路由，缺失时报不可用，不回退。Change文件、内部状态计算及其他文档保留。此前双入口记录仅作历史。

REQ子文档一致性扫尾：PRD/流程/故事/验收/trace阅读摘要/原型HTML与context已改为单入口；capture/review历史事实无需修改。API索引和delta spec同步；schema/DB/权限/部署/客户端生成无需修改。product_data_collection_observability：affected_layers=[web,api]；日志/事件/Task Trace/存储N/A，无新增采集和请求封装；验证覆盖Issue路由与缺失不回退。

单入口最终验证：后端44通过（含REQ/BUG所有阶段、Change存在但Issue trace缺失）、前端65通过、TypeScript通过；9个浏览器用例通过，正文为Issue文件，缺失只显示不可用，未请求Change trace。证据evidence/ui/issue-trace-styles.json及新截图。OpenSpec严格/中文/目录/Sprint scope/空白校验通过。当前业务部署未切换，产品签收待确认。


### 任务文档定位返修记录

- 反馈与 confirmed 根因：三个进度按钮绕过文档读取，直接构建统计面板。现统一关联文档读取与定位，高亮实际章节或任务；独立进度视图已移除。
- 卡片研发、测试、人工验收入口统一打开关联 tasks.md 的完整 Markdown 文档。加载完成后优先定位匹配章节，其次定位匹配任务并高亮、聚焦；不打开独立进度面板。缺少关联时提示未关联 tasks.md；文件不存在或已移动时提示读取目标缺失；章节或任务缺失时保留完整文档并提示未找到目标，不以计数、历史返修记录或其他文档伪造目标。普通 tasks.md 链接从顶部打开，既有编辑与勾选权限不变。
- REQ 子文档一致性扫尾检查：requirement、business-flow、user-stories、acceptance、trace 阅读摘要、prototype/web/context.md 和 prototype.html 已同步。capture/review 为历史事实，无需改写；历史截图保留，新证据替代对应交互。
- product_data_collection_observability：affected_layers=[web]；复用既有文档请求、授权与保存，未改变事件、日志、Task Trace、API schema 或存储，其他层 N/A；validation 为前端交互回归、类型检查和浏览器验证。
- API、数据库、部署、安全边界及客户端生成无需同步：均未改变。


任务入口返修验证结果：本轮最终前端回归67项通过，TypeScript检查通过；浏览器24个生产组件场景通过，覆盖1440px深浅主题、390px、章节优先、任务回退、缺文件、缺章节、普通入口无定位；同步原型4个交互验证通过。视觉与 computed style 证据见 evidence/ui/tasks-navigation-*。OpenSpec strict、中文、目录、Sprint scope、diff检查通过。后端未改变，本轮未重跑后端测试。


### Sprint 文档归属返修记录

卡片 sprint.md 属于关联 Sprint，通过现有 Issue 文档读取接口按当前授权项目解析。展示、读取和缺失校验共用解析：按关联 ID 查活动目录，仅活动目录不存在时查同 ID 归档目录；活动目录缺文件不读取归档旧副本，不回退 Issue、Change 或其他 Sprint。文件缺失时保留明确提示；读取保持只读，trace.md 仍仅属于当前 REQ/BUG。


REQ 子文档一致性扫尾检查：requirement、business-flow、user-stories、acceptance、prototype/web/context.md 与 prototype.html 已同步；trace 通过当前 Change 摘要和 Workflow Sync 承接。capture/review 为历史事实，无需更新。

product_data_collection_observability：affected_layers=[api,web]；复用原文档读取路由及请求日志，无新增事件、字段或 Task Trace。DB、对象存储、部署、安全权限与客户端生成 N/A（schema、授权机制、写入边界均未改变）。validation：关联文档与权限回归，API索引语义同步，OpenAPI无需重新生成。


Sprint文档返修验证：后端58项通过（聚合、REQ/BUG活动与归档来源、缺失不回退、路径校验、作用域和HTTP接口）；浏览器6个场景通过，覆盖1440深浅与390px正常/缺失态，原型Sprint入口验证通过。证据为evidence/ui/sprint-document-*及样式JSON。OpenSpec strict、中文、目录、Sprint scope与diff检查通过。浏览器为真实仓库聚合/正文与合成HTTP，未切换业务部署。


### 主动作阻塞与消息避让返修

卡片主动作统一使用接口disabled_reason、Issue阻塞和前置文档缺失判断，阻塞提示、按钮原生禁用、title原因与执行前守卫一致；文档仍可阅读，补齐后刷新恢复按钮。Tips位于Agent助手上方并保留安全间距，提高层级；窄屏限制宽度、长词换行，超长消息在受限高度内滚动，不遮挡助手。


REQ 子文档一致性扫尾检查：requirement、business-flow、user-stories、acceptance、prototype/web/context.md和prototype.html同步；trace由Change当前摘要与Workflow Sync承接。capture/review保留历史事实无需改写。

product_data_collection_observability：affected_layers=[web]。本轮只改按钮状态、执行守卫和Tips布局，无新增事件、请求封装、日志或Task Trace；API、数据库、权限、部署、对象存储及客户端生成N/A，接口与写入边界未变。validation为交互回归与浏览器几何/样式检查。


主动作与Tips返修最终验证：70项前端回归及TypeScript通过；12个浏览器状态通过（1440深浅、390、320；禁用/补齐恢复、短提示、长中文及无空格长词），提示矩形与Agent至少保留8px间距，无横向越界。原型禁用/恢复与长提示验证通过。证据为evidence/ui/action-toast-*和样式JSON；使用合成HTTP，只证明本地源码UI，未切换业务部署。OpenSpec strict、中文、目录、Sprint scope和diff检查通过。


### 主文档持续展示返修

REQ的requirement.md、BUG的bug.md一旦在所属Issue中生成，即在全部阶段卡片持续显示并固定文档列表首位，包括迭代规划、开发、验收和已完成。读取始终来自所属REQ/BUG当前目录，兼容Issue归档迁移；不读取Change同名文档。未生成不伪造入口，文件删除后按最新快照移除，已打开入口读取缺失明确提示。仅调整展示与排序，保留既有阶段编辑和只读权限。


REQ 子文档一致性扫尾检查：requirement、business-flow、user-stories、acceptance、prototype/web/context.md及prototype.html同步；trace通过Change摘要与Workflow Sync承接。capture/review为历史事实无需更新。

product_data_collection_observability：affected_layers=[api,web]；仅聚合展示列表和UI排序，复用原Issue文档读取、能力矩阵与日志，不新增事件/请求字段/Task Trace。DB、部署、对象存储、安全边界、客户端生成N/A，API schema不变；API索引补充来源与展示规则。validation为后端聚合/权限回归和前端全阶段及浏览器验证。


主文档持续展示最终验证：后端80项、前端79项、TypeScript通过；15个浏览器场景通过（1440深浅/390，活动和归档REQ/BUG首位入口、Issue正文、只读与缺失不回退），原型主文档入口通过。证据为evidence/ui/main-document-*和样式JSON。OpenSpec strict、中文、目录、Sprint scope及diff校验通过。浏览器使用真实仓库聚合和正文配合合成HTTP，本轮未切换业务部署。


### Sprint 文档持续展示

sprint.md在关联Sprint文档出现后于所有阶段卡片持续展示，包括待开发、研发中、验收中和已完成；requirement.md/bug.md仍保持首位。复用关联Sprint读取、只读能力、活动/归档解析及缺失不回退。只扩大展示白名单，不将sprint.md新增为其他阶段的必需文档，不改变阻塞与权限判断。


REQ 子文档一致性扫尾检查：requirement、business-flow、user-stories、acceptance、prototype/web/context.md及prototype.html同步；trace由Change摘要和Workflow Sync承接。capture/review为历史事实无需更新。product_data_collection_observability：affected_layers=[web]；无新增事件、请求封装、日志或Task Trace，API/DB/权限/部署/对象存储/客户端生成N/A，来源与接口schema不变。仅变更展示规则，后端无需修改或重复测试；既有Sprint活动/归档及权限回归由上轮记录承接，当前以组件和浏览器回归验证UI。


### 卡片文档分组与排序

常驻区按所属requirement.md/bug.md、关联sprint.md、所属trace.md固定排序；阶段区按当前任务优先排序。待开发proposal/spec/design/tasks；研发和验收tasks/spec/design/proposal；已完成archive/tasks/spec/design/proposal；已评审review优先，其他沿阶段阅读顺序。两个分组之间仅保留4px间距，无分隔线与额外内边距，组内自然换行，单组无空白占位；来源、权限及原必需文档校验不变。

REQ子文档一致性扫尾：上述行为已同步PRD、流程、故事、验收、原型；capture/review是历史记录无需更新，Issue trace由Workflow Sync同步。product_data_collection_observability：affected_layers=[web]，API/DB/日志/Task Trace/部署/安全/客户端生成N/A，原因是仅改变卡片文档布局和排序，读取及权限不变。

文档分组返修：前端79项回归及TypeScript通过；15个浏览器场景通过，覆盖1440深浅/390、活动与归档REQ/BUG、文档只读和缺失提示。常驻顺序与阶段顺序由九阶段参数回归验证，单组无分隔、双组细线由相邻组CSS控制；computed style记录组间距、边框及宽度，无组内横向溢出。截图见evidence/ui/document-groups-*，原型同步。OpenSpec严格/中文、目录、Sprint scope与diff检查通过。后端无变更，未重跑；浏览器为真实仓库数据配合合成HTTP，未部署。


### 紧凑换行返修

移除双组边框及额外内边距，仅4px组间距；单组无占位。REQ子文档一致性已同步PRD/流程/故事/验收/原型；capture/review历史事实无需变更，Issue trace由Workflow Sync维护。仅Web样式，API/DB/安全/部署/客户端生成无变化，沿用上述观测N/A声明。

紧凑文档区返修：移除分隔线及额外padding，双组margin-top为4px，单组0px。15个浏览器场景通过，1440深浅与390的computed style确认border/padding为0、组间距4px，顺序与只读入口回归通过；原型同步。证据见evidence/ui/document-compact-*。本轮仅CSS与原型样式修改，未重跑TypeScript及单元测试；此前79项结果为历史记录。OpenSpec严格/中文检查通过；未部署，浏览器仍为真实仓库数据配合合成HTTP。


### 文档读取与刷新性能

单次Change文档请求复用同一授权稳定快照的临时目录，避免授权和正文读取重复物化；不引入跨请求缓存，保留项目授权、写入恢复、epoch及绑定版本检查。相同项目的context刷新复用进行中请求，初始加载完成后开始轮询；切换项目及卸载取消旧请求。文档内容/草稿/版本冲突处理与原型布局不变。分段日志仅含服务端request_id、操作名、成功状态及各阶段毫秒耗时，不含文档内容或本机路径。

REQ子文档扫尾：PRD、流程、故事、验收与原型context已更新；prototype.html交互模拟不含真实HTTP调度，无需修改；capture/review历史不变；Issue trace由Workflow Sync维护。product_data_collection_observability：affected_layers=[web,api]，增加脱敏分段日志；数据库、Task Trace schema、部署、安全边界、客户端生成N/A，未新增接口或字段且权限不变。

文档性能与刷新返修验证：后端72项、前端80项及TypeScript通过；15个浏览器文档场景通过，1440深浅/390下4.2秒context延迟配合focus/visibility事件仅产生一次初始context请求，卸载取消由单元测试覆盖。权限隔离、写入恢复、草稿冲突回归通过。真实仓库1002文件快照817ms；同快照对照两次物化894/1534ms，一次569/720ms，详见evidence/read-performance.json；仅文件系统对照，不含DB授权/HTTP排队，不能宣称原20.81秒已解决。截图/样式见evidence/ui/refresh-performance-*，合成HTTP，未部署。OpenSpec严格/中文、Sprint scope与diff检查通过。


### 卡片更新时间格式

所有阶段REQ/BUG卡片统一显示“更新 YY/MM/DD HH:mm”，保留真实日期及源时间时分，各字段补零；缺失、无效或仅有日期/时分时显示“更新时间未知”，不补造日期和时间。footer必要时换行，时间自身不拆分，避免窄屏挤压动作。

REQ子文档扫尾：PRD/流程/故事/验收/原型HTML与context同步；capture/review历史不变，Issue trace由Workflow Sync维护。product_data_collection_observability：affected_layers=[web,api]；日志/Task Trace/DB/安全/部署/客户端生成N/A，无新增schema或采集字段，仅updated_at显示格式调整。

卡片日期返修验证：后端65项、前端80项与TypeScript通过；15个浏览器场景覆盖1440深浅/390，完整日期与未知值、活动/归档REQ/BUG，以及时间与动作矩形无重叠。证据evidence/ui/updated-date-*。九阶段共享卡片日期断言通过。OpenSpec严格/中文、目录、Sprint scope及diff检查通过。原型与REQ子文档已同步；浏览器使用合成日期与HTTP，未部署。旧Capture测试“更新刚刚”已改为缺失真实日期时“更新时间未知”。


### 所属需求原型常驻入口

所属REQ的prototype.html及prototype目录内HTML存在时，在主文档后常驻展示；多端以相对路径区分，兼容活动/归档目录。发现与读取共用安全解析，缺失无占位、不回退其他Issue/Change、不扩大必需文档校验。维持项目授权、只读预览和4px紧凑分组。

REQ扫尾：PRD/流程/故事/验收/原型同步；capture/review历史无需更改，trace由Workflow Sync维护。product_data_collection_observability affected_layers=[web,api]；DB/部署/安全边界/日志schema/客户端生成N/A，沿用项目授权与预览响应头，仅既有preview路径支持嵌套原型。

原型常驻返修：后端76项回归通过，补充嵌套预览HTTP授权用例单独通过；TypeScript通过；九阶段常驻前端9项及HTML新页交互聚焦验证通过，浏览器15场景通过（1440深浅/390、多端标识、活动/归档、紧凑布局），证据evidence/ui/prototype-persistent-*。后端覆盖符号链接、越界、缺失路径，预览沿用授权入口。浏览器是合成HTTP，不代表业务部署。
完整套件限制与全仓中文校验外部失败详见Change trace，本轮不宣称全量通过。


原型入口标签仅显示区分多端所需相对路径（如web/prototype.html、admin/prototype.html），移除“原型 · ”前缀；常驻位置、排序、URL与预览权限不变。

REQ扫尾：上述子文档与原型已同步，capture/review历史无需修改；Issue trace经Workflow Sync维护。product_data_collection_observability affected_layers=[web,api]；仅label文案，不改schema、DB、日志、授权、部署或客户端生成。

原型标签精简验证：后端label/URL/新页模式聚焦检查通过，15个浏览器场景通过（1440深浅/390，活动/归档、多端相对路径、原有文档交互）；证据evidence/ui/prototype-label-*。本轮只改label与原型文案，未重跑全量测试或类型检查；前轮测试限制保留。OpenSpec strict通过；全仓中文校验仍被其他Change英文标题阻断，本Change无报错。未部署归档。
