---
requirement_id: REQ-0026-requirement-center-standalone-change-cards
title: Change 卡片原型拆解与局部一致契约
owner: product
created_at: 2026-09-12 21:17:00
updated_at: '2026-09-14 00:43:26'
---

# 当前卡片两项调整契约

## 范围与事实源

用户本轮反馈优先；当前 src/web/src/pages/catalog/RequirementCenterPage.tsx 的 renderIssueCard 与 src/web/src/styles/globals.css 为结构和样式基准。保真模式为当前卡片局部精确一致：REQ/BUG仅新增 Change ID 行及替换中文标题；独立 Change 另增加文末阶段动作，不重设计页面、卡片或抽屉。

页面为卡片前后对照，不是新看板。左侧显示当前结构，右侧显示调整结果，底部提供长 ID 与无 Change 样例。所有数据为合成样例；无 API 调用。既有按钮保留外观并用演示反馈表示入口，不能宣称已复刻业务弹窗或真实授权。

## 组件与 selector 映射

| 顺序 | 当前 selector | 原型处理 |
|---|---|---|
| 1 | .rc-card-top > strong / .rc-sprint-tag | 原 REQ ID 与 Sprint 标签不变 |
| 2 | 新增 .rc-change-id-row > strong | 插在原 ID 下方；复用 .rc-card-top strong 样式来源，当前字号 10.5px |
| 3 | .rc-card-title | 仅将文本换为 Change 中文标题，字号保持 13.5px |
| 4 | .rc-card-meta / .rc-card-tags | 原 P1 与责任人标签 |
| 5 | .rc-docs / .rc-doc-group | 原常驻和阶段文档分组 |
| 6 | .rc-progress | 原研发、测试、人工验收入口 |
| 7 | footer / .rc-card-actions | 原更新时间和动作 |

原型直接引用仓库 globals.css 和 tokens.generated.css，保留真实级联；仅新增行、演示容器和提示样式。新增行上下间距 4px，长 ID 允许换行，字体、字重、斜体、颜色和行高与原 ID 一致，不增加徽标或复制按钮。

## 状态与数据

无 Change：完全保留原卡片。唯一当前 Change：显示真实完整 ID，中文标题来自同一 Change。缺中文标题：保留 Issue 标题，详情提示。多个关联且当前项可确定：沿用既有上下文；不能唯一确定：原标题保留，新增行提示当前项待核实，不任意取第一项。独立卡片仅有自身 Change ID，不虚构 REQ 行。归档、授权与去重仍按 PRD 验收。

## 动作按钮矩阵

| 动作族 | selector | modal 类型 | 状态与证据 |
|---|---|---|---|
| 标题 | .rc-card-title | 沿用当前详情 | AC-002/011；对比点击目标不变 |
| 文档 | .rc-docs button | 沿用当前文档抽屉 | AC-006/011；来源与权限回归 |
| 进度 | .rc-progress-action | 沿用当前任务阅读 | AC-006/011；进度归属一致 |
| 阶段动作 | footer button | 真实模式保留原提示/任务阅读；Demo模式保留原modal族 | AC-010/011；不得由原型新增写权限 |
| Change ID | .rc-change-id-row strong | 无 | 文本选择复制、无新增动作 |

原型演示反馈不作为现有 modal 的视觉契约，后续使用当前实现的组件族和完整矩阵验证。

## 断点、样式采样与分批验证

1440px 对照两个同宽卡片；390px 对照列垂直排列。卡片宽度由对照容器设定，生产仍由现有看板列控制。采样原 ID、新增 ID 的 font-size/font-family/font-weight/font-style/line-height/color；两行 font-size 必须相等。其余采样 .rc-card、.rc-card-title、.rc-docs、.rc-progress、footer 的 padding/border/radius/background/gap/width/overflow，除新增一行引起的高度增量外保持基准。

批次一：源码/DOM及两项文本差异；批次二：真实 UI Skeleton 的 1440px 深浅主题截图和 computed style；批次三：长 ID、无 Change、多关联歧义及现有入口真实回归。PNG 本阶段暂不要求，旧原型及旧视觉结论已失效。浏览器本地 URL 曾被安全策略拒绝，本次不绕过该限制；此前此阶段只做静态检查；本次apply已在真实应用完成视觉及交互验证，证据见关联Change verification.md，Skeleton已获用户确认。

## 实施验证回填

旧版HTML仅表达两项卡片增量，本轮已追加独立Change阶段样例，API/授权不由HTML模拟结论代替。最终6组1440/390深浅主题证据及computed style位于openspec/changes/add-requirement-center-change-visibility/evidence/ui。原阅读器追溯属性与筛选开关属于实际业务接入，卡片未增加关联面板。

## 2026-09-13 验收返修约定

独立Change使用主题info蓝色左边框，REQ金色、BUG红色保持。移除九阶段之外的“状态待核实”卡片区；unknown对象仅通过默认收起的数据异常入口查看只读ID/说明，不计入页面业务统计，接口原始unknown和授权保持兼容。搜索/类型过滤同时约束诊断集合，零正常对象时业务总数为0而诊断仍可达。重复归档已核对为不同内容复用ID，保留冲突事实，不按日期任取版本、不删除历史。

验收覆盖1440/390深浅主题、九阶段DOM、三类边框颜色、收起/展开键盘操作、仅异常筛选及正常文档入口；证据见Change返修记录和logs/req0026-modify/。

## 已完成独立变更的迭代归属补充

