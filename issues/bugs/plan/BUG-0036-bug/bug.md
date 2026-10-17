---
bug_id: BUG-0036-bug
title: 需求中心 Bug 生成治理链路验收隔离夹具
severity: low
owner: user_b6aa2646805846d49532232d30dcff48
status: draft
discovered_at: null
environment: 本地验收隔离环境（来源声明，运行态待验证）
related_requirement: null
related_change: null
---

# 需求中心 Bug 生成治理链路验收隔离夹具

## 现象

本对象是本地验收测试夹具，用于验证需求中心 bug-generate、候选、自动应用、状态投影与后续治理命令链路，不代表新发现的产品缺陷，不纳入正式交付或 Sprint。来源材料未提供实际异常或验收结果。

来源关联标识 BUG-0025-requirement-center-command-chain-write-gap 仅保留为背景事实，不替代当前编号，也不据此推定同一根因。capture 的创建时间不是已确认的缺陷发现时间。

## 复现与验收步骤

以下是待执行的夹具验收流程，不是已复现缺陷：

1. 在本地隔离环境进入需求中心采集池，定位 BUG-0036-bug。
2. 发送 `/bug-generate BUG-0036-bug`，观察生成任务与候选记录。
3. 检查应用记录，确认生成 bug.md，并更新已有 trace.md。
4. 核对 trace、注册表、看板与产品页面的标题和状态是否一致。
5. 在受控失败场景下检查旧成果是否保留，记录失败阶段与应用结果。

## 期望与实际

| 检查项 | 期望 | 已知实际 |
|---|---|---|
| 候选及应用 | 留下候选与应用记录 | capture 有来源引用，但未提供本次生成与应用的运行态证据 |
| 文档生成 | 生成 bug.md，trace 更新为 draft | 本次执行前仅有 capture.md 与 trace.md，状态为 captured |
| 状态一致 | trace、注册表、看板和页面一致 | 执行前治理记录均为 captured；生成后的治理状态由 Workflow Sync 核验，页面待验收 |
| 异常保护 | 失败时保留旧成果 | 未提供故障注入或异常执行证据 |

## 影响范围

验收范围包括需求中心生成命令、候选应用、文档持久化及状态投影。无已证实的生产用户影响、数据损坏或服务不可用。本次仅生成文档并同步治理状态，不修改业务代码、API、数据库、UI、部署、安全或客户端生成产物。

## 严重等级说明

沿用 trace 的 low，仅用于夹具分级结构，不表示已确认真实缺陷或实际影响。

## 证据与根因摘要

根因状态：unknown。没有实际异常，无法建立产品缺陷根因，不将夹具用途视为已确认缺陷。

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | data_sample | issues/bugs/plan/BUG-0036-bug/capture.md | 明确为隔离验收夹具，无实际异常结果 | 不能认定真实产品缺陷 |
| E2 | data_sample | issues/bugs/plan/BUG-0036-bug/trace.md | 执行前 captured，iteration 为空，无关联 Change | 尚未进入正式交付 |
| E3 | data_sample | issues/bugs/_registry.yaml、issues/bugs/CHANGELOG.md | 执行前均为 captured | 生成前索引与 trace 一致 |

已聚焦核对来源快照和仓库记录。本轮未执行浏览器产品链路验收；当前提供的工具没有浏览器会话连接入口，未据此判断产品无法访问。文件生成与治理状态同步不能证明候选自动应用或异常保护验收通过。

如夹具验收发生实际异常，需要返回：触发动作、出现时间、失败阶段、预期与实际、脱敏错误摘要及请求状态。操作时在需求中心定位本夹具，执行生成，检查候选和应用结果，再比较页面与治理记录。以步骤列表及预期/实际表返回，不提供凭证、完整会话或客户数据。没有异常证据前保持根因未知，不推进修复评审。
