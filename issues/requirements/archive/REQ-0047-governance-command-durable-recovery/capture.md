---
requirement_id: REQ-0047-governance-command-durable-recovery
title: 治理命令持久化阶段与幂等恢复闭环
status: done
created_at: '2026-10-19 14:16:01'
updated_at: 2026-10-19 18:28:27
priority: P1
owner: 产品团队
source: 本会话 explore 整合及用户授权 capture
lifecycle_stage: plan
captured_via: capture
classification_rationale: 在已有命令真实化与完成门禁基础上补充跨中断的持久化阶段、恢复入口和启动完整性预检。
parent_requirement: REQ-0027-requirement-center-command-chain-realization
related_requirements:
- REQ-0046-chat-execution-output-status-feedback
related_bugs:
- BUG-0047-review-recovery-operation-record-missing
- BUG-0044-requirement-stage-premature-transition-session-split
---

# 治理命令持久化阶段与幂等恢复闭环

## 目标与背景

以 BUG-0047-review-recovery-operation-record-missing 为故障案例，在已有命令真实写入和阶段完成门禁上补齐持久化执行阶段、启动完整性预检及幂等恢复。服务中断或响应丢失后，能够识别已有成果并继续未完成步骤，降低重复模型执行与重复写入风险。

按一个可独立验收的治理操作恢复能力记录，阶段检查、成果保留和幂等续接是同一恢复闭环。P1 为初判：涉及多类治理命令可靠性和重复写入风险，实际覆盖范围待完善。

## 增量范围

1. 启动前检查基线、恢复记录、命令身份、版本与权限；准备完整才启动，失败提供明确处理路径。
2. 持久化操作阶段与成果引用，区分生成、校验、应用、回读、完成；服务重启后可读取可信检查点。
3. 恢复先核对成果、原始版本、当前权限和并发冲突，复用有效成果并只重试未完成步骤；重复恢复及响应丢失不重复迁移或生成记录。
4. 区分可自动重试、需要重新生成、需要人工处理；证据不足保持阻断，不补空记录、不强改状态、不绕过校验。
5. 为展示层提供可信完成结果、版本及可执行恢复能力；应用完成但看板同步失败须可区分，统一文案与呈现由 REQ-0046-chat-execution-output-status-feedback 承接。

建议先在 req-review / bug-review 验证完整恢复闭环，再按适用矩阵推广到其他治理命令；不默认将生产发布或不可逆操作纳入自动重试授权。

## 既有能力与去重边界

| 关联项 | 当前状态 | 归属与边界 |
|---|---|---|
| REQ-0027-requirement-center-command-chain-realization | done / archive | 既有命令 controller、真实写入与 Workflow Sync 基础；本需求作为增量子需求，不重复建设命令入口。 |
| BUG-0044-requirement-stage-premature-transition-session-split | done / archive | 已有阶段完成门禁、对象互斥和失败成果核验；本需求复用并评估不足，不重复声明其交付。 |
| REQ-0046-chat-execution-output-status-feedback | pending_review / plan | 统一状态提示、成功措辞约束及异常入口展示；不另建展示需求。 |
| BUG-0047-review-recovery-operation-record-missing | captured / plan | 修复本次评审恢复记录缺失；本需求负责通用能力增量。 |
| BUG-0046-chat-midrun-question-response-unavailable | pending_review / plan | 人工问题回答与同轮续接，非中断后的成果幂等恢复。 |

用户已通过本会话原生交互选择：新增关联需求，仅记录持久化阶段、幂等续接、启动完整性预检等增量，关联 BUG-0044 与 REQ-0027。未修改已归档 Issue 的状态或历史交付。

## 建议验收

- 启动记录缺失：执行前阻断，事实源不变。
- 生成成果后、应用前服务重启：成果可核查并恢复未完成步骤。
- 应用成功、响应丢失：重复请求返回同一可信结果，不重复产生副作用。
- 同对象并发修改：报告冲突，不覆盖新成果。
- 权限或项目绑定变化：重新鉴权，拒绝越权恢复。
- 应用成功、看板同步失败：后端完成事实保留，展示可重新加载，不重新执行评审。
- 正常完成：事实源、应用记录、Chat 与看板最终一致，完成依据包含业务校验与回读结果。
- 不足以安全恢复：保留成果和诊断，明确人工处理；不展示不可用的恢复按钮。

## 实施建议与待澄清

先完成关联缺陷的根因定位与聚焦修复，再定义增量恢复契约并以评审链路试点。需确认既有持久化记录覆盖、检查点粒度、恢复入口和权限、自动重试上限及退避、历史记录兼容、成果保留周期、跨命令适用矩阵。文件与数据库不能假定天然原子，后续设计需明确提交与恢复一致性策略。当前仅 Capture，不承诺已实现恢复能力。

## 数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: API、请求日志、Task Trace、阶段记录和 Web 结果关联。

validation: 后续验证预检失败、服务重启、重复恢复、并发冲突和结果同步的脱敏链路；本次仅记录，不改变 schema、API、部署、保留周期、对象存储或客户端生成物，以上实现变更本轮 N/A。
