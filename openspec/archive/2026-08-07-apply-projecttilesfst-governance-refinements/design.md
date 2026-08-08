---
purpose: OpenSpec Change Design
content: A-E 治理学习候选的 MoonBox 适配方案
created_at: 2026-08-07 00:00:00
updated_at: 2026-08-07 00:00:00
owner: MoonBox 产品团队
---

# Design

## 设计原则

- 按 MoonBox 已有目录和命令体系重写规则，不复制 ProjectTilesFST 业务内容。
- 优先增强现有 `docs/spec-logs/`、Mintlify、usage-docs 和 deploy 能力，不新增业务运行时依赖。
- 校验脚本只做公开安全和结构一致性检查，不读取真实 env 或输出敏感值。

## 影响范围

- API：无影响。
- 数据库：无影响。
- Web：无业务实现影响。
- 客户端：无影响。
- 管理端：无业务实现影响。
- Orval：不需要。
- Docker Compose：仅部署文档和脚本边界说明；不改变 Compose 拓扑。
- 测试：运行治理脚本和文档校验。
