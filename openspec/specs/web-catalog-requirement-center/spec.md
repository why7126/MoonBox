# web-catalog-requirement-center Specification

## Purpose
TBD - created by archiving change fix-frontend-user-menu-change-password. Update Purpose after archive.
## Requirements
### Requirement: 前台用户菜单修改密码

系统 MUST 支持已登录前台用户从需求中心用户菜单发起自助修改密码，并在成功后清理完整本地会话。

#### Scenario: 前台菜单点击打开修改密码弹窗

- **GIVEN** 用户已登录前台并进入 `/requirements`
- **WHEN** 用户打开左侧底部用户菜单并点击“修改密码”
- **THEN** 系统必须关闭用户菜单
- **AND** 系统必须打开标题为“修改密码”的弹窗
- **AND** 弹窗必须包含“当前密码”“新密码”“确认新密码”三个输入项
- **AND** 弹窗文字、输入框、边框、光标和主按钮在前台深色与浅色主题中必须保持可读可填写

#### Scenario: 前台修改密码提交调用既有接口

- **GIVEN** 用户已打开前台修改密码弹窗
- **AND** 用户填写当前密码、新密码和确认新密码
- **AND** 两次新密码一致
- **WHEN** 用户点击“更新密码”
- **THEN** 系统必须调用 `/api/v1/admin/auth/change-password`
- **AND** 请求体必须包含 `current_password`、`new_password`、`confirm_password`
- **AND** 请求必须携带当前可用登录会话 token 的 Bearer 授权头
- **AND** 当用户只有 `moonbox.frontend.session.access_token` 且没有 `moonbox.admin.session` 时，系统必须使用 frontend session token 提交改密请求
- **AND** 后端必须允许任意正常登录用户通过该接口修改自己的密码，不得要求后台管理员角色
- **AND** 后台用户管理等管理接口必须继续要求后台管理员权限

#### Scenario: 前台修改密码成功后重新登录

- **WHEN** 前台修改密码接口返回成功
- **THEN** 系统必须清理 `moonbox.admin.session`
- **AND** 系统必须清理 `moonbox.frontend.session`
- **AND** 浏览器地址必须跳转到 `/login`
- **AND** 用户必须重新登录后才能回到前台需求中心

#### Scenario: 前台修改密码失败保留状态

- **WHEN** 前台修改密码接口返回错误
- **THEN** 修改密码弹窗必须保持打开
- **AND** 已填写内容不得被静默清空
- **AND** 页面必须展示接口返回的错误信息或默认失败提示
- **AND** 系统不得清理当前会话
- **AND** 用户继续修改任一密码输入项后，旧的提交级错误必须清除，避免与当前字段级错误同时展示

#### Scenario: 确认密码不一致不发起请求

- **GIVEN** 用户填写的新密码和确认新密码不一致
- **WHEN** 用户点击“更新密码”
- **THEN** 系统必须展示“两次输入的新密码不一致”
- **AND** 系统不得调用 `/api/v1/admin/auth/change-password`

#### Scenario: 后台修改密码流程保持不回归

- **WHEN** 用户进入后台用户管理页
- **AND** 通过后台用户菜单点击“修改密码”
- **THEN** 后台必须仍能打开修改密码弹窗
- **AND** 修改成功后必须清理后台会话并回到登录页

### Requirement: 前台框架与主题

系统 MUST 使用 MoonBox 前台框架承载需求中心，并保持统一的侧边栏、品牌、主题、会话展示和页面结构。

#### Scenario: 需求中心使用现代 Ops 工作台 Shell

- **WHEN** 用户打开需求中心
- **THEN** 页面必须展示现代 Ops 工作台 Shell
- **AND** 需求中心导航项必须高亮
- **AND** 侧边栏必须展示登录后产品工作台的信息架构分组
- **AND** 品牌区必须展示 MoonBox、工作台版本或等价产品状态标记
- **AND** 前台品牌区的 Logo、产品名、副标题、版本标记和展开/收起按钮视觉规格必须与后台侧边栏品牌区保持一致，同时副标题可保留前台工作台业务语义
- **AND** 当前导航项必须使用现代 Ops active 态表达，不得只依赖旧品牌叙事样式
- **AND** 侧边栏、导航密度、字体字号、图标尺寸、折叠按钮、收起态行为和用户菜单视觉层级必须与管理后台 Shell 保持一致
- **AND** 前后台用户菜单必须使用区别于侧边栏的浮层背景、边框、阴影和 hover 态
- **AND** 退出登录必须在前后台用户菜单中单独成组并使用一致危险色
- **AND** 侧边栏必须支持展开与收起形态，收起后必须保留图标、悬停提示和当前菜单高亮
- **AND** 窄屏下必须避免品牌区、版本标记和页面标题互相挤压；可隐藏版本标记以优先保证主标题和主操作可读
- **AND** 需求中心右侧内容标题区必须采用与后台用户/空间管理一致的内容页标题布局，英文小标题必须显示为 `Requirement Operations`，不得使用额外底部分隔线、sticky 顶栏感、半透明背景或 blur

