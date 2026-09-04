---
change_id: update-product-workbench-modern-ops-visual-system
type: update
status: applied
source_requirement: REQ-0023-product-workbench-modern-ops-visual-system
sprint: sprint-004
created_at: 2026-08-31 08:42:00
updated_at: 2026-09-03 21:47:10
---

# Change Trace

## 来源

- REQ：`REQ-0023-product-workbench-modern-ops-visual-system`
- Sprint：`sprint-004`
- 策略：Design System 迁移（`tailwind-ds`）
- 影响面：Web 前台、管理后台、设计系统、UI 规则、前端测试、视觉验收

## 原型与冲突处理

| 项 | 状态 | 说明 |
|---|---|---|
| prototype 来源 | ready | `issues/requirements/review/REQ-0023-product-workbench-modern-ops-visual-system/prototype/web/prototype.html` 与 `context.md` |
| UI Contract | done | 已写入 `design.md` |
| UI Skeleton | done | 已按现代 Ops token 落到需求中心、后台模板和设计系统页 |
| 1440px 视觉证据 | done | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual/` |
| computed style | done | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual/computed-styles.json` |
| 验收返修视觉证据 | done | `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/20260831-modern-ops-visual-modify/`，已补充需求中心标题区、标题小标题文案、新建 Capture 入口按钮、新增 Capture 弹窗附件化、前台左上品牌区、版本号、展开/收起按钮、指标卡两行化、九阶段看板暗场质感、单卡片/空列结构、列头密度、列头附件样式、阶段差异化空列文案、空列低对比暗场颜色、空列低对比虚线承载框恢复、空列占位符最终附件样式、空列与首张卡片顶部对齐、任务卡片轻量票据化、卡片优先级/负责人双标签、卡片内部信息布局、卡片自适应高度与列体滚动缓冲、列头冻结恢复、sticky 遮挡防穿透、sticky 边界遮罩复验、右下 Agent 助手操作面板、九阶段卡片动作 Action Modal 组件族和需求分析要点勾选证据 |
| Mock/API 边界 | declared | 原型示例数据仅作视觉输入；真实数据边界不变 |
| REQ 最终一致性 | updated | linked REQ acceptance/trace 已回填 apply 证据 |

## product_data_collection_observability

