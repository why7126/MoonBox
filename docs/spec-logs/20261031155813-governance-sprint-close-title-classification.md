---
title: Sprint 关闭标题误报修复
created_at: 2026-10-31 15:58:13
updated_at: 2026-10-31 15:58:13
---

目标：区分缺陷名称与当前生命周期状态。
变更：扫描时只移除已匹配 Issue 的完整标题，保留原行诊断与路径检查。
影响及更新文件：scripts/sprint_close_stale_scan.py、对应单元测试、scripts/README.md、iterations-lifecycle 规则、sprint-archive 技能与当前 Change。
验证：5项回归通过，sprint-017 实际扫描0阻塞。
API/DB/Web/客户端/管理端/Orval/Docker Compose：均无变化。
后续：效果待观察，不宣称用量收益；继续原 Sprint 归档。
