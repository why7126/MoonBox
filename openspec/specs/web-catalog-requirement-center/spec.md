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

#### Scenario: 需求中心根层背景跟随主题

- **WHEN** 用户打开 `/requirement-center` 或等价需求中心前台页面
- **THEN** 工作台根容器、`html`、`body` 与 `#root` 必须使用与当前主题一致的背景
- **AND** 深色主题下页面向上滑动、边界 overscroll 或根容器边界外露时不得显示浅色全局背景
- **AND** 浅色主题下不得保留深色工作台根层背景
- **AND** 需求中心侧边栏、看板、抽屉、工具栏和卡片背景不得因根层同步出现透明穿透或文字可读性回归

### Requirement: 前台需求中心生命周期看板

系统 MUST 在 MoonBox 前台提供需求中心看板，保留 9 个阶段展示 Requirement 与 Bug 生命周期，并展示独立 Change 的对应交付阶段。

#### Scenario: 卡片展示治理对象摘要

- **WHEN** 看板渲染 Requirement 或 Bug 卡片
- **THEN** 卡片必须展示 ID、标题、分级标签、负责人或来源、阶段产物、更新时间、阻塞状态、研发或测试进度以及阶段主动作
- **AND** Requirement 卡片分级标签必须展示 `priority`，合法值为 `P0`、`P1`、`P2`、`P3`
- **AND** Bug 卡片分级标签必须展示 `severity`，合法值为 `blocker`、`critical`、`high`、`medium`、`low`，或产品确认的中文映射
- **AND** Requirement 与 Bug 的分级标签必须在各自合法值范围内按等级呈现可区分颜色
- **AND** Bug 卡片不得因缺少 `priority` 被默认展示为 `P2` 或其他 P 值
- **AND** 卡片必须保持当前实现的标签、文档分组、进度、底部动作和更新时间结构，仅按当前 Change 身份展示契约新增 ID 行与替换标题
- **AND** 已进入迭代规划及后续阶段的卡片必须展示唯一 `sprint-xxx` 标签
- **AND** 未纳入迭代的卡片不得展示空 Sprint 标签

### Requirement: 前台需求中心筛选与搜索

系统 MUST 支持用户按对象类型、关键字、负责人、优先级和 Sprint 聚焦需求中心看板范围，并在 Sprint 筛选选项中展示可追溯的 Sprint 状态。

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
- **AND** Sprint 筛选新增状态展示不得改变默认选中、手动选择、搜索叠加、刷新、项目切换或统计口径

#### Scenario: Sprint 筛选展示状态

- **WHEN** 用户打开需求中心工具栏中的 Sprint 筛选下拉
- **THEN** 每个具体 Sprint 选项 MUST 展示 Sprint ID 或名称以及状态信息
- **AND** “全部 Sprint” MUST 作为聚合筛选项展示，不得绑定或伪造单个 Sprint 状态
- **AND** `planning`、`in_progress`、`completed` 和归档目录事实 MUST 分别映射为规划中、进行中、已完成和已归档
- **AND** 状态缺失、非法或事实源冲突时 MUST 展示“状态待核实”或等价安全文案，且不得阻断其他 Sprint 选择
- **AND** 状态展示 MUST 来自需求中心稳定快照、Sprint 结构化字段或后端可追溯派生结果，前端不得凭排序、选中项或 ID 文案临时推断状态

#### Scenario: Sprint 状态展示保持安全和可达

- **WHEN** 用户在深色主题、浅色主题、窄屏、长 Sprint 名称、键盘导航或权限受限场景中使用 Sprint 筛选
- **THEN** 状态文本或标签 MUST 可读、可聚焦、可选择，且不得撑破筛选栏、遮挡选项或改变卡片布局
- **AND** 无权 Sprint 不得进入可见选项
- **AND** 状态异常、授权失败或上下文加载失败不得泄漏内部路径、原始日志或无权对象内容
- **AND** 工具栏 Sprint 筛选与加入迭代弹窗的 Sprint 状态口径 MUST 保持一致

#### Scenario: 用户手动刷新 9 阶段看板

- **WHEN** 用户点击需求中心工具栏中的刷新图标按钮
- **THEN** 系统必须重新读取需求中心上下文并更新统计区和 9 阶段看板
- **AND** 系统必须保留当前搜索、对象类型、负责人、优先级和 Sprint 筛选条件
- **AND** 刷新过程中刷新按钮必须展示 loading 语义并避免重复点击
- **AND** 刷新失败时不得清空当前看板，必须保留最近一次成功加载的数据并给出轻量失败提示

### Requirement: 阶段动作门禁

系统 MUST 根据治理对象类型和当前阶段提供正确主动作，并在阶段产物缺失、权限不足、版本冲突、同步失败或验收未完成时阻止错误流转。REQ 卡片的需求分析、生成需求、完善需求、发起评审、加入迭代、生成 OpenSpec、开始开发和完成归档八类动作 MUST 使用完整对象身份、授权项目和后端事实源裁判，写操作完成状态 MUST 以产物校验、Workflow Sync 成功和事实源重读为准。

#### Scenario: REQ 卡片八动作真实执行

- **GIVEN** 用户在需求中心查看一个有权访问的 REQ 卡片
- **WHEN** 用户点击需求分析、生成需求、完善需求、发起评审、加入迭代、生成 OpenSpec、开始开发或完成归档动作
- **THEN** 系统 MUST 向后端传递完整 REQ ID、授权项目、动作类型、对象版本和幂等标识
- **AND** 后端 MUST 读取最新文件事实、权限、阶段、材料和 Sprint/Change 关系后裁判
- **AND** 前端不得凭本地状态、按钮文案、短编号或客户端路径直接推进生命周期

#### Scenario: 只读分析不写治理事实

- **GIVEN** REQ 可读但尚未满足写动作材料门禁
- **WHEN** 用户点击需求分析并在 Chat 中要求生成、开发或归档
- **THEN** 系统 MUST 保持只读分析模式
- **AND** 不得修改 requirement、trace、registry、CHANGELOG、Sprint 或 OpenSpec 文件
- **AND** 不得触发 Workflow Sync 生命周期事件
- **AND** 必须提示用户使用对应受控动作完成写入

