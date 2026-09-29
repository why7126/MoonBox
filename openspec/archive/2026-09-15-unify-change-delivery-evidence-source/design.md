---
created_at: 2026-09-15 09:07:02
updated_at: 2026-09-15 09:07:02
---

# 设计：证据必有，文件不固定

## 现状

需求中心验收中卡片的交付验证来源识别顺序为：

1. `trace.acceptance_refs` 指向的 Change 内 Markdown 文件。
2. 非空 `acceptance.md` 或 `verification.md`。
3. `trace.md` 中非空的验证类章节。

纯治理 Change 的验证摘要通常写入治理日志、最终输出或 `trace.md` 的执行记录表；这些事实人可读，但不一定命中需求中心的验证来源白名单。

## 目标

- 保留独立 Change 的轻量文档形态，不强制生成 `acceptance.md` 或 `verification.md`。
- 将 applied Change 的最小交付验证来源收敛为 Change 内事实源，避免证据散落在最终回复或治理日志中。
- 让 `/spec-opt`、`/opsx-apply` 和 `/opsx-archive` 对同一证据契约使用一致口径。

## 非目标

- 不修改需求中心后端识别逻辑。
- 不批量迁移历史 Change。
- 不把 tasks 全勾、`status: applied` 或 Workflow Sync 成功当作验收通过证据。

## 决策

| 决策 | 结论 | 理由 |
|---|---|---|
| 是否强制 `acceptance.md` | 不强制 | 纯治理 Change 常只需记录校验摘要，固定文件会增加空壳文档和语义噪音。 |
| 默认证据落点 | `trace.md` 的 `## 验证记录` 或 `## 验证摘要` | 与执行事实同处 Change 内，需求中心可识别，归档复核成本低。 |
| 复杂证据 | 使用 `trace.acceptance_refs` 指向 Change 内 Markdown | 适合 UI 截图、长验收报告、外部脚本摘要或多批次证据。 |
| 完成门禁 | `/opsx-apply` 完成同步前检查证据入口 | 防止 applied 后才在卡片暴露“验收来源待核实”。 |

## 风险与控制

| 风险 | 控制 |
|---|---|
| 验证章节变成流水账 | 只记录命令、结果、影响边界和不适用原因；详细证据可用 `acceptance_refs` 引出。 |
| 与治理日志重复 | 治理日志保留长期治理摘要，Change `trace.md` 保留卡片和归档可识别的最小验证入口。 |
| 历史 Change 仍有提示 | 不批量迁移；遇到具体卡片时用 `/opsx-modify` 或聚焦修复补齐证据入口。 |
