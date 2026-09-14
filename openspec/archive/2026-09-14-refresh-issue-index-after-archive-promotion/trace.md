---
status: applied
iteration: sprint-005
change_id: refresh-issue-index-after-archive-promotion
created_at: 2026-09-14 09:01:23
updated_at: 2026-09-14 09:06:20
---

## 链路

- 来源：`/spec-opt` 归档链路复盘建议。
- Sprint：sprint-005。
- 范围：治理脚本、测试、OpenSpec Change、治理日志。
- product_data_collection_observability：N/A；未触达 API、DB、日志审计、行为埋点、Task Trace、对象存储或请求封装。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-09-14 09:01:23 | spec.opt | 创建治理优化 Change，修复 promote 后索引路径漂移。 |
| 2026-09-14 09:06:20 | spec.opt | 脚本、测试、治理日志与 Sprint 派生同步完成，待 Workflow Sync 收口。 |
| 2026-09-14 09:07:15 | workflow-sync | opsx.apply 同步完成，AI Usage hook 为 warning/unavailable。 |
| 2026-09-14 09:11:30 | opsx.archive | 归档后补充修正纯治理 Change 来源识别，避免 proposal 正文 BUG/REQ 背景被误判为关联 Issue。 |

## 验证摘要

- `uv run --with pytest --with pyyaml pytest tests/unit/test_promote_issues_for_archive.py tests/unit/test_workflow_sync_patch.py -q`：2 passed。
- `uv run --with pytest --with pyyaml pytest tests/unit/test_promote_issues_for_archive.py tests/unit/test_workflow_sync_patch.py tests/unit/test_workflow_sync_collect.py -q`：4 passed。
- `python scripts/validate-agent-context-budget.py`：通过。
- `python scripts/validate-openspec-language.py`：通过。
- `python scripts/validate-directory-structure.py`：通过。
- `openspec validate refresh-issue-index-after-archive-promotion`：valid。
- `python scripts/validate-sprint-scope.py sprint-005 --item refresh-issue-index-after-archive-promotion`：pass。
- Workflow Sync `opsx.apply`：Updated=2，Errors=0。
- AI Usage Hook：warning/unavailable，未发现可归因 token_count 事件，未伪造用量。
- 归档后复核：sprint-005 changes 表中 `refresh-issue-index-after-archive-promotion` 关联列为 `—`，不再误关联 BUG-0014。

## 影响边界

API、DB、Web、客户端、管理端、Orval、Docker Compose 均不适用；本次只修改治理脚本、脚本级测试、OpenSpec Change 与治理日志。
