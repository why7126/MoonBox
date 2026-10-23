---
title: 卡片常驻信息标签变更追溯
change_id: add-card-persistent-info-tags
requirement: REQ-0051-card-persistent-info-tags
status: applied
acceptance_refs:
- evidence/acceptance/20261022191809580956-9179f514/summary.md
iteration: sprint-013
created_at: '2026-10-22 13:57:16'
updated_at: 2026-10-22 19:20:00
prototype_refs:
- issues/requirements/review/REQ-0051-card-persistent-info-tags/prototype/web/prototype.html
- issues/requirements/review/REQ-0051-card-persistent-info-tags/prototype/web/context.md
prototype_gate:
  decomposition: done
  ui_contract: defined
  ui_skeleton: done
  visual_acceptance_1440: done
  computed_style: done
  req_final_consistency: done
product_data_collection_observability:
  status: applicable
  affected_layers:
  - web
  - api
  - usage_events
  - request_logs
  reason: 卡片聚合和文档查看复用授权读取链路
  na_reason: 不新增任务链路、DB结构、对象存储写入和保留周期
  validation: AC-007/009/011；OpenAPI/Orval、权限与诊断脱敏在apply验证
execution:
  schema_version: 1
  started_at: 2026-10-22 14:05:23
  completed_at: 2026-10-22 18:25:55
  last_event: opsx.apply
---

# 卡片常驻信息标签变更追溯

## 创建事实

REQ已批准且纳入sprint-013，CLI创建Change，尚未实施。原型拆解与18项AC已承接；Readiness为Partially Ready，仅产品视觉证据待实施。

## 创建时的冲突与界面门禁

抽屉560px为示意，保留既有420—760px可拖拽及移动全宽；UI Contract、局部一致契约和Skeleton设计见design.md。原型为Mock，实现需真实API；1440px及关键交互截图、computed style、最终一致性均pending，PNG不在本次生成范围。

## 创建时的验证记录

创建阶段仅运行文档、OpenSpec、Sprint归属和工作流校验，不执行产品测试。18项验收全部未开始；实现证据归属evidence/acceptance。

## 下一步

apply已完成，连续执行opsx-accept；最终结论见当前验收报告。

## 首轮实施记录（已由续接结果补齐）

2026-10-22：实施与隔离验证完成11/13任务；详见[evidence/acceptance/implementation-review.md](evidence/acceptance/implementation-review.md)。真实产品验证待本地Web/API重建授权，尚未applied。18项验收计划已建立，5项包含待补真实产品样本，暂不宣称可归档。

## 真实产品观察补齐（2026-10-22）

用户授权重建Web/API后完成业务卡片与已完成根因抽屉观察；隔离真实HTTP服务完成三阶段、刷新和权限失效。13/13实施任务完成，详见evidence/acceptance/product/review.md；随后同步apply并执行18项验收。不进行正式归档。

## 自动验收结论（2026-10-22）

18/18通过，0失败、0受阻、0待采集；本轮命令执行18次、复用0、去重0。当前证据入口：evidence/acceptance/20261022182642680023-597635c6/summary.md。临时归档预演通过，opsx.accept同步成功，最终archive-readiness为ready。AI Usage两次hook均actual且无warning；不将验收耗时当模型用量。

最终预检曾因6个历史specs目录的未跟踪且已忽略.DS_Store失败（archive delta files unsupported or missing）。已移出至本机临时备份，不修改历史规格正文，复验18/18 ready。建议后续治理将文件系统元数据与非法规格文件分别诊断；本轮未创建Issue或Change。隔离真实HTTP验收服务已停止，业务Web/API保持运行。未执行正式归档。

## 2026-10-22 标签返修

用户确认五档人天及同标签样式；执行中为研发中，canonical applied与首次completed_at保留。返修证据、子文档检查见acceptance-fixes.md。product_data_collection_observability: N/A（本轮仅格式与CSS，原采集、授权和请求链路不变）；affected_layers: web；验证：分档边界、标签样式、根因交互与既有验收。

## 标签返修完成

22项专项测试通过；九阶段×双视口×双主题36张新截图，新旧标签六项样式完全一致；12组根因键盘/焦点检查通过。本地Web已重建，API聚合曾504，在授权内重启API后恢复，实际M/L/XL/XXL标签已观察；临时真实HTTP样本及Mock视觉分别记录。REQ七份子文档一致性扫尾和产品手册校验通过，无API/DB/权限/生成客户端变化。

最终验收包：evidence/acceptance/20261022190522208993-31d85746/summary.md，18/18通过，0失败、0受阻、0待采集；3次命令执行、15次去重、0历史项复用。modify及accept同步通过，保留首次apply完成事实。临时服务均已停止，本地Web/API保持运行，未正式归档。建议验收持续比较同排既有标签而非只检查新标签自身尺寸；本轮未自动创建Issue/Change。

## 第二轮标签间距返修

仅收紧人天分隔点至左右各2px，保留applied及首次completed_at；详见acceptance-fixes.md第二轮。product_data_collection_observability: N/A（纯文本结构及CSS，不变更采集）；affected_layers: web；验证采用当前截图和computed style。

第二轮完成：22项定向测试、36组阶段视觉与共享样式检查、12组根因键盘检查通过。当前Docker构建index-Dh8ZUJtI.js在隔离真实HTTP服务实测分隔点左右各2px；证据见evidence/acceptance/spacing/。REQ子文档与原型、Change规格、Sprint验收/发布说明、公开手册已同步，API/DB/安全/生成客户端无需变更。自动验收包evidence/acceptance/20261022191809580956-9179f514/summary.md：18/18通过，3次命令执行、15次去重，归档预演与最终readiness均ready。Workflow Sync modify/accept均0错误；modify用量estimated_fallback（缺少token_count），accept用量actual。临时服务与验收标签页已清理，本地Web保留最新构建；未正式归档。链路复盘：将固定间距纳入computed style验证可避免字体空格宽度差异；无新增治理需求，未自动创建Issue/Change。
