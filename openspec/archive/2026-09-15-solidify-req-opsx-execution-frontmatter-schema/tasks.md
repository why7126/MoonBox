## 1. Change 准备

- [x] 1.1 使用 OpenSpec CLI 创建 active Change，并通过 Change 身份唯一性检查。
- [x] 1.2 将纯治理 Change 纳入 `sprint-006` 机器范围，避免绕过 Sprint Inclusion Gate。

## 2. 命令模板与校验

- [x] 2.1 更新 `/req-opsx` 技能，固化 Change trace `execution.schema_version=1` 初始 frontmatter 模板。
- [x] 2.2 更新上下文预算校验脚本，阻断 `/req-opsx` execution schema v1 模板回退。
- [x] 2.3 同步 `AGENTS.md` 与 `rules/agent-context-budget.md` 的命令入口和上下文预算规则。
- [x] 2.4 修复 Workflow Sync 对 schema v1 初始 `null` 执行时间的写入逻辑，并补充聚焦单元测试。

## 3. 规格与文档同步

- [x] 3.1 补齐 proposal、design、trace、acceptance、test-plan 和 delta spec。
- [x] 3.2 写入治理迭代日志，并更新 `docs/spec-logs/CHANGELOG.md`。

## 4. 验证

- [x] 4.1 运行上下文预算校验。
- [x] 4.2 运行 OpenSpec 中文优先校验。
- [x] 4.3 运行目录结构校验。
- [x] 4.4 运行目标 Change OpenSpec 校验。
- [x] 4.5 运行 Sprint scope 与 Workflow Sync 校验。
