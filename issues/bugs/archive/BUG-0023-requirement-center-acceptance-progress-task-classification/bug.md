---
bug_id: BUG-0023-requirement-center-acceptance-progress-task-classification
title: 需求中心验收中卡片进度未按 tasks.md 分类统计返修任务
status: done
owner: 产品团队
discovered_at: '2026-09-15 22:32:37'
environment: local
related_requirement: REQ-0012-frontend-requirement-center
related_change: fix-requirement-center-acceptance-progress-task-classification
created_at: 2026-09-15 22:40:01
updated_at: 2026-09-17 10:24:34
severity: medium
---

# 需求中心验收中卡片进度未按 tasks.md 分类统计返修任务

## 现象

需求中心「验收中」卡片展示的「研发 / 测试 / 人工验收」完成度与产品期望口径不一致：

- 研发进度当前表现为 linked Change `tasks.md` 中所有 checkbox 的完成数 / 总数，未按研发、测试、人工验收任务分类。
- 测试进度当前表现为文档齐备度，倾向使用 `acceptance.md`、`review.md`、`trace.md` 三个文档存在性显示 `测试 n/3`。
- 人工验收进度修复前由人工确认计数推导；缺少计数时可能显示 `人工验收 1/1`。
- `/opsx-modify` 验收返修追加的返修实现、返修测试、视觉证据、文档同步和人工复验任务缺少稳定纳入进度分母的分类口径。

用户附件截图 Image #1 中，「验收中」列表里至少两张卡片显示完成态进度：

| 卡片 | 当前展示 |
|---|---|
| Capture 图文候选审阅与确认采集 | 研发 `33/33`、测试 `3/3`、人工验收 `1/1` |
| 聊天框新增 Agent、模型和推理程序选择 | 研发 `29/29`、测试 `3/3`、人工验收 `1/1` |

这类展示容易让用户误以为研发、测试、人工验收已经完整闭环；但产品定义要求这三个进度都应来自 `tasks.md` 分类 checkbox，并且包含 `/opsx-modify` 返修任务。

## 复现步骤

1. 打开需求中心页面。
2. 定位「验收中」列的 REQ、BUG 或独立 Change 卡片。
3. 查看卡片上的「研发」「测试」「人工验收」进度。
4. 打开该卡片关联 Change 的 `tasks.md`。
5. 检查 `tasks.md` 中开发任务、测试任务、人工验收任务以及 `/opsx-modify` 返修任务。
6. 对比卡片进度是否按上述三类任务分别统计，且是否把返修任务纳入分母。

## 期望结果

需求中心验收中卡片的三个进度应统一来自当前 linked Change 的 `tasks.md`：

| 展示项 | 期望统计口径 |
|---|---|
| 研发 | `tasks.md` 中研发类 checkbox 完成数 / 研发类 checkbox 总数 |
| 测试 | `tasks.md` 中测试类 checkbox 完成数 / 测试类 checkbox 总数 |
| 人工验收 | `tasks.md` 中人工验收类 checkbox 完成数 / 人工验收类 checkbox 总数 |

统计范围应包含首次 `/opsx-apply` 任务和后续 `/opsx-modify` 返修追加任务。任务历史记录表、说明文字、证据链接和 `acceptance-fixes.md` 台账正文不应直接计入分母；只有 `- [ ]` / `- [x]` 形式的可关闭任务项进入计数。

后续修复时应同步沉淀 `tasks.md` 三类任务与 `/opsx-modify` 返修任务统计口径，避免同类展示再次漂移。

## 实际结果

当前实现与产品口径不一致：

- 研发进度按 `tasks.md` checkbox 总数统计，未按任务类别拆分。
- 测试进度按验收阶段的文档存在性计算，未读取 `tasks.md` 测试类任务。
- 人工验收进度由前端对 `manual_acceptance_count` 推导，未读取 `tasks.md` 人工验收类任务。
- 当前没有稳定规则把 `/opsx-modify` 返修任务按研发、测试、人工验收分类后纳入进度。

## 影响范围

- 影响需求中心「验收中」阶段卡片的进度可信度。
- 影响 REQ、BUG 和独立 Change 的验收判断与归档前确认。
- 对存在 `/opsx-modify` 返修的 UI 型、API 型或治理型 Change 影响更明显：返修任务尚未完成时，卡片仍可能呈现测试或人工验收满格。
- 不涉及已知权限越界、数据丢失或运行时中断；暂未发现需要热修的证据。

## 严重等级说明

严重等级为 `medium`。

理由：该问题会误导验收阶段的完成度判断，可能导致用户过早认为卡片已经具备归档条件；但当前证据显示它主要影响治理看板展示与验收判断准确性，尚未证明会直接造成数据损坏、安全问题或核心流程不可用。

## 后续补证方向

- 选取 Image #1 中任一卡片，读取对应 Change `tasks.md`，确认当前三类任务与返修任务分布。
- 通过需求中心 context 响应或前端页面，记录该卡片实际返回的 `task_progress`、`test_progress`、`manual_acceptance_count`。
- 在 `/bug-complete` 中把代码路径、真实样本和测试缺口整理为根因证据链。
