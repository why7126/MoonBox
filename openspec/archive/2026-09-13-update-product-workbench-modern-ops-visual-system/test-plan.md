---
change_id: update-product-workbench-modern-ops-visual-system
status: updated
created_at: 2026-08-31 08:42:00
updated_at: 2026-08-31 09:45:00
---

# 测试计划

## 自动化验证

- 设计系统校验：检查硬编码颜色、绕过设计系统组件、原生确认弹窗和 toast 使用。
- 前端聚焦测试：覆盖需求中心筛选、刷新、看板、抽屉、主题切换、用户菜单和状态反馈。
- 管理后台聚焦测试：覆盖 CRUD 列表分页、筛选、状态操作确认弹窗和 fixed toast。
- OpenSpec 校验：验证 proposal、design、tasks 和 delta spec 结构。

## 视觉验证

- 1440px 深色主题默认首屏。
- 1440px 浅色主题默认首屏。
- 侧边栏展开/收起。
- 筛选 Popover 打开、active badge、外部点击关闭。
- 用户菜单和空间二级浮层。
- 看板横向滚动、空列、错误态、卡片 hover。
- 右侧 Markdown/任务/AI 抽屉。
- 390px 或等价窄屏布局。
- 验收返修后复验移动端品牌区与标题挤压、Kanban 空列承载感、筛选 Popover 密度和右下 AI 入口位置。

## 证据要求

长期验收证据写入 `openspec/changes/update-product-workbench-modern-ops-visual-system/evidence/` 或在 Change trace 中记录脱敏摘要。本地临时截图可先放入被 ignore 的 `tmp/visual-evidence/`，归档前不得只依赖临时路径。
