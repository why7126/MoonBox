---
title: 验收卡片检查入口迁入操作流程设计
created_at: '2026-10-31 23:21:31'
updated_at: '2026-11-01 00:22:06'
---

# 验收卡片检查入口迁入操作流程设计

用户最新确认：不新增弹窗，仅移除卡片“检查验收条件 / 验收待检查”整行，检查沿用现有流程。此前归档准备面板方案已撤回；不修改原有按钮、禁用条件、确认流程、检查API或服务端门禁。

## 设计方案与冲突处理
用户最新指令优先于旧原型与已批准的新面板方案；撤回ArchivePreparationDialog及其预览。仅删除RequirementCenterPage的acceptance-check JSX，保留checkObject用于迭代检查，不改action判定。
## UI Contract 与 UI Skeleton
无新组件或面板；用户确认的是现有卡片局部删除。保留rc-card全部其他节点与样式。旧骨架不再适用。
## UI Reference Replication Contract
来源为标注截图及最新范围决定；selector acceptance-check/acceptance-readiness预期不存在。原有动作→既有流程，不新增modal。分批：DOM删除及回归、1440/390视觉与computed style、文档同步。样式采样卡片height/padding/gap/font-size/overflow；非目标布局不变。
## 数据与观测
既有检查API、CLI验收、迭代检查保留；自动验收按钮现有禁用不变。product_data_collection_observability applicable，affected_layers web；无新增请求、DB、部署、对象存储或权限变化，无需OpenAPI/Orval。标准docs/standards/product-data-collection-observability.md。
## 验证与风险
摘要加载、刷新、迭代检查失败重试及原有交付确认回归；原本地页面验收列为空；本次用户授权隔离真实前后端样本已完成双视口视觉。不得自动把其他工作改为验收中造样本。回滚只恢复本次删除行，不触及其他改动。
