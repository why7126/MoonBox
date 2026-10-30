---
purpose: 归档跨入口收尾一致性治理
created_at: 2026-10-30 09:04:53
updated_at: 2026-10-30 09:04:53
---

# 归档收尾一致性第一批

目标：单项归档提前发现普通引用和当前正文残留，避免目录已移动就报告完整成功。

变更：共享只读 archive_finalization、CLI check-archive-finalization、archive-change.sh 完成报告、Sprint 扫描器，以及普通/受控/首次启用协调器的完成与重放检查。更新归档技能、AGENTS、文档治理和上下文预算、脚本说明及校验器；回归与证据归属 fix-archive-finalization-consistency。

验证：83 项聚焦回归及四项自动验收通过；OpenSpec、Sprint 范围和 diff 校验通过。已验证恢复只补收尾、完成重放复核、普通与历史导航、部分交付保留。历史 applied trace 保留，当前状态与历史混杂项需证据复核。

真实观察：sprint-014 只读扫描发现 7 处当前正文残留，原文与证据未改。未执行真实产品归档；Docker reap 服务不可达，本次无新容器。已有目录 legacy SQLite 警告保留。

影响：API/DB/Web/客户端/管理端/Orval/Docker Compose 无接口或结构变化；仅后端治理协调器接入，授权、签名、恢复日志、验收和部分交付策略不变。

后续：按证据逐项处置当前残留；正式部署后的行为收益继续观察，不宣称本轮已证明减少弹窗或节省 Token。
