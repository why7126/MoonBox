---
title: 归档收尾一致性追溯
change: fix-archive-finalization-consistency
status: applied
sprint: sprint-016
execution:
  schema_version: 1
  started_at: 2026-10-30 08:54:19
  completed_at: 2026-10-30 09:04:53
  last_event: opsx.apply
---

# 归档收尾一致性追溯

## 范围与授权

用户授权第一批跨入口治理修复。保留历史证据，不改变部分交付状态策略。产品侧仅接入共享只读门禁，不修改业务接口。

## 验证记录

- 自动验收四项通过：83 项聚焦回归、上下文预算、当前 Change 中文校验、目录校验。回归使用真实协调器/SQL/文件检查点，工具与准入使用隔离替身，不代表真实部署归档轮次。
- 用例覆盖普通、受控及首次启用入口的恢复/重放、每请求一次收尾检查、合并与同步不重复、CLI 非 finalize/失败报告、历史与部分交付正反例。
- OpenSpec、Sprint 范围与 diff 空白校验通过。目录校验已有 legacy SQLite 路径警告保留。
- 真实 sprint-014 只读扫描检出 7 处明确当前正文残留；未修改原 Issue、归档 Change、验收证据或恢复日志。
- Docker reap 预检返回 docker_command_failed:info，本次未创建容器，不能声明既有资源已清理。
- 证据：最新 evidence/acceptance 清单及 summary。静态、合成回归已通过；实际产品归档效果与用量收益仍为 observing。

## 影响与限制

API、DB、UI、部署、安全授权及客户端生成均无变更；后端仅治理收尾接入。当前正文采用有限显式语义，混杂历史语境列为 review，不做自动历史改写。保留部分交付状态策略、旧 applied 执行事实及原验收/签名/恢复门禁。

## 产品数据与链路观测

product_data_collection_observability:
- status: not_applicable
- affected_layers: governance
- reason: 本次只读收尾检查与协调器完成条件不新增 API、DB、request_logs、usage_events、Task Trace 或请求封装字段。
- validation: 归档检查及恢复回归通过，不把报告或遥测作为授权依据。

## 验收返修

中文冒号裸路径误报已修复，10处当前文案已同步，旧文案完整保存在[返修台账](acceptance-fixes.md)。88项聚焦回归通过，两个Sprint扫描零命中，1548个相关归档文件摘要不变；部分交付策略与首次apply事实保留。无API/DB/UI/部署或客户端生成变化。


## 2026-10-30 过期证据增量复验

用户授权仅复验并核对准入，不执行正式归档。AC-ARCHIVE 与 AC-REPAIR-DOCS 因输入变化重新执行，均通过；AC-CONTEXT、AC-LANGUAGE、AC-DIRECTORY 按当前指纹复用。完整验收 5/5 通过，0 失败、0 阻断、0 待采集，执行 2 项、复用 3 项。

证据：[本轮验收摘要](evidence/acceptance/20261030104523742557-24a276a7/summary.md)。文档检查确认 sprint-014、sprint-015 扫描通过，1548 个受保护文件摘要不变。原历史验收报告保留，部分交付状态策略不变，未修改产品实现或正式归档对象。

临时副本规格合并预演通过。本轮为命令回归及文件状态复验，不声明新增真实产品归档轮次；不创建临时 Docker 环境。API、数据库、UI、部署、安全及生成客户端均无需同步。

补充检查：当前 Change 中文校验与 diff 空白校验通过；额外全 Change 标题检查发现既有文档缺少 title/H1 或不一致（proposal、design、tasks、spec、trace、acceptance-fixes）。该检查不属于本次两项复验计划，未扩大为文档格式返修，结果单独保留，不宣称标题检查通过。

## 文档标题返修

本轮按用户授权补齐六份文档 title/H1，详见 [返修台账](acceptance-fixes.md)批次二。标题检查纳入 AC-DOC-TITLES，最终结果以最新 evidence/acceptance 完整清单为准；保留此前检查失败记录与首次 apply 事实，不执行正式归档。
