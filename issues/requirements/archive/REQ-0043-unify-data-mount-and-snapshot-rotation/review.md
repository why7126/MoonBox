---
review_id: REV-REQ-0043-001
requirement_id: REQ-0043-unify-data-mount-and-snapshot-rotation
title: 统一 data 目录边界与本地数据挂载及快照轮转评审记录
date: 2026-10-08
participants:
  - 产品团队
result: approved
created_at: '2026-10-08 14:25:36'
updated_at: '2026-10-08 14:25:36'
---

# 统一 data 目录边界与本地数据挂载及快照轮转评审记录

## 评审结论

通过。用户已选择按用途分目录、自动本地快照默认保留 2 份、配置 `0` 关闭自动创建；需求文档把业务库路径、旧数据迁移、轮转保护和恢复验收组成一条独立闭环。评审通过不表示已迁移数据库、清理历史备份或验证生产部署。

## 评审清单

| 检查项 | 结论 | 依据 |
|---|---|---|
| 范围及非目标 | 通过 | PRD 明确本地业务库、挂载和快照轮转；执行器状态合库、按空间分库及异机灾备不在范围内 |
| 验收可测试 | 通过 | 19 条 AC 覆盖路径一致性、双库差异、配置矩阵、受保护快照、删除恢复和故障注入 |
| 优先级与依赖 | 通过 | P1；关联已交付的 REQ-0025，本次交付与验收闭环独立 |
| UI 策略 | 不适用 | 无产品 UI、prototype 或参考稿 |
| 相似需求 | 通过 | trace 已说明 REQ-0025 与 REQ-0042 的边界 |
| 产品数据采集与链路观测 | 通过 | 已引用 `docs/standards/product-data-collection-observability.md`，声明 DB、Task Trace 与 span；未规划 HTTP 或 UI 入口的 request_logs、usage_events 和请求封装有具体 N/A 原因 |
| 知识库承接 | 通过 | 无 UI 横切标签；承接 sprint-007 关于 legacy runtime 迁移及证据分层的经验 |

## 条件通过项

- [ ] 纳入 Sprint 与创建 Change 后，细化历史业务库差异的人工确认与回滚步骤；未确认来源前不得覆盖数据库文件。
- [ ] 在 Change 设计中明确自动与手动副本的可靠区分、治理成套备份引用保护、旧快照分批过期和配置 `0` 后的历史库存处理。
- [ ] 实施验收须分别提供本地 Docker 挂载、SQLite 完整性与恢复、MySQL 生产门禁、故障注入和脱敏任务观测证据。

## 风险与状态

数据覆盖和误删备份属于高影响风险；上述条件作为设计和实施门禁，不阻断需求评审通过。当前仅将需求状态批准为 `approved`，后续须先纳入 Sprint，再创建 OpenSpec Change。

```yaml
result: approved
status_after_review: approved
reviewed_at: 2026-10-08 14:25:36
approved_at: 2026-10-08 14:25:36
next: /sprint-propose --req REQ-0043-unify-data-mount-and-snapshot-rotation
```
