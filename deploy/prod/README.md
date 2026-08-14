---
purpose: 生产部署矩阵
content: MoonBox 生产 Docker Compose 环境、外部依赖、安全边界和产品手册站点
created_at: 2026-08-04 00:00:00
updated_at: 2026-08-04 00:00:00
owner: MoonBox 产品团队
---

# 生产部署矩阵

当前默认生产目标环境为 `prod-external-storage-external-mysql`：

- 数据库：外部 MySQL。
- 对象存储：外部 S3/MinIO 兼容服务，Bucket 由运维提前创建。
- Compose：`deploy/prod/compose.s3-mysql.yml`。
- env 示例：`deploy/prod/external-storage-external-mysql.env.example`。
- 产品手册站点：默认启用 `docs-site` profile 并启动 `moonbox-docs-site`，端口由 `HOST_PORT_MINTLIFY_DOCS` 控制。

生产 Compose 不启动本地 MinIO、MySQL 或 SQLite 挂载。生产环境必须显式替换 `APP_SECRET_KEY`、`DATABASE_URL`、`MINIO_ENDPOINT`、`MINIO_ACCESS_KEY`、`MINIO_SECRET_KEY`、`MINIO_BUCKET` 等占位值。

## 启动

```bash
cp deploy/prod/external-storage-external-mysql.env.example deploy/prod/external-storage-external-mysql.env
# 编辑 deploy/prod/external-storage-external-mysql.env，替换所有生产占位值
bash deploy/scripts/up.sh prod external-storage-external-mysql
```

## 安全边界

- `APP_ENV=production`，`APP_DEBUG=false`。
- `DATABASE_TYPE=mysql`，禁止 SQLite。
- `OBJECT_STORAGE_DEPLOYMENT_MODE=external-minio`，生产不启动本地 MinIO。
- `MINIO_SECURE=true`，生产对象存储默认使用 HTTPS。
- 生产 Bucket 必须提前创建；应用不得依赖本地初始化脚本创建生产 Bucket。
- 产品手册站点只挂载 `mintlify/` 公开源目录，不挂载生产 env、密钥或运行时数据。
- 生产承载可使用 Compose 内 `docs-site`、外部 Mintlify 托管、静态托管、CDN rewrite 或反向代理；采用方案必须在发布门禁中记录。若方案未确认，`/release-prepare <version>` 必须记录 blocker 或待确认项。

## 校验

变更生产 Compose 文档或 env 示例后，至少校验：

```bash
python deploy/scripts/validate-env.py --domain prod --environment external-storage-external-mysql --env-file deploy/prod/external-storage-external-mysql.env
MOONBOX_DEPLOY_ENV_FILE=external-storage-external-mysql.env docker compose --project-name moonbox --env-file deploy/prod/external-storage-external-mysql.env --profile docs-site -f deploy/prod/compose.s3-mysql.yml config --quiet
```

`deploy/prod/external-storage-external-mysql.env.example` 保留 `replace-with-*` 占位值，只用于说明变量结构，不应作为生产通过校验的 env。
