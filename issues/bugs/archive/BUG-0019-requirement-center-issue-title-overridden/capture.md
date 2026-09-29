---
bug_id: BUG-0019-requirement-center-issue-title-overridden
title: 需求中心阶段业务标题来源与文档中文标题校验采集记录
status: done
created_at: '2026-09-14 10:25:53'
updated_at: 2026-09-29 14:18:37
related_requirement: null
related_bug: null
severity: medium
---

# 需求中心阶段业务标题来源与文档中文标题校验采集记录

## 现象

需求中心 REQ/BUG 卡片关联唯一 Change 后，主标题优先显示 Change 文档提取标题，覆盖已有的正确 Issue 业务标题。两个样本来自用户在验收阶段的实际观察，属于同一页面、同一根因，合并为一条缺陷。

严重度初判 medium：影响需求/缺陷识别及跨阶段标题一致性；当前未发现数据丢失、权限越界或操作链路中断证据。
环境：用户未明确部署方式；前序探索已使用本仓库代码与治理文件完成只读标题函数验证，未进行浏览器重放。

## 复现步骤

1. 打开需求中心，定位关联唯一 Change 的 REQ/BUG 卡片。
2. 对照用户报告时验收阶段的 BUG-0016-capture 与 REQ-0022-local-project-import-product-iteration。
3. 对比卡片主标题、Issue 注册表 title 和关联 Change trace.md 一级标题。
4. 注意：本次 capture 时 BUG-0016 已迁入归档，验收阶段是历史观察；后续回归使用受控验收阶段数据，并覆盖已完成阶段。

## 期望 vs 实际

| 样本 | 实际标题（用户报告及前序函数验证） | 期望标题 |
|---|---|---|
| BUG-0016-capture | BUG-0016修复追溯 | 需求中心刷新缓慢，MD 文档右侧抽屉加载缓慢或无法加载 |
| REQ-0022-local-project-import-product-iteration | Change 实施与验证记录 | 本地存量项目导入 MoonBox 并支持产品内迭代闭环 |

历史采集方案已由本轮阶段来源契约替代，当前目标以 bug.md 为准。

## 已有探索证据

- issues/bugs/_registry.yaml 与 issues/requirements/_registry.yaml 已存在两个样本的正确 title。
- src/backend/app/governance/change_index.py 的 chinese_title 从 proposal.md、design.md、trace.md 回退提取一级标题，仅以包含中文及固定通用标题黑名单过滤，接受上述追溯标题。
- 同文件 ChangeIndex.cards 在唯一关联 Change 时设置 current_change。
- src/web/src/pages/catalog/RequirementCenterPage.tsx 使用 current_change.title || issue.title 渲染主标题。
- 前序 /explore 只读执行源码标题提取函数，两个输出均与用户报告一致。根因已有代码路径与函数复现证据，待 bug-complete 汇入正式根因证据文档。

## 当前范围

按 bug.md 的阶段来源契约与全部生成文档中文标题要求执行。此前全阶段统一 Issue 标题方案已被用户新要求替代。原两个样本作为 proposal 标题缺失时的回退回归，不再要求有效 proposal 标题不得展示。
