---
title: 必要依赖子交付的验收范围保护
created_at: '2026-10-29 11:15:00'
updated_at: '2026-10-29 11:15:00'
---

# 必要依赖子交付的验收范围保护

用户批准在三个工作区需求的闭环中推进 REQ-0048 必需依赖；本次未授权交付其全量 Chat 自主编排。对应 Change 为 add-isolated-candidate-validation。

现有同步器把来源 Change ready 直接投影为 Issue passed，无法表达批准的子交付。新增计划字段 issue_acceptance_scope partial：当前 Change 仍通过全部自身 AC，来源需求投影 partial 且不自动勾选整体清单；既有未声明计划行为保持一致。回归覆盖部分与完整计划的不同投影，不把命令退出成功视作整体产品完成。

本次变更属于必要依赖的签认边界，不创建额外 Issue 或 Change，不触发归档或发布。验证结果与实现成本随本次依赖 Change 记录。

补齐计划读入门禁：部分范围须有本地完整 AC 清单、逐项 Issue 映射和范围说明；回归包含有效子范围、未知 Issue AC、漏列本地 AC 与完整范围拒绝。

归档预检发现整Issue AC数量被用于子Change门禁，现已拆分：子Change只依据其有效映射与证据，完整Issue保持未就绪；partial状态阻止父Issue自动关闭与目录晋级。保留原恢复、规格合并和人工验收门禁。
