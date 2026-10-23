---
title: 归档用量修复验证
created_at: "2026-10-20 19:44:04"
updated_at: "2026-10-20 19:44:04"
---

# 归档用量修复验证

## 回归
23 项通过（17.36 秒），覆盖 wrapper 串行恢复、iteration 和 Sprint 范围解析、桌面文本块、图片忽略、Token 旁路去重与缺失诊断。初次测试隔离 fixture 缺少现有 app 依赖，补齐只读测试依赖后通过。

## 真实会话
初始 269 条 token_count 却 0 命令；修复后持续会话解析 16 条命令、279 条 Token 事件，解析 0.1324 秒。事件增加来自持续执行，不作为性能收益。证据见 evidence/real-session-summary.json。历史两项归档合并重放 Hook 成功：actual、1 条共享命令、0 warning，sprint-011 快照 refreshed；未重复归档。

## 成本与门禁
分析运行 run-a8f58af3b7684601bc304e87e3cb00b0 为 87.353329 秒；实施验收运行 run-8e0f53e79f09469695dc5fc52c728165 待结算。候选 opt-c5cafdbbb9f06ee0baec3736 因 cost-incomplete、recursive-optimization 阻断，保留原状态。本次按明确单次任务授权继续，未放宽自动策略。Token 精确边界仍不可得，收益待观察。

## 影响
仅治理脚本、测试、标准与技能；业务 src、API、DB、Web、客户端、管理端、Orval、Docker Compose 均无变更。已归档 Change 未修改。

## 历史归档用量回填
共享归档命令记录：13 次模型调用，total_tokens=763846，input_tokens=762746，output_tokens=1100；两项 BUG 与 Change 同时关联 sprint-011。该值是模型报告的输入输出总量，含重复上下文输入，不是本次优化成本，不按两项 Change 重复加总。

## 最终门禁与成本结算
最终 24 项回归通过，自动验收 4/4，readiness=ready、stale=[]；增量执行 1 项、复用 3 项，7.129 秒。OpenSpec strict、中文、上下文预算、目录、交付证据、Sprint 范围和 shell 语法均通过。Workflow Sync opsx.apply/opsx.accept 无错误。

实测分析 87.353329 秒，实施与验证 285.800713 秒，合计 373.154042 秒（约 6 分 13 秒）；覆盖显式计时区间，不含初始路由及最终文档收尾。成本归并见 evidence/optimization-cost.json。精确优化 Token=null，当前 Hook 仅为未结束调用的 provisional 数值，不能作为完整成本或净收益。候选保持 blocked；交付 passed、收益 observing。
