---
title: 归档包装证明修复交付验证
created_at: 2026-10-19 23:36:00
updated_at: 2026-10-19 23:36:00
---

# 归档包装证明修复交付验证

## 修改与影响

新增 `src/backend/app/governance/archive_proof.py`，在 `execution_context.py` 结束归档重核验分支接入。检查原操作身份、项目绑定、不可变私有基线、归档唯一性、核心文档、规格合并和只读 Workflow Sync check；最终稳定快照与门禁版本共同防止晚到确认。失败只保留有界原因，不重放归档、不把原 false 步骤改为 true。

影响 backend、chat-worker、governance-controller 的治理确认路径。部署、API原因说明与经验文档已同步；无 API schema、DB迁移、前端交互或客户端生成变化。没有新增权限或网络入口。

## 合成回归

聚焦五个测试文件：archive_proof、governance_execution_guard、ac011_direct_command_journal、ac012_archive_reentry、ac011_source_fault_matrix。最终包含93项测试及6子测试，包括数据库门禁接入与只读时间戳兼容测试；结果以逐项验收引擎清单为准。AC-002/003/005/006 共用一次安全命令执行，3项去重。测试覆盖不等同于真实产品观察。

## 真实观察

BUG-0048 原轮次 completed，原16条观测步骤保留，原同步成功步骤数仍0；新增服务端 archive_source_revalidation 证明绑定原操作。当前门禁已收敛 done，浏览器原会话完全只读，看板已完成；未启动新模型或重放归档。证据：`evidence/acceptance/bug0048-recovery.json`、`bug0048-restored-1440.jpg`、`bug0048-chat-readonly-1440.jpg`。

BUG-0050 为明确授权创建并归档的独立 low 级正式样本，依次完成评审、Sprint、Change、apply和准备验收。通过真实产品Chat发起首次归档，不能用BUG-0048恢复替代。首次轮次completed，但父任务进度同步与归档共享注册表写入竞争，导致archive_issue_not_promoted拒绝。只读check定位注册表及Sprint漂移后，串行重建两处派生状态，重启三个服务后原轮次证明成立、门禁done；不将其当作无干扰首次成功。用户补充授权BUG-0051独立串行首次归档，执行期间暂停其他治理写入。

## 部署与环境

三个本地服务健康，实际代码 SHA-256 与源码一致，见 `evidence/acceptance/deployment.json`。看板读取曾超时，后续请求加载成功；该现象不当作归档证明通过条件，也不宣称解决全局性能问题。

## 保守边界

失败、停止、未知轮次不自动采用归档重核验；RENAMED delta 或目标能力后续变更无法证明时继续待核对。仅已完成归档动作进入本次分支，直接同步路径不变。

product_data_collection_observability: applicable；affected_layers: Agent Workflow、私有操作证明、执行门禁、状态投影；validation: 身份/摘要/终态/失败原因测试及脱敏产品证据。未保存原始消息、私有基线、真实凭证或数据库。

## 最终产品结果

BUG-0051无干扰串行首次归档已完成，轮次、包装命令、服务端证明、正式文件和看板/会话权限一致。BUG-0050保留并发拒绝及重启恢复证据，不作为首次成功替代。AC逐项证据由acceptance-plan.json绑定，最终清单见evidence/acceptance。

## 串行样本发现与修复

BUG-0051首次归档后，严格检查曾因目标 Sprint 归档展示时间与 accepted_at 更新顺序产生的时间戳差异拒绝。新增 archive_workflow_check.py，仅在只读检查中忽略同一已归档 Change 的展示时间差异，其他内容差异仍阻断；强制 write=False，并恢复检查钩子。子进程明确使用已部署 backend 模块路径。修复核验器并重启后，原轮次自动收敛；未修改该样本治理源文件，也未重放归档或模型。
