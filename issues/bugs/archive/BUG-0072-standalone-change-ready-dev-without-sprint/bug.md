---
bug_id: BUG-0072-standalone-change-ready-dev-without-sprint
title: 独立 Change 未纳入迭代却提前显示待开发
status: done
severity: medium
lifecycle_stage: archive
created_at: '2026-10-31 08:15:41'
updated_at: 2026-10-31 10:53:17
related_requirement: null
related_bug: BUG-0039-standalone-change-sprint-membership-false-warning
iteration: null
openspec_changes: []
owner: 产品团队
discovered_at: '2026-10-31'
environment: local Docker
related_change: null
root_cause_status: confirmed
---
# 独立 Change 未纳入迭代却提前显示待开发

## 缺陷概述
需求中心将尚未纳入 Sprint 的独立提案提前放在“待开发”，同时提示缺少归属并禁用开发按钮。阶段展示与开发准入条件不一致，用户无法从卡片主动作直接进入迭代规划。

## 复现条件与步骤
1. 存在无REQ/BUG来源的活动Change，包含有效proposed状态与提案、设计、任务文档。
2. 未在任何有效Sprint的changes列表中纳入该Change。
3. 打开本地需求中心并刷新，定位该对象。
4. 可见卡片处于待开发、提示缺少唯一有效的Sprint归属，主动作仍为禁用的“开始开发”。
本会话实例为 add-archive-tool-version-routing。截图及此前浏览器刷新观察一致；本轮复核相关代码，未触发产品写操作。

## 期望与实际
| 条件 | 期望阶段与提示 | 主要动作 |
|---|---|---|
| 已有提案、未纳入Sprint | 迭代规划，标注“待纳入迭代” | 加入迭代 |
| 已有提案、已纳入唯一有效Sprint | 待开发 | 开始开发 |
| Sprint归属冲突或失效 | 明确阻塞提示，不能伪装成普通未排期 | 核对归属 |
当前无归属对象直接进入待开发；缺少规划入口。冲突或失效时默认留在迭代规划并展示阻塞，细化方案见acceptance.md，待评审确认。

## 根因判断与证据
confirmed（限于无Sprint却进入待开发的分列原因）：`src/backend/app/governance/change_index.py:155` 将proposed直接映射ready-dev，未使用Sprint解析结果。`sprint_id()`解析归属，`action()`在约273行仅将缺少归属作为disabled_reason，未改变阶段或切换加入迭代动作。与用户截图及本会话真实页面观察吻合。
根因不是初始化trace失效，也不是开发权限绕过。多重归属、失效归属的具体产品表现未在本轮逐一运行验证，作为后续负向验收范围，不冒充已复现。

## 影响范围与严重等级
severity: medium。影响独立Change的分列、统计理解及规划操作入口；现有准入保护仍有效，未发现越权、执行事实回退或数据丢失证据。REQ/BUG已有链路、研发中、验收中和已完成阶段需做防回归。

## 修复边界与建议验收
- 保留canonical proposed和原执行时间，不通过修改历史状态来凑列，不自动分配Sprint。
- 无归属、有唯一有效归属、冲突/失效分别验证分列、标注、主动作及开发准入。
- 加入有效Sprint并刷新后进入待开发；归属失效后阻断开发。
- 核对归属入口只用于查看和处理问题，不自动选择某个Sprint或覆盖冲突。
- 未评审前不实施，不修改已归档治理Change。

## 关联与非重复说明
BUG-0039处理已有有效归属却误报缺失，本BUG处理真实未排期却提前进入待开发，修复闭环独立但解析逻辑相关。BUG-0037处理状态缺失造成unknown，并非本次有效proposed分列。

## 产品数据采集与链路观测
product_data_collection_observability: applicable
敏感影响层 affected_layers: 需求中心API投影、Web主动作、Agent Workflow。
validation: 后续检查API阶段与Web分列一致、动作路由正确、准入门禁保留；若引入真实加入迭代操作，复用既有权限和链路观测。当前仅文档生成，DB、日志表、行为事件、Task Trace、请求封装及OpenAPI/Orval修改均N/A；实施时按实际契约变化复核。

## 证据与待完善项
来源：用户三类规则、用户卡片截图、同会话Firefox刷新观察及上述代码路径。仅保留脱敏文字，不存本机路径、用户信息或原始日志。本轮已补齐根因、workaround与acceptance；冲突/失效列位置和只读诊断入口的细化方案供评审确认。

## 完善结论
根因已确认，详见root-cause.md；四类隔离合成对照已执行。冲突/失效归属默认留在迭代规划，核对入口为只读诊断；完整细化方案与待执行验收见acceptance.md，供评审确认。本轮不实施。