#### Scenario: 主题切换使用现代 Ops Token

- **WHEN** 用户在用户菜单内切换明暗主题
- **THEN** 页面必须即时应用现代 Ops 深色或浅色 Token
- **AND** 深浅主题下文字、面板、边框、状态色、focus、disabled 和 loading 状态必须清晰可读
- **AND** 主题切换不得改变业务状态

### Requirement: 前台需求中心生命周期看板

系统 MUST 在 MoonBox 前台提供需求中心看板，保留 9 个阶段展示 Requirement 与 Bug 生命周期，并展示独立 Change 的对应交付阶段。

#### Scenario: 用户打开需求中心看到 9 阶段看板

- **WHEN** 用户进入 MoonBox 前台需求中心
- **THEN** 页面必须展示采集池、规划中、待评审、已通过、迭代规划、待开发、研发中、验收中、已完成 9 个阶段
- **AND** Requirement 与 Bug 必须共享阶段框架
- **AND** 每个阶段列头必须展示阶段标题、原型定义的命令副标题和两位数对象数量
- **AND** 页面必须通过横向看板结构表达 9 个阶段，筛选为 Bug 时仍保留全部 9 个阶段列，且不得展示冗余横向滚动提示文案
- **AND** Requirement 卡片必须复用当前实现的类型边框与主题样式
- **AND** Bug 卡片必须以红色左边框表达对象类型
- **AND** 独立Change卡片必须使用主题info蓝色左边框，与需求和缺陷区分

#### Scenario: 卡片展示治理对象摘要

- **WHEN** 看板渲染 Requirement 或 Bug 卡片
- **THEN** 卡片必须展示 ID、标题、优先级、负责人或来源、阶段产物、更新时间、阻塞状态、研发或测试进度以及阶段主动作
- **AND** 卡片必须保持当前实现的标签、文档分组、进度、底部动作和更新时间结构，仅按当前 Change 身份展示契约新增 ID 行与替换标题
- **AND** 已进入迭代规划及后续阶段的卡片必须展示唯一 `sprint-xxx` 标签
- **AND** 未纳入迭代的卡片不得展示空 Sprint 标签

### Requirement: 前台需求中心筛选与搜索

系统 MUST 支持用户按对象类型、关键字、负责人、优先级和 Sprint 聚焦需求中心看板范围。

#### Scenario: 用户按对象类型筛选

- **WHEN** 用户点击全部、需求或 Bug 筛选控件
- **THEN** 看板必须只展示匹配对象类型的卡片
- **AND** 统计区必须与当前筛选范围一致

#### Scenario: 用户搜索治理对象

- **WHEN** 用户输入 ID、标题、文档名或负责人关键字
- **THEN** 看板必须展示匹配的 Requirement 或 Bug
- **AND** 不匹配的卡片不得出现在当前结果范围内

#### Scenario: 用户按负责人、优先级或 Sprint 筛选

- **WHEN** 用户选择负责人、优先级或 Sprint 筛选项
- **THEN** 看板卡片范围必须按筛选条件刷新
- **AND** 筛选不得破坏 9 阶段列头与横向滚动行为

#### Scenario: 用户手动刷新 9 阶段看板

- **WHEN** 用户点击需求中心工具栏中的刷新图标按钮
- **THEN** 系统必须重新读取需求中心上下文并更新统计区和 9 阶段看板
- **AND** 系统必须保留当前搜索、对象类型、负责人、优先级和 Sprint 筛选条件
- **AND** 刷新过程中刷新按钮必须展示 loading 语义并避免重复点击
- **AND** 刷新失败时不得清空当前看板，必须保留最近一次成功加载的数据并给出轻量失败提示

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

### Requirement: 组织空间切换

系统 MUST 在用户菜单中提供轻量组织空间切换交互，使用户可在当前页面基于真实后台空间上下文快速切换已加入空间。

#### Scenario: Hover 切换空间打开空间列表

- **WHEN** 用户 Hover 用户菜单中的“切换空间”
- **THEN** 系统必须在一级用户菜单右侧展示空间列表
- **AND** 用户无需点击即可展开空间列表
- **AND** 从一级菜单移动到空间列表期间一级用户菜单必须持续显示
- **AND** 空间列表必须具备短延时防误关闭能力

#### Scenario: 用户浏览真实空间列表

