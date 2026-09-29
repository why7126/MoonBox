---
title: 需求中心阶段标题来源规格
created_at: '2026-09-15 23:04:19'
updated_at: '2026-09-15 23:04:19'
---

# 需求中心阶段标题来源规格

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
- **AND** 卡片 ID 保持当前对象身份，中文标题按阶段来源契约选择，关联文档和进度指向受控当前 Change；无分级的独立对象不得伪造默认优先级

## ADDED Requirements

### Requirement: 阶段业务标题来源
系统 SHALL 按阶段选择显示标题，保留对象身份与来源信息，不读取 design 或 trace 作为 Change 业务标题。

#### Scenario: 采集及规划阶段
- **WHEN** 对象在采集池或规划至迭代规划阶段
- **THEN** 采集池使用注册表 title，规划中、待评审、已评审、迭代规划使用 requirement.md 或 bug.md 中文业务标题
- **AND** 主文档不可用时回退注册表，再回退对象 ID，并提示缺失

#### Scenario: 开发及交付阶段
- **WHEN** 对象在待开发、研发中、验收中或已完成
- **THEN** 唯一关联 Change 的 proposal 中文业务标题优先，已完成读取唯一有效归档版本
- **AND** 零个、多个、版本含糊或 proposal 标题不可用时依次回退主文档、注册表、对象 ID

#### Scenario: 标题有效性及独立对象
- **WHEN** 读取业务文档标题
- **THEN** 优先有效中文 Frontmatter title，历史缺字段可读取有效中文一级标题；空白、纯ID、纯英文、纯文档类别不作为业务标题
- **AND** 独立 Change 仅用 proposal 标题或 Change ID；Issue 详情保留 Issue 标题，点击不改变对象身份
