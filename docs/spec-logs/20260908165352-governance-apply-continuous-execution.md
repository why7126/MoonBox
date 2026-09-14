---
purpose: Apply 连续执行治理迭代
created_at: 2026-09-08 16:53:52
updated_at: 2026-09-08 17:35:18
---

# Apply 连续执行治理迭代

## 迭代目标
统一两份 apply 技能，减少批次结束、普通错误和自检返修导致的非必要中断。

## 变更摘要
- 命令顺序文档承载连续推进、硬阻塞与停止、完成门禁、中断续接四项契约；技能、入口和预算规则引用同一事实源。
- 自检修复留在当前 apply，验证后勾选；all_done 不直接推出可归档。保留 Sprint、根因、UI 人工确认与权限边界。
- 中断检查点保存脱敏任务与证据，恢复时核实当前文件；不承诺自动唤醒，不重复请求已有授权。
- 增加静态契约检查与六项脚本回归测试，覆盖两份技能的十类旧文案回退、引用缺失、事实源缺失/空白、显式禁止旧指令与无关技能边界。

## 影响范围与更新文件
- `.agents/skills/opsx-apply/SKILL.md`、`.agents/skills/openspec-apply-change/SKILL.md`
- `AGENTS.md`、`rules/agent-context-budget.md`
- `docs/08-command-execution-order.md`、`docs/README.md`、`docs/spec-logs/CHANGELOG.md`
- `scripts/validate-agent-context-budget.py`、`tests/unit/test_validate_agent_context_budget.py`
- `openspec/archive/2026-09-08-unify-apply-continuous-execution/`、`iterations/change/sprint-004/` 的范围及派生状态

## 验证结果
- `python3 -m unittest discover -s tests/unit -p test_validate_agent_context_budget.py`：6项通过；两份技能各覆盖十条旧文案反例。
- 上下文预算、OpenSpec 中文、目录结构、目标 Change validate：通过。
- 首轮反例暴露通用否定词检查误将句尾 don't guess 当成对前文 Pause 的否定；已改成只判断匹配前缀，并通过复验。
- Sprint scope：通过；Workflow Sync：解析 sprint-004，Errors 0，派生状态 applied（3/3）。AI Usage Hook：warning / unavailable，command_run_count 0，Sprint snapshot 因 no-command-runs 跳过，warning_count 1；需要真实用量时再提供含可归因 token_count 的显式 session 输入。
- 静态检查证明规则已统一和已知文案回退可被发现；尚未观察后续真实开发会话，不能保证消除环境强制中断。

## 产品边界
API、DB、Web、客户端、管理端、Orval、Docker Compose 均无变更，无需生成客户端或执行迁移；不改变 request_logs、usage_events、Task Trace、请求封装、对象存储和运行时观测。仅改变 Agent 开发治理与静态校验，业务测试不适用。工作区原有业务变更未由本次编辑。

## 后续建议
已完成归档；后续以实际 Change 观察暂停原因与续接质量。未自动创建 follow-up Issue/Change。

## 归档结果

2026-09-08 17:35:18：正式规格新增一项 Requirement 与四个场景，清理历史 Purpose 占位文案。归档目录、环境 ignore、归档证据、Workflow Sync 与 Issue promote 均成功；无关联 Issue 迁移。AI Usage 仍为 warning/unavailable，不阻断归档。
