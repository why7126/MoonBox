# deployment-governance Specification

## Purpose
TBD - created by archiving change apply-projecttilesfst-governance-refinements. Update Purpose after archive.
## Requirements
### Requirement: 部署矩阵 env 回退与安全输出

MoonBox deploy 脚本 MUST 支持本地演示和配置校验场景下从真实 env 回退到同名 `.env.example`，但真实部署前 MUST 使用真实 env 并替换占位值。部署脚本和 env 校验脚本 MUST NOT 输出密钥值、数据库连接串、Authorization header、Cookie 或真实 `.env` 原文。

#### Scenario: Docker Web 默认使用同源 API 反向代理

- **WHEN** 使用 Docker Compose 启动 Web 静态服务
- **THEN** Web nginx MUST 将 `/api/` 请求反向代理到后端 API 服务
- **AND** Docker 默认管理后台登录 MUST NOT 依赖运行期 `VITE_API_BASE_URL` 才能命中后端
- **AND** `VITE_API_BASE_URL` SHOULD 仅作为本地 Vite dev 或前后端分域部署的可选配置

#### Scenario: Docker Web 前端路由支持 SPA fallback

- **WHEN** 用户直接访问或刷新 `/admin`
- **THEN** Web nginx MUST 返回 SPA 入口文件
- **AND** 前端路由 MUST 展示管理后台登录页或已登录管理后台页面
- **AND** nginx MUST NOT 将 `/admin` 当作静态文件路径返回 404

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

### Requirement: 本地数据目录治理

MoonBox 本地部署 MUST 明确区分本地持久数据目录与运行时控制状态目录。SQLite、对象存储、Chat Platform runtime、Governance runtime 和临时文件处理目录的宿主机归属 MUST 在部署文档中可追溯，迁移期间不得静默切换真实数据路径。

#### Scenario: SQLite 与对象存储拥有 canonical 宿主机目录

- **WHEN** 使用本地 SQLite 与自建 MinIO/S3 兼容对象存储
- **THEN** 本地 SQLite canonical 宿主机目录 MUST 为 `data/sqlite/`
- **AND** 自建 MinIO/S3 对象数据 canonical 宿主机目录 MUST 为 `data/s3/`
- **AND** 生产 MySQL 或外部对象存储模式 MUST NOT 依赖本地 SQLite 或本地 MinIO 数据目录作为生产事实源

#### Scenario: Chat 与治理 runtime 不承载业务持久数据库

- **WHEN** 启用 Chat Platform、Governance Controller 或 Codex 执行器
- **THEN** `data/runtime/chat-platform/` MAY 承载 Chat 状态、备份、工作区和 Codex 执行器 runtime
- **AND** `data/runtime/governance/` MAY 承载治理控制器私有状态
- **AND** `data/runtime/` MUST NOT 被描述为本地 SQLite 或对象存储数据的 canonical 目录

#### Scenario: 迁移 legacy runtime backend 存储前置检查

- **GIVEN** 旧部署曾将容器 `/app/data` 挂载到 `data/runtime/backend/`
- **WHEN** 准备将实际 SQLite 或媒体文件迁回 canonical 目录
- **THEN** 实施方 MUST 先停止相关服务
- **AND** MUST 备份源库和目标库
- **AND** MUST 执行 SQLite 完整性检查与关键表行数对比
- **AND** MUST 在验证 Chat 会话、媒体上传和治理控制器可用后再清理 legacy 目录