#### Scenario: 写操作完成必须重读事实源

- **WHEN** 七类写动作执行完成
- **THEN** 系统 MUST 先确认允许范围内的产物已写入并通过校验
- **AND** 必须确认对应 Workflow Sync 成功
- **AND** 必须重新读取 REQ、Sprint、Change 或归档事实源后刷新卡片和文档入口
- **AND** 请求已受理、Chat 消息发送、模型回复或任务全勾均不得单独作为完成证据

#### Scenario: 工作区与候选不得替代事实源

- **WHEN** Chat 工作台、执行工作区或治理 candidate 产生了文件差异、assistant 回复或模型完成信号
- **THEN** 系统 MUST 将这些内容视为候选或执行证据
- **AND** 必须在应用前校验 manifest、revision、binding revision 和最新事实源版本
- **AND** 应用后必须完成 Workflow Sync 并重读事实源
- **AND** 若工作区或 candidate 所基于的事实源已变化，系统 MUST 进入 conflict、stale 或待恢复状态
- **AND** 前端不得展示成功、刷新卡片阶段或更新文档入口为完成态

#### Scenario: 部分写入和同步失败可恢复

- **WHEN** 写操作在多文件写入、Workflow Sync、事实源重读或目录迁移期间失败
- **THEN** 系统 MUST 区分未执行、部分写入、同步失败、版本冲突、权限不足和已完成
- **AND** 必须保留可查询操作身份和安全错误摘要
- **AND** 重试时必须先核实已落盘步骤，再重放未完成步骤
- **AND** 不得声称全部回滚或伪造成功状态

#### Scenario: 开发启动与归档投影

- **WHEN** 用户从 REQ 卡片触发开始开发
- **THEN** 系统 MUST 在前置门禁通过并记录真实 `opsx.start` 后才展示研发中投影
- **AND** REQ canonical 状态在归档前仍保持 `in_sprint`
- **WHEN** 用户触发完成归档
- **THEN** 系统 MUST 校验任务、测试、人工验收、文档同步和 Change 归档门禁
- **AND** 所有关联 Change 归档闭环后才允许 REQ 进入 done

#### Scenario: Requirement 和 Bug 主动作按阶段映射

- **WHEN** 用户查看某个阶段的 Requirement 或 Bug 卡片
- **THEN** 系统必须根据对象类型与阶段映射 `req-*`、`bug-*`、`sprint-*` 或 `opsx-*` 主动作
- **AND** 卡片主动作必须展示产品化文案，例如“生成需求 →”“加入迭代 →”“开始开发 →”“完成 / 归档 →”
- **AND** 实现必须保留可追溯命令映射，避免仅以裸 `/req-*` 或 `/opsx-*` 命令作为用户可见按钮文案
- **AND** 采集池对象必须指向生成文档动作
- **AND** 待评审对象必须指向评审动作
- **AND** 已通过对象必须指向 Sprint 规划动作
- **AND** 迭代规划对象必须指向 OpenSpec Change 创建动作
- **AND** 每个动作必须声明产品真实能力状态，区分真实候选写入、真实应用写入、demo 模拟和仅展示

#### Scenario: 未接入真实链路的命令不得模拟成功

- **WHEN** 用户在非 demo 需求中心触发 `complete`、`review`、`sprint-propose`、`opsx` 系列中尚未接入真实治理写入链路的动作
- **THEN** 系统必须阻止真实流转
- **AND** 系统必须展示该动作尚未接入产品写入链路的提示
- **AND** 提示必须给出对应 Codex 命令和完整对象 ID
- **AND** 系统不得创建虚假的成功状态、不得仅通过前端临时 state 移动卡片、不得写入伪造 trace 或 registry

#### Scenario: Bug Generate 使用真实治理候选链路