- **WHEN** 用户在空间列表中浏览空间
- **THEN** 空间列表必须平铺展示当前用户已加入空间的空间名称、中文角色、成员数、空间单选、当前项勾选和创建或加入入口
- **AND** 空间列表不得展示标题、搜索框、组织分组或用户菜单摘要
- **AND** 空间二级浮层必须使用区别于侧边栏的暗色浮层背景、清晰边框和可读按钮样式
- **AND** 任一时刻最多一个空间处于选中状态
- **AND** 回收中空间、未加入空间和无权限空间不得显示

#### Scenario: 冻结空间展示只读标记

- **WHEN** 用户已加入的空间处于冻结状态
- **THEN** 空间列表必须展示该空间
- **AND** 空间项必须显示“已冻结”或“只读”等低干扰状态标记
- **AND** 状态标记不得挤压空间名称、成员数或当前项勾选图标
- **AND** 深色与浅色主题下状态标记均必须可读

#### Scenario: 切换空间后刷新上下文

- **WHEN** 用户选择新的空间
- **THEN** 系统必须更新用户区空间名称
- **AND** 系统必须保存最近选择到本地空间偏好
- **AND** 保存前必须校验所选空间存在于当前接口返回的可访问空间列表
- **AND** 看板必须按新空间上下文刷新或保持明确的项目级聚合边界

#### Scenario: 空间列表加载失败

- **WHEN** 前台空间上下文接口失败
- **THEN** 空间浮层必须展示脱敏错误态和可恢复操作
- **AND** 页面不得清空最近一次成功加载的看板数据
- **AND** 错误态不得展示内部堆栈、本机路径、数据库错误详情、密钥、token 或后台审计原文

### Requirement: 当前空间设置弹窗

系统 MUST 在用户菜单中提供当前空间设置入口，并使用分栏弹窗维护空间配置。

#### Scenario: 用户打开空间设置

- **WHEN** 具备管理角色的用户点击用户菜单中的“设置空间”
- **THEN** 系统必须打开作用于当前空间的居中分栏弹窗
- **AND** 弹窗左侧必须包含常规、成员与权限、Agent、Skill、集成、高级设置
- **AND** 弹窗右侧必须显示当前分组配置项

#### Scenario: 用户保存常规设置

- **WHEN** 用户编辑空间名称、空间标识、空间描述或默认时区并点击保存
- **THEN** 系统必须校验权限、字段和幂等提交
- **AND** 保存成功后必须关闭弹窗并展示 fixed toast
- **AND** 取消或关闭不得保存未确认变更

#### Scenario: 空间设置弹窗符合横切验收

- **WHEN** 空间设置弹窗在浏览器中渲染
- **THEN** 实现不得让通用 `modal-card` 与专属宽度类并存
- **AND** 必须在 computed style 中验收最终宽度与原型一致
- **AND** 低视口下弹窗 body 必须可滚动
- **AND** 底部保存和取消操作必须可访问
- **AND** 遮罩不得吞掉内部滚动或导致页面主体误滚动

### Requirement: 原型驱动 UI 验收

系统 MUST 将 REQ-0023 的产品原型和附件视觉方向作为设计输入，并在实现、验收和归档阶段保持文档一致。

#### Scenario: Change 设计承接现代 Ops 原型拆解

- **WHEN** OpenSpec Change 创建完成
- **THEN** `design.md` 必须包含 UI Contract
- **AND** UI Contract 必须声明事实源优先级、品牌分层、Token、组件、交互状态、权限规则、Mock/API 边界和 computed style 验收点
- **AND** `design.md` 必须包含 UI Skeleton
- **AND** UI Skeleton 必须覆盖页面结构、区域边界、组件层级、状态容器、数据依赖、可测选择器和 1440px 验收焦点
- **AND** `tasks.md` 中 UI Skeleton 任务必须早于细节实现任务

#### Scenario: 视觉验收覆盖现代 Ops 关键状态

- **WHEN** `/opsx-apply` 完成 UI 实现
- **THEN** 必须产出 1440px 桌面视觉证据
- **AND** 视觉证据必须覆盖默认首屏、侧边栏展开/收起、用户菜单、筛选 Popover、看板横向滚动、空列、错误态、卡片 hover、右侧抽屉、AI 入口、深浅主题和窄屏状态
- **AND** computed style 证据必须覆盖关键字体、字号、行高、间距、圆角、边框、背景、颜色、z-index、overflow 和 position
- **AND** `/opsx-archive` 前必须确认 REQ 文档、Change 设计、最终实现和验收证据一致

### Requirement: 前台创建空间申请流程

系统 MUST 在前台提供创建空间申请流程，使登录用户可从空间切换上下文提交创建空间申请，并在平台管理员审批通过后获得可使用空间。

#### Scenario: 打开创建空间弹窗

