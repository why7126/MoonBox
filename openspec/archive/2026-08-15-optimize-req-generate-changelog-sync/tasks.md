## 1. OpenSpec 与 Sprint

- [x] 1.1 创建 active OpenSpec Change `optimize-req-generate-changelog-sync`。
- [x] 1.2 将 Change 纳入 `sprint-003` scope。
- [x] 1.3 补齐 proposal、design、delta spec、trace 和 acceptance。

## 2. Workflow Sync

- [x] 2.1 新增 Issue 当前态看板行生成与替换函数。
- [x] 2.2 在 `req.generate` 聚焦事件中刷新 `issues/requirements/CHANGELOG.md` 对应 REQ 行。
- [x] 2.3 保持刷新为单行派生，不全量重写看板。

## 3. 规则与 Skill

- [x] 3.1 更新 `.agents/skills/req-generate/SKILL.md`。
- [x] 3.2 更新 `rules/requirement-management.md`。

## 4. 验证与日志

- [x] 4.1 运行 `req.generate` dry-run 验证 CHANGELOG 派生覆盖。
- [x] 4.2 运行上下文预算、OpenSpec 语言、目录结构、OpenSpec validate、Sprint scope、Workflow Sync 和 AI Usage。
- [x] 4.3 写入治理日志并更新 `docs/spec-logs/CHANGELOG.md`。
