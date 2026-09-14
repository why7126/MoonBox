---
note: 11/11 Change 已归档，Sprint 关闭验收通过；AI 用量采用估算回退。
sprint_id: sprint-004
status: passed
lifecycle_stage: archive
created_at: 2026-08-31 08:39:23
updated_at: 2026-09-14 00:07:19
---

# sprint-004 Acceptance Report

## 验收范围

<!-- workflow-sync:acceptance-scope:start -->
REQ-0023、REQ-0024、REQ-0025；11个 Change、142项任务，均完成并归档。
<!-- workflow-sync:acceptance-scope:end -->

## 验收结论

最终验收通过（2026-09-14 00:05:53）：11/11 Change 已归档，142/142 任务完成，REQ-0023、REQ-0024、REQ-0025 均已闭环。以下分批记录保留各阶段历史状态，最终交付以归档 Change trace 与本节为准。

## 返修验收摘要

| Change | 反馈 | 处理 | 证据 |
|---|---|---|---|
| `update-product-workbench-modern-ops-visual-system` | 移动端挤压、Kanban 空列承载、筛选 Popover 密度、右下 AI 入口位置需继续贴近附件 | 已完成同范围 UI 返修，不改变 API/DB/权限/部署边界 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/` |
| `update-product-workbench-modern-ops-visual-system` | 需求中心右侧内容标题区需保持与后台用户/空间管理 `admin-page-head` 一致，不需要分隔线、sticky 顶栏感、半透明背景和 blur | 已仅调整标题区布局；指标卡、Kanban 列头、左上品牌区和其它视觉系统保持不变 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 前台左上 Logo、产品名、副标题与后台存在视觉差异；副标题需保留前台业务语义 | 已仅调整前台品牌区视觉规格；保留 `OPS WORKBENCH`，不改其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 前台左上版本号高度、展开与收起按钮与后台存在差异 | 已仅调整版本号高度和 collapse 按钮基础态/折叠态；不改其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 九阶段看板视觉与附件仍有差异 | 已仅调整九阶段看板列宽、列距、列头、标题/副标题、count、列体 padding 和空列承载；不改其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 用户补充两张截图后确认九阶段看板暗场质感仍有较大差异 | 已仅调整九阶段列实线面板感、列头分隔、空列大面积承载框、count 紧凑状态牌和卡片视觉；不改其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`requirements-board-scrolled-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 用户最新截图确认九阶段看板仍像深色表格列，需重构列结构表达 | 已取消完整列面板和强竖向边界，列头作为暗场浮动标题，非空列靠卡片承载，空列由列体自身形成大面积虚线框；不改其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`requirements-one-card-empty-columns-1440.png`、`requirements-board-scrolled-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 九阶段列头字号和上间距偏大，空列缺少阶段差异化占位文案且结构与非空列不一致 | 已压缩列头字号和上间距，为 9 个阶段渲染真实差异化空列文案，并统一空列与非空列的列体结构；不改其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 九阶段空列颜色仍偏蓝灰抬升，斜线纹理和金色虚线边框对比偏强 | 已仅调整空列底色、斜线纹理透明度和虚线边框混色，降低抬升感和金色对比；不改其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 空列仍像独立蓝灰面板，承载框和斜线纹理存在感过强 | 已移除空列斜线纹理，背景贴近页面暗场，虚线边框改为低对比冷灰且不含金色；不改其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 空列仍未符合预期且上一轮误伤列头冻结能力 | 已恢复九阶段列头冻结；空列取消完整大矩形框和独立背景，仅保留低存在感暗场占位与现有阶段文案；不改其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 九阶段列头冻结后出现内容穿透，任务卡文字与列头文字重叠 | 已为 sticky 列头增加页面暗场遮挡背景，保持无强分隔线、无实心面板感；不改其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | sticky 列头冻结边界仍有卡片顶部和文字露出 | 已为列头增加上下扩展的暗场遮罩缓冲区，并补充纵向滚动边界截图证据；不改其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-sticky-head-boundary-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | sticky 冻结边界仍有列间空隙和顶部 padding 穿透 | 已改为看板层横向连续暗场遮罩带，覆盖列头上下边界、列间空隙和顶部 padding；不改其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-sticky-head-boundary-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 连续遮罩方案导致卡片信息被遮住，部分列头滚动表现不一致 | 已移除独立大面积遮罩，改为 header/body 分离与列体内部纵向滚动；不改其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-sticky-head-boundary-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 空列应按最新附件样式展示，保留大面积低对比虚线承载框；此前测试错误固化了无框透明状态 | 已恢复空列冷灰虚线承载框和近暗场轻量背景，并同步更新测试契约；不改列头、卡片、sticky、筛选区、指标卡、品牌区和其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 空列占位文字字体仍偏普通 UI 文本，与附件空态文字气质有差异 | 已将空列占位标题和说明文字切换为现代 Ops 技术感字体 token，并补充 strong/p computed style 证据；不改字号、颜色、框体、列头或卡片 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 需求中心标题区英文小标题需由 `MoonBox Ops` 改为 `Requirement Operations` | 已仅替换标题区英文小标题文案，并补充回归断言和 1440px 视觉证据；不改标题区布局、字体样式或其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png` |
| `update-product-workbench-modern-ops-visual-system` | 新建 Capture 入口按钮与附件 `.btn-new` 不一致，需为金色实心按钮、深色文字、贴近附件尺寸/圆角/间距和 hover 上浮 | 已仅调整需求中心右上新建 Capture 入口按钮，并补充样式契约测试、1440px 截图和 computed style 证据；保留现有点击打开 Capture 表单能力，不改弹窗和其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 九阶段列头需与附件 `.col-head/.col-name/.col-tags/.col-count` 保持一致 | 已仅调整列头 baseline 对齐、附件式 padding、14.5px 标题、Space Grotesk 标题字体、JetBrains Mono 副标题/count、紧凑 count pill 和 filled/empty 状态；保留 sticky 与 header/body 分离，不改空列框体、卡片和其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 最新空列占位符截图显示空态应对齐附件 `.empty-state`，此前空态仍存在 mono 字体、CSS 小圆和说明块被拆散的问题 | 已仅调整空列占位符：1.5px 冷灰虚线框、12px 圆角、`◌` 图标、body 字体和合并说明块；不改列头、卡片、sticky、筛选区、指标卡、新建 Capture 按钮、品牌区和其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 九阶段任务卡片与附件相比偏重，状态条、圆角、标题、padding、分隔线和状态信息视觉权重需轻量化 | 已仅调整卡片视觉：3px 状态条、11px 圆角、13.5px 标题、收紧 padding、低权重分隔线和进度状态框；保留 sprint、研发/测试进度、缺失文档、文档入口和动作能力，不改列头、空列、sticky 和其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 任务卡片 `P1 · 产品团队` 合并标签与附件中两个独立 tag 的展示方式不一致 | 已仅调整卡片标签结构和样式，将优先级与负责人拆为两个独立 tag，并对齐附件 gap、padding、圆角、技术字体和轻量视觉权重；不改列头、空列、sticky、卡片其它区域和其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 任务卡片内部信息拥挤，文档默认下划线、研发/测试/人工验收分散成多块，缺失文档提示位置滞后 | 已仅调整卡片内部信息布局：卡片高度保持内容自适应；文档链接默认无下划线、hover/focus 才显示；缺失提示前置到文档后；研发、测试、人工验收合并为同一行轻量进度信息，并保留研发进度点击能力 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | ready 阶段列多卡片场景中 footer/action 贴近卡片底部，底部卡片在列体视口中仍有视觉裁切感 | 已保持 9 阶段共用卡片组件，将卡片内部改为稳定垂直 flex 流，增加卡片底部 padding 和列体底部滚动缓冲；不改卡片信息顺序、列头、空列、sticky 和其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 九阶段卡片仍存在固定高度感，且文档、缺失提示、进度行、更新时间/action 的行间距不一致，部分阶段长内容仍可能压到 footer | 已保持 9 阶段共用卡片组件，取消旧 `min-height: 150px` 固定感，统一信息栈间距并修正后置 CSS 覆盖；长标题、多缺失文档、多进度信息时卡片由内容自然撑高，footer/action 保持在卡片内部 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 最新截图显示ready 阶段列卡片被压成横条，用户明确要求按研发中卡片样式展示 | 已纠正上一轮过度取消基础高度的副作用：以研发中卡片为视觉基准，恢复合理基础票据高度，列体改为纵向列表，卡片禁止被列表压缩；长内容仍通过 `height:auto` 自然增高 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-board-scrolled-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 指标卡第 3 行 `flow/scope/quality/risk` 装饰标签信息冗余 | 已仅移除指标卡第三行装饰标签，保留标题与数值两层信息结构，并收紧卡片高度和 padding；不改 Kanban、筛选区、新建 Capture、品牌区和其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 每个阶段首张卡片需要与空列顶部对齐 | 已仅统一九阶段列体首项顶部基准：空列移除额外 margin，并通过同一 20px 顶部基准绘制虚线承载框；不改列头、空列文案、卡片、sticky、筛选区、指标卡、新建 Capture、品牌区和其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-one-card-empty-columns-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 9 个阶段的列间隙比较大，需要更紧凑 | 已仅将 `.rc-board` 横向列间距从 16px 下调到 10px；保留 9 列 320px、row-gap、列头、空列、卡片和其它视觉系统不变 | `src/web/src/styles/globals.css`、`src/web/src/requirement-center.test.tsx` |
| `update-product-workbench-modern-ops-visual-system` | 新增 Capture 需要按照附件 modal 完整实现 | 已仅调整需求中心新增 Capture 弹窗：补齐附件式三层标题、类型切换、标题、描述 200 字计数、负责人、来源、P0-P3、footer 快捷键提示、Esc 关闭和 Cmd/Ctrl+Enter 创建；保留点击入口和提交插入采集池能力，不改其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-capture-modal-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 新增 Capture 弹窗需删除 eyebrow 与 footer 快捷键提示，并为类型/标题/来源/优先级标注必填 | 已仅调整新增 Capture 弹窗文案和必填标识：删除 header eyebrow、删除 footer 快捷键提示，为类型/标题/来源/优先级显示红色 `*`；保留快捷键行为、点击入口和提交插入采集池能力，不改其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-capture-modal-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 9 个阶段右下角 Agent 助手按钮需按附件实现对应 UI 交互 | 已仅调整需求中心右下 Agent 助手入口与对应交互：右下金色 pill 点击后打开居中 Agent 操作面板，承载 9 阶段当前可执行动作与上下文提示，并复用既有阶段动作、确认弹窗、toast、任务进度和 AI 消息能力；不改九阶段列头、空列、卡片、指标卡、筛选区、新建 Capture 或品牌区 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-agent-modal-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 九阶段卡片动作按钮需参照附件 Action Modal 组件族实现弹窗交互 | 已仅调整卡片动作按钮触发后的弹窗承载：分析、生成、完善、评审/确认、加入迭代、生成 Opsx、开始开发/修复、查看进度和完成/归档均进入附件式 Action Modal，并复用既有阶段动作、toast、任务进度和 AI 消息能力；不改看板静态视觉和其它系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-action-analysis-modal-1440.png`、`requirements-action-generate-modal-1440.png`、`requirements-action-complete-modal-1440.png`、`requirements-action-sprint-modal-1440.png`、`requirements-action-opsx-modal-1440.png`、`requirements-action-progress-modal-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 需求分析 Action Modal 的解决方案要点需要支持勾选 | 已仅修正分析 modal 要点勾选：三条默认全选，支持取消/重新勾选，底部主按钮实时更新 `采纳 n/3 项并保留分析 →`，0 项禁用；不改其它 Action Modal、看板、卡片静态样式或其它视觉系统 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-action-analysis-selection-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 已完成卡片不需要显示进度信息或 `查看归档` 动作 | 已仅调整 `done` 阶段卡片展示：隐藏研发/测试/人工验收进度和 footer 动作按钮，保留 `archive.md`、`trace.md` 与基础信息；不改其它阶段卡片、看板、Action Modal 或其它视觉系统 | `src/web/src/requirement-center.test.tsx` |
| `update-product-workbench-modern-ops-visual-system` | 加入迭代弹窗需按附件 `sprintModal` 一比一收敛结构与样式 | 已仅调整加入迭代 Action Modal：补齐对象 label 与左侧金色边对象信息块、`加入现有迭代 / 新建迭代` 文案、现有迭代 radio、状态 pill、容量 used/total、capacity bar、容量不足 disabled/badge，以及新建迭代编号和确认按钮禁用/文案联动；不改其它 Action Modal、看板和静态视觉 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/requirements-action-sprint-modal-1440.png`、`computed-styles.json` |
| `update-product-workbench-modern-ops-visual-system` | 任务卡片进度行 `x/x` 数值颜色与字重被回退，需恢复附件 `.card-metrics b` 分层 | 已仅恢复进度行 JetBrains Mono、10.5px、10px 纯 gap、label 低对比和 value secondary + 600 字重；保持无特殊符号分隔和点击行为不变 | `openspec/archive/2026-09-13-update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/computed-styles.json`、`src/web/src/requirement-center.test.tsx` |

## 本次新增范围验收状态

REQ-0025-chat-workbench 已纳入 sprint-004，验收未开始；34 条功能 AC、8 条横切 AC 和8条原型 AC 均不得据此标记通过。评审 RC-001至RC-004仍需接入、配置、入口和视觉证据。事实源：issues/requirements/archive/REQ-0025-chat-workbench/acceptance.md。历史视觉系统返修结论仅适用于原范围，不覆盖新加入的 Chat 能力。


REQ-0025续作：会话管理、鉴权事件读取和内部预留事务已验证，Change进度4/25；SQLite Chat13+API20，MySQL Chat13，前端Chat14+既有64通过。9张合成数据视觉截图见Change evidence/session-ui。实际18102登录态空间/历史读取正常，无仓库时新建禁用。真实执行worker与完整AC未完成，不能进入归档。


REQ-0025执行增量：Change6/25，新增完成存储模型2.1、事件/Diff2.5。48项常规后端检查、独立MySQL16项和单独真实模型1项通过；真实用例含两轮及原线程恢复。平台隔离与其他AC未完成，未进入归档。证据见Change trace的App Server增量段及evidence/backend/real-runner.json。估算暂沿用13人天，尚无证据支持扩大Sprint范围。


REQ-0025本轮连续apply检查点：12/25任务已验证。新增对象/快照/撤权、重试/停止结算、当前代码删除保护、治理只读策略、观测与完整UI动作族。后端41项、前端79个不同用例、真实本机双轮及双容器隔离均有证据，23张合成数据视觉截图见Change evidence/session-ui。正式平台认证与仓库绑定尚未提供，额度/删除时限按用户决定暂不配置，正式执行与实际副本清理未验收。Change保持in_progress，不能归档。

### REQ-0025 共享侧边栏补充验收

需求中心与Chat侧边栏已提取共享组件，87项相关Web测试通过；52张双页与账号动作截图、12组computed对照、23张会话回归截图通过。仅隔离Web重新部署，证据见add-chat-workbench-codex/evidence/sidebar-ui/verification.json。当前13/26任务完成；平台执行认证/仓库/副本清理及暂缓额度时限仍未闭合，Sprint不据此宣称交付完成。


REQ-0025本批五步隔离验证完成：真实Web/API/worker双轮及停止、原线程恢复、账号/凭证隔离和临时环境清理通过。RC-001 Spike关闭，Change整体14/26保持in_progress；一个中止轮次未返回用量，保留待对账事实，未按零结算。不是正式发布或applied完成。证据见openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/live-web-execution/verification.json。


### Chat恢复与清理补验（2026-09-09）

REQ-0025受控验证新增独占进程组守护、可信副本清理回调和失败重试，清理状态仍受当前空间权限控制。无DB结构或API字段变更。MySQL 8.2独立容器32 passed/1 skipped，SQLite后端回归46 passed/1 skipped，新增清理权限聚焦2 passed。非root只读镜像重启后保留unknown活动锁，不自动重领。真实Codex线程历史删除通过，但实际备份适配、正式平台配置与模型容器执行未完成；证据见openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/recovery-cleanup/，不代表正式发布。


### REQ-0025推荐组合落地（2026-09-09）

新增6.1/6.2受控验收完成，累计18/28项。SQLite恢复删除不复活、独立Linux容器真实双轮/续接/停止及后端claim/Diff/21621 tokens结算通过。正式对象存储备份和共享认证/额度/期限仍未完成，不自动进入applied或归档。product_data_collection_observability=applicable，affected_layers=[db,request_logs,task_traces,task_trace_spans]，沿用可信运行记录与脱敏证据。详见Change evidence/recommended-deployment/和trace。

本批最终兼容回归：后端51 passed/3 skipped，独立MySQL 8.2矩阵33 passed/1 skipped；SQLite本地备份4项通过。所有跳过的显式真实测试均与单独运行证据区分，详见Change evidence/recommended-deployment/verification.json。


### REQ-0025日常部署脚本验收（2026-09-09）

add-chat-workbench-codex任务6.3完成，累计19/29项；11项脚本、5项控制通道、5项备份/隔离回归通过。完整--chat-test构建和启动、真实登录、备份删除重放、worker清理及幂等启停通过；测试数据与服务已清理，常规服务健康保留。无新增模型轮次、API字段、业务表或UI改动。证据见Change evidence/deployment-scripts/；正式认证/运营配置、MySQL/S3恢复及全量上线验收仍未完成，整体acceptance保持pending。


### 终态并发释放补充（2026-09-09）

REQ-0025当前Change任务2.4内的终态并发占用缺陷已修复，整体19/29不变。SQLite聚焦38 passed/1 skipped、MySQL36 passed/1 skipped；Chat回归59 passed/5 skipped，进程守护2项受沙箱限制后获准复测通过。实际旧终态补偿保留未知Token，新环境真实停止和后续发送均通过；正式上线验收继续pending。


### 执行进程计量范围补充（2026-09-09）

REQ-0025本批关闭任务2.3/2.4/3.1/4.3/5.5，累计24/29。计量进程范围根因confirmed并修复；真实协议3轮、真实claim2轮计量一致、真实双标签页200/409仅一轮且重启不重放。SQLite42 passed/1 skipped、MySQL39 passed/1 skipped、Web22 passed，OpenAPI契约无变化。验收映射全部完成，功能AC-023/031/033/034及原型004仍未通过，正式认证/配置/部署事实阻塞整体完成。证据见Change evidence/usage-scope/。


### 单机常驻方案确认（2026-09-09）

用户已明确采用单机 Docker Compose、SQLite、本地独立备份、本机 Codex 认证单文件，取消用户/空间额度、并发和存储运营上限。显式 unlimited 与缺失配置区分，仍计量结算；同会话互斥、权限、未知态和单轮结果处理技术边界保留。历史及备份不自动过期；主动删除仍记录和跟踪主存储/执行线程/备份，副本无固定删除截止时间，旧备份物理移除前保持待清理。单机控制器顺序处理持久队列，容量不足不绕过隔离。正式仓库路径及空间映射尚待提供，当前不宣称正式服务已开放。方案细节以 docs/02-deployment.md 的单机常驻章节为准，替代此前“认证、限额和期限尚未决定”的当前态描述；历史证据保留。


### 实际单机部署检查点（2026-09-09）

用户指定当前MoonBox项目仓库及MoonBox空间。读取实际后端确认唯一空间编码moonbox对应显示名“AI原生软件工厂”，未新建或重命名空间。私有env保存仓库/空间映射、local-codex和unlimited策略，原env有私有备份；路径、ID与凭证不复制到治理证据。根up/down可根据已保存执行模式自动加载常驻Compose覆盖文件，脚本4项回归通过。

实际根up部署完成，API、Web、MinIO、Chat Worker均healthy；控制器非root，单认证文件只读挂载，API无认证文件及Docker socket，后台就绪摘要/空间权限/未配置仓库拒绝和独立备份日志核验通过。所选仓库已提交树1573文件、38876348字节成功初始化干净独立基线，源目录未改动，未提交代码不自动导入。证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/target-deployment/。

任务5.4完成，整体28/29；5.6最终当前账号端到端验收和完成同步仍待登录。现有浏览器会话失效，使用已配置初始密码的一次登录返回401，不再重试、不重置账号、不伪造会话；已打开正常登录页并请求用户自行登录。独立环境的真实双轮/重启/删除恢复证据承接上一批，不冒充本次用户账号下的实际发送。常驻服务保留运行，不清理业务数据；下一动作是在当前有效登录下验证发送与刷新恢复，再执行最终完成同步。未执行applied/归档及完成AI Usage钩子。

product_data_collection_observability：status=applicable；affected_layers=[request_logs,task_traces,task_trace_spans,db]；reason=实际部署接入和身份验收；validation=仅保存部署布尔结果和计数，初始密码及日志未外泄；后台只读检查不伪造用户行为，尚无本批真实用户轮次。不涉及公开API字段、业务schema或客户端重生；UI布局不变，既有原型证据继续适用。

执行链路复盘：REQ-0025-chat-workbench → add-chat-workbench-codex → sprint-004，in_progress/acceptance=pending。仓库和空间依赖已解除，剩余是当前有效账号登录；建议以空间唯一编码辅助解析显示名称，本批已交叉核对，未自动创建Issue/Change。


REQ-0025最终当前账号验收：用户重新登录后，在实际moonbox空间及指定仓库完成两轮真实消息，结算14969/15189 Tokens，刷新恢复、无重复轮次、互斥释放及空Diff通过。来源Change evidence/target-deployment；此前“等待登录”检查点已解除，常驻服务保持运行。

## 2026-09-10 执行展示返修

连续相邻、同消息和同执行轮次的文字事件归并显示；工具/状态/消息身份变化及序号缺口保留边界。原始事件默认折叠，保留最近1000条窗口说明。所选轮次当前状态单独展示，时间线状态明确标为历史。安全Markdown新增表格（表头、对齐、转义管道、行内代码、空单元格），窄屏在表格内滚动，保持HTML/图片/危险链接不可执行。旧事件缺少消息身份时仅按连续区段归并，不伪造缺失边界。

本次只改变Web展示，事件持久化、SSE、API、DB、鉴权、停止/重试、Token计量不变，无需迁移或客户端生成。文件路径链接不在本次范围。

### 本次返修验证结果

8个测试文件27项通过，TypeScript及Vite生产构建通过；Web已重新构建部署。合成API搭配实际部署Web的1440/390深浅主题8张截图、computed style及无页面溢出检查通过，12个原始事件显示为5组，原始事件默认折叠/展开通过。首轮截图发现深色表格文字被全局样式覆盖，已显式继承rc-text并重新构建复验。证据：openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/event-display/verification.json、events-dark-1440.png及同目录其余截图。附件对照三项均已修复；无新增modal，原停止/重试测试通过。

当前应用内浏览器认证失效，未读取现有真实会话；视觉数据为合成，不声称本批真实模型执行通过。数据层与执行协议未变，现有消息及事件在重新登录并刷新后使用新渲染。未请求重新登录作为修复阻塞；无发消息或模型用量。


## 2026-09-11 验收返修：Harness 对话与轨迹

以本机 DeepSeek Harness 的对话/轨迹结构为新参考，保持 MoonBox 共享导航与空间/对象权限。对话为右侧用户气泡、无边框助手正文、紧凑自适应输入、消息复制与本轮轨迹入口；Enter发送、Shift+Enter换行、中文输入法不误发送。活动轮次显示过程摘要，失败附着轮次。消息历史加载更早页，滚动阅读不强制跳底；轨迹标签隐藏保留阅读状态。

轨迹包含按原标识配对的工具节点、搜索、内容折叠、事件概览与可调整宽度的详情。详情提供概述、参数、结果、Schema可用性及计时；窄屏上下排列。现有停止确认、原轮次重试、引用快照及Diff保留。事件每窗口最多1000条，可以读取后续窗口或从头查看；窗口边界缺少工具开始记录时不伪造开始时间。旧数据未采集字段明确显示不可用。耗时概览按对数缩放并显示说明，不冒充模型请求计时。

新增工具详情仅存于本人会话事件JSON：白名单参数、截断输出、退出码、状态、记录时间和耗时来源。先脱敏再限长；不新增表/接口/认证/部署范围。平台日志与审计不记录这些正文。明确final_answer可用时最终消息使用最终正文，其余过程留在轨迹；旧协议保持兼容。Schema、模型请求层级、缓存率、内部推理不编造，也不增加模型切换、附件、分支入口。

验证：前端31项聚焦回归通过；后端工具/权限/结算聚焦回归与构建记录见本批最终验证摘要。真实组件+合成API在1440桌面和390窄屏深浅主题观察；样式与无横向溢出记录于 openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/harness-trajectory/verification.json。未宣称与参考逐像素相同，原始参考截图含私人路径而未落盘。新一轮真实模型执行与合成视觉验收明确区分。


### 本批最终验证与一致性扫尾

后端48 passed、1 skipped（需显式启用的真实模型测试）；前端31 passed，TypeScript及生产构建通过。工具详情通过模拟App Server→Worker→真实测试数据库的入库、脱敏、结果、退出码及耗时断言；不冒充本轮真实模型验证。Web与Worker按原Compose配置更新并健康，更新前活动运行数为0；运行Worker的execution.py和tool_record.py摘要与工作树一致。原有recovery容器保留。

REQ 子文档一致性扫尾：requirement、business-flow、user-stories、acceptance、prototype/web/context已同步；trace由工作流同步。prototype.html保留原始历史参考，不覆盖附件来源，新基线冲突与覆盖范围记录在context和design。Schema、模型请求级分组、内部推理、附件与分支不属于本批；界面明确不可用，不伪造采集。产品数据采集影响声明承接本次design契约，无新表或OpenAPI结构变化，不需迁移或Orval再生成。既有SSE payload为开放JSON，本次字段说明同步API索引和DB设计。

本Change严格规格、中文优先、目录、Sprint scope与上下文预算检查通过。全仓中文优先校验被另一活动Change的既有英文标题阻断，未修改无关Change。浏览器验收为合成API配合真实组件，1440/390深浅截图已在工具输出中观察，脱敏样式摘要为长期证据；尚未进行与DSH逐像素差异断言。


## REQ-0025 首次输入返修

进入可输入与无弹窗新建、失败幂等纳入原Change验收；测试及视觉证据见add-chat-workbench-codex/evidence/first-send/verification.json。无新需求或新部署边界，未归档。

本批最终验证：前端23通过，后端39通过/1跳过；1440/390深浅合成接口视觉验收完成。Web/API更新健康且幂等字段已核对，完整证据见上述JSON。


## 顶部精简验收调整（2026-09-11）

Chat移除顶部空间工具栏和项目连接栏；会话标题行仅承接原展开/收起按钮，历史和新建动作保留。空间和主题通过共享侧边栏菜单切换。当前唯一授权仓库自动选中，首次发送创建会话；多仓库保留输入区选择，无仓库仍显示真实不可用原因，不硬编码仓库路径或绕过权限。消息区填满剩余空间、输入卡居中，切换轨迹不丢草稿。


## 会话标题与历史入口返修（2026-09-11）

已创建会话的标题及编辑图标作为重命名入口，复用既有弹窗；空草稿显示“新会话”，首次发送创建后才可改名。删除标题下拉及快速切换弹窗，其他会话统一从历史弹窗选择。移除对话/轨迹栏常驻“个人会话”标签，权限说明保留在历史弹窗：仅本人可查看，同时遵循空间、仓库与关联对象权限。保存成功同步标题及历史，空白禁用保存，失败保留编辑内容，取消不修改。后端权限校验及接口无变化。


### 输入框提示精简返修（2026-09-13）

输入框正常就绪时不显示常驻执行说明或空提示节点；仅保留服务未就绪、归档、原运行未终止、缺少仓库及发送失败提示。发送按钮在有无提示时均右对齐，权限校验与请求流程不变。

验证：Composer 6项测试、TypeScript和生产构建通过。1440×900及390×844深浅主题截图已在浏览器工具观察；正常态hint节点不存在，右边界差0px，无横向溢出。真实组件配合合成API，未触发真实执行。


## 归档前文档引用复核

ready 阶段列对应界面中的“待开发”列。上述记录描述历史 UI 偏差及已完成修复，并非尚待实施任务；陈旧扫描的 `待.*(?:开发|实现)` 曾误命中原列名。本次仅澄清表述并将已归档视觉 Change 的证据引用更新为实际归档路径，保留历史验收结论。


## Sprint 关闭验证摘要

- 严格归档 readiness、陈旧扫描、目录结构、环境忽略、Change 身份与中文优先校验通过；两个本次归档 Change 的 OpenSpec strict 和归档证据通过。
- REQ 子文档与归档路径已回填；早期执行记录明确历史语义，不改写当时验证结果。
- product_data_collection_observability: applicable；affected_layers: [web_request_wrapper, api, db, usage_events, request_logs, task_traces, task_trace_spans]。validation: 复核 REQ-0024 权限矩阵/脱敏操作记录及 REQ-0025 真实执行/隔离/可信计量/数据库兼容与分批视觉证据。具体 N/A：权限矩阵单次同步 task toggle 不接入长任务 Trace；Chat 无新增附件上传、管理页或移动客户端。实际模型执行与合成接口视觉验收分别记录。
- ai_usage_mode: estimated_fallback。自动 session 发现两次均返回 unavailable/no-command-runs；现有快照过期且范围覆盖不足，无法给出本 Sprint 真实总 Token 或成本。recommended_action: 如需用量审计，提供可归因的显式 session 和历史映射后重新提取；不将已有估算当作真实用量。
- 归档目录日期保留 OpenSpec CLI 实际生成的 2026-09-13；本地关闭时间使用 Asia/Shanghai。包装脚本跨日预期差异已通过实际路径、身份、目录和证据复验恢复。
