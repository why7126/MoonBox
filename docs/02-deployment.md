---
purpose: 部署说明
content: MoonBox 本地 docker-compose 部署、端口和环境变量边界
created_at: 2026-07-29 22:55:00
updated_at: 2026-09-18 16:07:12
owner: MoonBox 产品团队
---

# 部署说明

MoonBox 当前启用 docker-compose 部署。根目录 `docker-compose.yml` 保留为本地开发事实源；`deploy/` 目录提供本地六模式矩阵、生产 Compose 入口、env 示例、启动/停止脚本和产品手册站点服务。

后端 Docker 镜像以 `src/backend/pyproject.toml` 作为 Python 依赖事实源构建，新增后端依赖时必须同步更新 `pyproject.toml`，不得在 Dockerfile 中维护与项目依赖漂移的手写安装列表。

Docker Web 默认通过 nginx 同源 `/api` 反向代理访问后端，浏览器侧请求不需要配置运行期 `VITE_API_BASE_URL`。`VITE_API_BASE_URL` 仅作为本地 Vite dev 或前后端分域构建的可选配置；静态 Web 镜像构建完成后，容器运行期环境变量不会改写已构建的前端 bundle。

需求中心 BFF 在 Docker 中通过 `MOONBOX_GOVERNANCE_ROOT=/app/governance` 读取治理事实源。根目录本地开发 Compose 允许后端对 `issues/` 中采集池 `capture.md` 做受控写入，写入权限仍由后端限制为“仅采集阶段、仅 `capture.md`”；`iterations/`、`openspec/`、`docs/` 和 `rules/` 继续只读挂载。不得挂载 `.env`、运行时数据库、对象存储数据、日志或密钥目录。

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
| `ADMIN_SPACE_APPLICATION_DEMO_SEED` | `false` | 开发/演示环境可开启，启动时用真实后端申请数据结构生成待审批空间申请；生产环境忽略该演示播种 |
| `HOST_PORT_BACKEND` | `18101` | 后端宿主机端口；MoonBox 本地端口统一使用 `18101-18199` |
| `HOST_PORT_WEB` | `18102` | Web 宿主机端口 |
| `HOST_PORT_MINIO_API` | `18103` | MinIO API 宿主机端口 |
| `HOST_PORT_MINIO_CONSOLE` | `18104` | MinIO Console 宿主机端口 |
| `HOST_PORT_MINTLIFY_DOCS` | `18105` | 产品手册站点宿主机端口 |
| `BACKEND_CORS_ORIGINS` | `http://localhost:18102,http://127.0.0.1:18102` | 后端允许跨域来源 |
| `VITE_API_BASE_URL` | 可选 | 本地 Vite dev 或前后端分域构建时使用的 API 基础地址；Docker Web 默认通过 nginx 同源 `/api` 反代访问后端，运行期不需要配置 |

空间申请演示数据可通过 `python scripts/seed-admin-space-applications.py` 手动生成。脚本会加载本地 `.env`，并把 Docker 容器内 SQLite 路径 `sqlite:////app/data/sqlite/moonbox.db` 映射到宿主机运行库。目录治理目标是 `data/sqlite/moonbox.db` 作为本地 SQLite 唯一持久数据库；历史部署若仍映射到 `data/runtime/backend/sqlite/moonbox.db`，该路径只视为迁移期 legacy 位置，生产环境拒绝执行演示播种。
| `MOONBOX_GOVERNANCE_ROOT` | `/app/governance` | 需求中心 BFF 治理事实源根目录；根目录本地开发 Compose 允许对 `issues/` 中采集池 `capture.md` 受控写入，其他治理目录保持只读 |
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
| `DATA_ROOT` | `./data` | 本地数据根目录；SQLite canonical 目录为 `data/sqlite`，自建 MinIO 对象目录默认 `data/s3` |
| `UPLOAD_DIR` / `PROCESSED_DIR` / `TMP_DIR` | `/app/data/...` | 容器内文件处理目录 |
| `MEDIA_ENABLED` | `true` | 是否启用媒体能力 |
| `MAX_UPLOAD_SIZE_MB` | `100` | 单文件上传大小上限 |

## Docker Compose 注释约定

`docker-compose.yml` 已为服务、端口映射、数据卷、健康检查相关配置添加中文注释。维护时遵循：

- 宿主机端口写在映射左侧，可通过 `.env` 覆盖；容器内端口保持稳定。
- `.env` 为本地覆盖文件，Compose 中设置为可选读取，避免初始化校验依赖本地文件。
- 本地 SQLite canonical 宿主机目录为 `./data/sqlite`，自建 MinIO 对象数据挂载到 `./data/s3`，自建 MySQL 数据使用命名卷 `mysql-data`。历史部署中的 `./data/runtime/backend/sqlite` 与 `./data/runtime/backend/media` 仅作为迁移期 legacy 目录保留；切换 Compose 挂载前必须先完成停服、备份、完整性校验、关键表行数对比和回滚方案。
- 需求中心治理事实源只读挂载到 `/app/governance`，仅用于读取 REQ、BUG、Sprint、OpenSpec 和长期文档状态，不得写回容器内挂载目录。
- 示例凭据只允许用于本地开发，生产环境必须通过安全配置注入。

