---
title: 临时 Docker 验证资源闭环治理记录
created_at: 2026-10-26 12:12:25
updated_at: 2026-10-26 12:12:25
---

# 临时 Docker 验证资源闭环治理记录

## 迭代目标
解决任务退出后临时验证容器仍保留的问题，建立创建前登记、结束清理和到期回收门禁。

## 变更摘要与影响范围
新增temporary_docker.py的register/check/cleanup/reap。精确三标签和daemon匹配、默认预览、禁止卷删除、外部网络保护、到期运行拒绝和清理后重扫。没有常驻定时器；后续任务入口执行到期扫描，任务结束主动收尾。规则无法拦截绕开契约的任意shell动作，历史未登记资源不接管。

## 更新文件
脚本：scripts/temporary_docker.py、scripts/test_temporary_docker.py、scripts/smoke_temporary_docker.py、scripts/validate-agent-context-budget.py、scripts/README.md。
规则与文档：AGENTS.md、rules/environment.md、rules/agent-context-budget.md、rules/directory-structure.md、docs/README.md、docs/08-command-execution-order.md、docs/standards/opsx-acceptance.md、docs/standards/temporary-docker-lifecycle.md。
技能：opsx-apply、openspec-apply-change、opsx-modify、opsx-accept、spec-opt。
事实源：openspec/changes/add-temporary-docker-lifecycle/与iterations/change/sprint-014/。

## 验证结果
14项边界回归和真实Docker的2容器/1网络隔离样本通过、零残留。到期时钟模拟，不伪装真实长期运行。首次第二网络创建失败且已完成清理；缩小样本后通过。治理契约、标题、中文、CLI、Sprint scope与diff检查通过；目录校验保留既有legacy SQLite警告。最终逐项验收以Change内证据包与trace为准。

## 系统影响
API/DB/Web/客户端/管理端/Orval/正式Docker Compose均无变更；不修改Chat业务容器执行逻辑、不清理历史未登记环境。product_data_collection_observability: N/A；affected_layers: []；本地治理登记不改变产品观测链路；validation: 边界回归与Docker实测。

## 后续建议
观察后续任务资源收尾记录；如需无人值守按时回收，另行明确常驻调度环境。未自动创建后续Issue/Change，不以本次回归通过宣称长期节省已确认。
