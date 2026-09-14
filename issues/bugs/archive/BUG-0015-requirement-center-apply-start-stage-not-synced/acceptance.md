---
bug_id: BUG-0015-requirement-center-apply-start-stage-not-synced
created_at: 2026-09-12 17:45:49
updated_at: 2026-09-14 09:25:34
acceptance_status: passed
---

# 验收清单

## 验收状态

acceptance_status: not_started

修复自验已执行；逐项证据见关联Change verification.md。人工验收状态由完成同步置为待定，不将开发自验冒充用户签收。

## 验收条件

| 编号 | 场景 | 通过标准 | 验证方式 | 结果 |
|---|---|---|---|---|
| AC-001 | 未启动 0/N | REQ/BUG 已评审并纳入 Sprint，未正式启动时保持准备开发态，显示启动动作。 | 自动化状态与看板回归 | 自验通过，见验证映射 |
| AC-002 | 启动成功 0/N | 通过门禁开始实施后即记录启动事实，卡片进入研发中，完成数仍为 0，动作改为查看进度。 | 启动事件集成测试及真实浏览器 | 自验通过，见验证映射 |
| AC-003 | 启动门禁失败 | 门禁失败或仅 dry-run 不产生启动事实，卡片保持准备开发态；报告阻塞原因。 | 门禁失败回归 | 自验通过，见验证映射 |
| AC-004 | 进度更新 | 验证通过再勾选；部分完成仍为研发中，所有状态投影与任务计数一致。 | 任务更新和 API 集成测试 | 自验通过，见验证映射 |
| AC-005 | 重复同步 | 重复启动或重跑同步幂等，不重复启动记录、不将已启动 0/N 派生回 提议态；不重开已归档条目。 | 幂等与终态保护回归 | 自验通过，见验证映射 |
| AC-006 | 中断与恢复 | 中断恢复保留已启动事实和实际进度，不假报完成；仅继续被授权且符合门禁的任务。 | 恢复场景回归 | 自验通过，见验证映射 |
| AC-007 | 完成门禁 | 任务全勾选但完成门禁未通过时不提前宣告 验收态；通过后统一进入验收，归档仍走独立流程。 | 完成门禁和阶段回归 | 自验通过，见验证映射 |
| AC-008 | 共享入口一致 | opsx-apply、openspec-apply-change 和 Sprint 编排采用相同启动/进度/完成契约，REQ/BUG 均验证。 | 技能契约检查和入口矩阵 | 自验通过，见验证映射 |
| AC-009 | 状态投影一致 | Change trace、Issue 关联 Change 状态、registry/索引与 API/看板按各自字段语义一致，不把 Issue 迭代内 与 Change 进行态 误判为漂移。 | 持久化事实源及派生一致性集成测试 | 自验通过，见验证映射 |
| AC-010 | 真实刷新 | 在实际目标项目从准备开发态启动至研发中，验证 0/N 下轮询、焦点刷新及手动刷新，保留 context 响应摘要和页面截图；请求成功后不依赖局部假状态。 | 真实 API/浏览器观察 | 自验通过，见验证映射 |
| AC-011 | 关联隔离与观测 | 记录实际条目与 Change/Sprint 的关联，切换项目不串卡；CLI 不伪造界面行为事件，日志脱敏；受影响层级声明和证据完整。 | 项目隔离与观测检查 | 自验通过，见验证映射 |

## 验收证据要求

- 自动化证据记录测试命令、用例结果、失败摘要及源码版本；开始、计数、完成门禁分别断言。
- 真实观察记录页面路径、项目与条目脱敏标识、时间、截图、context 的 stage/tasks/snapshot_revision 及状态码；不使用 mock 响应替代真实 API。
- 复现环境与修复验收环境分开标注，不把 BUG-0014 后续文件变化当成本缺陷通过证据。
- 原型像素复刻不在范围；页面阶段、动作及刷新行为属于验收范围。

## 数据采集与链路观测

- product_data_collection_observability: applicable
- affected_layers: Agent Workflow、后端治理状态读取、Web 看板展示。
- N/A 原因：当前仅完善缺陷包，无 API/DB、埋点表结构、对象存储、部署或客户端生成变更；后续 Change 按实际实现复核适用层级，CLI 不伪造 usage_events。
- validation: 根因合成复现四组通过；AC-001至011已完成自验映射，真实请求与快照摘要见Change evidence/browser-lifecycle.json。

## 完成判定

全部适用条件通过且证据可定位，根因、主文档、trace 与关联需求反向索引一致后，才可进入相应完成/归档流程。必需证据缺失时保留已验收，不默认豁免。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-09-14 09:25:34
accepted_by: workflow-sync
source_change: fix-requirement-center-apply-lifecycle-sync
source_sprint: sprint-005
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

