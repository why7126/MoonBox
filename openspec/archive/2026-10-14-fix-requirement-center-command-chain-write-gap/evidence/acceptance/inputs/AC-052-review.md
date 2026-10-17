---
title: 隔离 Bug 过期基准与续接复核
created_at: 2026-10-13 16:56:00
updated_at: 2026-10-13 16:56:00
---

# 隔离 Bug 过期基准与续接复核

- BUG-0038-acceptance-stale-retry 的旧候选 `3c87807f-236d-5885-ab00-6fd1a24919a2` 在发送前因事实源变化被拒绝，保留为 prepared，未产生执行轮次或应用；新候选 `de41425e-8b8e-5f36-a3a5-363d28a60b9f` 在产品轮次 `96786af1-c09c-4c51-abb8-15ca975e600d` 应用成功，同轮 `bug.generate` 同步命令退出码为 0。
- BUG-0039-acceptance-stale-kind 的旧候选 `3826484f-0f00-5254-adb3-316fc0b3aebd` 同样停留在 prepared，无执行轮次。此前 Firefox 观察到“项目文件已变化，请重新准备治理动作”；结构化 `workspace_fact_source_stale` kind 经聚焦回归断言确认。
- 历史产品操作及文件保留证据见 Change `verification.md` 和 Issue `acceptance.md`。本次只读复核产品 SQLite 的候选、轮次及应用状态，不将新候选成功视为旧候选执行成功。
