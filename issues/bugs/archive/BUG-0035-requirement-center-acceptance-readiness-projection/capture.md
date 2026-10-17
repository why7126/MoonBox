---
bug_id: BUG-0035-requirement-center-acceptance-readiness-projection
title: 需求中心卡片验收进度与归档门禁不一致且验收文档入口消失
status: done
created_at: 2026-10-09 22:32:00
updated_at: 2026-10-13 08:26:10
owner: 产品团队
source: 用户截图反馈与只读代码定位
lifecycle_stage: plan
environment: local Docker
related_requirement: REQ-0012-frontend-requirement-center
related_bug: BUG-0023-requirement-center-acceptance-progress-task-classification
severity: medium
---

# 需求中心卡片验收进度与归档门禁不一致且验收文档入口消失

## 现象

BUG-0025 在需求中心验收中卡片显示“研发 41/41、测试 37/37”和“完成 / 归档”，但关联 Chat 的 `/opsx-archive` 被未完成产品复验与交付证据门禁阻断。卡片没有反映 `acceptance.md` 的待验收状态；关联 Change 后，Issue 的 `acceptance.md` 入口也未持续显示。用户补充：凡已生成且有权读取的治理 MD 文档，在对象后续阶段均应保持卡片入口；当前产品按阶段隐藏了部分既有文档。

## 复现步骤

1. 打开需求中心，定位已关联 OpenSpec Change、处于验收中的 BUG-0025 卡片，查看研发、测试进度、人工验收提示、文档入口和归档动作。
2. 对照关联 Change 的 `tasks.md` 与 Issue 的 `acceptance.md`：前者任务全部勾选，后者仍有待验证 AC。
3. 从卡片进入 Chat 工作台执行 `/opsx-archive BUG-0025-requirement-center-command-chain-write-gap`，观察交付证据门禁结果。
4. 在待评审、已评审、Sprint 规划、待开发、研发中、验收中和完成阶段核对已生成的 Issue、关联 Change、Sprint 治理 MD 文档是否仍有可访问入口，尤其是 `acceptance.md`；不存在或无权读取的文档不应出现虚假入口。

## 期望 vs 实际

| 项 | 期望 | 实际 |
|---|---|---|
| 进度与验收 | 研发、测试任务进度和验收结论分别表达；待验收 AC 或缺证据时，卡片显示待验证状态与原因，不把任务满格等同于可归档 | 卡片仅显示 `tasks.md` 分类进度，后端 `manual_acceptance_count` 固定为 0，无法表达待验收项 |
| 归档动作 | 卡片提示与实际归档门禁一致；阻塞时可查看原因和验收文档 | 卡片展示“完成 / 归档”入口，Chat 实际归档被交付证据门禁阻断 |
| 验收文档 | `acceptance.md` 生成后在后续阶段持续可见，归档后只读可见，并遵守对象权限 | 关联 Change 后，后端优先返回 Change 文档；前端后续阶段过滤了 Issue `acceptance.md` |
| 已生成 MD 文档 | 具备读取权限的 Issue、关联 Change、Sprint MD 文档生成后，在对象后续阶段持续提供可访问入口；同名文档标明来源，归档后遵守只读权限；可用分组或折叠控制卡片密度 | 前端按阶段白名单过滤既有文档；后端关联 Change 后以 Change 文档清单替代部分 Issue 文档，导致入口随阶段消失 |

## 影响范围与初判

- 同一需求中心卡片的进度、验收提示、文档入口和归档动作共同构成一次验收决策，因此保持一条 BUG；不改写已归档 BUG-0023 的任务分类结论。
- 严重度初判 `medium`：会误导归档准备判断和验收取证；现有 Chat 归档门禁仍能阻断本次操作，未观察到越权归档或数据丢失。
- `tasks.md` 保持研发与测试任务来源；`acceptance.md` 是验收标准与验证结果来源，不应把每条 AC 无差别计入三类任务分母。待 `/bug-explore` 核定验收项分类、证据口径及所有阶段的权限边界。
- “持续显示”指真实存在、属于当前授权对象且可读取的治理 MD 文档，不意味着生成尚不存在的文件、放宽对象权限或扩大人工编辑权限；Issue 与 Change 同名文档须分别标注来源和打开正确路径。

## 证据与相似项检查

- 用户本次对话截图：BUG-0025 卡片显示任务满格与归档入口；Chat 归档反馈 AC-051、AC-052 待复验及 AF-040 视觉证据不足。原图未复制到仓库。
- 只读代码定位：`src/backend/app/services/requirement_center.py` 的 `_build_issue`、`_display_document_names`；`src/web/src/pages/catalog/RequirementCenterPage.tsx` 的 `stageVisibleDocs`、`visibleIssueDocuments`、`canArchive`。
- 补充直接证据：`src/web/src/requirement-center.test.tsx` 的阶段过滤用例断言已提供的 `acceptance.md` 在 capture 阶段不可见，说明隐藏行为是当前实现的显式约定；这项补充反馈要求调整该产品约定，并核对每个后续阶段的文档清单。
- BUG-0023 已归档，修复范围是 `tasks.md` 任务分类统计；BUG-0025 验收中，范围是治理命令真实写入。用户已确认将本次 `acceptance.md` 投影与入口问题作为独立关联 BUG 记录；BUG-0025 是本次复现实例和相关链路。

## 2026-10-12 补充复现：文档存在却提示缺少

- 用户截图显示 BUG-0035 的验收中卡片已在 Change 组列出 `proposal.md`、`spec.md`、`design.md`、`tasks.md`，同一张卡片仍以红字提示“缺少 proposal.md、spec.md、design.md、tasks.md”。截图来源为本次对话附件，未复制到仓库。
- 复核关联 Change `fix-requirement-center-acceptance-readiness-projection`：`proposal.md`、`design.md`、`tasks.md` 均在 Change 根目录；`spec.md` 存在于 `specs/*/spec.md`，后端将其投影为可读的 `spec.md` 文档入口。
- 只读代码定位：`src/web/src/pages/catalog/RequirementCenterPage.tsx` 的 `missingDocs` 仅在待开发、研发中阶段对非 `trace.md` 文档读取关联 Change 清单；验收中阶段回退到 Issue 自身 `documents`，因此对已显示的 Change 文档产生缺失误报。该提示属于卡片展示错误，不能据此判定文档缺失或归档门禁结论。
- 期望：验收中卡片的缺文档提示按 Issue、Change、Sprint 实际归属及授权后的文档来源判断；已在 Change 组显示的四份文档不得再提示缺少。建议在后续返修中加入该场景的回归断言。
- 判重结论：与本 BUG 的“关联 Change 文档持续可见且来源正确、验收卡片提示准确”属于同一页面及修复链路。用户已选择关联更新 BUG-0035，不分配新 BUG ID。
