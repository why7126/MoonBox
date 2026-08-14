---
change_id: add-git-check-pre-push-security-gate
type: add
status: applied
created_at: 2026-08-09 07:30:21
updated_at: 2026-08-09 08:18:35
source_requirement: REQ-0009-git-check-pre-push-security-gate
sprint: sprint-002
impact:
  backend: false
  web: false
  miniapp: false
  admin: false
  database: false
  storage: false
  api: false
  governance: true
governance_impact: true
spec_log_refs:
  - docs/spec-logs/20260809081835-governance-git-check-security-gate.md
changelog_updated: true
capabilities:
  new:
    - git-check-security-gate
  modified: []
---

# Trace

## 状态

```yaml
status: applied
source_requirement: REQ-0009-git-check-pre-push-security-gate
sprint: sprint-002
next: /opsx-archive REQ-0009-git-check-pre-push-security-gate
```

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-09 07:30:21 | req.opsx | 从 REQ-0009 创建 OpenSpec Change。 |
| 2026-08-09 07:40:40 | opsx.apply | 完成 `/git-check` 命令、脚本、测试和文档同步。 |
| 2026-08-09 07:44:41 | opsx.modify | 验收返修：将已跟踪的 `data/s3/**` 运行时对象存储数据迁出 Git 索引，保留本地文件；`git-check` 复验无 error。 |
| 2026-08-09 08:04:52 | opsx.modify | 验收返修：将本机绝对路径纳入隐私阻断，`local-absolute-path` 命中升级为 error；历史归档文档已脱敏为占位符，相关校验脚本避免自检误命中。 |
| 2026-08-09 08:18:35 | opsx.modify | 验收返修：补充 `docs/spec-logs` 治理日志和 `CHANGELOG.md` 索引，并规定 REQ/BUG 驱动但触达治理资产的 Change 也必须纳入 spec-logs。 |
