---
change_id: optimize-workflow-sync-issue-output-next
acceptance_status: passed
created_at: 2026-08-27 08:02:44
updated_at: 2026-08-27 08:02:44
---

# 验收标准

- `--apply-issue-subdocuments` summary 输出能直接看到聚焦 Issue 的子文档更新文件数、字段数、验收状态和安全同步项。
- `/req-opsx` 或 `/bug-opsx` 同一轮 sync 回填 Change 后，当前态看板 `下一步` 字段推导为 `/opsx-apply <REQ-full-id>` 或 `/opsx-apply <BUG-full-id>`。
- 聚焦单元测试和治理校验通过。

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-27 08:02:44
accepted_by: workflow-sync
evidence:
  - pytest tests/unit/test_workflow_sync_engine.py tests/unit/test_workflow_sync_patch.py
  - python scripts/validate-agent-context-budget.py
  - python scripts/validate-openspec-language.py
  - python scripts/validate-directory-structure.py
  - openspec validate optimize-workflow-sync-issue-output-next
failed_items: []
source_event: opsx.apply
notes: 本 Change 聚焦验证和治理校验均通过。
```
