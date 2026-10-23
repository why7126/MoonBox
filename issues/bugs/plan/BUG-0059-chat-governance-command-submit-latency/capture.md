---
bug_id: BUG-0059-chat-governance-command-submit-latency
title: 聊天治理命令同步准备导致消息提交等待过长缺陷记录
status: captured
created_at: '2026-10-21 08:50:06'
updated_at: '2026-10-21 08:50:06'
severity: high
environment: local
owner: 产品团队
source: 用户授权与同会话 explore 证据
related_requirement: null
related_bug: null
root_cause_status: probable
lifecycle_stage: plan
---

# 聊天治理命令同步准备导致消息提交等待过长缺陷记录

用户第 4 项：消息提交异常慢；用户进一步明确主要发生于 /opsx-*、/req-* 等治理命令。普通文本是否受影响尚未确认，暂不扩大范围。

## 已确认的证据

| 编号 | 类型 | 来源 | 事实及确认边界 |
|---|---|---|---|
| E1 | user_report | 本会话用户结构化补充 | 慢发送主要是治理命令，不是已确认普通文本普遍慢。 |
| E2 | code_path | src/web/src/components/chat/Composer.tsx，submit | 等待 POST /conversations/.../turns 成功后才清空草稿、调用 onSubmitted；新会话先串行创建会话。 |
| E3 | code_path | src/backend/app/chat/service.py，request_turn | prepare_command_snapshot、check_send 在 enqueue 前同步执行；不能把受理前等待全算为模型生成时间。 |
| E4 | code_path | src/backend/app/governance/preparation.py，_send_baseline、_preflight_object_session、prepare_command_snapshot | 写命令预检取得快照，随后再次 reader.snapshot 对比版本；每次 stable 内双读取，失败可最多三次尝试，并保存治理基准后继续。具体命令分支需运行时确认。 |

## 根因判断

probable：同步准备和重复快照是强推测，调用顺序已确认，但未采集慢发送 POST 或服务端分段计时。本轮没有实际发送测试消息，不能确认哪个步骤主导耗时，也不能套用看板 27 秒作为发送时长。

## 判重与拆分

BUG-0045 是执行环境缺少验收能力，BUG-0046 是执行中缺少回答续接入口，均非提交时延。与卡片导航时延共享潜在准备成本，但发生在独立提交接口，涉及受理、幂等及失败草稿的独立闭环。

## 复现与期望

1. 在允许的测试会话或下一次自然提交时输入治理命令。
2. 记录点击发送、POST 发出、响应、用户气泡出现、入队、Agent 首次输出时刻。
3. 期望及时反馈受理/准备状态，失败保留草稿；实际用户报告提交前等待异常长。

## 待补证与验收建议

记录命令族、已有/新会话、部署版本、请求状态、Waiting、总耗时、request_id；服务端分段覆盖对象解析、快照读取次数与耗时、版本重试、基准保存、门禁及 enqueue。用同等数据规模下普通文本作对照，区分受理延迟与首输出延迟。后续验收验证快照复用的一致性、并发写入、幂等重试、重复点击、失败草稿保留及受理反馈，不以跳过授权/版本/执行占用检查换性能。

## 证据归属与边界

证据复用同会话 2026-10-21 浏览器工具结果与源码只读检查；本次 capture 未重新计时。运行态样本未保存 HAR/截图文件，以上为脱敏观察摘要，不伪称已有附件。代码行号可能变化，按文件与函数定位。浏览器 DOM 只读接口不支持 performance，已改用 Chrome 原生 DevTools 取证；未因单工具失败判定服务不可用。

后续补证优先自主浏览器与服务端可用观测；涉及创建会话或执行命令的采样使用明确测试对象或用户自然操作。返回格式：环境/版本、动作、脱敏路径、状态码、总耗时、Waiting、阶段计时、样本规模；禁止凭证、原始消息/文档、个人标识及本机路径。

## 严重等级与观测声明

初判 high：核心研发入口出现明显长等待，影响日常连续操作；无数据丢失、安全事故或全站不可用证据，不提升为 critical/blocker。

product_data_collection_observability:
- status: applicable
- affected_layers: Web、API、request_logs、Task Trace
- reason: 性能定位涉及请求等待及治理步骤计时；本次只记录 BUG，不改变埋点或日志契约。DB 索引/结构、对象存储和部署变更尚无证据支持，暂不提出修改。
- validation: 同会话浏览器观察与聚焦代码路径；未执行修复或性能回归，剩余计时见待补证。

