---
title: Chat 未知轮次有界恢复变更追溯
change_id: fix-chat-unknown-recovery-container-churn
status: applied
bug_id: BUG-0064-chat-unknown-recovery-container-churn
iteration: sprint-014
execution:
  schema_version: 1
  started_at: 2026-10-26 14:02:31
  completed_at: 2026-10-26 14:35:32
  last_event: opsx.apply
---

# Chat 未知轮次有界恢复变更追溯

## 来源与状态

来源：[BUG-0064-chat-unknown-recovery-container-churn](../../../issues/bugs/review/BUG-0064-chat-unknown-recovery-container-churn/trace.md)。修复评审approved，Sprint为sprint-014，估算5人天。当前实现与8项自动验收完成，原运行部署未升级。

## 证据与范围

采用BUG E1—E8确认无界恢复机制；原执行异常与单次RPC错误未知。验收基线AC-01至AC-08映射tasks第3节。product_data_collection_observability适用Task Trace/span和恢复元数据，HTTP请求与用户行为采集N/A；双库与真实Docker验证通过。

## 下一步

`/opsx-archive BUG-0064-chat-unknown-recovery-container-churn`



## 实施检查点

根因门禁通过（8项证据）；sprint-014双向范围有效，opsx.start已成功。旧技能中的opsx.apply dry-run会提前要求启动/全任务完成，不能作为实施前范围探测；以正式opsx.start的Sprint解析、Issue状态和scope核对完成准入，不伪造完成勾选。

横切检查：backend/DB/Docker，admin-list/admin-form/admin-modal/media-upload均N/A；AC-XCUT、knowledge_base_refs与UI/原型门禁N/A，承接Sprint隔离取证约束。无API/UI/客户端生成变化；数据库、部署配置、恢复观测及权限回归适用。

已实现持久化预算、独立恢复槽、权威终态围栏、成功预检缓存、单次无变化提示、运维续接和脱敏观测。补齐本机worker同路径，读取最长60秒、租约120秒。最后一次尝试崩溃后只领取清理任务、不新增读取；失租旧任务不能清理新持有者。验收计划AC-01至AC-08关联同一组完整输入指纹及双库/真实Docker证据。

首轮扩大回归137通过、1项显式环境用例跳过；首轮真实Docker330秒静默、正常/异常/取消/中断回收通过。最终失租、历史清理修改后的回归和真实观察已通过，以最新evidence文件及验证记录为准。真实样本使用合成认证、不调用模型、不访问历史unknown；原运行部署尚未升级。

临时资源登记run为7745b0dcc95649dbaeecc80a8a3041c2，属于本Change的MySQL与Docker隔离验证；结束须cleanup --apply及check。全部正式服务、卷、宿主数据保留。


## 验证记录

最终SQLite142通过/1显式模型用例跳过，MySQL23通过/1SQLite专属备份用例跳过，真实Docker受控恢复6创建/6销毁，暂停330秒0新增，正常/异常/取消/中断/超时清理通过。所有证据与当前完整输入指纹一致，见[交付验证](verification.md)与evidence中的双库、Docker和资源清理摘要。临时run已cleanup并check为clean，零容器/网络残留；共享服务、数据卷和宿主数据未删除。正式运行worker未升级，不声称原部署已停止历史恢复循环。

执行复盘：范围内失败均已修正；过期证据未作为通过来源。建议后续将opsx-apply的实施前Sprint检查改为独立只读范围检查，避免completion dry-run与启动/任务全勾门禁冲突；本次未另建Issue/Change。精确本命令Token用量不可得，不估造收益。

自动验收最终清单：[8项通过](evidence/acceptance/20261026143724020477-0ad85f24/summary.md)。规格合并预演passed，尚未执行正式归档。
