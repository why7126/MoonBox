---
bug_id: BUG-0066-chat-auto-verification-status-stale
title: Chat 自动核验状态未持续刷新导致结果待核验提示滞留
status: done
severity: medium
created_at: '2026-10-26 18:01:50'
updated_at: 2026-10-30 08:33:55
environment: local docker chat-platform
owner: 产品团队
source: 用户双条 bug-capture 授权及同会话只读探索
related_requirement: null
related_bug: BUG-0052-verified-result-execution-guard-not-released
lifecycle_stage: archive
root_cause_status: confirmed
---

# Chat 自动核验状态未持续刷新导致结果待核验提示滞留

## 现象与影响

用户在治理命令结束后看到“结果待核验”，疑惑是否每次还需人工点击。初判 medium：误导用户重复核验，现有样本最终核验成功，无证据表明业务成果丢失。

## 复现步骤

1. 在本地 Docker Chat 观察 BUG-0056-requirement-center-context-load-latency 的 sprint-propose 轮次完成状态。
2. 保持页面打开，观察自动核验期间和完成后的状态变化，不重新发送治理命令。
3. 将页面状态与对应自动核验队列、执行保护状态及时间关联；后续用受控延迟验证首次查询返回 needs_review 后的更新。

## 期望与实际

期望：正常流程自动核验，页面及时反映进度与最终结果；失败或证据不足时才展示具体原因及人工重试入口。
实际：截图显示结果待核验；后续浏览器已显示成果已核验。只读队列为 confirmed、attempt_count=1、reason_code=null，执行保护为 validated。自动队列登记时间 2026-10-26 17:51:07，保护更新时间 17:51:18，页面最近核验为 17:51:22。

## 证据与根因边界

复用本会话用户截图、Chrome /chat 观察、聚焦 SQLite 只读查询和源码分析，不复制原始业务记录。

- E1：截图为结果待核验，后续页面为成果已核验；不能以先后观察证明截图瞬间后端已经完成。
- E2：governance_completion_handoffs 对应轮次自动核验 confirmed 且一次成功；不是必须人工核验的设计证据。
- E3：src/web/src/components/chat/DirectCompletion.tsx 的 useEffect 只在加载/URL变化时 GET，未订阅自动完成或持续刷新；POST 由核验按钮触发。
- E4：src/backend/app/governance/controller.py 每约10秒调用 completion_handoff.tick，直接命令有自动核验队列。

前端持续更新机制缺口 confirmed；该样本截图时间、请求时序、人工动作与后端完成之间的精确因果尚待补证，完整根因保留 probable。不能声称用户必然点击过或自动核验失败。需补充受控延迟下 GET 时间、状态转换和页面文本，不采集认证头。

## 判重与关联

BUG-0052 已归档，处理后端成果已核验但执行保护未解除；本样本后端为 validated，修复面是前端状态跟进。BUG-0058 为历史请求放大，采用有界刷新时需协同避免增加历史轮次无界轮询；BUG-0060 为完成证明失效，本次未见该失败证据。因此独立记录。

## 建议验收

覆盖首次 needs_review 后自动 confirmed 无点击更新、失败原因与人工重试、权限变化、卸载取消、请求去重、历史终态不轮询；核验不重新执行模型或业务命令。明确自动处理中与需人工处理的状态区别。

## 数据采集与链路观测

product_data_collection_observability:
- status: applicable
- affected_layers: Web、API、DB、Agent Workflow
- reason: 涉及输出持久化或核验读取链路；本次仅记录，不修改接口、表结构、日志或埋点；对象存储与部署变更暂无依据。
- validation: 同会话页面、只读统计及代码路径证据；未执行修复回归。

## 附件边界

截图沿用用户会话附件，仅记录脱敏结论；未复制附件或原始日志到仓库。
