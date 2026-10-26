---
title: 已验收规格演进准入修复
created_at: 2026-10-26 10:37:24
updated_at: 2026-10-26 10:37:24
---

# 已验收规格演进准入修复

## 目标与根因
support-reviewed-spec-evolution修复REQ-0053被追加式文本门禁拒绝的问题，落实已生效REQ-0050 v6。用户已授权独立治理Change与保留门禁；不新增签名、批准人或文本例外。

## 修改与影响
修改src/backend/app/governance/archive_admission.py及archive_diagnostics.py，增加test_reviewed_spec_evolution.py；同步rules/security.md与docs/standards/opsx-acceptance.md、Change及Sprint。允许当前证据覆盖的同名MODIFIED，保留删除拒绝、完整历史、权限、证据及并发门禁。
无API结构、DB、Web组件、客户端、管理端、Orval或Docker Compose变化；仅既有诊断文案调整。product_data_collection_observability=applicable，affected_layers=[api,agent_workflow]；不增加采集字段，复用既有请求与业务鉴权链。

## 验证
19项新增回归通过；四项联合AC全部passed，证据为Change evidence/acceptance/20261026103749885583-0e8221e0/summary.md。相关回归、目录/预算/语言/标题/Sprint/观测和OpenSpec strict均通过；仅既有legacy SQLite目录警告。REQ-0053当前27项验收有效，归档准入已返回ready；仍待本Change收尾后的最终复查。未执行正式归档。

## 过程问题与后续
Sprint范围脚本对无缩进YAML序列插入带缩进条目，导致一次解析失败；已仅纠正本次新增条目的缩进并重跑同步成功。脚本行为修复不混入本Change。建议后续聚焦修复其两种合法YAML缩进输入的回归；未自动创建Issue。
