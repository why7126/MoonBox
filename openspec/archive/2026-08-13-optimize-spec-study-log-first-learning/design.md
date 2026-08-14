---
created_at: 2026-08-09 08:27:52
updated_at: 2026-08-09 08:27:52
---

# 设计

## 方案

在 `/spec-study` 的 Phase 1 中增加“日志优先学习顺序”：

```text
docs/spec-logs/CHANGELOG.md
-> 相关 YYYYMMDDhhmmss-study/governance 日志
-> 对应 AGENTS/rules/skills/scripts/docs/部署示例
-> 必要代码或配置片段
-> 候选学习项 / 不采纳项 / 风险
```

该顺序只在学习对象存在 `docs/spec-logs/CHANGELOG.md` 时启用；如果不存在，则继续按原 Learning Matrix 先定位治理文件，再分主题读取必要片段。

## 关键约束

- `CHANGELOG.md` 只作为入口地图和摘要索引，不替代单次日志、OpenSpec Change、Sprint 四件套、正式规格或实际治理资产。
- 单次 `study` / `governance` 日志用于理解变更目标、采纳原因、影响范围和验证结果。
- 真实资产校验仍必须覆盖项目入口、`rules/`、`docs/`、Agent 目录、`scripts/`、部署与环境示例。
- 对代码、脚本和配置只做必要补证，优先定位和片段读取，避免为学习目的扩大到业务实现。

## 取舍

选择日志优先，是为了把“为什么这样治理”放在“现在文件长什么样”之前；继续保留横向校验，是为了防止日志过期、漏记或与当前资产漂移。