## Docker Compose 稳定容器名

主编排中的核心服务和常驻 Chat / 治理叠加服务使用稳定容器名，避免运行态回退为 Compose 默认的 `moonbox-<service>-1` 序号名称。默认约定：

| 服务 | 默认容器名 | 覆盖变量 |
|---|---|---|
| `backend` | `moonbox-backend` | 已在主编排中固定 |
| `web` | `moonbox-web` | 已在主编排中固定 |
| `minio` | `moonbox-minio` | 已在主编排中固定 |
| `mysql` | `moonbox-mysql` | 已在主编排中固定 |
| `chat-worker` | `moonbox-chat-worker` | `CHAT_WORKER_CONTAINER_NAME` |
| `governance-controller` | `moonbox-governance-controller` | `GOVERNANCE_CONTROLLER_CONTAINER_NAME` |
| `chat-recovery` | `moonbox-chat-recovery` | `CHAT_RECOVERY_CONTAINER_NAME` |

显式 `container_name` 适用于单副本本地部署和验收定位。若同一 Compose 项目内需要为上述叠加服务运行多副本，不应依赖固定容器名扩展副本，应改用 Compose 服务名、label 或按环境覆盖容器名，并在部署说明中记录选择。

## deploy 目录规范

`deploy/` 参考 ProjectTilesFST 的环境矩阵实践，并按 MoonBox 项目变量体系做了适配：

- `deploy/README.md` 是部署矩阵入口，说明环境 ID、Compose/env/script 分工。
- `deploy/local/compose.yml` 面向本地六模式验收，支持 `self-hosted-storage`、`self-hosted-db` 和 `docs-site` profile。
- `deploy/prod/compose.s3-mysql.yml` 面向生产默认模式：外部对象存储 + 外部 MySQL + 产品手册站点。
- `deploy/scripts/validate-env.py` 在启动前校验 env 与 profile 是否匹配，生产环境禁止 SQLite、调试模式和示例密钥。
- `deploy/scripts/up.sh` 和 `deploy/scripts/down.sh` 是推荐的部署矩阵启动/停止入口。
- `deploy/scripts/docs-site-static-server.mjs` 用于在 Docker Compose 中静态承载 `mintlify/` 产品手册源目录。

真实 env 文件必须复制为 `deploy/<domain>/<environment>.env` 并替换占位值；`deploy/**/*.env` 禁止提交。真实 env 文件可在本地存在用于部署验收，归档和发布校验只应阻断未被 Git ignore 覆盖、已 staged/tracked、被复制进公开文档/归档/release 产物，或泄露真实内容的情况。

Web 前端默认使用相对路径 `/api` 访问后端。Docker Web 服务通过 nginx 将 `/api/` 反向代理到 Compose 网络内的 `backend:8000`，并对 `/admin` 等前端路由使用 SPA fallback 返回 `index.html`。本地 Vite dev 可继续使用 `vite.config.ts` 中的 `/api` proxy；前后端分域构建时才需要在构建期提供 `VITE_API_BASE_URL`。

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

`docs-site` 服务只读挂载 `mintlify/` 和静态预览脚本，不挂载 `.env`、`deploy/**/*.env`、`data/`、运行时数据库、对象存储数据、后端运行时目录或密钥。生产部署时可以由 Compose 内 `docs-site`、外部 Mintlify 托管、静态托管、CDN rewrite 或反向代理承载到 `/docs` 或独立文档域名；采用方案必须在发布门禁中记录，未确认时 `/release-prepare <version>` 必须记录 blocker 或待确认项。发布范围涉及 `docs-site`、`HOST_PORT_MINTLIFY_DOCS`、Mintlify Compose 或静态预览脚本时，必须运行对应 `docker compose ... --profile docs-site ... config --quiet` 并记录结果。

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


## Chat工作台本地验收状态

REQ-0025的/chat页面骨架已通过本地Web镜像构建与18102容器验证。该路由沿用登录跳转，当前执行服务未接通，创建和发送保持禁用。部署页面不代表会话API或Codex worker已经交付；实际状态和截图以openspec/archive/2026-09-13-add-chat-workbench-codex/trace.md及evidence/local-deployment.json为准。此阶段不涉及数据库迁移或正式版本发布。


## Chat恢复worker本地部署

后端已接入Chat增量表与首批API，18102同源Chat接口无认证时返回401，不再是404。执行入口仍返回未就绪。根.env可配置MOONBOX_CHAT_REPOSITORIES，值为只含id、space_id的JSON数组；缺失或非法配置不返回仓库。空白配置禁用新建，不能借此开启模型执行。

SQLite本地恢复进程使用deploy/local/compose.chat-recovery.yml；从仓库根目录执行docker compose -f docker-compose.yml -f deploy/local/compose.chat-recovery.yml up -d --no-deps chat-recovery。仅在默认SQLite本地布局使用，不用于MySQL生产部署。它继承后端镜像，挂载现有SQLite数据，network_mode none、read_only、cap_drop ALL、no-new-privileges、32 PID、128MiB内存、0.5 CPU，无仓库、Docker socket或个人Codex配置挂载。当前与数据文件所有者保持容器默认用户，不能用于执行不可信仓库脚本。

