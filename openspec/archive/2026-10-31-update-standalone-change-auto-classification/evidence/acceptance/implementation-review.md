---
title: 独立 Change 自动分级实施与验收证据
created_at: '2026-11-01 00:57:00'
updated_at: '2026-11-01 00:57:00'
---

# 独立 Change 自动分级实施与验收证据

## 结构确认与实现
用户已确认“只读展示严重性/优先级及待评估、待核实状态，删除设置区，保留标题、文档和交付动作；原型双列仅用于比较状态”，沿用现有卡片样式。未新增 CSS；删除 ChangePriorityEditor 的卡片挂载与回调，保留旧接口兼容及其执行前保护。

| 区域/动作 | 产品 selector | 验收结论 |
|---|---|---|
| 卡片、元信息 | .rc-card、.rc-card-meta | 保留既有布局；标签独立于负责人、工作量 |
| 分级 | .rc-priority-tag、.rc-severity-tag | 按维度显示，有效/待评估/待核实 |
| 设置、保存 | change-priority-edit/editor/save | 所有阶段不存在，无可聚焦替代入口 |
| 标题、文档 | .rc-card-title、.rc-docs | 保留详情和文档抽屉 |
| 开发、返修、验收、归档 | .rc-card-actions、change-stage-action、view-execution | 原动作组件及权限保留，无新增 modal |

## 证据来源与范围
真实产品：本地既有后端、治理控制器及 Web 更新后，通过浏览器读取历史 fix 和非 fix 卡片。fix 显示严重性待评估，非 fix 显示优先级待评估；无编辑入口，不写历史等级。actual-fix-* 为真实页面双视口双主题截图，computed-style.json 为真实窄屏样式。
隔离浏览器样本：mock-*.jpg 和 mock-computed-style.json 覆盖四阶段×1440/390×深浅主题，共16组合，每组6种维度/状态。使用实际 RequirementCenterPage 组件与现有 CSS、隔离 fetch；不是业务 API 数据或产品对话。visual-matrix.jpg 为截图索引；mock-fixture.tsx.txt 保留样本构造。全部卡片无内部横向溢出，编辑节点0；字号/行高/内边距与原组件 token 一致。长看板正常横向滚动，手机屏按现有布局纵向滚动。截图代表可见区，完整六状态由DOM及组件回归补充。
真实 CLI：cli-observation.json 为临时仓库中的 openspec new change → Agent 提供评估 → opsx.propose 完成校验。fix/high、non_fix/P2、重试不变、pending拒绝均观察通过。scripts/test_change_classification_workflow.py 可重跑；不调用产品 Chat，不将其声称为模型行为评测。
请求证据：前端测试记录 fetch 调用，全部阶段无卡片 PUT priority；这是合成请求回归，不是浏览器 HAR。旧接口权限、版本、维护窗口、执行前复核及审计沿用既有回归，fix新增409保护。未新增行为点击、DB表、数据保留期或Task Trace事件。

## 视觉签认
Codex 检查真实截图、16组合截图索引和代表性全尺寸图：保留区沿用现有样式；设置区已删除；标签可读，窄屏卡片宽266px且无内部溢出。主题以实际 main[data-theme] 核对；390截图以浏览器 innerWidth/innerHeight 核对。隐藏页尺寸不生效的一批错误证据已被重新采集覆盖，不参与最终结论。

## 范围与限制
自动评估由创建 Agent 根据 proposal/design/spec 判断，校验器验证类型、合法级别、理由、证据引用、主体和时间，不靠关键词或默认等级制造结论。来源 Issue 继续继承；已有历史未批量迁移。真实库没有各阶段全部异常样本，因此完整状态矩阵使用隔离数据，真实产品观察只声明实际存在样本。没有新建正式测试 Issue/Change，没有执行真实归档。

## 文档一致性
requirement、business-flow、user-stories、acceptance、trace 与 prototype 逐项核对：类型口径、只读入口、来源保护、历史兼容与实际实现一致；原型两列仅比较状态。API索引、OpenAPI和生成客户端已同步；无数据库迁移、部署拓扑或安全权限扩大。现有本地服务更新仅用于验证，不是正式发布。
