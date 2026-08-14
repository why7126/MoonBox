---
req_id: REQ-0013-requirement-center-real-data-integration
status: archived
created_at: 2026-08-10 20:04:27
updated_at: 2026-08-13 22:45:12
recorded_by: product
source: 用户反馈
priority_hint: P1
parent_requirement: REQ-0012-frontend-requirement-center
---

# 一句话

需求中心真实数据接入：在 REQ-0012 前台需求中心 UI 原型与交互骨架基础上，新增真实数据聚合与页面状态能力，替换 Mock 数据源。

# 原始描述

当前 REQ-0012 已完成前台需求中心 UI 原型与交互骨架，但页面仍使用 Mock 数据；需要新增真实数据接入能力，聚合 REQ、BUG、Sprint、OpenSpec Change、空间和用户权限数据，替换静态 `initialIssues`、`workspaces`、`currentUser`，并支持真实统计、筛选、搜索、权限态、加载态和错误态。

# 待澄清

- [ ] 需求中心真实数据来源以现有后端 API 聚合为主，还是新增专用 BFF/聚合接口？
- [ ] 空间与用户权限数据的最小权限模型、可见范围和无权限提示策略。
- [ ] 统计口径：REQ/BUG/Sprint/OpenSpec Change 状态映射、跨空间聚合范围和刷新策略。
- [ ] 加载态、空态、错误态是否沿用 REQ-0012 原型视觉，还是需要补充独立异常状态设计。

# 探索结论

（/req-explore 后人工确认写入）
