---
title: 纯治理 Change 归档验收返修台账
created_at: 2026-10-13 18:38:00
updated_at: 2026-10-13 18:38:00
---

# 纯治理 Change 归档验收返修台账

## 批次一：归档续接门禁

| 项目 | 记录 |
|---|---|
| 验收反馈 | 产品 Chat 首次归档成功后，`archive-change.sh --finalize` 被 `ACCEPTANCE_GATE_BLOCKED change_trace_missing` 阻断。 |
| 期望 | 已有唯一 canonical archive 时，沿用其 trace 判定纯治理或 Issue 验收状态，完成验证与 Workflow Sync，不重新合并规格。 |
| 实际 | `validate-issue-acceptance-ready.py` 只读取活动 Change 目录；首次归档移动目录后，续接立即失败。 |
| 根因状态 | confirmed；同一隔离源仓库产品轮次 `2a0f8ff2-5be0-43d6-9485-bad1e6c69cf6` 的门禁标记与脚本分支直接对应。 |
| 处理 | 活动目录不存在时仅接受唯一 canonical archive 或 CLI 旧目录过渡阶段的 trace；活动与归档并存、多个归档日期或关联 Issue 未签认继续拒绝。 |
| 验证 | 归档门禁与恢复聚焦回归 16 passed；产品续接轮次 `f908138b-7395-438b-add3-ece95e413b6b` 为 `completed`、目标命令退出码 0、Workflow Sync 0 errors。 |
| 影响面 | 仅归档门禁与验收测试；未变更 API、DB、UI、部署拓扑、客户端生成或权限 profile。 |

首次产品源仓库归档轮次 `8436f1d1-4381-423a-89f2-2f29f789edc0` 亦为 `completed`、目标命令退出码 0；活动目录消失且唯一 canonical archive 存在。完整脱敏证据见 `evidence/acceptance/samples/AC-005.md`。

## 批次二：验收清单指纹稳定性

Workflow Sync 将 linked Issue 的 `accepted_at` 与证据入口刷新后，完整清单虽为 5/5 passed，`--readiness` 却立即报告五项 stale。`scripts/opsx_acceptance.py` 原来对 Issue `acceptance.md` 全文取指纹，将自动生成的状态投影误当作验收条件。现对 Issue 验收输入仅排除生成的 frontmatter 时间/状态和 `## 验收结果回填` 段；AC 复选框及人工正文仍参与指纹。新增测试验证同步投影刷新不使清单过期、复选框变化会过期；相关验收与归档门禁测试共 35 passed。同步语义已补充至 `docs/standards/opsx-acceptance.md`。

其他文档：归档续接规则属于本 Change 原有设计范围，已补设计与追溯；无需修改产品规格、API、数据库、UI、部署或客户端生成文档。AI 用量钩子在隔离样本无可归因会话时返回 `usage_mode: unavailable`，不影响归档事实。
