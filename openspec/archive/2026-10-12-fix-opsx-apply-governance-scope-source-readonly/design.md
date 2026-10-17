---
title: 实现写权限字段归一化与决策观测设计
created_at: 2026-10-07 15:16:20
updated_at: 2026-10-07 16:55:05
---

# 实现写权限字段归一化与决策观测设计

## 背景与现状

根因证据见来源 BUG root-cause.md E15、E17、E21、E22。当前 `_implementation_ready` 使用 bug/requirement 与 sprint，而实际 trace 使用 bug_id/iteration。只补一个字段仍失败，同时归一化两个字段后完整策略可返回 implementation_write。

## 修复方案

### 可信字段归一化

只解析服务端绑定治理根目录内的 trace，不信任 prompt 或客户端 supplied scope。BUG 来源候选为 bug、bug_id、source_bug、related_bug；REQ 来源为 requirement、requirement_id、req_id、source_requirement；Sprint 为 sprint、iteration。仅接受非空字符串和合法 ID。多字段存在时要求同语义一致，冲突、错误类型、同时声明不一致来源或与主对象不符时拒绝实现写入，返回稳定诊断原因。缺失仍按缺失处理，不能从自由文本猜测授权。

优先局部共享解析函数而非在策略中散布逐字段回退；不改写历史 trace，不通过无条件授予权限修复。保留注册表 in_sprint、合法 related_change、proposed/in_progress、Sprint 同时包含来源 Issue 和 Change 的门禁。仅归一化 Change 输入，不扩展直接 Change 主对象授权、applied/archived 阶段或未知命令权限。

### 权限决策与执行器一致性

保留空间/成员授权和准备候选分支优先级。准备候选仍仅授治理权限；运行中权限撤销继续停止执行。实现门禁不足时保留安全权限范围，并提供区分缺失/冲突的稳定原因；不能将治理可写解释为实现已获准。

执行器启动前生成脱敏决策摘要，通过现有 chat 事件与 Task Trace 关联同一 turn：scope、reason_code、选用 profile、时间、主对象/Change/Sprint 标识、注册表目标条目及 Change/Sprint 输入内容摘要 hash。记录由服务端实际读取的版本派生，不用当前文件代替历史。区分计划 profile、启动时传入 profile 和可核验的实际启动结果；未取得实际结果时标明未知，不捏造已确认。配置不匹配阻断启动。观测写入失败不扩权、不伪造证据，依项目观测标准报告降级；未完成留痕回归不通过 AC-011。

### 数据采集与链路观测

product_data_collection_observability: applicable。affected_layers: Agent Workflow、chat 执行事件、request_logs/task_traces/task_trace_spans 的关联。优先复用现有事件 payload，禁止原始 prompt、凭证、完整治理文档、客户数据及本机绝对路径。无新增用户操作，不伪造 usage_events；不预设 schema/API 改动，若发生则同步迁移、SQLite/MySQL、OpenAPI 与客户端生成验证。validation：AC-011 校验同 turn 关联、版本摘要、profile 一致性、降级、重放和脱敏。

## 测试策略

先增加能在旧实现失败的真实字段组合回归，再验证规范字段、全部别名、单字段缺失、冲突、非法类型、错误来源、成员只读、Sprint 缺项、applied/archived、治理候选和撤权。以原 BUG-0029 字段建立受控测试对象，使用完整 write_policy 与执行器 adapter 验证，不只运行 AST。真实测试环境执行 apply，检查源码可写及治理边界、同 turn 留痕；合成回归不能替代真实行为验收。后端用例和 API 事件读写采用隔离数据库，不改生产数据。

## 风险与回滚

别名过度兼容可能扩权：采用一致性检查、来源匹配和负向矩阵。日志失败及 profile 漂移：明确未知/降级并核验实际启动。当前其他 Change 可能触及同模块，apply 前复核差异，保留既有归档授权修复。回滚代码而非扩大挂载，不删除审计证据。sprint-008 已满 30/30 人天，新增范围先重算门禁。

## 文档与验收边界

更新权限与观测文档及 BUG 验收结果；实际 API/DB/UI/部署变化按影响同步，N/A 写具体原因。原始历史 reason_code 仍不可恢复，不将复现值改写为历史观测。无原型/UI 布局修改，UI 视觉复刻门禁不适用。

## 实施细化

BUG 可以同时记录父 REQ；只将同类型来源用于授权，父 REQ 不替代 BUG 关联。无命名 profile 的旧 adapter 仅通过布尔 write 获得 implementation_write 对应范围，治理/归档范围不映射为宽泛源码写；其实际 profile 记 unknown。命名 adapter 的 profile 不匹配及实现 scope 下 write=False 均阻断。acknowledged 表示 RPC 请求确认而非 OS enforcement 证明，真实验收单列。沿用现有 Chat 事件和租约/source_id 幂等，不新增 schema。
