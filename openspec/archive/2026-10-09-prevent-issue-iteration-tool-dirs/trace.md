---
title: 阻止 Issue 与迭代目录生成工具残留追溯记录
status: applied
iteration: sprint-008
requirement: null
bug: null
---

# 阻止 Issue 与迭代目录生成工具残留追溯记录

## 来源与范围

来源：用户明确执行 `/spec-opt`，要求清理 `issues/` 与 `iterations/` 下的空工具目录并防止再次生成。Change 由 OpenSpec CLI 创建，作为纯治理项纳入 sprint-008。

## 验证记录

| 校验 | 结果 |
|---|---|
| 目标目录盘点与清理 | 四个目录均为空，已用 `rmdir` 移除；未触碰业务文件 |
| 目录结构正向校验 | 通过 |
| 目录结构反向校验 | 四种目标路径分别生成空目录时均被阻断，测试后已移除 |
| Agent 上下文预算 | 通过 |
| 当前 Change 中文优先与标题 | 通过 |
| OpenSpec validate | 通过 |
| sprint-008 scope | 通过；Change 已纳入 Sprint |
| 聚焦 diff whitespace | 通过 |

本次只修改治理脚本、规则和文档；API、数据库、Web、管理端、客户端生成和 Docker Compose 均未改动。无法从空目录本身确认原始创建进程；本次校验保证残留不再通过治理门禁，但不会在操作系统层禁止创建目录。