- **WHEN** 登录用户从空间切换浮层点击“创建空间”
- **THEN** 系统 MUST 打开标题为“创建空间”的弹窗
- **AND** 弹窗 MUST NOT 展示加入空间入口、加入空间标签、邀请码、空间搜索或申请加入能力
- **AND** 弹窗 MUST 说明每个空间对应一个产品，成员与数据相互隔离
- **AND** 弹窗 MUST 说明待平台管理员审批后才可使用
- **AND** 弹窗 MUST 在副标题中整合审批通过后系统会创建空间并分配申请人为负责人的说明
- **AND** 弹窗 MUST NOT 在表单上方重复展示审批提示行

#### Scenario: 填写创建空间基础信息

- **WHEN** 用户填写创建空间表单
- **THEN** 系统 MUST 采集空间名称、空间标识和空间说明
- **AND** 系统 MUST 在输入空间名称后自动生成空间标识
- **AND** 用户手动修改空间标识后，系统 MUST NOT 再自动覆盖该字段
- **AND** 空间标识 MUST 为 2-32 位小写字母、数字或连字符，并以小写字母开头
- **AND** 除空间说明外，必填项 MUST 以红色星号标识

#### Scenario: 配置配额与有效期

- **WHEN** 创建空间弹窗展示表单
- **THEN** 系统 MUST NOT 展示负责人卡
- **AND** 成员上限默认值 MUST 为 20，允许范围 MUST 为 1-100000，与后台空间管理一致
- **AND** 存储空间默认值 MUST 为 100GB，允许范围 MUST 为大于 0 的数值，单位 GB MUST 与后台空间管理一致
- **AND** AI Tokens 默认值 MUST 为 1000000，允许范围 MUST 为不小于 0 的整数，输入框 MUST NOT 额外展示 `Tokens` 单位
- **AND** 有效期默认 MUST 为固定日期
- **AND** 到期时间默认值 MUST 为本季度最后一天 23:59:59
- **AND** 到期时间 MUST 使用与后台空间管理一致的日期时间选择器，并在 AI Tokens 下方另起一行展示
- **AND** 到期时间选择器 MUST 在 1440x900 视口内完整可操作；当下方空间不足时 MUST 向上展开或在视口内限位
- **AND** 到期时间选择器 MUST NOT 展示“取消 / 确定”操作
- **AND** 用户点击到期时间选择器的 3 个快捷按钮后，系统 MUST 立即应用对应时间并关闭面板
- **AND** 用户点击到期时间控件外区域后，系统 MUST 关闭面板并保留当前值
- **AND** 到期时间选择器面板自身 MUST NOT 出现滚动条
- **AND** 创建空间弹窗右上角关闭按钮 MUST 清晰可见，并具备稳定尺寸、边框/背景和 hover/focus 状态

#### Scenario: 提交申请并进入待审批结果态

- **WHEN** 用户提交有效创建空间表单
- **THEN** 系统 MUST 禁用提交按钮并显示“正在创建...”
- **AND** 系统 MUST 生成待审批创建空间申请
- **AND** 系统 MUST NOT 立即创建正式空间或展示进入空间入口
- **AND** 系统 MUST 展示申请已提交结果态
- **AND** 结果态 MUST 说明待平台管理员审批后才可使用

### Requirement: 卡片文档查看与详情跳转

系统 MUST 支持从需求中心卡片安全查看关联 Markdown/HTML 文档，并支持卡片标题和归档入口新 Tab 打开对象详情。

#### Scenario: Markdown 文档从右侧抽屉打开

- **WHEN** 卡片关联文档包含 `.md` 文件
- **THEN** 文件名必须展示为可点击入口
- **AND** 点击后必须从右侧打开 Markdown 文档抽屉
- **AND** 抽屉必须展示当前对象 ID、文件名和文档内容
- **AND** 抽屉打开后必须显示背景蒙层
- **AND** 桌面端抽屉必须支持 420px-760px 范围内拖拽调整宽度，移动端必须使用全屏宽度
- **AND** 文件点击不得冒泡触发卡片详情或阶段动作

#### Scenario: 采集池 capture.md 受控编辑保存

- **GIVEN** 用户打开采集池阶段对象的 `capture.md`
- **WHEN** 文档抽屉完成加载
- **THEN** 系统必须默认展示 `capture.md` 预览内容和“编辑”按钮，不得直接进入编辑器
- **WHEN** 用户点击“编辑”后修改内容并保存
- **THEN** 系统必须通过受控 API 保存 `capture.md`
- **AND** 保存成功后必须展示成功反馈，回到预览态，并用服务端返回内容更新抽屉预览
- **AND** 再次打开该文档必须回显最新内容
- **AND** 用户关闭存在未保存修改的抽屉前必须出现确认提示
- **AND** `trace.md`、非采集池阶段 Markdown 或非 `capture.md` 文件必须保持只读且保存请求必须被阻断

#### Scenario: HTML 文档从新 Tab 打开