该进程仅做状态恢复，不是模型执行worker；已有真实Codex本机登录不会自动挂载入容器。隔离实测和镜像摘要见openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/backend/verification.json。停止使用相同compose文件执行stop chat-recovery；保留业务数据，不执行down -v或DB restore。


### Chat 会话管理与额度预留增量

本地18102已接通空间、会话列表、搜索、新建、重命名、置顶、归档/恢复及空会话删除。仓库目录仍必须由服务端显式配置，未配置时新建禁用，不从浏览器接受路径。恢复容器继续只执行unknown核对，无模型进程。

`MOONBOX_CHAT_LIMITS`接受JSON对象，八个必填正整数字段：`user_concurrency`、`space_concurrency`、`user_monthly_tokens`、`space_monthly_tokens`、`user_storage_bytes`、`space_storage_bytes`、`turn_reserved_tokens`、`turn_reserved_bytes`。空对象、缺项、布尔值或预留超过总额均不就绪。没有生产默认数值；测试显式给小额度。配置正确本身不会打开发送，仍须接入并验证平台执行worker、权限上下文、结果容量硬停止与清理时限。

增量迁移新增usage_accounts和usage_reservations两表；并发/容量在全局账户计量，Token使用UTC月份账户，终态幂等结算。SQLite与临时MySQL 8.2.0的13例均通过，临时数据库已清理。该版本仅部署本地环境，不等同生产发布。


### 执行适配器开发验收状态

本地后端镜像包含App Server适配、单轮执行器、快照/Diff和10表迁移；chat-recovery服务仍只做租约核对。现有后端/恢复镜像不是配置完毕的模型执行平台，不会自动安装或运行Codex，也不会从个人认证目录复制凭证。实际模型链路已通过受控本机测试，但平台专用认证代理、执行容器的工作区/网络/凭证隔离及正式额度配置尚未部署，因此HTTP新发送门禁保持关闭。

升级前已做SQLite在线备份；只增表/索引，保留原业务数据。恢复镜像与后端同步更新，验证网络none、只读rootfs和cap-drop ALL仅适用于恢复进程。回退不自动删除新增基准表或恢复数据库。

Chat 对象目录通过 MOONBOX_CHAT_REPOSITORY_BINDINGS 显式配置，每项包含 id、space_id、governance_root，前两项必须匹配 MOONBOX_CHAT_REPOSITORIES。governance_root 仅指向该仓库授权的容器内只读治理目录；不得把多空间共享的全量治理目录绑定给无权读取全部对象的空间。Chat Skill 候选读取同一 governance_root 下的 `.agents/skills`，本地 Compose 必须以 `./.agents:/app/governance/.agents:ro` 只读挂载项目 Skill，否则仓库存在 Skill 时页面会误显示空候选。未配置时授权候选为空并显示原因，不影响无引用会话管理。读取逐级使用目录描述符与 NOFOLLOW，拒绝符号链接、硬链接和超1MiB源文件；禁止将平台凭证放入该目录。

Chat Codex 执行写权限分为三档：`read_only` 完全只读；`governance_write` 将 `/work` 整体保持只读，仅允许 `issues/`、`openspec/changes/`、`iterations/`、`docs/spec-logs/` 等受控治理目录写入；`implementation_write` 才允许产品实现工作区写入。早期 REQ/BUG 只要主对象可见且当前用户具备空间拥有者/管理员/编辑者角色，即可获得治理写权限，用于受控写入对应治理文档，不要求主对象已 `in_sprint`。产品实现写入仍在每次真实执行前检查主对象 `in_sprint`、对应活动 Change trace 和 Sprint 双向纳入；不满足时只能治理写或完全只读。运行期间写权限 scope 变化会进入未知并关闭本地执行进程。此策略不能替代平台容器、凭证和网络隔离验收。

MOONBOX_CHAT_RETENTION 需要显式 executor_delete_seconds、backup_expiry_seconds。用户已选择先开发验证、暂不设置正式值；保持空对象。有历史会话删除前，MOONBOX_CHAT_REPOSITORY_BINDINGS 的 workspace_root 必须为预配置绝对容器目录，且 workspace_id 与会话ID一致。不能只按历史Diff计数永久禁删，也不能自动提交代码以通过清理检查。副本和备份实际删除适配尚待配置平台运行环境，pending状态不会按时间自动伪装完成。


### Chat 本地登录真实执行探针

已授权个人登录的开发者可在macOS宿主机、仓库根目录运行以下显式测试（要求codex-cli 0.153.4、后端测试依赖和现有Codex文件登录缓存）：

```bash
CHAT_LIVE_ISOLATED_PROBE=1 PYTHONPATH=src/backend python -m pytest src/backend/tests/test_chat_local_execution.py -q
```

此命令消耗当前登录账号的用量。测试自动建立可丢弃Git仓库、独立SQLite及合成业务身份；认证缓存复制至受保护临时目录，原生工具权限拒绝凭证、其他工作区和DB读取。正常结束自动删除临时认证副本，强制宕机清理及登录刷新尚未验证。不得将该目录挂载到模型工作区。测试内部并发为1，单轮预留40000 tokens、4000000 bytes，用户与空间测试月额度各200000 tokens、容量各20000000 bytes；仅用于本次合成测试，不是正式运营配置。

