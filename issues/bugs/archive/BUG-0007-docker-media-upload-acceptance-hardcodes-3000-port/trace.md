---
bug_id: BUG-0007-docker-media-upload-acceptance-hardcodes-3000-port
status: done
lifecycle_stage: archive
severity: high
priority: P1
created_at: 2026-08-12 12:08:14
updated_at: 2026-08-13 22:51:12
related_requirement:
related_bug:
related_change: fix-docker-media-upload-acceptance-gate
iteration: sprint-002
openspec_changes:
  - change_id: fix-docker-media-upload-acceptance-gate
    type: fix
    status: archived
---

# BUG-0007 Docker 媒体上传横切验收依赖固定端口和默认管理员密码

```yaml
bug_id: BUG-0007-docker-media-upload-acceptance-hardcodes-3000-port
status: done
lifecycle_stage: archive
severity: high
priority: P1
related_requirement:
related_bug:
related_change: fix-docker-media-upload-acceptance-gate
iteration: sprint-002
openspec_changes:
  - change_id: fix-docker-media-upload-acceptance-gate
    type: fix
    status: archived
```

## 当前状态

- 状态：done
- 阶段：archive
- 严重等级：high
- 优先级：P1
- 关联 Change：fix-docker-media-upload-acceptance-gate
- 下一步：无

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-13 22:50:17 | /opsx-archive | Change `fix-docker-media-upload-acceptance-gate` 已归档，状态同步完成。 |
| 2026-08-12 13:05:30 | /opsx-apply | Change `fix-docker-media-upload-acceptance-gate` apply 完成，待 archive。 |
| 2026-08-12 12:56:35 | bug.opsx | 创建 OpenSpec Change `fix-docker-media-upload-acceptance-gate`。 |
| 2026-08-12 12:52:16 | sprint.propose | 正式纳入 sprint-002，归档前已纳入 sprint-002。 |
| 2026-08-12 12:50:28 | bug.review | 评审通过，状态推进为 approved；下一步先纳入 Sprint。 |
| 2026-08-12 12:48:13 | bug.complete | 补齐 root-cause、workaround、acceptance，状态推进为 pending_review。 |
| 2026-08-12 12:43:36 | bug.generate | 补充验收不应依赖 `data/runtime/backend` 持久库中的默认管理员密码，应由脚本准备一次性测试用户或测试会话。 |
| 2026-08-12 12:41:46 | bug.generate | 生成 bug.md，明确 Docker `:3000` 验收口径与 MoonBox `18101-18199` 端口规范冲突、影响范围和严重等级。 |
| 2026-08-12 12:08:14 | bug.capture | 记录 Docker 媒体上传横切验收硬编码 `:3000`，与 MoonBox `18101-18199` 端口规范冲突并错误阻塞 `/opsx-apply` 的缺陷。 |

- 阶段迁移：plan → review（/bug-review --approve）
- 2026-08-13 22:40:16 workflow-sync：状态同步为 done（Change archived）
- 归档同步：/opsx-archive fix-docker-media-upload-acceptance-gate
