---
change_id: add-guided-feedback-dialog-copy-hierarchy
status: proposed
created_at: 2026-08-16 11:47:41
updated_at: 2026-08-16 11:47:41
---

# Test Plan

## 校验命令

```bash
python scripts/validate-agent-context-budget.py
python scripts/validate-openspec-language.py
python scripts/validate-directory-structure.py
openspec validate add-guided-feedback-dialog-copy-hierarchy
python scripts/sync-workflow-status.py --event opsx.apply --change add-guided-feedback-dialog-copy-hierarchy --sprint auto
```

## 业务测试

不适用。本次仅修改治理规则、Skill 契约和 OpenSpec 文档，不修改业务运行时代码、API、数据库、UI 实现或部署配置。
