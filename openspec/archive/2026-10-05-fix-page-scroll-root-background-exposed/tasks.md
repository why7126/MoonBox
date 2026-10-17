---
title: 页面滚动底部浅色背景露出修复任务
created_at: 2026-10-04 23:54:49
updated_at: 2026-10-05 00:10:12
---

# 页面滚动底部浅色背景露出修复任务

## 实施任务

- [x] 1. 定位 Chat 与需求中心前台工作台根容器、主题来源和页面卸载路径，确认根层背景同步的最小实现点。
- [x] 2. 实现工作台路由挂载期间的 `html`、`body`、`#root` 背景同步，并确保主题切换即时更新。
- [x] 3. 确保离开工作台页面后恢复登录页、官网首页、管理后台和其他非工作台页面的既有背景行为。
- [x] 4. 保留 `.requirement-center`、`.chat-shell`、输入区、侧边栏和执行详情面板的局部背景，不引入透明穿透。

## 回归验证

- [x] 5. 补充前端测试，覆盖工作台根层背景、深浅主题切换和卸载清理。
- [x] 6. 使用浏览器在 1440px 访问 `/chat` 深色主题，保存 computed style 证据，字段至少包括 `html`、`body`、`#root`、`[data-testid=chat-shell]` 的背景、尺寸和 overflow。
- [x] 7. 使用浏览器触发页面向上滑动或边界 overscroll，保存不露出浅色背景的截图证据。
- [x] 8. 回归 `/requirement-center` 深浅主题根层背景一致性。
- [x] 9. 回归登录页、官网首页、管理后台背景与滚动行为不受影响。
- [x] 10. 运行 `python scripts/validate-openspec-language.py --change fix-page-scroll-root-background-exposed --residual-report`、`python scripts/validate-document-titles.py --change fix-page-scroll-root-background-exposed` 和目标 OpenSpec 校验。

## 文档同步

- [x] 11. 回填 BUG-0027 `acceptance.md`、`trace.md` 与 Change `trace.md` 的验证摘要和证据入口。
- [x] 12. 若修复过程中发现可复用的工作台根层主题经验，评估是否沉淀到 `docs/knowledge-base/incidents/` 或 best-practice；无复用价值时在 trace 中记录不适用原因。