- **GIVEN** Bug 处于采集池阶段且 `capture.md` 与 `trace.md` 均存在并非空
- **WHEN** 用户在需求中心真实模式触发 Bug Generate
- **THEN** 系统必须以 `BUG-*` 完整 ID 和 `bug-generate` action 调用治理准备链路
- **AND** Chat 输入框必须只展示简洁 `/bug-generate <BUG-full-id>` 命令，不得裸露内部治理约束、写入范围或 dry-run 规则
- **AND** Chat 历史消息展示与复制内容也必须只暴露用户可理解的短命令，不得展示隐藏执行上下文
- **AND** Chat turn 与 `chat_messages` 必须只保存用户可见短命令，执行所需内部治理约束必须由后端基于治理候选恢复，不得作为前端隐藏 prompt 或用户消息正文落库
- **AND** 用户手动编辑可见草稿后，系统不得继续追加旧治理约束
- **AND** Chat 主对话区不得展示大型治理成果面板、`查看成果`、`待应用成果` 或 `审阅治理成果` 弹窗
- **AND** Chat assistant 消息、外层消息历史轨道、正文 bubble、markdown 容器，以及 TurnActivity 的执行中 status/alert 文案必须在运行态占满对话区可用宽度展示执行摘要，用户命令消息仍必须保持右侧气泡宽度限制
- **AND** 该 assistant 满宽规则不得按命令名或 action 白名单生效；`req-generate`、`req-complete`、`bug-generate`、`bug-complete`、review、sprint、opsx 和普通 Chat 的 role=assistant running 输出必须使用同一布局规则
- **AND** 满宽回归证据必须包含运行态 DOM/computed style 命令矩阵，不得只校验 CSS 源码或只覆盖 generate 命令
- **AND** TurnActivity 的工具调用/完成状态摘要必须作为轻量 meta 左对齐到 assistant 内容列，不得漂浮到正文上方中间或被拉成满宽输出块
- **AND** 治理候选、实际 Diff、应用状态和失败原因必须通过后台应用链路、轨迹或轻量提示承载
- **AND** 合法候选通过写入边界、manifest、revision、dry-run 和冲突校验后，后端必须自动创建 application 并交由 controller 应用
- **AND** 历史打开会话时，pending 且已有后端 application 的候选必须轮询 operation，prepared 空候选不得申请 application
- **AND** 前端历史入口不得向 `/governance-candidates/{candidate_id}/applications` 发起自动 application POST
- **AND** 历史打开会话时不得恢复或渲染治理成果大面板、`待应用成果`、`查看成果` 或 `审阅治理成果`
- **AND** 自动应用失败、版本冲突、越界、恢复阻塞或校验 warning 时，系统不得展示治理成果大面板，只能展示轻量错误或轨迹提示
- **AND** 应用成功后必须重新读取需求中心 context
- **AND** 部署到产品运行态后，运行中的 Web bundle 不得包含 `待应用成果`、`查看成果`、`审阅治理成果` 或 `确认应用` 面板文案
- **AND** Web 启动时必须标记当前构建版本，并在检测到当前脚本资产不是最新 HTML 声明资产时自动刷新一次
- **AND** Chat 历史入口必须清理旧版治理成果面板 DOM，避免旧 bundle、缓存或历史节点恢复已移除的面板
- **AND** Chat 新会话默认执行配置的推理程度必须为 Low，后端 capabilities 默认与前端 fallback 必须保持一致
- **AND** 发送前必须完成执行器 sandbox/dry-run preflight，并区分 `executor_unavailable` 与 `governance_validation_failed`
- **AND** Chat 工作台必须将 chat、governance 和 events 的 `NetworkError` / `Failed to fetch` 归一化为中文局部提示，不得向用户展示浏览器原生英文错误
- **AND** 导航、历史恢复或组件卸载产生的 `AbortError` 不得渲染为错误；已有成功消息不得被 turns/events/governance 轮询失败覆盖成全局错误
- **AND** 所有写入型产品命令以当前治理文件 manifest/revision 校验；默认副本模式自动同步隔离工作区，显式本地真实仓库模式直接使用 `source_root` 当前工作树
- **AND** 治理投影不要求 .git；source_root 与投影内容实际不一致时返回 workspace_fact_source_stale / manifest_mismatch
- **AND** 显式本地真实仓库模式不得展示候选二次应用入口，命令成果直接写入真实仓库后必须刷新需求中心看板事实源投影
- **AND** Toast 提示同步事实源，无需提交 Git；不得把未提交直接解释为执行器不可见
- **AND** 写入命令仍校验完整对象 ID、registry path、trace status 和必需文档，状态或文档缺失返回 governance_validation_failed
- **AND** 看板阶段投影必须来自 `trace.md`、registry、CHANGELOG、Sprint 和 Change 事实源，而不是仅来自前端临时 state

#### Scenario: Req Generate 保持不回退

- **WHEN** 用户继续对采集池 Requirement 执行 Req Generate
- **THEN** 既有 `req-generate` 准备、候选、自动应用和刷新闭环必须保持可用
- **AND** 新增 Bug Generate 能力不得放宽 Requirement 的文件写入 allowlist 或状态门禁

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

#### Scenario: OpenSpec 设计承接原型契约

- **WHEN** 需求中心 UI 型需求进入 OpenSpec Change
- **THEN** Change design.md 必须写明 Prototype Source、Conflict Resolution、UI Contract 和 UI Skeleton
- **AND** UI Contract 必须声明事实源优先级、品牌分层、Token、组件、交互状态、权限规则、Mock/API 边界和 computed style 验收点
- **AND** UI Skeleton 必须覆盖页面结构、区域边界、组件层级、状态容器、数据依赖、可测选择器和 1440px 验收焦点
- **AND** 对于 REQ-0033，UI Skeleton 必须覆盖工具栏、多选下拉、搜索输入、复选框候选项、无结果空态、单维清空、全局清空、权限态、选中摘要和窄屏摘要

#### Scenario: 视觉验收覆盖现代 Ops 关键状态

- **WHEN** 需求中心 UI 变更进入实现验收
- **THEN** 系统必须保留 1440px 桌面视口视觉证据
- **AND** 视觉证据必须覆盖默认首屏、侧边栏展开/收起、用户菜单、筛选 Popover、看板横向滚动、空列、错误态、卡片 hover、右侧抽屉、AI 入口、深浅主题和窄屏状态
- **AND** 对于 REQ-0033，视觉证据还必须覆盖多选摘要、下拉内搜索、搜索无结果、候选项内部滚动、全选入口、清空入口、刷新保留筛选和文本溢出检查
- **AND** 验收材料必须记录关键筛选控件的 computed style 证据，包括触发器尺寸、Popover 宽高、复选框尺寸、focus ring、边框、背景、文字颜色和滚动容器高度
- **AND** OpenSpec 归档前必须确认 requirement.md、acceptance.md、trace.md、Change design.md、实现证据和验收结论一致

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

系统 MUST 支持从需求中心卡片安全查看关联 Markdown/HTML 文档，并支持卡片标题和归档入口新 Tab 打开对象详情。Markdown 文档抽屉 MUST 只承载当前文档阅读、文档属性和既有编辑能力，不得在正文前渲染 Change 追溯属性模块。

#### Scenario: Markdown 文档从右侧抽屉打开

- **WHEN** 卡片关联文档包含 `.md` 文件
- **THEN** 文件名必须展示为可点击入口
- **AND** 点击后必须从右侧打开 Markdown 文档抽屉
- **AND** 抽屉必须展示当前对象 ID、文件名和文档内容
- **AND** 抽屉打开后必须显示背景蒙层
- **AND** 桌面端抽屉必须支持 420px-760px 范围内拖拽调整宽度，移动端必须使用全屏宽度
- **AND** 文件点击不得冒泡触发卡片详情或阶段动作

#### Scenario: Markdown 文档抽屉不展示 Change 属性模块

- **GIVEN** 用户打开 REQ、BUG 或独立 Change 的 Markdown 文档抽屉
- **WHEN** 文档抽屉完成加载
- **THEN** 抽屉正文前必须只保留文档属性区和当前文档正文
- **AND** 抽屉不得渲染“Change 追溯属性”标题、模块边框、左侧色条、任务进度文案、告警分隔符、关联 Change 列表或模块内 Change 文档按钮
- **AND** 文档属性区必须继续使用面向用户的“文档属性”标题，并保留展开/收起能力
- **AND** 删除模块后不得保留空白占位、残留分隔线、贴边文本或正文顶部断层

