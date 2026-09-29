---
change_id: remove-requirement-center-document-drawer-change-attributes
title: 需求中心文档抽屉移除 Change 属性模块 - 任务
status: applied
created_at: 2026-09-15 23:32:00
updated_at: 2026-09-16 08:45:49
---

# 需求中心文档抽屉移除 Change 属性模块 - 任务

## 1. UI Contract 与 Skeleton

- [x] 1.1 阅读 `RequirementCenterPage.tsx` 的文档抽屉渲染、`openDocument`、卡片文档入口、独立 Change 文档入口和现有测试，确认抽屉内 Change 属性模块的完整删除范围。
- [x] 1.2 按 design.md 的 UI Skeleton 先完成结构调整：抽屉标题区、文档属性区、正文区三段式结构，不渲染 Change 属性模块。
- [x] 1.3 确认删除模块后，加载态、错误态、只读态、可编辑 capture、独立 Change 和多 Change 关联场景均不会出现模块残影。
- [x] 1.4 声明 Mock/API 边界：本 Change 不新增 API 字段、OpenAPI、Orval、请求封装或 Mock 数据。

## 2. 抽屉模块删除与入口保留

- [x] 2.1 删除右侧 Markdown 抽屉中的“Change 追溯属性”条件渲染分支，包括标题、容器、任务进度、告警分隔符、关联 Change 列表和模块内文档按钮。
- [x] 2.2 保留 `current_change`、`related_changes`、`task_progress`、`warnings`、`drift_warnings`、`document_entries` 的读取和抽屉外使用，不删除后端聚合或类型字段。
- [x] 2.3 确认单 Change、多 Change、独立 Change 的文档入口仍可从抽屉外卡片、详情或既有文档分组打开。
- [x] 2.4 确认多 Change 场景不默认选择第一个 Change，不把多个 Change 任务进度汇总成单个 Change。
- [x] 2.5 确认 Issue trace 与 Change trace 的入口标签或上下文可区分。

## 3. 样式与响应式

- [x] 3.1 调整或删除因模块移除产生的残留间距、边框、分隔线或左侧色条；不得新增替代面板。
- [x] 3.2 验证文档属性区展开/收起、键盘焦点、关闭、全屏/恢复和正文滚动不回归。
- [x] 3.3 验证深浅主题、1440px、窄视口、长标题、长 Change ID 和长正文不溢出或遮挡。

## 4. 权限与安全

- [x] 4.1 回归无权对象、只读成员、冻结空间、跨项目同 ID 和直接文档 URL，不得因入口调整暴露受限对象内容。
- [x] 4.2 确认 `trace.md`、非采集池 Markdown 和非 `capture.md` 文件保持只读且保存请求被阻断。
- [x] 4.3 确认缺失文档、加载失败和草稿保护行为不回归。

## 5. 原型驱动 UI 验收

- [x] 5.1 采集 1440px 桌面证据，覆盖普通 REQ 文档、独立 Change 文档、多 Change 关联文档入口回归和文档属性展开态。
- [x] 5.2 采集窄视口证据，覆盖文档属性折叠、正文阅读、关闭/展开和抽屉外 Change 文档入口。
- [x] 5.3 记录 computed style 或等价检查：文档属性区 `padding`、`border`、`gap`、`font-size`、`line-height`、正文顶部间距、抽屉滚动容器 `overflow`。
- [x] 5.4 在 Change trace 中记录截图、computed style、Mock/API 边界和 REQ 最终一致性状态。

## 6. 测试与文档同步

- [x] 6.1 更新前端测试：验证“Change 追溯属性”模块不存在，单 Change、多 Change、独立 Change 文档入口仍可达。
- [x] 6.2 更新或删除仍要求抽屉内 Change 属性模块存在的旧测试。
- [x] 6.3 运行聚焦前端测试和 TypeScript/build 检查；若实现触及 API 或后端聚合，再运行相关后端/API 和 OpenAPI/Orval 校验。
- [x] 6.4 运行 `openspec validate remove-requirement-center-document-drawer-change-attributes --strict`。
- [x] 6.5 实施完成后同步 REQ `acceptance.md`、`trace.md` 与 Change `trace.md` 验证记录。


## 7. 验收返修

- [x] 7.1 根据验收反馈，将卡片上的关联 Change 文档入口收敛为直接紧凑文档入口，不在卡片上展开完整 Change ID。
- [x] 7.2 保留 Issue trace 与 Change trace 可区分：Issue 文档仍显示 `trace.md`，直接文档入口显示 `Change trace.md`。
- [x] 7.3 返修台账、视觉证据、聚焦测试和 TypeScript 校验已回填；详见 `acceptance-fixes.md`。

- [x] 7.4 移除额外的 `Change 文档` / `更多` 弹层，仅保留直接紧凑文档入口；多 Change 使用 `Change 1`、`Change 2` 短前缀区分。

- [x] 7.5 卡片文档入口按文件名和语义去重：`proposal.md`、`spec.md`、`design.md`、`tasks.md`、`sprint.md` 不重复出现，Issue trace 与 Change trace 保持短文案区分；详见 `acceptance-fixes.md`。
