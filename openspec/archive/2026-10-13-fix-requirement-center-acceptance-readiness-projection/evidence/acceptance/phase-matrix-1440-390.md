---
title: BUG-0035 阶段卡片双视口验收矩阵
created_at: 2026-10-12 16:46:00
---

# BUG-0035 阶段卡片双视口验收矩阵

环境：Firefox、隔离治理源副本与临时 SQLite、当前 Web 构建；视口分别为 1440×900、390×900，截图像素比 2。临时 BUG-9101/9102/9103 与 sprint-909 仅存在于隔离副本；其余为该副本从当前治理源复制的实际对象。截图均由 Firefox 响应式视口导出，已逐张核对卡片完整入镜，保存在同目录 `stage-visual/`。

| 阶段 | 样本 | 1440px | 390px | 观察 |
|---|---|---|---|---|
| 待评审 | BUG-0037 | [桌面](stage-visual/pending-review-1440.png) | [移动](stage-visual/pending-review-390.png) | Issue 已生成文档可见；尚无 Change/Sprint 时不显示空分组。 |
| 已评审 | REQ-0045 | [桌面](stage-visual/approved-1440.png) | [移动](stage-visual/approved-390.png) | REQ 使用 requirement.md，Issue 文档持续可见。 |
| 迭代规划 | BUG-9101 | [桌面](stage-visual/planning-1440.png) | [移动](stage-visual/planning-390.png) | Issue 7 份、Sprint 3 份，无 Change 分组。 |
| 待开发 | BUG-9102 | [桌面](stage-visual/ready-dev-1440.png) | [移动](stage-visual/ready-dev-390.png) | Issue 7 份、Change 5 份、Sprint 3 份；研发 0/1 为危险色。 |
| 研发中 | BUG-9103 | [桌面](stage-visual/development-1440.png) | [移动](stage-visual/development-390.png) | 三组入口持续可见；研发 0/1 为危险色。 |
| 验收中 | BUG-0035 | [桌面](stage-visual/acceptance-1440.png) | [移动](stage-visual/acceptance-390.png) | 三组入口及研发、测试、验收进度持续可见。 |
| 已完成 | BUG-0026 | [桌面](stage-visual/done-1440.png) | [移动](stage-visual/done-390.png) | Issue/Change/Sprint 文档在完成阶段仍保留入口。 |
| 独立 Change | add-automated-opsx-acceptance | [桌面](stage-visual/standalone-change-1440.png) | [移动](stage-visual/standalone-change-390.png) | 只显示 Change 与 Sprint 文档，不生成 Issue 分组。 |

交互取证：隔离 BUG-9102 标题在 390px 视口打开 Issue `acceptance.md` 右侧抽屉；1440px 视口点击 Change `tasks.md` 打开题头 `BUG-9102 · tasks.md`，正文“阶段验证任务”可读。Sprint `release-note.md` 与 `acceptance-report.md` 的授权只读抽屉在本 Change `acceptance-fixes.md` 批次一中已有同产品浏览器观察及 GET 200 记录。未发送隔离样本的 Chat 命令。

样式取证：所有样本复用 `.rc-card`、`.rc-doc-group` 和 `.rc-progress` 选择器；既有 Firefox 双视口 computed style 记录显示卡片宽 300px、文档组宽 264px，390px 时 `body.scrollWidth=390`，见本 Change `acceptance-fixes.md` 批次一、二。新截图中三组文档在卡片内换行，未见文字越出卡片或新增页面横向溢出。此处复用同一选择器的既有 computed style，不将截图读数伪称为本轮重新采样。
