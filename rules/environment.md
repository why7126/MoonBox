---
purpose: 环境变量管理规范
content: .env.example 维护、环境变量命名、安全边界、Docker Compose 环境同步规则
update_method: 新增服务、端口、密钥、第三方配置、对象存储、数据库或处理参数时更新
created_at: 2026-06-13 00:00:00
updated_at: 2026-08-04 00:00:00
note: .env.example 可提交，.env 禁止提交
---

# 环境变量管理规范

## 1. 基本原则

- 根目录必须提供 `.env.example`。
- 真实 `.env` 文件禁止提交 Git。
- 真实环境文件允许存在于本地工作区用于启动、构建和验收；只要被 Git ignore 覆盖且未被复制进受治理文档/归档/发布产物，其存在本身不得阻断 `/opsx-archive`、`/sprint-archive` 或目录结构校验。
- 真实环境文件包括但不限于 `.env`、`.env.local`、`.env.*`、`deploy/**/*.env`、`scripts/build-images.env`；对应 `.env.example`、`deploy/**/*.env.example`、`scripts/build-images.env.example` 必须保持可提交。
- 新增任何环境变量时，必须同步更新 `.env.example`。
- 新增或修改 `.env.example`、`.env.docker` 等变量时，变量上一行 SHOULD 有注释，说明用途、取值范围、默认值含义或安全边界。
- Docker Compose 使用的变量必须在 `.env.example` 中有说明。
- Docker Compose 默认支持自建对象存储/外部对象存储与 SQLite/自建 MySQL/外部 MySQL 组合模式，模式变量必须在 `.env.example` 和部署文档中同步说明。
- `deploy/local/*.env.example`、`deploy/prod/*.env.example` 必须与 `deploy/README.md` 的环境矩阵保持一致；真实 `deploy/**/*.env` 禁止提交。
- 产品手册站点端口使用 `HOST_PORT_MINTLIFY_DOCS`，必须同步 `.env.example`、`docs/02-deployment.md` 和 `deploy/*/*.env.example`。
- 不允许在代码、文档示例、测试中写入真实密钥。
- 生产环境不得静默使用本地/demo 默认配置。
- 环境文件 ignore 策略变化后 MUST 运行 `python scripts/validate-env-ignore-policy.py`。

## 2. 命名规范

环境变量使用大写蛇形命名：

```text
SERVICE_NAME_CONFIG_NAME
```

示例：

```text
DATABASE_URL
DATABASE_DEPLOYMENT_MODE
OBJECT_STORAGE_DEPLOYMENT_MODE
OBJECT_STORAGE_BUCKET
MAX_UPLOAD_SIZE_MB
VITE_API_BASE_URL
```

## 3. AI 更新规则

AI 修改以下内容时，必须检查 `.env.example`：

```text
□ docker-compose*.yml
□ Dockerfile
□ 后端配置文件
□ 前端构建配置
□ 数据库连接
□ 对象存储配置
□ 上传大小限制
□ 第三方服务配置
```

注释不得包含真实密钥、真实生产域名、真实客户数据或无法公开的运维信息。
