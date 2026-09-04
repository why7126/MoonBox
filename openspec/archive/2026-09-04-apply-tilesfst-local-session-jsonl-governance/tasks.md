---
change_id: apply-tilesfst-local-session-jsonl-governance
status: applied
created_at: 2026-09-04 16:05:54
updated_at: 2026-09-04 16:05:54
---

# Tasks

## 1. OpenSpec 与 Sprint

- [x] 1.1 创建独立治理 Change，承载 TilesFST 本地 session JSONL 学习应用。
- [x] 1.2 将 Change 纳入 `sprint-004` scope。

## 2. 规则、技能与文档

- [x] 2.1 更新 Workflow Sync session 输入发现规则。
- [x] 2.2 更新 Sprint Archive / Sprint Experience 的 AI Usage gate 口径。
- [x] 2.3 新增 `data/ai-usage/README.md`，声明脱敏派生事实和禁止持久化内容。
- [x] 2.4 同步命令顺序和上下文预算说明。

## 3. 脚本与测试

- [x] 3.1 更新 `scripts/ai_usage.py` 缺 session、缺 token 和路径不存在时的推荐动作。
- [x] 3.2 新增 AI Usage 单元测试覆盖自动发现、fallback、unsafe record 和路径泄漏保护。

## 4. 学习报告与验证

- [x] 4.1 写入 `docs/spec-logs/YYYYMMDDhhmmss-study-tilesfst-local-session-jsonl.md`。
- [x] 4.2 在 `docs/spec-logs/CHANGELOG.md` 倒序登记本次 study。
- [x] 4.3 运行脚本级测试、上下文预算、OpenSpec 语言、目录结构、目标 Change 校验和 Sprint scope 校验。
- [x] 4.4 运行 Workflow Sync 与 AI Usage hook，复核学习对象只读状态。
