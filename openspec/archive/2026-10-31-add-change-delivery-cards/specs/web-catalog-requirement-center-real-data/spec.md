---
title: 需求中心独立交付卡片增量规格
---
# 需求中心独立交付卡片增量规格

## MODIFIED Requirements

### Requirement: 治理文件事实源聚合

系统 SHALL 从当前授权项目的治理文档、REQ/BUG registry、Issue trace、Sprint 四件套和 OpenSpec Change 元信息聚合首版真实数据。

#### Scenario: 聚合 REQ 与 BUG registry

- **WHEN** 后端构建需求中心治理对象列表
- **THEN** 系统读取 `issues/requirements/_registry.yaml` 与 `issues/bugs/_registry.yaml` 的白名单字段

#### Scenario: trace 优先于 registry

- **WHEN** Issue `trace.md` 与 registry 摘要状态不一致
- **THEN** 系统以 `trace.md` 为优先事实源，并返回对象级漂移提示

#### Scenario: Docker 环境读取治理事实源

- **WHEN** 后端运行在 Docker Compose 中
- **THEN** 系统通过已授权项目绑定解析治理目录，以只读方式聚合 `issues/`、`iterations/`、`openspec/`、`docs/` 和 `rules/`，不得依赖容器源码或无作用域全局目录
- **AND** 受控文档写入与治理成果应用由可信写入通道统一协调，普通聚合接口不获取任意主机写权限

#### Scenario: 完整仓库归档事实

- **WHEN** registry 中的 Issue 已完成且关联 Change 或 Sprint 已迁入归档目录
- **THEN** 聚合保留 Issue 已完成阶段并读取归档事实，不因活动目录缺项回退为待开发
- **AND** 已完成事项的历史漂移作为诊断信息，不计入当前阻塞
- **AND** Issue 计数仅覆盖 registry 注册项；交付计数覆盖有效授权 Change，不自动纳入其他基础建设目录

#### Scenario: 验收文档与卡片展示分离

- **WHEN** applied Change 的卡片展示 Issue、Change 和关联 Sprint 的已生成文档入口
- **THEN** 系统将对象映射验收中，分别检查来源 Issue 验收文档与目标 Change 的交付证据，不将二者结论混用
- **AND** 卡片必须持续提供可读取的 acceptance.md 入口；文件缺失、冲突或无权时给出脱敏不可用说明，不借用其他对象的同名文件


### Requirement: 9 阶段状态映射

系统 SHALL 在完成型迁移通过执行终态、业务校验和同步一致性门禁后，将 REQ、BUG、Sprint 和 OpenSpec Change 状态映射到采集池、规划中、待评审、已评审、迭代规划、待开发、研发中、验收中、已完成 9 个阶段。

#### Scenario: 已纳入 Sprint 但未创建 Change

- **WHEN** REQ 或 BUG 状态为 `in_sprint` 且没有关联 OpenSpec Change
- **THEN** 系统将该对象映射到“迭代规划”阶段

#### Scenario: Change 已创建但未 apply

- **WHEN** 独立交付卡的目标 Change 尚未完成 apply
- **THEN** 系统依据统一执行事实源将未启动对象映射到“待开发”、已启动对象映射到“研发中”，并独立返回真实任务进度摘要

#### Scenario: 已闭环对象

- **WHEN** 当前交付卡的目标 Change 已归档，或无有效交付卡的 Issue 已按既有门禁完成
- **THEN** 系统只将该对象映射到“已完成”阶段，不因兄弟 Change 归档而完成其他卡或父 Issue

#### Scenario: approved 展示为已评审

- **WHEN** REQ 或 BUG 的底层状态为 `approved`
- **THEN** 前端展示阶段必须为“已评审”
- **AND** API 可以保留 `approved` 作为机器状态，但必须提供可展示中文阶段或等价映射

#### Scenario: 已启动零完成任务

- **WHEN** Change已记录启动事实且完成数为0/N
- **THEN** 系统 MUST 返回研发中阶段与真实零进度，并提供查看进度动作

#### Scenario: 执行状态刷新一致

- **WHEN** 启动、进度或完成事实变化并成功刷新context
- **THEN** 系统 MUST 返回与治理事实源一致的阶段、动作、任务数及更新后的快照标识
- **AND** 轮询、焦点刷新及手动刷新 MUST 不依赖仅存在于前端的模拟状态，项目切换后不能串卡

#### Scenario: 完成门禁后进入验收

- **WHEN** 新契约Change通过完成门禁并记录完成事实
- **THEN** 系统 MUST 映射为验收中；仅全勾选但无完成事实时保持研发中

#### Scenario: 文档先写入但命令尚未完成
- **WHEN** 治理文档已写入下一阶段且相关轮次仍在执行
- **THEN** 系统 MUST 保持上次已确认业务阶段，展示执行状态并禁止后续治理写入
- **AND** 开发或返修实际启动事件 MUST 及时展示研发中，不等待轮次结束

#### Scenario: 终态成功但成果未通过校验
- **WHEN** 轮次已成功但业务验证或同步失败
- **THEN** 系统 MUST 保持待核验状态，直到同一成果指纹验证及同步通过才完成迁移

