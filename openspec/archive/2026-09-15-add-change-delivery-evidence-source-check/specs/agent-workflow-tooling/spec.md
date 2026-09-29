## MODIFIED Requirements

### Requirement: 规范优化命令 spec-opt

`/spec-opt` MUST 作为项目治理规范优化入口，用于新增或修改 `.agents/skills/` 命令、`rules/` 文档、`docs/` 文档规范、`scripts/` 治理脚本、`AGENTS.md` 入口和 active OpenSpec Change 文档。`/spec-opt` 完成本项目规范、技能、脚本、目录边界或校验规则迭代后，MUST 在 `docs/spec-logs/YYYYMMDDhhmmss-governance-xxx.md` 写入治理迭代日志，并 SHOULD 同步更新 `docs/spec-logs/CHANGELOG.md` 的目录级变更历史。`/spec-opt` 不强制纯治理 Change 生成 `acceptance.md` 或 `verification.md`，但当 Change 进入 applied 前，MUST 在 Change 内保留需求中心可识别的交付验证来源，优先使用 `trace.md` 的 `## 验证记录` 或 `## 验证摘要`，或使用 `trace.acceptance_refs` 指向 Change 内 Markdown 证据。新增或修改 applied Change 交付验证来源门禁时，系统 SHOULD 提供可脚本化扫描 active applied Change 的校验入口。

#### Scenario: 校验 applied Change 交付验证来源

- **WHEN** Agent、CI 或归档前流程需要确认 active applied Change 的交付验证来源
- **THEN** 系统 SHOULD 提供脚本校验 active applied Change 是否存在需求中心可识别验证来源
- **AND** 脚本 SHOULD 复用需求中心交付验证来源识别口径
- **AND** 脚本 SHOULD 支持聚焦指定 Change
- **AND** 缺少可识别来源时脚本 MUST 返回非零退出码并列出对应 Change
