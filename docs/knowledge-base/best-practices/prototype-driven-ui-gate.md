---
title: Prototype-driven UI Gate
purpose: 沉淀带 prototype 页面从需求完善到归档的 UI 开发门禁
content: 原型拆解、UI Skeleton、1440px 视觉验收和 REQ 文档最终一致性检查
source: spec-opt governance
update_method: UI 验收复盘或命令门禁变化时更新
owner: MoonBox 产品团队
status: active
created_at: 2026-08-08 21:08:00
updated_at: 2026-08-08 21:08:00
---

# Prototype-driven UI Gate

## 适用条件

命中任一条件即适用：

- REQ 或 Change 存在 `prototype/web/`、`prototype/admin/`、`prototype/**/prototype.html`、`prototype/**/context.md` 或 PNG 原型。
- `acceptance.md` 存在 `AC-PROTOTYPE-*`。
- Change `design.md` 存在 UI Skeleton 或原型冲突处理章节。

## 标准流程

| 阶段 | 必须完成 |
|---|---|
| `/req-complete` | 原型拆解：页面清单、关键区域、组件层级、状态矩阵、交互触发、数据依赖、响应式断点、1440px 验收焦点 |
| `/req-opsx` | 将拆解写入 Change `design.md` UI Skeleton，并在 `tasks.md` 设置先行 Skeleton 和 1440px 验收任务 |
| `/opsx-apply` | 先落 UI Skeleton，再实现细节；完成 UI 任务前必须跑 1440px 视觉验收 |
| `/opsx-modify` | UI 返修后重新跑 1440px 验收，并更新 Change/REQ 文档中发生变化的口径 |
| `/opsx-archive` | 归档前确认 REQ `requirement.md`、`acceptance.md`、`trace.md` 与最终实现和验收证据一致 |
| Workflow Sync | 只同步已有证据和状态，不替父命令推断视觉通过 |

## 验收 Gate

- [ ] 原型拆解完整，且 `trace.md` 记录 `prototype_refs` 与 `prototype_gate`。
- [ ] Change `design.md` 存在 UI Skeleton，覆盖页面结构、区域边界、组件层级、状态容器、数据依赖、可测选择器和 1440px 验收焦点。
- [ ] Change `tasks.md` 中 UI Skeleton 任务早于细节实现任务。
- [ ] 1440px 桌面视口已检查首屏结构、间距、对齐、主题、字号、弹窗、toast、滚动和文本溢出。
- [ ] 视觉验收证据记录了工具/命令、viewport、页面路径、截图或等价证据入口、结果摘要和例外说明。
- [ ] `/opsx-modify` 后涉及 UI 的旧截图或旧验收结论已失效并重新验证。
- [ ] `/opsx-archive` 前 linked REQ 文档与 Change 设计、最终实现、验收证据一致。

## 常见阻断

| 阻断 | 处理 |
|---|---|
| 只有 prototype 文件，没有拆解 | 回到 `/req-complete <REQ-full-id>` 补齐原型拆解和 AC-PROTOTYPE |
| Change 缺 UI Skeleton | 在 `/req-opsx` 或 `/opsx-apply` 前补 Change `design.md` 与 `tasks.md` |
| 1440px 证据缺失 | 运行浏览器/Playwright 视觉验收并回填 Change trace |
| 返修后仍沿用旧截图 | 重跑 1440px 验收并替换证据 |
| REQ 描述仍是旧原型行为 | 在归档前回填 REQ `requirement.md` / `acceptance.md` / `trace.md` |

