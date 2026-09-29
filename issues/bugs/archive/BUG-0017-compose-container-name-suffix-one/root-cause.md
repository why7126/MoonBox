# 根因分析

## 根因状态

status: confirmed

## 现象

- 用户反馈 Docker/Compose 启动后的部分容器名带 `-1` 后缀。
- 期望容器名保持项目约定的稳定名称，不出现 Compose 默认序号后缀。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | config_diff | `docker-compose.yml:37-44`、`docker-compose.yml:102-109` | 主编排中的 `backend`、`web` 显式配置 `container_name`，运行态名称为 `moonbox-backend`、`moonbox-web`，不带 `-1`。 | 显式 `container_name` 可避免这些主服务落回 Compose 默认序号命名。 |
| E2 | config_diff | `deploy/docker-compose.chat-platform.yml:19-57` | `chat-worker` 服务定义没有 `container_name` 字段。合并配置摘要显示 `chat-worker: container_name=<missing>`。 | `chat-worker` 会使用 Compose 自动生成的项目名-服务名-序号命名。 |
| E3 | config_diff | `deploy/docker-compose.governance.yml:21-56` | `governance-controller` 服务定义没有 `container_name` 字段。合并配置摘要显示 `governance-controller: container_name=<missing>`。 | `governance-controller` 会使用 Compose 自动生成的项目名-服务名-序号命名。 |
| E4 | reproduction | `docker compose ps --format json` 运行态摘要 | 当前运行容器中，`backend`/`web`/`minio` 名称分别为 `moonbox-backend`、`moonbox-web`、`moonbox-minio`；`chat-worker` 与 `governance-controller` 名称分别为 `moonbox-chat-worker-1`、`moonbox-governance-controller-1`。 | 运行态证明 `-1` 后缀集中出现在缺少显式 `container_name` 的叠加服务。 |
| E5 | config_diff | `deploy/local/compose.chat-recovery.yml:3-22` | `chat-recovery` 服务定义没有 `container_name` 字段；运行态名称为 `moonbox-chat-recovery-1`。 | 独立恢复 worker 同样符合“缺少显式容器名 → 默认序号后缀”的模式。 |

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 主 `docker-compose.yml` 的全部服务都缺少容器名。 | E1 显示主服务已配置 `container_name`，运行态也不带 `-1`。 |
| `-1` 后缀由镜像名、端口映射或健康检查导致。 | E2-E5 显示差异集中在服务是否声明 `container_name`；主服务同样有镜像、端口和健康检查，但不带 `-1`。 |
| 这是所有 Docker 服务统一表现。 | E4 显示同一项目运行态中既有不带后缀的主服务，也有带后缀的叠加服务。 |

## 已确认根因

`deploy/docker-compose.chat-platform.yml`、`deploy/docker-compose.governance.yml` 与 `deploy/local/compose.chat-recovery.yml` 中的新增/叠加服务未声明 `container_name`。在 Compose 项目名为 `moonbox` 的运行环境中，这些服务落回 Docker Compose 默认容器命名规则，生成 `moonbox-<service>-1` 形式的名称；而主 `docker-compose.yml` 中已显式声明 `container_name` 的服务保持为 `moonbox-backend`、`moonbox-web`、`moonbox-minio` 等稳定名称。

## 修复方向

- 为 `chat-worker`、`governance-controller`、`chat-recovery` 等用户可见或脚本会引用的服务补齐显式 `container_name`。
- 容器名应允许通过环境变量覆盖，并提供稳定默认值，例如 `moonbox-chat-worker`、`moonbox-governance-controller`、`moonbox-chat-recovery`。
- 修复前需评估这些服务是否需要多副本扩展；显式 `container_name` 会限制同一 Compose 项目内同服务多副本。
- 同步更新部署文档、脚本验证和相关测试，避免后续新增服务再次遗漏容器名约定。

## 验证闭环

1. 运行 Compose 配置解析，确认目标服务均出现预期 `container_name`。
2. 启动涉及的部署模式，运行 `docker compose ps`，确认目标容器名不再出现 `-1` 后缀。
3. 运行现有 Docker 部署脚本测试或新增测试，覆盖 chat-platform、governance-controller 与 chat-recovery 的容器命名约定。
4. 确认主服务、网络、卷、健康检查和脚本引用不因容器名变化产生回归。
