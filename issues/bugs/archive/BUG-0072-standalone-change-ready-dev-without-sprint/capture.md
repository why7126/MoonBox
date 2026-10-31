---
bug_id: BUG-0072-standalone-change-ready-dev-without-sprint
title: 独立 Change 未纳入迭代却提前显示待开发
status: done
severity: medium
lifecycle_stage: archive
created_at: '2026-10-31 08:14:12'
updated_at: 2026-10-31 10:53:17
related_requirement: null
related_bug: BUG-0039-standalone-change-sprint-membership-false-warning
iteration: null
openspec_changes: []
---
# 独立 Change 未纳入迭代却提前显示待开发

## 现象与证据
用户截图与同会话本地需求中心观察：add-archive-tool-version-routing 没有有效 Sprint 归属，却在待开发列显示，卡片提示缺少唯一有效的 Sprint 归属且开始开发禁用。ChangeIndex 将 proposed 直接映射 ready-dev，Sprint 检查仅在动作层阻断。来源为本会话 explore；当前治理初始化修复已归档，但不包含本次产品分列调整。

## 复现步骤
1. 准备有 proposal、design、tasks、有效 proposed trace 的独立 Change，不纳入任何 Sprint。
2. 打开需求中心并刷新，观察卡片所在列、提示、主动作和统计。
3. 分别核对唯一有效归属、多重归属及失效归属的显示和动作。

## 期望与验收规则
| 独立 Change 情况 | 期望展示 | 主要动作 |
|---|---|---|
| 已有提案、未纳入 Sprint | 迭代规划，标注“待纳入迭代” | 加入迭代 |
| 已有提案、已纳入唯一有效 Sprint | 待开发 | 开始开发 |
| Sprint 归属冲突或失效 | 保留明确阻塞提示 | 核对归属 |

保留底层 proposed 事实和开发准入保护；禁止自动分配 Sprint 或将冲突当作普通未排期。覆盖分列、统计、主动作、无归属到有效归属后的刷新及失效后的阻断；REQ/BUG既有流转不受影响。归属冲突或失效时的具体列位置待完善阶段明确，不擅自补充用户未指定规则。

## 影响与分级
medium：阶段语义误导与规划入口缺失，现有开发按钮保护仍有效，无越权或数据丢失证据。三种情况属于同一分列与动作决策，一条缺陷闭环。

## 重复检查
BUG-0039 是有效归属被误报缺失，本条是真实未归属却进入待开发；关联但独立。BUG-0037是缺失状态导致unknown，与本条有效proposed状态不同。

## 产品数据采集与链路观测
product_data_collection_observability: applicable
affected_layers: 需求中心API投影、Web主动作、Agent Workflow
validation: 后续验证阶段与动作一致、保留准入保护；本次仅capture，不新增API字段、DB、日志或行为采集。是否需调整请求契约在完善阶段核定。

## 附件
用户本会话提供的待开发卡片截图；本次仅保存脱敏文字证据，不复制本机路径或原始日志。
