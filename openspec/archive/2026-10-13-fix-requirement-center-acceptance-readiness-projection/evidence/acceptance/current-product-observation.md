---
title: BUG-0035 当前产品验收观察摘要
created_at: 2026-10-12 15:40:00
updated_at: 2026-10-12 18:18:51
---

# BUG-0035 当前产品验收观察摘要

- 环境：本地 MoonBox Web v0.1.0；Firefox；平台超级管理员；`/requirements` 已刷新且统计显示 38 个可见对象。仅记录脱敏的对象编号与计数，不保存会话正文或凭证。
- BUG-0035 验收中：Issue、Change、Sprint 三组分别有 7、6、3 个文档入口；研发 14/14、测试 14/14、验收 9/11；卡片不显示归档动作。
- BUG-0033 验收中：研发 11/11，无测试分母，验收 0/11；BUG-0029 为 0/6，BUG-0034 为 0/5。BUG-0028 已评审，保留 Issue 文档入口。
- BUG-0025 验收中：研发 42/42、测试 38/39、验收 24/52；无归档入口。此观察只证明当前页面投影，不能证明 Chat 归档命令的服务端拒绝。
- 取证状态：Firefox 当前页面可读；Chat 工作台已连接本地项目，但历史会话搜索仍显示“正在读取会话”，尚未取得 BUG-0025 当前命令轮次。
- 视觉边界：当前浏览器只取得桌面无障碍树，未保存本轮 1440px 与 390px 的完整阶段矩阵截图和 computed style；AC-009 仍待补。

2026-10-12 补充：用户授权隔离样本后，临时源副本的 BUG-9101/9102/9103 分别出现在迭代规划、待开发、研发中。Firefox 页面无障碍树显示 Issue/Change/Sprint 分组与预期一致；响应式截图导出整窗且目标卡片被裁切，双视口视觉证据及 computed style 仍缺。详见 `isolation-stage-and-archive-observation.md`。

用户另授权正式 BUG-0025 归档尝试。旧轮次 `f3d624c6-2422-4eee-9a49-3181af97d5fd` 先被任务与规格合并校验阻断，未触达验收门禁。2026-10-12 修正 AF-041 与 delta 规格后，新 Chat 轮次 `9bffe2e8-bb23-4559-b132-b4feb6856ef6` 已完成；同轮 `execution.tool` 序号 38 实际执行 `bash scripts/archive-change.sh fix-requirement-center-command-chain-write-gap --finalize`，退出码 1，结果含 `ACCEPTANCE_GATE_BLOCKED issue_acceptance_pending checked=24 total=52`。正式 Change `trace.md` 仍在 active 目录，Issue `acceptance.md` 保持 pending；无规格合并、目录迁移或 Issue 状态推进。本段只保留命令标记、计数和状态，不保存 Chat 正文或工具原始输出。

2026-10-12 返修批次七：Firefox 常驻产品 `/requirements` 已刷新，BUG-0035 的 Change 组显示 `proposal.md`、`spec.md`、`design.md`、`tasks.md`，同卡片仍有四份文档“缺少”红字；该服务仍运行返修前 Web 包。修复版隔离 Vite 预览用合成 API 在 Chrome 1440×900 和 390×844 显示四份 Change 文档且无缺失红字；computed style 为卡片宽 300px、文档区宽 264px，`scrollWidth=clientWidth=264px`，页面宽分别为 1440px 和 390px。此项只验证修复版前端组件与响应式表现，不声称常驻产品已经部署新包；源文件回归与完整视觉对照见 `acceptance-fixes.md`。
