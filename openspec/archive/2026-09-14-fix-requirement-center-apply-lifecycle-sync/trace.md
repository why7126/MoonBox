---
status: applied
iteration: sprint-005
change_id: fix-requirement-center-apply-lifecycle-sync
bug_id: BUG-0015-requirement-center-apply-start-stage-not-synced
created_at: 2026-09-12 21:01:17
updated_at: 2026-09-12 21:30:31
execution:
  schema_version: 1
  started_at: 2026-09-12 21:14:02
  completed_at: 2026-09-12 21:30:31
  last_event: opsx.apply
---

## 链路

- 来源BUG：BUG-0015-requirement-center-apply-start-stage-not-synced
- 父需求：REQ-0012-frontend-requirement-center
- Sprint：sprint-005；沿用M=3人天，不重复计入估算。
- Readiness：Ready；已评审并纳入Sprint，根因confirmed（6条证据）。
- 阶段：已实施并通过目标回归，完成同步单独记录。
- product_data_collection_observability: applicable
- affected_layers: agent_workflow、web、api治理读取。
- N/A原因：无已确定数据库表、对象存储或保留周期变更；CLI不伪造行为事件。
- validation: OpenSpec严格、中文、目录、上下文预算、观测与Sprint Scope校验通过；bug.opsx同步零错误，真实验收在apply阶段完成。

## 实施检查点

2026-09-12 21:06:59：根因/Sprint门禁通过，正式开始实施；当前CLI尚无opsx.start，按设计自举先记录兼容in_progress，不执行完成同步。新事件可用后立即接入。

## 实施结果

实现及回归完成，详见 [verification.md](verification.md)；真实浏览器证据见 [browser-lifecycle.json](evidence/browser-lifecycle.json)。完成态以本文件 execution 与任务清单及 Workflow Sync 结果为准。

## 归档验证摘要

归档请求：用户于2026-09-14执行 /opsx-archive BUG-0015，解析为本Change。13/13任务完成，工件全部done；复核既有85项后端/工作流、9项前端、构建与真实1440px浏览器证据，见verification.md及evidence/。本次为归档复核，未重跑业务测试。

规格合并：agent-workflow-tooling新增研发执行生命周期同步；web-catalog-requirement-center-real-data修改9阶段状态映射，现行标题匹配。长期API索引、共享技能契约及知识库经验已同步；无API结构、DB、部署、安全或客户端生成变化。本次是状态行为修复，非原型/截图视觉复刻，无新增modal族；保留已有截图与computed style证据。

身份唯一性、目录、env忽略策略、观测与目标OpenSpec严格校验通过。系统python3缺PyYAML，改用项目已安装依赖的虚拟环境完成校验。归档后按顺序同步Issue/Sprint并迁移BUG，Sprint保持独立流程。
