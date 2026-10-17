---
title: BUG-0033 隔离环境真实写入复验记录
created_at: 2026-10-12 23:30:00
updated_at: 2026-10-12 23:30:00
---

# BUG-0033 隔离环境真实写入复验记录

执行 `CHAT_LIVE_ISOLATED_PROBE=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src/backend src/backend/.venv/bin/python -m pytest -q src/backend/tests/test_chat_container_worker.py -k test_bug_alias_apply_writes_source_with_same_turn_permission_event`，结果 `1 passed, 4 deselected`，耗时 45.43 秒。

该测试在一次性治理根目录、仓库、SQLite 和真实 Codex 容器中建立 `bug_id/iteration` 形式的 BUG、Sprint、Change。它断言 `counter.txt` 从 `0` 写为 `1`，同一 turn 的持久事件包含 `implementation_write`、选用 `moonbox-write`、确认 `moonbox-write`，且事件中的 turn ID 与执行 turn 一致。测试的 finally 清理运行目录及工作区；临时测试根目录由测试夹具清理。

本记录只证明隔离样本的实际写入与同轮事件，不是原 BUG-0029 部署会话的 AC-009 复验，不覆盖 REQ 真实写入、运行中撤权或治理命令真实只读边界。未保存聊天原文、prompt、原始事件、数据库或容器日志。