本探针覆盖内部入队、claim、执行适配、线程恢复、Diff与停止；不启动常驻执行worker，不开放发送/重试API，不代表Docker或浏览器全链路验收。中止缺少用量时保留预留待对账，不以零值结算。安全状态证据见Change的evidence/backend/local-credential-execution.json；脚本临时报告写入系统临时目录。


### Chat 五步回环集成验证（2026-09-08）

测试启动器位于src/backend/tests/chat_isolated_harness.py；仅显式CHAT_LIVE_ISOLATED_PROBE=1启用。在仓库根目录、已安装后端依赖且本地Codex文件登录有效时运行：

```bash
CHAT_LIVE_ISOLATED_PROBE=1 PYTHONPATH=src/backend python src/backend/tests/chat_isolated_harness.py
```

启动器使用HOST_PORT_CHAT_TEST（默认18121，范围18101–18199），仅监听127.0.0.1；同源提供API和src/web/dist构建产物。启动前先构建Web。它创建独立SQLite、两个测试账号、合成治理资料、种子仓库和临时认证目录，不读取真实业务DB、不改正常部署。权限白名单、配置0600/目录0700、测试环境、DB位置、配置一小时有效期和5秒内worker心跳共同控制发送入口；正常部署不满足门禁始终拒绝执行。

将启动输出中的临时root路径保存在本机TEST_ROOT变量，不提交。另一个终端运行node src/web/scripts/chat-live-browser.mjs "$TEST_ROOT" first；第一轮完成后，在启动器终端输入restart，再运行同脚本second、stop。运行restart-active时，临时目录出现restart-ready.json后在启动终端输入restart，脚本核验原轮次停止。inspect采集最终累计Diff及样式。脚本使用真实登录/API/页面，不Mock业务响应。临时测试限制：并发1、用户/空间月额度各400000 tokens、单轮60000 tokens/4000000 bytes、存储各40000000 bytes；不作为正式限额。适配器固定codex-cli 0.153.4，本地探针显式low推理参数用于受控任务。

完成后先运行PYTHONPATH=src/backend python src/backend/tests/chat_isolated_evidence.py "$TEST_ROOT" openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/live-web-execution导出脱敏事实，再在启动终端输入cleanup。检查服务退出、临时根目录删除和监听端口释放；启动器正常退出/异常抛出会清理，宿主机强制断电/SIGKILL残留清理未被本次证明。API、worker、凭证历史和测试DB随本次环境结束，不常驻开放给平台用户。

用量运维入口为python -m app.chat.accounting（需已有后端PYTHONPATH与目标部署DB配置），只列待对账轮次；--turn指定轮次仅根据持久化可信receipt尝试幂等补结算，不接受手填用量。真实用量缺失时继续保留预留；本次测试第四轮明确属于该情况，不能把测试DB清理解释成用量已结算。证据见Change evidence/live-web-execution/verification.json。


### 异常恢复与部署探针（2026-09-09）

使用独立标签构建：`docker build -t moonbox-backend:chat-verification src/backend`；随后从项目根运行 `python src/backend/tests/chat_deployment_probe.py`。探针使用HOST_PORT_CHAT_DEPLOY_TEST（默认18127，仅127.0.0.1，范围18101–18199）、随机测试管理员密码、临时环境文件和独立数据卷；最终清理容器/卷/配置。镜像可由CHAT_TEST_IMAGE覆盖。禁止指向真实业务数据；该脚本不替换当前服务，不运行模型，不挂载本地认证。

执行故障探针：`PYTHONPATH=src/backend python -m pytest src/backend/tests/test_chat_process_guard.py src/backend/tests/test_chat_app_server.py -q`。需要允许本机启动/终止测试子进程。真实线程删除探针使用已有本地凭证显式开启：`CHAT_LIVE_ISOLATED_PROBE=1 PYTHONPATH=src/backend python src/backend/tests/chat_thread_delete_probe.py`，会消耗一次真实模型用量，结束清除临时认证。MySQL矩阵入口为 `PYTHONPATH=src/backend python src/backend/tests/chat_mysql_matrix.py`，需Docker及pymysql，创建并删除独立MySQL 8.2容器，测试端口18126。结果只保留脱敏摘要。

本地worker每30秒尝试执行历史清理，未配置备份适配时保持retry，不以删除时限认定成功。进程组守护可处理worker丢失及同组工具残留，但不是cgroup级逃逸防护，也不解决整机宕机后的认证目录清理。实际备份清单、恢复删除重放与外部删除成功后数据库提交失败的对账仍需接入。未知用量继续保留预算，禁止手填零值释放。


### 推荐组合落地：本地备份＋会话容器（2026-09-09）

用户选择先完成受控方案，正式方向保留为独立对象存储备份＋每会话容器。本批已实现SQLite本地备份与容器worker接入，未连接真实MinIO/S3备份桶、未进行生产恢复。正常部署发送门禁不变。

从项目根构建独立镜像：

```bash
docker build -f src/backend/Dockerfile.chat-executor -t moonbox-chat-executor:0.153.4-test src/backend
```

