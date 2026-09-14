---
created_at: '2026-09-12 22:41:21'
updated_at: '2026-09-14 00:04:31'
---

## MODIFIED Requirements

### Requirement: 治理对象列表

系统 SHALL 为需求中心返回能支撑卡片文档查看、动作流转、AI 聊天反馈和任务进度展示的治理对象字段。

#### Scenario: 治理对象包含文档入口

- **WHEN** 后端返回 Requirement 或 Bug 卡片数据
- **THEN** 每个关联文档必须包含文件名、文档类型、打开方式、可访问 URL 或禁用原因
- **AND** 前端卡片必须按当前阶段可展示文档白名单渲染这些入口；采集池阶段只展示 `capture.md` 与 `trace.md`
- **AND** Markdown 文件打开方式必须可映射到右侧抽屉
- **AND** HTML 文件打开方式必须可映射到新 Tab 预览

#### Scenario: 治理对象包含动作映射

- **WHEN** 后端返回 Requirement 或 Bug 卡片数据
- **THEN** 每个对象必须包含当前阶段主动作的产品化文案、命令映射、是否需要选择弹窗、禁用状态和禁用原因
- **AND** 命令映射必须使用完整 REQ 或 BUG ID

#### Scenario: 治理对象包含任务进度

- **WHEN** 对象关联 OpenSpec Change 且存在 `tasks.md`
- **THEN** 系统必须返回任务总数、已完成数量、是否只读、是否可验收和阻塞提示
- **AND** `tasks.md` 缺失或解析失败时必须返回脱敏错误摘要，而不是误报完成

#### Scenario: 返回独立与关联 Change 身份
- **WHEN** 授权项目快照含无 Issue 来源的 Change 或 Issue 已关联 Change
- **THEN** 系统 SHALL 为独立 Change 返回 type=change 的自身身份、只读文档、状态及进度，且不伪造 Issue；阶段动作使用真实能力元数据，依据实际文档和权限给出禁用原因，不按独立Change类型固定禁用，文档仍只读
- **AND** Issue 卡片保留原 id，返回受控关联摘要及可空当前 Change，含糊时不任意选取末项或首项
- **AND** 卡片 ID、中文标题、文档和进度必须指向同一当前 Change；无分级的独立对象不得伪造默认优先级


### Requirement: 真实统计、筛选和搜索

系统 SHALL 基于真实治理对象支持统计、对象类型筛选、负责人筛选、优先级筛选、Sprint 筛选和关键词搜索。

#### Scenario: 统计与筛选一致

- **WHEN** 用户调整筛选条件
- **THEN** 统计区和看板卡片范围基于同一过滤结果刷新

#### Scenario: 搜索覆盖关键字段

- **WHEN** 用户输入 ID、标题、阶段产物、负责人或来源关键词
- **THEN** 看板只展示匹配的治理对象，并保留 9 阶段列

#### Scenario: 独立类型与关联搜索去重
- **WHEN** 用户选择独立 Change 类型或搜索关联 Change ID
- **THEN** 系统 SHALL 只计数独立 Change 卡片，关联 ID 搜索返回所属 Issue 卡片
- **AND** 同筛选下总数等于需求、缺陷、独立卡片数量之和，页面九阶段卡片数量等于页面总数；unknown只计入单列的数据异常数量，接口原始统计不变
- **AND** 未授权对象不参与卡片、搜索提示、统计或异常详情


## ADDED Requirements

### Requirement: 独立 Change 关系与授权解析
系统 SHALL 在完整稳定项目快照中识别结构化关系后再过滤权限，文档直接API与卡片遵循同一授权。

#### Scenario: 关联对象受限或来源缺失
- **WHEN** Change 的关联 Issue 不可见、缺失或来源冲突
- **THEN** 系统 SHALL 不把该 Change 重新认作独立，保留受控异常且不泄漏隐藏身份

#### Scenario: 独立对象授权
- **WHEN** 用户读取独立 Change 或直接请求文档
- **THEN** 系统 SHALL 校验空间、项目、Change完整ID对象权限和路径白名单，拒绝跨项目及符号链接越界，新增入口只读

### Requirement: Change 版本和状态证据
系统 SHALL 精确识别活动与归档完整ID，不以任务完成推断验收或归档。

#### Scenario: 活动与归档冲突
- **WHEN** 活动和归档同ID，或存在多份归档
- **THEN** 系统 SHALL 优先活动并提示冲突，活动缺文档不读旧副本，多份归档禁用含糊入口

#### Scenario: 状态映射与缺失
- **WHEN** 活动trace为proposed/in_progress/applied，或唯一归档，或未知状态
- **THEN** 系统 SHALL 分别映射待开发/研发中/验收中、已完成或默认收起的数据异常诊断入口；未知对象不渲染卡片、不计入页面业务统计
- **AND** 缺tasks显示未知，任务全部勾选不自动改为已完成；Sprint信息不覆盖trace

#### Scenario: 稳定快照失败
- **WHEN** registry解析失败、迁移半写入或项目切换发生
- **THEN** 系统 SHALL 保留受控同步失败状态，不能把全部Change判成独立，不能将旧项目迟到响应覆盖新项目

### Requirement: 独立变更交付验收来源
系统 SHALL 按独立Change交付证据定位验收来源，不套用Issue的固定acceptance.md要求。

#### Scenario: 历史验证记录
- **WHEN** 无显式acceptance_refs且没有acceptance.md或verification.md
- **THEN** 系统 SHALL 接受trace中非空验证记录、验收记录、验证结果或验收结果章节作为证据入口；无来源时提示待核实
- **AND** 证据存在 SHALL 不被解释为自动验收通过

#### Scenario: 显式来源
- **WHEN** trace声明acceptance_refs
- **THEN** 系统 SHALL 校验每个Change内相对Markdown引用，拒绝越界，缺失或空文件明确提示，不回退掩盖错误
