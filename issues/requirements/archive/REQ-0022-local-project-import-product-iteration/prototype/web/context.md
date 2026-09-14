---
requirement_id: REQ-0022-local-project-import-product-iteration
title: 本地项目闭环原型拆解
created_at: 2026-09-11 08:42:14
updated_at: 2026-09-12 17:39:20
---

# 本地项目闭环原型拆解

## 原型用途与事实源

prototype.html 是无需网络的交互草图，所有卡片、差异、时间和结果都是显式模拟数据。仅用于讨论需求中心与 Chat 间的项目绑定、待应用成果、确认和冲突反馈；不访问 API、不执行命令、不写仓库。PNG 当前不要求，真实视觉截图留到 Skeleton 与实施验收；故 Prototype Gate 为 Partially Ready。

UI Reference Replication Contract 种子：保真模式为局部一致。业务约束以 PRD/acceptance 优先；旧组件视觉以 rules/ui-design.md、现有 WorkbenchSidebar.tsx 与 styles/workbench.css 为准；新增流程布局以本 context 和 HTML 为准。规则中引用的 ui-design/ui-design.md 在当前仓库未找到，不能伪称已读取；当前规则 token 和现有工作台足以形成草案，设计阶段核对该引用。

本草图使用文字品牌锚点和精简导航，不作为替换正式 Logo、完整导航、用户菜单、折叠按钮的依据；正式实现复用这些组件。无外部附件、无一对一复刻要求，不牺牲既有会话权限、差异保留、编辑草稿和治理门禁。

## 页面、层级与数据依赖

| 页面/区域 | 层级与 selector | 数据来源与职责 |
|---|---|---|
| 共享壳 | .shell > aside / main；#project-binding | 授权空间/仓库绑定，沿用现有页面路由 |
| 需求中心 | #requirements > .toolbar / .board / .issue | 项目治理快照、同步时间、卡片状态 |
| Chat | #chat > .conversation / .result | 本人会话、所选对象、本轮实际执行状态 |
| 成果预览 | #apply-dialog > header / .dialog-body / footer | 固定成果版本、完整文件集合、源版本与真实 Diff |
| 错误/反馈 | #apply-status / #sync-status / #toast | 操作可信结果、刷新失败与最后成功状态 |

## 状态矩阵

| 族 | 状态 | 草图覆盖与实际规则 |
|---|---|---|
| 绑定 | connected、unbound、forbidden、unavailable | 草图 connected；其余无内容且禁止执行，由实施补证 |
| 同步 | ready、loading、failed、stale | 草图刷新与失败；真实轮询保留完整快照 |
| Chat | idle、running、failed、stopped、unknown、completed | 草图 completed 的待应用成果；其他沿用 REQ-0025 |
| 应用 | pending、applying、conflict、failed、applied | 草图提供正常/冲突/失败三种模拟选择 |
| 按钮 | default、hover、focus、disabled、loading | CSS 与模拟应用覆盖；权限不可用实施覆盖 |
| 文档 | reading、dirty、remote-changed | 草图不实现编辑器；实际保留草稿且拒绝旧基准保存 |

## 动作按钮与 modal 矩阵种子

| 动作 | modal 类型 | 原型 selector → 目标候选 | 状态 | 证据与处置 |
|---|---|---|---|---|
| 卡片进入 Chat | N/A，页面导航 | #open-chat → [data-testid=issue-open-chat] | default/disabled | 对象与仓库参数断言；新增入口 |
| 查看成果 | dialog | #preview → [data-testid=governance-result-preview]；#apply-dialog → [data-testid=governance-apply-dialog] | open/empty/error | 截图、宽度及文件集合；共用弹窗族 |
| 确认应用 | confirm，同一弹窗 footer | #confirm-apply → [data-testid=governance-apply-confirm] | loading/conflict/failed/applied | 真实应用、幂等与冲突断言 |
| 取消/关闭 | dialog exit | #close-dialog → [data-testid=governance-apply-close] | open/applying | Esc、焦点返回；应用中禁用避免误解 |
| 刷新 | N/A | #refresh → [aria-label="刷新需求中心"] | loading/failed | 同步时间、保留筛选与草稿 |

