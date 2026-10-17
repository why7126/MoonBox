---
title: 隔离产品长运行轮次复核
created_at: 2026-10-13 19:54:00
updated_at: 2026-10-14 09:00:00
---

# 隔离产品长运行轮次复核

当前隔离 SQLite 中的产品 Chat 轮次 `67825fa2-122c-4204-99ca-9a194f55885a` 执行 `/bug-review BUG-0999-ac051-isolated-review --approve`，从 2026-10-13 16:04:09 UTC 持续至 16:09:41 UTC，历时 332 秒，超过 300 秒默认墙钟界限。`chat_turns.status=completed`、`error_code=null`、`heartbeat_at=16:09:41`，原执行器标识保留；同轮候选 `applied`，application `applied/verified`，无错误码。数据库保留 401 条事件和两条消息；定向验收以这条当前仍在 SQLite 的轮次为准。

先前 BUG-0039 `bug-generate` 轮次 `fb856ea0-fb5a-4c34-a27a-421bbcafb684` 从 17:32:11 至 17:43:38，历时 11 分 27 秒，曾在旧隔离库完成并由当时的定向验收通过；当前 SQLite 已重建，不再将旧轮次当成当前数据库证据。其历史产品截图见 [桌面](AC-030-assistant-running-1440x900.jpg) 与 [移动](AC-030-assistant-running-390x900.jpg)。

`src/backend/tests/test_chat_long_running.py` 覆盖默认无墙钟限制、显式限制及长历史响应与流事件大小边界；停止、权限、额度与恢复门禁由聚焦回归和历史 AF-038 返修记录核对。原 REQ-0027 执行器权威状态为 `interrupted` 时按 stopped 归并，保留部分成果而不报告完成。当前 332 秒真实轮次没有主动停止或触发额度失败，负向分支不冒充真实产品观察。

本次聚焦回归：长运行、手动停止、仓库权限撤销、额度边界、输出上限与恢复用量共 10 passed；原执行器精确轮次恢复、断线归并及评审部分结果拒绝共 8 passed。单项产品轮次诊断以当前 332 秒轮次得到 `same-turn-complete`，同轮命令序号 200、退出码 0。`AC-038` 的测试与真实观察分开记录。
