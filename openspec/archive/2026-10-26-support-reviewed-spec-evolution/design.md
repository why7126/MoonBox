---
title: 已验收业务规格演进准入设计
created_at: 2026-10-26 10:32:28
updated_at: 2026-10-26 10:32:28
---

# 已验收业务规格演进准入设计

## 证据与根因
archive_admission.protected_rule_integrity只允许append_only或supported精确旧例外，与REQ-0050 v6不增加独立证明的生效规格不一致。REQ-0053重复检查返回archive_requirement_conflict，三个同名MODIFIED条文均有完整前驱。旧归档元数据已另行核验纠正。

## 决策
保持conflicts对唯一已完成前驱及可解析新旧条文的核验。追加场景沿用兼容行为；非追加MODIFIED必须有有效结构化验收，复用readiness及source_root，不接受只有Markdown签认、旧确认或精确文本例外。REMOVED及不支持的语法继续拒绝。不新增人工批准字段或签名体系。
受影响delta文件必须进入至少一项验收的完整输入范围，避免验收与替代内容脱钩；不能用仅选标题的input_sections替代完整规格绑定。正常操作层继续检查来源/评审/Sprint、项目权限、撤权、锁及写前输入版本，本函数返回ready不授权写入。
同名Requirement与conflicts中的protected_changes明确替代关系，证据和差异通过已有入口呈现。不篡改历史、不写openspec/specs。

## 验证
真实临时文件树与验收清单验证MODIFIED成功及缺证、过期、失败、篡改、覆盖缺失、删除、重复历史、未完成历史拒绝；产品只读详情与CLI共用门禁。既有权限、撤权、跨项目及围栏测试回归。REQ-0053重新检查与临时合并预演，绝不真实归档。

## 风险与回退
结构化证据本身并非语义证明，继续依赖已评审需求及受影响测试，不根据文本相似自动判定安全。回退仅撤回本Change准入差异，不撤回其他在途实现。无数据迁移或服务部署。

## 横切与观测
product_data_collection_observability: applicable
affected_layers: [api, agent_workflow]
reason: 共享只读准入影响既有API结论；不改变行为事件、请求日志、Task Trace、DB或权限模型。
validation: 回归共享入口、直接读取、权限拒绝及证据失败；无新采集字段、不写原文或凭证，既有遥测不作授权。
UI/原型/知识库组件族门禁为N/A：没有页面及交互组件变更。