使用已有Web构建产物启动完整隔离测试环境：

```bash
CHAT_LIVE_ISOLATED_PROBE=1 MOONBOX_CHAT_TEST_EXECUTOR=container PYTHONPATH=src/backend python src/backend/tests/chat_isolated_harness.py
```

启动器创建独立账号、业务库、仓库、认证副本和backups目录；HOST_PORT_CHAT_TEST默认18121。真实登录资料只写本次私有browser.json，不写命令参数或证据。测试内部保留配置为执行副本60秒、备份120秒；这只用于验证状态/时限字段，不会到点伪造清理成功，也不是正式运营承诺。容器测试资源上限为1CPU/1GiB/128进程。控制端保留模型服务联网，模型工具禁网；不挂业务库或Docker socket。seccomp差异、UID映射和内核依赖见src/backend/container/README.md。

启动器自动初始化独立删除日志并生成初始SQLite备份。TEST_ROOT指当前测试根目录，BACKUP_ID取create命令返回的不透明标识；需要验证某一聊天恢复场景时，在创建该聊天之后再建立备份：

```bash
PYTHONPATH=src/backend python -m app.chat.backup --root "$TEST_ROOT/backups" create --source "$TEST_ROOT/chat.db"
PYTHONPATH=src/backend python -m app.chat.backup --root "$TEST_ROOT/backups" restore --backup "$BACKUP_ID" --destination "$TEST_ROOT/restored.sqlite"
PYTHONPATH=src/backend python -m app.chat.backup --root "$TEST_ROOT/backups" expire --backup "$BACKUP_ID"
```

独立部署需预先创建0700备份目录并运行backup模块的init子命令，再create首次备份建立数据库归属，最后配置MOONBOX_CHAT_BACKUP_ROOT；不要对已有日志运行init或删除日志重建。配置了备份库而日志缺失/归属不符时，聊天删除失败关闭。主动删除先持久化不含正文的删除意图，再清理业务事务；事务失败时保留意图以便重试，不自动撤销。

restore只生成新的离线文件，不覆盖在线库或切换服务；恢复时重放最新删除日志，删除聊天消息/引用/事件/Diff，保留审计与代码，并将旧排队/活动轮次置unknown、保留互斥。恢复的额度账本需要可信对账，不能直接开放执行。删除日志必须独立、完整且保持最新，不能与旧业务备份一起回滚；本地同机存储不提供异地容灾。旧备份正文仍存在时cleanup保持pending/retry；显式expire物理删除登记备份后，worker验证库存才标记purged。期限调度、MySQL/S3恢复及生产灾备另行验收。

输入cleanup退出启动器并清理临时服务、凭证、数据库和仓库。真实容器验证入口为chat_container_execution_probe.py；后端claim/Diff/结算验证为显式启用的test_chat_container_worker.py；默认测试不会调用模型。启动器挂接路径已提供，但本批真实证据为容器适配器和后端claim测试；网页真实发送证据仍承接此前原生worker验收。


## 日常脚本与 Chat 受控测试

根目录 `scripts/docker-up.sh`、`scripts/docker-down.sh` 支持六种既有模式，默认 `self-storage-sqlite`。
从其他目录调用也按项目根目录解析 Compose 文件。通过 shell 环境变量 `ENV_FILE` 选择配置文件，up/down 应使用同一文件；相对路径按调用目录解析。指定文件不存在或启动模式与数据库配置冲突时直接失败，不输出连接凭证。配置文件不作为 shell 脚本执行，`MOONBOX_ENV_FILE` 同步选择容器实际读取的 env 文件。

普通重建部署：

```bash
bash scripts/docker-down.sh self-storage-sqlite && bash scripts/docker-up.sh self-storage-sqlite
```

显式增加 Chat 真实执行测试：

```bash
bash scripts/docker-up.sh self-storage-sqlite --chat-test --check
bash scripts/docker-up.sh self-storage-sqlite --chat-test
```

第一条只检查 Compose 配置、本机依赖和端口，不构建或启停服务。第二条构建常规后端/Web与固定执行器镜像，等待常规服务健康，再启动独立 Chat 测试环境。仅支持 `self-storage-sqlite`；其他模式带此选项会在 Docker 操作前拒绝。

前置条件是非 root 宿主用户、本地 Codex 已登录、Git、Linux Docker 引擎，以及 Python 3.12+ 和已安装的后端依赖。`PYTHON_BIN` 是调用脚本时设置的 shell 环境变量，默认 `python`，不从 dotenv 读取。可使用 `PYTHON_BIN=.venv/bin/python bash scripts/docker-up.sh self-storage-sqlite --chat-test` 指定项目虚拟环境，并在停止时使用同一解释器。容器执行器的 seccomp/内核依赖见上述推荐组合说明；预检通过不等于正式平台认证验收通过。

常规页面仍为 18102，Chat 测试页面默认为 `http://localhost:18121/chat`，由 `HOST_PORT_CHAT_TEST` 调整，仅监听回环地址。测试静态页面来自本次构建的 Web 镜像，不依赖宿主旧 dist。脚本输出 URL、有效期及私有 `login_file` 路径；在本机打开该文件读取测试登录资料，不将密码打印到终端。原业务账号不用于此独立测试库。

