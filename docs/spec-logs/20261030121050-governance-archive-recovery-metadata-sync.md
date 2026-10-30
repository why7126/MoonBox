---
title: 归档恢复状态与受保护引用一致性
created_at: 2026-10-30 12:10:50
updated_at: 2026-10-30 12:12:35
---

# 目标与结果

修复 REQ-0048 跨迭代归档状态、受保护验收初始元数据和中文原型引用冲突。REQ-0048 已归档，收尾检查 22 份文件零冲突；304 个原归档文件及原恢复日志逐文件哈希不变。

## 变更与文件

- scripts/workflow_sync/engine.py：跨 Sprint 关联闭包与成员级子文档同步。
- src/backend/app/governance/archive_metadata.py、scripts/restore-archive-metadata.py：绑定原文、日志、交付投影及完整通过清单的追加恢复记录，不重写原文件。
- src/backend/app/governance/archive_finalization.py、archive_issue_reference.py 和 scripts/workflow_sync/prototype_references.py：中文裸路径边界及已证明的历史 Issue 引用位置解析，活动文档不豁免。
- scripts/README.md、rules/document-governance.md、docs/standards/opsx-acceptance.md、opsx-archive 技能说明及本次 Change：同步恢复与阻断契约。
- 对应回归覆盖证据篡改、失效证明、重复身份、未完成兄弟、真实缺失、符号链接及幂等；可变 Issue trace 保留旧摘要与原字段说明。

## 验证与证据

静态门禁、104 项聚焦回归、真实 wrapper 收尾已通过；5 项自动验收全部通过，最后增量执行 2 项、复用 3 项。临时副本归档预演和当前 readiness 均通过。新增同一行中文路径反例曾检出短路径误去重，修复与失败清单均保留。证据位于 openspec/changes/fix-archive-recovery-metadata-sync/evidence/。原恢复日志与产品验收材料保留原字节，恢复附加记录独立存放。未重复运行真实产品验收；既有 20 项通过证据仍有效。

## 影响与后续

API、数据库 schema、Web、管理端、客户端、Orval、Docker Compose、部署及安全授权边界均无变化；仅共享纯治理检查模块。product_data_collection_observability: not_applicable；affected_layers: governance；validation: 状态、引用及证据完整性检查通过，不新增产品数据采集。

当前修复验证通过，收益阶段为 observing；没有可归因的完整 Token 对照，不宣称节省。未自动创建 follow-up Issue。本治理 Change 待单独归档授权；REQ-0048 的既有归档授权已执行完毕。
