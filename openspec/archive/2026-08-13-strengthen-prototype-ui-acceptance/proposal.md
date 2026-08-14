# Proposal: 强化原型驱动 UI 验收规范

## Background

REQ-0012 前台需求中心在 Sidebar、9 阶段看板、用户菜单、前后台一致性、Mock 数据边界和登录入口等方面经历多轮视觉返修，说明现有 Prototype-driven UI Gate 只约束了“需要有原型拆解、UI Skeleton 和 1440px 验收”，但缺少可执行的 UI Contract、前后台一致性 checklist、关键交互截图、computed style 和 Mock/API 边界声明。

## Goals

- 为带 `prototype/` 的 UI Change 增加 UI Contract，提前锁定事实源、布局、视觉 token、交互、权限、图标文案和数据边界。
- 将 Skeleton 首轮确认、1440px/关键交互截图、computed style 验收和 stale 证据失效规则纳入门禁。
- 明确前后台一致性 checklist，减少 Sidebar、用户菜单、字体层级、折叠按钮等跨端视觉差异。
- 明确 Mock/API 边界，避免 Mock 数据被误判为真实接口已完成。
- 同步规则、专项标准、技能入口、AGENTS 路由和治理日志。

## 非目标

- 不修改 `src/` 业务代码、前台实现、后台实现、API 或数据库。
- 不为 REQ-0012 新增业务返修项；本 Change 只沉淀后续治理规范。
- 不引入新的截图自动化脚本；本次先定义验收合同和人工/工具可执行门禁。

## 影响范围

- 影响带 prototype 的 UI REQ/Change 的需求完善、OpenSpec 转换、实现、返修和归档流程。
- 影响 `.agents/skills/req-opsx`、`.agents/skills/opsx-apply`、`.agents/skills/opsx-modify` 的执行口径。
- 影响 `rules/ui-design.md`、`docs/standards/` 和 `AGENTS.md` 的 UI 读取路由。
