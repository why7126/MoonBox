---
created_at: 2026-08-10 22:36:56
updated_at: 2026-08-10 22:36:56
owner: MoonBox 产品团队
change_id: optimize-issues-changelog-current-state-index
---

# 设计说明

## 设计原则

REQ/BUG 根目录 CHANGELOG 只回答“当前有哪些 Issue、各自处于什么阶段、下一步看哪里”，不回答“完整状态变化链路是什么”。完整状态变化链路仍由单条 Issue `trace.md` 负责。

## 看板模型

REQ 看板字段：

```text
REQ | 标题 | 当前状态 | 阶段 | 优先级 | 关联 Sprint | 关联 Change | 最近更新时间 | 下一步 | 事实源
```

BUG 看板字段：

```text
BUG | 标题 | 严重等级 | 当前状态 | 阶段 | 关联 Sprint | 关联 Change | 最近更新时间 | 下一步 | 事实源
```

## 维护策略

- 新建、评审、纳入 Sprint、创建 Change、apply、archive、状态同步或历史漂移修复后，更新对应 Issue 行。
- 生成或补齐文档后，仅当当前状态、下一步或事实源发生变化时更新对应 Issue 行。
- 普通文案润色、格式调整、错别字修复和非状态性验收措辞调整不要求更新 CHANGELOG。
- 看板中的状态字段是便捷快照，不参与机器状态判断；需要确认事实时继续读取 `_registry.yaml`、目标 Issue `trace.md`、Sprint 四件套或 OpenSpec Change。

## 风险与控制

- 风险：看板快照和事实源发生漂移。
- 控制：CHANGELOG 明确标注自身不是事实源；命令和脚本判断不得读取 CHANGELOG 替代 `trace.md` 或 registry。

- 风险：看板记录过多业务细节，重新变成 trace 副本。
- 控制：摘要字段收敛为下一步和事实源，不保留每步事件说明，不复制复现日志、验收全文或 UI 证据清单。
