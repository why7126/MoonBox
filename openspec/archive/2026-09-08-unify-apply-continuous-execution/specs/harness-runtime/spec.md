---
created_at: 2026-09-08 16:48:48
updated_at: 2026-09-08 16:48:48
---

## ADDED Requirements

### Requirement: Apply 连续执行与完成门禁
Agent MUST 在已授权 Change 范围内连续实现、验证和同步，不得仅因完成一批任务而等待用户继续；完整细则由命令顺序文档集中维护。

#### Scenario: 可修复自检失败
- **WHEN** 当前 apply 的编译、测试或视觉自检失败且可在授权范围内修复
- **THEN** Agent 在当前 apply 内补证、修复并重跑相关检查，不将自检转为用户必须另发的 modify

#### Scenario: 真实外部阻塞
- **WHEN** 必需权限、关键业务决策或人工证据缺失且无法自主解决
- **THEN** Agent 保留门禁并说明证据、已尝试动作与所需输入，在授权范围内继续不依赖阻塞的工作；用户明确停止时立即停止

#### Scenario: 完整交付
- **WHEN** 所有任务已有完成证据
- **THEN** Agent 核实必要验证、文档同步和串行 Workflow Sync 后才宣布完成，非阻断 AI Usage warning 如实披露

#### Scenario: 中断与恢复
- **WHEN** 执行被中断或上下文被压缩后恢复
- **THEN** Agent 根据 Change、任务、实际文件和验证证据核实进度，从首个可执行剩余任务继续，不重复确认已有授权，不把部分完成标记 applied