#### Scenario: 抽屉外 Change 文档入口保持可达

- **GIVEN** REQ 或 BUG 关联一个或多个 Change
- **WHEN** 用户需要查看关联 Change 的 proposal、design、tasks 或 Change trace
- **THEN** 系统必须通过抽屉外的卡片、详情或既有文档分组入口提供可达路径
- **AND** 卡片侧关联 Change 文档入口必须保持紧凑，使用直接紧凑文档入口承接，不得在卡片上展开完整 Change ID
- **AND** Issue 自身文档与关联 Change 文档合并展示时，`proposal.md`、`spec.md`、`design.md`、`tasks.md`、`sprint.md` 等同名文档必须按 Issue、Change、Sprint 来源和所属对象身份区分，不得合并真实存在的不同内容
- **AND** 多 Change 场景不得默认选择第一个 Change
- **AND** 系统不得把多个 Change 的任务进度汇总成单个 Change 的进度
- **AND** Issue trace 与 Change trace 的入口标签或上下文必须可区分

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

#### Scenario: 文档抽屉视觉与权限回归

- **WHEN** 文档抽屉在 1440px、窄视口、深色主题或浅色主题下展示
- **THEN** 文档属性、正文、关闭、全屏或恢复、滚动和长标题/长 ID/长正文不得重叠或溢出
- **AND** 实现必须提供 1440px 与窄视口视觉证据，以及文档属性区和滚动容器的 computed style 或等价检查
- **AND** 无权对象、只读成员、冻结空间、跨项目同 ID 和直接文档 URL 不得因模块删除暴露受限内容

### Requirement: 全局 AI 聊天与卡片动作反馈

系统 MUST 在需求中心提供全局 AI 聊天悬浮入口，并用右侧聊天抽屉承载用户消息、卡片动作上下文、命令执行反馈和异常分支。系统 MUST 在卡片动作触发 Chat 时基于对象类型和对象 ID 进入对象会话：同一 REQ、BUG 或 Change 优先复用最近的未归档、未删除且当前用户有权访问的会话；不存在可用会话时才新建对象会话。生成类治理动作 MUST 在同一对象会话内创建新的 turn 和新的 candidate，不得默认复用历史 candidate。

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

#### Scenario: 同一对象复用最近可用会话

- **WHEN** 用户从同一个 REQ、BUG 或 Change 卡片触发 Chat 动作
- **THEN** 系统必须按对象类型和对象 ID 查询可复用会话
- **AND** 系统只允许复用未归档、未删除、当前用户有权访问且允许继续交互的会话
- **AND** 存在多个可用会话时必须按服务端稳定事实源选择最新会话，不得依赖前端本地列表顺序
- **AND** 不存在可用会话时必须创建新的对象会话并写入对象关联

#### Scenario: 生成类动作新建本轮候选

- **WHEN** 用户从卡片触发生成、完善、评审、加入迭代、生成 OpenSpec 或等价生成类治理动作
- **THEN** 系统必须在目标对象会话内创建新的 turn
- **AND** 系统必须为本轮动作创建新的 candidate
- **AND** 历史 candidate 只能作为历史上下文或显式引用来源，不得被默认标记为本轮候选或本轮可提交结果
- **AND** 本轮 candidate 必须能追溯到本轮 turn、触发动作、对象类型、对象 ID、操作者和创建时间

#### Scenario: 失败与重复提交不流转卡片阶段

- **WHEN** 会话查找、新建会话、追加 turn、创建 candidate、权限校验或重复提交识别失败
- **THEN** 系统必须展示可区分的失败反馈
- **AND** 系统不得刷新卡片阶段
- **AND** 系统不得写入 REQ、BUG、Change、Sprint 或 OpenSpec 事实源
- **AND** 行为事件、请求日志或 Task Trace 只允许记录脱敏摘要

#### Scenario: 右侧抽屉互斥

- **WHEN** Markdown 文档抽屉、tasks 抽屉或 AI 聊天抽屉之一打开
- **THEN** 其他右侧抽屉必须关闭或收起
- **AND** 抽屉必须支持关闭按钮、Escape 和外部点击关闭
- **AND** 内部点击不得误关闭抽屉
- **AND** 外部点击应通过蒙层完成，且不得影响抽屉内编辑、保存或拖拽宽度交互

### Requirement: Capture 新建与导入选择

系统 MUST 支持在需求中心创建 Capture，并在生成或完善阶段提供 AI 生成与文件导入选择。

#### Scenario: 用户创建 Capture

- **WHEN** 用户打开新建 Capture 工作区
- **THEN** 系统 MUST 默认显示原始文字与图片输入，不要求预填标题、类型或分级
- **AND** 系统 MUST 经 AI 整理形成未编号候选供用户编辑、改类型、合并、拆分、删除和查看来源；仅在审阅时校验标题与最终类型分级
- **AND** 用户 MUST 确认最新完整候选版本后，服务端才可分配编号并创建采集记录
- **AND** 系统 MUST 在整批目录、capture.md、trace.md、注册表、索引及编号映射校验完成后展示成功，以服务端完整 ID 刷新采集池
- **AND** 详情遵循 capture-candidate-review 能力，候选阶段不占号、不写正式目录

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
- **AND** 同一操作者、项目和幂等键的相同请求 MUST 返回同一操作与ID；候选批次同一确认快照更换请求键也必须返回原任务，已确认批次不能改版本重建
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

- **WHEN** 用户在候选审阅中切换Capture类型
- **THEN** REQ展示priority P0/P1/P2/P3，BUG展示severity blocker/critical/high/medium/low；切换类型保留候选身份、内容和图片，重新建议目标类型分级供审阅，不做两类分级直接映射
- **AND** 提交仅包含对应类型字段，缺失、非法值和混用字段必须拒绝
- **AND** capture、trace、注册表和索引保存相同正式分级，不固定BUG为medium，不写入异类字段或hint

#### Scenario: Capture 弹窗尺寸与分级解释

