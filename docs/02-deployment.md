---
purpose: 部署说明
content: MoonBox 本地 docker-compose 部署、端口和环境变量边界
created_at: 2026-07-29 22:55:00
updated_at: 2026-08-08 10:29:47
owner: MoonBox 产品团队
---

# 部署说明

MoonBox 当前启用 docker-compose 部署。根目录 `docker-compose.yml` 保留为本地开发事实源；`deploy/` 目录提供本地六模式矩阵、生产 Compose 入口、env 示例、启动/停止脚本和产品手册站点服务。

后端 Docker 镜像以 `src/backend/pyproject.toml` 作为 Python 依赖事实源构建，新增后端依赖时必须同步更新 `pyproject.toml`，不得在 Dockerfile 中维护与项目依赖漂移的手写安装列表。

本地覆盖 `HOST_PORT_BACKEND` 时，浏览器侧 `VITE_API_BASE_URL` 必须指向相同宿主端口；例如 `HOST_PORT_BACKEND=8001` 时，`VITE_API_BASE_URL` 应为 `http://localhost:8001`。`scripts/docker-up.sh` 启动前会读取环境变量和 `.env`：未显式设置 `VITE_API_BASE_URL` 时自动使用 `http://localhost:${HOST_PORT_BACKEND}`；显式设置但 localhost 端口不一致时直接失败，避免管理后台登录、头像上传等请求出现 `NetworkError`。

`BACKEND_CORS_ORIGINS` 会由后端 FastAPI CORS 中间件读取，必须包含实际访问 Web 管理后台的浏览器 Origin，例如 `http://localhost:18102`；否则后台登录等跨域请求会在浏览器预检阶段失败。

## 本地服务

| 服务 | 容器端口 | 默认主机端口 | 说明 |
|---|---:|---:|---|
| backend | 8000 | 18101 | FastAPI REST API |
| web | 5173 | 18102 | React 开发服务 |
| minio | 9000 | 18103 | 文档与图片对象存储 API |
| minio-console | 9001 | 18104 | MinIO Console |
| mysql | 3306 | 18106 | MySQL 兼容验证服务，默认 profile 不启动 |
| docs-site | 3000 | 18105 | Mintlify 产品手册预览/承载服务，默认 profile 启动 |

## 命令

```bash
cp .env.example .env
bash scripts/docker-up.sh self-storage-sqlite
bash scripts/docker-down.sh
```

部署矩阵入口：

```bash
bash deploy/scripts/up.sh local self-storage-sqlite
bash deploy/scripts/up.sh prod external-storage-external-mysql
bash deploy/scripts/down.sh local
```

## Docker Compose 部署模式

MoonBox 的默认 docker-compose 拓扑由 `backend`、`web`、`minio`、`mysql` 四个服务组成。`backend` 和 `web` 总是由 Compose 启动；对象存储和数据库可选择自建或外部接入。

| 模式 | 对象存储 | 数据库 | 启动命令 | 关键环境变量 |
|---|---|---|---|---|
| `self-storage-sqlite` | 自建 MinIO | SQLite | `bash scripts/docker-up.sh self-storage-sqlite` | `DATABASE_TYPE=sqlite`、`MINIO_ENDPOINT=minio:9000` |
| `external-storage-sqlite` | 外部 S3/MinIO 兼容服务 | SQLite | `bash scripts/docker-up.sh external-storage-sqlite` | `DATABASE_TYPE=sqlite`、`OBJECT_STORAGE_DEPLOYMENT_MODE=external-minio`、`MINIO_ENDPOINT=<external-endpoint>` |
| `self-storage-self-mysql` | 自建 MinIO | 自建 MySQL | `bash scripts/docker-up.sh self-storage-self-mysql` | `DATABASE_TYPE=mysql`、`DATABASE_URL=mysql+pymysql://moonbox:change-me@mysql:3306/moonbox` |
| `self-storage-external-mysql` | 自建 MinIO | 外部 MySQL | `bash scripts/docker-up.sh self-storage-external-mysql` | `DATABASE_TYPE=mysql`、`DATABASE_URL=<external-mysql-url>`、`MINIO_ENDPOINT=minio:9000` |
| `external-storage-self-mysql` | 外部 S3/MinIO 兼容服务 | 自建 MySQL | `bash scripts/docker-up.sh external-storage-self-mysql` | `DATABASE_TYPE=mysql`、`DATABASE_URL=mysql+pymysql://moonbox:change-me@mysql:3306/moonbox`、`MINIO_ENDPOINT=<external-endpoint>` |
| `external-storage-external-mysql` | 外部 S3/MinIO 兼容服务 | 外部 MySQL | `bash scripts/docker-up.sh external-storage-external-mysql` | `DATABASE_TYPE=mysql`、`DATABASE_URL=<external-mysql-url>`、`MINIO_ENDPOINT=<external-endpoint>` |

