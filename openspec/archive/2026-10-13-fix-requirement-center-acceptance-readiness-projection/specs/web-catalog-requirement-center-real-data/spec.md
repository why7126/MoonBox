---
title: 需求中心验收事实与授权文档聚合规格增量
created_at: 2026-10-09 23:00:00
updated_at: 2026-10-09 23:00:00
---

# 需求中心验收事实与授权文档聚合规格增量

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
- **AND** 对象计数仅覆盖 registry 注册项，不自动纳入未注册基础建设目录

#### Scenario: 验收文档与卡片展示分离

- **WHEN** applied Change 的卡片展示 Issue、Change 和关联 Sprint 的已生成文档入口
- **THEN** 系统将对象映射验收中，使用真实 Issue 文档检查 acceptance.md 存在性与非空内容
- **AND** 卡片必须持续提供可读取的 acceptance.md 入口；文件缺失、冲突或无权时给出脱敏不可用说明，不借用其他对象的同名文件

### Requirement: 治理对象列表

系统 SHALL 为需求中心返回能支撑卡片文档查看、动作流转、AI 聊天反馈和任务进度展示的治理对象字段。

#### Scenario: 治理对象包含文档入口

- **WHEN** 后端返回 Requirement 或 Bug 卡片数据
- **THEN** 每个关联文档必须包含文件名、文档类型、打开方式、可访问 URL 或禁用原因
- **AND** 前端卡片必须从文件生成阶段起持续展示当前用户可读取的入口，并标明 Issue、Change 或 Sprint 来源；采集池阶段不得隐藏已生成且可读的其他文件
- **AND** Issue 组按对象类型展示主文档和 Issue trace，不混入 Sprint 文档；Change 组直接使用 `trace.md` 文件名；Sprint 组独立展示实际存在的 `sprint.md`、`release-note.md`、`acceptance-report.md`，纯 Change 卡片没有 Issue 组
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

### Requirement: 已生成治理文档持续可达

系统 SHALL 在授权项目内按 Issue、关联 Change 与 Sprint 来源聚合真实存在的治理 Markdown 文件，并在生成后的所有阶段保持可读入口。

#### Scenario: 多来源同名文档

- **WHEN** Issue、Change 或 Sprint 同时存在同名 trace.md 等文档
- **THEN** 系统 SHALL 为每个来源返回独立身份、受控读取路径与可读能力，不能用一个文件覆盖另一个
- **AND** Sprint 文档必须以关联 Sprint 的真实成员关系解析，始终只读，不因扩展展示而放宽对象授权

#### Scenario: 归档与权限边界

- **WHEN** 对象归档、文档移走、身份冲突或用户缺少读取权限
- **THEN** 已授权且仍存在的文档保持只读可达，其他入口返回安全的不可用说明，不泄露其他对象正文
- **AND** 文档展示范围扩大不得改变人工编辑、任务勾选或跨项目授权规则