- **WHEN** 用户在桌面打开Capture弹窗
- **THEN** 输入态工作区使用居中单列布局，材料抽屉、MD 编辑器、草稿状态和删除草稿属于同一张 card；来源材料以紧凑 pill chip 展示，文本文件以内嵌来源块进入该编辑器，图片以同一材料流的 pill chip 展示；`AI 整理候选` 位于 card 外并全宽显示；900px以下单列，390px无横向溢出，头部步骤与主操作保持可达
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

系统 SHALL 将原型作为设计输入，最终验收结合 Change design、acceptance、真实截图、computed style、Mock/API 边界和 REQ 最终一致性。

#### Scenario: 八动作浮层与反馈验收

- **WHEN** 实现 REQ 卡片八动作入口和反馈容器
- **THEN** 系统 SHALL 在 Change design 中维护动作按钮到 modal 类型、selector、状态和验收证据的矩阵
- **AND** 实现前 SHALL 完成 UI Skeleton 和 1440px 首轮确认
- **AND** 实现完成前 SHALL 验证 1440px、390px、矮视口、深浅主题、权限差异、错误态、长 ID、外部点击关闭和内部 `stopPropagation` 场景
- **AND** 验收 SHALL 记录关键 computed style、Mock/API 边界和 linked REQ 文档最终一致性

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

系统 SHALL 复用REQ/BUG的阶段按钮、弹窗族、权限与执行能力门禁。验收中独立 Change 的完成/归档入口 SHALL 检查 Change 内交付验证来源，但 SHALL NOT 固定要求 `acceptance.md` 或 `verification.md`；当存在非空 `trace.md` 验证类章节或有效 `trace.acceptance_refs` 时，系统 SHALL 接受其作为证据入口。

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

#### Scenario: 接受 Change 内非固定验证来源

- **WHEN** 独立 Change 处于验收中且没有 `acceptance.md` 或 `verification.md`
- **THEN** 系统 SHALL 查找 `trace.acceptance_refs` 指向的 Change 内 Markdown
- **AND** 未声明显式引用时，系统 SHALL 查找 `trace.md` 中非空的验证类章节
- **AND** 找到有效来源时 SHALL 不展示“未找到交付验证记录”
- **AND** 未找到任一来源时 SHALL 提示验收来源待核实

#### Scenario: 独立变更从追溯正文读取中文标题

- **WHEN** trace显式标题与proposal/design业务标题均缺失，但trace正文存在有效中文一级业务标题
- **THEN** 卡片必须使用该业务标题，保留完整Change ID身份行
- **AND** 追溯、背景与动机、验证记录等通用章节名不得作为业务标题；无有效标题时回退完整Change ID

### Requirement: 需求中心默认当前迭代范围
系统 MUST 在前台需求中心默认聚焦当前迭代和未纳入 Sprint 的相关卡片，并通过既有 Sprint 多选保留查看非当前范围的入口，不得新增独立范围按钮组或筛选模块下方提示模块。

#### Scenario: 首次进入默认当前迭代
- **WHEN** 用户首次进入需求中心
- **THEN** 系统必须默认展示当前迭代和未纳入 Sprint 的 REQ、BUG 和独立 Change 卡片
- **AND** 既有 Sprint 多选必须直接选中当前 Sprint 和“未纳入 Sprint”
- **AND** Sprint 候选可用 meta 或状态标识表达“当前迭代”，但不得新增 `当前迭代｜全部｜历史｜未纳入迭代｜归档` 范围筛选模块
- **AND** 系统不得让用户误以为当前项目只存在这些卡片

#### Scenario: 重置筛选恢复默认范围
- **GIVEN** 用户已清空 Sprint 多选、选择历史/归档 Sprint 或选择单个 Sprint
- **WHEN** 用户点击重置筛选或回到默认视图
- **THEN** 系统必须恢复当前 Sprint 和“未纳入 Sprint”的默认选择
- **AND** 不得恢复为全量范围，除非用户显式清空 Sprint 多选

#### Scenario: 查看非当前范围
- **WHEN** 用户清空 Sprint 多选，取消“未纳入 Sprint”，或在 Sprint 多选中选择历史/归档 Sprint
- **THEN** 看板必须展示用户显式选择范围内的卡片
- **AND** 搜索、对象类型、负责人、优先级、Sprint、文档阅读和阶段动作必须继续按既有权限与筛选规则工作

#### Scenario: 多个当前迭代
- **WHEN** 系统存在多个当前迭代候选
- **THEN** 默认范围必须展示全部当前迭代和未纳入 Sprint 的相关卡片
- **AND** Sprint 多选必须默认选中全部当前 Sprint 和“未纳入 Sprint”，并提供进一步取消或选择单个 Sprint 的显式操作
- **AND** 系统不得无证据地只选择编号最大、更新时间最新或读取顺序靠前的 Sprint

#### Scenario: 无当前迭代或当前迭代无卡片
- **WHEN** 当前项目没有当前迭代或当前迭代范围内没有卡片
- **THEN** 页面必须展示稳定空态
- **AND** 页面必须默认保留“未纳入 Sprint”对象，并可通过清空 Sprint 多选或选择历史 Sprint 查看其他非当前对象
- **AND** 系统不得静默展示全量卡片并伪装为当前迭代结果

#### Scenario: UI 视觉与响应式验收
- **WHEN** 需求中心默认当前迭代范围在 1440px 桌面、窄屏、深色主题或浅色主题下展示
- **THEN** Sprint 多选、筛选控件、指标区、看板列头和卡片文本不得重叠或溢出
- **AND** 看板 sticky 表头、横向滚动和卡片密度必须保持父需求基线
- **AND** 实现必须提供 1440px 和关键交互视觉证据，以及必要的 computed style 验收摘要

### Requirement: 需求中心 Sprint 数量指标
需求中心 MUST 在指标区展示项目级 Sprint 数量指标，包含已完成 Sprint 数与总体 Sprint 数，并与既有需求中心视觉、深浅主题和响应式布局保持一致。