目标 selector 是设计候选，不声称已存在。既有 .rc-sidebar、.rc-nav、.rc-user-menu 映射 WorkbenchSidebar；新增选择器在 Change 设计时冻结。预览使用完整差异，确认会写原仓库，因此保留取消/确认。应用前可点击遮罩或 Esc 关闭；内部点击不关闭，事件捕获覆盖内部 stopPropagation。应用中关闭不作为停止写入能力，草图禁用关闭，生产需沿同一合同。

## 响应式与样式采样

1440px：侧栏 224px，主区 minmax(0,1fr)，两列示意看板；预览宽 880px、最大高视口减 48px。小于 768px 侧栏改为紧凑顶部导航、内容单列、弹窗宽为视口减 24px；正式侧栏响应式仍以现有共享组件为准。

金色、背景、边框、文字和字体沿用规则；按钮圆角 2px，面板不超过 8px，正文 14px/1.45。重点采样 #project-binding、.issue、#apply-dialog、.dialog-body、footer、#toast 的 width、font-size、line-height、padding、gap、border、background、color、position、z-index、overflow；深浅主题分别检查。草图不外载字体，实际字体使用现有资源。

分批验收：①共享壳与项目绑定/同步；②卡片到 Chat；③预览/确认/冲突/失败/完成整个动作族；④390px、低高视口、键盘与草稿保护。每批保留 selector、截图和关键样式证据，不能以“更贴近”代替结论。

## Mock/API 边界与状态语义

HTML 的模拟应用只移动演示卡片并显示模拟完成；不代表实现了恢复、授权、原子性或真实同步。完整产品按 FR-001 至 010 和 AC-001 至 016 接入。执行完成、成果已应用和需求交付完成彼此独立。

## 实施一致性记录（2026-09-11）

实施保留现有正式侧栏、九阶段看板、主题和 Composer。需求中心移除独立 project-binding；同步状态位于工具栏刷新按钮 title，selector 为 [aria-label="刷新需求中心"]；Chat 的项目状态并入现有关联栏，selector 为 chat-project-status（.pg-chat-project），不额外占用顶部独立栏。成果动作使用 governance-result-preview、governance-apply-dialog、governance-maintenance-confirm、governance-apply-confirm、governance-application-state。prototype.html 仍是显式离线模拟，真实 API 与视觉证据位于关联 Change 的 evidence/ui/。


返修冲突消解：最新用户附件1明确移除需求中心连接栏，覆盖旧HTML此区域；HTML中#project-binding现只在Chat页展示。绑定能力和授权边界保留。九阶段与完整仓库计数以REQ看板补充和Change设计为准，草图继续使用离线模拟。新视觉证据为关联Change evidence/ui/modify-board-*，旧需求中心连接栏截图仅作历史记录。


## 首屏加载返修

原型新增“模拟首屏加载”，在现有列内原位占位，不再插入加载面板。真实UI的.rc-loading-number/.rc-loading-count/.rc-loading-card为骨架selector；读屏提示不占布局，容器aria-busy。原型仍为离线模拟；最新证据为Change evidence/ui/loading-*，原成功态截图不替代慢请求证据。

## trace 单入口规则

所有REQ/BUG卡片在所有阶段仅保留一个trace.md入口，读取所属Issue目录的trace.md，标签和标题使用普通文件名；缺失时提示不可用，不回退Change trace。Change trace仍参与内部阶段判断，其他文档入口不变。


### 任务入口原型更新

卡片研发、测试、人工验收入口统一打开关联 tasks.md 的完整 Markdown 文档。加载完成后优先定位匹配章节，其次定位匹配任务并高亮、聚焦；不打开独立进度面板。缺少关联时提示未关联 tasks.md；文件不存在或已移动时提示读取目标缺失；章节或任务缺失时保留完整文档并提示未找到目标，不以计数、历史返修记录或其他文档伪造目标。普通 tasks.md 链接从顶部打开，既有编辑与勾选权限不变。

