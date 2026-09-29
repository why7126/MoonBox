---
bug_id: BUG-0023-requirement-center-acceptance-progress-task-classification
title: 需求中心验收中卡片进度未按 tasks.md 分类统计返修任务
status: active
created_at: 2026-09-15 22:47:41
updated_at: 2026-09-15 22:47:41
owner: 产品团队
---

# 临时规避

## 可用规避

在正式修复前，不要把需求中心验收中卡片的「研发 / 测试 / 人工验收」进度作为归档或验收通过的唯一依据。

临时判断步骤：

1. 打开卡片关联的 `tasks.md`。
2. 人工按任务内容区分研发、测试和人工验收任务。
3. 检查 `/opsx-modify` 返修追加任务是否仍有未勾选项。
4. 同步查看 `acceptance-fixes.md`、Change `trace.md` 的验证记录和 linked Issue `acceptance.md`。
5. 只有返修实现、返修测试、视觉证据、文档同步和人工复验均闭环后，再视为验收可继续推进。

## 限制

- 该规避依赖人工判断任务分类，无法防止卡片继续显示误导性满格进度。
- `acceptance.md`、`review.md`、`trace.md` 齐备不等于测试任务完成。
- 人工验收显示 `1/1` 不等于真实 sign-off。
- 不能替代正式修复，也不能作为归档门禁的长期依据。

## 解除条件

完成正式修复并通过回归验收后，可以解除该规避。正式修复应让需求中心卡片进度直接来自 `tasks.md` 三类任务统计，并纳入 `/opsx-modify` 返修任务。
