---
purpose: OpenSpec Change Test Plan
content: spec-logs 跨项目落地提示词列验证计划
created_at: 2026-08-08 21:01:51
updated_at: 2026-08-08 21:01:51
owner: MoonBox 产品团队
---

# Test Plan

## 验证命令

```bash
python scripts/validate-agent-context-budget.py
python scripts/validate-openspec-language.py
python scripts/validate-directory-structure.py
openspec validate add-spec-logs-adoption-prompt-column
python scripts/validate-sprint-scope.py sprint-001 --item add-spec-logs-adoption-prompt-column
python scripts/sync-workflow-status.py --event opsx.apply --change add-spec-logs-adoption-prompt-column --sprint auto
```

## 业务测试

本 Change 仅修改治理 Markdown 与 OpenSpec 文档，不涉及业务运行时代码；后端、前端、API、DB、Docker Compose 业务测试不适用。