测试控制器在宿主启动独立 API 和 worker，为每会话选择 Docker 执行器，自动初始化独立 SQLite 备份库与删除日志。账号、种子仓库、业务库、认证副本及备份全部属于一次性测试环境，有效期一小时；不会导入正式业务数据或开启 18102 的正常平台发送。测试资源和时限仅用于验证，正式额度与删除时限仍按用户决定暂缓。

停止全部本环境服务：

```bash
bash scripts/docker-down.sh self-storage-sqlite --chat-test
```

脚本先通过私有 Unix 控制通道停止测试 worker/API 并清理测试数据，再执行 Compose down；不带 `-v`，常规数据库与对象存储数据保留。普通 down 在 Python 可用时也会清理同一配置文件对应的受管 Chat 测试实例。停止 Chat 必须能调用启动时的 Python。重复启动复用健康的同一测试实例，重复停止安全返回；失联控制端保留现场并报错，不按历史 PID 杀进程，不接管被其他程序占用的端口。

启动失败返回非零，已启动的常规服务可能仍在运行，不自动删除业务数据。此入口是根部署脚本的受控验收扩展，`deploy/scripts/up.sh` 的生产部署矩阵不接受 `--chat-test`。平台长期运行、共享认证、MySQL/S3 备份与正式运营参数仍需单独完成上线验收。

2026-09-09 实测：完整 `--chat-test` 构建和启动通过，常规 backend/Web/MinIO 健康；测试真实登录、执行门禁、备份初始化、删除恢复不复活、worker 确认备份清理、代码保留及幂等启停通过。本批未发送模型轮次；真实容器修改与用量结算证据沿用推荐组合批次。测试服务和临时数据已清理，常规服务保留运行。脱敏证据位于 `openspec/archive/2026-09-13-add-chat-workbench-codex/evidence/deployment-scripts/`。


### 终态并发释放补充（2026-09-09）

并发释放修复新增预留表内部字段concurrency_released，后端初始化执行可重复迁移。升级应先备份并确认无活动模型任务，按同版本更新API和执行worker；不通过修改active_runs或Token账本手工解锁。受控测试worker在旧终态对账时释放并发且继续保留未知用量。本批常规本地镜像已重建；旧测试环境到期后已重新创建，登录资料按新login_file获取。回滚不要混跑旧版结算worker；需在维护窗口核对已释放标志与账本，避免旧结算代码重复扣减并发。


### 执行进程计量范围补充（2026-09-09）

计量升级已在本地常规服务和隔离worker部署。每次claim独占新App Server进程，新receipt使用app_server_process_v1范围。旧无scope的待结算记录不自动结算，额度继续保留；旧已结算记录不得用推算金额直接覆盖，需可信原始执行记录另行核实。此前多轮测试材料的旧算法金额不再作为准确计量证明。本次没有启用正式平台认证、正式限额或删除期限。

### Chat 单机常驻部署（2026-09-09）

本次 REQ-0025 已选择单机 Compose、SQLite、本地独立备份和部署用户的 Codex 登录认证单文件。`--chat-platform` 启动常驻 API/Worker，区别于一小时自动清理的 `--chat-test`。正式仓库和空间仍须明确映射，不会自动选择当前项目或测试空间。

在被 Git 忽略的本地 env 配置 `MOONBOX_CHAT_SOURCE_ROOT`（已提交本地 Git 仓库绝对路径）、`MOONBOX_CHAT_REPOSITORY_ID`（不透明标识）和 `MOONBOX_CHAT_SPACE_ID`（已有空间 ID）；私有根目录默认位于 `data/runtime/chat-platform`。该目录只承载 Chat 状态、备份、工作区和 Codex 执行器 runtime，不作为业务 SQLite 或对象存储 canonical 目录。可用 `MOONBOX_CHAT_AUTH_SOURCE` 指定本机认证文件，默认仅使用部署用户的 Codex `auth.json`，不会导入整个认证目录、配置或技能。宿主登录更新且替换了文件 inode 时，需要重建 Worker 容器以重新绑定文件；镜像和仓库不得包含认证。

用户确认不设运营上限，对应 `MOONBOX_CHAT_LIMITS`：

```json
{"user_concurrency":"unlimited","space_concurrency":"unlimited","user_monthly_tokens":"unlimited","space_monthly_tokens":"unlimited","user_storage_bytes":"unlimited","space_storage_bytes":"unlimited","turn_reserved_tokens":"unlimited","turn_reserved_bytes":16777216}
```

`turn_reserved_bytes` 是单轮结果处理缓冲（16 MiB），不限制用户累计存储；协议消息、快照和容器资源仍有技术安全边界。Token 零预留后按可信实际数结算，不用大整数伪装无限。不限制用户/空间入队数；单机 Worker 一次处理一轮，其他轮次持久排队，同会话依旧互斥。上游账号自身的可用额度不受 MoonBox 配置改变。

`MOONBOX_CHAT_RETENTION` 配置为 `{"executor_delete_seconds":"unlimited","backup_expiry_seconds":"unlimited"}`。聊天、引用和 Diff 不自动过期，主动删除清理主数据及执行线程，备份先记录独立删除日志并在恢复时重放。没有固定副本删除截止时间；旧备份保留至运维显式 expire，物理清除前不标记备份已清理。Worker 启动时和运行中每24小时创建一致性备份，不自动轮转备份；保留审计和代码。该本地备份不提供整机损坏后的异机灾备。

