---
title: 建立 Git 远程同步治理技能迭代日志
created_at: 2026-10-09 10:22:12
updated_at: 2026-10-09 10:22:12
---

# 建立 Git 远程同步治理技能迭代日志

## 迭代目标

为项目提供按交付范围安全暂存、提交、正式版本打标与远程同步的连续命令入口。

## 变更摘要与影响范围

新增 `/git-sync` Skill，复用 `/git-check` 安全扫描；明确忽略规则、已跟踪禁入文件、提交说明、版本标签、远端分叉及冲突处理门禁。同步 Agent 命令入口、上下文预算和安全规则，并建立 OpenSpec Change。清理由目录结构校验发现的四个空工具目录。

## 更新文件

- `.agents/skills/git-sync/SKILL.md`
- `AGENTS.md`
- `rules/agent-context-budget.md`
- `rules/security.md`
- `openspec/changes/add-git-sync-skill/` 下的提案、设计、任务与规格
- 本治理迭代日志

## 验证结果

OpenSpec 当前 Change 中文优先和目录结构校验通过；完整验证结果以 Change `trace.md` 的验证记录为准。本次未执行真实 Git 提交、标签创建或远程推送。

## 系统影响与后续建议

API、数据库、Web、客户端、管理端、Orval 和 Docker Compose 均无变化。后续可在独立交付任务中用真实混合工作区验证范围选择与远程分叉处理，并按证据完善 Skill。
