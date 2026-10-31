---
bug_id: BUG-0046-chat-midrun-question-response-unavailable
title: Chat 命令执行中提出问题但缺少可回答和续接入口
status: done
created_at: '2026-10-19 11:24:41'
updated_at: 2026-10-31 12:30:14
severity: high
environment: 产品 Chat 执行器；具体部署版本待核对
owner: 产品团队
source: 用户截图、同会话续接记录及本次 bug-capture
lifecycle_stage: archive
related_requirement: REQ-0025-chat-workbench
related_bug: BUG-0045-chat-acceptance-runtime-capability-gap
---

# Chat 命令执行中提出问题但缺少可回答和续接入口

## 现象

产品 Chat 命令执行途中，助手要求用户选择提供测试环境或保留验收阻塞；截图中问题及选项作为部分输出正文出现。用户反馈无法回答，执行过程因此无法通过产品交互继续。

## 复现步骤

1. 在产品 Chat 执行需要用户补充环境信息的授权命令；本次来源为 BUG-0028 的 opsx-apply。
2. 在执行中观察助手提出的测试入口问题及两个选项。
3. 检查是否有可提交的选项、补充说明及回答确认；尝试从产品已有输入区回答。
4. 核对回答是否关联原问题、原轮次并实际恢复执行，而非创建不相关的新任务。步骤3、4的具体事件与接口结果待探索补证。

## 期望与实际

期望：提问具有可操作的回答入口，回答绑定正确问题并续接；不支持交互时应明确限制及可执行替代路径，不能展示无法完成的选择要求。
实际：截图可确认文字问题和选项，用户反馈无法回答；尚不能单凭截图判定是控件缺失、执行中输入被禁用、桥接不支持还是答案回传失败。

## 影响、严重度与边界

high：需要用户决策的命令无法在同轮正常闭环，可能诱发重复命令。尚未确认执行器死锁或数据丢失。本条独立覆盖提问呈现、回答提交与续接，不负责补装验收依赖，也不重做执行终态提示。

## 建议验收

覆盖选择题与补充说明、等待回答状态、回答回传、断线重连、刷新后待答问题恢复、超时/取消及能力不支持分支；回答不重复提交、不串会话，不因执行中状态封禁唯一回答入口。运行结束与任务完成表达关联 REQ-0046，避免重复实现。

## 判重结论

BUG-0030 已归档，解决助手正文缺失，本次正文可见而回答不可操作；BUG-0044 处理阶段迁移、会话分裂，与问答桥接不同；REQ-0046 处理过程输出和结果状态，不覆盖问题回传。可独立建单并建立关联。

## 来源与证据边界

用户本会话提供的截图及反馈，来源命令 /opsx-apply BUG-0028-requirement-center-card-owner-raw-user-id；来源 Change fix-requirement-center-owner-display、Sprint sprint-010 仅用于复现关联，本 BUG 未评审、未纳入 Sprint。截图未复制入仓库，避免保留原始聊天内容；未创建 root-cause.md 或确认根因。BUG-0028 后续桌面验收通过不代表产品执行器问题已修复。

## 数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: Chat 执行器、Web 交互、命令事件/API 和 Task Trace 关联诊断。

validation: 后续按同会话、同轮次核对能力检查或问题回答事件及恢复结果，保存脱敏摘要；当前仅 Capture，无代码、API、DB、部署、客户端生成或日志采集策略变更，以上变更 N/A。