`deploy/local/compose.yml` 使用同一组模式，但每个模式都有独立 env 示例文件：

| env 示例 | 对象存储 | 数据库 | profile |
|---|---|---|---|
| `deploy/local/self-storage-sqlite.env.example` | 自建 MinIO | SQLite | `self-hosted-storage`、`docs-site` |
| `deploy/local/external-storage-sqlite.env.example` | 外部 S3/MinIO 兼容服务 | SQLite | `docs-site` |
| `deploy/local/self-storage-self-mysql.env.example` | 自建 MinIO | 自建 MySQL | `self-hosted-storage`、`self-hosted-db`、`docs-site` |
| `deploy/local/self-storage-external-mysql.env.example` | 自建 MinIO | 外部 MySQL | `self-hosted-storage`、`docs-site` |
| `deploy/local/external-storage-self-mysql.env.example` | 外部 S3/MinIO 兼容服务 | 自建 MySQL | `self-hosted-db`、`docs-site` |
| `deploy/local/external-storage-external-mysql.env.example` | 外部 S3/MinIO 兼容服务 | 外部 MySQL | `docs-site` |

等价的原生 Compose 命令：

```bash
# 自建对象存储 + SQLite
docker compose up -d --build backend web minio

# 外部对象存储 + SQLite
OBJECT_STORAGE_DEPLOYMENT_MODE=external-minio docker compose up -d --build backend web

# 自建对象存储 + 自建 MySQL
DATABASE_DEPLOYMENT_MODE=self-hosted-mysql DATABASE_TYPE=mysql DATABASE_URL=mysql+pymysql://moonbox:change-me@mysql:3306/moonbox docker compose --profile mysql up -d --build backend web minio mysql

# 自建对象存储 + 外部 MySQL
DATABASE_DEPLOYMENT_MODE=external-mysql DATABASE_TYPE=mysql DATABASE_URL=<external-mysql-url> docker compose up -d --build backend web minio

# 外部对象存储 + 自建 MySQL
OBJECT_STORAGE_DEPLOYMENT_MODE=external-minio DATABASE_DEPLOYMENT_MODE=self-hosted-mysql DATABASE_TYPE=mysql DATABASE_URL=mysql+pymysql://moonbox:change-me@mysql:3306/moonbox docker compose --profile mysql up -d --build backend web mysql

# 外部对象存储 + 外部 MySQL
OBJECT_STORAGE_DEPLOYMENT_MODE=external-minio DATABASE_DEPLOYMENT_MODE=external-mysql DATABASE_TYPE=mysql DATABASE_URL=<external-mysql-url> docker compose up -d --build backend web
```

外部对象存储模式下不得启动 `minio` 服务；必须通过 `.env` 或部署系统提供 `MINIO_ENDPOINT`、`MINIO_ACCESS_KEY`、`MINIO_SECRET_KEY`、`MINIO_BUCKET`。外部 MySQL 模式下不得启动 `mysql` 服务；必须提供 MySQL scheme 的 `DATABASE_URL` 或 `MYSQL_DATABASE_URL`。

## 环境变量说明

根目录 `.env.example` 已按变量逐项添加中文注释。新增或修改 Docker Compose 使用的变量时，必须同步更新 `.env.example` 中对应注释。

