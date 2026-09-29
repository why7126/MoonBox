---
title: 需求中心 Capture 流程修改规格
created_at: '2026-09-15 00:17:15'
updated_at: '2026-09-16 23:12:00'
---
## MODIFIED Requirements

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

## ADDED Requirements

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
