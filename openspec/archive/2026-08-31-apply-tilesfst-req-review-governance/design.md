---
change_id: apply-tilesfst-req-review-governance
status: applied
created_at: 2026-08-31 08:36:34
updated_at: 2026-08-31 08:36:34
---

# Design

## 学习来源

学习对象：ProjectTilesFST（本地只读项目）

已采纳候选项：

- A：无 flag 默认通过。
- B：正向路径命令提示去参数化。
- C：`req-review` 显式接 AI Usage Hook。
- D：评审后目录迁移、当前态看板和子文档一致性收尾闭环。

## 适配策略

MoonBox 继续保留引导式反馈契约，但只在材料缺失、风险判断、用户选择或阻塞处理时触发。常规 `/req-review REQ-xxxx-slug` 进入正向评审通过路径；`--approve` 保留为兼容别名；`--reject` 和 `--defer` 仍为显式反向结果。

## 执行顺序

1. 读取目标 REQ 的 requirement、acceptance、trace 和必要 prototype。
2. 执行评审清单；若存在阻断风险，按引导式反馈契约收敛，不静默通过。
3. 写入 `review.md`，同步 `trace.md` 与 `requirement.md` 状态。
4. 默认 approve 或 `--approve` 时，在 Workflow Sync 前运行 `promote-issue-stage.py` 将目录迁入 `review/`。
5. 运行 `sync-workflow-status.py --event req.review --req <REQ-full-id> --sprint auto`，刷新 trace、registry、当前态看板和可安全同步的子文档。
6. Workflow Sync 成功后运行 AI Usage Hook，仅输出 compact 摘要。
7. 输出下一步、待用户决策/处理和执行链路复盘。

## 文档同步

正向命令统一推荐 `/req-review <REQ-full-id>`。只有需要明确拒绝或延后时才提示 `--reject` 或 `--defer`。

## 验证策略

- 上下文预算与技能输出契约校验。
- OpenSpec 中文和目标 Change 结构校验。
- 目录结构校验。
- Sprint scope 校验。
- Workflow Sync dry-run/正式同步。
- AI Usage Hook。
