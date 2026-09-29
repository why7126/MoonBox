---
change_id: add-requirement-center-sprint-dropdown-status
requirement_id: REQ-0032-requirement-center-sprint-dropdown-status
sprint_id: sprint-006
acceptance_status: implemented_pending_acceptance
created_at: 2026-09-14 15:36:27
updated_at: 2026-09-14 18:11:58
---

# 实现验收摘要

## 验收结论

REQ-0032 的实现已完成并通过自动化验证，等待用户或归档阶段进行最终验收确认。

## AC 对照

| AC | 实现结果 | 证据 |
|---|---|---|
| AC-001 | Sprint 筛选下拉展示 Sprint ID 与状态；全部 Sprint 保持聚合入口 | 前端测试、Playwright 截图 |
| AC-002 | 后端从活动与归档 Sprint 事实源派生状态 | 后端集成测试 |
| AC-003 | 状态缺失、非法和冲突降级为状态待核实并保留 warning | 后端集成测试、前端测试 |
| AC-004 | 筛选、刷新和项目切换行为不回退 | 前端测试 |
| AC-005 | 选择单个 Sprint 后仅展示匹配卡片 | 前端测试 |
| AC-006 | 错误与未知状态不暴露内部路径或原始内容 | 后端测试、观测边界说明 |
| AC-007 | 工具栏筛选与加入迭代弹窗复用状态映射 | 前端实现与类型检查 |
| AC-008 | API 字段已同步 OpenAPI、Orval、API 文档和测试 | OpenAPI/Orval 生成、`docs/03-api-index.md` |
| AC-UI-001 到 AC-UI-006 | 状态标签低噪音、深浅主题可读、桌面与窄屏不重叠、交互状态可达 | Playwright 截图与 computed style |
| AC-PROTOTYPE-001 到 AC-PROTOTYPE-005 | 原型拆解、UI Contract、Skeleton、视觉证据和实现一致性已完成 apply 阶段检查 | Change `design.md`、`trace.md`、evidence |
| AC-OBS-001 到 AC-OBS-003 | 未新增 DB/任务链路；响应与 warning 只保留安全摘要 | Change `trace.md`、`test-plan.md` |

## 证据文件

| 文件 | 说明 |
|---|---|
| `evidence/ui/sprint-status-dark-1440.png` | 1440px 深色主题下拉打开态 |
| `evidence/ui/sprint-status-light-390.png` | 390px 浅色窄屏下拉打开态 |
| `evidence/ui/sprint-status-styles.json` | 状态徽标 computed style 与页面错误采样 |

## 验收返修结果

| 时间 | 反馈 | 结果 | 证据 |
|---|---|---|---|
| 2026-09-14 18:11:58 | 筛选子下拉与触发器距离过远；删除“已完成 / 归档”重复筛选项。 | 已修复。子下拉恢复贴近触发器；筛选面板内不再展示该 checkbox。 | `evidence/ui/sprint-status-styles.json` 中 1440px 与 390px 样本 `popoverGapPx=6`；相关 Vitest 2 passed。 |