| 变量 | 默认值 | 说明 |
|---|---|---|
| `APP_NAME` | `MoonBox` | 应用显示名称 |
| `APP_ENV` | `development` | 应用运行环境；生产环境不得沿用开发默认值 |
| `APP_DEBUG` | `true` | 调试开关；生产环境必须设为 `false` |
| `APP_SECRET_KEY` | `change-me-in-local-env` | 应用签名密钥示例值；生产环境必须替换 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `120` | 管理后台 access token 默认过期分钟数 |
| `JWT_REMEMBER_ME_EXPIRE_DAYS` | `7` | 预留记住登录天数；当前后台登录 MVP 不启用 refresh token |
| `ADMIN_USERNAME` | `admin` | 首次初始化系统内置超级管理员用户名 |
| `ADMIN_INITIAL_PASSWORD` | `change-me-on-first-run` | 首次初始化超级管理员示例密码；生产环境禁止使用空密码、示例密码或弱密码 |
| `HOST_PORT_BACKEND` | `18101` | 后端宿主机端口；MoonBox 本地端口统一使用 `18101-18199` |
| `HOST_PORT_WEB` | `18102` | Web 宿主机端口 |
| `HOST_PORT_MINIO_API` | `18103` | MinIO API 宿主机端口 |
| `HOST_PORT_MINIO_CONSOLE` | `18104` | MinIO Console 宿主机端口 |
| `HOST_PORT_MINTLIFY_DOCS` | `18105` | 产品手册站点宿主机端口 |
| `BACKEND_CORS_ORIGINS` | `http://localhost:18102,http://127.0.0.1:18102` | 后端允许跨域来源 |
| `VITE_API_BASE_URL` | `http://localhost:18101` | 前端访问后端 API 的浏览器侧地址；管理后台登录、退出、头像上传等请求必须使用该地址拼接后端 API；使用 `scripts/docker-up.sh` 时缺省会按 `HOST_PORT_BACKEND` 自动补齐 |
| `DATABASE_TYPE` | `sqlite` | 数据库类型；开发默认 `sqlite`，生产必须显式为 `mysql` |
| `DATABASE_DEPLOYMENT_MODE` | `sqlite` | 数据库部署模式：`sqlite`、`self-hosted-mysql`、`external-mysql` |
| `DATABASE_URL` | `sqlite:////app/data/sqlite/moonbox.db` | 统一数据库连接串；生产必须改为 MySQL |
| `SQLITE_DATABASE_URL` | `sqlite:////app/data/sqlite/moonbox.db` | SQLite 专用连接串，用于开发和测试 |
| `MYSQL_DATABASE_URL` | `mysql+pymysql://moonbox:change-me@mysql:3306/moonbox` | MySQL 示例连接串；不得提交真实凭据 |
| `MYSQL_CHARSET` / `MYSQL_COLLATION` | `utf8mb4` / `utf8mb4_0900_ai_ci` | MySQL 字符集与排序规则 |
| `DATABASE_TIMEZONE` | `+08:00` | 数据库存储时区策略；MoonBox 默认北京时区 |
| `OBJECT_STORAGE_DEPLOYMENT_MODE` | `self-hosted-minio` | 对象存储部署模式：`self-hosted-minio`、`external-minio` |
| `MINIO_ENDPOINT` | `minio:9000` | 容器内访问 MinIO 的服务地址 |
| `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` | `change-me` | MinIO 示例凭据；生产环境必须替换 |
| `MINIO_BUCKET` | `moonbox` | 默认对象存储桶；一个项目一个 Bucket |
| `OBJECT_STORAGE_PREFIX_IMAGES_AVATARS` | `images/avatars/` | 管理后台头像对象前缀 |
| `OBJECT_STORAGE_KEY_PATTERN` | `{resource_type}/{subtype}/{uuid}.{ext}` | 对象 Key 规则；桶内用二级目录/前缀区分资源类型 |
| `OBJECT_STORAGE_PREFIX_*` | 见 `.env.example` | 标准二级对象前缀，例如 `images/original/`、`documents/source/` |
| `DATA_ROOT` | `./data` | 本地数据根目录；自建 MinIO 对象目录默认 `data/s3` |
| `UPLOAD_DIR` / `PROCESSED_DIR` / `TMP_DIR` | `/app/data/...` | 容器内文件处理目录 |
| `MEDIA_ENABLED` | `true` | 是否启用媒体能力 |
| `MAX_UPLOAD_SIZE_MB` | `100` | 单文件上传大小上限 |

## Docker Compose 注释约定

`docker-compose.yml` 已为服务、端口映射、数据卷、健康检查相关配置添加中文注释。维护时遵循：

- 宿主机端口写在映射左侧，可通过 `.env` 覆盖；容器内端口保持稳定。
- `.env` 为本地覆盖文件，Compose 中设置为可选读取，避免初始化校验依赖本地文件。
- 后端运行时数据挂载到 `./data/runtime/backend`，自建 MinIO 对象数据挂载到项目根目录 `./data/s3`，自建 MySQL 数据使用命名卷 `mysql-data`。
- 示例凭据只允许用于本地开发，生产环境必须通过安全配置注入。

## deploy 目录规范

`deploy/` 参考 ProjectTilesFST 的环境矩阵实践，并按 MoonBox 项目变量体系做了适配：

