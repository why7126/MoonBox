## 1. Change 与 Sprint

- [x] 1.1 使用 OpenSpec CLI 创建 active Change，并通过 Change 身份唯一性检查。
- [x] 1.2 沿用用户已确认的 `sprint-006`，将纯治理 Change 纳入 Sprint 机器范围。

## 2. 目录治理

- [x] 2.1 更新 `.gitignore`，明确忽略根目录 `.vite/`。
- [x] 2.2 更新 `scripts/validate-directory-structure.py`，允许忽略 `.vite/` 本地缓存目录。
- [x] 2.3 更新 `rules/directory-structure.md`，说明 `.vite/` 的本地缓存边界。

## 3. OpenSpec 与日志

- [x] 3.1 补齐 proposal、design、trace、acceptance、test-plan 和 delta spec。
- [x] 3.2 写入治理迭代日志，并更新 `docs/spec-logs/CHANGELOG.md`。

## 4. 验证

- [x] 4.1 运行目录结构校验。
- [x] 4.2 运行上下文预算校验。
- [x] 4.3 运行当前 Change 聚焦 OpenSpec 中文校验与残留分离报告。
- [x] 4.4 运行目标 Change OpenSpec validate。
- [x] 4.5 运行脚本语法检查、Sprint scope 校验和 Workflow Sync。
