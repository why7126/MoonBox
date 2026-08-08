---
purpose: OpenSpec Change Design
content: spec-study 学习应用治理设计
created_at: 2026-08-07 00:00:00
updated_at: 2026-08-07 00:00:00
owner: MoonBox 产品团队
---

# 设计说明

## 方案

采用最小治理同步方案：

- 在 `/sprint-propose` 技能中加入 Sprint ID Rules，使命令入口直接约束自动编号。
- 在 `rules/iterations-lifecycle.md` 中加入 Sprint 自动编号章节，作为跨命令事实源。
- 在 `rules/agent-context-budget.md` 中加入已读摘要复用细则，降低长任务重复读取成本。
- 在 `docs/spec-logs/README.md` 中补充报告目录边界，防止学习报告承载业务事实源或敏感文件。
- 在 active Change 中新增 `agent-workflow-tooling` 与 `sprint-planning-governance` delta spec，归档后合并到正式规格。

## 取舍

- 不直接复制 ProjectTilesFST 长文档或业务脚本，只提取通用治理约束并改写为 MoonBox 表述。
- 不直接修改 `openspec/specs/`，遵守归档合并规则。
- 复用现有 `sprint-001` scope 承载本治理 Change，避免在已有进行中 Sprint 存在时默认另建并行 Sprint。

## 影响

- API：无影响。
- 数据库：无影响。
- Web：无业务实现影响。
- 客户端：无生成物影响。
- 管理端：无业务实现影响。
- Docker Compose：无配置影响。
- 测试：仅治理校验脚本和 OpenSpec 校验。
