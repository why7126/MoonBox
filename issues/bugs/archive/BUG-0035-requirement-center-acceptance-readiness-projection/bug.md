---
bug_id: BUG-0035-requirement-center-acceptance-readiness-projection
title: 需求中心卡片验收进度与归档门禁不一致且验收文档入口消失
status: done
owner: 产品团队
discovered_at: 2026-10-09 22:32:00
environment: local Docker
related_requirement: REQ-0012-frontend-requirement-center
related_bug: BUG-0023-requirement-center-acceptance-progress-task-classification
related_change: fix-requirement-center-acceptance-readiness-projection
created_at: 2026-10-09 22:38:20
updated_at: 2026-10-13 08:26:09
severity: medium
---

# 需求中心卡片验收进度与归档门禁不一致且验收文档入口消失

## 现象

需求中心 BUG-0025 的验收中卡片显示“研发 41/41、测试 37/37”，并提供“完成 / 归档”动作；关联 Chat 工作台实际执行 `/opsx-archive` 时，因产品复验和交付证据未完成而阻断。卡片未表达这些待验收项，已生成的 `acceptance.md` 等 Issue 文档在进入后续阶段或关联 Change 后也可能从卡片消失。

用户补充的范围是：已生成、属于当前授权对象且可读取的治理 MD 文档，在后续阶段持续提供入口；Issue、关联 Change 和 Sprint 文档应区分来源。文档持续可见不改变阶段写入权限，也不为不存在的文件生成虚假入口。

## 复现

1. 打开需求中心，定位 BUG-0025 验收中卡片，查看进度、文档入口和“完成 / 归档”动作。
2. 对照关联 Change 的 `tasks.md` 和 BUG 的 `acceptance.md`：研发、测试任务已勾选，但验收项仍待产品复验。
3. 从卡片进入 Chat 执行 `/opsx-archive BUG-0025-requirement-center-command-chain-write-gap`，观察归档门禁反馈。
4. 对照其他已生成 MD 文档，检查对象从待评审、已评审、Sprint 规划、待开发、研发中、验收中到完成后，入口是否持续可达。

## 期望与实际

| 检查点 | 期望 | 实际 |
|---|---|---|
| 进度 | 研发、测试任务进度与验收结论分别显示；待验收或缺证据时给出待办摘要 | 卡片显示任务满格，未反映 `acceptance.md` 的待验证状态 |
| 归档 | 卡片动作提示与服务端归档门禁一致；阻断时说明原因并能打开证据文档 | 卡片展示“完成 / 归档”，Chat 归档被交付证据门禁阻断 |
| 文档 | 已生成且可读取的治理 MD 在后续阶段持续可达；同名文档标明 Issue、Change 或 Sprint 来源 | 前端按阶段白名单隐藏文档；关联 Change 后，后端会用 Change 清单替代部分 Issue 文档 |

## 影响范围与严重等级

- 影响需求中心 REQ/BUG 卡片的验收判断、文档追溯及归档准备；关联 Change 的卡片文档聚合也需核对。
- 初判 `medium`：可能误导用户以为已满足归档条件，但现有 Chat 归档门禁仍能阻断本例；暂无越权归档或数据丢失证据。
- BUG-0023 已解决 `tasks.md` 分类统计，BUG-0025 是本次复现实例；本缺陷独立覆盖 `acceptance.md` 验收投影、归档提示及已生成文档的持续展示。

## 根因状态与证据

**状态：confirmed（卡片展示与文档入口路径）。** 代码和现有测试可直接解释已生成文档随阶段消失、人工验收待办未进入卡片提示的触发条件。归档门禁本身保持阻断；所有文档类型和阶段的实际影响范围仍需逐项回归。

| 证据 | 来源 | 观察与判断 |
|---|---|---|
| E1 用户截图 | 本次对话的需求中心卡片与 Chat 归档反馈 | 同一 BUG 显示任务满格与归档入口，而实际归档反馈 AC-051、AC-052 待复验及视觉证据不足；原图未复制到仓库 |
| E2 代码路径 | `src/backend/app/services/requirement_center.py` 的 `_build_issue`、`_display_document_names` | 人工验收待办数固定为 0；关联 Change 后优先取 Change 文档，仅特例保留 Issue trace |
| E3 代码路径与测试 | `src/web/src/pages/catalog/RequirementCenterPage.tsx` 的 `stageVisibleDocs`、`visibleIssueDocuments`、`canArchive`；`src/web/src/requirement-center.test.tsx` 的阶段过滤用例 | 前端按阶段过滤已存在文档，并以测试进度和人工验收待办数判断归档入口可见性；现有测试明确断言部分文档被隐藏 |
| E4 聚焦回归 | `uv run pytest tests/test_governance_board.py -q -k 'trace_always_targets_issue or missing_issue_trace'` | 后端 23 项通过，确认 Issue trace 在各阶段保持正确来源且缺失时不借用 Change trace；同名来源必须区分 |

前端阶段过滤用例在当前 Node 25 / Vitest 环境中于测试初始化时报 `window.localStorage.clear is not a function`，尚未进入文档可见性断言。已尝试关闭实验性 Web Storage 及指定临时 localStorage 文件，结果相同；因此 E3 的测试断言作为现有代码事实，不声明本轮前端回归通过。用户提供的实际卡片与 Chat 截图、后端路径和前端过滤代码已经分别证明本例的展示偏差和触发分支。

## 待完善事项

- 定义 `acceptance.md` 中验收标准、执行结果、人工复验与证据缺口如何形成卡片待办，不将每条 AC 无差别并入研发、测试任务分母。
- 核对 Issue、关联 Change、Sprint 的全部已生成治理 MD 文档及同名文档来源；按阶段与权限验证可见、可读、只读和缺失情形。
- 对照后端实际归档门禁，确定卡片动作的阻断原因和刷新时机，并补充对应回归验收。