- **WHEN** 卡片关联文档包含 `.html` 文件
- **THEN** 文件名必须展示为可点击入口
- **AND** 点击后必须在新 Tab 打开受控 HTML 预览或详情页面
- **AND** 系统不得向浏览器暴露本机绝对路径或内部文件系统结构

#### Scenario: 卡片标题和查看归档打开详情

- **WHEN** 用户点击任意卡片标题
- **THEN** 系统必须在新 Tab 打开对应 Requirement 或 Bug 详情页
- **AND** 已完成卡片的“查看归档”动作必须使用相同详情打开规则

#### Scenario: 文档异常不触发流转

- **WHEN** 文档不存在、类型不符、读取失败或权限不足
- **THEN** 系统必须展示可理解的异常反馈
- **AND** 系统不得触发卡片阶段流转
- **AND** 错误反馈不得包含本机绝对路径、内部堆栈、密钥、token 或 `.env` 内容

### Requirement: 全局 AI 聊天与卡片动作反馈

系统 MUST 在需求中心提供全局 AI 聊天悬浮入口，并用右侧聊天抽屉承载用户消息、卡片动作上下文、命令执行反馈和异常分支。

#### Scenario: 用户打开全局 AI 聊天抽屉

- **WHEN** 用户点击需求中心全局 AI 聊天悬浮按钮
- **THEN** 系统必须从右侧打开 AI 聊天抽屉
- **AND** 用户必须可以输入消息
- **AND** Enter 必须发送消息
- **AND** Shift+Enter 必须换行

#### Scenario: 卡片动作带入 AI 上下文

- **WHEN** 用户从卡片触发分析、生成、完善、评审、迭代、开发或归档动作
- **THEN** AI 聊天抽屉必须获得当前对象 ID、标题、类型、阶段和建议命令
- **AND** 系统必须展示执行中、成功或失败反馈
- **AND** 失败反馈不得自动移动卡片阶段

#### Scenario: 右侧抽屉互斥

- **WHEN** Markdown 文档抽屉、tasks 抽屉或 AI 聊天抽屉之一打开
- **THEN** 其他右侧抽屉必须关闭或收起
- **AND** 抽屉必须支持关闭按钮、Escape 和外部点击关闭
- **AND** 内部点击不得误关闭抽屉
- **AND** 外部点击应通过蒙层完成，且不得影响抽屉内编辑、保存或拖拽宽度交互

### Requirement: Capture 新建与导入选择

系统 MUST 支持在需求中心创建 Capture，并在生成或完善阶段提供 AI 生成与文件导入选择。

#### Scenario: 用户创建 Capture

- **WHEN** 用户打开 Capture 新建表单
- **THEN** 表单必须支持对象类型、标题、对应类型分级和补充说明
- **AND** 类型与分级应使用轻量选择控件，避免低频下拉增加采集成本
- **AND** 标题必须必填
- **AND** 标题输入框打开弹窗后必须自动聚焦
- **AND** 标题为空时系统必须阻止提交并展示校验提示
- **AND** 标题校验提示必须在表单内展示，并在输入框上体现明确错误态
- **AND** 表单应减少字段间分割线和纵向留白，保持 Capture 快速采集心智
- **AND** 服务端完成目标项目目录、capture.md、trace.md、注册表与当前态索引持久化后，系统才可展示成功反馈，并用服务端完整ID将新对象插入采集池

#### Scenario: 生成阶段导入文件校验

- **WHEN** 用户在生成 Requirement 或 Bug 时选择文件导入
- **THEN** 生成 Requirement 只能上传单个 `requirement.md`
- **AND** 生成 Bug 只能上传单个 `bug.md`
- **AND** 文件缺失、文件名不符、类型不符、重复文件或解析失败时，系统不得执行命令或流转状态

#### Scenario: 完善阶段导入文件校验

- **WHEN** 用户在完善 Requirement 或 Bug 时选择文件导入
- **THEN** 系统必须允许合法 ZIP 或约定多文件集合
- **AND** 文件缺失、文件名不符、类型不符、重复文件或解析失败时，系统不得执行命令或流转状态
- **AND** 校验异常必须在 AI 聊天或等价反馈区域展示

#### Scenario: 两类采集内容持久化与重新加载

- **WHEN** 有写权限的用户提交合法 Requirement 或 Bug Capture
- **THEN** 系统 MUST 在授权项目对应plan目录生成唯一完整ID、capture.md及trace.md，并同步注册表和当前态索引为captured
- **AND** 描述、标题、对应类型分级、负责人和来源等有效字段 MUST 保留
- **AND** 完整刷新后同一条目及文档 MUST 可重新读取
- **AND** 创建 MUST NOT 自动进入评审、Sprint或OpenSpec

#### Scenario: 并发与重复请求

