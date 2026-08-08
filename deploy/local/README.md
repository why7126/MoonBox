---
purpose: 本地部署矩阵
content: MoonBox 六种本地 docker-compose 部署环境、前置条件和启动方式
created_at: 2026-08-04 00:00:00
updated_at: 2026-08-04 00:00:00
owner: MoonBox 产品团队
---

# 本地部署矩阵

本地域复用 `deploy/local/compose.yml`。该文件以根目录 `docker-compose.yml` 为本地拓扑基线，保持 `backend`、`web`、`minio`、`mysql`、默认端口和 `data/` 卷一致。只有 `self-storage-*` 环境会启用项目自建 MinIO；只有 `*-self-mysql` 环境会启用项目自建 MySQL。

| 环境 ID | 数据库 | 对象存储 | profile | env 示例 |
|---|---|---|---|---|
| `self-storage-sqlite` | SQLite | 项目自建 MinIO | `self-hosted-storage` | `deploy/local/self-storage-sqlite.env.example` |
| `external-storage-sqlite` | SQLite | 外部 S3/MinIO 兼容服务 | 无 | `deploy/local/external-storage-sqlite.env.example` |
| `self-storage-self-mysql` | 自建 MySQL | 项目自建 MinIO | `self-hosted-storage`、`self-hosted-db` | `deploy/local/self-storage-self-mysql.env.example` |
| `self-storage-external-mysql` | 外部 MySQL | 项目自建 MinIO | `self-hosted-storage` | `deploy/local/self-storage-external-mysql.env.example` |
| `external-storage-self-mysql` | 自建 MySQL | 外部 S3/MinIO 兼容服务 | `self-hosted-db` | `deploy/local/external-storage-self-mysql.env.example` |
| `external-storage-external-mysql` | 外部 MySQL | 外部 S3/MinIO 兼容服务 | 无 | `deploy/local/external-storage-external-mysql.env.example` |

所有 local 启动环境默认同时启用 `docs-site` profile，并启动 MoonBox 产品手册预览。文档站默认访问 `http://localhost:18105`，可通过 `HOST_PORT_MINTLIFY_DOCS` 覆盖。

真实本地 env 可复制到 `deploy/local/<environment>.env`。真实 env 文件已被 `.gitignore` 阻断，禁止提交。

## 校验

变更本地 Compose 文档或 env 示例后，至少校验：

```bash
docker compose config --quiet
MOONBOX_DEPLOY_ENV_FILE=deploy/local/self-storage-sqlite.env.example docker compose --env-file deploy/local/self-storage-sqlite.env.example --profile self-hosted-storage --profile docs-site -f deploy/local/compose.yml config --quiet
python deploy/scripts/validate-env.py --domain local --environment self-storage-sqlite --env-file deploy/local/self-storage-sqlite.env.example --profile self-hosted-storage
```

