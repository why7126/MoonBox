# release-governance Specification

## Purpose
TBD - created by archiving change apply-projecttilesfst-governance-refinements. Update Purpose after archive.
## Requirements
### Requirement: Mintlify 产品手册公开站点投影

MoonBox MUST 将 `mintlify/` 作为公开产品手册站点投影目录，而不是产品、发布或部署事实源。站点投影 MUST 通过 `mintlify/site-manifest.json` 记录版本、latest 指针、共享截图资产、投影来源和人工修正记录，并通过公开安全校验。

#### Scenario: 站点投影校验

- **WHEN** 生成、更新或校验 Mintlify 产品手册
- **THEN** 系统 MUST 校验 Mintlify 主配置、导航页面、`site-manifest.json`、站内链接、共享截图资产和公开安全敏感模式
- **AND** 页面 MUST NOT 包含真实 `.env`、数据库连接串、密钥、Authorization header、Cookie、对象存储凭据、生产私有地址或真实客户数据

#### Scenario: 旧版本内容修正

- **WHEN** 修改已发布版本产品手册的用户可见内容
- **THEN** 系统 MUST 要求明确授权
- **AND** 系统 MUST 在 `site-manifest.json manual_overrides` 或对应 release manifest 中记录原因、确认人、时间、影响文件和摘要
- **AND** 未授权时只允许 broken link、frontmatter、格式、导航引用或敏感信息清理等非语义维护

### Requirement: 产品手册截图资产

MoonBox 产品手册 SHOULD 使用 `mintlify/assets/screenshots/` 下的真实系统截图作为共享公开资产。截图资产 MUST 可公开、可追溯，并在记录 hash 时校验实际文件内容。

#### Scenario: 截图资产引用

- **WHEN** 产品手册页面引用 `/assets/screenshots/<file>`
- **THEN** 文件 MUST 存在于 `mintlify/assets/screenshots/`
- **AND** 如 `site-manifest.json` 记录 `sha256` 或 `content_hash`，校验脚本 MUST 验证文件 hash
- **AND** 系统 MUST NOT 使用原型图、设计稿、未脱敏截图或不可公开运维截图替代真实系统截图

