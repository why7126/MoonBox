---
bug_id: BUG-0047-review-recovery-operation-record-missing
title: 评审恢复记录缺失导致成果未应用与卡片未流转
status: done
created_at: '2026-10-19 14:16:01'
updated_at: 2026-10-19 15:36:46
severity: high
owner: 产品团队
source: 本会话 explore 整合及用户授权 capture
lifecycle_stage: review
captured_via: capture
classification_rationale: 已有评审能力执行失败，属于既有能力偏差，独立于通用恢复能力增量。
environment: 本地产品；沿用本会话 2026-10-19 取证，部署版本待核对
related_requirement: REQ-0046-chat-execution-output-status-feedback
related_bug: BUG-0044-requirement-stage-premature-transition-session-split
related_requirements:
- REQ-0047-governance-command-durable-recovery
- REQ-0027-requirement-center-command-chain-realization
product_data_collection_observability:
  status: applicable
  affected_layers:
  - api
  - request_logs
  - task_traces
  - task_trace_spans
  - web
  reason: 治理操作准备、阶段持久化、恢复与完成确认需要关联操作、轮次、对象及可信结果。
  validation: 后续验证预检失败、服务重启、重复恢复、并发冲突和结果同步的脱敏链路；本次仅记录，不改变 schema、API、部署、保留周期、对象存储或客户端生成物，以上实现变更本轮
    N/A。
discovered_at: '2026-10-19 13:57:27'
root_cause_status: confirmed
---

# 评审恢复记录缺失导致成果未应用与卡片未流转

## 现象

REQ-0046-chat-execution-output-status-feedback 在产品 Chat 执行 req-review，助手输出工作区评审通过及同步无差异；产品却显示轮次失败，评审未形成成功应用，需求中心仍处于待评审。助手文本不构成后端完成事实。

## 环境与触发条件

- 本地 MoonBox Web /chat、/requirements，Chrome；故障轮次开始于 2026-10-19 13:57:27（Asia/Shanghai）。
- 对象评审前为 pending_review / plan，候选使用 source 工作区；数据库与私有恢复记录仅作聚焦只读检查。
- 本轮容器检查：backend、chat-worker、governance-controller 分别于当日 08:59:03、08:59:09、08:59:09 启动。新解释器导入时，backend 与 chat-worker 的 preparation 模块文件摘要一致；这不代表长期运行进程内存或故障发生时的模块版本一致。
- 禁止在真实业务记录中删除 operation.json 制造故障；机制复现采用临时隔离目录与虚构对象。

## 复现步骤

### 已发生产品案例核查

1. 打开目标需求的原 req-review 会话，查看失败轮次及助手工作区输出。
2. 对照 chat_turns、governance_candidates、governance_applications 的聚焦只读结果。
3. 根据轮次推导对应命令基线记录目录，检查 baseline.json 与 operation.json 的完整性。
4. 刷新需求中心，对照目标 trace.md 的 status、lifecycle_stage、reviewed、approved。历史观察为 pending_review / plan，评审时间为空。

### 隔离机制复现

1. 从仓库 HEAD 版本与当前工作区的 direct_command_journal.py 用 AST 提取 DIRECT_ACTIONS、record_id、prepare、completion_block_reason；仅替换存储为临时目录适配器，不连接业务库。
2. 写入虚构 req-review baseline，调用 HEAD 的 prepare：operation 不存在。
3. 调用当前 completion_block_reason：返回 direct_command_recovery_blocked。
4. 对照调用当前 prepare 后再检查：operation 存在，completion_block_reason 返回 None。

本探针验证特定名单兼容机制，不是完整 HTTP、模型执行或产品恢复验收；临时文件随探针退出清理，源码和测试文件未修改。

## 期望与实际

| 项目 | 期望 | 实际证据 |
|---|---|---|
| 准备记录 | 后续收尾所需记录在执行前准备完整，兼容历史基线 | 目标目录只有 baseline.json |
| 结果判定 | 业务校验、应用及回读一致后确认成功 | 轮次 failed，错误 direct_command_recovery_blocked |
| 事实源 | 成功评审进入 approved / review；失败不伪造成功 | 当前案例保持 pending_review / plan，无成功应用记录 |
| 诊断 | 保留具体准备或恢复错误及关联阶段 | 候选错误归类为 executor_unavailable，UI 提示笼统 |
| 成果处理 | 可信成果可核查，安全恢复前核对版本和权限 | 原始输出和 Diff 存在；完整成果可恢复性尚未验证 |

## 影响范围与严重度

severity: high。已证实一个 req-review 样本被阻断，影响评审流转并可能诱发重复执行。尚未证明所有评审、bug-review 或其他命令都受影响，也未证实数据丢失。通用恢复能力独立归属 REQ-0047-governance-command-durable-recovery；展示归属 REQ-0046-chat-execution-output-status-feedback，不扩展为本次正式功能实现。

## 根因状态与证据

root_cause_status: confirmed

本次 bug-complete 已补证：实际部署 backend/chat-worker 的 DIRECT_ACTIONS 均不包含 req-review，prepare 静默跳过 operation；同一部署模块的收尾函数却要求读取该文件。真实函数隔离探针得到 operation_exists=False 与 direct_command_recovery_blocked，解释原轮次失败。完整证据、排除假设与结论边界见 root-cause.md。

此前 probable 表示当时仅有历史代码探针，现已被实际部署证据更新。当前工作区名单扩展尚未进入部署，不据此声明修复完成。历史成果恢复及正式修复回归仍待执行。

## 建议验收与关联边界

- 记录缺失在执行前被明确识别；无法安全恢复时阻断且不虚假完成。
- 正常评审的目录、主状态、生命周期、应用记录、Chat 结果与看板一致。
- 完成前服务中断或应用响应丢失后，成果可核查；重复恢复不重复迁移。
- 并发改动与权限变化得到明确拒绝，已有成果和诊断不丢失。
- 不重复实现 BUG-0044 的对象互斥与完成门禁；与该历史修复建立关联而不修改其归档事实。
- 已完成评审并纳入 sprint-010，关联 fix-review-recovery-operation-record-missing（proposed）；未开发或部署。

## 数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: API、Chat 轮次、治理候选、请求日志、Task Trace、恢复记录与 Web 结果关联。

validation: 已取得聚焦脱敏数据摘要与隔离机制探针；实施后需验证准备、收尾、恢复的原始错误及版本关联。当前仅文档生成，API、DB schema、UI、部署、安全策略、对象存储和客户端生成均未改变；这些实现同步本轮 N/A。
