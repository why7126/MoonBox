---
title: BUG-0033 原部署 REQ 与撤权轮次复验证据
created_at: 2026-10-12 23:48:00
updated_at: 2026-10-12 23:48:00
---

# BUG-0033 原部署 REQ 与撤权轮次复验证据

## AC-003 REQ 实现写入

一次性 REQ、Sprint、Change 使用 `requirement_id/iteration`，Change 为 `in_progress`。真实产品 turn `9a67d449-acff-4f0e-9c07-4fa55ce4a8b8` 为 `completed`，无错误码；同轮 selected/acknowledged 事件均记录 `implementation_write` 与 `moonbox-write`。目标命令退出码 0，临时文件从 `0\n` 变为 `1\n`，最终 SHA-256 为 `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865`。

- result: req counter 0→1。

## AC-007 执行中撤权

在一次性 BUG 的真实产品 turn `f9ec9bb4-2722-43fc-97bd-2ae81e605bbc` 记录 selected `implementation_write` 后，将该临时 Change 状态由 `in_progress` 改为 `applied`。同轮 acknowledged profile 为 `moonbox-write`；服务端轮次以 `error_code=write_permission_revoked` 结束，状态先为 `unknown`，随后收敛为 `stopped`，没有目标文件写入命令。随后没有残留 Chat executor 容器，临时文件持续为 `0\n`，SHA-256 为 `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa`。临时 Change 状态已恢复到 `in_progress`，供夹具清理。

- result: revoked before write。

`unknown` 是撤权后的过渡状态，最终 `stopped`，不能误记为普通 `completed`；本项按撤权错误码、无写入、执行器退出三项证据判断。未保存 prompt、聊天原文、完整事件、数据库或容器日志。
