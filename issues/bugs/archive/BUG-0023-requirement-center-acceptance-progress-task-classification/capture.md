---
bug_id: BUG-0023-requirement-center-acceptance-progress-task-classification
title: 需求中心验收中卡片进度未按 tasks.md 分类统计返修任务
status: done
created_at: '2026-09-15 22:32:37'
updated_at: 2026-09-17 10:24:39
environment: local
related_requirement: REQ-0012-frontend-requirement-center
related_bug: null
severity: medium
---

# 现象

需求中心「验收中」卡片展示的研发、测试、人工验收完成度未按 `tasks.md` 内任务类别统计，也未把 `/opsx-modify` 验收返修追加的任务纳入同一进度口径，导致卡片可能显示研发、测试、人工验收已完成，但实际返修任务、返修测试或人工复验尚未闭环。

本次保持单条 BUG：问题发生在同一页面、同一卡片进度组件，修复面集中在验收中卡片的进度口径与 `tasks.md` 任务分类统计，拆分会造成重复复现与重复验收。

严重度初判 medium：该问题会误导验收判断与归档前确认，但当前没有证据表明会直接造成数据丢失、权限越界或运行时阻断。

# 复现步骤

1. 打开需求中心，定位处于「验收中」阶段的 REQ、BUG 或独立 Change 卡片。
2. 查看卡片上的「研发」「测试」「人工验收」进度。
3. 打开关联 Change 的 `tasks.md`，检查任务是否可按研发、测试、人工验收分类，并确认是否存在 `/opsx-modify` 返修追加任务。
4. 对比卡片进度与 `tasks.md` 中当前交付闭环内所有任务，尤其是返修实现、返修测试、视觉证据、文档同步和人工复验任务。

# 期望 vs 实际

| 项 | 期望 | 实际 |
|---|---|---|
| 研发进度 | 统计 `tasks.md` 中所有研发类 checkbox 完成数 / 研发类 checkbox 总数，包含返修实现任务 | 修复前实现倾向统计 linked Change `tasks.md` 的所有 checkbox，不区分研发、测试、验收 |
| 测试进度 | 统计 `tasks.md` 中所有测试类 checkbox 完成数 / 测试类 checkbox 总数，包含返修回归、视觉证据和校验任务 | 修复前实现倾向使用 `acceptance.md`、`review.md`、`trace.md` 三个文档存在性作为 `测试 n/3` |
| 人工验收进度 | 统计 `tasks.md` 中所有人工验收类 checkbox 完成数 / 人工验收类 checkbox 总数，包含返修后的人工复验或 sign-off | 修复前实现倾向由 `manual_acceptance_count` 推导；缺少计数时可能默认显示 `1/1` |
| 返修任务 | `/opsx-modify` 追加的返修实现、返修测试、文档同步和人工复验任务进入对应分母 | 修复前进度口径没有稳定表达返修任务分类与纳入规则 |

# 已有探索证据

- 需求中心卡片展示存在「研发」「测试」「人工验收」三个进度按钮。
- 后端修复前研发进度来自 linked Change `tasks.md` 的 checkbox 总数统计，未按任务类别拆分。
- 后端修复前测试进度为验收阶段中 `acceptance.md`、`review.md`、`trace.md` 三个文档的存在性计数。
- 后端修复前 `manual_acceptance_count` 默认值为 `0`，前端在缺少人工验收计数时可能显示人工验收 `1/1`。
- 当前产品讨论已确认期望口径为：研发、测试、人工验收都应来自 `tasks.md` 分类 checkbox，并包括 `/opsx-modify` 返修任务。

# 建议验收要点

- `tasks.md` 任务分类规则明确，至少能稳定识别研发、测试、人工验收三类任务。
- 首次 apply 任务与 `/opsx-modify` 返修追加任务均进入当前卡片进度统计。
- 返修实现未完成时研发进度不应显示完成。
- 返修回归、视觉证据或校验任务未完成时测试进度不应显示完成。
- 人工复验或 sign-off 未完成时人工验收不应默认显示 `1/1`。
- 任务历史记录表、说明文字和证据链接不计入分母；只有 `- [ ]` / `- [x]` 任务项进入计数。

# 附件

无新增截图或日志附件。证据来自本轮 `/explore` 对现有需求中心进度口径、前后端字段和产品定义的只读分析。
