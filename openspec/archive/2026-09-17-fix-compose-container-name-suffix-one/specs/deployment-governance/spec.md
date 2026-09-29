## ADDED Requirements

### Requirement: Compose 服务容器命名稳定性

MoonBox Docker Compose 中用户可见、运维脚本会引用或验收步骤会定位的服务 SHALL 使用稳定容器名，避免回退到 Compose 默认的项目名-服务名-序号命名。显式容器名 SHALL 支持按环境覆盖，并在需要多副本扩展时说明限制或改用服务名、label 等定位方式。

#### Scenario: 叠加服务默认名称稳定

- **GIVEN** 启用 chat-platform、governance 或 chat-recovery Compose 组合
- **WHEN** 解析 Compose 配置
- **THEN** `chat-worker`、`governance-controller` 和 `chat-recovery` SHALL 具有显式 `container_name`
- **AND** 默认容器名 SHALL 不包含 Compose 自动追加的 `-1` 序号后缀

#### Scenario: 容器名可按环境覆盖

- **WHEN** 部署环境提供目标服务的容器名覆盖变量
- **THEN** Compose 配置 SHALL 使用覆盖后的容器名
- **AND** 默认稳定容器名 SHALL 继续作为未配置覆盖变量时的回退值

#### Scenario: 多副本限制明确

- **WHEN** 某服务需要在同一 Compose 项目中运行多副本
- **THEN** 部署说明或 Change 设计 SHALL 明确显式 `container_name` 的单副本限制
- **AND** 实施方 SHALL 选择服务名、label 或其他适配多副本的定位方式，而不是依赖固定容器名扩展副本
