---
created_at: '2026-09-12 23:30:00'
updated_at: '2026-09-14 08:43:01'
---

# REQ-0026 实施验证

来源：REQ-0026-requirement-center-standalone-change-cards；Change：add-requirement-center-change-visibility；Sprint：sprint-005。

## 实现与兼容边界

- 新增请求内 ChangeIndex：完整注册表及双向关联先于授权过滤；隐藏、多来源拒绝、短 ID 歧义和无效来源均不转成独立对象。不使用全局缓存。
- 活动版本优先，活动缺文档不读归档副本；唯一归档识别完成，多归档只保留待核实摘要。状态依据 trace/execution，任务全勾选不推导完成；多关联保留既有阶段聚合优先级，当前项不确定时不聚合冒充单个任务进度。
- 保留原 Issue 卡片 id 的短显示标识，完整 Issue 身份仍用于文档与原动作。新增 current_change、related_changes、warnings 和 standalone_changes；独立卡片无虚构分级、无新增写入能力。反向来源新增读取不扩大原写入权限。
- 卡片只新增原 ID 下的同字号文本行和替换中文标题。关联明细、分别计数的任务进度及 Change trace 通过原阅读器的折叠追溯属性查看，不增加卡片关联面板或新抽屉。缺中文标题保留原标题。
- 类型筛选增加 Change，现有筛选菜单增加已完成/归档开关；本轮返修后未知项仅在数据异常诊断可达，不渲染卡片、不纳入页面业务计数。第四个类型按钮改为四列；390px给看板保留可滚动高度，卡片本身样式不改。
- 独立标题打开首个合法文档，优先 proposal；spec保留来源标记。Sprint依赖 iteration 和 changes 成员关系；不存在时返回受控缺失。

## 合成回归

| 验证 | 结果 | 证据与覆盖 |
|---|---|---|
| 后端 Change、项目权限、既有卡片、可信写入 | 93 passed | src/backend/tests/test_change_visibility.py、test_governance_scope.py、test_governance_board.py、test_governance_writer.py |
| Chat/观测及新增 Change 观测组合 | 38 passed，1 skipped | test_chat.py 与当时7项Change测试；跳过项是显式真实Codex执行探针，当前只读范围无需启动Agent，不替代本次真实API验证 |
| 卡片/阅读器/筛选/旧动作 | 77 passed | src/web/src/requirement-center.test.tsx |
| 项目切换、迟到响应、刷新草稿与请求边界 | 9 passed | src/web/src/governance.test.tsx |
| TypeScript、Vite生产构建 | pass | 本地 tsc --noEmit 与 vite build |
| OpenAPI/Orval | pass | 从 app.main.app.openapi 生成；本地 Orval 8.29.0，未下载依赖 |

后端测试使用已有系统Python测试环境（后端.venv无pytest）；未改依赖或真实env。测试覆盖冻结/过期/无成员、对象权限、直接API拒绝、路径/符号链接、注册表解析失败、并发项目隔离、归档歧义、缺tasks、标题回退、可信request_id、日志脱敏及采集失败降级。数据库使用隔离SQLite；未新增schema或SQL方言，不把这次执行称为真实MySQL部署验证。

## 真实浏览器与 API 观察

Playwright Chromium，真实Vite生产构建与FastAPI、专用临时项目、临时SQLite、两个专用成员；无API路由Mock、无真实客户数据、未调用生产服务或自动开发。观测与单测分开记录。

| 观察 | 结果 | 证据 |
|---|---|---|
| 双账号真实登录，独立及所属卡片 | pass | evidence/ui/live-results.json |
| 修改trace后刷新至development/acceptance，迁移归档后done | pass | evidence/ui/live-results.json |
| 外部新增关联后独立卡片去重，多关联当前项不猜测 | pass | evidence/ui/live-results.json、ambiguous-current.png |
| 对象权限限制，受限成员列表0、直接文档403 | pass | evidence/ui/permission-results.json、restricted-member.png |
| 冻结空间允许读取，保存返回403 | pass | evidence/ui/permission-results.json |
| 原标题打开原Issue地址；原进度打开tasks并定位/解释缺章节 | pass | evidence/ui/live-results.json、existing-progress.png |
| 独立文档只读，Esc退出；分Change进度与Change trace来源 | pass | readonly-document.png、multi-change-readonly.png、detail-results.json |
| 缺中文标题回退，归档开关计数一致 | pass | missing-title.png、detail-results.json |
| 真实请求日志只保存安全字段 | pass | evidence/api-audit.json；聚合200/403结果，不保存正文或凭证 |

