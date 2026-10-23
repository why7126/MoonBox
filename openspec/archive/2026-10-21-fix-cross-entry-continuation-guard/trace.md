---
title: 跨入口续接证明修复追溯记录
created_at: '2026-10-21 16:11:48'
updated_at: 2026-10-21 17:21:47
change_id: fix-cross-entry-continuation-guard
bug_id: BUG-0061-cross-entry-continuation-guard-convergence
status: applied
iteration: sprint-012
execution:
  schema_version: 1
  started_at: 2026-10-21 16:17:49
  completed_at: 2026-10-21 17:21:47
  last_event: opsx.apply
---

# 跨入口续接证明修复追溯记录

## 来源与状态

BUG-0061-cross-entry-continuation-guard-convergence，sprint-012；已实施部署，最终逐 AC 验收收尾中。关联BUG-0060/0052已归档基线；BUG-0055为sprint-011现场，不迁移其实现范围。

## 证据与边界

根因10项证据confirmed，历史归因partial；19项累计差异不等于首次冲突。验收见acceptance.md映射及evidence/acceptance，执行时间由Workflow Sync维护。

## 观测

product_data_collection_observability: applicable；affected_layers: governance、API、Web、CLI、proof、recovery audit；validation: 规划阶段，后续按design.md与AC矩阵执行；不记录凭证或私有正文。

## 实施与验证记录

2026-10-21：实施对象范围后继核验、结构化同步结果和正式验收收据。旧 journal 步骤不修改，后继核验写独立 final_verification.successor；任务范围、有效验收、输入覆盖、权限/绑定和 guard 版本仍为硬门禁。原现场19项差异已读取，历史行级归因保持 partial。

已验证：后端聚焦186项通过，另1项因macOS临时目录符号链接拒绝；规范化TMPDIR后相关41项及6子测试通过。同步/工作流80项通过。前端141项通过（Node关闭实验webstorage以使用jsdom存储）。独立MySQL8.2矩阵120项及6子测试通过。以上为合成回归；真实模型与正式现场恢复尚未执行，不计为产品终态验收。

标准部署前检通过，构建部署进行中。用户授权REQ/BUG各一次隔离模型归档调用，当前使用0/2。正式BUG-0055保留旧保护，待部署后通过产品核验入口恢复。

增量验证：日志提交中断用例在 MySQL 8.2 上26项通过；增加当前阶段和累计摘要用例后SQLite29项通过。完整CLI归档对照已在附加临时副本中成功执行REQ/BUG各一次，包含迁移、Workflow Sync、Issue promote及终态验证，不是静态ready。隔离产品HTTP核验曾发现累计历史run摘要误阻断，已补归属校验并复验；未消耗模型次数。正式BUG-0055当前12/12证据仍ready。

## 最终部署与真实观察

三个运行服务的5份核心文件哈希与已测版本一致，Web标准构建已部署。最新MySQL8.2后继回归31项通过。两次授权模型调用均成功：实际发送HTTP200，轮次completed，保护validated/done，Issue和Change均已归档。旧受阻前置为合成夹具，后续CLI同步、HTTP核验、模型归档及业务回读为真实执行。

BUG-0055通过产品核验恢复，140条原步骤哈希一致，909条事件保留且最后更新时间仍为原执行终止时。产品首次核验出现网关504，后端已提交，刷新状态确认成功；未重放。随后标准finalize退出0，Issue/Change进入archive，产品看板已完成。

1440/390视口验证结果待核验、成果已核验及刷新持久化，截图与computed style位于implementation证据目录；真实API，无Mock。API字段与数据库结构未改变，无迁移或客户端重生成需求；已同步API语义、数据库兼容、部署及事故知识文档。

## 最终验收结论

2026-10-21：14/14通过，最终运行20261021172015757258-d2606c57；12项证据复用，2项增量执行。opsx.apply和opsx.accept均退出0，错误0；子文档根因status=confirmed提醒经核对保持根因语义。BUG-0061未正式归档。
