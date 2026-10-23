---
bug_id: BUG-0050-archive-wrapper-proof-acceptance-fixture
title: 归档证明验收样本根因
created_at: '2026-10-19 23:19:57'
updated_at: '2026-10-19 23:19:57'
root_cause_status: confirmed
---

# 归档证明验收样本根因

## 根因状态

status: confirmed

## 证据链

| id | type | source | 摘要 |
|---|---|---|---|
| E1 | code_path | src/backend/app/governance/direct_command_journal.py:is_formal_workflow_sync；BUG-0049/root-cause.md | 父缺陷包装归档漏识别已确认，本样本用于修复后首次归档验证。 |
