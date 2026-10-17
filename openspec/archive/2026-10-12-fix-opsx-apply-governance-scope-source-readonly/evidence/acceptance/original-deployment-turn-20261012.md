---
title: BUG-0033 原部署产品轮次权限复验证据
created_at: 2026-10-12 23:42:00
updated_at: 2026-10-12 23:42:00
---

# BUG-0033 原部署产品轮次权限复验证据

- 环境：本地 MoonBox `moonbox-backend`、`moonbox-chat-worker`、`moonbox-web`，Chat Worker 为 `workspace_mode: source`。后端容器 `policy.py`、`execution.py`、`app_server.py` 与当前工作区源码 SHA-256 逐一相等。
- 样本：临时 BUG、Sprint、Change 使用 `bug_id/iteration` 字段组合且 Change 为 `in_progress`；仅允许写入一次性计数文件。样本不代表原 BUG-0029 历史 turn。
- 真实产品 turn：`9b89c57a-541f-4483-9e78-517b5360ef59`，终态 `completed`，错误码为空。
- 同轮权限事件：selected 与 acknowledged 均为 `implementation_write`、`implementation_change_in_sprint`、`moonbox-write`；治理输入版本字段包含 Change、Sprint、registry 条目摘要，事件 turn ID 与执行 turn 一致。
- 命令事件：目标计数文件的命令以退出码 0 完成；目标文件由 `0\n` 变为 `1\n`，最终 SHA-256 为 `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`。
- result: counter 0→1。
- 边界：本记录只支持合法 BUG 写入、同轮权限留痕和原部署模式的受控复验；不把临时样本等同于原 BUG-0029 历史会话，不保存 prompt、聊天原文、完整事件或数据库。
