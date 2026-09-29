---
bug_id: BUG-0023-requirement-center-acceptance-progress-task-classification
title: 需求中心验收中卡片进度未按 tasks.md 分类统计返修任务
review_result: approved
reviewed_at: 2026-09-15 22:57:14
reviewed_by: product
severity: medium
hotfix_required: false
created_at: 2026-09-15 22:57:14
updated_at: 2026-09-15 22:57:14
---

# 缺陷评审

## 评审结论

确认修复，评审通过。

## 评审清单

| 检查项 | 结论 | 说明 |
|---|---|---|
| 可复现或根因充分 | 通过 | 用户截图证明验收中卡片存在 `研发 33/33 测试 3/3 人工验收 1/1` 等满格展示；`root-cause.md` 根因状态为 `confirmed`，证据链包含后端聚合、前端推导、现有测试 fixture 和治理规则，共 8 条证据；根因门禁脚本通过。 |
| 严重等级合理 | 通过 | `medium` 合理；问题影响需求中心验收判断、治理看板可信度和返修任务闭环识别，当前未见数据破坏、权限绕过、服务不可用或安全风险证据。 |
| 回归验收明确 | 通过 | `acceptance.md` 覆盖 `tasks.md` 研发、测试、人工验收三类分类统计，`/opsx-modify` 返修任务纳入分母，人工验收不再默认 `1/1`，以及 API、前端类型、前后端测试和统计口径沉淀。 |
| 是否需 hotfix 路径 | 不需要 | 缺陷影响验收展示可信度，但存在人工核对 `tasks.md` 与 `acceptance-fixes.md` 的临时规避；按常规 Sprint 纳入修复。 |

## 评审依据

- `bug.md` 已描述现象、期望与实际、影响范围、严重等级和用户截图摘要。
- `root-cause.md` 已确认根因：验收中卡片研发、测试、人工验收三类进度缺少统一的 `tasks.md` 分类统计模型，测试与人工验收存在文档存在性和前端默认推导误报。
- `workaround.md` 已提供短期规避：修复前人工核对 linked Change 的 `tasks.md`、`acceptance-fixes.md`、`acceptance.md`、`trace.md`，不以卡片三组进度作为唯一验收依据。
- `acceptance.md` 已列出修复验收项，当前验收状态为 `passed`。

## 后续动作

无；本 BUG 已纳入 `sprint-007`，关联 Change 已归档。
