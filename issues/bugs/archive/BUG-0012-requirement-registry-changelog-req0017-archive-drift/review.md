---
bug_id: BUG-0012-requirement-registry-changelog-req0017-archive-drift
review_result: approved
reviewed_at: 2026-08-15 11:03:51
reviewer: product
decision: approve
created_at: 2026-08-15 11:03:51
updated_at: 2026-08-15 11:03:51
---

# 缺陷评审

## 评审结论

确认修复，状态推进为 `approved`。

## 评审清单

| 检查项 | 结论 | 说明 |
|---|---|---|
| 可复现或根因充分 | 通过 | `root-cause.md` 已记录 8 条证据，根因状态为 `confirmed`，`validate-root-cause-evidence.py` 通过。 |
| 严重等级合理 | 通过 | 该问题为非阻塞治理漂移，不影响运行时能力，但会误导当前态索引和后续治理命令判断，严重等级 `medium` 合理。 |
| 回归验收明确 | 通过 | `acceptance.md` 已限定修复范围为 `issues/requirements/_registry.yaml` 与 `issues/requirements/CHANGELOG.md`，并要求验证 REQ-0017 与真实 archive 目录一致。 |
| hotfix 路径 | 不需要 | 不影响线上运行、API、DB、UI 或部署；按常规 Sprint 修复链路推进。 |

## 修复范围

本 BUG 仅修复 `REQ-0017-admin-space-management` 在需求 registry 与需求当前态看板中的状态、阶段、路径、关联 Change 和下一步漂移。

不纳入本 BUG 的范围：

- `iterations/archive/sprint-002` 中历史路径或状态残留。
- `src/`、`openspec/`、API、数据库、UI、部署、安全或客户端生成物。

## 下一步

按流程先纳入 Sprint：

```bash
/sprint-propose --bug BUG-0012-requirement-registry-changelog-req0017-archive-drift
```