完成 env 配置后配对使用：

```bash
bash scripts/docker-up.sh self-storage-sqlite --chat-platform --check
bash scripts/docker-up.sh self-storage-sqlite --chat-platform
bash scripts/docker-down.sh self-storage-sqlite --chat-platform
```

显式模式不覆盖 `.env`；原来的空 `{}` 仍表示尚未配置，必须按上方策略填写。Worker 预检目录、提交基准、备份日志、本机认证、固定执行镜像及真实嵌套沙箱后才发布就绪心跳。停止保留业务DB、工作区和备份；不从排队或未知状态推断旧执行已经完成。

Compose 控制器为非root用户，单独持有 Docker socket 权限；此控制器属于受信任部署边界。API没有 socket 或认证挂载，模型执行容器没有业务DB、socket、其他会话工作区或宿主认证目录。Linux 部署需确保 `MOONBOX_CHAT_DOCKER_GID` 和持久目录权限允许部署用户访问；不得通过给执行容器挂载 socket 来修复。所选源仓库只读挂载，会话从已提交树初始化独立 Git 基线，不导入源仓库 hooks/config/未提交文件。当前模板只支持默认 SQLite 数据位置，已有其他数据库布局须先调整模板并验证。


单机部署续接：已按用户指定项目仓库与唯一编码`moonbox`的现有空间建立映射，该空间显示名为“AI原生软件工厂”，未创建或重命名空间。实际路径和空间ID仅保留在被忽略的私有env。配置`MOONBOX_CHAT_EXECUTION_MODE=local-codex`后，根up/down脚本自动加载常驻覆盖文件，原`bash scripts/docker-up.sh self-storage-sqlite`和配对down命令可继续使用；显式`--chat-test`仍选择测试模式。旧初始密码不代表现有账号密码，前台验收使用用户当前有效登录，不修改或重置账号。


REQ-0025最终当前账号验收：用户重新登录后，在实际moonbox空间及指定仓库完成两轮真实消息，结算14969/15189 Tokens，刷新恢复、无重复轮次、互斥释放及空Diff通过。来源Change evidence/target-deployment；此前“等待登录”检查点已解除，常驻服务保持运行。

## 本地项目治理闭环（REQ-0022，实施中）

`deploy/docker-compose.governance.yml` 是显式加载的本地覆盖文件，位于基础Compose和Chat覆盖文件之后，由常驻Chat启动脚本自动接入。它将API的issues/openspec挂载改为只读，仅独立governance-controller拥有治理写权限；控制器没有Docker socket、模型凭证、源仓库源码写权限。Chat执行控制器仅向独立副本覆盖治理基准。首版覆盖文件复用SQLite部署；MySQL schema兼容验证与该本地模板分开。

新增私有状态目录由 `MOONBOX_GOVERNANCE_HOST_STATE_ROOT` 配置，目录0700，文件0600；容器统一使用 `MOONBOX_GOVERNANCE_STATE_ROOT=/app/governance-state`。API、Chat控制器和治理写入控制器需要共享该私有目录及数据库。执行模型容器不得挂载它。绑定的governance_root必须是当前原仓库治理目录；Chat准备同时比较source_root与governance_root的完整内容摘要。

启用前依次核对：新API/Web协同部署；所有文档保存与tasks勾选已改为入队；API治理挂载只读；只有一个注册的治理写入控制器；停止其他编辑器、Agent和脚本写原仓库。之后由运维在私有目录登记maintenance.json，包含scope_key、binding_revision、registered_writers（唯一governance-controller）、external_writers_paused=true和不超过1小时的expires_at。此文件不能通过公共API创建，客户端勾选不能替代服务端登记。只在真实停止外部写入后登记，不能把登记当成能够检测或阻止任意编辑器的文件系统事务。

任务处理为pending→applying→applied；源版本变化时conflict，已部分写入且检测到未知外部内容时recovery_blocked。读接口遇到应用/恢复阻塞返回503以保留客户端最近完整快照。重启控制器先取得同项目文件锁；取得锁证明先前本机注册控制器不再持有它，再比较前后镜像恢复。不得删除锁文件绕过互斥，也不得按超时强行清除未知操作。

备份需在暂停写入并确认无applying/recovering状态后，成套备份数据库和私有状态目录；SQLite使用既有数据库备份接口，状态目录保留权限与文件摘要，MySQL使用专用数据库备份路径。仅备份DB不能恢复候选正文或前后镜像。恢复先到隔离目录，重验数据库/镜像对应关系，再启动单控制器。未终态或recovery_blocked的文件不得自动清理。当前治理会话清理入口保持阻断，直到受控保留清理能力验收完成。

回退先关闭治理入口，排空或恢复未终态操作，保留新增三表、私有记录与锁文件；不自动drop表、不恢复整个代码仓库。尚未通过真实部署、维护窗口、备份恢复与10次刷新观察验收，本段不是已投产声明。