- **WHEN** 多个客户端同时创建或重试同一创建请求
- **THEN** 服务端 MUST 协调编号与文件版本，避免覆盖已存在条目
- **AND** 同一操作者、项目和幂等键的相同请求 MUST 返回同一操作与ID
- **AND** 相同键但不同内容 MUST 返回冲突

#### Scenario: 写入失败与处理中反馈

- **WHEN** 请求仅被受理、发生网络失败或部分文件写入失败
- **THEN** 界面 MUST NOT 提示创建成功或伪造可用文档
- **AND** 系统 MUST 保留输入并提供重试或查询原操作的反馈
- **AND** 服务端 MUST 通过受控恢复防止半成品作为完整条目展示，遇到较新外部修改时不得覆盖

#### Scenario: 项目授权与异步响应隔离

- **WHEN** 无写权限用户提交、请求伪造项目或用户在提交后切换项目
- **THEN** 服务端 MUST 拒绝越权创建，不修改未授权目录
- **AND** 旧项目的异步结果 MUST NOT 插入新项目看板

#### Scenario: 创建链路可追踪

- **WHEN** 创建操作成功、失败或进入恢复
- **THEN** 系统 MUST 可通过请求ID关联操作和任务节点摘要
- **AND** 日志 MUST NOT 保存表单全文、凭证或本机路径，直接API调用不得伪造用户行为事件

#### Scenario: Capture服务就绪与持续创建

- **WHEN** 用户打开Capture弹窗或刷新写入状态
- **THEN** 系统 MUST 查询当前授权项目的写入就绪状态，未就绪时禁用创建并提供脱敏原因
- **AND** 显式continuous部署 MUST 通过最近controller心跳和绑定版本校验支持日常Capture，不依赖人工每小时续期
- **AND** controller失联或项目存在恢复屏障时 MUST 拒绝新建，重启就绪后可恢复
- **AND** 常驻Capture MUST NOT 放宽其他治理操作的维护窗口、项目授权、版本冲突或恢复保护

#### Scenario: 按类型选择并持久化分级

- **WHEN** 用户切换Capture类型
- **THEN** REQ展示priority P0/P1/P2/P3，BUG展示severity blocker/critical/high/medium/low，并保留各自选值
- **AND** 提交仅包含对应类型字段，缺失、非法值和混用字段必须拒绝
- **AND** capture、trace、注册表和索引保存相同正式分级，不固定BUG为medium，不写入异类字段或hint

#### Scenario: Capture 弹窗尺寸与分级解释

- **WHEN** 用户在桌面打开Capture弹窗
- **THEN** 弹窗宽度为840px，窄屏按视口留边收缩
- **AND** REQ显示P0/P1/P2/P3，BUG显示致命/严重/高/中/低并提交原英文枚举
- **AND** 分级不显示鼠标悬停或键盘聚焦浮层，仅在下方显示当前选中说明；原生键盘与触屏选择仍可更新说明

- **AND** 就绪成功不显示文案或状态容器，检查中和异常仍提示并保持创建校验

### Requirement: tasks 进度抽屉与受限验收

系统 MUST 支持从研发中或验收中卡片查看 `tasks.md` 进度，并在验收中执行受限验收与归档门禁。

#### Scenario: 研发中查看 tasks 只读进度

- **WHEN** 对象处于研发中
- **AND** 用户点击查看进度
- **THEN** 系统必须从右侧打开 `tasks.md` 进度抽屉
- **AND** 抽屉必须展示任务列表、完成状态、总数、已完成数量和阻塞提示
- **AND** 研发中模式必须只读

#### Scenario: 验收中进度入口打开统一进度抽屉

- **WHEN** 对象处于验收中
- **AND** 卡片展示研发、测试或人工验收进度
- **THEN** 研发、测试和人工验收进度均必须作为可点击入口打开右侧 `tasks.md` 统一进度抽屉
- **AND** 卡片上的进度入口必须默认呈现灰蓝色次级内联文本视觉并仅使用空格与 `gap` 做视觉分隔，不得使用 `·`、`Â·`、金色主动作色、加粗、重型按钮、边框、底色或等宽小字
- **AND** 人工验收进度必须与研发、测试一样使用 `已完成/总数` 格式展示
- **AND** 抽屉必须同时展示研发任务、自动化测试和人工验收三类进度
- **AND** 抽屉必须根据点击来源默认高亮对应分区
- **AND** Requirement 与 Bug 卡片必须保持一致交互

#### Scenario: 验收中受限验收

- **WHEN** 对象处于验收中
- **THEN** 系统必须展示未完成测试或人工验收项
- **AND** 仅允许用户在受限范围内更新可验收项
- **AND** 必要任务和验收项未完成时，系统不得启用“完成 / 归档”

#### Scenario: 满足门禁后完成归档

- **WHEN** 对象处于验收中
- **AND** 必要任务和验收项均满足完成条件
- **THEN** 系统必须允许发送 `/opsx-archive <完整 REQ 或 BUG ID>`
- **AND** 归档成功后对象必须进入已完成阶段

