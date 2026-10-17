---
title: 本地数据目录用途说明
created_at: 2026-10-08 14:54:45
updated_at: 2026-10-08 14:54:45
---

# 本地数据目录用途说明

| 目录 | 用途 |
|---|---|
| `data/sqlite/` | 本地业务 SQLite，默认 `moonbox.db`；不是 Chat/Codex 状态库的汇总目录 |
| `data/runtime/` | Chat、治理控制器、Codex 执行状态和按用途分隔的私有备份；`migrations/` 保存离线迁移保全副本 |
| `data/tmp/` | 可清理的临时处理文件 |
| `data/s3/` | 本地自建 MinIO 对象数据 |

运行数据库、私有备份、删除日志和真实客户数据均被 Git 忽略。不得按文件扩展名将执行器状态库搬进 `data/sqlite/`，也不得删除独立删除日志来清理快照。

旧业务库迁移和自动快照轮转的操作与回滚步骤见 `docs/02-deployment.md`；本说明只给出目录归属。
