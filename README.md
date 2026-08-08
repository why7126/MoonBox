---
purpose: 项目入口说明
content: MoonBox 产品简介、快速启动、目录导航、常用命令和文档入口
created_at: 2026-07-29 22:55:00
updated_at: 2026-08-07 00:00:00
owner: MoonBox 产品团队
---

# MoonBox

MoonBox 是下一代 AI 软件研发基础设施。它不是帮助开发者更快写代码，而是帮助个人和企业建立一个由 Agent 驱动的软件研发组织，让软件从团队生产走向智能组织生产。

## 产品范围

| 项 | 配置 |
|---|---|
| 产品定位 | AI 原生软件工厂 |
| 目标用户 | AI 创业者、小型软件团队、AI 原生企业团队 |
| 产品形态 | Web 端、管理后台、REST API |
| 核心能力 | Harness Runtime、Agent Workflow Engine、Product Knowledge Graph、Agent Organization Model |
| UI 设计 | 严格遵循 `rules/ui-design.md`，来源为 MoonBox UI 设计指南 |

## 技术栈

| 分层 | 技术栈 |
|---|---|
| 后端 | Python + FastAPI + Pydantic + uv |
| 前端 | React + TypeScript + TailWind + Shadcn/UI + Axios + Orval + pnpm |
| 数据库 | SQLite |
| 对象存储 | MinIO 兼容对象存储，用于文档与图片资产 |
| 部署 | docker-compose 本地六模式矩阵、生产外部对象存储 + 外部 MySQL |
| 产品手册 | Mintlify 源目录 + Docker Compose docs-site 预览/承载 |

## 快速启动

```bash
cp .env.example .env
bash scripts/docker-up.sh
```

部署矩阵与产品手册预览：

```bash
bash deploy/scripts/up.sh local self-storage-sqlite
python scripts/generate-mintlify-docs.py --version latest
python scripts/validate-mintlify-docs.py
```

运行校验：

```bash
python scripts/validate-directory-structure.py
python scripts/validate-env-ignore-policy.py
python scripts/validate-openspec-language.py
python scripts/validate-sprint-archive-readiness.py --sprint sprint-001
python scripts/generate-sprint-fact-sheet.py --sprint sprint-001 --summary
python scripts/validate-generated-docs.py --strict
bash scripts/validate-openspec.sh
bash scripts/run-tests.sh
```

## 目录导航

| 路径 | 用途 |
|---|---|
| `AGENTS.md` | AI Agent 执行入口、读取路由与红线 |
| `project.yaml` | 项目结构化事实源 |
| `rules/` | 工程、文档、API、数据库、UI、安全、测试规则 |
| `docs/` | 产品、架构、部署、API、数据库与专项标准 |
| `docs/spec-logs/` | `/spec-study` 跨项目 Harness 学习报告 |
| `issues/` | 需求与缺陷治理 |
| `iterations/` | Sprint 计划、执行和归档 |
| `openspec/` | OpenSpec 变更与规格 |
| `deploy/` | 本地/生产 Docker Compose 环境矩阵、env 示例和部署脚本 |
| `mintlify/` | 公开产品手册源目录、版本投影和站点配置 |
| `.agents/skills/` | 唯一 Agent 技能入口 |

## 常用命令

开放问题、想法或方案讨论先用 `/explore` 只读探索；需求从 `/capture` 或 `/req-capture` 进入；缺陷从 `/bug-capture` 进入；已评审事项通过 `/req-opsx` 或 `/bug-opsx` 转为 OpenSpec Change；实现通过 `/sprint-apply` 或 `/opsx-apply` 执行，并在完成后同步工作流状态。规范、技能、命令和治理脚本优化使用 `/spec-opt`；跨项目 Harness 学习和确认后应用使用 `/spec-study`。

关键未决策事项集中在 `docs/pending-decisions.md`。
