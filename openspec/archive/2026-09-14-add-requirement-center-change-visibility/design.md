---
created_at: '2026-09-12 22:41:21'
updated_at: '2026-09-14 08:43:01'
---

## 背景

REQ-0026 已归档，来源路径为 issues/requirements/archive/REQ-0026-requirement-center-standalone-change-cards/。聚合服务当前仅读取 Issue registry，ProjectReader 对 Change 的读取授权依赖关联 Issue；前端 type 仅有 requirement/bug。既有原型曾另造布局，用户明确收敛为当前卡片上两项修改。

## 目标与非目标

目标：独立 Change 授权可见、关联 Change 身份清晰、归档/状态/进度可追溯，复用当前页面和请求链路。

非目标：新增任意编辑、自动Chat发送或独立开发/归档执行服务、重做卡片和弹窗、创建虚构 Issue、修改正式规格目录或引入数据库迁移。独立卡片不伪造 REQ ID；原 Issue 动作仍使用完整 Issue 身份。

## 设计决策

### D1 当前组件与 CSS 复用

采用 CSS Port 的最小增量策略：继续 renderIssueCard 和 globals.css，新增 .rc-change-id-row 紧随 .rc-card-top，复用原 ID token/规则；仅替换 .rc-card-title 的显示值。拒绝新设计系统或另写卡片/抽屉，因为用户已确认仅两项改动。字号当前基准为10.5px，标题13.5px；最终以当前实现运行时一致性为准。

### D2 完整快照先识别关联再授权

在 ProjectReader 的稳定 Snapshot 上构建一次 Change 索引与 Issue→Change 反向索引，再做可见性裁剪；禁止在已过滤 registry 上判断独立性。索引只存在于当前请求/快照 revision，不跨项目复用可见性结果。

关联证据来自 registry related_change/related_changes、Issue trace openspec_changes 和 Change trace 来源字段。完整 ID 精确匹配，短 Issue ID 仅唯一解析后认可；正文提及不是关联。任一明确关联即排除独立身份，缺失/冲突引用保留受控异常。registry 无法解析继续采用快照失败策略，不输出假空列表或把全部 Change 变成独立。

独立对象先校验当前项目成员/绑定，再通过现有 scope.visible 对 Change 完整 ID 校验；关联对象保留所有关联 Issue 的既有读取限制。列表、文档及异常摘要共用解析与授权；隐藏对象不通过搜索或统计泄漏。对象路径继续白名单、根目录及符号链接约束。

### D3 版本、状态和当前 Change

活动目录优先；归档按日期前缀加完整 ID 精确解析，唯一候选才可读，多归档不任意取值。活动缺文档不回退归档副本。归档唯一项已完成；活动 trace proposed/in_progress/applied 对应待开发/研发中/验收中。未知或冲突状态保留后端unknown事实，仅在默认收起的数据异常入口展示ID和说明，不渲染业务卡片，保留九阶段。

当前 Change 仅在关联集合只有一个候选，或既有上下文能提供唯一、真实且通过关联校验的当前对象时设置；不将 tasks.source 的循环末项当选择证据。多关联歧义时 current_change=null，新增行显示待核实、保留原 Issue 标题，原关联数据仍可通过既有详情追溯。不以排序选第一项，不混用标题与任务进度。

中文标题优先 Change trace 显式中文业务标题，再取 Change 文档有效中文业务标题；排除通用章节标题。所属 Issue 无中文标题时保持原标题并在现有详情提示；独立对象无有效标题时使用完整 ID 回退。tasks 是进度不是验收结果。缺 tasks 返回未知摘要而非0/0完成。

### D4 兼容响应与文档

保留卡片 id 的原 Issue 短显示身份，文档URL与动作继续使用完整 Issue 身份；新增 related_changes 数组（id、中文标题、stage、source_kind、任务摘要及受控文档），current_change 可空及显示异常原因。独立卡片 type=change、id=Change完整ID；原前端类型、缺省样式和动作分支全部审计，不能走 bug 默认分支。

stats 增加 standalone_changes；搜索关联 ID 时匹配所属卡片，独立类型计数只计算独立卡片。相同筛选下九阶段卡片总和等于页面业务统计；unknown只计入数据异常数量，API原始统计不变。无分级的独立对象不伪造P2，UI隐藏无值标签；owner/时间缺失用现有未知表达。

