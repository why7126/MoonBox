---
purpose: OpenSpec Change Design
content: 命令执行顺序治理设计
created_at: 2026-08-07 23:20:00
updated_at: 2026-08-07 23:20:00
owner: MoonBox 产品团队
---

# Design

## 顺序模型

MoonBox 命令执行顺序采用分层链路：

```text
capture / complete / review
→ sprint-propose
→ req-opsx / bug-opsx
→ opsx-apply
→ opsx-modify（可选）
→ opsx-archive
→ sprint-archive / sprint-exps
→ release / image / usage-docs
```

治理规则：

- `sprint.yaml` 是 Sprint scope 机器事实源。
- `req-opsx` / `bug-opsx` 必须通过 Workflow Sync 把 Change 回填到同一 Sprint。
- `opsx-apply` 前必须 dry-run 确认 Sprint scope 可解析目标 Change。
- `opsx-archive` 必须在归档后串行运行目录校验、环境 ignore 校验、归档证据校验、Workflow Sync、Issue promote 和 AI Usage。
- `sprint-archive` 必须先确认全部 Change 已归档，再关闭 Sprint。
- release / image / usage-docs 是发布链路，不应早于 OpenSpec 与 Sprint 关键门禁。

## 影响范围

- API：无影响。
- 数据库：无影响。
- Web：无业务实现影响。
- 客户端：无影响。
- 管理端：无业务实现影响。
- Orval：不需要。
- Docker Compose：无拓扑影响。
- 测试：运行治理、语言、目录和 OpenSpec 校验。
