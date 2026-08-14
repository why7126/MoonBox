## ADDED Requirements

### Requirement: Docker media-upload 测试身份

MoonBox Docker media-upload 验收 SHALL 使用脚本准备的可控测试身份，不得依赖本地持久库中的默认管理员密码。

#### Scenario: 本地持久库默认密码漂移

- **GIVEN** Docker 后端数据挂载在 `data/runtime/backend`
- **AND** 管理员密码可能已被用户修改或由不同 `ADMIN_INITIAL_PASSWORD` seed
- **WHEN** 执行 Docker media-upload 验收
- **THEN** 验收脚本 MUST NOT 假设 `ADMIN_INITIAL_PASSWORD` 或项目示例密码等于当前管理员密码
- **AND** 验收脚本 MUST 创建或准备一次性测试用户、测试会话或可回收 fixture

#### Scenario: 使用测试身份完成上传链路

- **GIVEN** 验收脚本已准备测试身份
- **WHEN** 执行 media-upload 回归验证
- **THEN** 脚本 MUST 使用该身份完成 `/api/v1/auth/login`
- **AND** 脚本 MUST 使用该身份完成 `POST /api/v1/auth/avatar`
- **AND** 脚本 MUST 验证受保护头像读取和同会话回显
- **AND** 验收输出 MUST NOT 包含真实密码、Authorization header、Cookie 或真实 `.env` 原文