#### Scenario: 展示项目级 Sprint 数量
- **WHEN** 用户进入需求中心且上下文请求成功
- **THEN** 指标区必须展示 Sprint 已完成数量与总体数量
- **AND** 卡片标题文案必须为 `Sprint`
- **AND** 文案必须表达“已完成 / 总体”或等价语义
- **AND** 该指标必须让用户理解为当前项目级 Sprint 总览
- **AND** 项目级口径说明必须通过指标名后的统一 tooltip 呈现，不得在卡片底部额外展示辅助说明

#### Scenario: 对象指标展示完成比例
- **WHEN** 用户查看需求中心指标区
- **THEN** 需求、Bug 与独立 Change 指标必须展示“已完成 / 总体”或等价比例
- **AND** 这些对象指标必须继续跟随当前搜索、对象类型、负责人、优先级和 Sprint 筛选条件变化
- **AND** 每个指标名后必须提供统一信息图标，鼠标悬停或键盘聚焦时展示该指标的统计口径说明

#### Scenario: 无 Sprint 时展示空态数字
- **WHEN** 当前项目没有任何有效 Sprint
- **THEN** Sprint 数量指标必须展示 `0 / 0` 或等价空态
- **AND** 页面不得隐藏该指标卡或留下空白占位

#### Scenario: 筛选不改变 Sprint 总览
- **WHEN** 用户修改搜索关键字、对象类型、负责人、优先级或 Sprint 筛选
- **THEN** 看板卡片与既有局部统计可以按筛选条件刷新
- **AND** Sprint 数量指标必须保持项目级总览数字

#### Scenario: 刷新与空间切换更新指标
- **WHEN** 用户首次加载需求中心、手动刷新或切换空间
- **THEN** Sprint 数量指标必须跟随后端上下文聚合结果刷新
- **AND** 刷新中必须保持指标区布局稳定

#### Scenario: 加载、错误和权限状态安全展示
- **WHEN** Sprint 指标正在加载、接口失败、权限不足或数据解析失败
- **THEN** 页面必须展示骨架、上一可用值、`0 / 0` 或轻量错误态之一
- **AND** 页面必须提供重试或随下一次刷新恢复的路径
- **AND** 错误文案不得暴露本机绝对路径、系统用户名、内部堆栈、密钥、token、`.env` 内容或未脱敏治理文档全文

#### Scenario: 响应式与主题一致
- **WHEN** 用户在 1440px、1024px 或 390px 视口查看需求中心
- **THEN** Sprint 数量指标不得与相邻指标、筛选区或看板列头重叠
- **AND** 主数字、标题和 tooltip 触发图标不得溢出容器
- **AND** 深色主题与浅色主题下的背景、边框、字号、间距和圆角必须复用需求中心既有视觉体系

### Requirement: 当前迭代容量展示

系统 MUST 在前台需求中心展示当前迭代容量，支持单当前迭代、两个当前迭代、默认容量、超量、待核实和刷新失败状态，并保持现有看板结构和筛选体验。

#### Scenario: 单当前迭代容量展示
- **WHEN** 用户打开需求中心
- **AND** 上下文中包含一个当前迭代容量项
- **THEN** 页面必须在当前迭代相关统计或筛选区域展示该容量项
- **AND** 容量项必须展示 Sprint ID 和 `已使用容量 / 总容量`
- **AND** 容量单位必须沿用 Sprint 容量治理口径
- **AND** 容量项不得分散到每张治理对象卡片内

#### Scenario: 两个当前迭代容量展示
- **WHEN** 上下文中包含两个当前迭代容量项
- **THEN** 页面必须同时展示两个容量项
- **AND** 两个容量项视觉权重必须一致
- **AND** 页面不得默认隐藏其中一个容量项
- **AND** 窄屏下可以换行、折叠或纵向排列，但必须保留 Sprint ID 和容量比例可见

#### Scenario: 容量状态展示
- **WHEN** 容量项状态为正常、接近上限、已超量或待核实
- **THEN** 页面必须为不同状态提供可辨识视觉反馈
- **AND** 已超量状态只能提示规划风险，不得自动阻止用户浏览、筛选或打开文档
- **AND** 待核实状态必须展示可理解提示，不得显示伪造的 `0/0`

#### Scenario: 默认容量提示
- **WHEN** 容量项总容量来自默认规则
- **THEN** 页面必须提供轻量提示说明该值来自默认容量
- **AND** 显式容量存在时页面必须优先展示显式容量

#### Scenario: 刷新失败保留容量
- **WHEN** 用户点击刷新或切换筛选后上下文刷新失败
- **AND** 页面已有上一次成功容量结果
- **THEN** 页面必须保留上一次成功容量信息
- **AND** 页面必须展示轻量失败提示
- **AND** 页面不得清空整个看板或删除 9 阶段列

#### Scenario: 当前迭代容量视觉验收
- **WHEN** 完成当前迭代容量 UI 实现
- **THEN** 验收必须覆盖 1440px 桌面视口下的正常、双当前迭代、超量、待核实和刷新失败状态
- **AND** 验收必须覆盖深色主题和浅色主题
- **AND** 验收必须覆盖窄屏下文本不遮挡统计区、筛选器、看板列头、卡片 ID 或阶段动作
- **AND** 验收必须记录截图、computed style 或等价证据

#### Scenario: 容量条局部参考稿一致
- **WHEN** 用户验收要求当前迭代容量区域参考附件 HTML 的容量模块
- **THEN** 页面必须将当前迭代容量展示为紧凑横向容量条
- **AND** 容量条必须保留 Sprint ID、容量来源、容量比例、进度轨和状态提示
- **AND** 页面不得展示额外可见标题“当前迭代容量”
- **AND** 页面可以保留 `aria-label` 或等价无障碍语义
- **AND** 该调整不得改变需求中心其他统计、筛选、看板或卡片模块

### Requirement: 当前迭代归档入口

系统 SHALL 在前台需求中心当前迭代容量区域或当前迭代操作区提供受 Sprint archive readiness 控制的“归档当前迭代”入口，并通过确认流程复用既有 Sprint archive 门禁。

#### Scenario: 展示可进入确认的归档入口
- **WHEN** 用户打开需求中心
- **AND** 当前迭代存在
- **AND** 当前迭代 `used_capacity` 大于 0 人天
- **AND** Sprint archive readiness 汇总允许进入确认流程
- **THEN** 页面 SHALL 在当前迭代容量区域或当前迭代操作区展示“归档当前迭代”入口
- **AND** 入口 SHALL 明确绑定目标 Sprint
- **AND** 入口 SHALL 靠近容量信息展示，不得分散到每张治理对象卡片内

