# 最终归档准入诊断

## 当前结论（治理修复后）

独立Change support-reviewed-spec-evolution已完成实现与四项联合验收，恢复REQ-0050 v6要求的现行证据准入：同名MODIFIED需有效结构化验收且全文输入覆盖，保留历史、权限及并发门禁。REQ-0053的27项验收保持有效，历史兼容与三项旧文本限制已解决；最终共享门禁结果见final-archive-readiness.json。以下为过程历史，不代表当前阻塞。未执行正式归档。

2026-10-26：实现状态 applied，任务24/24，验收27/27 passed；Workflow Sync opsx.accept 成功，Issue acceptance_status=passed。规格临时副本预演通过，证据 readiness 为 ready。

最终共享门禁 `opsx_acceptance.py --change update-chat-scalable-execution-storage --archive-readiness` 返回 blocked / acceptance_source_invalid。逐层只读定位：Issue 验收证据本身 ready；protected_rule_integrity → rule_change.conflicts 抛出 incomplete_archive_history。

已定位的首个历史对象：openspec/archive/2026-09-13-add-chat-workbench-codex，关联 codex-session-execution 的“平台额度与结果空间”。目录身份唯一，但 completed_archive 返回 false：trace 为 applied，缺少门禁要求的 execution.completed_at 完成事实。不能仅因已位于 archive 目录就补写历史事实。

处理边界：不改写历史，不放宽门禁，不执行正式归档；保留当前验收结果。需另行核验历史归档证据与兼容迁移方案，再重新检查完整历史及规则约束。尚未判定通过所有后续历史检查。

AI Usage 两个工作流 hook 均返回 actual、0 warning；治理耗时记录独立为 usage-unavailable，未将其换算成实测Token或收益。未自动创建跟进 Issue/Change。

## 历史核验后的复查（2026-10-26）

历史归档事实已确认：提交217d84c2e89583daccb84d11bb3967ad481695f5收录唯一归档目录；sprint-004关闭报告记录11/11 Change归档；REQ-0025为done/archive；目标Change46/46任务完成。按文档治理的历史状态纠正规则，将旧trace的applied投影纠正为archived，记录本次核验时间与来源，不补写未知execution或归档时间，不改变历史规格、任务或验收正文。此为已存在事实的元数据纠正，无新增运行时代码或校验行为，不新建Change。

另查到2026-09-29-add-chat-agent-model-reasoning-selector/specs中的未跟踪.DS_Store，file确认是Apple桌面元数据，已转存Git忽略的本地取证目录，不删除原文件内容、不改解析器。

复查不再返回acceptance_source_invalid或incomplete_archive_history，而是archive_requirement_conflict：
- codex-session-execution / 平台额度与结果空间
- codex-session-execution / 事件持久化与可信差异
- web-catalog-chat-workbench / 额度与容量反馈

三项历史保护来源均为add-chat-workbench-codex。当前protected_rule_integrity只允许原约束不变的追加或已知精确例外；REQ-0053是已评审的业务语义替换，不能用改写历史、改名规避或伪造追加来消除冲突。当前验收27/27保持有效，但最终归档未就绪。扩大为规格演进门禁治理修复须单独建立Change并保持评审/验收/权限边界；已向用户提出该范围选择。未执行归档或提交。
