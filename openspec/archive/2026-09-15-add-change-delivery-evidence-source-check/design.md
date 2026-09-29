---
created_at: 2026-09-15 09:38:43
updated_at: 2026-09-15 09:38:43
---

# 设计：Change 交付验证来源校验

## 设计决策

| 决策 | 说明 |
|---|---|
| 识别口径复用 | 脚本直接复用 `app.governance.change_index.ChangeIndex.acceptance_source_reason()`，避免脚本、需求中心卡片和后端归档门禁出现不同判断。 |
| 默认扫描范围 | 默认扫描 active applied Change，也就是需求中心验收中阶段对应的 active Change。非 active、非 applied Change 输出为 skipped，不作为失败。 |
| 聚焦模式 | 支持重复传入 `--change`，用于 `/opsx-archive` 前校验单个或少量目标 Change。 |
| 输出模式 | 默认文本报告适合人工阅读；`--json` 输出 `status`、checked/missing/skipped 计数和明细，适合 CI 或后续脚本调用。 |
| 安全边界 | 脚本只读取治理文档元数据和 Change 内 Markdown，不输出文档正文、绝对路径、密钥、env 内容或原始日志。 |

## 失败语义

- 任一被检查的 active applied Change 缺少可识别验证来源时，脚本返回 `1`。
- 指定的 Change 不存在时，脚本返回 `1`，并在 missing 明细中提示 `Change not found`。
- 非 active 或非 applied 目标被跳过，不阻断默认扫描；聚焦使用时报告 skipped，便于确认目标状态。

## 不变范围

- 不新增或修改需求中心 API。
- 不修改后端 `ChangeIndex` 识别逻辑。
- 不把 tasks 全勾、Workflow Sync 成功、最终回复或治理日志本身视为交付验证来源。
- 不自动补建 `acceptance.md`、`verification.md` 或修改任何 Change 文档。
