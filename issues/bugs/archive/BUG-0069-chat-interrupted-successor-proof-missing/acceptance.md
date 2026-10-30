---
bug_id: BUG-0069-chat-interrupted-successor-proof-missing
created_at: '2026-10-27 16:38:20'
updated_at: 2026-10-30 08:33:56
title: Chat 中断缺少旧同步证明导致外部接续完成后仍受限验收标准
acceptance_status: passed
---

# Chat 中断缺少旧同步证明导致外部接续完成后仍受限验收标准

复用来源：[BUG-0061的2026-10-27复发材料](../../archive/BUG-0061-cross-entry-continuation-guard-convergence/trace.md)。用户明确授权承接，不继承原历史验收passed或原已归档Change。

## 验收状态

8项均已获得本次证据；AC-008现场规则与任务承接成功，旧停止及步骤保留，共享准入可发送。原RC-001至RC-008一一映射本BUG的AC-001至AC-008。

## 验收矩阵

| 编号 | 验收要求 | 证据与通过条件 | 当前结果 |
|---|---|---|---|
| AC-001 | 原轮已停止且无成功同步证明，外部完成具有独立可信证据时可发起后继核验 | REQ/BUG隔离正例；真实接口及页面均可进入核验，不伪造原同步步骤 | 已通过，见 Change verification.md |
| AC-002 | 后继完成验证对象、动作、Change、绑定、授权、时间关系、正式完成收据及当前验收指纹 | 缺收据、仅勾选任务、仅ready、错对象、错绑定、过期证据、缺可信启动基线逐项拒绝 | 已通过，见 Change verification.md |
| AC-003 | 历史不被改写，后继证明独立留痕 | 原停止状态、旧步骤、事件及证明哈希保持；新记录关联原操作与后继证据、核验版本和原因 | 已通过，见 Change verification.md |
| AC-004 | 拒绝并发覆盖及真实依赖冲突 | 新执行占用、权限撤回、快照变化、过期回调、任务范围变化与未覆盖输入等负例；无部分放行 | 已通过，见 Change verification.md |
| AC-005 | 幂等及中断恢复 | 重复核验、刷新和服务中断后重试不重复业务执行，不解除新保护，不重复合并规格 | 已通过，见 Change verification.md |
| AC-006 | 卡片与执行详情解释当前事实 | 1440px与390px分别验证可核验、核验中、成功、失败；成功显示已由后续执行完成及证据入口，旧执行仍已停止；附截图、selector、computed style | 已通过，见 Change verification.md |
| AC-007 | 真实完整链路与兼容性 | 隔离Chat中断→外部完成→产品核验→合法后续动作实际发送→终态；SQLite/MySQL均验证；既有有证明恢复与review/archive专用协议回归 | 已通过，见 Change verification.md |
| AC-008 | BUG-0056现场恢复单独验证 | 修复后重读现场、证据与版本，经授权核验后检查当前准入；不能用隔离结果代替正式对象恢复，正式归档另按授权执行 | 已通过，见现场ac-008.json |

product_data_collection_observability: affected。affected_layers: governance workflow、completion proof、API admission、Web UI、recovery audit。validation: AC-002至AC-007验证请求与操作关联、拒绝原因和核验结果脱敏可追溯；后台核验不伪造用户行为事件。遵循docs/standards/product-data-collection-observability.md。DB schema与客户端生成是否变化在修复设计确认；对象存储、管理端及未启用客户端本次无已确认改动。API响应及生成客户端已同步；无数据库schema迁移。详见Change验证记录。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-10-30 08:33:56
accepted_by: workflow-sync
source_change: fix-chat-interrupted-successor-proof
source_sprint: sprint-014
evidence: [openspec/archive/2026-10-27-fix-chat-interrupted-successor-proof/evidence/acceptance/20261027182313150225-0fde4c1e/summary.md]
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

## 验收执行清单

- [x] AC-001 原轮已停止且无成功同步证明，外部完成具有独立可信证据时可发起后继核验
- [x] AC-002 后继完成验证对象、动作、Change、绑定、授权、时间关系、正式完成收据及当前验收指纹
- [x] AC-003 历史不被改写，后继证明独立留痕
- [x] AC-004 拒绝并发覆盖及真实依赖冲突
- [x] AC-005 幂等及中断恢复
- [x] AC-006 卡片与执行详情解释当前事实
- [x] AC-007 真实完整链路与兼容性
- [x] AC-008 BUG-0056现场恢复单独验证
