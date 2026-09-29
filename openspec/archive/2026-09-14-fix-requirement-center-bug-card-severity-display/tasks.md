---
change_id: fix-requirement-center-bug-card-severity-display
source_bug: BUG-0021-requirement-center-bug-card-severity-display
created_at: 2026-09-14 14:12:36
updated_at: 2026-09-14 14:38:53
---

# 任务清单

- [x] 1. 更新后端需求中心响应模型，表达 BUG `severity`。
- [x] 2. 更新后端构卡逻辑，REQ 使用 `priority`，BUG 使用 `severity`，不得对 BUG 默认填充 `P2`。
- [x] 3. 更新前端 `IssueCard` 类型和卡片标签渲染，按类型展示分级。
- [x] 4. 更新前端和后端测试 fixture，移除 BUG 使用 `priority` 的错误样本。
- [x] 5. 补充后端 API / 构卡测试，覆盖 REQ priority、BUG severity、缺失或非法 severity 的可诊断行为。
- [x] 6. 补充前端卡片测试，覆盖 BUG 显示 severity、REQ 保持 P0-P3、独立 Change 卡片不回退。
- [x] 7. 如响应 schema 影响 OpenAPI / Orval 类型，执行生成或校验并复核目标 schema。
- [x] 8. 回填 BUG-0021、sprint-006 与 Change 验收记录。
- [x] 9. 若修复经验具备复用价值，沉淀到 `docs/knowledge-base/incidents/` 或后续 Sprint 复盘。

## 验收返修记录

- [x] 2026-09-14 `/opsx-modify`：根据验收反馈“不同的值，是否颜色不一样”，为 REQ `priority` 和 BUG `severity` 标签补充等级值 class 与分级颜色样式，并补充前端样式测试。

## 附件截图逐项视觉对照表

| 项 | 期望 | 实际证据 | 偏差 | 处置 |
|---|---|---|---|---|
| 分级标签颜色 | REQ `P0/P1/P2/P3`、BUG `blocker/critical/high/medium/low` 在各自体系内颜色可区分 | 用户本轮文本反馈；返修前 `globals.css` 仅有 `.rc-priority-tag` 与 `.rc-severity-tag` 两类基础颜色 | 缺少按等级值细分的颜色规则 | 已增加等级值 class、CSS 色阶和前端样式断言 |
