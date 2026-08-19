## ADDED Requirements

### Requirement: 目录与临时证据治理

系统 MUST 明确区分正式项目目录、Git 忽略的本地临时目录和可归档的验收证据目录，避免临时视觉证据阻断目录结构校验或误入长期文档。

#### Scenario: 本地视觉证据临时目录被 ignore

- **WHEN** Agent 或开发者在 UI 验收中生成截图、computed style JSON 或视觉对照中间产物
- **THEN** 这些临时产物 MAY 写入被 `.gitignore` 覆盖的 `tmp/visual-evidence/`
- **AND** 根目录 `tmp/` MUST NOT 被视为正式项目顶层目录
- **AND** 目录结构校验 MUST NOT 因被 ignore 的根目录 `tmp/` 存在而失败

#### Scenario: 长期视觉证据必须沉淀到 Change

- **WHEN** 视觉证据需要支撑 Change 验收、Issue 验收或归档闭环
- **THEN** 关键证据 MUST 转存到对应 `openspec/changes/<change-id>/evidence/` 或写入脱敏后的证据摘要
- **AND** `/opsx-archive` MUST NOT 只依赖 `tmp/visual-evidence/` 作为唯一证据入口
- **AND** 证据 MUST NOT 包含真实客户数据、密钥、访问令牌、Cookie、Authorization header、真实 `.env`、未脱敏日志或个人信息
