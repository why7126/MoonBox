---
req_id: REQ-0023-product-workbench-modern-ops-visual-system
status: done
created_at: 2026-08-30 23:00:42
updated_at: 2026-09-13 23:47:24
recorded_by: product
source: explore
parent_requirement:
priority: P1
---

# 一句话

MoonBox 产品工作台全面升级为现代 Ops 视觉系统，并允许同步调整品牌与 UI 设计系统。

# 原始描述

用户在 `/explore` 对比当前实现与附件 `moonbox-board.html` 后，选择“全面向附件风格靠拢（包括品牌）”，目标是获得更现代的视觉表现，并预期可能涉及 UI 设计系统调整。

# 待澄清

- [ ] 品牌升级范围：仅登录后的产品工作台，还是首页、登录页、管理后台与公开产品手册全部同步。
- [ ] 视觉系统方向：是否采用“现代 Ops 工具台”为主，保留 MoonBox 金色强调与品牌资产作为识别点。
- [ ] 字体与 token 策略：是否从现有 Noto Serif SC / Noto Sans SC / EB Garamond 体系调整为更现代的 UI 字体与等宽辅助字体。
- [ ] 迁移节奏：是否先以需求中心为试点，再扩展到后台、工作台和全局组件。
- [ ] 验收边界：需要覆盖哪些页面、主题、断点和关键交互截图。

# 探索结论

前置探索倾向认为：附件风格更适合强化“AI 原生软件工厂”的生产力工具感，但直接全面替换现有品牌会冲击 `rules/ui-design.md` 中的东方器物感、衬线标题、近直角和克制排版基调。推荐在后续 `/req-explore` 中重点评估“双品牌分层”或“全站统一现代化”两条路线，并明确设计系统 token、组件规范和视觉验收迁移策略。
