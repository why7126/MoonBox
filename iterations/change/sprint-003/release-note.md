---
purpose: sprint-003 发布说明
sprint_id: sprint-003
status: planning
lifecycle_stage: change
created_at: 2026-08-14 17:00:00
updated_at: 2026-08-15 10:04:45
---

# sprint-003 发布说明

## 治理变化

- 新增证据化根因分析治理：已确认根因必须有证据链；证据不足时必须输出人工补证操作步骤。
- 新增 root-cause evidence 校验脚本，用于 BUG 和 BUG 来源 Change 的结构化门禁。

## 业务影响

- 修复管理后台用户管理列表展示：角色以无边框、无浅底色的图标文字标签展示，状态标签沿用空间管理页无边框圆形 check 图标语义表达，最近登录时间、创建时间和更新时间统一展示，并新增更新时间列。
- 不修改 API、DB、客户端生成物或 Docker Compose。
