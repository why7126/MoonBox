---
purpose: Docker 基线说明
content: Compose 服务、脚本与目录约定
source: initialize-project / project.yaml
update_method: 部署架构变更时同步更新
created_at: 2026-06-27 08:44:18
updated_at: 2026-09-18 16:07:12
---

# Docker 基线

本项目采用根目录 `docker-compose.yml` + 各服务 Dockerfile 的 Compose 部署模式。

## 服务

| 服务 | 镜像/构建 | 端口（宿主机默认） |
|------|-----------|-------------------|
| backend | `src/backend/Dockerfile` | 8000 |
| web | `src/web/Dockerfile` + nginx | 3000 |
| minio | `minio/minio` | 9000 / 9001 |
| minio-init | `minio/mc` | — |

## 脚本

```bash
./scripts/docker-up.sh
./scripts/docker-down.sh
```

## 环境变量

见根目录 `.env.example`；运行时复制为 `.env`（禁止提交）。

## 数据卷

```text
data/sqlite
data/s3
data/uploads
data/processed
data/tmp
data/runtime/chat-platform
data/runtime/governance
```

`data/sqlite` 是本地 SQLite canonical 持久数据库目录；`data/s3` 是自建 MinIO/S3 对象数据目录。`data/runtime/chat-platform` 与 `data/runtime/governance` 只承载运行控制状态。历史 `data/runtime/backend/sqlite` 或 `data/runtime/backend/media` 仅作为迁移期 legacy 目录处理，切换或清理前必须停服、备份并完成完整性校验。

## 文档

- `docs/02-deployment.md`
- `docker-compose.yml`

## 说明

按 `rules/directory-structure.md`，不在根目录新增 `docker/` 业务目录；Compose 与 Dockerfile 位置见上表。


Chat常驻单机执行使用根脚本`--chat-platform`，先`--check`再配对启动/停止；需要显式仓库/空间及unlimited或有限策略配置。与可丢弃`--chat-test`互斥，私有数据长期保留，见`docs/02-deployment.md`。
