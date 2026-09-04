# release-governance Specification

## Purpose
TBD - created by archiving change apply-projecttilesfst-governance-refinements. Update Purpose after archive.
## Requirements
### Requirement: Mintlify 产品手册公开站点投影

MoonBox MUST 将 `mintlify/` 作为公开产品手册站点投影目录，而不是产品、发布或部署事实源。站点投影 MUST 通过 `mintlify/site-manifest.json` 记录版本、latest 指针、共享截图资产、投影来源和人工修正记录，并通过公开安全校验。发布对象 MUST 记录本版本产品手册是否需要生成或刷新，且不得在未确认时自动创建空产品手册目录。

#### Scenario: 站点投影校验

- **WHEN** 生成、更新或校验 Mintlify 产品手册
- **THEN** 系统 MUST 校验 Mintlify 主配置、导航页面、`site-manifest.json`、站内链接、共享截图资产和公开安全敏感模式
- **AND** 页面 MUST NOT 包含真实 `.env`、数据库连接串、密钥、Authorization header、Cookie、对象存储凭据、生产私有地址或真实客户数据

#### Scenario: 产品手册发布决策

- **WHEN** 执行发布准备或发布确认
- **THEN** 发布对象 MUST 将产品手册决策记录为 `generated`、`skipped` 或 `pending_confirmation`
- **AND** `generated` MUST 记录生成或刷新命令、校验结果、版本或 latest 投影和执行时间
- **AND** `skipped` MUST 记录确认来源、确认时间和跳过原因，且不得创建空产品手册目录
- **AND** `pending_confirmation` MUST 阻断发布准备完成或发布确认

#### Scenario: 旧版本内容修正

- **WHEN** 修改已发布版本产品手册的用户可见内容
- **THEN** 系统 MUST 要求明确授权
- **AND** 系统 MUST 在 `site-manifest.json manual_overrides` 或对应 release manifest 中记录原因、确认人、时间、影响文件和摘要
- **AND** 未授权时只允许 broken link、frontmatter、格式、导航引用或敏感信息清理等非语义维护

#### Scenario: Mintlify 服务部署门禁

- **WHEN** 发布范围涉及 Mintlify 站点、docs-site 服务、`HOST_PORT_MINTLIFY_DOCS`、文档站 Compose 配置或静态预览脚本
- **THEN** 发布门禁 MUST 包含 Mintlify 生成或刷新、公开安全校验和 docs-site Compose config 校验
- **AND** 如生产承载方式未确认，发布准备 MUST 记录 blocker 或待确认项

### Requirement: 产品手册截图资产

MoonBox 产品手册 SHOULD 使用 `mintlify/assets/screenshots/` 下的真实系统截图作为共享公开资产。截图资产 MUST 可公开、可追溯，并在记录 hash 时校验实际文件内容。

#### Scenario: 截图资产引用

- **WHEN** 产品手册页面引用 `/assets/screenshots/<file>`
- **THEN** 文件 MUST 存在于 `mintlify/assets/screenshots/`
- **AND** 如 `site-manifest.json` 记录 `sha256` 或 `content_hash`，校验脚本 MUST 验证文件 hash
- **AND** 系统 MUST NOT 使用原型图、设计稿、未脱敏截图或不可公开运维截图替代真实系统截图

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

