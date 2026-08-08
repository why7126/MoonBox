---
purpose: 部署环境矩阵入口
content: MoonBox deploy 目录职责、local/prod 环境 ID、Compose/env/script 分工
created_at: 2026-08-04 00:00:00
updated_at: 2026-08-04 00:00:00
owner: MoonBox 产品团队
---

# deploy 部署矩阵

`deploy/` 是 MoonBox 部署环境矩阵、环境化 Compose、env 示例和部署脚本的主目录。根目录 `docker-compose.yml` 保留为本地开发事实源；`deploy/local/compose.yml` 必须跟随它的服务名、端口、profile、卷挂载和关键环境变量。生产环境不继承本地 SQLite 或自建 MinIO 默认值，优先使用 `deploy/prod/` 下的生产 Compose。

## 原则

- 一环境一 env 示例：变量差异通过 `*.env.example` 表达。
- 一域一 Compose：`local` 与 `prod` 分开维护，避免生产误用本地服务。
- 统一脚本入口：启动使用 `bash deploy/scripts/up.sh <domain> <environment>`，停止使用 `bash deploy/scripts/down.sh <domain>`。
- 固定项目名：部署脚本使用 `moonbox` 作为 Compose project name，避免入口目录名影响网络、镜像前缀和容器 label。
- 服务自愈：长期运行服务 SHOULD 使用 `restart: unless-stopped`；一次性初始化任务 SHOULD 使用 `restart: on-failure`，失败重试、成功不循环。
- env 回退：部署脚本找不到真实 `deploy/<domain>/<environment>.env` 时 MAY 回退同名 `.env.example` 进行本地演示或 `docker compose config` 校验，但真实部署前 MUST 复制为真实 env 并替换占位值。
- 输出安全：部署脚本和 env 校验脚本只能输出环境 ID、服务地址、缺失字段或占位字段名，不得打印密钥值、数据库连接串、Authorization header、Cookie 或真实 `.env` 原文。
- 安全优先：只提交 `.env.example`，不得提交真实 `.env`、密钥、数据库连接串、客户数据、运行时数据库、MinIO 数据或镜像包。

## 环境矩阵

| 环境 ID | 域 | 数据库 | 对象存储 | Compose | env 示例 |
|---|---|---|---|---|---|
| `local-self-storage-sqlite` | local | SQLite | 项目自建 MinIO | `deploy/local/compose.yml` + `self-hosted-storage` | `deploy/local/self-storage-sqlite.env.example` |
| `local-external-storage-sqlite` | local | SQLite | 外部 S3/MinIO 兼容服务 | `deploy/local/compose.yml` | `deploy/local/external-storage-sqlite.env.example` |
| `local-self-storage-self-mysql` | local | 自建 MySQL | 项目自建 MinIO | `deploy/local/compose.yml` + `self-hosted-storage` + `self-hosted-db` | `deploy/local/self-storage-self-mysql.env.example` |
| `local-self-storage-external-mysql` | local | 外部 MySQL | 项目自建 MinIO | `deploy/local/compose.yml` + `self-hosted-storage` | `deploy/local/self-storage-external-mysql.env.example` |
| `local-external-storage-self-mysql` | local | 自建 MySQL | 外部 S3/MinIO 兼容服务 | `deploy/local/compose.yml` + `self-hosted-db` | `deploy/local/external-storage-self-mysql.env.example` |
| `local-external-storage-external-mysql` | local | 外部 MySQL | 外部 S3/MinIO 兼容服务 | `deploy/local/compose.yml` | `deploy/local/external-storage-external-mysql.env.example` |
| `prod-external-storage-external-mysql` | prod | 外部 MySQL | 外部 S3/MinIO 兼容服务 | `deploy/prod/compose.s3-mysql.yml` | `deploy/prod/external-storage-external-mysql.env.example` |

## 命令

```bash
# 本地默认：自建对象存储 + SQLite + 产品手册预览
bash deploy/scripts/up.sh local self-storage-sqlite

# 本地：外部对象存储 + 自建 MySQL
bash deploy/scripts/up.sh local external-storage-self-mysql

# 生产：外部对象存储 + 外部 MySQL + 产品手册站点
bash deploy/scripts/up.sh prod external-storage-external-mysql

# 停止对应域
bash deploy/scripts/down.sh local
bash deploy/scripts/down.sh prod
```

脚本会优先读取 `deploy/<domain>/<environment>.env`；若真实 env 不存在，会退回同名 `.env.example` 进行 `docker compose config` 或本地演示。真实部署前必须复制示例文件并替换占位值。

## Compose 入口选择

| 场景 | 推荐入口 |
|---|---|
| 快速本地开发 | `bash scripts/docker-up.sh self-storage-sqlite` |
| 本地六模式矩阵验收 | `bash deploy/scripts/up.sh local <environment>` |
| 本地产品手册预览 | `bash deploy/scripts/up.sh local self-storage-sqlite` 后访问 `http://localhost:${HOST_PORT_MINTLIFY_DOCS:-3001}` |
| 生产 Docker Compose 部署 | `bash deploy/scripts/up.sh prod external-storage-external-mysql` |
| 只做配置校验 | `python deploy/scripts/validate-env.py --domain local --environment self-storage-sqlite --env-file deploy/local/self-storage-sqlite.env.example --profile self-hosted-storage` |
