## 测试范围

| 范围 | 命令 | 期望 |
|---|---|---|
| 目录结构 | `python scripts/validate-directory-structure.py` | 根目录 `.vite/` 存在时仍通过，未知根目录仍保持阻断。 |
| 脚本语法 | `python -m py_compile scripts/validate-directory-structure.py` | 校验脚本语法通过。 |
| 上下文预算 | `python scripts/validate-agent-context-budget.py` | 命令技能和治理文档契约通过。 |
| 当前 Change 中文校验 | `python scripts/validate-openspec-language.py --change ignore-local-vite-cache-directory --residual-report` | 当前 Change 不残留英文脚手架标题；非当前残留只作分离报告。 |
| OpenSpec 结构 | `openspec validate ignore-local-vite-cache-directory --strict` | 目标 Change 结构与 delta spec 通过。 |
| Sprint 范围 | `python scripts/validate-sprint-scope.py sprint-006 --item ignore-local-vite-cache-directory` | Change 出现在 Sprint scope 与派生文档中。 |

## 业务测试

不适用。本变更不修改 `src/` 业务代码、API、DB、Web、管理端、客户端生成、Orval 或 Docker Compose。