离线成套备份验证入口为 `app.governance.backup.create/restore`：复用既有LocalBackupStore和独立删除日志，记录对应history_backup_id，并校验数据库与所有允许私有JSON记录的摘要。恢复必须依赖仍有效的原备份及独立删除日志，已物理过期或摘要不一致时拒绝；恢复仅生成新离线目录，不导入旧维护窗口、不启动worker。治理候选关联会话的删除记录同样先于turn外键清理回放；已删除对象的私有记录不从备份重新投影。合成测试覆盖成套恢复、篡改拒绝及既有Chat删除回放回归。

## Capture 写入部署边界（BUG-0014）

新建Capture复用governance-controller，不需要模型worker或模型凭证。API进程对治理源保持只读，controller对issues具有创建目录及替换文件权限；沿用deploy/docker-compose.governance.yml的私有状态目录与单写入器维护窗口。普通Compose仅挂载治理目录不足以启用创建：缺少匹配绑定、可写私有目录或新鲜controller心跳时返回不可用；非continuous模式还要求有效maintenance.json。

实际临时Compose探针已验证同一宿主目录对API只读、controller可写且不挂载Docker socket；测试使用当前overlay模式，没有改动生产服务。浏览器真实验收采用独立SQLite、账号与合成项目，回环18129，无对象存储或生产数据写入。

操作applied前不显示成功。controller意外中止后自动检查前后镜像并续写；文件权限故障或未知外部内容导致recovery_blocked时保持读屏障，先暂停外部写入、成套备份DB/私有状态/治理文件，再由管理员核对操作前后镜像和实际文件。禁止删除锁或盲目改状态重试；确认受控离线恢复后才重新开放。此次未新增自动解除recovery_blocked入口，也未执行生产部署。


## BUG-0014 常驻Capture与目标环境返修

`bash scripts/docker-up.sh --chat-platform`（或已配置local-codex的普通启动）现在自动加载治理overlay，创建默认 `data/runtime/governance` 私有目录，并将 API 与 controller 设为同一宿主 UID/GID，防止私有操作文件跨进程不可读。`data/runtime/governance` 只承载治理控制状态，不作为业务 SQLite 或对象存储 canonical 目录。`--check` 只读检查；停止脚本使用同一 Compose 集合，不删除数据。

`MOONBOX_GOVERNANCE_CAPTURE_MODE=continuous`明确启用日常Capture；可在环境文件设disabled关闭常驻模式。controller每轮发布私有心跳，包含绑定摘要与issues目录可写性；API在30秒心跳窗口内允许新建，失联、只读或绑定不一致时拒绝。重启后自动恢复，不生成或续期maintenance.json。此例外仅覆盖Capture，其他成果应用和文档写入仍遵守原维护窗口；不能用此配置绕过项目授权或外部内容冲突。

授权项目可查询GET /api/v1/requirement-center/capture-readiness，弹窗检查服务并显示原因，未就绪禁用创建，可刷新且保留输入。DB与对象存储结构不变。当前本地backend/web/chat-worker/governance-controller已构建并健康，重启controller后就绪恢复；浏览器最终目标账号创建验证单独记录于Change trace，不以健康检查冒充创建验收。

## Capture 整理 worker（REQ-0029，实施中）

沿用 `bash scripts/docker-up.sh self-storage-sqlite --chat-platform --check` 预检，再使用相同命令去除 --check 启动。依赖已配置的本地仓库、空间/仓库绑定、私有运行目录及单文件Codex授权；不复制个人config或其他凭证。真实环境未就绪时整理返回503，草稿仍可保存。

Capture worker复用常驻模型worker进程，正式写入仍由独立governance-controller处理。模型执行容器只有只读材料副本、隔离运行目录和只读权限配置，禁用shell、统一执行、多Agent、Apps及图片生成能力，不挂载正式治理仓库。输出经严格schema和来源ID校验后才保存为建议。

运行目录中的临时材料与授权副本在正常结束清理；停止信号取消整理，启动时在独占worker锁内清理带本运行域标签的遗留Capture容器及有所有权标记的临时目录。草稿材料清理在worker维护循环执行。删除日志是治理私有状态的一部分，恢复旧数据库时必须保留该日志并先重放删除，再开放读取；不得通过回滚数据库恢复主动删除的材料。

验证边界：本地SQLite服务已启动且真实模型读取合成图片成功，MySQL仅完成独立数据层验证，浏览器完整流程和模型质量验收尚未完成。

Capture worker需要与backend相同的OBJECT_STORAGE_ENDPOINT及MINIO访问配置，用于读取私有材料与执行清理；Compose已显式复用这些变量。它们仅存在于可信worker进程环境，模型执行子容器使用独立最小环境，不继承对象存储凭证。

worker同时接入app-network，通过服务名解析MinIO；仅注入配置但未加入应用网络会造成DNS失败。执行子容器的隔离挂载和权限配置不因此变化。

恢复数据库后、开放流量前，在已配置的backend/worker运行环境执行 `python -m app.governance.capture_cleanup replay-deletions`；按需手工执行到期材料清理使用 `python -m app.governance.capture_cleanup cleanup`。两者使用部署配置，不接受客户端路径；后者会实际删除满足清理条件的对象，不作用于retained正式来源。
