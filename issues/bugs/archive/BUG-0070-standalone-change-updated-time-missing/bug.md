---
title: 独立 Change 卡片更新时间缺失
status: done
severity: medium
created_at: '2026-10-30 09:41:28'
updated_at: 2026-10-31 23:01:58
owner: 产品团队
source: capture.md 与同会话探索证据
lifecycle_stage: archive
iteration: null
bug_id: BUG-0070-standalone-change-updated-time-missing
related_requirement: null
related_bug: null
environment: local
root_cause_status: confirmed
product_data_collection_observability:
  status: applicable
  standard_ref: docs/standards/product-data-collection-observability.md
  affected_layers:
  - web
  - api
  - governance
  reason: 涉及卡片元数据来源与 API 投影；本次仅记录，不修改采集或请求契约。DB、部署、对象存储和安全权限无本次变更。
  validation: 复用探索中的页面与源码证据；后续检查字段来源、权限与日志脱敏，客户端生成依实际 API 差异确定。
discovered_at: '2026-10-30 09:33:58'
related_change: null
---

# 独立 Change 卡片更新时间缺失

## 现象与复现
2026-10-30 同会话 Firefox 已登录的本地 /requirements 页面，刷新至 09:33:58 后，fix-archive-finalization-consistency 卡片仍显示“更新时间未知”。该对象来源 sprint-016，研发任务 7/7；来源迭代不等于本 BUG 已纳入该迭代。

1. 打开需求中心，定位上述独立 Change。
2. 刷新看板，观察卡片底部更新时间。
3. 对照 Change trace 元数据与卡片投影。

## 期望与实际
期望：有效业务更新时间可显示且来源可追溯，旧数据兼容不虚构更新时间。实际：Change trace 无 created_at、updated_at，虽有 execution.started_at/completed_at，卡片仅读取前两个字段，最终显示未知。

## 已确认的证据与边界
- 用户附件截图和本轮前一探索中的 Firefox 刷新观察一致；复用会话观察，不声称本次再次浏览或已保存截图附件。
- openspec/changes/fix-archive-finalization-consistency/trace.md 缺少上述两个字段。
- src/backend/app/governance/change_index.py 的 cards 只以 trace.updated_at 或 created_at 投影 updated_at。
- src/web/src/pages/catalog/RequirementCenterPage.tsx 的 rc-updated 对无有效格式显示“更新时间未知”。
- 显示链路根因 confirmed；具体哪个创建/同步入口遗漏维护字段仍需后续追溯，不能将执行完成时间直接当作最后更新时间。

## 判重与拆分
已检查 BUG CHANGELOG 与注册表。用户管理时间展示问题属于其他模块；BUG-0039 为 Sprint 归属误报、BUG-0018 为验收来源识别，均非本时间字段链路。与归档按钮检查入口故障修复面不同，独立记录。

## 建议验收
覆盖新建、apply、modify、归档后的时间维护及历史缺字段兼容；刷新后显示与事实源一致；不得把文件复制时间或当前查询时间冒充业务更新时间。初判 medium：影响进度判断但无数据丢失或执行阻断证据。

## 影响范围与修复边界
影响需求中心无来源 Issue 的独立 Change 卡片；其他卡片是否有相同问题需后续回归，不扩张为全站故障。本 BUG 与独立优先级需求 REQ-0057 分开交付。保留原有对象授权、来源识别和归档门禁。

## 文档与实现同步要求
后续修复按实际差异同步 UI、API 字段契约与测试；客户端生成由接口变化决定。当前仅正式缺陷文档，无 API、DB、UI、部署或安全配置改动。不得以文档生成冒充修复完成。

## 当前状态与证据时效
本轮 bug-complete 已补齐 root-cause.md、workaround.md、acceptance.md；根因证据校验通过，已评审批准修复，已纳入 sprint-018 并创建 fix-standalone-change-updated-time；实现与7项验收已完成，待正式归档。用户明确授权复用同会话探索证据，本轮重新读取相关源码和目标 trace，确认上述数据与分支仍存在。浏览器事实来自 09:33:58 刷新观察，不声称新一轮运行态验收。

## 已排除判断与后续定位
显示 unknown 不是优先级字段造成：时间与 priority 在投影中独立读取。源 trace 缺字段可以直接解释现象，不是已证实的时区错误。创建/同步入口为何没有维护时间仍待修复设计定位，该缺口不改变已确认的显示链路根因。后续选择兼容数据时须保留“创建时间”“执行完成时间”和“更新时间”的不同语义。

## 完善补证

执行同步 transition 只替换已有 updated_at，不插入缺字段；详见 root-cause.md E4。原创建入口的历史归责仍未知，不将此缺口冒充已复现历史过程。
