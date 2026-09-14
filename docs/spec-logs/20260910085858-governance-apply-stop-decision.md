---
created_at: 2026-09-10 08:58:58
updated_at: 2026-09-10 09:16:21
---

# Apply停止判定与行为验收

## 迭代目标与变更
一次授权持续完成；阶段只汇报；自修后续做；局部依赖不停止独立工作；必要人工等待保留。补充CLI暂停提示解释、停止前决策和脱敏行为验收。

## 影响范围与更新文件
两份apply技能、AGENTS.md、rules/agent-context-budget.md、docs/08-command-execution-order.md、docs/README.md、docs/standards/apply-behavior-acceptance.md、scripts/validate-apply-behavior.py、scripts/validate-agent-context-budget.py及其单元测试；Change enforce-apply-stop-decision纳入sprint-004，估算1人天。

## 验证结果
合成10场景44断言、预算7项测试通过。首次两项夹具失败已自修并复验，无用户继续指令；本次为spec-opt真实自修观察，其余真实apply场景未观察，不将合成通过视为真实行为保证。OpenSpec严格与观测校验通过；最终治理校验与同步见Change验收。

## 产品边界与后续建议
API、DB、Web、客户端、管理端、Orval、Docker Compose不变，无业务测试或迁移需求。后续按行为标准采样实际apply，不保存原始会话；未自动创建额外Issue/Change，不自动归档。

## 归档结果

2026-09-10 09:16:21：已归档至 `openspec/archive/2026-09-10-enforce-apply-stop-decision/`，harness-runtime正式规格新增1项Requirement。目录、环境ignore、归档证据、Workflow Sync通过；无关联Issue需迁移。真实行为覆盖边界保持，不宣称未观察场景通过。
