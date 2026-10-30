---
bug_id: BUG-0057-requirement-card-chat-navigation-latency
title: 需求卡片动作准备会话导致进入聊天工作台等待过长
severity: high
status: done
root_cause_status: confirmed
owner: 产品团队
created_at: '2026-10-21 09:17:44'
updated_at: 2026-10-31 06:31:25
discovered_at: '2026-10-21 08:50:06'
environment: local
source: capture、用户提供的浏览器截图与同会话容器只读采样
related_requirement: null
related_change: fix-object-session-preparation-latency
iteration: sprint-016
---

# 需求卡片动作准备会话导致进入聊天工作台等待过长

## 现象与范围

需求中心治理卡片动作在进入 Chat 工作台前等待过长。已取得 BUG 对象执行 bug-opsx 动作的真实样本：POST /api/v1/chat/object-sessions 返回 200，Waiting for server response 为 21.27 秒，响应下载仅 4.39 ms。响应为 reused_conversation=true、execution_state=idle、can_send=true，说明复用已有会话也存在准备延迟，并非该样本在创建新会话或执行 Agent 命令。

本 BUG 覆盖点击动作至准备返回、路由切换的阶段；进入后的历史加载属于 BUG-0058，消息提交 POST /conversations/.../turns 属于 BUG-0059，不混用它们的时长。截图中的对象 BUG-0055 是采样业务对象，不是本缺陷的修复链路。

## 复现步骤与结果

1. 在本地需求中心选取已满足 bug-opsx 前置条件、已有对应会话的 BUG 对象；保留 DevTools Network 记录。
2. 点击该对象的治理动作，观察 POST /api/v1/chat/object-sessions；本次用户提供样本的 action 为 bug-opsx。
3. 记录点击、请求发出、响应完成、路由切换、聊天页面可交互时刻；查看 Timing、状态码和脱敏响应。
4. 实际：该 POST 等待响应 21.27 秒，成功返回已有空闲会话。前端在请求成功后才执行 pushState，因此准备等待处于导航关键路径。截图不包含完整点击至可交互计时，不能将 21.27 秒当作全部页面加载时长。
5. 期望：及时反馈准备状态，在保留权限、版本和执行占用门禁的前提下减少不必要的重复准备，尽快进入正确会话。量化性能门槛以已批准review.md为准，不把目标当成部署保证。

历史21.27秒事件仅有一个完整截图；后续同请求自然计时和修复对照另行编号，不冒充该历史请求的精确复现。

## 当前结论与证据入口

root_cause_status: confirmed。确认同步重复快照读取处于导航关键路径；当前自然请求两条快照占97.40%/96.93%，历史bug-opsx准入重构支持机制可复现。历史21.27秒精确占比、唯一性和数据库等待未知，不外推当前比例。

完整E1–E16证据索引、确认边界及剩余未知见 [根因分析](root-cause.md)。此前微基准、诊断过程、各阶段probable判断和计时表完整保留于 [调查历史原文](investigation-history.md)。当前同请求计时已补齐；不再作为待补任务。

## 影响范围与严重等级

severity: high。核心治理入口存在 21 秒级等待，影响用户进入聊天并继续研发工作。当前直接样本为已有会话的 bug-opsx；其他写动作共享部分准备路径，但需分别验证。无数据丢失、安全事故、全站不可用或必须紧急上线的证据，建议常规修复。

## 修复方向与回归建议

优先评估单请求复用已验证快照，减少入口与预检重复全树读取；保持写入围栏、源/投影版本一致性、权限、对象阶段、占用及幂等约束。评估 reconcile 是否可以收窄到目标对象，同时防止遗漏跨对象恢复义务；前端准备反馈只能改善可感知性，不能替代性能修复。

后续回归覆盖已有/新会话、只读/写动作、执行占用、版本推进和持续变更、无权限、失败重试、重复点击；验证不会重复创建会话、绕过门禁或错配命令草稿。点击至路由、接口准备、路由至历史可见分别计时；同规模多样本验证性能，不能用一次微基准替代接口验收。

## 关联与观测声明

BUG-0056、BUG-0058、BUG-0059为邻接问题，共享路径不等于共同根因。BUG-0057已纳入sprint-016，状态in_sprint，修复Change为fix-object-session-preparation-latency（当前实施与验收事实见Change trace）。本轮评审授权更新生命周期；既有治理归档不代表本BUG修复。

product_data_collection_observability: applicable；affected_layers: Web、API、request_logs、Task Trace诊断；validation: 当前两条自然请求身份关联、分段计时与历史准入正反例已取得，临时诊断已恢复。公开API、DB schema、安全权限、对象存储及客户端生成不变；内部读取调度、SQLite准备Trace写顺序及Web取消等待已调整，临时验证部署已恢复。

实现及性能/正确性自检已完成，正式修复验收状态见 [验收计划](acceptance.md)。

## 缺陷完善复核

已按归档规则明确机制确认范围、剩余未知及重启调查条件，修复验收计划补齐环境可比性、性能目标制定和正确性门禁。详细内容分别维护于root-cause.md与acceptance.md，不重复历史采样。完善材料齐备不代表修复验收或已获评审授权；本轮已授权评审，结论及性能目标见review.md，当前已纳入sprint-016，状态in_sprint。


## 本轮实现结果

暖态固定原路由中位数从6520.795ms降到1595.880ms；冷态中位数3194.204ms，3并发30请求无新增SQL错误、5xx或重复会话。自然浏览器10次暖态准备中位数1955.131ms、最大3580.169ms，点击至路由观察上界中位数2070ms、最大3707ms。历史加载单列，不纳入本BUG目标。详见[修复验证记录](../../../../openspec/archive/2026-10-30-fix-object-session-preparation-latency/verification.md)。原运行服务已恢复，代码交付与正式发布分开。


## 最新本地部署观察

2026-10-30：用户授权的本地服务已更新且健康正常；10次有效自然导航中位数5.36秒、最大8.53秒，性能未达原目标。旧通过记录仅代表原固定/临时窗口，当前等待性能复验，不推进归档。运行版本、回滚与完整样本见[部署记录](../../../../openspec/archive/2026-10-30-fix-object-session-preparation-latency/deployment.md)。

## 2026-10-30 快速打开返修当前范围

按用户授权在原 BUG / Change 实现“快速打开，发送时最终检查”。卡片只携带草稿意图进入 Chat，open-chat 保留读取权限但不做写准备；发送请求在入队前重新执行完整协调、新鲜度、权限、阶段、Sprint、占用及候选检查。生成候选绑定实际打开的会话，失败保留草稿，重试沿用幂等身份。旧版本性能及交互记录保留为历史证据，不替代当前版本复验。历史21.27秒请求精确归因仍为未知，限定机制确认不扩大。

Sprint 容量仍30人天，其他任务不调整；本项5→8人天，总估算32/30（106.7%），属于允许记录风险的区间，并非硬阻塞。超额带来延期风险，不能解释为已保证30人天完成。