真实模式既有“开始开发”按钮原本只提示“当前仅支持采集需求的生成动作”；没有真实Action Modal。此行为保留并实测。动作Modal族的打开、取消、Esc保留由原Demo模式组件回归验证；未把Demo动作当真实执行。该事实修正设计矩阵的描述，不开放新动作。

## 视觉证据与用户确认

Skeleton使用明确的合成数据注入当前真实页面；用户在本次会话已确认“确认，按此继续”。首轮截图skeleton-1440.png，ID均10.5px，标题13.5px。

最终真实API截图：actual-1440-dark/light.png、long-id-1440-dark/light.png、long-id-390-dark/light.png；最终样式见final-style.json。原ID与新增ID的font-size、family、weight、style、line-height、color逐项相等；标题13.5px；长ID可换行，无文字溢出；无浏览器pageerror。保留card padding、border、圆角及meta/docs/progress/footer样式采样。已人工查看最终1440及390截图。

原卡片未改区域以既有源码规则与Skeleton对照为基线。新增行只增加所需高度。筛选第四项和手机看板高度修复是在视觉失败后完成并重取证。原HTML仍为设计对照页，不作为真实API证据，不绕过此前file URL浏览器策略。

## 文档一致性及观测说明

已核对requirement、业务流程、用户故事、acceptance、trace及prototype context/HTML；主约束相同，历史过程记录保留时间语义。UI、API索引、后端schema、OpenAPI和Orval同步。product_data_collection_observability为applicable，affected_layers=[web,api]；GET复用现有服务器request_id与请求日志，客户端字段不用于授权；无新行为事件种类、DB迁移/索引、存储、部署拓扑或异步Task Trace。请求采集失败不阻断读取。

## 执行问题与恢复

- 首次pytest解释器缺pytest：改用现有系统Python，相关回归通过。
- 工作流写入REQ registry的related_change时使用固定4空格，而现有条目为2空格，导致YAML解析失败。已只修复REQ-0026字段缩进；后续同步与注册表解析复核通过。
- REQ trace列表曾是零缩进，工作流未更新其关联Change状态。已规范化该trace缩进，再由opsx.progress重放，现为in_progress；未手写工作流marker。
- 浏览器执行需要本地启动权限，已通过工具审批运行隔离服务与浏览器。无未解决必需权限或证据缺口。

建议后续用/spec-opt为工作流YAML列表及新增字段缩进增加回归，并让语言校验拒绝空扫描；本次未自动创建Issue/Change或修改治理脚本。人工业务验收与归档尚未执行，由后续流程确认。

## 最终版本与流程验证

最终后端93项、前端两文件86项、TypeScript和Vite构建通过。最终6组视觉与既有阅读器回归重取证通过；源文件SHA256见evidence/source-version.json。OpenSpec strict、8份Change中文文档、Sprint scope、产品观测和git diff --check通过；REQ/Sprint YAML解析通过。Apply连续执行真实轨迹3条验证通过，见evidence/apply-behavior.json；未发生用户停止/平台中止场景，不声称全部场景已观察。

Workflow Sync最终结果：opsx.apply成功、Errors=0，REQ关联applied、人工验收pending，当前态索引下一步为完整REQ身份的opsx-archive。AI Usage自动发现未取得可归属事件，usage_mode=unavailable、command_run_count=0、Sprint快照skipped；未伪造用量。临时验收服务已停止。

## 2026-09-13 返修验证

独立Change已使用info蓝框；unknown不再渲染九阶段之外的卡片，保留默认收起的只读数据异常入口，页面统计只计算真实阶段卡片。修正rc-content固定四行网格，改纵向flex，避免可选诊断行及窄屏标题动作遮挡。

