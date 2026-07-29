---
purpose: OpenSpec 测试映射
content: MoonBox 需求、Bug、Change 与测试证据映射规则
created_at: 2026-07-29 22:55:00
updated_at: 2026-07-29 22:55:00
owner: MoonBox 产品团队
---

# 测试映射

MoonBox 的需求、Bug、OpenSpec Change 和 Sprint 必须能追溯到测试证据。

| 来源 | 测试证据 |
|---|---|
| REQ | acceptance.md、单元测试、集成测试、E2E 或人工验收记录 |
| BUG | 复现记录、回归测试、修复验证 |
| OpenSpec Change | tasks.md 中的验证项和实际命令输出 |
| Sprint | acceptance-report.md 和 release-note.md |

涉及 API、DB、UI、对象存储、安全或部署的变更必须补充对应专项测试。