独立 Change 的 Sprint 标签优先使用合法 iteration 并核对 Sprint changes 成员关系；iteration 缺失、null 或空串时反查活动及归档 Sprint，仅唯一 Sprint ID 可关联。多个成员关系不猜测并提示待核实；显式错误不被反查覆盖。同 ID 活动 Sprint 优先，不从归档补活动缺口。标签不依赖 sprint.md 存在，文档入口仍要求文件可读。

## 独立 Change 阶段按钮补充契约

本次范围增补已实施并通过自验，人工业务验收待确认；原已应用 Change 和 sprint-005 关联保留，历史只读版本验收不覆盖新增动作。复用 REQ/BUG 的 footer 位置、按钮样式、弹窗族、权限和执行能力门禁，不另建执行系统。

| 阶段 | 主按钮 | 交互与门禁 | 命令身份 |
|---|---|---|---|
| 待开发 | 开始开发 | 复用 apply 动作弹窗；有写权限、有效 Sprint 纳入及真实能力才可执行；未接入显示禁用原因 | /opsx-apply 加完整 Change ID |
| 研发中 | 查看进度 | 复用 tasks 阅读入口；无 tasks 提示缺失，不生成虚假进度；只读用户可按读取权限查看 | 当前 Change tasks |
| 验收中 | 完成 / 归档 | 复用验收与归档确认交互；测试、人工验收、权限及执行能力全部通过才开放；缺证据不视作通过 | /opsx-archive 加完整 Change ID |
| 已完成 | 无阶段主按钮 | 与当前 REQ/BUG 一致，标题和文档仍可读取 | 无 |
| 状态未知 | 无 | 保留数据异常诊断，不提供流转入口 | 无 |

纯独立 Change 使用自身完整 ID；关联 REQ/BUG 仍使用完整 Issue ID，不伪造来源。只读成员、冻结空间不得执行写动作；无读取权限不显示对象或动作。能力不足明确提示具体原因，不静默无响应。按钮显示不等于具有执行能力；Demo 仅模拟弹窗状态，不调用真实写入、创建会话或修改阶段。真实模式沿用已有执行入口，未接入能力不得伪装成功。提交期间防重入，失败保留上下文，成功后读取稳定快照，不仅靠前端移动卡片。

不新增独立 Change 创建/任意编辑/任务勾选能力，不新增自动发送 Chat 命令或新的后端执行服务。若复用需扩大接口或授权边界，后续评审明确范围后再进入 OpenSpec。

### 本轮原型拆解与复刻种子

保真模式：局部一致。优先级：用户确认的新增范围 → 当前 REQ/BUG 组件结构和样式 → 原型合成示例。页面仍为卡片对照，新增独立 Change 阶段样例区；层级为样例区/阶段卡片/footer/主按钮，弹窗沿用生产组件族而非把原型说明浮层当成生产设计。

| 动作按钮 | modal/抽屉类型 | selector候选 | 状态 | 证据计划 |
|---|---|---|---|---|
| 开始开发 | apply动作弹窗 | .rc-card.change footer .primary；实际modal selector由Change阶段核对 | 可用/能力缺失/只读/提交中/失败 | 截图、命令身份、拒绝请求 |
| 查看进度 | 当前tasks阅读器 | .rc-card.change footer .primary；现有文档drawer | 内容/缺失/无权 | 只读API、归属截图 |
| 完成 / 归档 | 现有验收确认族 | .rc-card.change footer .primary；确认selector由Change阶段核对 | 未验收/可确认/禁用/失败 | 门禁与确认截图 |
| 已完成 | 无modal | .rc-card.change footer | 无主按钮 | DOM数量断言 |

数据依赖：stage、完整ID、读取/写权限、Sprint成员、任务/验收证据、执行能力及禁用原因。1440px并排对照，650px以下单列，390px无按钮溢出；采样font-size、padding、gap、border、color、disabled和modal宽高/overflow。批次为矩阵与Skeleton确认、全动作族实现、真实门禁与视觉验收。本原型用说明反馈演示目标，PNG暂不要求，新范围截图待实现；历史Skeleton确认仅适用于旧范围。


## 阶段按钮实施与证据

阶段按钮已接入：待开发开始开发、研发中查看进度、验收中完成/归档，已完成与未知无阶段主按钮。后端沿用action字段提供完整Change命令和禁用原因；前端同样保守禁用未接入执行能力，不能由响应中伪造action解除门禁。冻结空间返回只读原因；进度按读取权限打开当前tasks，只读文档不允许编辑。无tasks保留现有缺失反馈。

当前独立Change没有真实开发/归档执行服务，因此相关按钮禁用；不开放Demo模拟写入或伪造成功。矩阵中开发/归档modal、提交防重入/成功刷新在本轮不可执行分支为N/A，原因是已批准的能力门禁禁止进入执行分支；不以禁用按钮宣称真实开发或归档已实现。既有REQ/BUG弹窗族与执行交互保持，78项前端回归覆盖其行为。进度复用.rc-drawer、关闭按钮和Escape退出。

用户已确认1440px Skeleton布局；openspec/archive/2026-09-14-add-requirement-center-change-visibility/evidence/actions/skeleton-dark-1440.png与skeleton-light-1440.png为首轮证据。最终1440/390深浅主题4组截图、进度抽屉截图及computed style见openspec/archive/2026-09-14-add-requirement-center-change-visibility/evidence/actions/，真实浏览器组件+合成API夹具，非部署观察。仓库实际索引只读核验48个独立对象、2个有阶段动作、0个写动作开放。

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
