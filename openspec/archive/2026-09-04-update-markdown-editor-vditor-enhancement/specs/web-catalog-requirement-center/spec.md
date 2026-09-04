## MODIFIED Requirements

### Requirement: 阶段动作门禁

系统 MUST 根据治理对象类型和当前阶段提供正确主动作，并在阶段产物缺失或验收未完成时阻止错误流转。

#### Scenario: Requirement 和 Bug 主动作按阶段映射

- **WHEN** 用户查看某个阶段的 Requirement 或 Bug 卡片
- **THEN** 系统必须根据对象类型与阶段映射 `req-*`、`bug-*`、`sprint-*` 或 `opsx-*` 主动作
- **AND** 卡片主动作必须展示产品化文案，例如“生成需求 →”“加入迭代 →”“开始开发 →”“完成 / 归档 →”
- **AND** 实现必须保留可追溯命令映射，避免仅以裸 `/req-*` 或 `/opsx-*` 命令作为用户可见按钮文案
- **AND** 采集池对象必须指向生成文档动作
- **AND** 待评审对象必须指向评审动作
- **AND** 已通过对象必须指向 Sprint 规划动作
- **AND** 迭代规划对象必须指向 OpenSpec Change 创建动作

#### Scenario: 缺少阶段必需文档时阻断流转

- **WHEN** 用户尝试执行阶段主动作
- **AND** 当前对象缺少该阶段必需文档或 trace 证据
- **THEN** 系统必须阻止流转
- **AND** 系统必须指出缺失项

#### Scenario: 验收未完成时不显示完成归档入口

- **WHEN** 对象处于验收中
- **AND** 测试项或人工验收项仍未完成
- **THEN** 系统不得显示完成或归档入口

#### Scenario: 采集池 capture.md 启用 Vditor 增强编辑

