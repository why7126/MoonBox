---
title: 独立 Change 优先级交付追溯
created_at: '2026-10-31 21:27:39'
updated_at: 2026-10-31 21:48:52
change_id: add-standalone-change-priority
requirement_id: REQ-0057-standalone-change-priority
status: applied
iteration: sprint-018
product_data_collection_observability:
  status: applicable
  affected_layers: [web, api, governance, usage_events, request_logs, task_traces, task_trace_spans]
  reason: 分级保存复用异步控制器及既有Task Trace；必要审计与priority同文件提交，无新增表或迁移。
  validation: 权限、版本、必要审计、遥测故障回归及隔离真实HTTP回读通过，证据边界见verification.md。
execution:
  schema_version: 1
  started_at: 2026-10-31 21:28:38
  completed_at: 2026-10-31 21:48:52
  last_event: opsx.apply
---

# 独立 Change 优先级交付追溯

## 来源与状态
REQ-0057-standalone-change-priority；sprint-018；实施完成，12项任务完成，20项自动验收通过。
原型：../../../issues/requirements/review/REQ-0057-standalone-change-priority/prototype/web/prototype.html，拆解见同目录context.md。
冲突处理与UI Contract见design.md；Skeleton已确认；双视口关键交互截图、computed style和最终一致性已完成；原型Mock，生产使用真实API。无PNG输入，不伪造截图。
## 验证摘要
20项自动验收通过，证据位于evidence/acceptance；真实产品只读观察与隔离HTTP编辑回读的边界见verification.md。


## 历史实施入口检查点

已执行 opsx.start，Sprint解析为sprint-018，保持研发中；12项任务均未勾选，尚未修改本需求业务代码。

任务1.1发现设计与现有安全边界实质冲突：writer.py 的 maintenance/write_permission 要求文档类写入存在服务端维护窗口；enqueue_document及控制器执行阶段均拒绝独立Change通用文档写入。现有控制器是异步持久化模型，project_lock仅协调已登记writer，不能保护任意外部编辑器。设计中同步保存不能直接复用该链路，更不能用新API绕过维护窗口。

待确定：推荐保留维护窗口及异步控制器，新增限于priority的受控操作，前端等待完成并回读；另一方案为日常即时保存，需要先补外部writer协调和权限边界设计。该决策影响API响应、保存状态机、观测Task Trace、可编辑能力与验收，先完成任务1.1再确定骨架及其余实现。
已向用户发送结构化选择；未把现有独立文档只读限制直接放宽。恢复后先更新design、spec和REQ一致性，再实施。既有工作区修改保留，不覆盖其他交付。

## 历史异步方案实施进展
用户已确认保留维护窗口与异步控制器，原保存方式决策已解除。新增change-priority窄操作，控制器复核来源、版本及写集；通用文档只读未放宽。PUT接口与OpenAPI/Orval已生成，卡片投影增加分级状态/版本，写权限禁用由服务端控制。实现仍未完成，不作applied同步。
已完成合成验证：分级规划/审计/同值/冲突/归档拒写，真实控制器入队执行及维护窗口拒绝；与交付卡回归共16项通过。此结果不是浏览器真实产品验收。
UI Skeleton已在本地Vite预览并用Playwright采集1440×900浅色截图，证据evidence/skeleton/1440-light.png。纯合成静态样本，未接API；首轮人工结构确认已请求，尚待回复。UI细节、筛选、遥测、完整回归及真实产品验收仍待执行。

## 完成验证摘要
用户确认的异步与UI方案已实现。后端9项聚焦、writer/交付既有回归、前端4项聚焦及既有8项组合、TS/Vite构建通过。最终视觉和隔离HTTP证据见verification.md。全仓DS历史残留单独报告，本次组件聚焦无违规。完成态及自动验收以后续Workflow Sync和manifest为准。
