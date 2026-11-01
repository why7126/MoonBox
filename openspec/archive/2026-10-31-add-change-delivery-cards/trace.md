---
title: 需求中心独立交付卡片追溯记录
change_id: add-change-delivery-cards
requirement_id: REQ-0056-requirement-center-change-delivery-cards
status: applied
iteration: sprint-018
prototype_refs:
- path: issues/requirements/review/REQ-0056-requirement-center-change-delivery-cards/prototype/web/prototype.html
  role: html-structure
- path: issues/requirements/review/REQ-0056-requirement-center-change-delivery-cards/prototype/web/context.md
  role: decomposition-and-contract
- path: issues/requirements/review/REQ-0056-requirement-center-change-delivery-cards/prototype/web/cards-minimal-change-v2.png
  role: visual-reference
prototype_gate:
  decomposition: done
  ui_skeleton: confirmed
  visual_acceptance_1440: passed
  computed_style: passed
  req_final_consistency: checked
product_data_collection_observability:
  status: applicable
  affected_layers:
  - web
  - api
  - web_request_wrapper
  - usage_events
  - request_logs
  - task_traces
  reason: 卡片到执行恢复需保留明确目标Change及授权来源。
  validation: 直接API与UI来源授权、受控metadata、Task Trace目标、遥测降级回归通过；固定镜像隔离目标与中断拒绝观察见verification.md。
execution:
  schema_version: 1
  started_at: 2026-10-31 16:35:55
  completed_at: 2026-10-31 18:18:28
  last_event: opsx.apply
---
# 需求中心独立交付卡片追溯记录

## 来源与交付范围
REQ-0056已评审并纳入sprint-018；对应Change为add-change-delivery-cards。保留旧卡片样式，交付阶段按Change独立成卡；来源追溯、去重、任务与所有动作绑定明确目标。

## 原型与授权
用户已确认1440px实施骨架，无需再次确认。原型HTML/PNG为设计输入；最终组件映射和样式偏差说明见design.md。角色与主题视觉使用实际组件及合成只读响应；真实产品和隔离执行单独留证。

## 验证记录
详细结果、入口矩阵、30项AC映射与适用边界见verification.md；逐AC执行计划为acceptance-plan.json。evidence/acceptance/ui包含16组角色/主题/视口、20组浮层及8组历史/筛选截图和computed style。真实产品REQ-0048两张历史交付及兄弟任务定位已核对。

固定镜像隔离样本实际启动synthetic-alpha并主动停止；改绑synthetic-beta后原轮次重试409 delivery_target_mismatch，未执行beta。同目标成果待核对时仍拒绝重试；不把该观察写成成功续接。证据evidence/acceptance/observations/interruption-target.json。临时run f9e2114b28674e8da66351b936ca6970已清理，容器/网络均0。

## 实施检查点
实现、定向回归、最终部署和视觉自检已完成。PRD、故事、流程、验收计划、原型context、API索引与生成客户端已核对；无DB迁移、部署参数或对象存储变更。执行权限判定纳入持久化目标和当前Sprint正式范围。自动验收产品按钮因执行能力限制禁用并解释，CLI验收继续使用既有入口。

opsx.apply与opsx.accept同步均成功；30项验收通过，命令执行2次、同轮去重28项，失败/受阻/待采集均0。当前证据ready；归档临时副本预演通过。验收报告见[evidence/acceptance/20261031182048982884-f75aa82a/summary.md](evidence/acceptance/20261031182048982884-f75aa82a/summary.md)。未经授权未归档，历史批次不叠加计数。


## 最终归档门禁阻塞

本次30/30项验收通过，证据就绪，临时副本归档预演通过；最终共享归档门禁未通过，不能宣称可归档。`--archive-readiness` 返回 `acceptance_source_invalid`，直接调用保护规则检查定位为 `incomplete_archive_history`。

受影响历史来源：
- `2026-08-13-add-requirement-center-real-data-integration`：trace为applied，但缺少execution.completed_at。
- `2026-09-04-update-requirement-center-card-document-actions-ai-chat`：trace仍为in_progress。

两者与本次规格修改存在相同条目，当前completed_archive检查不认可其完成事实。未修改历史档案、未绕过门禁、未实际归档。本次保留applied及验收passed；后续需独立核实上述历史归档事实后，再执行本REQ的opsx-accept增量复核。此问题不改变本次实现和逐AC证据结论。

## 卡片顶部布局返修
2026-10-31：标题下展示完整Change ID；人力待估算并入标签行。截图、样式、REQ子文档扫尾及验证见[返修台账](acceptance-fixes.md)。原applied与首次completed_at保持不变；返修与自动复验完成：30/30通过，失败/受阻/待采集均0；执行2组命令，同轮去重28项，证据ready。运行20261031192129096768-f204b061；归档临时副本预演通过，最终共享门禁仍因既有历史记录返回acceptance_source_invalid，未实际归档。opsx.modify与opsx.accept同步成功，REQ验收passed，卡片回到验收中。

## 2026-10-31 19:29 增量验收
用户执行opsx-accept后复核：30项全部通过，按当前输入指纹复用30项，新增测试命令0次、同轮去重0项，失败/受阻/待采集均0。公共预检通过、证据ready、归档副本预演通过；未重新声明产品操作观察。完整报告见[evidence/acceptance/20261031192925517041-14bb3c1f/summary.md](evidence/acceptance/20261031192925517041-14bb3c1f/summary.md)。Workflow Sync成功，REQ验收保持passed；最终归档门禁单独复核，历史档案不改写。

最终准入仍blocked：acceptance_source_invalid；直接复核保护规则为incomplete_archive_history，与前次两份历史归档来源相同。AI Usage回填成功（actual，1条命令记录，0警告）。未归档、未新建Issue/Change。

## 历史归档事实核实
2026-10-31：按用户授权核实两份历史Change，任务36/36与26/26、来源Issue归档事件、Git提交1cdea0a9与5f181743中的归档/正式规格变更交叉一致。仅将对应历史trace的applied/in_progress更正为archived，原时间与其他文件保持不变，不补造execution时间。修正前后哈希与证据入口见evidence/acceptance/history-verification/status-correction.json。此前incomplete_archive_history结论为修正前状态；修正后以本轮最终准入为准。

历史状态修正后暴露验收计划缺项：增量规格全文未纳入inputs，导致archive_requirement_conflict。现将该规格全文纳入全部AC输入指纹，保留原用例与门禁，重新运行验收，不调整正式规格或业务代码。

## 历史核实后验收结果
2026-10-31：两份历史Change的归档事实已核实并仅更正trace状态；增量规格全文已纳入验收输入。此前历史记录与规格覆盖阻塞已消除。最新运行20261031193424806046-3530fd99：30/30通过，2次命令执行、同轮去重28项，失败/受阻/待采集均0；证据ready及副本预演通过。Workflow Sync与AI Usage收尾成功；本轮最终共享归档准入为ready，recovery_reason为空。不实际归档。历史修正依据见evidence/acceptance/history-verification/status-correction.json。
