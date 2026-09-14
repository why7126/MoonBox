---
created_at: 2026-09-12 21:28:51
updated_at: 2026-09-12 21:28:51
---

# Apply生命周期事件契约

来源BUG-0015，Change fix-requirement-center-apply-lifecycle-sync，sprint-005。两份apply技能、sprint-apply、workflow-sync及命令顺序接入opsx.start/opsx.progress/opsx.apply；document-governance记录execution版本与兼容边界。实现与证据见Change verification.md。保留Issue in_sprint及BUG severity语义。

跨项目落地提示词：分离启动事实、任务计数与完成门禁，让CLI和看板共享状态解析，并验证0/N、幂等、故障恢复和真实刷新。

后续建议：复用该矩阵检查未来入口，无需自动新增Issue。
