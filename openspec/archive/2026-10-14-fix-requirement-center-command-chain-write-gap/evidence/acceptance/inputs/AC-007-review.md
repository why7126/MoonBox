---
title: 未接入治理命令的产品提示复核
created_at: 2026-10-13 20:04:00
updated_at: 2026-10-13 20:04:00
---

# 未接入治理命令的产品提示复核

- 当前前端源码对能力矩阵以外的命令返回 `codex_command_only`，点击时显示“产品内尚未接入该治理写入链路，请在 Codex 执行”及具体命令，并在创建对象会话前返回。
- `keeps unknown governance commands in Codex without opening a product object session` 使用未接入测试命令验证提示包含完整命令、对象会话请求为零、原卡片仍在。完整需求中心前端测试 125 项通过；这是源码与组件回归，不冒充隔离产品镜像中的新运行态截图。
