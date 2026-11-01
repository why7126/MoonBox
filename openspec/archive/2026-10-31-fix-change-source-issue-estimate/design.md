---
title: Change 来源人力估算修复设计
created_at: '2026-10-31 23:29:25'
updated_at: '2026-10-31 23:29:25'
---

# Change 来源人力估算修复设计

## 根因
真实scope行id属于BUG，虽然change字段明确，estimate_metadata的Change分支仍排除。为避免总量复制的保护过宽，缺少唯一归属判定。
## 修复方案
1. 优先目标Change自身合法记录；自身非法或冲突不以来源掩盖。
2. 无自身记录时，以授权项目完整关系索引校验来源和交付绑定；不能只凭当前可见卡片数量判断唯一。
3. 来源唯一、全量关系唯一且scope明确绑定目标，才读取来源数值；多个来源或多个未分配交付保持缺失/冲突，不自动求和或均分。
4. 保留有限非负数规则，0有效；重复一致值去重，冲突不猜测。
5. 来源不可见不泄漏名称或数值；卡片区分来源估算与实际耗时。容量仍按原scope计算，读取不写任何源文档。
## API 与观测
product_data_collection_observability: applicable；affected_layers: api、web。标准docs/standards/product-data-collection-observability.md。复用请求日志与关联，不新增Task Trace任务；无新写操作或埋点要求。DB/部署/对象存储/保留周期N/A。validation：来源权限、摘要/完整响应、日志脱敏及无写入验证。来源展示若需新字段，同步OpenAPI/Orval/docs/03-api-index.md和契约测试，否则声明无需生成。
## 测试策略
BUG AC-001至008逐项映射：真实3人天样本、独立优先、自身非法、零值、重复、冲突、多来源、一对多、归档、权限过滤及容量不变。后端函数/API回归与前端真实刷新分别取证，不能用合成测试冒充产品观察。
## 风险与回滚方案
防止隐藏来源造成假一对一、防止历史关系丢失及重复计量；信息不足时继续待核实。回退本次代码差异，不改历史Sprint事实。

## 实施约定与门禁

新增可空响应字段 estimate_source_issue_id，来源提示复用 CardInfoTags 的 title；标签正文、样式、动作及弹窗不变。选择器为 person-days-tag，期望显示 M·3人天，提示说明引用 BUG-0070 且非实际耗时；1440/390 复核不溢出和字号。此为数据修复，不是附件样式复刻，没有 prototype 或新页面骨架任务。管理端列表/表单/弹窗/上传四类横切标签不适用；承接 partial-delivery-sprint-handoff，不复制总量到兄弟交付。

根因门禁通过5项；Sprint包含BUG与Change，来源为in_sprint。opsx.apply dry-run在启动前因缺启动、启动后因任务未全勾拒绝，这是完成门禁，并非Sprint未纳入；opsx.start及聚焦scope校验已成功解析sprint-018。