- `deploy/README.md` 是部署矩阵入口，说明环境 ID、Compose/env/script 分工。
- `deploy/local/compose.yml` 面向本地六模式验收，支持 `self-hosted-storage`、`self-hosted-db` 和 `docs-site` profile。
- `deploy/prod/compose.s3-mysql.yml` 面向生产默认模式：外部对象存储 + 外部 MySQL + 产品手册站点。
- `deploy/scripts/validate-env.py` 在启动前校验 env 与 profile 是否匹配，生产环境禁止 SQLite、调试模式和示例密钥。
- `deploy/scripts/up.sh` 和 `deploy/scripts/down.sh` 是推荐的部署矩阵启动/停止入口。
- `deploy/scripts/docs-site-static-server.mjs` 用于在 Docker Compose 中静态承载 `mintlify/` 产品手册源目录。

真实 env 文件必须复制为 `deploy/<domain>/<environment>.env` 并替换占位值；`deploy/**/*.env` 禁止提交。真实 env 文件可在本地存在用于部署验收，归档和发布校验只应阻断未被 Git ignore 覆盖、已 staged/tracked、被复制进公开文档/归档/release 产物，或泄露真实内容的情况。

Web 前端在浏览器侧通过 `VITE_API_BASE_URL` 访问后端。开发环境可使用 Vite `/api` proxy 作为兜底，但 Docker、本地浏览器验收和生产环境必须确保 `VITE_API_BASE_URL` 指向可访问的后端 API origin。`HOST_PORT_BACKEND` 与显式 `VITE_API_BASE_URL` 端口不一致时，`scripts/docker-up.sh` 会在启动前报错；删除 `.env` 中的 `VITE_API_BASE_URL` 可让脚本按后端宿主机端口自动生成。

管理后台正式入口为 `/admin`。Web 服务或反向代理必须对 `/admin` 返回同一个 SPA 入口文件；旧 `#admin-users` 仅作为兼容入口保留，不应作为正式访问地址传播。

## 生产默认模式

当前默认生产入口：

```bash
cp deploy/prod/external-storage-external-mysql.env.example deploy/prod/external-storage-external-mysql.env
bash deploy/scripts/up.sh prod external-storage-external-mysql
```

生产环境必须满足：

- `APP_ENV=production`
- `APP_DEBUG=false`
- `DATABASE_TYPE=mysql`
- `DATABASE_DEPLOYMENT_MODE=external-mysql`
- `OBJECT_STORAGE_DEPLOYMENT_MODE=external-minio`
- `MINIO_SECURE=true`
- `DATABASE_URL`、`MINIO_ACCESS_KEY`、`MINIO_SECRET_KEY`、`APP_SECRET_KEY` 由部署系统或密钥系统注入

生产 Compose 不启动本地 MinIO、MySQL 或 SQLite 挂载；对象存储 Bucket 必须提前创建。

## Mintlify 产品手册站点

`mintlify/` 是公开产品手册源目录。生成、校验和本地预览：

```bash
python scripts/generate-mintlify-docs.py --version latest
python scripts/validate-mintlify-docs.py
bash deploy/scripts/up.sh local self-storage-sqlite
```

`docs-site` 服务只挂载 `mintlify/` 和静态预览脚本，不挂载 `.env`、运行时数据库、对象存储数据或密钥。生产部署时可以由反向代理将该服务挂载到 `/docs` 或独立文档域名。

## MySQL 兼容验证

开发环境默认使用 SQLite。需要验证生产数据库路径时，可启动 MySQL profile：

```bash
docker compose --profile mysql up -d mysql
DATABASE_TYPE=mysql DATABASE_URL=mysql+pymysql://moonbox:change-me@localhost:3306/moonbox PYTHONPATH=src/backend pytest tests/compatibility/database
```

生产环境必须满足：

- `APP_ENV=production`
- `DATABASE_TYPE=mysql`
- `DATABASE_URL` 或 `MYSQL_DATABASE_URL` 使用 MySQL scheme，例如 `mysql+pymysql://...`
- 连接串、账号、密码通过环境变量或密钥系统注入，不写入 Git
- MySQL 配置缺失、连接串非 MySQL 或误用 SQLite 时，后端必须启动失败

## 环境边界

- `.env.example` 只保留开发默认值和变量说明。
- `.env`、`.env.*`、`deploy/**/*.env`、`scripts/build-images.env`、真实密钥、真实客户数据、运行时数据库文件不得提交；若它们被 Git ignore 覆盖，存在本身不影响 OpenSpec 或 Sprint 归档。
- 生产环境必须替换默认密钥、数据库凭据、对象存储凭据和外部 LLM 凭据。