#### Scenario: 只读入口保持可访问
- **WHEN** 对象正在执行或等待恢复核验
- **THEN** 系统 MUST 允许授权用户查看文档、任务进度和验收详情


### Requirement: 真实统计、筛选和搜索

系统 SHALL 基于真实治理对象支持统计、对象类型筛选、负责人筛选、优先级筛选、Sprint 筛选、枚举筛选多选、下拉内候选项搜索和关键词搜索。

#### Scenario: 统计与筛选一致

- **WHEN** 用户调整筛选条件
- **THEN** 统计区和看板卡片范围基于同一过滤结果刷新
- **AND** 同一筛选维度内多选条件必须使用 OR 语义
- **AND** 不同筛选维度之间必须使用 AND 语义
- **AND** 阶段列、阶段计数、总数和筛选无结果态必须与过滤结果一致

#### Scenario: 搜索覆盖关键字段

- **WHEN** 用户输入 ID、标题、阶段产物、负责人或来源关键词
- **THEN** 看板只展示匹配的治理对象，并保留 9 阶段列

#### Scenario: 筛选候选项来自授权上下文

- **WHEN** 系统构建对象类型、阶段或状态、优先级、负责人、Sprint、独立 Change 或归档可见性候选项
- **THEN** 候选项必须只来自当前用户有权访问的需求中心上下文
- **AND** 未授权对象不得参与候选项、数量、搜索提示、统计或异常详情
- **AND** 候选项为空、解析失败或权限不足时必须返回可展示的脱敏空态或错误态
- **AND** 系统不得暴露本机路径、内部堆栈、密钥、Token 或原始治理文档全文

#### Scenario: 下拉候选项搜索不改变事实源

- **WHEN** 用户在筛选下拉内搜索候选项
- **THEN** 系统只过滤当前授权候选项的可见范围
- **AND** 已选条件不得因搜索词变化丢失
- **AND** 下拉内搜索不得触发跨权限对象探测或服务端授权绕过

#### Scenario: 独立类型与关联搜索去重

- **WHEN** 用户选择独立 Change 类型或搜索关联 Change ID
- **THEN** 系统 SHALL 独立类型仅匹配无来源 Change；关联 ID 搜索返回目标交付卡，来源 ID/标题可匹配多个交付且按 Change 去重
- **AND** 同筛选下总数等于可见早期 Issue 卡与唯一交付卡数量之和；需求/缺陷指标另按来源 Issue 去重，不与交付数相加，页面九阶段卡片数量等于页面总数；unknown只计入单列的数据异常数量，接口原始统计不变
- **AND** 未授权对象不参与卡片、搜索提示、统计或异常详情


### Requirement: 治理对象列表

系统 SHALL 为需求中心返回能支撑卡片文档查看、动作流转、AI 聊天反馈和任务进度展示的治理对象字段。

#### Scenario: 治理对象包含文档入口

- **WHEN** 后端返回前期 Issue 或交付 Change 卡片数据
- **THEN** 每个关联文档必须包含文件名、文档类型、打开方式、可访问 URL 或禁用原因
- **AND** 前端卡片必须从文件生成阶段起持续展示当前用户可读取的入口，并标明 Issue、Change 或 Sprint 来源；采集池阶段不得隐藏已生成且可读的其他文件
- **AND** Issue 组按对象类型展示主文档和 Issue trace，不混入 Sprint 文档；Change 组直接使用 `trace.md` 文件名；Sprint 组独立展示实际存在的 `sprint.md`、`release-note.md`、`acceptance-report.md`，纯 Change 卡片没有 Issue 组
- **AND** Markdown 文件打开方式必须可映射到右侧抽屉
- **AND** HTML 文件打开方式必须可映射到新 Tab 预览

#### Scenario: 治理对象包含动作映射

- **WHEN** 后端返回前期 Issue 或交付 Change 卡片数据
- **THEN** 每个对象必须包含当前阶段主动作的产品化文案、命令映射、是否需要选择弹窗、禁用状态和禁用原因
- **AND** 命令映射必须使用完整 REQ 或 BUG ID

#### Scenario: 治理对象包含任务进度

- **WHEN** 对象关联 OpenSpec Change 且存在 `tasks.md`
- **THEN** 系统必须返回任务总数、已完成数量、是否只读、是否可验收和阻塞提示
- **AND** `tasks.md` 缺失或解析失败时必须返回脱敏错误摘要，而不是误报完成

#### Scenario: 返回独立与关联 Change 身份
- **WHEN** 授权项目快照含无 Issue 来源的 Change 或 Issue 已关联 Change
- **THEN** 系统 SHALL 为独立 Change 返回 type=change 的自身身份、只读文档、状态及进度，且不伪造 Issue；阶段动作使用真实能力元数据，依据实际文档和权限给出禁用原因，不按独立Change类型固定禁用，文档仍只读
- **AND** 前期 Issue 卡保留原 id；存在有效 Change 后，每个项目+完整 Change ID 展示唯一交付卡，多个来源仍只一张，不再保留重复聚合交付卡；缺失/冲突关系保留有权 Issue 诊断
- **AND** 卡片 ID 保持当前对象身份，中文标题按阶段来源契约选择，关联文档和进度只指向本卡目标 Change，保留来源 Issue 文档与自身 Sprint 文档，不混入兄弟 Change；无分级的独立对象不得伪造默认优先级


