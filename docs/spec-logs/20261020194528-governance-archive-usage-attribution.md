---
title: 归档用量归属与桌面消息兼容
created_at: "2026-10-20 19:45:28"
updated_at: "2026-10-20 19:45:28"
---

# 归档用量归属与桌面消息兼容

## 目标与证据
归档使用 iteration 元数据，但旧 wrapper 只读取 sprint；桌面用户 content 数组未被识别，导致有 Token 事件却无命令。证据仅保留事件类型和聚合计数。

## 更新文件与影响
scripts/archive-change.sh 复用 Workflow Sync 解析；scripts/ai_usage.py 支持文本块并输出诊断；tests/unit/test_ai_usage.py、test_change_identity.py 覆盖兼容和真实 wrapper；同步 opsx-archive 技能与治理量化标准。Change: fix-archive-usage-attribution，Sprint: sprint-011，新增估算 1 人天、2 SP，容量仍保留 30 人天。

## 验证与效果
初轮 23 项测试通过，首次 4/4 自动验收通过；摘要诊断增量回归结果见 Change 验证记录。真实历史归档由 unavailable/no-sprint 变为 actual，Sprint 快照 refreshed，0 warning；两项 Change 共用 1 条命令记录、13 次模型调用、763846 Token，不重复累计。修复后实时会话解析 16 条命令，解析 0.1324 秒；不将持续增长的会话作为速度比较样本。

## 优化成本与授权
分析 87.353329 秒；实施、验证实耗见 Change verification.md。实际优化 Token 精确边界不可得，不能以历史归档 Token 替代。自动候选因成本不完整、防递归保持 blocked；按用户本次明确授权实施，未放宽策略。修复已验证，长期净收益待观察。

## 业务边界
API、DB、Web、客户端、管理端、Orval、Docker Compose 均 N/A，未修改业务 src 或已归档 Change；未新增权限、未提交原始会话。

## 后续建议
后续收集同组完成调用样本再评估收益；不触发递归优化或创建额外 Issue。
