---
req_id: REQ-0026-requirement-center-standalone-change-cards
title: 需求中心支持独立 OpenSpec Change 卡片
status: done
created_at: '2026-09-12 17:51:26'
updated_at: 2026-09-14 08:44:37
recorded_by: product
source: 反馈
parent_requirement: null
priority: P1
---

# 一句话
需求中心支持未关联 REQ/BUG 的独立 OpenSpec Change 卡片，覆盖活动与归档 Change。

# 原始描述
需求中心支持独立OpenSpec Change卡片，聚合未关联REQ/BUG的活动及归档Change，支持阶段映射、文档读取、统计筛选与项目授权，避免关联Change重复展示。

# 背景与范围
- 来源：REQ-0022-local-project-import-product-iteration 验收后的 explore；示例为 unify-issue-classification-metadata。
- 已核对现状：看板仅从 REQ/BUG 注册表聚合；独立 Change 虽已纳入 Sprint，也没有卡片；现有 Change 文档授权依赖关联 Issue。
- 同一交付单元覆盖独立 Change 识别、活动/归档聚合、阶段映射、文档入口、统计筛选与项目内授权。
- 已关联 REQ/BUG 的 Change 继续归属原卡片，避免重复统计及展示；不自动创建虚构 REQ/BUG。
- 初判 P1：补齐研发看板覆盖范围与授权读取闭环，不属于当前线上阻断。

# 待澄清
- [ ] 独立 Change 的关联识别、关联缺失与去重规则，以及活动/归档同 ID 的优先级。
- [ ] Change 状态证据的优先级、缺失状态处理及阶段动作范围。
- [ ] 主文档、Sprint、trace 的显示顺序及缺失提示；不强制要求 Issue 文档。
- [ ] 项目角色与对象授权、只读/编辑能力，避免绕过原权限。
- [ ] 统计筛选、长 ID、窄屏与归档展示的验收细节。

# 建议验收方向
- 示例独立 Change 可见，已关联 Change 不重复出现。
- 活动及归档来源、状态和文档匹配真实事实源。
- Change 类型筛选与总数一致，REQ/BUG 现有行为不回归。
- 无权限用户不能通过卡片或文档接口读取独立 Change。

# 探索结论
本次仅保存采集线索与待澄清项；正式方案由后续 req-explore/req-generate 收敛。

# 影响层与观测
product_data_collection_observability：预计 affected_layers=[web,api]；聚合、文档读取及权限验证纳入后续验收。DB/部署/客户端生成是否受影响待方案确认，本次仅采集文档，无实现或采集链路变更。