复用 Change 文档路由和右侧阅读组件，Change 文档能力在新增入口均只读；不能经旧写路由新增独立写权限。Issue trace 仍属于 Issue；Change trace 通过既有文档来源上下文区分，不增加重复裸名入口。Sprint 文档先校验 iteration 与 Sprint changes 成员关系，未纳入不阻断只读。OpenAPI/Orval生成、docs/03-api-index.md和相关测试与响应字段一并更新。

## 冲突解决（Conflict Resolution）

优先级为本轮用户明确反馈 > 已修订HTML > PNG（当前无）> context/acceptance > UI规则 > 既有spec。HTML只定义两项视觉增量，Mock按钮反馈不是业务语义；授权、去重和写入边界由PRD及本设计补足。此前自建关联列表和抽屉撤销。旧spec卡片“单pill、蓝色边框”等与当前代码冲突，delta以当前组件为基准；不能借spec迁移恢复旧样式。

独立卡片及未知状态的完整数据逻辑在HTML中未模拟，由本设计/spec/acceptance约束。暂无未解决产品选择；运行时样式、真实权限和多关联数据证据在实施阶段取得。

## UI Contract

范围为现有 /requirements 内卡片；页面壳、品牌、侧栏、工具栏、九阶段列、空态、滚动/sticky保持现有结构。独立类型筛选和收起的数据异常入口沿用现有页面留白，不用原型对照页替换生产页面。

- REQ ID下增加文本行，字体/字重/斜体/行高/颜色复用 .rc-card-top strong；10.5px 基准。长ID允许换行，不缩字号。
- 中文标题仅换字，.rc-card-title 保持13.5px及原点击目标；meta、文档、进度、footer不变。
- 前后台一致性checklist：沿用当前品牌、导航密度、主题、图标、焦点、toast和浮层组件；不新增管理端或独立主题。
- 新增 ID 无点击行为、无复制按钮；使用文本选择复制。现有按钮、modal及权限一并回归。
- Mock/API边界：HTML全部合成数据，仅作设计输入；生产接入真实授权快照，不允许演示数据回退。

## UI Skeleton

组件层级：RequirementCenterPage → 既有看板列/异常集合 → renderIssueCard → rc-card-top → 新增ID行 → 原中文标题 → 原meta/docs/progress/footer。仅添加可测属性 data-change-id，不改变原 data-issue-id。

状态容器：无Change、唯一当前、多关联歧义、独立活动、独立归档、缺标题/文档、未知状态、受限/只读、加载/失败。数据依赖为授权Snapshot与上述响应字段。先用隔离测试样本实现Skeleton，在1440px确认新增行和标题之外无结构改动，再进入业务细节与真实数据联调。

## UI Reference Replication Contract

局部精确一致；组件文件为 src/web/src/pages/catalog/RequirementCenterPage.tsx，CSS为 src/web/src/styles/globals.css。原型来自 linked REQ 的 prototype/web/prototype.html 与 context.md。当前实现是未调整区域的事实源。

| 参考selector | 目标/测试selector | 状态/批次 |
|---|---|---|
| .rc-card-top strong | .rc-card-top strong | 全状态、第一批 |
| .rc-change-id-row strong | 同名 + data-change-id | 唯一/长ID/歧义、第一批 |
| .rc-card-title | 同名 | 有/无中文标题、第一批 |
| .rc-docs / .rc-progress | 同名 | 原阅读交互、第二批 |
| footer .rc-card-actions | 同名 | 原治理动作族、第二批 |
| 当前筛选工具栏 | 新type选项/待核实入口可测标签 | 独立/空结果、第三批 |

### 动作按钮与 modal 矩阵

| 动作 | modal类型/组件族 | selector | 状态 | 证据 |
|---|---|---|---|---|
| 中文标题 | 原详情入口，沿用openIssueDetail | .rc-card-title | 打开/返回 | AC-002/011，原目标不变 |
| 文档按钮 | 既有文档抽屉族 | .rc-docs button | 加载/只读/缺失/拒绝 | AC-006/010/011 |
| 研发/测试/人工验收 | 原tasks阅读定位 | .rc-progress-action | 找到/缺章节 | AC-006/011 |
| footer阶段动作 | 真实模式保留原提示/任务阅读；Demo模式沿用IssueActionDialog动作族 | .rc-card-actions button | 可用/禁用/退出 | AC-010/011，独立对象无新写动作 |
| ID文本 | 无modal | .rc-change-id-row strong | 选择复制 | AC-008/011 |

动作矩阵在第一批核对当前函数/selector，第二批按族一次性验收，不单按钮改造。现有外部关闭浮层保留capture阶段监听及stopPropagation回归。