证据：用户附件与源码路径已在design.md逐项对照；09-01/09-02同ID归档分别为建立契约/扩展动作矩阵，不是等价副本，保留历史冲突，不自动删除或按日期选版本。核对完成，不宣称历史ID冲突已被修复。

验证：Vitest需求中心与错误回归86项通过；TypeScript通过；后端既有Change身份/归档/权限8项通过。浏览器 `src/web/tests/requirement-center-change-layout.cjs` 四组1440/390深浅主题通过，styles.json和layout/diagnostics截图在logs/req0026-modify/。验证三类边框不同、九阶段DOM、无待核实卡片区、统计一致、仅unknown搜索、诊断折叠键盘与标题统计无重叠。视觉检查已查看1440深色和390浅色截图。首轮夹具缺项目目录上下文导致0卡片已修正；后续视觉发现固定网格重叠，留在本轮自修后重验。

Mock/API边界：本轮视觉采用真实浏览器组件与合成API，不冒称真实数据验收；本地Web服务更新另记。API/schema/权限/后端统计无修改，不需要OpenAPI或客户端重生成；DB、存储、安全策略及Task Trace无新增变更。product_data_collection_observability：applicable，affected_layers：web；复用既有读取请求，无新增埋点或日志字段。

REQ子文档一致性扫尾：已更新requirement、business-flow、user-stories、acceptance、prototype/context及prototype.html意图说明；trace由Workflow Sync更新。capture/review保持历史输入和原评审，不改写历史结论。Change design/spec/acceptance/verification与Sprint验收及release-note同步；Sprint容量、范围、API索引无需更新，原因是原Change内UI返修且接口不变。历史视觉证据不替代本轮截图。

## Sprint 标签返修证据

独立 Change 的 Sprint 标签优先使用合法 iteration 并核对 Sprint changes 成员关系；iteration 缺失、null 或空串时反查活动及归档 Sprint，仅唯一 Sprint ID 可关联。多个成员关系不猜测并提示待核实；显式错误不被反查覆盖。同 ID 活动 Sprint 优先，不从归档补活动缺口。标签不依赖 sprint.md 存在，文档入口仍要求文件可读。

真实仓库只读复核：45 个已完成独立 Change 中40个缺 iteration，40个均恢复唯一归属；build-api-standard → sprint-000。浏览器为真实组件加合成 API 响应，非部署观察；截图和 computed style 在 evidence/sprint-tag/。

product_data_collection_observability: applicable；affected_layers: API。复用现有请求日志与鉴权，直接API/日志失败回归继续覆盖；无新增行为事件、Task Trace 或端侧链路字段，脱敏与保留周期不变。OpenAPI/Orval N/A：字段类型和接口结构未变。

返修验证结果：后端 Change/治理权限/看板共92项通过（其中 Change 聚焦16项）；包括真实HTTP归档反查、缺文档404与不可见403。1440px深浅主题2项通过，Sprint标签字号10px、主题颜色正确、无pageerror。OpenSpec strict、中文优先、Sprint scope、产品数据采集、目录结构、上下文预算校验通过。前端业务源码与schema未修改，无需客户端重新生成。

## 阶段按钮实施与证据

阶段按钮已接入：待开发开始开发、研发中查看进度、验收中完成/归档，已完成与未知无阶段主按钮。后端沿用action字段提供完整Change命令和禁用原因；前端同样保守禁用未接入执行能力，不能由响应中伪造action解除门禁。冻结空间返回只读原因；进度按读取权限打开当前tasks，只读文档不允许编辑。无tasks保留现有缺失反馈。

当前独立Change没有真实开发/归档执行服务，因此相关按钮禁用；不开放Demo模拟写入或伪造成功。矩阵中开发/归档modal、提交防重入/成功刷新在本轮不可执行分支为N/A，原因是已批准的能力门禁禁止进入执行分支；不以禁用按钮宣称真实开发或归档已实现。既有REQ/BUG弹窗族与执行交互保持，78项前端回归覆盖其行为。进度复用.rc-drawer、关闭按钮和Escape退出。

