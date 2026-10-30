---
bug_id: BUG-0071-change-summary-acceptance-check-entry-missing
title: 独立 Change 归档按钮禁用且缺少验收检查入口
status: pending_review
severity: high
created_at: '2026-10-30 09:41:28'
updated_at: 2026-10-30 09:49:12
owner: 产品团队
source: capture.md 与同会话探索证据
lifecycle_stage: plan
environment: local
iteration: null
related_requirement: null
related_bug: BUG-0054-change-card-blocked-reason-missing
related_bugs:
- BUG-0054-change-card-blocked-reason-missing
- BUG-0056-requirement-center-context-load-latency
root_cause_status: confirmed
product_data_collection_observability:
  status: applicable
  standard_ref: docs/standards/product-data-collection-observability.md
  affected_layers:
  - web
  - api
  - web_request_wrapper
  - usage_events
  - request_logs
  reason: 涉及卡片级验收检查请求和状态回填；后续执行归档仍走现有授权及 Task Trace，不以检查替代执行授权。
  validation: 本次复用浏览器刷新观察与代码路径，未执行归档；后续验证检查权限、行为与请求关联、失败重试、缓存失效及脱敏。DB、部署、对象存储暂无修改目标，客户端生成视
    API 契约差异决定。
discovered_at: '2026-10-30 09:33:58'
related_change: null
---

# 独立 Change 归档按钮禁用且缺少验收检查入口

## 现象与复现
2026-10-30 同会话 Firefox 已登录本地 /requirements，刷新至 09:33:58，fix-archive-finalization-consistency（来源 sprint-016）处于验收中，研发 7/7，“完成 / 归档”禁用，辅助提示为“验收待检查”。卡片没有执行对应验收检查的入口。

1. 打开需求中心并定位上述独立 Change。
2. 刷新看板，观察禁用按钮和提示。
3. 查看卡片动作，无法发起按对象的验收条件检查以解除待检查态。

## 期望与实际
期望：摘要首屏可延后重检查，但提供显式检查入口；检查通过才开放归档，不通过展示具体原因，失败允许重试。检查不自动归档、不放宽服务端门禁。
实际：摘要响应将验收态强制设为“验收待检查”并禁用归档，前端隐藏该提示正文且没有检查入口，刷新仍回到同一状态。

## 根因证据与限制
- 浏览器证据：复用前一 explore 的刷新后 AX 状态与用户截图；本次未保存新截图附件，未执行归档。
- src/web/src/pages/catalog/RequirementCenterPage.tsx 的 loadContext 请求 context?view=summary。
- src/backend/app/governance/reader.py 在 summary 且 acceptance 时设置 checks_deferred、acceptance_blocked_reason 和 action.disabled_reason。
- src/backend/app/governance/change_index.py 的 acceptance_source_reason 在摘要模式直接返回“验收待检查”。
- RequirementCenterPage.tsx 的 renderIssueCard 隐藏该提示，按钮因 tip 非空被禁用；openIssueDetail 对 Change 仅打开文档。
- 根因为 confirmed 的范围是摘要检查与交互断点。09:13 完整验收报告 passed 仅为历史事实，未重新验证当前输入指纹，不宣称对象已满足归档条件。

## 判重与用户决策
已检查 BUG CHANGELOG、注册表及候选 capture。BUG-0054 已 done/archive，修复已知阻塞原因仅显示 blocked；BUG-0056 已 done/archive，为首屏性能优化。当前是摘要路径下未检查状态缺少主动检查入口。用户明确选择新建关联 BUG，独立修复并保留旧归档事实。BUG-0053 的部署输入解析、BUG-0035 的进度投影也不等同本触发路径。

## 建议验收与严重度
- 摘要加载后可从卡片发起只读验收检查，明确区分待检查、检查中、通过、阻塞、失败重试。
- 通过才启用归档；阻塞显示具体原因及处理方向，不以任务 7/7 代替验收通过。
- 覆盖无权限、证据过期、多卡、切换项目、刷新及重复检查；不串用对象结果，不退回全量首屏重检查。
- 保留归档独立确认与服务端授权门禁，兼容关联 Issue 卡及独立 Change。
- 初判 high：核心交付操作被 UI 断点阻断；无全站不可用、数据丢失或安全事件证据。

## 影响范围与修复边界
影响需求中心无来源 Issue 的独立 Change 卡片；其他卡片是否有相同问题需后续回归，不扩张为全站故障。本 BUG 与独立优先级需求 REQ-0057 分开交付。保留原有对象授权、来源识别和归档门禁。

## 文档与实现同步要求
后续修复按实际差异同步 UI、API 字段契约与测试；客户端生成由接口变化决定。当前仅正式缺陷文档，无 API、DB、UI、部署或安全配置改动。不得以文档生成冒充修复完成。

## 当前状态与证据时效
本轮 bug-complete 已补齐 root-cause.md、workaround.md、acceptance.md；根因证据校验通过后进入 pending_review，尚未评审或纳入 Sprint。用户明确授权复用同会话探索证据，本轮重新读取相关源码和目标 trace，确认上述数据与分支仍存在。浏览器事实来自 09:33:58 刷新观察，不声称新一轮运行态验收。

## 已排除判断与后续定位
研发 7/7 不能证明验收有效，也不能解除归档保护。页面已有 sprint-016 标签，当前 disabled_reason 明确是“验收待检查”，不是本样本缺少 Sprint。现有完整通过报告不足以证明当前 ready；后续修复需调用真实只读门禁，检查完成后再次按对象版本验证再归档。单对象检查不执行验收计划中的命令，不自动发送 Agent 消息。
