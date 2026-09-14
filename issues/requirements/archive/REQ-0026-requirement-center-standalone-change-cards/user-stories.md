---
requirement_id: REQ-0026-requirement-center-standalone-change-cards
title: Change 可见性与关联追溯用户故事
owner: product
created_at: 2026-09-12 21:17:00
updated_at: '2026-09-14 00:43:26'
---

# 用户故事

在可见性与追溯基础上增补独立 Change 阶段按钮，复用现有动作能力，不新增任意编辑或自动 Chat 执行。

## US-001 找到已授权项目内的独立 Change

作为研发成员，我希望找到已授权项目内的独立 Change，以便即使没有 REQ/BUG 也能读取当前方案与任务。

验收要点：AC-001、AC-004；功能映射：FR-001、FR-002。成功以授权快照与实际展示一致为准，不以原型演示代替生产验证。

## US-002 在原 REQ/BUG ID 下方看到同字号 Change ID，并以 Change 中文标题作为卡片标题

作为产品负责人，我希望在原 REQ/BUG ID 下方看到同字号 Change ID，并以 Change 中文标题作为卡片标题，以便确认交付对象并保留归档追溯。

验收要点：AC-002；功能映射：FR-003。成功以授权快照与实际展示一致为准，不以原型演示代替生产验证。

## US-003 逐个查看多个 Change 的文档和进度

作为验收人员，我希望逐个查看多个 Change 的文档和进度，以便避免把混合任务进度当单个 Change 的结果。

验收要点：AC-006；功能映射：FR-005、FR-006。成功以授权快照与实际展示一致为准，不以原型演示代替生产验证。

## US-004 准确读取活动或归档版本

作为研发成员，我希望准确读取活动或归档版本，以便避免旧副本与当前文档混用。

验收要点：AC-003；功能映射：FR-004、FR-006。成功以授权快照与实际展示一致为准，不以原型演示代替生产验证。

## US-005 按类型及完整或部分可见 Change ID 搜索

作为项目成员，我希望按类型及完整或部分可见 Change ID 搜索，以便找到所属卡片且统计一致。

验收要点：AC-005；功能映射：FR-007。成功以授权快照与实际展示一致为准，不以原型演示代替生产验证。

## US-006 保持项目及对象读取权限

作为空间负责人，我希望保持项目及对象读取权限，以便受限 Issue 不因新增独立卡片而泄漏。

验收要点：AC-004、AC-010；功能映射：FR-008。成功以授权快照与实际展示一致为准，不以原型演示代替生产验证。

## US-007 刷新及切换项目时保留正确上下文

作为前台用户，我希望刷新及切换项目时保留正确上下文，以便避免迟到响应展示其他项目对象。

验收要点：AC-007；功能映射：FR-009。成功以授权快照与实际展示一致为准，不以原型演示代替生产验证。

## US-008 读取、选择复制长 ID 并沿用原文档入口

作为键盘或窄屏用户，我希望读取、选择复制长 ID 并沿用原文档入口，以便完整身份无需依赖悬停。

验收要点：AC-008、AC-011；功能映射：FR-003、FR-006。成功以授权快照与实际展示一致为准，不以原型演示代替生产验证。


## 实施一致性核对

2026-09-12：与add-requirement-center-change-visibility实现核对一致。所属卡片仅增加ID行与替换标题，独立对象只读；多Change进度和来源在原阅读器追溯属性查看，歧义不选首项。类型/归档筛选、状态、权限及刷新已验证。证据见openspec/archive/2026-09-14-add-requirement-center-change-visibility/verification.md，人工验收由acceptance.md承接。

## 2026-09-13 验收返修约定

独立Change使用主题info蓝色左边框，REQ金色、BUG红色保持。移除九阶段之外的“状态待核实”卡片区；unknown对象仅通过默认收起的数据异常入口查看只读ID/说明，不计入页面业务统计，接口原始unknown和授权保持兼容。搜索/类型过滤同时约束诊断集合，零正常对象时业务总数为0而诊断仍可达。重复归档已核对为不同内容复用ID，保留冲突事实，不按日期任取版本、不删除历史。

验收覆盖1440/390深浅主题、九阶段DOM、三类边框颜色、收起/展开键盘操作、仅异常筛选及正常文档入口；证据见Change返修记录和logs/req0026-modify/。

## 已完成独立变更的迭代归属补充

独立 Change 的 Sprint 标签优先使用合法 iteration 并核对 Sprint changes 成员关系；iteration 缺失、null 或空串时反查活动及归档 Sprint，仅唯一 Sprint ID 可关联。多个成员关系不猜测并提示待核实；显式错误不被反查覆盖。同 ID 活动 Sprint 优先，不从归档补活动缺口。标签不依赖 sprint.md 存在，文档入口仍要求文件可读。

## US-008 独立 Change 的阶段动作

作为项目成员，我希望独立 Change 与同阶段 REQ/BUG 使用一致的按钮和反馈，从卡片开始开发、查看进度或申请归档；无权限、前置证据不足或能力未接入时获知原因。验收对应 AC-ACTION-001 至 006；已完成不新增主按钮。

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