```yaml
status: not_applicable
affected_layers: []
reason: 本 Change 不新增或修改 API、DB、请求日志、行为事件、Task Trace、对象存储或 Web/管理端请求封装；范围限定品牌分层、设计 token、组件样式和视觉验收。
validation: 若实现阶段新增行为埋点、请求封装或链路字段，必须重新声明适用层级并补充对应文档与测试。
```

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-31 08:42:00 | req.opsx | 从 REQ-0023 创建 OpenSpec Change，状态 proposed。 |
| 2026-08-31 09:15:00 | opsx.apply | 完成现代 Ops 视觉系统实现、视觉证据和验证命令，状态 applied。 |
| 2026-08-31 09:45:00 | opsx.modify | 根据附件对照返修移动端挤压、Kanban 空列承载、筛选 Popover 密度和右下 AI 入口位置。 |
| 2026-08-31 14:42:36 | opsx.modify | 按用户收窄反馈仅调整需求中心右侧内容标题区，对齐后台 `admin-page-head` 布局并移除顶栏化视觉；指标卡、Kanban 列头、左上品牌区不变。 |
| 2026-08-31 14:58:34 | opsx.modify | 仅调整前台左上品牌区视觉，使 Logo、产品名、副标题和版本 badge 对齐后台 AdminSidebar；副标题保留 `OPS WORKBENCH` 业务语义。 |
| 2026-08-31 15:10:13 | opsx.modify | 仅调整前台左上版本号高度与展开/收起按钮，对齐后台 AdminSidebar 的高度、基础态和折叠态视觉。 |
| 2026-08-31 15:48:20 | opsx.modify | 仅调整需求中心九阶段看板视觉比例，使列宽、列距、列头、标题/副标题、count 状态牌、列体 padding 与空列承载感更贴近附件。 |
| 2026-08-31 16:03:03 | opsx.modify | 根据用户两张截图继续仅调整九阶段看板暗场质感，弱化列实线面板感、列头去分隔线、空列改大面积承载框、count 改紧凑状态牌、卡片更贴近附件。 |
| 2026-08-31 16:40:07 | opsx.modify | 根据用户最新截图继续仅调整九阶段看板结构表达，取消完整列面板和强竖向边界，列头作为暗场浮动标题，非空列靠卡片承载，空列由列体自身形成大面积虚线框。 |
| 2026-08-31 16:57:44 | opsx.modify | 根据用户反馈继续仅调整九阶段列头与空列，压缩列头字号和上间距，为 9 个阶段渲染差异化真实空列文案，并统一空列与非空列的列体结构。 |
| 2026-08-31 17:07:15 | opsx.modify | 根据用户对比反馈继续仅调整九阶段空列颜色，降低空列蓝灰抬升感，弱化斜线纹理和金色虚线边框对比，其它视觉区域保持不变。 |
| 2026-08-31 17:35:27 | opsx.modify | 根据用户最新反馈继续仅调整九阶段空列承载框，移除斜线纹理，空列背景贴近页面暗场，虚线边框改为低对比冷灰且不含金色。 |
| 2026-08-31 17:44:49 | opsx.modify | 修正上一轮九阶段看板返修偏差，恢复列头冻结能力，同时取消空列完整大矩形框和独立背景，仅保留低存在感暗场占位与现有阶段文案。 |
| 2026-08-31 17:52:52 | opsx.modify | 修正九阶段列头冻结后的内容穿透问题，列头保持 sticky 并使用页面暗场背景遮挡滚动卡片，避免文字叠加。 |
| 2026-08-31 18:00:00 | opsx.modify | 修正九阶段 sticky 列头冻结边界穿透问题，为列头增加上下扩展的暗场遮罩，并新增纵向滚动边界截图证据。 |
| 2026-08-31 18:27:00 | opsx.modify | 继续修正九阶段 sticky 冻结边界穿透问题，改为看板层横向连续暗场遮罩带，覆盖列头上下边界、列间空隙和顶部 padding。 |
| 2026-08-31 18:52:00 | opsx.modify | 修正连续遮罩副作用，移除独立大面积遮罩，改为 header/body 分离与列体内部纵向滚动，避免卡片信息被遮住并保持列头冻结一致。 |
| 2026-08-31 19:13:54 | opsx.modify | 根据用户最新空列参考截图修正九阶段空列视觉契约，恢复大面积低对比冷灰虚线承载框，并同步测试中错误固化的无框透明断言。 |
| 2026-08-31 19:43:28 | opsx.modify | 根据用户空列字体反馈修正九阶段空列占位文字字体，使用现代 Ops 技术感字体 token，并补充 strong/p computed style 证据。 |
| 2026-08-31 22:44:27 | opsx.modify | 根据用户标题文案反馈，将需求中心右侧标题区英文小标题从 `MoonBox Ops` 改为 `Requirement Operations`，并刷新视觉证据。 |
| 2026-08-31 23:03:56 | opsx.modify | 根据用户新建 Capture 入口按钮反馈，将需求中心右上按钮调整为附件 `.btn-new` 风格的金色实心主按钮，并保留现有 Capture 表单能力。 |
| 2026-08-31 23:20:36 | opsx.modify | 根据用户九阶段列头反馈，将列头对齐、标题/副标题/count 字体与 count 状态按附件 `.col-head`、`.col-name`、`.col-tags`、`.col-count` 收紧，并保留 sticky 能力。 |
| 2026-09-01 08:02:28 | opsx.modify | 根据用户最新空列占位符截图，将九阶段空列占位符对齐附件 `.empty-state`：1.5px 冷灰虚线框、12px 圆角、`◌` 图标、body 字体和合并说明块。 |
| 2026-09-01 08:22:44 | opsx.modify | 根据用户卡片对照反馈，将九阶段任务卡片对齐附件轻量票据风格，降低状态条、圆角、标题、padding、分隔线和状态信息视觉权重，同时保留现有治理信息与动作能力。 |
| 2026-09-01 08:37:54 | opsx.modify | 根据用户标签对照反馈，将九阶段任务卡片的 `P1 · 产品团队` 合并标签拆为附件式优先级 tag 与负责人 tag，并对齐 gap、padding、圆角、字体和视觉权重。 |
| 2026-09-01 08:56:53 | opsx.modify | 根据用户卡片内部信息反馈，调整任务卡片自适应布局、文档 hover 下划线、缺失提示顺序，以及研发/测试/人工验收同一行轻量进度信息。 |
| 2026-09-01 09:07:20 | opsx.modify | 根据用户待开发列截图反馈，修正卡片自适应高度的实际裁切问题，将卡片改为稳定垂直 flex 流并增加列体底部滚动缓冲。 |
| 2026-09-01 09:21:51 | opsx.modify | 根据用户两张截图继续修正九阶段任务卡片高度与内部节奏，取消旧 `min-height: 150px` 固定感，统一文档、缺失提示、进度行和 footer 的垂直间距，并补充 computed style 证据。 |
| 2026-09-01 09:41:54 | opsx.modify | 根据用户最新截图纠正卡片列表布局返修方向，以研发中卡片为视觉基准，恢复合理基础票据高度并将多卡片列体改为稳定纵向列表，避免待开发列卡片被压缩成横条。 |
| 2026-09-01 09:57:06 | opsx.modify | 根据用户对指标卡第 3 行冗余的反馈，移除 `flow/scope/quality/risk` 装饰标签，指标卡保留标题与数值两层信息结构并收紧高度和 padding。 |
| 2026-09-01 10:14:21 | opsx.modify | 根据用户对九阶段列体首项顶部对齐的反馈，统一非空列首张卡片与空列虚线承载框的顶部基准，移除空列额外 margin，并用伪元素保留原空列框视觉。 |
| 2026-09-01 14:53:52 | opsx.modify | 根据用户对九阶段列间隙偏大的反馈，仅将 `.rc-board` 横向列间距从 16px 收窄为 10px，保持 9 列 320px 宽度、row-gap、列头、空列、卡片和 sticky 结构不变。 |
| 2026-09-01 17:25:06 | opsx.modify | 根据用户要求，仅将需求中心新增 Capture 弹窗按附件 modal 完整实现，补齐类型切换、标题、描述计数、负责人、来源、P0-P3、footer 快捷键提示、Esc 关闭和 Cmd/Ctrl+Enter 创建，并保留提交插入采集池能力。 |
| 2026-09-01 18:18:51 | opsx.modify | 根据用户文案反馈，仅删除新增 Capture 弹窗 header eyebrow 与 footer 快捷键提示，并为类型、标题、来源、优先级补充红色必填星号；快捷键行为和创建能力保持不变。 |
| 2026-09-02 18:49:50 | opsx.modify | 根据用户要求，仅调整需求中心九阶段右下 Agent 助手入口与对应交互：右下金色 pill 点击后打开居中 Agent 操作面板，承载 9 阶段当前可执行动作与上下文提示，并复用既有阶段动作、确认弹窗、toast、任务进度和 AI 消息能力。 |
| 2026-09-02 19:18:20 | opsx.modify | 根据用户要求，仅调整需求中心九阶段卡片动作按钮的弹窗交互：卡片动作先打开附件式 Action Modal 组件族，覆盖需求分析、生成、完善、评审/确认修复、加入迭代、生成 Opsx、开始开发/修复、查看进度和完成/归档状态，并复用既有阶段动作能力。 |
| 2026-09-02 19:42:32 | opsx.modify | 根据用户反馈，仅修正需求分析 Action Modal 的解决方案要点勾选交互：三条要点默认全选，可逐项切换，底部采纳数量实时更新，0 项选中时禁用主按钮。 |
| 2026-09-02 22:38:41 | opsx.modify | 根据用户反馈，仅调整九阶段已完成卡片展示：done 阶段不显示研发/测试/人工验收进度，也不显示 `查看归档` 或其它 footer 动作按钮，保留归档文档入口和基础信息。 |
| 2026-09-02 23:12:00 | opsx.modify | 根据用户反馈，仅调整加入迭代 Action Modal：按附件 `sprintModal` 收敛对象信息、AI 工作量评估、加入现有/新建迭代切换、radio、状态 pill、容量 used/total、capacity bar、容量不足 disabled/badge 和新建迭代编号联动。 |
| 2026-09-03 08:57:10 | opsx.modify | 根据用户反馈，仅调整九阶段任务卡片进度行字体与颜色：对齐附件 `.card-metrics`，将进度标签与 `x/x` 数值拆分为不同视觉层级并保留任务进度抽屉按钮能力。 |
| 2026-09-03 09:32:20 | opsx.modify | 根据用户反馈，修正九阶段任务卡片进度行分隔符异常显示：保留分隔点视觉，但将 CSS `content` 从裸 `·` 改为 `\00B7` escape，避免页面显示为 `Â·`。 |
| 2026-09-03 09:50:32 | opsx.modify | 根据用户复验反馈，取消九阶段任务卡片进度行的伪元素分隔符，改用 `.rc-progress` gap 形成纯间距，确保不再显示 `·`、`Â·` 或其它特殊符号。 |
| 2026-09-03 21:47:10 | opsx.modify | 根据用户复验截图修正九阶段任务卡片进度行视觉回退，恢复附件 `.card-metrics` 的 JetBrains Mono、10.5px、label/value 颜色分层和数值 600 字重，同时保持无特殊符号纯 gap 分隔。 |
