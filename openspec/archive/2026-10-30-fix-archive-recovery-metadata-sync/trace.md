---
title: 归档恢复元数据一致性追溯
change: fix-archive-recovery-metadata-sync
status: applied
sprint: sprint-016
created_at: 2026-10-30 12:02:45
updated_at: 2026-10-30 12:12:35
execution:
  schema_version: 1
  started_at: 2026-10-30 12:02:46
  completed_at: 2026-10-30 12:10:51
  last_event: opsx.apply
---

# 追溯

## 授权与范围
用户明确授权治理修复并续接 REQ-0048 归档。修复 Change 本身不自动归档。

## 产品数据与链路观测
product_data_collection_observability: not_applicable
affected_layers: governance
原因：仅治理状态与文件检查，不新增 API、数据库、业务日志、Task Trace 或客户端字段。
validation: 治理回归、归档预检及真实 REQ-0048 收尾通过。

## 验证记录
104 项聚焦回归通过；5 项自动验收全部通过，最终增量运行执行 2 项、复用 3 项。上下文预算、中文优先、目录及 OpenSpec 校验通过；目录仅保留既有 legacy SQLite 警告。REQ-0048 wrapper 实际恢复成功，22 份文件零冲突；304 个原归档文件与恢复日志哈希不变。证据见 evidence/archive-finalize-report.md 和 evidence/history-integrity.json。

第一次恢复解决了状态同步，后在原型迁移预检发现引用冲突，未迁移 Issue；追加修复与负向回归后第二次完整收尾通过。原日志和验收材料未覆盖。治理修复本身不代表再次运行产品验收；真实产品原 20 项通过证据继续有效。完整 Token 成本尚不可归因，不宣称收益确认。

## 最终验收与收尾

- 完整验收清单：evidence/acceptance/20261030121136762609-6f3b2c34/manifest.json。首次统一运行在新增中文路径反例中发现同一行短路径被误去重，修复后受影响两项复验通过，旧失败清单保留。
- 临时副本归档预演与当前 readiness 通过；REQ-0048 已归档，22 文件零冲突；本治理 Change applied，5/5 AC 通过，待独立归档授权。
- 原归档 303 文件及原恢复日志合计 304 项逐字节不变。所有新增恢复记录及失败/成功检查记录独立保留。