### Computed style采样

| 页面/视口/主题 | selector及状态 | 属性 | 期望 | 当前值/容差 | 证据 |
|---|---|---|---|---|---|
| /requirements 1440，深浅 | 原ID与新增ID，普通/长ID | font-size/family/weight/style/line-height/color | 两行完全相同，CSS基准10.5px | 运行时待采样；差值0 | evidence/ui/id-style.json |
| 同上及390 | .rc-card-title | font-size/padding/color/line-height | 当前13.5px基准、仅文本变化 | 待采样；同环境差值0 | evidence/ui/title-style.json |
| 同上 | .rc-card/meta/docs/progress/footer | width/gap/padding/border/background/overflow/position | 与变更前一致，允许新增行增加高度 | 待采样；布局坐标舍入≤1px | evidence/ui/card-baseline.json |
| 1440及390，深浅 | 原抽屉/退出交互 | z-index/height/overflow | 保持原组件契约 | 待采样 | evidence/ui/interaction-summary.md |

批次一：反向工程、selector和Skeleton+1440首轮确认；批次二：卡片两项改动与原阅读/动作族回归；批次三：真实授权、归档、筛选与390px。每批截图、样式和版本写入 evidence/ui/，未改区逐项对照。原型无PNG且此前file URL被浏览器策略拒绝；实施时在允许的真实应用验收环境补证，不绕过安全策略。

## 产品数据采集与链路观测

依据 docs/standards/product-data-collection-observability.md。

```yaml
product_data_collection_observability:
  status: applicable
  affected_layers: [web, api]
  reason: 新增聚合类型、筛选及文档对象授权，复用行为事件与请求日志关联。
  validation: AC-009/010验证成功/拒绝请求、直接API、行为字段透传与非法忽略、采集失败降级、日志脱敏；实现后同步OpenAPI/Orval/API文档与测试，当前未执行。
```

DB无需schema/索引/保留周期变更，复用对象授权表，SQLite/MySQL既有兼容路径做权限回归；无新增对象存储或部署拓扑。同步只读请求不新增长任务，因此不新增Task Trace/span；若引入异步工作再补设计与验证。日志不存Markdown全文、凭证或本机路径。

## 风险与取舍

- 隐藏Issue被误判独立 → 全量关系索引先于授权过滤，列表与直接API共享检查。
- 历史归档重名/标题缺失 → 显式异常与安全回退，不猜测当前项。
- CSS复制漂移 → 实现共用当前ID规则；对照样式采样相等。
- Sprint 110%且无fix缓冲 → 不扩展动作范围，不压缩真实验收；新增工作重新规划。
- 同域REQ-0022尚未归档 → 实施前复核最新快照/文档入口，保留其已验证行为，不以旧spec覆盖。

## 发布与回滚策略

无数据迁移。先完成响应兼容字段、类型和UI共同交付，按项目真实回归再进入发布治理；本命令不部署。回滚对应应用版本，不修改项目治理事实文件；拒绝权限和原Issue卡片功能保持。自动提交、推送与生产操作不在本Change文档生成范围。

## 待验证事项

无阻止提案的产品决策。运行时样式基线、真实权限样本与相关模块最新变化由先行任务取证；结果不符合契约时先修复或回填风险，不能跳过门禁。

## 实施核对

真实卡片两项改动及当前样式已验证，详见verification.md。原阅读器内折叠追溯属性承载多Change分别的阶段/进度与来源文档；不增加卡片关联面板或新抽屉。归档筛选复用既有筛选菜单，默认显示。第四个类型按钮使用四列，窄屏看板保留可滚动高度。实测原ID/新增ID均10.5px、标题13.5px；全部样式记录见evidence/ui/final-style.json。

## 本轮验收返修契约

最新用户反馈优先：独立Change蓝色左框；移除主看板下方待核实卡片集合。保留九阶段和原有滚动、列宽、文档操作。未知对象仅通过工具栏下默认收起的“数据异常”原生details查看只读ID/说明，不渲染卡片、不计入业务统计；后端权限与unknown事实不改变。

### 附件截图逐项视觉对照表

