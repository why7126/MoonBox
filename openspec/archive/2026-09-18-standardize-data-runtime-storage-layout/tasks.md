## 1. Change 与 Sprint

- [x] 1.1 使用 OpenSpec CLI 创建 active Change，并通过 Change 身份唯一性检查。
- [x] 1.2 按用户确认将纯治理 Change 纳入 `sprint-007`。

## 2. 目录治理

- [x] 2.1 更新 `rules/directory-structure.md`，明确 `data/sqlite`、`data/s3`、`data/runtime` 的唯一职责。
- [x] 2.2 更新 `scripts/validate-directory-structure.py`，对 legacy runtime backend 存储目录输出 warning。
- [x] 2.3 更新部署、数据库和 Docker 基线文档，补齐迁移期说明与迁移注意事项。

## 3. OpenSpec 与日志

- [x] 3.1 补齐 proposal、design、trace、test-plan 和 delta spec。
- [x] 3.2 写入治理迭代日志，并更新 `docs/spec-logs/CHANGELOG.md`。

## 4. 验证

- [x] 4.1 运行目录结构校验。
- [x] 4.2 运行上下文预算校验。
- [x] 4.3 运行当前 Change 聚焦 OpenSpec 中文校验与残留分离报告。
- [x] 4.4 运行目标 Change OpenSpec validate。
- [x] 4.5 运行脚本语法检查、Sprint scope 校验和 Workflow Sync。
