## ADDED Requirements

### Requirement: 部署矩阵 env 回退与安全输出

MoonBox deploy 脚本 MUST 支持本地演示和配置校验场景下从真实 env 回退到同名 `.env.example`，但真实部署前 MUST 使用真实 env 并替换占位值。部署脚本和 env 校验脚本 MUST NOT 输出密钥值、数据库连接串、Authorization header、Cookie 或真实 `.env` 原文。

#### Scenario: 真实 env 缺失时回退示例文件

- **WHEN** `deploy/scripts/up.sh <domain> <environment>` 找不到 `deploy/<domain>/<environment>.env`
- **THEN** 脚本 MAY 使用同名 `.env.example` 进行本地演示或 Compose config 校验
- **AND** 脚本 MUST 明确提示真实部署前需要复制为真实 env 并替换占位值

#### Scenario: 部署输出不得泄露敏感值

- **WHEN** 部署脚本或 env 校验脚本输出执行结果
- **THEN** 输出 MAY 包含环境 ID、服务地址、缺失字段名和占位字段名
- **AND** 输出 MUST NOT 包含密钥值、数据库连接串、Authorization header、Cookie、真实 `.env` 原文或真实客户数据
