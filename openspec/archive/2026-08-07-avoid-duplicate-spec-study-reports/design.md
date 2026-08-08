---
purpose: OpenSpec Change Design
content: spec-study 报告去重设计
created_at: 2026-08-07 00:00:00
updated_at: 2026-08-07 00:00:00
owner: MoonBox 产品团队
---

# Design

## 规则

同一次 `/spec-study` 流程以学习对象、学习主题和用户确认批次作为去重边界：

- 学习阶段候选内容不落盘为正式 study 报告。
- 应用完成后创建或更新一份正式 `study` 报告。
- 对同一流程的后续验证回填或修正更新同一报告。
- `/spec-study` 触发的治理资产应用结果汇总到同一报告，不额外创建重复 governance 日志。

独立 `/spec-opt` 治理变更仍按自身规则生成 `governance` 日志。

## 影响范围

- API：无影响。
- 数据库：无影响。
- Web：无业务实现影响。
- 客户端：无影响。
- 管理端：无业务实现影响。
- Orval：不需要。
- Docker Compose：不需要。
- 测试：治理校验。
