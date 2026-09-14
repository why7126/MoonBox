---
change_id: add-requirement-center-change-visibility
title: 需求中心 Change 可见性与卡片身份展示
status: archived
requirement: REQ-0026-requirement-center-standalone-change-cards
iteration: sprint-005
created_at: '2026-09-12 22:42:37'
updated_at: '2026-09-14 08:43:01'
knowledge_base_refs:
  - docs/knowledge-base/best-practices/prototype-driven-ui-gate.md
  - docs/knowledge-base/retrospectives/sprint-003-retrospective.md
prototype_refs:
  - path: issues/requirements/archive/REQ-0026-requirement-center-standalone-change-cards/prototype/web/prototype.html
    role: html-structure
  - path: issues/requirements/archive/REQ-0026-requirement-center-standalone-change-cards/prototype/web/context.md
    role: decomposition-and-contract
prototype_gate:
  decomposition: done
  ui_skeleton: done
  visual_acceptance_1440: passed
  computed_style: passed
  key_interactions: passed
  req_final_consistency: checked_before_archive
product_data_collection_observability:
  status: applicable
  affected_layers:
    - web
    - api
  reason: 聚合、筛选及独立对象读取授权复用行为与请求日志；无新增DB、部署、存储或异步Task Trace。
  validation: 后端93项、Web77项及项目切换9项回归通过；真实双账号/冻结/拒绝日志与浏览器证据见Change verification.md；OpenAPI/Orval同步，无新增DB/部署/存储/异步Task
    Trace。
execution:
  schema_version: 1
  started_at: 2026-09-12 22:49:59
  completed_at: 2026-09-14 00:14:22
  last_event: opsx.archive
---

# Change 追溯

## 当前摘要

旧范围实施自验完成；本轮阶段按钮已评审并纳入Sprint，新增任务待实施，旧完成时间保留在历史记录。UI策略为当前组件/CSS最小增量；Conflict Resolution、UI Contract、Reference Replication Contract、UI Skeleton见design.md。仅新增原ID下同字号Change ID和替换中文标题，撤销旧原型自建布局。原型全Mock；真实截图、computed style、API观察和实施文档一致性已完成，不把CLI工件完成当作业务完成。

## 验收入口

REQ acceptance.md的11项功能、5项原型、阶段动作增补和返修项为业务验收源；本Change acceptance.md记录映射与结果。截图清单及真实/合成证据见verification.md与evidence/；2026-09-14 用户执行 `/opsx-archive REQ-0026`，作为本轮归档验收确认来源。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-09-12 22:42:37 | req.opsx | CLI创建Change并生成proposal/design/specs/tasks，关联sprint-005；不写业务代码。 |

## 提案阶段验证

OpenSpec strict校验、聚焦中文校验、Sprint scope和产品观测校验通过；CLI四项工件均done，15项实施任务未勾选。全仓中文检查仍发现fix-requirement-center-apply-lifecycle-sync的6个既有英文标题，不属于本Change，未修改。真实UI及API验收尚未执行。

## 实施完成证据

实施、自修、视觉及接口回归见 [verification.md](verification.md)。15项实施、验证及文档任务通过，最终同步串行执行；本次Skeleton已获用户确认，无剩余实现阻塞。

## 最终工作流结果

opsx.apply同步成功，Errors=0；Change与REQ关联均为applied，Sprint显示15/15，REQ acceptance_status=pending。子文档检查无阻塞。AI Usage Hook返回warning/unavailable、command_run_count=0、Sprint快照因no-command-runs跳过；不影响业务交付。临时API与Vite服务已停止，无自动提交、推送、部署或归档。

## 2026-09-13 返修验证

独立Change已使用info蓝框；unknown不再渲染九阶段之外的卡片，保留默认收起的只读数据异常入口，页面统计只计算真实阶段卡片。修正rc-content固定四行网格，改纵向flex，避免可选诊断行及窄屏标题动作遮挡。

证据：用户附件与源码路径已在design.md逐项对照；09-01/09-02同ID归档分别为建立契约/扩展动作矩阵，不是等价副本，保留历史冲突，不自动删除或按日期选版本。核对完成，不宣称历史ID冲突已被修复。

验证：Vitest需求中心与错误回归86项通过；TypeScript通过；后端既有Change身份/归档/权限8项通过。浏览器 `src/web/tests/requirement-center-change-layout.cjs` 四组1440/390深浅主题通过，styles.json和layout/diagnostics截图在logs/req0026-modify/。验证三类边框不同、九阶段DOM、无待核实卡片区、统计一致、仅unknown搜索、诊断折叠键盘与标题统计无重叠。视觉检查已查看1440深色和390浅色截图。首轮夹具缺项目目录上下文导致0卡片已修正；后续视觉发现固定网格重叠，留在本轮自修后重验。

Mock/API边界：本轮视觉采用真实浏览器组件与合成API，不冒称真实数据验收；本地Web服务更新另记。API/schema/权限/后端统计无修改，不需要OpenAPI或客户端重生成；DB、存储、安全策略及Task Trace无新增变更。product_data_collection_observability：applicable，affected_layers：web；复用既有读取请求，无新增埋点或日志字段。

REQ子文档一致性扫尾：已更新requirement、business-flow、user-stories、acceptance、prototype/context及prototype.html意图说明；trace由Workflow Sync更新。capture/review保持历史输入和原评审，不改写历史结论。Change design/spec/acceptance/verification与Sprint验收及release-note同步；Sprint容量、范围、API索引无需更新，原因是原Change内UI返修且接口不变。历史视觉证据不替代本轮截图。

最终补充：BUG-0016错误/详情浏览器4组回归通过。Web生产构建成功并更新既有本地moonbox-web；CUA原tab已不属于当前会话，重新发现超时，未冒称本轮完成用户登录态真实UI观察。本轮截图来自已声明的合成API浏览器测试。OpenSpec严格、目标中文、Sprint scope、diff空白校验通过。

## Sprint 标签返修证据

独立 Change 的 Sprint 标签优先使用合法 iteration 并核对 Sprint changes 成员关系；iteration 缺失、null 或空串时反查活动及归档 Sprint，仅唯一 Sprint ID 可关联。多个成员关系不猜测并提示待核实；显式错误不被反查覆盖。同 ID 活动 Sprint 优先，不从归档补活动缺口。标签不依赖 sprint.md 存在，文档入口仍要求文件可读。

真实仓库只读复核：45 个已完成独立 Change 中40个缺 iteration，40个均恢复唯一归属；build-api-standard → sprint-000。浏览器为真实组件加合成 API 响应，非部署观察；截图和 computed style 在 evidence/sprint-tag/。

product_data_collection_observability: applicable；affected_layers: API。复用现有请求日志与鉴权，直接API/日志失败回归继续覆盖；无新增行为事件、Task Trace 或端侧链路字段，脱敏与保留周期不变。OpenAPI/Orval N/A：字段类型和接口结构未变。

## 阶段按钮增补追溯

原范围completed_at为2026-09-12 23:33:35，保留已完成21项；新增5项待实施，重开当前交付完成门禁。原型拆解完成，新增Skeleton、视觉、样式、关键交互及最终一致性均pending；Mock/API边界及Conflict Resolution见design阶段按钮章节。

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

证据：change_index.py 与 test_change_visibility.py；浏览器 title-fallback 四组1440/390深浅主题截图及styles.json。使用合成API验证组件，未部署18102；归档确认来源为 2026-09-14 用户执行 `/opsx-archive REQ-0026`。