#### Scenario: 未归档闭环时隐藏或禁用入口
- **WHEN** 当前迭代 `used_capacity` 大于 0 人天
- **AND** Sprint 范围内任一 REQ、BUG 或独立 Change 未归档闭环
- **THEN** 页面 SHALL 隐藏归档入口或展示禁用态
- **AND** 若展示禁用态，页面 SHALL 展示安全摘要和修复方向
- **AND** 页面 MUST NOT 允许用户进入可执行归档路径
- **AND** 安全摘要 MUST NOT 泄露不可见资源细节、内部路径、堆栈、密钥或 `.env` 内容

#### Scenario: 容量或当前迭代不满足时不可执行
- **WHEN** 无当前迭代、无可见 Sprint、容量待核实、当前迭代解析失败或 `used_capacity` 等于 0
- **THEN** 页面 MUST NOT 提供可执行归档入口
- **AND** 页面 MAY 隐藏入口或展示不可用摘要

#### Scenario: 多当前迭代绑定目标 Sprint
- **WHEN** 需求中心存在多个当前迭代
- **THEN** 每个归档入口或确认流程 SHALL 明确绑定一个目标 Sprint
- **AND** 系统 MUST NOT 默认选择编号最大、更新时间最新或容量最高的 Sprint 直接进入归档
- **AND** 迟到的 readiness 或归档响应 MUST NOT 覆盖用户当前正在确认的其他 Sprint

#### Scenario: 点击入口进入确认流程
- **WHEN** 用户点击可进入确认的归档入口
- **THEN** 页面 SHALL 打开归档确认弹窗或等价 action modal
- **AND** 确认流程 SHALL 展示目标 Sprint ID、当前状态、容量摘要、门禁检查结果和归档影响
- **AND** 页面 MUST NOT 因入口点击直接执行 Sprint archive

#### Scenario: 取消确认不改变事实源
- **WHEN** 用户在归档确认流程中点击取消或按约定关闭弹窗
- **THEN** 系统 MUST NOT 改变 Sprint、REQ、BUG、Change、验收报告或 Workflow Sync 状态
- **AND** 页面 SHALL 保留当前迭代容量和卡片上下文

#### Scenario: 门禁失败阻断执行
- **WHEN** Sprint archive readiness 或执行前门禁发现未归档范围、验收报告未 sign-off、权限不足或 Workflow Sync 校验失败
- **THEN** 页面 SHALL 展示失败项和修复方向
- **AND** 页面 MUST NOT 展示“强制归档”或等价绕过按钮
- **AND** 失败项入口 MUST 遵守权限过滤和脱敏规则

#### Scenario: 后端门禁是最终裁判
- **WHEN** 用户确认执行归档
- **THEN** 服务端或既有治理命令 MUST 重新校验目标 Sprint、权限、未归档范围、验收 sign-off 和 Workflow Sync
- **AND** 服务端 MUST NOT 信任客户端传入的 readiness、权限、Sprint ID 或行为链路字段作为最终授权依据
- **AND** 前端自行判定通过 MUST NOT 直接写入归档结果

#### Scenario: 归档成功刷新需求中心
- **WHEN** Sprint archive 执行成功
- **AND** Workflow Sync 刷新成功
- **THEN** 需求中心 SHALL 刷新当前迭代列表、容量区域、Scope 投影和相关卡片状态
- **AND** 已归档 Sprint MUST NOT 继续伪装为当前迭代

#### Scenario: 执行或同步失败保留上下文
- **WHEN** 门禁检查、归档执行请求或 Workflow Sync 刷新失败
- **THEN** 页面 SHALL 保留当前迭代容量和卡片上下文
- **AND** 页面 SHALL 展示轻量失败信息或状态可能过期提示
- **AND** 页面 MUST NOT 清空看板、伪装归档成功或静默移除当前迭代

#### Scenario: 当前迭代归档入口 UI 验收
- **WHEN** 完成当前迭代归档入口 UI 实现
- **THEN** 验收 MUST 覆盖 1440px 桌面下的入口、禁用态、确认弹窗、门禁失败列表、权限态和成功/失败反馈
- **AND** 验收 MUST 覆盖 390px 窄屏、长 Sprint ID、多当前迭代和文本不重叠
- **AND** 验收 MUST 记录截图、computed style 或等价证据
- **AND** click outside 关闭若被支持，验收 MUST 覆盖弹窗内 `stopPropagation` 不误关闭、外部点击仍按约定关闭

### Requirement: Capture 弹窗按附件原型呈现单列三阶段工作台

Capture 弹窗 MUST 使用当前 MoonBox 设计系统复刻验收附件的单列三阶段布局，保持确认前不分配正式编号。

#### 场景：Capture 弹窗按附件原型呈现单列三阶段工作台

