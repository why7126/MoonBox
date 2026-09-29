---
change_id: add-requirement-center-current-iteration-capacity
source_requirement: REQ-0031-requirement-center-current-iteration-capacity
sprint: sprint-006
created_at: 2026-09-15 09:33:51
updated_at: 2026-09-15 09:33:51
owner: product
---

# 验收返修台账

## 返修批次

| 时间 | 反馈来源 | 范围判断 | 处理状态 |
|---|---|---|---|
| 2026-09-15 09:33:51 | `/opsx-modify`：需求中心卡片仍提示“验收来源待核实：未找到交付验证记录” | 范围内；属于 Change 交付验证来源入口补齐，不改变当前迭代容量业务行为、API、DB、Web UI、权限、部署或观测契约 | 已处理 |

## 偏差证据

| 项 | 记录 |
|---|---|
| 期望 | applied Change 在需求中心验收中卡片可识别 Change 内交付验证来源，不展示“未找到交付验证记录”。 |
| 实际 | `trace.md` 存在 `## 验证证据`，但当前需求中心识别白名单不接受该标题，也未声明 `acceptance_refs`。 |
| 证据链 | 需求中心 Change 索引返回 `验收来源待核实：未找到交付验证记录`；后端识别逻辑接受 `acceptance_refs` 或非空 `验证记录`、`验证摘要` 等章节。 |
| 根因状态 | confirmed。 |

## 调整内容

- 在 `trace.md` Frontmatter 增加 `acceptance_refs: [acceptance-fixes.md]`。
- 在 `trace.md` 增加非空 `## 验证记录`，指向既有 `## 验证证据`、容量视觉证据、前后端验证和 OpenSpec strict 结果。
- 在 `tasks.md` 保留既有返修记录，并补充本次验证来源入口返修勾选与台账链接。

## 验证证据

- 需求中心 Change 索引复核：本 Change 的归档动作阻断原因为 `None`。
- `openspec validate add-requirement-center-current-iteration-capacity --strict`：通过。
- `python scripts/validate-openspec-language.py --change add-requirement-center-current-iteration-capacity --residual-report`：通过。

## REQ 子文档一致性扫尾检查

- 已检查现有 `requirement.md`、`acceptance.md`、`trace.md`、`business-flow.md`、`user-stories.md` 与 `prototype/**` 一致性。
- 本次只补齐 Change 内交付验证来源入口，不改变容量计算口径、展示行为、接口字段、Mock/API 边界或验收标准，REQ 子文档无需手工更新。