用户已确认1440px Skeleton布局；evidence/actions/skeleton-dark-1440.png与skeleton-light-1440.png为首轮证据。最终1440/390深浅主题4组截图、进度抽屉截图及computed style见evidence/actions/，真实浏览器组件+合成API夹具，非部署观察。仓库实际索引只读核验48个独立对象、2个有阶段动作、0个写动作开放。

验证：后端93项（含HTTP权限、冻结只读、日志拒绝与采集失败）、前端78项、TypeScript、浏览器4组通过。未部署、未进行真实开发/归档执行。接口schema未变，无需重新生成OpenAPI/Orval；API行为说明已同步。DB、部署、对象存储、安全策略不变。

## 固定禁用提示返修结论

本节替代上一轮独立Change一律禁用的结论。后端复用REQ/BUG阶段必需文档与非空门禁，并核对唯一Sprint；缺失/空文档/只读才返回相应原因，不再固定生成测试核对或能力未接入提示。文档存在不代表测试执行通过；前端复用已有testProgress/manualAcceptanceCount判断，数据不存在不伪造检查结论。

独立Change与REQ/BUG进入同一动作处理器：研发中读取tasks；真实模式中当前未支持的开发/归档动作点击后显示现有统一能力提示，不执行写入；Demo沿用现有弹窗和模拟流转，不接入真实执行。取消、提交防重入和刷新行为复用当前组件，未新增服务或权限。

验证：后端94项、前端79项、TypeScript通过；1440/390深浅主题4组真实组件合成API浏览器验收通过，截图和computed style位于evidence/action-gates/。非部署观察，未执行真实开发/归档。保留现有权限和真实能力限制；新证据替代旧固定禁用截图。

## 独立交付验收来源返修（当前结论）

验收中不再固定要求acceptance.md：优先校验trace.acceptance_refs声明的Change内相对Markdown路径；显式引用无效、缺失或为空返回具体待核实原因，不回退。未声明时查现有acceptance.md、verification.md，再识别trace中非空“验证记录/验收记录/验证结果/验收结果”章节。不得跨Change或通过绝对路径、父路径、符号链接越界读取。没有证据来源提示待核实，不补建文件；本机制定位证据，不自动判断验收通过，applied和tasks全勾均不代替验收。

真实仓库样本standardize-sprint-default-capacity以trace验证记录作为来源；unify-issue-classification-metadata使用acceptance.md，两者当前源码均无来源阻塞。后端95项回归通过，包含显式引用、缺失、空源、越界与历史trace来源；浏览器复用真实组件+合成API在1440/390深浅主题验收，证据evidence/action-gates，非部署验收。

运行页面核对：用户地址localhost:18102对应moonbox-web，加载index-y8JI4bjc.js，其中无旧能力提示；moonbox-backend镜像动作函数也无旧提示，但仍采用上一版固定acceptance.md清单，尚未部署本次解析。未对运行容器做重建或重启，截图旧提示的实际响应来源仍未取得，不断言缓存根因。

REQ主文档、故事、流程、验收、trace、原型context及HTML已核对同步；capture/review保留历史，不需改写。API既有action字段形状不变，无需OpenAPI/Orval生成；product_data_collection_observability为applicable，affected_layers为api，复用请求日志/授权，验证无越界；无新增DB、部署配置、存储、保留周期或Task Trace。

## 中文标题来源返修

标题来源保留既有优先级：trace显式中文标题或标题字段、proposal/design有效业务标题，最后回退trace正文一级业务标题；过滤追溯、背景与动机、验证记录、验收结果等通用章节名，全部缺失才显示完整Change ID。

证据：change_index.py 与 test_change_visibility.py；浏览器 title-fallback 四组1440/390深浅主题截图及styles.json。使用合成API验证组件，未部署18102，人工验收仍待确认。

最终验证：107项后端测试通过；真实仓库unify-issue-classification-metadata解析为“Issue 分级元数据统一”；四组浏览器测试通过。2026-09-14 用户执行 `/opsx-archive REQ-0026`，本验证文档作为归档证据输入；运行环境18102未部署本轮源码，归档不声明该本地容器已更新。