### Requirement: Markdown 文档人工编辑权限矩阵

系统 MUST 在需求中心按治理阶段、对象类型、文档名和文档路径类别计算 Markdown 文档的人工编辑能力，避免单一 `editable` 布尔值或前端硬编码决定编辑入口。

#### Scenario: 采集池只允许 capture

- **WHEN** Requirement 或 Bug 对象处于采集池阶段
- **THEN** 仅 `capture.md` 的 `human_editable` MUST 为 true
- **AND** `trace.md` 的 `human_editable` MUST 为 false

#### Scenario: 规划中只允许主文档

- **WHEN** Requirement 对象处于规划中阶段
- **THEN** 仅 `requirement.md` 的 `human_editable` MUST 为 true
- **AND** `bug.md` MUST NOT 因矩阵存在而对 Requirement 开放
- **WHEN** Bug 对象处于规划中阶段
- **THEN** 仅 `bug.md` 的 `human_editable` MUST 为 true
- **AND** `requirement.md` MUST NOT 因矩阵存在而对 Bug 开放

#### Scenario: 待评审允许完善类文档

- **WHEN** Requirement 对象处于待评审阶段
- **THEN** `user-stories.md`、`business-flow.md`、`acceptance.md` 和 `requirement.md` 的 `human_editable` MUST 为 true
- **AND** 其他文档 MUST 保持人工只读
- **WHEN** Bug 对象处于待评审阶段
- **THEN** `root-cause.md`、`workaround.md`、`acceptance.md` 和 `bug.md` 的 `human_editable` MUST 为 true
- **AND** 其他文档 MUST 保持人工只读

#### Scenario: 已评审允许评审材料编辑

- **WHEN** Requirement 或 Bug 对象处于已评审阶段
- **THEN** 待评审阶段可编辑文档和 `review.md` 的 `human_editable` MUST 为 true
- **AND** `trace.md` MUST 保持人工只读

#### Scenario: 受控阶段关闭全文编辑

- **WHEN** 对象处于迭代规划、研发中或已完成阶段
- **THEN** 所有 Markdown 文档的 `human_editable` MUST 为 false
- **AND** 前端 MUST 展示阅读态和受限原因

### Requirement: Markdown 抽屉能力驱动渲染

系统 MUST 根据后端返回的文档能力对象渲染 Markdown 抽屉，不得继续以 `capture.md` 或单一阶段判断硬编码编辑体验。

#### Scenario: 完整编辑态

- **WHEN** 文档能力中 `human_editable` 为 true
- **THEN** 前端 MUST 显示完整 Markdown 编辑、分栏、保存和脏状态保护
- **AND** 保存成功后关闭抽屉 MUST NOT 触发未保存确认

#### Scenario: 只读态

- **WHEN** 文档能力中 `readable` 为 true 且 `human_editable` 和 `task_toggle_only` 均为 false
- **THEN** 前端 MUST 以阅读态展示文档
- **AND** 前端 MUST 展示可理解的只读原因
- **AND** 关闭只读文档 MUST NOT 触发未保存确认

#### Scenario: checkbox-only 态

- **WHEN** 文档能力中 `task_toggle_only` 为 true
- **THEN** 前端 MUST 只渲染任务清单 checkbox 操作
- **AND** 前端 MUST NOT 显示 Vditor 工具栏、源码编辑区、全文保存入口或分栏编辑入口

#### Scenario: 待开发 Change 文档展示范围

- **WHEN** 用户查看待开发阶段的 OpenSpec Change 文档
- **THEN** 前端 MUST 清楚展示文档属于当前 Change 工作区
- **AND** 前端 MUST 避免让用户将 Change 草案 `spec.md` 与已生效 `openspec/specs/**/spec.md` 混淆

### Requirement: 验收中 tasks 勾选能力

系统 MUST 在验收中阶段仅允许用户对 `tasks.md` 执行 checkbox-only 操作，不允许全文 Markdown 编辑。

#### Scenario: 验收中 tasks 返回 checkbox-only

- **WHEN** 对象处于验收中阶段且用户打开 `tasks.md`
- **THEN** 文档能力 MUST 返回 `task_toggle_only=true`
- **AND** `human_editable` MUST 为 false

#### Scenario: 验收中其他文档只读

- **WHEN** 对象处于验收中阶段且用户打开非 `tasks.md` 文档
- **THEN** `human_editable` MUST 为 false
- **AND** `task_toggle_only` MUST 为 false

#### Scenario: tasks checkbox-only 操作不产生全文编辑脏状态

- **WHEN** 用户只切换 `tasks.md` 中的任务 checkbox
- **THEN** 前端 MUST 仅标记 task toggle 待保存状态
- **AND** 前端 MUST NOT 打开完整 Markdown 未保存确认流程