| 附件/页面状态 | 对照对象与期望 | 实际与偏差 | 检查方式/selector | 处置及证据 |
|---|---|---|---|---|
| 用户附件1，需求中心深色，原图2378×1612，展示尺寸1920×1301（不推断CSS视口） | 独立Change与REQ颜色区分 | 共同继承金色左框 | globals.css .rc-card.change，采样border-left-color | confirmed；补info蓝色token，1440/390深浅截图验收 |
| 同附件，页面底部 | 九阶段保持完整，不增加待核实卡片区 | 独立section位于board-wrap外，顶左标题与额外卡片破坏留白 | RequirementCenterPage.tsx .rc-unknown-changes；DOM父子关系及padding/overflow | confirmed；移除该卡片区，异常改为紧凑收起诊断入口 |
| 同附件，add-ui-reference-replication-governance | 不把归档歧义作为开发卡片 | 两个同ID归档，directory为空，unknown及未知进度 | change_index.py索引路径、两份proposal/trace | confirmed；09-01建立契约，09-02扩展动作矩阵，是不同内容复用ID；不能任取最新或删除历史，本轮保留冲突事实 |

动作矩阵：数据异常summary → 原生details（非modal）→ .rc-data-diagnostics → collapsed/expanded/empty，键盘Enter及折叠布局验收；无新增弹窗。采样卡片border-left-color、看板grid-template-columns/padding/overflow、诊断width/margin。两批：先颜色与容器，再筛选/统计/unknown与只读文档回归。

视觉自检追加证据：固定四行rc-content网格无法容纳可选诊断行，390px标题动作与统计区域重叠。改为纵向flex，header/stats/toolbar/diagnostics按内容高度排列，看板保留独立横向滚动及最小高度；浏览器增加header底部不超过stats顶部断言。

## 历史冲突纠正补记

2026-09-13 16:00:41：上表的双归档冲突为当时观察。经用户确认，2026-09-02 强化已独立为 `enhance-ui-reference-replication-action-matrix`，初建仍为 `add-ui-reference-replication-governance`；本次身份修正消除该样本冲突，不改变多归档冲突的防御语义。

## 已完成独立变更的迭代标签返修

根因 confirmed：归档独立 Change 缺少 trace.iteration 时，旧实现未反查 Sprint changes 成员关系；且将标签绑定到 sprint.md 可读性。只读样本 build-api-standard 已归档并属于 sprint-000，原响应 sprint_id 为 null。

### 附件截图逐项视觉对照表

本轮无新增图片附件，沿用现有卡片契约；偏差由实际仓库数据和服务响应确认。

| 页面/状态 | 期望 | 实际/偏差 | 检查方式 | 处置与证据 |
|---|---|---|---|---|
| 需求中心/已完成/1440px | 唯一 Sprint 成员显示原样式标签 | 缺 iteration 导致 sprint_id 为空 | change_index.py、归档 trace、Sprint changes；.rc-sprint-tag DOM 与 computed style | 修复数据解析；新增聚焦回归和浏览器证据 |

优先采用合法 iteration 且验证成员关系；只有 iteration 缺失、null 或空串时反查活动与归档 Sprint。唯一 Sprint ID 才关联，多成员提示待核实；显式错误不被反查覆盖。同 ID 活动 Sprint 优先，归档不补活动缺口。标签仅依赖成员身份，文档入口另需 sprint.md 存在。无新动作、modal、样式或权限规则。

## 阶段按钮增补：冲突处理与实现策略

Conflict Resolution：本轮已评审REQ阶段契约覆盖旧独立Change无动作规则；HTML按钮仅演示目标，不是生产弹窗或能力证据。旧截图只覆盖旧范围。D1沿用当前组件/CSS最小增量策略，复用REQ/BUG动作族，不重新设计弹窗。

### UI Contract 与 UI Reference Replication Contract

局部一致：保留页面壳、导航、统计、筛选、九阶段、蓝色边框、ID和文档结构；新增独立卡片footer阶段主动作。业务事实优先用户已评审契约，视觉使用当前REQ/BUG同阶段组件、HTML、context；原型反馈提示不能替代真正modal。

| 动作 | 组件族/modal | selector映射 | 状态 | 验收 |
|---|---|---|---|---|
| 开始开发 | 既有apply动作弹窗 | .rc-card.change .rc-card-actions .primary → 现有role=dialog动作族 | 可用/无Sprint/只读/能力缺失/提交/失败 | AC-ACTION-001至006 |
| 查看进度 | tasks阅读器 | footer主按钮 → .rc-drawer / markdown-drawer | 加载/内容/缺失/拒绝 | 读取权限与当前Change归属 |
| 完成 / 归档 | 既有验收确认族 | footer主按钮 → .rc-dialog-actions | 证据不足/禁用/可确认/提交/失败 | 前置证据、取消、刷新 |
| 已完成/未知 | 无主动作 | .rc-card-actions或数据诊断 | 无按钮 | DOM断言 |

