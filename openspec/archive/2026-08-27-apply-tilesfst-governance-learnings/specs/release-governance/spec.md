## ADDED Requirements

### Requirement: 产品版本升级与回滚计划

MoonBox MUST 为产品版本发布提供可校验的部署升级与回滚计划，覆盖首次部署、相邻升级和跨版本人工复核。升级计划 MUST 基于 release 事实源、env 示例摘要、数据库影响、对象存储影响和回滚证据生成，不得自动执行生产升级或修改真实环境。

#### Scenario: 生成升级计划

- **WHEN** 用户执行 `/upgrade-plan --from <fresh|version> --to <version>`
- **THEN** 系统 MUST 读取目标版本 release 事实源和公开安全的 env 示例摘要
- **AND** 系统 MUST 生成 `releases/<version>/upgrade-plans/<from>-to-<version>.json`
- **AND** 计划 MUST 记录 from version、to version、support level、source confidence、env review、database review、object storage review 和 rollback review
- **AND** 系统 MUST NOT 自动执行生产升级、真实 env 修改、数据库 restore 或对象存储写入维护任务

#### Scenario: 校验升级计划

- **WHEN** 用户执行 `/upgrade-validate --plan <path>`
- **THEN** 系统 MUST 校验计划结构、支持级别、blocker、warning 和敏感信息边界
- **AND** 跨版本升级若缺少中间版本事实、env diff、DB drift/smoke、对象存储影响或回滚证据，MUST 保留人工复核提示
- **AND** 系统 MUST NOT 将缺证据的跨版本升级宣称为 fully supported
