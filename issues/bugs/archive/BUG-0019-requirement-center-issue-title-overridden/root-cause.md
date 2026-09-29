---
bug_id: BUG-0019-requirement-center-issue-title-overridden
created_at: '2026-09-14 11:05:00'
updated_at: '2026-09-15 22:56:10'
title: 需求中心阶段业务标题来源与文档中文标题校验根因分析
---

# 需求中心阶段业务标题来源与文档中文标题校验根因分析

## 根因状态

status: confirmed

确认范围：当前源码及样本文件能够解释用户反馈的标题取值异常。未进行浏览器重放，不代表已完成修复或视觉验收。

## 现象

用户报告验收阶段 BUG-0016-capture 显示“BUG-0016修复追溯”，REQ-0022-local-project-import-product-iteration 显示“Change 实施与验证记录”。两条注册表已有正确 Issue 业务标题。本次完善时两个样本均为 done，归档文件仍能复现标题错取，历史验收状态不回写到真实数据。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | reproduction | capture.md：用户样本表 | 两个验收阶段卡片显示追溯名称 | 用户可见现象 |
| E2 | data_sample | issues/bugs/_registry.yaml；issues/requirements/_registry.yaml | 两个样本 title 分别为“需求中心刷新缓慢，MD 文档右侧抽屉加载缓慢或无法加载”和“本地存量项目导入 MoonBox 并支持产品内迭代闭环” | 正确数据已存在 |
| E3 | code_path | src/backend/app/services/requirement_center.py：_build_issue | 从 entry.title 生成 issue.title，缺失回退 Issue ID | Issue 字段取值正常 |
| E4 | code_path | src/backend/app/governance/change_index.py：chinese_title、ChangeIndex.cards | 唯一关联 Change 设置 current_change；含中文且不在黑名单的 trace 一级标题被接受 | 非业务标题进入 current_change.title |
| E5 | code_path | src/web/src/pages/catalog/RequirementCenterPage.tsx：renderIssueCard | 主标题优先 current_change.title，非空时覆盖 issue.title；没有阶段限制 | 覆盖发生于卡片展示 |
| E6 | reproduction | 下述只读函数复核步骤与结果 | 前次源码对两个归档样本返回用户反馈的错误标题 | 提取链路可重复验证 |

## 已排除假设

| 假设 | 排除依据 |
|---|---|
| 注册表业务标题缺失或错误 | E2 正确标题已存在 |
| 验收列头中文映射错误 | E5 异常为卡片主标题，列头使用独立静态映射 |
| 仅某一条 Issue 文档内容错误 | E1、E6 两类对象均触发同一分支 |
| 仅由缓存造成 | E6 绕过 HTTP 缓存直接执行源码提取函数仍返回错误值；未据此排除其他独立缓存问题 |

## 已确认根因

既有路径没有按阶段区分注册表、Issue 主文档及 proposal 的业务标题来源；Change 提取允许 trace/design 及通用追溯标题进入主标题。新契约允许开发及后续阶段采用唯一 Change proposal 业务标题，因此“任何 Change 标题覆盖都是错误”的旧判断不再适用。

## 修复方向

以 bug.md 的阶段来源表、有效中文业务标题规则和生成校验契约为准。读取端限制来源，生成端确保标题，历史缺失降级提示。新扩展的所有生成入口校验要求属于用户确定的目标，不把未逐一审计的入口写为已确认根因。

## 验证闭环

2026-09-14 历史只读复核步骤：

1. 从当前源码 AST 提取 _frontmatter 与 chinese_title 函数，仅去除 _frontmatter 的缓存装饰器，用 yaml、Path、re 和 legacy._frontmatter 绑定执行；未导入完整服务或连接数据库。
2. 在两个注册表中按完整样本 ID 定位 title 和 status。
3. 读取 openspec/archive/2026-09-14-fix-requirement-center-loading-and-errors/ 下 proposal.md、design.md、trace.md，以及 openspec/archive/2026-09-14-add-local-project-governance-loop/ 下对应三份文件。
4. 调用 chinese_title，断言分别等于“BUG-0016修复追溯”“Change 实施与验证记录”，且均不等于注册表 title。
5. 对照 renderIssueCard 的非空优先表达式确认展示分支。

结果：2/2 错取分支复现，命令退出 0；两个样本当前状态均为 done。此结果证明当前缺陷存在，不是回归通过。修复后需要执行 acceptance.md 的全部用例，再补浏览器真实观察与 1440px 标题证据。

## 本轮代码复核

2026-09-15 核对 renderIssueCard 仍使用 current_change.title 优先；chinese_title 仍读取 trace 字段及 proposal/design/trace 文档。其黑名单现已引入 DELIVERY_EVIDENCE_HEADINGS，旧 2/2 具体输出仅作历史证据，本轮未重新声称这两个提取结果不变。跨来源提取与阶段契约缺失仍有直接代码证据。