组件来源为RequirementCenterPage.tsx与globals.css；实现前补充实际modal selector与同阶段REQ基线，不凭示例推断已接入。采样1440/390、深浅主题下footer按钮font-size/padding/gap/border/color及modal宽高/overflow：期望与同阶段REQ组件相等，几何容差1px，字体颜色一致；当前值由先行任务采样，证据存evidence/actions/。前后台一致性沿用导航、焦点、图标、toast和浮层退出，不新增管理端样式。

### UI Skeleton 与分批门禁

先完成卡片footer插槽、动作/能力状态容器、modal和drawer映射；数据依赖stage、完整ID、对象权限、项目可写、Sprint成员、任务/人工验收证据、能力和禁用原因。先采同阶段REQ/BUG参考，1440px首轮Skeleton确认后再完成动作族细节；随后覆盖390px、深浅主题、键盘退出、内部点击不误关闭、外部关闭与项目切换。最后运行真实权限/拒绝路径回归及子文档扫尾。

### 数据与执行边界

后端动作元数据沿用既有action字段，明确label/command/disabledReason；不得因type=change无条件抹除，也不得仅靠前端赋予写权限。独立Change命令用自身完整ID。真实未接入能力保持禁用说明；进度按读取权限独立可用。已有执行路径由服务端再次验证对象、项目、Sprint与前置证据；本次不新增执行器。Demo不发送真实写请求、不自动创建Chat或宣称成功。错误防重入并保留上下文，成功读取稳定快照。

product_data_collection_observability: status=applicable；affected_layers=[web,api]；reason=阶段按钮与能力响应涉及交互和请求；validation=核验行为事件/请求ID/拒绝路径/脱敏与采集失败不阻断，已有Task Trace复用。OpenAPI字段结构预计不变，若schema需改则同步OpenAPI、Orval和docs/03-api-index.md及测试；DB/SQLite/MySQL schema、存储、部署、保留周期均N/A，无迁移。

## 阶段按钮实施与证据

阶段按钮已接入：待开发开始开发、研发中查看进度、验收中完成/归档，已完成与未知无阶段主按钮。后端沿用action字段提供完整Change命令和禁用原因；前端同样保守禁用未接入执行能力，不能由响应中伪造action解除门禁。冻结空间返回只读原因；进度按读取权限打开当前tasks，只读文档不允许编辑。无tasks保留现有缺失反馈。

当前独立Change没有真实开发/归档执行服务，因此相关按钮禁用；不开放Demo模拟写入或伪造成功。矩阵中开发/归档modal、提交防重入/成功刷新在本轮不可执行分支为N/A，原因是已批准的能力门禁禁止进入执行分支；不以禁用按钮宣称真实开发或归档已实现。既有REQ/BUG弹窗族与执行交互保持，78项前端回归覆盖其行为。进度复用.rc-drawer、关闭按钮和Escape退出。

用户已确认1440px Skeleton布局；evidence/actions/skeleton-dark-1440.png与skeleton-light-1440.png为首轮证据。最终1440/390深浅主题4组截图、进度抽屉截图及computed style见evidence/actions/，真实浏览器组件+合成API夹具，非部署观察。仓库实际索引只读核验48个独立对象、2个有阶段动作、0个写动作开放。

验证：后端93项（含HTTP权限、冻结只读、日志拒绝与采集失败）、前端78项、TypeScript、浏览器4组通过。未部署、未进行真实开发/归档执行。接口schema未变，无需重新生成OpenAPI/Orval；API行为说明已同步。DB、部署、对象存储、安全策略不变。

## 固定禁用返修证据与契约

confirmed：change_index.action在验收中无条件拼接两条提示，前端actionForStage同样固定禁用，未读取验收事实。本次无新增附件，沿用已确认footer布局。

| 页面/参考 | 期望 | 实际偏差 | selector与检查 | 处置/证据 |
|---|---|---|---|---|
| 需求中心验收中，1440px深浅，历史evidence/actions | 与REQ/BUG共用真实文档门禁及动作入口 | 不论材料是否齐备均禁用 | .rc-blocked、footer .primary；后端action代码 | 移除常量原因，测试齐备/缺失/空文档/只读与实际交互 |

复用现有阶段所需文档与非空判断；不把文件存在声明为测试通过。前端保留真实响应的testProgress/manualAcceptanceCount门禁。真实模式使用REQ/BUG同一动作路由：未支持的阶段点击后显示现有能力提示，不伪造执行。Demo复用既有弹窗族且仅模拟。布局已确认，无需再次确认Skeleton；重跑1440px与关键交互截图。

