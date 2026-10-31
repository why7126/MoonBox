---
bug_id: BUG-0045-chat-acceptance-runtime-capability-gap
title: Chat 自主验收能力缺口修复评审
created_at: '2026-10-21 16:24:14'
updated_at: '2026-10-21 16:24:14'
reviewed_at: '2026-10-21 16:24:14'
review_result: approved
severity: high
owner: 产品团队
related_requirement: REQ-0025-chat-workbench
related_requirements:
  - REQ-0044-shared-project-verification-environment
  - REQ-0048-chat-isolated-acceptance-orchestration
---

# Chat 自主验收能力缺口修复评审

## 评审结论

用户明确批准修复，维持 high，Readiness 为 Ready，采用常规 fix。无已证实的数据损坏，不采用解除执行隔离的 hotfix。本次仅评审通过，未纳入 Sprint、未创建 Change、未开发或验收。

## 评审依据

- 根因充分：bug.md、root-cause.md E1–E8 已确认测试依赖供应、验证 worker 部署与项目绑定、执行前预检及调用链缺口；本会话复核代码与 Docker 清单支持该判断。
- 严重度合理：阻断产品开发验收闭环，迫使用户切换桌面环境；不泛化为所有部署不可用。
- 验收明确：现有 AC-001—010 覆盖能力预检、Python、前端平台依赖、浏览器、同操作调用回传、局部恢复、异常、安全和真实部署闭环。
- 证据边界：历史 AnyIO 超时不归并为已确认根因；静态、合成测试与真实浏览器证据分开记录。

## 批准范围与拆分

本 BUG 负责启用并正确配置 REQ-0044 的验证能力、锁定 Python/前端测试依赖、Chat 受控调用与证据回传、前置能力预检、局部阻塞和原操作下的验证续接。浏览器使用获授权且可核对版本的既有目标，不给执行容器开放任意网络或 Docker socket。

新增能力由关联需求 REQ-0048-chat-isolated-acceptance-orchestration 承接：独立 MySQL、本轮代码快照的测试应用编排、短期测试身份、环境编排检查点与原操作关联、租约及资源回收。BUG 可针对预配置目标独立验收；完整自动供应环境的闭环由新需求验收，不将未交付的新能力计入本 BUG 完成证明。

BUG-0046 继续负责人工提问、回答提交与回传；REQ-0047 的身份、幂等和检查点原则可复用，不声称其已支持完整验收恢复。轮次已终止时保留原终态，以关联续接尝试继续；用户主动停止后不自动恢复模型。

## 数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: Chat 执行器、验证任务 API、Web、请求日志、Task Trace。validation: 按 AC-001/005/007/009/010 核对项目、操作、轮次、任务及输入指纹关联和证据授权。禁止记录凭证、完整 Prompt、页面正文。本次仅文档评审，API、DB、UI、部署、安全策略、客户端生成变更均 N/A；实施时按实际影响同步。

## 后续门禁

先执行 /sprint-propose --bug BUG-0045-chat-acceptance-runtime-capability-gap，成功纳入后才进入 bug-opsx。新需求独立完善、评审和排期。

## 校验说明

根因证据校验通过，8项证据；Workflow Sync check 无状态漂移。子文档扫描对 root-cause.md 的 status: confirmed 提示语义待人工核对；已确认它表示根因确认状态，保持原值，不替换为 Issue 的 approved。新需求当前仅 capture，正式验收文档缺失符合当前阶段，不代表已通过验收。
