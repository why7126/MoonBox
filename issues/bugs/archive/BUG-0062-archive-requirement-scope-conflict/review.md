---
bug_id: BUG-0062-archive-requirement-scope-conflict
title: 归档恢复条文冲突判定修复评审
review_status: approved
created_at: '2026-10-21 18:10:04'
updated_at: '2026-10-21 18:10:04'
---

# 归档恢复条文冲突判定修复评审

## 评审结论

按用户明确的bug-review --approve指令评审通过，确认修复。严重等级保留high；根因confirmed，8条证据通过门禁。批准的是修复范围和验收标准，11项修复AC尚未执行，不能据此关闭sprint-011或放行REQ-0046归档恢复。

## 评审清单

| 检查项 | 结论 | 依据与边界 |
|---|---|---|
| 可复现或根因充分 | 通过 | root-cause.md E1—E8：目标36项及附件有效，后继链连续、Requirement不相交，模块级判断仍拒绝 |
| 严重等级 | high合理 | 阻断合法迭代关闭且进度失真，未证实数据丢失或生产安全事故 |
| 修复范围 | 通过 | 模块与Requirement组合判冲突、AC进度与恢复状态分离、共享深层预检 |
| 回归验收 | 标准通过，执行未开始 | acceptance.md AC-001—011覆盖正负例、证据完整性、诊断、并发、历史不可变及四入口一致性 |
| hotfix路径 | 不采用 | 尚无生产紧急事件证据，走正常Sprint与OpenSpec，不绕过门禁 |

## 批准的边界与实现约束

1. 同模块不同Requirement仅在完整连续证明、唯一身份、交付/附件哈希、原条文和后继最终效果均有效时承接，不按BUG/REQ编号特判。
2. 同条文修改、删除、重命名、重复标题、未知操作或无法可靠解析保持拒绝。标题解析和规范化规则由Change明确，不以模糊匹配放行；保留对规格非条文变化和未知变更的完整性约束。
3. 恢复失败与AC失败分别表达：有效AC不清零，真实附件损坏不能被原passed覆盖；错误码和冲突身份向产品、CLI与同步贯通。
4. Sprint预检与Workflow Sync调用相同深层判定，在移动目录或写终态前拒绝；错误结构和退出码的调用方兼容一并验证。
5. 不重写原journal、manifest、历史哈希、首次执行时间，不重放成功归档或模型，不回滚已合法合入的后继规格。
6. 规格语义调整通过新OpenSpec Change进行；现有模块重叠拒绝测试同步修订，并保留全部安全负例。

## 数据采集与文档同步评审

product_data_collection_observability: applicable；affected_layers: agent_workflow_governance、归档准入、验收/诊断投影、Sprint预检、Workflow Sync。validation：AC-005—010覆盖共享入口、进度保真、脱敏及只读边界；修复尚未实施。N/A：当前仅评审文档，无DB迁移、对象存储、权限、部署或新增采集。实施若改变API响应或UI，需同步API/OpenAPI/客户端和真实产品验收；无影响时写明依据，不能跳过说明。

## 排期与后续

先执行sprint-propose正式纳入，再执行bug-opsx。sprint-011是受影响现场，不代表自动纳入；本次iteration保持null，无Change。评审未授权直接开发、强制关闭Sprint或变更容量。临时处置按workaround.md继续保留阻塞。

## 执行链路复盘

评审通过，根因与验收边界明确。问题证据见root-cause.md；规范优化随本缺陷的共享门禁修复承接，不另建重复事项。未额外创建Issue/Change。
