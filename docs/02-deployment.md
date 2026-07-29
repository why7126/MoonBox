---
purpose: 部署说明
content: MoonBox 本地 docker-compose 部署、端口和环境变量边界
created_at: 2026-07-29 22:55:00
updated_at: 2026-07-29 22:55:00
owner: MoonBox 产品团队
---

# 部署说明

MoonBox 当前启用 docker-compose 本地开发部署。生产部署拓扑在 `docs/pending-decisions.md` 集中管理。

## 本地服务

| 服务 | 容器端口 | 默认主机端口 | 说明 |
|---|---:|---:|---|
| backend | 8000 | 8000 | FastAPI REST API |
| web | 5173 | 5173 | React 开发服务 |
| minio | 9000 | 9000 | 文档与图片对象存储 |

## 命令

```bash
cp .env.example .env
bash scripts/docker-up.sh
bash scripts/docker-down.sh
```

## 环境边界

- `.env.example` 只保留开发默认值和变量说明。
- `.env`、真实密钥、真实客户数据、运行时数据库文件不得提交。
- 生产环境必须替换默认密钥、对象存储凭据和外部 LLM 凭据。
