---
change_id: apply-tilesfst-local-session-jsonl-governance
type: update
status: proposed
created_at: 2026-09-04 16:05:54
updated_at: 2026-09-04 16:05:54
---

# 应用 TilesFST 本地 session JSONL 治理学习成果

## 背景

`/spec-study TilesFST --focus 本地session JSONL` 已完成只读学习，并确认可迁移能力集中在 AI Usage 本地 session JSONL 自动发现、隐私持久化边界、历史回填策略、Sprint 复盘 gate 和脚本级测试。

MoonBox 的 `scripts/ai_usage.py` 已具备本地自动发现能力，但部分技能说明和失败提示仍偏向显式 session 输入，缺少 `data/ai-usage` 目录级说明和单元测试兜底。本变更将学习结果转写为 MoonBox 治理资产。

## 目标

- 对齐 Workflow Sync、Sprint Archive 和 Sprint Experience 的 session 输入发现口径。
- 补齐缺 session、session 路径不存在、缺 `token_count` 时的推荐动作。
- 新增 `data/ai-usage/README.md`，声明脱敏派生事实、禁止持久化内容和历史回填边界。
- 增加 AI Usage 单元测试，覆盖自动发现、缺 token、unsafe 记录和路径泄漏保护。
- 输出单份 `/spec-study apply` 学习报告并登记到 `docs/spec-logs/CHANGELOG.md`。

## 非目标

- 不复制学习对象业务专属文档、历史 session、运行日志或脚本全文。
- 不修改 `src/` 业务代码、API、数据库 schema、Web 或管理端运行时。
- 不将 session 环境变量写入应用运行时 `.env.example`。
- 不使用自动发现做历史回填或审计归因。
- 不修改正式 `openspec/specs/`。

## 影响范围

```yaml
impact:
  backend: false
  web: false
  admin: false
  database: false
  api: false
  docker_compose: false
  governance: true
  tests: true
```
