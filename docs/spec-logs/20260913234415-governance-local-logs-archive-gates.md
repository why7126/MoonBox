---
purpose: 本地日志归属与归档门禁修复
created_at: 2026-09-13 23:44:15
updated_at: 2026-09-13 23:44:15
---

# 本地日志归属与归档门禁恢复

## 目标与证据

logs 下为 BUG-0016 与 REQ-0026 取证产物，现有 Change 文档引用，未被 Git 跟踪。保留路径与内容，定义为本地忽略目录，长期归档证据转存 Change evidence 或脱敏摘要。

## 变更与更新文件

.gitignore、scripts/validate-directory-structure.py、rules/directory-structure.md、AGENTS.md、README.md、docs/README.md；修复 fix-requirement-center-apply-lifecycle-sync 的 proposal/design 英文标题，仅文案无状态变化；扩展 repair-change-identity-uniqueness 的提案、设计、任务、规格及验证记录。

## 验证结果与影响

目录、全局中文、上下文预算、环境忽略及目标 Change strict 校验全部通过；隔离验证3项通过（无忽略拒绝、忽略且未跟踪通过、强制跟踪拒绝）。日志文件数量与聚合SHA-256前后一致，未移动或修改日志。API/DB/Web/管理端/客户端/Orval/Docker Compose及业务安全边界无变更。
product_data_collection_observability: not_applicable；affected_layers: []；原因：本地文件治理，不改变运行时观测。validation：脚本及完整性检查。

## 后续

继续此前已授权的 repair-change-identity-uniqueness 归档。未自动创建后续 Issue/Change。
