---
created_at: '2026-09-12 22:41:21'
updated_at: '2026-09-14 00:04:31'
---

## MODIFIED Requirements

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

## ADDED Requirements

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
