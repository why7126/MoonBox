## 设计目标

每次 workflow 命令结束时，AI 都应该反馈本次链路质量，但不能把成功路径变成长篇复盘。因此 Hook 采用轻量、结构化、可跳过冗余细节的设计。

## 输出契约

命令最终回复在「下一步」和「待用户决策/处理」之前或之后，MUST 包含：

```text
执行链路复盘：
- 链路状态：正常 / warning / blocked
- 问题证据：无 / <命令、脚本、日志或文件证据摘要>
- 规范优化建议：无 / <建议走 /spec-opt、/bug-capture 或文档优化的简述>
```

如果命令失败或出现阻塞，`问题证据` MUST 引用实际脚本输出、文件路径、校验报告、日志摘要或用户提供证据，不得靠猜测归因。

## 状态定义

| 状态 | 含义 |
|---|---|
| `正常` | 命令顺序、门禁、验证和同步均符合预期，未发现明显流程问题 |
| `warning` | 命令完成但暴露非阻断风险、可优化点、历史漂移或后续补证事项 |
| `blocked` | 命令未完成或门禁阻断，需要用户补证、确认、修复事实源或重新执行上游命令 |

## Follow-up 边界

- 默认不得自动创建 follow-up REQ/BUG/Change。
- 治理优化建议应输出 `/spec-opt <简述>`。
- 缺陷建议应输出 `/bug-capture <简述>` 或 `/capture <简述>`。
- 需求建议应输出 `/req-capture <简述>` 或 `/capture <简述>`。
- 只有用户明确授权“自动创建”时，才能进入对应 capture/spec-opt 流程。

## 与现有 Hook 的关系

- Workflow Sync 负责同步事实源。
- AI Usage Hook 负责使用量记录。
- Command Execution Review Hook 负责人类可读的链路质量反馈，不写状态、不改文件、不替代 Sprint 复盘。

## 维护策略

Hook 文案集中写入 `rules/agent-context-budget.md`，由命令技能继承。`scripts/validate-agent-context-budget.py` 只校验中央契约和 `workflow-sync` 技能是否保留 Hook 关键字段，避免每个技能复制模板造成维护噪音。
