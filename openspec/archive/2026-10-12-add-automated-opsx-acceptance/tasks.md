---
title: 自动验收与证据归档任务
created_at: 2026-10-12 14:59:30
updated_at: 2026-10-12 15:08:00
---

# 自动验收与证据归档任务

## 1. 验收内核

- [x] 1.1 实现声明式 AC 计划、预检、有界执行、产品轮次只读取证和证据脱敏。
- [x] 1.2 实现输入指纹、增量复验、证据包校验和归档就绪检查。
- [x] 1.3 补充聚焦测试，覆盖同轮成功、停止、缺失事件、输入过期和有界失败。

## 2. 工作流集成

- [x] 2.1 新增 `/opsx-accept` 技能并衔接 apply、modify、archive、Workflow Sync。
- [x] 2.2 修正 Issue 验收状态同步，保留已通过结论并拒绝无证据提升。
- [x] 2.3 同步 AGENTS、命令顺序、证据规范、目录规则和治理日志。

## 3. 验证与收尾

- [x] 3.1 运行脚本测试、OpenSpec、上下文预算、目录、Sprint 和 Workflow Sync 聚焦验证。
- [x] 3.2 更新 Change trace 的验证记录并完成 Workflow Sync 与 AI Usage hook。
