---
title: 本地端口上限收紧治理记录
created_at: 2026-10-08 18:29:53
updated_at: 2026-10-08 18:29:53
---
# 本地端口上限收紧治理记录

## 迭代目标

将本地宿主机允许端口段从 39001～39099 收紧为 39001～39050。

## 变更摘要与影响范围

端口规则、环境样例、部署说明、校验代码、测试探针和当前 OpenSpec Change 同步调整；现有默认端口与私有环境配置仍在新范围，无需重新分配端口。影响 Docker Compose 配置准入和本地探针；API、数据库、Web 功能、管理端、Orval、客户端生成及容器内端口不变。

## 更新文件

`rules/port-management.md`、`.env.example`、`docs/02-deployment.md`、`deploy/scripts/validate-env.py`、Chat 测试入口及聚焦测试、当前 OpenSpec Change 和 Sprint scope。

## 验证结果

端口边界、Compose 解析、OpenSpec、中文优先、目录与 Sprint scope 校验结果记录于 Change trace。

## 后续建议

以后新增本地服务端口从 39001～39050 中选择并运行环境校验。未自动创建 Issue。
