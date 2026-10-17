---
change_id: add-automated-opsx-acceptance
title: 自动验收与证据归档追溯记录
status: applied
created_at: 2026-10-12 14:59:30
updated_at: 2026-10-12 15:27:24
sprint: sprint-008
requirement: null
bug: null
product_data_collection_observability:
  status: applicable
  affected_layers:
    - agent_workflow
    - chat_events
  reason: 验收需要只读关联 Chat 产品轮次、目标命令事件与完成终态；不新增采集表或产品 API。usage_events、request_logs、task_traces 和 task_trace_spans 的新增或修改均 N/A。
  validation: 聚焦测试验证同轮命令完成、停止轮次不通过、事件摘要不含原始输出；MySQL 产品路径 N/A，待等价授权只读适配器。
execution:
  schema_version: 1
  started_at: 2026-10-12 15:06:58
  completed_at: 2026-10-12 15:14:48
  last_event: opsx.apply
---

# 自动验收与证据归档追溯记录

## 来源与范围

来源于 BUG-0026 长耗时验收的流程复盘，独立纯治理 Change，纳入 `sprint-008`。只变更治理技能、脚本、规则和文档；不修改产品业务 `src/`。

## 验证记录

按 `acceptance-plan.json` 自动执行，逐 AC 结论与清单位于 `evidence/acceptance/`。合成回归只证明验收内核判定，不冒充真实产品归档轮次。本 Change 没有要求生产或产品归档操作，产品 Chat 只读取证适配器由合成数据库覆盖。

- 逐 AC 计划包含内核回归、技能契约和 OpenSpec strict 三项；预检使用项目已有 Python 环境。脚本按输入指纹重验，Change `evidence/acceptance/` 保留脱敏 manifest 与摘要。
- 聚焦单测 27 passed，覆盖缺失完成事件、证据文件被改动和归档移动后仍可定位；上下文预算、中文优先、OpenSpec strict、目录结构、Sprint scope、产品数据观测和交付证据门禁均通过。`bash -n scripts/archive-change.sh` 与 Python 编译通过。
- 最新自动验收 run `20261012152723955014-d724518b`：3/3 AC passed，其中 2 项复用未过期证据，`--readiness` 为 ready；证据见 `evidence/acceptance/20261012152723955014-d724518b/summary.md`。Workflow Sync `opsx.apply` 与 `opsx.accept` 0 errors。AI Usage hook 返回 warning/unavailable，无可归因 token 事件，未阻断交付。
- 产品数据源只读实测：既有 BUG-0042 完整轮次可读为 `completed`，同轮目标归档命令事件序号 47、完成且退出码 0；未读取或写入聊天正文。本次仅验证采集适配器，历史轮次不作为本 Change 的产品行为 AC。
- API、DB schema、Web、客户端生成、部署配置、安全策略和对象存储协议 N/A：本 Change 仅治理脚本及技能，产品 SQLite 查询只读，原始会话与事件 payload 不入仓。完整产品轮次自动触发仍由授权对象 Chat Agent 执行，脚本核对终态与同轮命令事件。
