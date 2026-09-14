---
requirement_id: REQ-0026-requirement-center-standalone-change-cards
title: Change 可见性与关联追溯业务流程
owner: product
created_at: 2026-09-12 21:17:00
updated_at: '2026-09-14 00:43:26'
---

# 业务流程

## 主流程

```text
进入当前项目
  → 校验空间成员与项目绑定
  → 获取完整稳定治理快照
  → 解析 Issue、Change、Sprint 的结构化关联
  → 识别已关联 / 独立 / 关联异常
  → 按对象授权裁剪（关联识别在裁剪之前）
  → 解析活动 / 唯一归档 / 冲突与状态
  → 生成 REQ、BUG、独立 Change 卡片
  → 统一搜索与筛选 → 阶段及异常集合统计
  → 选择 Change → 文档列表 → 再授权读取指定文档
```

## 两类身份分支

```text
无 Change 的 Issue → 保留原卡片，不显示空关联行
Issue 关联唯一当前 Change → 原 ID 下方增加同字号 Change ID → 标题替换为该 Change 中文标题
独立 Change → 自身 ID 为主身份，不生成虚构 Issue
明确关联但来源缺失 → 保留异常，不转独立卡片
已关联但用户无权 → 不额外生成独立卡片，也不泄漏异常详情
```

## 生命周期与刷新

- 提议态 → 准备开发态；进行态 → 开发中；验收态 → 验收中；唯一归档 → 已完成。
- tasks 全勾选仅更新进度，不触发阶段变更；未纳入 Sprint 仍可只读展示。
- 活动与归档同 ID：采用活动版本并提示冲突，活动缺文档不回退旧副本。
- 多份同 ID 归档：保留一个受控异常摘要，禁用含糊文档入口。
- 状态未知：进入默认收起的数据异常诊断，仅展示只读ID及说明，不渲染卡片、不纳入页面业务计数，不进入采集池。
- 归档迁移及外部写入：等待稳定快照，保留最近完整结果与待同步提示；项目切换后丢弃旧响应。
- 打开文档后发现版本、绑定或权限变化：停止展示旧上下文并提示重新读取，不自动保存或执行动作。

## 交互流程

点击原有标题、文档或进度入口 → 沿用当前详情或阅读交互；新增 Change ID 行是文本，不新增点击动作。

多个关联保留既有关联数据；当前项可唯一确定时 ID、中文标题与内容一致，歧义时保留 Issue 标题并在新增行提示待核实，不任意选第一项。长 ID 可选择复制，不新增复制按钮。类型筛选沿用即时生效方式。

## 与关联需求的差异

本需求没有父需求。与 REQ-0022 共用项目绑定、快照及刷新机制；新增独立 Change 识别与授权、卡片关联 ID 展示。保留 REQ-0022 受控写入边界，不增加任意编辑或自动 Chat 执行；开发/归档按钮受本轮阶段契约约束。与 REQ-0020 共用文档阅读及动作交互模式。

## 数据与观测

前端仅提交项目、对象和文档受控标识；后端决定路径与授权。复用行为关联字段和请求日志，拒绝请求也有安全摘要，日志不含文档正文或主机路径。详见 requirement.md §7 与 acceptance.md AC-009。

## 实施一致性核对

2026-09-12：与add-requirement-center-change-visibility实现核对一致。所属卡片仅增加ID行与替换标题，独立对象只读；多Change进度和来源在原阅读器追溯属性查看，歧义不选首项。类型/归档筛选、状态、权限及刷新已验证。证据见openspec/archive/2026-09-14-add-requirement-center-change-visibility/verification.md，人工验收由acceptance.md承接。

## 已完成独立变更的迭代归属补充

独立 Change 的 Sprint 标签优先使用合法 iteration 并核对 Sprint changes 成员关系；iteration 缺失、null 或空串时反查活动及归档 Sprint，仅唯一 Sprint ID 可关联。多个成员关系不猜测并提示待核实；显式错误不被反查覆盖。同 ID 活动 Sprint 优先，不从归档补活动缺口。标签不依赖 sprint.md 存在，文档入口仍要求文件可读。

## 阶段动作流程

读取授权稳定快照 → 解析 Change 阶段 → 复用同阶段按钮 → 核对读取/写入权限、Sprint、前置证据和执行能力 → 不满足则禁用并提示 → 查看进度打开只读任务 → 可执行动作进入既有弹窗并由用户确认 → 防重入提交 → 成功刷新快照 / 失败保留上下文。已完成与未知状态无流转按钮；Demo 不执行真实请求。

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
