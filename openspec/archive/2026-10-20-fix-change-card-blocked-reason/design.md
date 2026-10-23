---
title: 纯 Change 卡片阻塞诊断修复设计
created_at: '2026-10-20 19:09:48'
updated_at: '2026-10-20 19:09:48'
---

# 纯 Change 卡片阻塞诊断修复设计

## 背景与现状

根因证据见 [BUG-0054-change-card-blocked-reason-missing 根因分析](../../../issues/bugs/review/BUG-0054-change-card-blocked-reason-missing/root-cause.md)。复用已有取证，实施前核对当前并行代码和部署版本，不把历史观察当作当前修复结果。

## 修复方案

保持 readiness 的准入布尔值与归档门禁不变，增加可安全传播的诊断结构：原因码、受影响 AC、必要的仓库相对输入路径、可操作建议。先核对现有接口 schema，优先兼容扩展，不移除既有 status/reason 消费契约。归档准入和 reader 投影不再将所有诊断压成 blocked。

中文展示区分未执行、输入缺失、输入变化及未知错误；未知情况不编造原因。按钮禁用提示与卡片摘要使用同一诊断语义，ready 时清除旧提示。后端输出前脱敏，不把绑定根、原始异常堆栈或配置传给前端；路径只允许授权范围内的仓库相对值。

## 测试策略

逐项映射来源 acceptance.md AC-001 至 AC-005，分别记录命令验证、真实部署与浏览器结果。隔离样本覆盖缺失、变更和拒绝路径，不修改业务证据。实施时创建完整 acceptance-plan 并运行自动验收；当前任务不伪造通过结果。

## 风险与依赖

两条修复可独立设计，共享样本联合验收建议先完成输入解析修复；BUG-0054 可使用独立失败样本验证，不能等待另一条修复而跳过诊断门禁。复用 S10-A002 和治理恢复与归档验收证据分层实践，保留原始失败历史。

## 观测与文档同步

product_data_collection_observability: 已评估；affected_layers: 后端治理读取、归档准入、Web 卡片及部署。新增事件、DB、对象存储和新的 Task Trace N/A：本次修复既有只读判定链路，不新增写入流程。沿用既有请求日志和鉴权边界，诊断不得输出绑定绝对路径或敏感值。validation: 后续接口/模块回归、路径安全及真实部署证据；响应字段如改变须同步 docs/03-api-index.md、OpenAPI/客户端生成及前端测试。

## 验收与量化

原 BUG 的5项 AC 全部通过且当前证据有效后才声明完成。记录首次/复验耗时、工具失败、误阻塞或无详情样本数及实际 Token；无法归属标记 unavailable，不虚构性能改善比例。容量仍为 1 人天。

## 回滚方案

按 proposal.md 回退实现/部署，保留历史证据及原有安全门禁。

## 实施入口矩阵与门禁

| 入口 | 输入及部署形态 | 正向与拒绝 | 验收映射 |
|---|---|---|---|
| CLI readiness | 源码仓库，真实验收计划 | 有效输入一致；变化后失效 | AC-001、AC-003 |
| 部署归档准入 | 当前本地容器，治理投影+可信绑定 | 根级输入读取；越界及缺失拒绝 | AC-001、AC-004 |
| 需求中心卡片 | 既有 API reason 字符串及真实浏览器 | ready 可用；AC-006 真实失效有原因且禁用 | AC-002、AC-003、AC-004 |
| 执行器与完成证明 | 本次不修改执行器/模型调用/完成证明 | 既有门禁保持，跨入口回归验证 | AC-005 |
| 归档 | 临时副本预演 | 仅核对规格合并，不实际归档 | 收尾门禁 |

AC-XCUT: n/a（不新增后台表单、列表、modal或上传）；knowledge_base_refs: pass，复用治理恢复与归档验收证据分层实践。现有截图仅用于缺陷事实，不是视觉复刻需求，无UI结构或样式改动。沿用既有卡片布局和选择器，不新增modal动作。原型/Skeleton门禁不适用；真实状态、按钮disabled和计算样式纳入证据。

product_data_collection_observability: {status: assessed, affected_layers: [governance, web, deployment], reason: '只读输入与既有诊断字符串语义变化；没有新增API字段、DB、request_logs、usage_events、Task Trace或请求封装', validation: '聚焦回归、跨入口门禁、真实部署卡片及脱敏测试'}