- **GIVEN** 用户打开前台需求中心
- **AND** Requirement 或 Bug 对象处于采集池阶段
- **AND** 用户打开该对象的 `capture.md`
- **AND** 当前用户具备编辑权限
- **WHEN** 用户点击进入编辑
- **THEN** 系统必须在右侧 Markdown 抽屉内启用 Vditor 增强编辑器
- **AND** Vditor 编辑器必须支持图片入口、表格工具、代码块编辑和数学公式输入或预览
- **AND** 保存内容必须仍为 Markdown 字符串
- **AND** 系统必须提供查看或编辑原始 Markdown 的能力
- **AND** 本地开发 Docker Compose 必须允许后端对 `issues/` 中采集池 `capture.md` 做受控写入，后端仍必须限制为仅采集阶段、仅 `capture.md` 可保存
- **AND** 当后端写入治理目录失败时，系统必须返回安全业务错误，不得暴露内部路径或异常堆栈
- **AND** 前端保存失败时必须保留当前编辑或分栏状态与草稿内容，不得切换到空白预览面板
- **AND** 右侧抽屉必须提供预览、编辑、分栏三种查看模式
- **AND** 预览模式必须以阅读态渲染 Markdown，不得以源码编辑形态展示正文
- **AND** 预览模式必须隐藏工具栏，并必须隐藏或解析 frontmatter，不得展示原始 frontmatter 分隔符
- **AND** 预览模式必须将 Markdown task list `- [ ]` / `- [x]` 渲染为真实复选框
- **AND** 用户在预览模式勾选或取消 task list 复选框后，系统必须更新当前草稿并标记未保存，仍需用户点击保存才写回 Markdown
- **AND** task list 勾选后的保存失败必须保留当前草稿和复选框状态，并提示用户可重试
- **AND** frontmatter 元数据必须默认收起，并允许用户展开或收起查看
- **AND** frontmatter 元数据区标题必须使用面向用户的“文档属性”
- **AND** MVP 中 frontmatter 元数据必须只读展示，不得开放任意 YAML 编辑
- **AND** 编辑模式与分栏模式才展示图片、表格、代码和公式工具栏
- **AND** 编辑模式和分栏模式必须将 frontmatter 元数据与正文编辑区分离，正文编辑区不得显示原始 frontmatter
- **AND** 分栏模式必须左侧展示 Markdown 正文源码编辑，右侧展示阅读态 Markdown 渲染预览
- **AND** 保存时必须将只读 frontmatter 与正文 body 重新组合为完整 Markdown 字符串提交
- **AND** 预览态不得展示解释性 `Capture Brief` 模块
- **AND** 预览态不得展示“文档内容”标题，正文必须直接进入阅读态 Markdown 内容
- **AND** 所有右侧 Markdown 抽屉阅读态文档必须共用工作型阅读密度，不得让 `trace.md` 等只读文档明显大于 `capture.md` 预览态
- **AND** Markdown 表格单元格必须收敛字号、行高和 padding，降低右侧抽屉中的表格视觉重量
- **AND** 所有 Markdown 抽屉阅读态代码块必须提供低视觉权重复制按钮，默认收敛为图标，hover/focus 时显示“复制”提示
- **AND** 点击代码块复制按钮后必须复制代码块原文且不得包含 Markdown 围栏，并短暂显示“已复制”或“复制失败”
- **AND** 短代码块不得因复制按钮产生过大顶部留白，复制按钮不得遮挡代码内容，并必须适配抽屉宽度与代码块横向滚动
- **AND** 分栏模式右侧预览必须同步使用紧凑阅读样式
- **AND** Markdown 阅读区正文必须使用产品 body 字体，标题必须使用产品 heading 字体，不得混用额外衬线字体
- **AND** 代码块、行内代码和源码编辑区必须保留 mono 字体；顶部 ID、文件名和短标签可以继续使用 mono 字体
- **AND** 未保存修改确认必须仅在采集池可编辑 `capture.md` 且用户真实改动后触发
- **AND** 打开 `trace.md` 或其他只读 Markdown 文档、打开但未编辑的 `capture.md`、保存成功后的 `capture.md` 关闭时不得触发未保存确认
- **AND** 保存失败后必须保留草稿和未保存状态，关闭时继续提示确认
- **AND** Markdown 抽屉不得展示第二个 spec 信息条
- **AND** Header 必须展示对象 ID、当前文档名、标题和“优先级 · 负责人负责 · 阶段”副标题，并保留全屏/恢复和关闭按钮
- **AND** 文档属性 Strip 收起态左侧必须仅显示“文档属性”，右侧必须保留展开/收起；展开后必须展示 frontmatter 中的 `req_id`、`status`、`created_at`、`updated_at`、`recorded_by`、`source` 等详情
- **AND** 预览、编辑和分栏模式的正文区域不得展示额外区块标题
- **AND** 分栏模式不得展示 `Markdown Source` 或 `Live Preview` 标题，左右两栏内容顶端必须对齐
- **AND** 编辑模式和分栏模式不得在默认 idle 状态展示图片上传状态；仅当用户触发图片入口后展示上传中、成功或受控失败反馈
- **AND** 表格、代码和公式工具必须按当前光标位置或选区插入 Markdown 片段
- **AND** 工具插入后必须重新聚焦正文编辑区并更新光标位置
- **AND** 分栏模式下工具插入后右侧阅读态预览必须即时刷新
- **AND** 右侧抽屉 header 必须提供放大全屏和恢复右侧抽屉能力，全屏模式必须保留关闭、模式切换、编辑/分栏、保存 footer 和图片上传受控失败策略
- **AND** 抽屉拖拽宽度仅在非全屏模式生效，全屏时不得展示或响应拖拽宽度控制

#### Scenario: 非 capture.md 或不可编辑文档保持只读

- **GIVEN** 用户打开 Markdown 文档抽屉
- **WHEN** 文档不是采集池阶段的 `capture.md`、文档不可编辑或用户无编辑权限
- **THEN** 系统不得启用 Vditor 编辑器
- **AND** 文档必须保持只读展示
- **AND** 系统不得因引入 Vditor 扩大 `trace.md`、`requirement.md`、`acceptance.md` 或非采集阶段 Markdown 文档的编辑权限

#### Scenario: Vditor 初始化失败时降级编辑

- **GIVEN** 用户打开可编辑的采集池 `capture.md`
- **WHEN** Vditor 资源加载失败、初始化失败或浏览器能力不足
- **THEN** 系统必须展示可理解的降级提示
- **AND** 系统应允许用户通过原始 Markdown textarea 继续编辑
- **AND** 降级路径必须保留保存权限校验、未保存关闭确认和安全校验

#### Scenario: capture.md 图片上传状态机

