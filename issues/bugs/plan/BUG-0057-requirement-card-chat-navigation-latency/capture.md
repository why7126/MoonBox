---
bug_id: BUG-0057-requirement-card-chat-navigation-latency
title: 需求卡片动作准备会话导致进入聊天工作台等待过长缺陷记录
status: enriching
created_at: '2026-10-21 08:50:06'
updated_at: '2026-10-21 09:22:50'
severity: high
environment: local
owner: 产品团队
source: 用户授权与同会话 explore 证据
related_requirement: null
related_bug: null
root_cause_status: probable
lifecycle_stage: plan
---

# 需求卡片动作准备会话导致进入聊天工作台等待过长缺陷记录

用户第 2 项：需求中心卡片动作点击后，进入 Chat 工作台异常缓慢。归因边界是点击至路由切换，不包括进入后的历史加载与发送命令。

## 已确认的证据

| 编号 | 类型 | 来源 | 事实及确认边界 |
|---|---|---|---|
| E1 | user_report | 本次用户反馈第 2 项 | 点击卡片按钮后长时间才响应；具体动作与耗时尚未量化。 |
| E2 | code_path | src/web/src/pages/catalog/RequirementCenterPage.tsx，openIssueActionDialog | 普通动作先 POST /api/v1/chat/object-sessions，部分采集池生成动作先 POST /api/v1/chat/governance-preparations；收到结果才 pushState 跳转。 |
| E3 | code_path | src/backend/app/governance/preparation.py，prepare_object_session、_preflight_object_session、prepare | 会话准备涉及对象解析、执行保护与阶段预检；写入动作包含快照/执行器一致性校验。只读动作分支不同，不能断言所有按钮都扫描完整快照。 |
| E4 | reproduction | 同会话 Chrome 需求中心已完成对象的“查看执行”入口 | 该入口能够直接导航到已有 Chat。代码 viewExecution 直接切路由；这不证明普通动作按钮响应正常。 |

## 根因判断

probable：同步会话准备阻塞路由切换，与用户现象吻合；缺少慢按钮对应 POST 的 Timing，尚不能认定主要成本在快照、数据库或执行器检查。未为探索触发会话创建或治理准备写入。

## 判重与拆分

BUG-0031 是跳转后 Skill 标签缺失，BUG-0044 是阶段提前迁移和会话分裂，与本条时延修复面不同，仅弱相关。与命令发送问题可能共享快照成本，但入口、事务、幂等与验收闭环不同，独立记录，不预设共同根因已确认。

## 复现与期望

1. 使用允许测试的非生产对象，记录卡片阶段、按钮名称及动作类型。
2. 点击普通治理动作，记录点击、准备请求发出/返回、路由切换和页面可交互时刻。
3. 与“查看执行”直接导航对照；期望及时给出准备状态并进入正确会话，实际用户报告长时间无有效响应。

## 待补证与验收建议

下次自然操作或获授权的测试操作中采集两种准备接口的状态码、Waiting、总耗时、request_id 和服务端预检阶段耗时；不重复提交真实治理动作以获取样本。分别覆盖只读分析、写入准备、已有会话、新会话、执行占用分支。验证会话不重复创建、权限与占用门禁保留，点击至导航与导航至历史显示分别计时。

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

