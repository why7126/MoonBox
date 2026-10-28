---
bug_id: BUG-0061-cross-entry-continuation-guard-convergence
title: 跨入口续接证明与执行保护收敛修复评审
review_result: approved
reviewed_at: '2026-10-21 15:57:03'
created_at: '2026-10-21 15:57:03'
updated_at: 2026-10-27 16:18:35
review_basis: 用户明确执行 bug-review --approve；缺陷包及根因证据门禁
---

# 跨入口续接证明与执行保护收敛修复评审

## 评审结论

批准修复，维持high，采用常规fix，不走hotfix。范围为跨入口后继完成证明、直接命令同步采集的dry-run误识别、保护安全收敛及产品/CLI实际归档准入一致性；以BUG-0055为恢复现场，不按对象ID特判。

批准仅允许进入Sprint规划，不代表实现、验收、恢复或归档已完成。先纳入Sprint并同步in_sprint，再创建OpenSpec Change。

## 评审清单

| 项目 | 结论 | 依据 |
|---|---|---|
| 可复现或根因充分 | 通过 | 根因confirmed，10条证据；旧progress证明、CLI后继变化与两条恢复路径缺口相互印证；dry-run分号误识别已纯函数复核 |
| 严重等级合理 | high | 阻断合法治理流转及归档，诱导重复执行风险；无数据丢失或P0事故证据 |
| 回归验收明确 | 通过 | AC-001—AC-014覆盖证明语义、差异分类、权限、并发、幂等、产品实际发送及CLI归档、现场恢复与历史边界；全部未执行 |
| hotfix路径 | 不采用 | 无绕过正确性门禁的依据，按常规修复验证交付 |
| 临时处理 | 无已验证的解除方案 | 保留旧保护和成果，仅只读核查，禁止手改guard或重放原命令 |

## 证据边界与实施约束

- 19项是旧最后同步至探索当前态的累计差异，不是首次冲突文件清单；同步时正文缺失，历史行级归因仍partial。该边界不否定已确认机制，也不授权忽略真实冲突。
- 保留旧操作未完成事实，创建独立后继核验关系；核对对象、Change、绑定、权限、事件、输入与验收证据，用版本比较防止并发及过期回调。
- 不把外层退出0、任意sync_succeeded、任务勾选、静态ready或按钮可点当成产品业务完成证明。
- 负向门禁覆盖真实冲突、缺证/过期、身份变化、运行中操作；评审和归档保留专用协议，不重复合并规格。
- 部署后完成产品受阻→CLI续接→产品安全核验→实际发送→归档终态，并用等价隔离对象对照CLI。正式现场操作前重新确认状态，避免覆盖后续执行。
- 关联BUG-0060与BUG-0052；BUG-0055仅为恢复现场。本BUG不继承现场Sprint，不混入消息排序实现。

## 文档与观测

product_data_collection_observability: affected

affected_layers: governance workflow、completion proof、API admission、UI projection、recovery audit。

validation: 依AC-006/007/009/010/013验证关联、版本、脱敏原因与审计；API/客户端及UI文档随实现同步，DB迁移按设计判断。无须为本次文档评审修改代码、部署或安全权限。

## 门禁与提醒

根因证据门禁通过（10项）。root-cause.md status=confirmed表达根因确认度，保留该字段；不将扫描器的语义提醒误改为Issue状态。验收保持not_started，历史归因partial继续显式保留。

## 下一步

/sprint-propose --bug BUG-0061-cross-entry-continuation-guard-convergence

## 2026-10-27 复发修复评审

评审结论：批准本次复发修复范围，严重度high，常规fix，不采用hotfix或绕过保护。此结论为复发批次业务评审，不复用2026-10-21的验收通过结论，不代表实现、现场恢复或归档完成。

| 评审项 | 结论 | 依据 |
|---|---|---|
| 根因充分 | 通过 | root-cause.md R1至R6：新页面观察、部署两份核心文件哈希一致、入口/恢复分派/后继验证器三处依赖旧同步证明 |
| 严重度 | high | 已完成交付的后续动作受限，可能诱导重复执行；无数据丢失或紧急安全事故证据 |
| 修复范围 | 批准 | 无旧成功同步证明的已终止apply/modify，可依据可信原操作身份及独立后继完成证据受控核验 |
| 回归验收 | 明确、待执行 | RC-001至RC-008覆盖正反例、历史完整性、并发、幂等、真实发送、SQLite/MySQL、UI及现场恢复 |
| 临时处理 | 保留保护与成果 | 当前无已验证自助解除方式，不改数据库、不伪造证明、不重放原命令 |
| 紧急路径 | 不采用 | 经标准Sprint与新Change交付，原review/archive专用协议继续保留 |

### 批准边界

保留旧停止状态、步骤、事件和已有证明；后继核验单独记录。可信操作身份/启动基线、对象/动作/绑定/权限、正式完成收据、当前验收指纹、输入覆盖及并发版本缺一不可。不能仅删除has_sync条件或仅按8/8、ready放行。缺少可信基线、真实冲突、证据过期、新执行占用继续拒绝。

本次仅确认机制缺口；不保证BUG-0056现有全部后继证据可直接通过未来核验。部署后按最新现场独立验证；正式归档遵守后续授权。

### 生命周期承接限制

用户此前明确选择补充原BUG并保留done/archive事实，本轮继续遵守。当前阶段迁移脚本仅允许plan/legacy进入review；Workflow Sync依据已归档关联Change仍派生done。因此本次不执行archive→review迁移、不将当前trace伪改approved、不重新纳入历史sprint-012，不推荐直接用该done对象执行sprint-propose。

复发业务评审已完成，进入新修复排期前需确定可支持的承接方式：保留原归档BUG并新建关联修复BUG走标准链路，或先通过独立治理变更建立原编号复发批次/重开机制。当前未获后者治理实施或新建Issue授权，均未自动执行。历史评审和归档记录不覆盖。

### 文档与观测审查

product_data_collection_observability: affected。affected_layers: governance workflow、completion proof、API admission、Web UI、recovery audit。validation: 按RC-002至RC-007验证关联、权限、拒绝原因和脱敏审计；后台核验不伪造用户行为事件。API结构、客户端生成与DB迁移按新Change设计确定；本轮仅文档评审，无产品变更。
