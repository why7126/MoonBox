---
title: 本地宿主机端口段治理记录
created_at: 2026-10-08 15:19:34
updated_at: 2026-10-08 15:19:34
---
# 本地宿主机端口段治理记录

## 迭代目标

将 MoonBox 本地宿主机端口统一迁移至 39001～39099。

## 变更摘要与影响范围

默认服务端口、Compose 映射、环境样例、校验脚本、测试探针和部署说明由旧 181xx 映射到 390xx。容器内部端口未变。影响 Docker Compose、Web 访问地址与后端 CORS 默认来源；API 契约、数据库、管理端功能、Orval 和客户端生成无变化。

## 更新文件

`rules/port-management.md`、`.env.example`、`deploy/local/*.env.example`、Compose、启动及端口校验脚本、相关测试入口、`docs/02-deployment.md`、README、OpenSpec Change。

## 验证结果

OpenSpec、中文优先、目录、上下文预算校验通过；根与本地 Compose config 通过。聚焦 pytest 因当前 Python 环境缺少 FastAPI/pytest 依赖未运行。

## 后续建议

在维护窗口将被 Git 忽略的私有 `.env` 端口与 CORS 来源同步到新范围，重启后以实际访问地址复验。未自动创建 Issue。
