## 测试范围

| 范围 | 命令 | 期望 |
|---|---|---|
| 上下文预算契约 | `python scripts/validate-agent-context-budget.py` | `/req-opsx` 与 `/bug-opsx` 保留 OpenSpec CLI 模板标题中文化契约。 |
| 当前 Change 中文校验 | `python scripts/validate-openspec-language.py --change localize-openspec-cli-template-titles --residual-report` | 当前 Change 不残留英文脚手架标题；非当前残留只作分离报告。 |
| 目录结构 | `python scripts/validate-directory-structure.py` | 治理目录结构通过。 |
| OpenSpec 结构 | `openspec validate localize-openspec-cli-template-titles --strict` | 目标 Change 结构与 delta spec 通过。 |
| Sprint 范围 | `python scripts/validate-sprint-scope.py sprint-006 --item localize-openspec-cli-template-titles` | Change 出现在 Sprint scope 与派生文档中。 |

## 业务测试

不适用。本变更不修改 `src/` 业务代码、API、DB、Web、管理端、客户端生成、Orval 或 Docker Compose。
