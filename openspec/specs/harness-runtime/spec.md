# harness-runtime Specification

## Purpose
TBD - created by archiving change add-opsx-modify-ui-screenshot-comparison-gate. Update Purpose after archive.
## Requirements
### Requirement: UI 返修附件截图逐项视觉对照

系统 MUST 在 UI 型 `/opsx-modify` 返修前，对验收反馈中的附件截图、标注截图、原型截图或实际截图建立逐项视觉对照表，并以该表作为进入实现返修的前置检查。

#### Scenario: UI 返修前建立逐项视觉对照表

- **WHEN** `/opsx-modify` 的验收反馈涉及 UI 视觉偏差、prototype、截图附件、标注图或关键交互状态
- **THEN** Agent MUST 先识别当前反馈中的附件截图、原型截图、实际截图和历史视觉证据
- **AND** Agent MUST 建立逐项视觉对照表，记录附件/截图编号、页面/状态、对照对象、期望表现、实际表现、偏差项、检查方式、处置结论和证据入口
- **AND** Agent MUST 在完成对照前不得开始修改业务实现

#### Scenario: 附件证据不足时阻断 UI 返修

- **WHEN** 附件截图缺少页面路由、视口、主题、关键交互状态、期望截图或实际截图，导致无法确认偏差
- **THEN** Agent MUST 输出人工补证步骤
- **AND** Agent MUST 标明需要返回的字段、脱敏要求和可接受证据格式
- **AND** Agent MUST NOT 将偏差根因标记为 confirmed

#### Scenario: UI 返修后复验对照结果

- **WHEN** Agent 完成 UI 返修
- **THEN** Agent MUST 将相关旧截图标记为 stale
- **AND** Agent MUST 重新执行 1440px 或受影响视口的视觉验收
- **AND** Agent MUST 在 Change `trace.md`、`tasks.md` 验收返修记录或等价验收证据中记录对照表复验结果

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

