---
change_id: add-ui-reference-replication-governance
change_type: governance
status: proposed
created_at: 2026-09-02 19:12:31
updated_at: 2026-09-02 19:12:31
---

# Proposal: 强化 UI 参考稿复刻动作矩阵治理

## 背景

MoonBox 已建立 UI Reference Replication Contract，用于约束附件 HTML、截图、标注图、既有页面或参考稿的一对一复刻和风格迁移。但近期 UI 返修中仍出现“先改入口按钮，再补 modal，再补文案和状态”的逐按钮问答式返修，说明现有契约对按钮触发的 modal 组件族没有足够前置约束。

本变更将“动作按钮 → modal 类型 → selector → 状态 → 验收证据”矩阵纳入 UI 参考稿复刻门禁，并要求同一动作族的按钮、弹窗、抽屉、Popover、确认框、Action Modal 或 AI 面板一次性设计、实现和验收。

## 变更内容

- 在 UI Reference Replication Gate 中新增动作按钮与 modal 组件族矩阵。
- 要求 `/req-complete` 记录矩阵种子，`/req-opsx` 在 Change `design.md` 固化矩阵，`/opsx-apply` 在实现前确认矩阵完整。
- 要求 `/opsx-modify` 遇到单个按钮或 modal 反馈时先扩展到所属动作族，避免继续逐按钮返修。
- 要求 `/opsx-archive` 复核动作按钮矩阵、selector、computed style、截图和非目标保留一致。
- 将长期事实源放在 `docs/standards/prototype-ui-acceptance.md`，入口约束放在 `rules/ui-design.md` 和相关命令 Skill。

## 影响范围

- 治理文档：`rules/ui-design.md`、`docs/standards/prototype-ui-acceptance.md`、`rules/agent-context-budget.md`。
- Agent 技能：`.agents/skills/req-complete`、`req-opsx`、`opsx-apply`、`opsx-modify`、`opsx-archive`。
- OpenSpec：新增 `harness-runtime` 治理 delta。
- 业务实现：不涉及，不修改 `src/`、API、数据库、Web、管理端、客户端生成或 Docker Compose。

## 非目标

- 不改变具体业务页面、按钮文案、modal 样式或前端组件代码。
- 不新增自动化 UI 校验脚本。
- 不替代已有附件截图逐项视觉对照表、computed style 采样和 1440px 视觉验收门禁。

## 产品数据采集与链路观测

```yaml
product_data_collection_observability:
  status: not_applicable
  affected_layers: []
  reason: 本 Change 仅修改治理规则、Agent 技能和 OpenSpec 文档，不改变 API、DB、请求日志、行为事件、Task Trace、对象存储或 Web/管理端请求封装。
  validation: 通过治理校验和 OpenSpec validate 验证；业务观测链路无需变更。
```
