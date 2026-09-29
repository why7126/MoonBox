---
created_at: 2026-09-15 09:46:43
updated_at: 2026-09-15 09:46:43
---

# 设计：返修执行态与验收态分层

## 状态分层

| 层级 | 职责 | 本次约束 |
|---|---|---|
| Change canonical status | 表达 OpenSpec Change 是否 proposed、in_progress、applied、archived | apply 完成后继续保留 `applied`，不因返修执行覆盖为普通 `in_progress` |
| execution facts | 记录首次 apply 的 started/completed/last_event | 保留 `execution.completed_at`，不伪造或重写首次完成时间 |
| repair projection | 表达 `/opsx-modify` 当前是否正在返修或待复验 | 返修执行中展示“研发中”，返修完成后展示“验收中” |
| acceptance status | 表达 linked Issue 是否待人工复验 | `opsx.modify` 同步后保持 `acceptance_status: pending` |

## 流转

```text
applied / 验收中
→ opsx-modify 开始处理验收反馈
→ 用户可见阶段：研发中
→ 完成返修任务、验证、文档同步、Workflow Sync
→ 用户可见阶段：验收中
→ 人工复验通过后 archive
```

## 边界

- 如果返修仍在原 Change 范围内，继续走 `/opsx-modify`。
- 如果反馈扩大 API、DB、权限、部署、对象存储或产品边界，停止返修并创建新的 REQ、BUG 或 OpenSpec Change。
- 如果需要持久化“返修中”机器字段，应新增专门字段或投影语义；不得把首次 apply 完成态回退为普通 `in_progress`。

## 验证策略

- OpenSpec delta 描述应覆盖返修执行中与返修完成后的阶段展示。
- `opsx-modify` Skill 应明确开始返修和完成返修的展示语义。
- 长期规则和命令顺序文档应与 Skill 保持一致。
- 本 Change 为纯治理变更，业务测试不适用。
