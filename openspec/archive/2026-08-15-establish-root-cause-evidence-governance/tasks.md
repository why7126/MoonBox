## 1. OpenSpec 与 Sprint 承载

- [x] 1.1 创建 active OpenSpec Change `establish-root-cause-evidence-governance`。
- [x] 1.2 创建 `iterations/change/sprint-003/` 四件套并纳入纯治理 Change。
- [x] 1.3 补齐 proposal、design、delta spec 和 trace/acceptance 记录。

## 2. 规则与标准

- [x] 2.1 新增 `rules/root-cause-evidence.md`，定义根因状态、证据链、人工补证和脚本门禁。
- [x] 2.2 更新 `AGENTS.md`、`rules/bug-management.md`、`rules/testing.md`、`rules/security.md`、`rules/ui-design.md`、`rules/agent-context-budget.md` 引用根因证据规则。
- [x] 2.3 更新 `docs/README.md`、`docs/standards/testing-governance.md`、`docs/standards/prototype-ui-acceptance.md`。

## 3. 技能门禁

- [x] 3.1 更新 `/explore`，证据不足时输出人工补证操作步骤，不确认根因。
- [x] 3.2 更新 `/bug-explore`，围绕复现、影响面、证据缺口和补证步骤探索。
- [x] 3.3 更新 `/bug-complete`，根因证据不足时不得进入 pending_review。
- [x] 3.4 更新 `/opsx-apply`，BUG 来源 Change 实现前校验 root-cause evidence。
- [x] 3.5 更新 `/opsx-modify`，验收返修和效果不符先补偏差证据。

## 4. 脚本与验证

- [x] 4.1 新增 `scripts/validate-root-cause-evidence.py`。
- [x] 4.2 运行脚本自检和目标 Change/active 扫描。
- [x] 4.3 运行上下文预算、OpenSpec 语言、目录结构、OpenSpec validate、Sprint scope 和 Workflow Sync 校验。

## 5. 治理日志

- [x] 5.1 写入 `docs/spec-logs/YYYYMMDDhhmmss-governance-root-cause-evidence.md`。
- [x] 5.2 更新 `docs/spec-logs/CHANGELOG.md`。
