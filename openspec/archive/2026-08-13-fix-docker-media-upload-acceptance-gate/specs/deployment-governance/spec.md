## MODIFIED Requirements

### Requirement: Docker media-upload 验收入口

MoonBox Docker 本地 media-upload 验收 MUST 使用环境解析得到的宿主机端口，不得硬编码 Docker Web `:3000`。

#### Scenario: 使用实际 Web 宿主机端口验收

- **GIVEN** Docker Compose 暴露 `HOST_PORT_WEB`
- **WHEN** 执行头像、Logo、图片或其他 media-upload 横切验收
- **THEN** 验收脚本或验收说明 MUST 解析实际 Web 宿主机端口
- **AND** 默认值 SHOULD 为 `18102`
- **AND** 验收不得要求 Docker Web 固定运行在 `:3000`

#### Scenario: 端口冲突不得误判上传失败

- **GIVEN** 本机 `:3000` 被其他服务占用
- **WHEN** MoonBox Docker Web 通过 `18102` 或其他 `18101-18199` 范围内端口可访问
- **THEN** media-upload 验收 MUST 使用 MoonBox 实际端口继续验证
- **AND** 不得因为 `:3000` 不可用阻塞 `/opsx-apply`
