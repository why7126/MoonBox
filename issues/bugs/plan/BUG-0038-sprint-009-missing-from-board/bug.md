---
bug_id: BUG-0038-sprint-009-missing-from-board
title: 需求看板未显示已存在的 sprint-009 迭代
severity: medium
status: enriching
owner: MoonBox 产品团队
discovered_at: '2026-10-11 09:57:28'
environment: local Docker，Firefox，需求中心 /requirements
related_requirement: REQ-0012-frontend-requirement-center
related_change: null
---

# 需求看板未显示已存在的 sprint-009 迭代

## 现象

当前仓库的 `iterations/change/sprint-009/sprint.yaml` 存在，状态为 `planning`。本地 Firefox 打开并重新加载需求中心后，Sprint 统计仍为“已完成 8 个，总体 8 个”，未计入该迭代。页面中的短 ID `BUG-0038` 指向“隔离版本冲突与重试验收夹具”，与当前仓库 `BUG-0038-sprint-009-missing-from-board` 不是同一对象，表明页面展示的数据与当前仓库不一致。

## 复现

1. 在当前仓库核对 `iterations/change/sprint-009/sprint.yaml` 的 `sprint_id: sprint-009`、`status: planning`。
2. 在本地 Firefox 打开 `http://localhost:39002/requirements`，重新加载，等待需求中心显示“已同步”。
3. 查看 Sprint 统计和筛选选项，并对照页面的 `BUG-0038` 标题与当前仓库的缺陷记录。

## 期望与实际

| 项目 | 期望 | 实际 |
|---|---|---|
| Sprint 总览与选项 | 对当前所选项目的数据源，计入有效的 `sprint-009` 并标明“规划中” | 页面刷新后仍显示 8/8；当前仓库已有 `sprint-009` |
| 数据来源 | 明确所选项目、治理数据来源和快照版本，使用户能判断是否正在查看目标仓库 | 页面显示“已同步”，但无法从该状态辨别其与当前仓库是否一致 |
| 异常处理 | 数据源或快照与目标项目不一致时提供可诊断提示与恢复入口 | 页面继续展示统计和对象卡片，未解释上述身份错位 |

## 影响范围与严重等级

严重等级为 `medium`。Sprint 总数、筛选和后续规划判断可能受到误导；相同短 ID 指向不同对象还会使用户误操作错误的缺陷卡片。目前没有 Sprint 文件被删除或业务数据被修改的证据。该问题应从项目绑定、快照一致性和产品提示共同闭环，不以硬编码 `sprint-009` 或单独修正计数作为完成条件。

## 证据与根因状态

| 证据 | 来源 | 支持的判断 |
|---|---|---|
| `sprint-009` 文件存在且为 `planning` | 当前仓库 `iterations/change/sprint-009/sprint.yaml` | 文件满足现有 Sprint 列表的状态条件 |
| 刷新后“已同步”，Sprint 仍为 8/8，且 `BUG-0038` 标题不同 | 2026-10-11 本地 Firefox `/requirements` 可见结果 | 页面当前展示的数据与本仓库不一致；刷新未消除错位 |
| 后端从已授权项目绑定的治理目录快照构建看板，Sprint 列表扫描快照内的 `iterations/change` | `src/backend/app/governance/reader.py`、`src/backend/app/services/requirement_center.py` | 项目绑定或快照来源是最小关键核查点 |

根因状态：`probable`。运行服务实际的项目绑定目录、快照版本及需求中心上下文响应尚未取得，不能确认是绑定错误、源目录滞后还是其他快照路径问题。已尝试 Firefox 刷新与代码路径核对；容器 API 访问受限，未取得运行容器绑定事实。此前浏览器清单曾超时，随后直接连接 Firefox 成功并完成刷新取证。

## 待补证与产品修复方向

在当前登录项目的需求中心，核对项目标识、绑定修订、脱敏后的治理目录身份、快照版本以及上下文接口的 `sprint_metrics`、`sprint_options`、`sprint_option_details`；同时在服务端核对绑定根目录中是否存在 `iterations/change/sprint-009/sprint.yaml`。不得提供凭证、Cookie、Authorization header、完整本机路径或客户数据。

修复应保证统计、筛选和卡片使用同一已授权快照；向用户展示可辨认的数据来源与同步状态；在绑定不符、源目录滞后或快照冲突时给出明确提示和重新连接或同步入口。验收需同时覆盖正确项目、错误绑定、旧快照、规划中 Sprint，以及同短 ID 异对象场景。