### Requirement: 当前 Change 标识与中文标题
系统 SHALL 在现有卡片基础上仅增加原REQ/BUG ID下方的同字号Change ID文本行，并用同一Change中文标题替换卡片标题。

#### Scenario: 唯一当前 Change
- **WHEN** Issue 已关联唯一可确定的当前 Change
- **THEN** 系统 SHALL 在 .rc-card-top 后、.rc-card-title 前显示 Change ID，其font-size与原ID相同，当前CSS基准10.5px
- **AND** 标题保持原13.5px样式和点击目标，仅替换中文文本；新增ID不新增按钮或弹窗

#### Scenario: 无关联或多关联歧义
- **WHEN** 无Change、缺中文标题或多个关联无法唯一确定当前项
- **THEN** 系统 SHALL 分别保持原卡片、回退原Issue标题或在新增行提示待核实且保留原标题
- **AND** 不任意选择第一项或混用多个Change进度

#### Scenario: 独立卡片身份
- **WHEN** 渲染独立Change卡片
- **THEN** 系统 SHALL 使用自身ID与中文业务标题，不伪造REQ行、不重复显示同一ID，阶段动作遵循独立变更阶段按钮契约

### Requirement: 当前卡片增量视觉验收
系统 SHALL 将原型作为设计输入，最终验收结合design、acceptance、真实截图、computed style、Mock/API边界和REQ最终一致性。

#### Scenario: 实施与归档门禁
- **WHEN** 开始UI细节实现或归档
- **THEN** 系统 SHALL 先完成Skeleton和1440px首轮确认；归档前具有1440px深浅主题、关键交互、390px长ID、原ID同字号采样及REQ子文档一致性证据
- **AND** 未改区域与当前实现一致，原型演示及任务勾选不能替代真实观察

### Requirement: 独立变更的唯一迭代标签
系统 SHALL 为已完成及其他交付阶段的独立 Change 解析唯一 Sprint 标签，保持既有标签样式。

#### Scenario: 历史变更缺少迭代字段
- **WHEN** iteration 缺失、null 或空串，活动及归档 Sprint changes 中仅有唯一 Sprint ID 包含该 Change
- **THEN** 系统 SHALL 展示该 Sprint 标签，且不因 sprint.md 缺失而隐藏标签
- **AND** 文档入口仍 SHALL 要求 sprint.md 存在

#### Scenario: 歧义与显式关联
- **WHEN** 解析 Sprint 归属
- **THEN** 系统 SHALL 优先核对显式合法 iteration 与成员关系，显式错误不被反查覆盖
- **AND** 无显式 iteration 且多个 Sprint 成员关系时 SHALL 不展示标签，并提示待核实
- **AND** 同 ID 活动 Sprint SHALL 优先于归档，不使用归档补活动缺口

### Requirement: 独立变更阶段按钮
系统 SHALL 复用REQ/BUG的阶段按钮、弹窗族、权限与执行能力门禁。

#### Scenario: 阶段匹配
- **WHEN** 独立Change位于待开发、研发中或验收中
- **THEN** 系统 SHALL 分别提供开始开发、查看进度、受验收门禁控制的完成/归档入口
- **AND** 已完成及未知状态 SHALL 不显示阶段主按钮

#### Scenario: 能力与权限
- **WHEN** 用户触发阶段动作
- **THEN** 写动作 SHALL 校验项目可写、对象权限、Sprint及前置证据，不得因独立Change类型固定禁用，真实能力反馈与同阶段REQ/BUG一致
- **AND** 查看进度 SHALL 仅要求读取权限，缺tasks提示缺失；不得伪造REQ身份或执行结果
- **AND** Demo SHALL 不调用真实写入，成功执行后 SHALL 刷新稳定快照

#### Scenario: 原型验收
- **WHEN** 完成按钮增补
- **THEN** 系统 SHALL 以design、acceptance、新增1440px及关键交互截图、computed style、Mock/API声明和REQ一致性共同验收；原型仅为设计输入

#### Scenario: 无固定禁用提示
- **WHEN** 独立Change满足现有阶段文档及权限门禁
- **THEN** 系统 SHALL 不添加固定验收核对提示，使用REQ/BUG相同的动作处理器与testProgress/manualAcceptanceCount门禁
- **AND** 真实模式尚未支持的动作 SHALL 给出相同能力反馈，不执行虚假流转

#### Scenario: 独立变更从追溯正文读取中文标题

- **WHEN** trace显式标题与proposal/design业务标题均缺失，但trace正文存在有效中文一级业务标题
- **THEN** 卡片必须使用该业务标题，保留完整Change ID身份行
- **AND** 追溯、背景与动机、验证记录等通用章节名不得作为业务标题；无有效标题时回退完整Change ID

