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
- **AND** 桌面端必须适配 420px-760px 右侧抽屉宽度
- **AND** 移动端必须适配全屏抽屉
- **AND** 保存按钮、关闭按钮、抽屉拖拽和编辑器内部点击不得互相误触发

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

