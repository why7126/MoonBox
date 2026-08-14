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

