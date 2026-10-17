---
title: 需求中心卡片全命令产品链路真实化提案
change_id: add-requirement-center-command-chain-realization
source_requirement: REQ-0027-requirement-center-command-chain-realization
change_type: add
created_at: 2026-09-30 18:06:35
updated_at: 2026-09-30 18:06:35
owner: MoonBox 产品团队
---

# 需求中心卡片全命令产品链路真实化提案

## 背景

需求中心卡片已经承载需求分析、生成需求、完善需求、评审、加入迭代、生成 OpenSpec、开始开发和完成归档等生命周期入口，但仅打开 Chat、发送命令文本或展示成功消息，不能证明治理文件、Workflow Sync、Sprint、Change 和执行事实已经真实写入并可恢复。

本变更将 REQ 卡片八类动作收敛为受控产品链路：前端入口只触发明确动作，后端按对象身份、权限、阶段、材料、幂等和 Workflow Sync 逐步裁判，成功必须以事实源重读为准。

## 变更内容

- 为需求中心 REQ 卡片八类动作建立统一的真实执行契约，区分只读分析、写操作受理、运行、部分写入、同步失败、完成和恢复。
- 扩展需求中心卡片动作的后端 controller 或等价受控分发器，要求完整 REQ ID、授权项目、版本和动作白名单校验。
- 将七类写操作的成功条件绑定到产物校验、Workflow Sync 成功和事实源重读，禁止仅凭 Chat 消息或请求受理推进状态。
- 为评审、加入迭代、生成 OpenSpec、开始开发和完成归档补齐弹窗/反馈容器、门禁摘要、取消语义、幂等与失败恢复要求。
- 承接 prototype/web 原型拆解，在 Change 设计中固化 UI Contract、UI Skeleton、动作按钮矩阵、computed style 采样和 1440px 视觉验收门禁。
- 补齐产品数据采集与链路观测声明，覆盖 usage_events、request_logs、task_traces 和 task_trace_spans，要求脱敏、直接 API 不伪造行为事件、Workflow Sync 失败阻断完成。

## 能力影响

### 新增能力

无。本变更扩展既有需求中心、Chat 工作台和 Agent Workflow 治理能力，不创建独立 capability。

### 修改能力

- `web-catalog-requirement-center`：扩展 REQ 卡片八动作真实执行、阶段门禁、反馈、幂等、恢复和 UI 原型验收要求。
- `web-catalog-chat-workbench`：扩展只读分析入口、动作反馈与脱敏观测边界，确保 Chat 不提升治理写权限。
- `agent-workflow-tooling`：扩展 req-opsx 后的 execution schema、opsx.start/apply/archive 投影和 prototype 门禁追溯要求。

## 影响范围

```yaml
impact:
  backend: true
  web: true
  miniapp: false
  admin: false
  database: true
  storage: false
  api: true
change_type: add
capabilities:
  new: []
  modified:
    - web-catalog-requirement-center
    - web-catalog-chat-workbench
    - agent-workflow-tooling
```

- Web：需求中心 REQ 卡片按钮、Chat 抽屉或 AI 面板、确认弹窗、Sprint 选择弹窗、执行反馈容器、文档入口和错误提示。
- 后端：需求中心动作 controller、治理候选/写入、Workflow Sync 调用、幂等、锁、恢复和权限校验。
- API：动作请求与结果查询需表达对象身份、动作类型、操作身份、受理/运行/失败/完成、产物引用和安全错误摘要；如修改接口必须同步 OpenAPI、Orval 和 `docs/03-api-index.md`。
- 数据库：优先复用既有治理候选、Chat turn、操作记录和观测结构；若新增表、字段、索引、迁移或保留周期，必须同步 SQLite/MySQL schema、迁移和 `docs/04-database-design.md`。
- 观测：四层观测均适用；不得保存完整 Prompt、文件正文、请求/响应正文、密钥、Cookie、Authorization header、本机路径或未脱敏治理材料。