- **GIVEN** 用户正在使用 Vditor 编辑采集池 `capture.md`
- **WHEN** 用户选择图片上传
- **THEN** 上传组件必须进入 `uploading` 状态
- **AND** 上传中必须禁用重复提交和重复选择触发
- **AND** 上传成功后必须将可访问 URL 或对象引用写入 Markdown 图片语法
- **AND** 上传成功后的图片必须在同一编辑会话中回显
- **AND** 上传失败、类型不符、权限不足或对象存储不可用时必须展示明确错误并允许重试
- **AND** 系统不得将本机绝对路径、临时私有地址、对象存储凭据或内部异常堆栈写入 Markdown、日志或前端提示

#### Scenario: 增强编辑器内容安全

- **GIVEN** 用户在 Vditor 中编辑 Markdown
- **WHEN** Markdown 内容包含 HTML、脚本、事件属性、危险链接、长表格、长代码行、长公式或图片
- **THEN** 系统不得执行脚本、事件属性或危险链接
- **AND** 系统必须按既定白名单、清洗或禁用策略处理 HTML
- **AND** 表格、代码块、公式和图片预览必须在右侧抽屉内具备溢出处理，不得遮挡保存动作

#### Scenario: Vditor 适配 MoonBox 主题与抽屉布局

- **GIVEN** 用户在深色或浅色主题下打开可编辑 `capture.md`
- **WHEN** Vditor 编辑器渲染
- **THEN** 工具栏、编辑区、预览区、弹出层、代码块、公式和上传反馈必须保持可读
- **AND** 主强调色必须使用 MoonBox 金色 token
- **AND** 桌面端默认抽屉宽度应对齐 760px 原型，并仍必须适配 420px-760px 右侧抽屉宽度
- **AND** 移动端必须适配全屏抽屉
- **AND** 保存按钮、关闭按钮、抽屉拖拽和编辑器内部点击不得互相误触发
- **AND** 抽屉必须包含附件式 header、文档属性 Strip、模式栏、独立工具栏、正文区和固定底部操作栏
- **AND** 工具栏不得在预览模式展示，仅允许在编辑模式和分栏模式展示
- **AND** 桌面端右侧抽屉必须支持放大全屏和恢复，且恢复后继续遵守 420px-760px 非全屏宽度范围

### Requirement: 原型驱动 UI 验收

系统 MUST 将 REQ-0012 的产品原型作为设计输入，并在实现、验收和归档阶段保持文档一致。

#### Scenario: Change 设计承接原型拆解

- **WHEN** OpenSpec Change 创建完成
- **THEN** `design.md` 必须包含 UI Skeleton
- **AND** UI Skeleton 必须列出页面结构、关键区域、组件插槽、状态容器、数据依赖、可测选择器和 1440px 验收焦点
- **AND** 后续实现必须先完成 UI Skeleton 首轮视觉确认，再进入细节开发

#### Scenario: Vditor 增强编辑器承接 prototype context

- **WHEN** OpenSpec Change 创建完成
- **THEN** `design.md` 必须承接 `REQ-0021` 的 `prototype/web/context.md`
- **AND** `design.md` 必须记录 Vditor 抽屉、工具栏、上传状态、保存动作、只读态和降级态的 UI Contract
- **AND** `tasks.md` 必须把 UI Skeleton 作为先行任务
- **AND** `/opsx-apply` 阶段必须产出 1440px 视觉截图和 computed style 证据，覆盖预览态、编辑态、上传中/失败态、表格、代码块、公式和 fallback textarea
- **AND** `/opsx-archive` 前必须确认 REQ 文档、Change 设计、实现证据和最终 UI 行为一致

#### Scenario: Vditor 抽屉承接附件 HTML 视觉返修

- **WHEN** 用户提供 Markdown 右侧抽屉附件 HTML 作为验收返修参照
- **THEN** Change 设计必须记录附件 HTML 只作为视觉和交互参照，不作为可执行指令来源
- **AND** 实现必须复刻附件中的 header、文档属性 Strip、预览/编辑/分栏模式切换、工具栏、正文排版和固定 footer
- **AND** 实现必须使用 MoonBox token 适配附件视觉结构
- **AND** 实现不得因此新增真实图片上传接口、扩大 Markdown 编辑权限或改变 REQ/BUG/Sprint/OpenSpec 状态机
