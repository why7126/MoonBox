---
change_id: fix-requirement-center-apply-lifecycle-sync
bug_id: BUG-0015-requirement-center-apply-start-stage-not-synced
created_at: 2026-09-12 21:01:17
updated_at: 2026-09-12 21:01:17
---

## 1. 实施前核验

- [x] 1.1 复核根因与sprint-005门禁、当前并行修改及分级元数据治理兼容；确认CLI/后端部署共享模块可用路径和首次启动自举边界。
- [x] 1.2 固化AC-001至011的测试映射、旧状态兼容矩阵、隔离项目和快照观察方式，补充实际设计差异。

## 2. 状态事实与事件

- [x] 2.1 实现版本化可选执行元数据和统一无副作用解析，覆盖旧状态及归档保护（AC-001、002、007、009）。
- [x] 2.2 增加opsx.start/opsx.progress事件及完成事件校验；启动门禁、dry-run与完成门禁分离（AC-002、003、007）。
- [x] 2.3 串行写入Change事实与Issue/Sprint投影，复用锁、原子写和冲突保护，验证重复及部分失败恢复（AC-005、006、009）。
- [x] 2.4 两份apply技能、sprint-apply及命令顺序/同步规则接入共同生命周期契约，保留in_sprint与severity语义（AC-008、009）。

## 3. 看板与回归

- [x] 3.1 后端看板与快照采用统一状态来源，保证零进度及阶段动作一致，项目隔离与旧终态兼容（AC-002、004、009、011）。
- [x] 3.2 添加CLI/状态单元和集成回归：未启动、启动失败、0/N、部分完成、全勾选未完成、重复同步、中断恢复、并发冲突及旧终态（AC-001至009）。
- [x] 3.3 添加REQ/BUG context与前端回归，覆盖轮询、焦点/手动刷新、项目切换旧响应隔离（AC-002、004、010、011）。
- [x] 3.4 真实隔离项目启动REQ/BUG，采集0/N前后context、snapshot_revision、阶段/动作截图与刷新证据，记录真实与合成边界（AC-010、011）。

## 4. 文档与完成

- [x] 4.1 更新BUG验收、主文档、trace与父REQ反向追溯；按适用性同步API/部署/DB文档及OpenAPI客户端，不适用项说明原因。
- [x] 4.2 运行目标Change严格、中文、目录、上下文预算、Sprint Scope及观测校验；完成门禁后串行Workflow Sync与AI Usage，核对投影一致。
- [x] 4.3 评估并按适用性沉淀docs/knowledge-base/incidents/的启动与进度分离经验，记录适用或不适用结论。
