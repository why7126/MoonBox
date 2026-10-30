---
bug_id: BUG-0066-chat-auto-verification-status-stale
title: Chat 自动核验状态未持续刷新导致结果待核验提示滞留
status: done
severity: medium
created_at: '2026-10-26 18:11:49'
updated_at: 2026-10-30 08:33:55
environment: local docker chat-platform
owner: 产品团队
source: 用户双条 bug-capture 授权及同会话只读探索
related_requirement: null
related_bug: BUG-0052-verified-result-execution-guard-not-released
lifecycle_stage: archive
root_cause_status: confirmed
discovered_at: '2026-10-26'
related_change: null
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

## 本次生成补证

2026-10-26 再次自主查看 Chrome 本地 /chat 原会话，当前为成果已核验，最近核验仍为 17:51:22；不点击核验或重放业务命令。

| 证据 | 来源 | 脱敏结果 | 判断 |
|---|---|---|---|
| E5 | TurnActivity.tsx::poll | completed/failed/stopped 且批次不满 200 后停止轮询 | 执行结束后的核验变化没有由父轮询持续承接 |
| E6 | DirectCompletion.tsx::useEffect | 首次 GET；依赖 read/url，不依赖自动核验事件或定时器 | 初次 needs_review 可以一直保留，展开切换不重新请求 |
| E7 | direct-completion.test.tsx | 既有测试覆盖按钮 POST、读取失败重试及历史状态，没有自动状态转换无点击刷新用例 | 现有覆盖不足；本次仅读测试，未声称运行通过 |
| E8 | 前序只读队列与本次当前页面 | 后端 confirmed、一次成功，当前页面已核验 | 不应把问题描述成每轮必需人工批准 |

根因状态：probable。前端没有自动状态跟进的代码缺口已确认；截图瞬间的 GET 返回时间、用户操作与后端完成先后仍缺直接证据。现有成功终态无法倒推旧页面何时刷新，也不确认用户是否点击过按钮。自动队列创建晚于正文显示的原因不在本次证据范围内，不声称正常自动核验只需固定秒数。

## 修复范围建议

将执行终态与核验终态分开跟踪：自动核验待处理时有界刷新或订阅，成功后终止，失败展示原因与人工重试。请求去重、取消、权限失败终止和历史终态不重复拉取，与 BUG-0058 的性能目标协调。保留服务器校验和人工兜底，不通过前端把 completed 当作成果成功。

## 后续最小补证

已完成浏览器当前状态、后端队列事实、父子组件生命周期和既有测试检查。历史截图缺少准确请求时间，当前页面已成功，不能只读回到旧响应。后续 bug-complete 使用隔离模拟接口：首次 GET needs_review、延迟变 validated，保持挂载且无点击，记录请求数、状态回调及页面标签；再验证失败/卸载/权限情况。若需真实运行证据，用户自然执行下一次治理命令时在 Network 保留 completion-verification 请求时间、方法、状态码和脱敏 state/reason_code，与页面录屏时间对齐；不导出 Cookie、Token、原始正文或完整 HAR。返回时间线表即可，无需重跑当前业务。

## 补齐结论

本次隔离复现已确认机制缺陷，前文 probable 为生成阶段历史判断，以 [根因分析](root-cause.md) 为当前结论；历史样本未证实部分仍保留，不扩张为全链路已确认。
