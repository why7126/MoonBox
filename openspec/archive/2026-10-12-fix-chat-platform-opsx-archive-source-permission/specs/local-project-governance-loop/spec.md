---
title: Chat 平台 source 工作区归档权限与状态诊断修复
created_at: '2026-10-04 11:17:53'
updated_at: 2026-10-10 07:21:24
---

# Chat 平台 source 工作区归档权限与状态诊断修复

## ADDED Requirements

### Requirement: 执行前准备失败明确终结

系统 SHALL 将未调用执行器的工作区准备失败记录为 failed，保留具体安全错误码、阶段事件与结构化日志，释放会话占用，保留未应用文件。不得将启动前失败作为持续等待的 unknown 展示。

#### Scenario: 上轮隔离成果尚未应用

- **WHEN** 新命令准备发现工作区存在不能安全覆盖的成果
- **THEN** 系统返回执行前阻断语义并保留成果，不覆盖文件、不声称已应用

#### Scenario: 恢复旧准备阶段未知态

- **WHEN** 旧轮次为 platform_workspace_unavailable 且没有执行器 turn ID，worker 与会话围栏匹配
- **THEN** 系统安全归并 failed，释放占用；真正执行中断或心跳丢失的 unknown 不被归并

#### Scenario: 执行器启动前 setup 失败

- **WHEN** 工作区校验、容器预检、权限 profile 或认证准备在 executor turn 创建前失败
- **THEN** 系统 MUST 将 turn 标记为 failed
- **AND** 系统 MUST 记录脱敏错误码和失败阶段事件
- **AND** 系统 MUST 释放 active turn 与并发预留
- **AND** 系统 MUST NOT 将该失败标记为 unknown

## MODIFIED Requirements

### Requirement: 治理动作可信基准

系统 SHALL 为已接入真实写入链路的治理动作准备原仓库当前治理快照与隔离副本基准，保护未提交内容和既有成果。

#### Scenario: 未提交文档存在

- **WHEN** 目标治理文档有未提交修改
- **THEN** 快照包含其稳定内容并记录摘要，不静默执行旧版本

#### Scenario: 工作区有未处理改动

- **WHEN** 既有会话含未处理成果
- **THEN** 系统要求新建兼容治理会话，不覆盖原副本

#### Scenario: 本地 source 工作区归档

- **WHEN** 本地 Chat 平台使用显式 source 工作区执行 `/opsx-archive <完整 REQ 或 BUG ID>`
- **THEN** worker 对 source root 的宿主挂载 MUST 可写
- **AND** backend 对治理投影和 source root 的读取仍保持只读
- **AND** 执行容器 MUST 使用 archive 专用权限 profile 限定可写路径
- **AND** 普通 governance 写权限 MUST NOT 获得 `openspec/specs` 或 `openspec/archive` 写入能力

#### Scenario: Change 身份校验忽略隐藏系统目录

- **WHEN** `openspec/changes` 或 `openspec/archive` 下存在 `.git`、`.agents`、`.codex`、`.DS_Store` 等隐藏系统目录
- **THEN** Change 身份唯一性校验 MUST 忽略这些隐藏系统目录
- **AND** 校验仍必须检查真实 active Change 与归档 Change 的 ID 格式、重复占用和 `trace.change_id` 一致性

#### Scenario: 跨挂载归档与半归档恢复

- **WHEN** source 对象会话归档 Change，目录位于不同 sandbox 挂载
- **THEN** Agent 优先驱动标准归档脚本，目录迁移使用跨设备安全移动，不使用 Path.rename
- **AND** 移入唯一同身份 archive 后，在用户和对象权限仍有效时继续完成归档写入
- **AND** 跨挂载复制期间，完整且已验证的唯一旧归档源仍存在、标准目标目录已出现但追溯文件尚未复制完成时，同一归档轮次保持归档写权限；目标身份冲突、源失效或命令变化时立即撤销
- **AND** 同一轮次的主对象历史引用在完整唯一旧归档源存在时继续可核对；其他引用对象和冲突目录不得继承过渡授权，未知轮次对账保留原始原因码
- **AND** active 已不存在而唯一 archive 存在时恢复验证与串行 Workflow Sync、Issue promote、用量 hook，不重复合并规格
- **AND** 验证失败或身份重复时保留成果并明确阻塞，不报告归档闭环成功

#### Scenario: 执行沙箱工具目录挂载与全仓残留治理

- **WHEN** Chat 执行沙箱在已配置的写入根目录下生成 `.agents`、`.codex` 精确空工具目录
- **THEN** 目录校验 MUST 根据私有 Chat 命令标记识别执行时空工具目录并给出警告，不将其误判为仓库残留
- **AND** worker MUST 在写入型轮次前后安全清理仓库自有目录的空工具残留；非空目录、文件及符号链接仍 MUST 阻断，第三方依赖与运行数据不自动清理
- **AND** 仓库目录校验 MUST 拒绝除根目录 `.agents` 外的项目自有工具路径
- **AND** 标准归档脚本 MUST 在移动 Change 前校验目录，并在已移动且唯一归档存在时允许串行续跑收尾
