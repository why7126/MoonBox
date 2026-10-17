---
purpose: 治理迭代日志
title: 本地数据目录与快照归属边界治理
content: 本地数据目录与自动快照归属边界
created_at: 2026-10-08 15:03:16
updated_at: 2026-10-08 15:03:16
owner: MoonBox 产品团队
---

# 本地数据目录与快照归属边界治理

## 变更摘要

数据规则明确 `data/sqlite` 为本地业务库目录，`data/runtime` 仅承载运行控制状态；自动快照与独立删除日志按用途隔离。旧运行目录出现业务库或媒体文件时，先盘点和保全，再按停服迁移步骤处理。

## 更新文件

`rules/data-management.md`、`data/README.md`、`docs/02-deployment.md`、`docs/04-database-design.md` 和 REQ-0043 对应 OpenSpec Change。

## 验证与后续

目录结构、当前 Change 中文优先和 OpenSpec 严格校验通过；运行态验收以 Change 验证记录为准。后续建议：在隔离部署中回归历史媒体路径迁移及重启读取。
