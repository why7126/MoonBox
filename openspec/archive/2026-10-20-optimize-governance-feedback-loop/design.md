---
title: 治理量化闭环设计
created_at: 2026-10-20 18:18:42
updated_at: 2026-10-20 18:18:42
---

# 治理量化闭环设计

## 设计目标
每次调用轻量采集和复盘；有可复核问题才优化，不为优化制造修改。保留现有主任务与质量门禁。脚本提供确定性指标、授权/预算/范围判定与候选台账，Agent 执行已授权的 spec-opt 链路。

## 架构
新增 scripts/governance_feedback.py（标准库），运行数据位于被忽略的 logs/governance-feedback/。start/finish 提供运行身份与结束事实；import-usage 仅导入派生量化事实；review 产生幂等候选；decide 校验授权、文件范围、Change/Sprint、预算和递归；evaluate 比较基线/后续同组完整样本，扣除优化成本。

规则事实源为 docs/standards/governance-feedback-loop.md，策略位于 rules/governance-feedback-policy.json。默认治理范围长期授权，明确排除 src、正式规格、安全权限及验收门禁放宽；可撤销策略，不自动归档、提交或发布。政策不是新增权限或绕过沙箱。

## 指标口径
wall_seconds 仅由明确 start/finish 计算；会话导入为 provisional，不伪装完整运行。Token 缺失为 null、实测为 actual；不累加缓存与推理子集。人工等待缺少来源时不扣除。样本按 command、task_class、model、environment、validation_profile、workload_key 比较，版本差异显式记录。优化成本包括分析/修复/验证子运行，按唯一 run_id 去重。缺成本、缺质量、样本不匹配时不签认收益。

## 控制与恢复
运行和候选原子写入并使用文件锁；同一 Hook 重放不重复计量。完整记录不被暂态导入覆盖。优化子任务标记 optimization_id 与 depth；depth 非零不得再创建优化。自动优化前先建立 Change 并纳入 Sprint，decide 不把放行候选当作完成。完成后必须通过测试，后续效果未证实时保留 observing。失败回退仅针对当前优化差异，不重置工作区。

## 验证方案
治理脚本单测、真实 CLI 生命周期集成、既有 AI Usage 回归、授权拒绝/预算/空样本/质量退化/净收益正反例、中文/目录/上下文/Change/Sprint 门禁及 opsx-accept。性能记录为本地 CLI 实测，样例收益只能标记合成验证，不宣称真实长期收益。