- **WHEN** 用户打开新建 Capture
- **THEN** 系统 MUST 展示居中弹窗工作台、topbar crumb、关闭动作和三点式进度，且不得展示独立顶部主标题或副标题
- **AND** 输入态 MUST 展示来源材料抽屉、紧凑材料 pill chip、唯一 MD 编辑器、草稿状态和删除草稿，并在 card 外展示全宽 `AI 整理候选` 主按钮；下方 Markdown 编辑器 MUST 作为默认输入区隐含存在，不得作为 `MD 文本` 或 `编辑器正文` chip 展示，也不得纳入来源材料计数；来源材料 MUST 仅统计并展示额外上传的图片和文本文件；上传文本文件 MUST 以独立 chip 展示文件名并提供删除入口，删除时同步移除 MD 编辑器中的对应来源文件块
- **AND** 审阅态 MUST 使用单列候选 board、条目序号栏、候选类型/分级 badge 和卡片内联编辑区域
- **AND** 结果态 MUST 展示完成状态标题、采集记录结果卡片和幂等重试说明；成功、失败或中断结果态 MUST NOT 展示圆形勾选或其他结果图标，confirming 状态 MAY 保留 loading 图标
- **AND** 条目序号、候选 badge 或内联编辑状态 MUST NOT 预占或展示正式 REQ/BUG 编号。
- **AND** 字体 family 和顶部 kicker MUST 与当前产品 Markdown 右侧抽屉保持一致：弹窗全局使用抽屉同源 body/heading/mono 字体族，`新建 CAPTURE` 使用抽屉 crumb 样式与颜色，MD 输入区使用抽屉同款 monospace 12.5px 编辑密度，输入说明应位于 MD 编辑器 placeholder 或内容 card 内轻提示。
- **AND** 审阅态 MUST NOT 展示 `AI 审阅结果` 标题；系统 MUST 仅在审阅头部展示 `{候选数} 条候选 · {需求数} 条需求 / {缺陷数} 条缺陷` 和 `合并所选` 操作；候选卡片 MUST 展示类型标签与对应分级标签，删除动作 MUST 使用危险色，且不得展示“这些仍是候选……” notice 模块。
- **AND** 候选卡片 MUST 仅在存在相似匹配时展示项目内可能相关的 REQ/BUG 提示；未发现相关项时 MUST NOT 展示 `可能相关` 模块、无匹配空态或默认 `继续创建新记录` 文案；用户选择合并到已有记录或作为已有记录补充材料时，该候选 MUST 从待创建统计和确认创建批次中排除，恢复创建后才可触发服务端编号分配。

- **AND** 输入态来源材料 MUST 保持轻量文案：不得展示 `确认前仅保存草稿`、字符计数、`图片材料` 副文案或可见 `原始材料` label；输入 card 和来源材料外部边框不得形成额外大卡片层级。
- **AND** 审阅态候选卡顶部 MUST 将选择复选框与候选标题放在同一行，类型和分级标签位于同一顶栏右侧；来源依据 MUST 在候选卡内以 `来源依据` label 加具体依据文本展示；编辑、拆分和删除相关卡内面板 MUST 在候选卡操作按钮行之后向下展开，不得打开二次弹窗；编辑按钮 MUST 显示为 `编辑` 并带编辑图标，删除按钮 MUST 带删除图标；拆分面板 MUST 使用左右两个完整子条目，每个子条目包含类目、标题和描述，且可独立选择需求或 BUG；确认创建 MUST 直接提交确认流程，不得再次弹窗确认。

### Requirement: 验收事实独立投影

系统 MUST 独立呈现 tasks.md 任务进度与可追溯验收结果，并以服务端门禁摘要指导归档动作。

#### Scenario: 任务满格而验收待复验

- **WHEN** 研发与测试任务已全部完成，但 acceptance.md 或交付证据仍有待复验项
- **THEN** 卡片必须分别显示任务完成数与待验收数或原因，不得把验收标准逐项并入任务分母
- **AND** 验收进度的分母取自所属 Issue `acceptance.md` 中可识别的 AC，研发与测试分母继续取 Change `tasks.md`
- **AND** 点击研发或测试进度必须打开当前关联 Change 的 `tasks.md` 并定位对应任务章节；文档仅存在于 Change 组时仍可用，多 Change 来源不唯一时不得借用其他 Change 的文档
- **AND** 研发、测试、验收中已知总数且完成数小于总数的进度仅将数字显示为危险色；标签与已完成数字保持常规色，未知总数不得当作未完成
- **AND** 完成或归档动作必须保持阻断，刷新后与服务端门禁状态一致

#### Scenario: 验收事实未知

- **WHEN** 验收文件缺失、解析失败或门禁事实不可确定
- **THEN** 卡片必须展示待核验状态和脱敏原因，不得推断为通过

### Requirement: 完善中事实可见

系统 SHALL 在规划中卡片按内部 draft 与 enriching 状态提供相应文档和动作，但不显示独立“草稿”或“完善中”标签；展示已存在的完善子文档、未完成提示及继续完善动作，不得以文档齐全替代根因确认门禁。

#### Scenario: 缺陷草稿已保存但根因未确认

- **WHEN** BUG 状态为 enriching 且根因未 confirmed
- **THEN** 卡片不显示独立“完善中”标签，但保留实际存在的根因/临时方案/验收文档及补证提示；长负责人名称省略显示并保留全文提示
- **AND** 继续完善仍调用 bug-complete，不自动进入待评审，不扩大文档编辑权限

#### Scenario: 草稿与完善完成状态

- **WHEN** 状态为 draft 或 pending_review
- **THEN** 分别保持规划中完善入口或待评审入口，不显示草稿状态标签或错误的完善中补证提示

### Requirement: 完善成果安全续接

系统 SHALL 保留可追溯的 req-complete 隔离成果，校验通过后由后端自动应用，不要求用户删除文件解除阻断。

#### Scenario: 原轮次留下部分文档

- **WHEN** 同对象原始基准未变化且未应用文件均在允许范围，执行器临时锁预检通过
- **THEN** 在原工作区继续完善并校验，成功后自动回写事实源、同步状态与工作区基准
- **AND** 版本冲突、越界或文档门禁未通过时保留成果且不强制流转

### Requirement: 运行消息独立内容列

系统 SHALL 将尚未落库的 assistant 运行输出放置于独立 assistant 内容区，不继承用户气泡宽度限制。

#### Scenario: 运行输出转为已保存消息

- **WHEN** 仅存在用户消息时产生运行输出，随后 assistant 消息落库或用户从历史重开会话
- **THEN** 运行输出与已保存正文均铺满 assistant 内容列，临时块在落库后移除，用户气泡保持原宽度限制

### Requirement: 已评审对象的加入迭代命令保持类型参数

系统 SHALL 在已评审需求与缺陷卡片生成带对象类型参数和完整 ID 的 Sprint 命令，并将同一命令带入 Chat Prompt。

#### Scenario: 从卡片进入 Chat

- **WHEN** 用户点击已评审 REQ 或 BUG 卡片的“加入迭代”
- **THEN** REQ Prompt 为 `/sprint-propose --req <完整REQ-ID>`，BUG Prompt 为 `/sprint-propose --bug <完整BUG-ID>`

