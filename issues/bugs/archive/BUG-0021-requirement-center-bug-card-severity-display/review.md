---
bug_id: BUG-0021-requirement-center-bug-card-severity-display
title: 需求中心 BUG 卡片显示优先级 P 值而非严重性
status: done
created_at: 2026-09-14 14:03:55
updated_at: 2026-09-14 14:44:39
reviewed_at: 2026-09-14 14:03:55
review_result: approved
severity: medium
reviewer: AI
---

# 缺陷评审

## 评审结论

确认修复，评审通过。

## 评审清单

| 检查项 | 结论 | 说明 |
|---|---|---|
| 可复现或根因充分 | 通过 | root-cause.md 为 `confirmed`，7 条证据覆盖截图、事实源、规范、后端模型、后端构卡、前端渲染和测试 fixture |
| 严重等级合理 | 通过 | `medium` 合理；影响治理看板分级判断和迭代排序参考，但无生产不可用、数据丢失、权限越界或安全风险证据 |
| 回归验收明确 | 通过 | acceptance.md 已列出 BUG 严重性展示、REQ 优先级保留、API 字段不混用、非法分级可诊断、测试覆盖和非目标范围不回退 |
| 是否需 hotfix 路径 | 不需要 | 当前无 P0、生产核心阻断或安全事件证据 |

## 评审依据

- `python scripts/validate-root-cause-evidence.py --bug BUG-0021-requirement-center-bug-card-severity-display` 通过，`root_cause_status=confirmed`，`evidence_count=7`。
- 需求中心卡片展示链路已定位到后端响应模型、构卡函数、前端类型和渲染，以及测试 fixture 的字段契约漂移。
- 修复范围清晰：REQ 继续使用 `priority`，BUG 使用 `severity`，并补齐后端、前端和测试覆盖。

## 后续门禁

评审通过后，下一步必须先纳入 Sprint：

```bash
/sprint-propose --bug BUG-0021-requirement-center-bug-card-severity-display
```

该 BUG 后续已纳入 sprint-006，创建 OpenSpec Change，并完成实现与归档。