prototype.html 增加三入口及共用 tasks.md 模拟文档、目标缺失场景。原型只展示交互，不请求真实 API、不写文件；实际源码验收见 Change tasks-navigation 证据。


### Sprint 文档入口契约

卡片 sprint.md 属于关联 Sprint，通过现有 Issue 文档读取接口按当前授权项目解析。展示、读取和缺失校验共用解析：按关联 ID 查活动目录，仅活动目录不存在时查同 ID 归档目录；活动目录缺文件不读取归档旧副本，不回退 Issue、Change 或其他 Sprint。文件缺失时保留明确提示；读取保持只读，trace.md 仍仅属于当前 REQ/BUG。


### 主动作阻塞与消息避让返修

卡片主动作统一使用接口disabled_reason、Issue阻塞和前置文档缺失判断，阻塞提示、按钮原生禁用、title原因与执行前守卫一致；文档仍可阅读，补齐后刷新恢复按钮。Tips位于Agent助手上方并保留安全间距，提高层级；窄屏限制宽度、长词换行，超长消息在受限高度内滚动，不遮挡助手。


### 主文档持续展示返修

REQ的requirement.md、BUG的bug.md一旦在所属Issue中生成，即在全部阶段卡片持续显示并固定文档列表首位，包括迭代规划、开发、验收和已完成。读取始终来自所属REQ/BUG当前目录，兼容Issue归档迁移；不读取Change同名文档。未生成不伪造入口，文件删除后按最新快照移除，已打开入口读取缺失明确提示。仅调整展示与排序，保留既有阶段编辑和只读权限。


### Sprint 文档持续展示

sprint.md在关联Sprint文档出现后于所有阶段卡片持续展示，包括待开发、研发中、验收中和已完成；requirement.md/bug.md仍保持首位。复用关联Sprint读取、只读能力、活动/归档解析及缺失不回退。只扩大展示白名单，不将sprint.md新增为其他阶段的必需文档，不改变阻塞与权限判断。


### 卡片文档分组与排序

常驻区按所属requirement.md/bug.md、关联sprint.md、所属trace.md固定排序；阶段区按当前任务优先排序。待开发proposal/spec/design/tasks；研发和验收tasks/spec/design/proposal；已完成archive/tasks/spec/design/proposal；已评审review优先，其他沿阶段阅读顺序。两个分组之间仅保留4px间距，无分隔线与额外内边距，组内自然换行，单组无空白占位；来源、权限及原必需文档校验不变。


### 文档读取与刷新性能

单次Change文档请求复用同一授权稳定快照的临时目录，避免授权和正文读取重复物化；不引入跨请求缓存，保留项目授权、写入恢复、epoch及绑定版本检查。相同项目的context刷新复用进行中请求，初始加载完成后开始轮询；切换项目及卸载取消旧请求。文档内容/草稿/版本冲突处理与原型布局不变。分段日志仅含服务端request_id、操作名、成功状态及各阶段毫秒耗时，不含文档内容或本机路径。


### 卡片更新时间格式

所有阶段REQ/BUG卡片统一显示“更新 YY/MM/DD HH:mm”，保留真实日期及源时间时分，各字段补零；缺失、无效或仅有日期/时分时显示“更新时间未知”，不补造日期和时间。footer必要时换行，时间自身不拆分，避免窄屏挤压动作。


### 所属需求原型常驻入口

所属REQ的prototype.html及prototype目录内HTML存在时，在主文档后常驻展示；多端以相对路径区分，兼容活动/归档目录。发现与读取共用安全解析，缺失无占位、不回退其他Issue/Change、不扩大必需文档校验。维持项目授权、只读预览和4px紧凑分组。


原型入口标签仅显示区分多端所需相对路径（如web/prototype.html、admin/prototype.html），移除“原型 · ”前缀；常驻位置、排序、URL与预览权限不变。