## 固定禁用提示返修结论

本节替代上一轮独立Change一律禁用的结论。后端复用REQ/BUG阶段必需文档与非空门禁，并核对唯一Sprint；缺失/空文档/只读才返回相应原因，不再固定生成测试核对或能力未接入提示。文档存在不代表测试执行通过；前端复用已有testProgress/manualAcceptanceCount判断，数据不存在不伪造检查结论。

独立Change与REQ/BUG进入同一动作处理器：研发中读取tasks；真实模式中当前未支持的开发/归档动作点击后显示现有统一能力提示，不执行写入；Demo沿用现有弹窗和模拟流转，不接入真实执行。取消、提交防重入和刷新行为复用当前组件，未新增服务或权限。

验证：后端94项、前端79项、TypeScript通过；1440/390深浅主题4组真实组件合成API浏览器验收通过，截图和computed style位于evidence/action-gates/。非部署观察，未执行真实开发/归档。保留现有权限和真实能力限制；新证据替代旧固定禁用截图。

## 独立交付契约返修

截图对照：用户附件中验收列standardize-sprint-default-capacity显示缺acceptance.md，实际trace含验证记录、design含验证约定；unify-issue-classification-metadata已有acceptance.md但截图仍显示旧能力提示。前者confirmed为错误套用Issue文件清单，后者运行版本待定位，不猜测缓存原因。布局沿用已确认1440px深浅主题footer和.rc-blocked，内容偏差以源码/实际Change文件/截图对照，修复验收来源并重取视觉证据。

来源策略：优先尊重trace结构化acceptance_refs（Change内相对Markdown路径）；缺失时使用现有acceptance.md或verification.md；否则仅接受trace中的非空验收/验证记录章节。明确引用缺失不得悄悄回退；非法路径拒绝。证据定位不等于验收通过，空源、缺源或未勾选任务保留具体提示，tasks全勾与applied均不单独产生通过结论。此处不做自由文本语义的自动验收判决。

## 独立交付验收来源返修（当前结论）

验收中不再固定要求acceptance.md：优先校验trace.acceptance_refs声明的Change内相对Markdown路径；显式引用无效、缺失或为空返回具体待核实原因，不回退。未声明时查现有acceptance.md、verification.md，再识别trace中非空“验证记录/验收记录/验证结果/验收结果”章节。不得跨Change或通过绝对路径、父路径、符号链接越界读取。没有证据来源提示待核实，不补建文件；本机制定位证据，不自动判断验收通过，applied和tasks全勾均不代替验收。

真实仓库样本standardize-sprint-default-capacity以trace验证记录作为来源；unify-issue-classification-metadata使用acceptance.md，两者当前源码均无来源阻塞。后端95项回归通过，包含显式引用、缺失、空源、越界与历史trace来源；浏览器复用真实组件+合成API在1440/390深浅主题验收，证据evidence/action-gates，非部署验收。

运行页面核对：用户地址localhost:18102对应moonbox-web，加载index-y8JI4bjc.js，其中无旧能力提示；moonbox-backend镜像动作函数也无旧提示，但仍采用上一版固定acceptance.md清单，尚未部署本次解析。未对运行容器做重建或重启，截图旧提示的实际响应来源仍未取得，不断言缓存根因。

REQ主文档、故事、流程、验收、trace、原型context及HTML已核对同步；capture/review保留历史，不需改写。API既有action字段形状不变，无需OpenAPI/Orval生成；product_data_collection_observability为applicable，affected_layers为api，复用请求日志/授权，验证无越界；无新增DB、部署配置、存储、保留周期或Task Trace。

## 中文标题返修：附件对照与来源契约

|附件/页面状态|期望|实际及偏差|检查方式|处置与证据|
|---|---|---|---|---|
|用户独立Change截图；requirements，深色静态卡片|主标题显示 Issue 分级元数据统一；顶部保留Change ID|两处均为 unify-issue-classification-metadata|对照 trace.md 一级标题与 chinese_title 解析代码|confirmed：解析漏读trace正文，本次修复|

保留trace显式元数据、proposal/design既有优先级，最后读取trace正文一级业务标题；通用章节名不作为标题，不翻译或推测业务名称。仅改变卡片数据文案，沿用既有UI Contract、标题selector、动作矩阵和样式；无需重做布局。浏览器使用合成API验证标题呈现，不能替代18102部署观察。
