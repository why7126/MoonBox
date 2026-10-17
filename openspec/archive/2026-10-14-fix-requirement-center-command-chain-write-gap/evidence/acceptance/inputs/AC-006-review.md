---
title: 未接入命令动作语义复核
created_at: 2026-10-14 09:00:00
updated_at: 2026-10-14 09:00:00
---

# 未接入命令动作语义复核

现行产品能力矩阵将 complete、review、sprint-propose、opsx 系列列为 `real_object_session_write`：卡片动作只进入绑定对象的 Chat 并填入命令草稿，不显示“执行成功，卡片已流转”。候选或 application 是否成功，必须由后端同轮校验和事实源投影决定；进入对象会话不算成功写入。

未列入矩阵的动作归入 `codex_command_only`，点击时显示“产品内尚未接入该治理写入链路，请在 Codex 执行”及完整命令，且在创建对象会话前返回。旧验收措辞中的上述命令已接入对象会话，因此本项按“未接入者不得伪装成功”的条件门禁复核；不把对象会话能力误写为每条命令已经真实应用。

证据为 `RequirementCenterPage.tsx` 的能力矩阵及 `openIssueActionDialog` 分支，配合需求中心前端完整回归。未知命令的请求为零和卡片不流转另见 [AC-007](AC-007-review.md) 与 [AC-008](AC-008-review.md)。