### Requirement: 阶段业务标题来源
系统 SHALL 按阶段选择显示标题，保留对象身份与来源信息，不读取 design 或 trace 作为 Change 业务标题。

#### Scenario: 采集及规划阶段
- **WHEN** 对象在采集池或规划至迭代规划阶段
- **THEN** 采集池使用注册表 title，规划中、待评审、已评审、迭代规划使用 requirement.md 或 bug.md 中文业务标题
- **AND** 主文档不可用时回退注册表，再回退对象 ID，并提示缺失

#### Scenario: 开发及交付阶段
- **WHEN** 对象在待开发、研发中、验收中或已完成
- **THEN** 本卡目标 Change 的 proposal 中文业务标题优先，已完成读取唯一有效归档版本
- **AND** 交付标题不可用时回退完整 Change ID，版本含糊时展示诊断；早期 Issue 才沿用主文档、注册表、Issue ID 回退

#### Scenario: 标题有效性及独立对象
- **WHEN** 读取业务文档标题
- **THEN** 优先有效中文 Frontmatter title，历史缺字段可读取有效中文一级标题；空白、纯ID、纯英文、纯文档类别不作为业务标题
- **AND** 独立 Change 仅用 proposal 标题或 Change ID；Issue 详情保留 Issue 标题，点击不改变对象身份


### Requirement: 单卡预估人天投影
系统 MUST 使用授权项目内对象有效Sprint归属的scope_estimates估算，支持已归档源；不得用总容量、优先级或story_points替代。

#### Scenario: 总量分项与异常值
- **WHEN** 存在Issue总量、关联Change分项或重复记录
- **THEN** 前期 Issue 维持唯一总量优先；交付卡仅使用明确 Change 分项，缺失显示待估算，不复制 Issue 总量或平均分摊。相同记录去重，冲突不得猜测；Sprint 容量沿用原 scope 口径，不按卡片重新累计
- **AND** 仅有限非负数有效，0和小数展示，字符串、布尔、负数和非有限数不输出数值


## ADDED Requirements

### Requirement: 交付卡目标绑定与两层验收
系统 SHALL 将项目、完整 Change ID、授权来源集合及版本绑定为交付卡上下文；任务、验收和动作不回退兄弟 Change。

#### Scenario: 任务并发与响应隔离
- **WHEN** 读取或提交本卡任务，或快速从 A 切换至 B
- **THEN** 任务章节、版本与写权限仅对应目标 Change；重复请求保持幂等，冲突不覆盖，A 迟到响应不更新 B。

#### Scenario: 多来源动作与恢复
- **WHEN** 开发、返修、验收、归档、重试或恢复需要执行目标
- **THEN** 确认、预填、后端及实际执行均校验同一项目、完整来源及 Change；需要唯一来源时先选择，变更选择清除旧预填；无明确目标传递能力时禁用，不猜测或虚构 CLI 参数。
- **AND** 来源命令保留完整 REQ/BUG ID，直接 API 也校验授权、关系、版本与动作准入；复用会话必须目标上下文一致。

#### Scenario: 历史交付与剩余范围
- **WHEN** 旧交付在旧 Sprint 完成而新交付正在开发，或父 Issue 尚有剩余范围
- **THEN** 卡片各自保留 Sprint、阶段、任务与验收；父 Issue 保持 partial/未完成，不重写归档事实、不自动完成需求。
- **AND** 返修阶段可显示研发中，但不得覆盖首次 apply 完成事实；缺验收证据不能用任务全选替代通过。

#### Scenario: 权限与观测
- **WHEN** 来源受限、关系冲突或存在旧快照、历史书签
- **THEN** 不将关联 Change 伪装为独立，不泄漏隐藏身份；含糊入口阻断或显式选择。请求和任务链路关联目标，直接 API 不伪造 UI 行为事件，遥测失败不阻断业务。

### Requirement: 独立交付卡原型验收门禁
系统 SHALL 将原型作为设计输入，最终按 Change 设计、来源验收、视觉证据、computed style、Mock/API 边界与 REQ 一致性共同验收。

#### Scenario: 实施与验收顺序
- **WHEN** 实施参考稿卡片
- **THEN** 先完成反向工程、selector映射、动作族矩阵和 UI Skeleton 首轮确认，再实现细节；保留现有卡片样式和三组文档。
- **AND** 1440×900及390×844、深浅主题、当前/历史筛选、多来源、任务、验收及阶段动作留截图与样式证据，关闭/Esc/焦点恢复和错误防重入可验证；静态HTML不能作为真实行为通过证据。

#### Scenario: 交付卡顶部信息顺序

- **WHEN** 展示交付卡
- **THEN** 来源编号及Sprint在顶部，中文交付标题下方展示完整Change ID
- **AND** 人力估算与优先级、负责人共用标签行，缺少估算显示“人力待估算”，窄屏不足时自然换行
