---
created_at: '2026-09-12 22:42:37'
updated_at: '2026-09-14 08:43:01'
---

# Change 验收映射

需求验收源：issues/requirements/archive/REQ-0026-requirement-center-standalone-change-cards/acceptance.md。

| 验收范围 | 实现任务 | 结果 |
|---|---|---|
| AC-001/003/004/010 独立来源、归档及权限 | 2.1至2.5、4.1、4.3 | 实施自验通过 |
| AC-002/008/011 当前卡片两项调整及原交互 | 1.1/1.2、3.1/3.3、4.2 | 实施自验通过 |
| AC-005/006/007 统计、进度与刷新 | 2.3至2.5、3.2、4.1至4.3 | 实施自验通过 |
| AC-009 观测与契约 | 4.4 | 实施自验通过 |
| AC-PROTOTYPE-001至005、AC-XCUT-001/002 | 1.1/1.2、4.2/4.5 | 拆解、用户Skeleton确认与真实浏览器检查通过 |

原型只作设计输入。最终通过需design、需求验收、1440px/关键交互截图、computed style、Mock/API边界和REQ子文档回填一致；CLI validate通过不代表此处业务通过。

## 实施自验结论

上述范围的合成回归、隔离真实观察与返修回归均通过，证据按verification.md映射。用户已确认首轮Skeleton，并在 2026-09-14 执行 `/opsx-archive REQ-0026` 进入归档闭环；该命令作为本轮业务验收确认来源，后续由 Workflow Sync 回填 REQ acceptance_status。

## 2026-09-13 验收返修约定

独立Change使用主题info蓝色左边框，REQ金色、BUG红色保持。移除九阶段之外的“状态待核实”卡片区；unknown对象仅通过默认收起的数据异常入口查看只读ID/说明，不计入页面业务统计，接口原始unknown和授权保持兼容。搜索/类型过滤同时约束诊断集合，零正常对象时业务总数为0而诊断仍可达。重复归档已核对为不同内容复用ID，保留冲突事实，不按日期任取版本、不删除历史。

验收覆盖1440/390深浅主题、九阶段DOM、三类边框颜色、收起/展开键盘操作、仅异常筛选及正常文档入口；证据见Change返修记录和logs/req0026-modify/。

## Sprint 标签返修验收

独立 Change 的 Sprint 标签优先使用合法 iteration 并核对 Sprint changes 成员关系；iteration 缺失、null 或空串时反查活动及归档 Sprint，仅唯一 Sprint ID 可关联。多个成员关系不猜测并提示待核实；显式错误不被反查覆盖。同 ID 活动 Sprint 优先，不从归档补活动缺口。标签不依赖 sprint.md 存在，文档入口仍要求文件可读。

覆盖缺字段、空值、活动/归档、文档缺失、歧义、显式非法、活动优先与权限不可见；浏览器1440px深浅主题通过，证据 evidence/sprint-tag/。

## 阶段按钮新增验收

REQ AC-ACTION-001至006及AC-XCUT-003全部待实施，映射tasks 7.1至7.5；原证据不覆盖新按钮。完成真实门禁、视觉和文档扫尾前不可归档。

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

证据：change_index.py 与 test_change_visibility.py；浏览器 title-fallback 四组1440/390深浅主题截图及styles.json。使用合成API验证组件，未部署18102；本次归档确认来源为 2026-09-14 用户执行 `/opsx-archive REQ-0026`。
