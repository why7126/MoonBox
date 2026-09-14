---
created_at: 2026-09-10 08:55:00
updated_at: 2026-09-10 08:55:00
---

## ADDED Requirements
### Requirement: Apply停止决策与行为轨迹验收
Agent MUST 在结束apply前判断所有剩余任务的依赖；未完成且仍有可执行任务时持续执行。校验器 MUST 区分合成回归与真实行为证据。
#### Scenario: 测试失败后自行修复
- **WHEN** 范围内测试失败且可自主修复
- **THEN** Agent修复并重验，不结束等待继续
#### Scenario: 用户插话或上下文压缩
- **WHEN** 用户询问进度或运行内发生上下文压缩
- **THEN** Agent承接原目标继续首个可执行任务
#### Scenario: 局部部署依赖缺失
- **WHEN** 部署缺配置但有独立开发任务
- **THEN** Agent询问必要输入并继续独立任务
#### Scenario: 全部任务依赖外部输入
- **WHEN** 无可执行任务且剩余任务均依赖有证据的必要外部输入
- **THEN** Agent报告依赖和恢复动作，允许等待
