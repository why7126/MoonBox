## 1. Change 准备

- [x] 1.1 使用 OpenSpec CLI 创建 active Change，并通过 Change 身份唯一性检查。
- [x] 1.2 将纯治理 Change 纳入 `sprint-006` 机器范围，避免绕过 Sprint Inclusion Gate。

## 2. 脚本实现

- [x] 2.1 为 `scripts/validate-openspec-language.py` 增加 `--change` 参数，支持重复传入。
- [x] 2.2 保持未传 `--change` 时的全量 active Change 校验行为。
- [x] 2.3 支持 `--change` 与 `--include-archive` 组合校验归档 Change，并对不存在的 Change 输出失败信息。
- [x] 2.4 支持 `--change` 与 `--residual-report` 组合输出非当前 Change 中文残留摘要，且不影响当前 Change 退出码。
- [x] 2.5 更新 `/req-opsx` 收尾契约，生成后自动运行当前 Change 聚焦中文校验与全仓残留分离报告。
- [x] 2.6 为 `scripts/validate-openspec.sh` 增加 `--change` 聚焦入口，串行运行目标 Change 中文优先校验和 `openspec validate`。
- [x] 2.6 更新 `/bug-opsx` 收尾契约，生成后自动运行当前 Change 聚焦中文校验与全仓残留分离报告。

## 3. 规格与文档同步

- [x] 3.1 补齐 proposal、design、trace、acceptance、test-plan 和 delta spec。
- [x] 3.2 同步上下文预算规则、缺陷管理规范、AGENTS 和命令顺序文档的 `/req-opsx` / `/bug-opsx` 聚焦语言校验口径。
- [x] 3.3 写入治理迭代日志，并更新 `docs/spec-logs/CHANGELOG.md`。

## 4. 验证

- [x] 4.1 运行目标 Change 聚焦语言校验。
- [x] 4.2 运行不存在 Change 的失败路径校验。
- [x] 4.3 运行残留分离报告校验。
- [x] 4.4 运行上下文预算、OpenSpec 语言、目录结构、目标 Change、Sprint scope 和 Workflow Sync 校验。
- [x] 4.5 运行 OpenSpec 校验总入口聚焦成功与不存在 Change 失败路径校验。
