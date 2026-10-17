---
bug_id: BUG-0033-opsx-apply-governance-scope-source-readonly
title: 产品内执行 opsx-apply 源码只读修复评审
status: done
owner: 产品团队
created_at: 2026-10-07 13:11:12
updated_at: 2026-10-12 23:44:10
---

# 产品内执行 opsx-apply 源码只读修复评审

## 评审结论

通过，确认修复。严重度沿用主文档与 trace 的 high；进入 approved，不表示已修复、已纳入 Sprint 或已创建 Change。本轮仅评审与迁移目标对象，最终项目事实是否应用以后端应用结果为准。

## 评审依据

| 检查项 | 结论与证据 |
|---|---|
| 可复现或根因充分 | 通过。root-cause.md 为 confirmed；E15 为原失败 turn 读到的 bug_id/iteration 字段，E17 为同轮次 moonbox-governance 实际 profile；E21/E22 完整 write_policy 对照仅在内存补齐 bug/sprint 即切换实现权限，结合原 Chat 源码只读阻塞，足以确认字段契约不兼容导致回退。 |
| 严重等级 | high 合理，正式实现流程受阻；未见数据破坏或越权事实，不上调等级。 |
| 回归验收 | AC-001 根因取证已完成；AC-002 至 AC-009 与 AC-011 等修复行为验收仍待实施，覆盖合法 REQ/BUG、字段变体、成员权限、Sprint 缺项、权限撤销及治理边界。 |
| 热修路径 | 不采用紧急绕过路径，按评审 → Sprint → OpenSpec → 实施执行。 |

## 修复范围与约束

修复治理事实字段与实现权限判定的兼容关系，保留成员授权、Sprint 双向关联、合法 Change 阶段及源码写入边界。不能通过无条件授予 implementation_write、伪造状态或放宽所有治理命令权限解决。

原失败轮次服务端 reason_code 未持久留存；当前完整策略复现结果不能冒充历史日志。该限制不否定已形成的因果对照，但需按 AC-011 在新 turn 记录脱敏权限决策、实际 profile 和治理输入版本摘要并关联验证。不得记录凭证、原始会话或完整治理文件。

## 验证与交付边界

本轮根因证据门禁通过（confirmed，识别 10 条证据），执行目标文档中文标题检查、迁移预演与 Workflow Sync 预演，完成后核验实际文件差异及子文档完整保留。没有运行修复后产品回归，不修改源码、其他对象、Sprint 或 OpenSpec。历史补证记录中的 hypothesis/probable 是阶段记录，当前结论以根因文档开头 confirmed 与最终确认章节为准。

## 数据采集与链路观测

- product_data_collection_observability: applicable。
- affected_layers: Agent Workflow 权限判定与执行器启动边界；具体日志与 Task Trace 接入在后续 Change 明确。
- N/A：本轮只做评审，不改变 API、DB、UI、部署、安全策略或客户端生成物，不新增埋点。
- validation：已复核 E15、E17、E21、E22 和 AC-011；真实修复验收尚未执行。

## 后续动作

执行 `/sprint-propose --bug BUG-0033-opsx-apply-governance-scope-source-readonly` 纳入 Sprint 并同步为 in_sprint 后，再进入 bug-opsx。当前不自动执行后续步骤，不创建其他 Issue/Change。
