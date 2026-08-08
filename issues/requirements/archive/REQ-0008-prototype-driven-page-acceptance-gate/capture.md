---
req_id: REQ-0008-prototype-driven-page-acceptance-gate
status: archived
created_at: 2026-08-08 20:49:11
updated_at: 2026-08-08 22:50:16
recorded_by: product
source: 用户反馈
priority_hint: P1
parent_requirement:
---

# 一句话

建立原型驱动页面开发验收门禁：存在 `prototype.html` 或 `prototype.png` 的页面，必须先完成原型拆解、UI Skeleton、1440px 截图验收和关键 DOM/CSS 尺寸检查，再进入业务逻辑联调。

# 原始描述

建立原型驱动页面开发验收门禁：有 prototype.html/prototype.png 的页面必须先完成原型拆解、UI Skeleton、1440px 截图验收和关键 DOM/CSS 尺寸检查，再进入业务逻辑联调。

# 待澄清

- [ ] 门禁适用范围是否覆盖 Web 前台、管理后台和后续其他端，还是先限定 Web 与管理后台页面。
- [ ] `prototype.html` 与 `prototype.png` 同时存在时，是否以 HTML 原型为主、PNG 为视觉对照，还是必须双重验收。
- [ ] UI Skeleton 的交付标准是否需要明确到路由、组件树、布局区块、交互占位和 mock 数据边界。
- [ ] 1440px 截图验收是否必须由 Playwright 自动生成，并保存到需求、Change 或测试报告目录。
- [ ] 关键 DOM/CSS 尺寸检查需要覆盖哪些指标，例如容器宽高、间距、字体、表格列宽、按钮尺寸、首屏区域和滚动行为。
- [ ] 门禁失败时是否阻断 `/opsx-apply` 继续业务逻辑联调，还是允许带风险记录继续。

# 探索结论

（/req-explore 后人工确认写入）
