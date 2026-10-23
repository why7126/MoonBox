---
bug_id: BUG-0044-requirement-stage-premature-transition-session-split
title: 需求中心阶段提前迁移与会话分裂根因分析
created_at: '2026-10-19 11:03:36'
updated_at: '2026-10-19 11:03:36'
---

# 需求中心阶段提前迁移与会话分裂根因分析

## 根因状态

status: confirmed

确认范围：BUG-0028 案例的提前放行及忙碌会话排除机制。其他命令共享该路径，但不宣称全部入口已真实复现；修复后验收尚未开始。

## 现象

前一轮尚未完成，治理文件已更新，需求中心开放后续动作。点击生成 Opsx 后创建新会话，后续命令在旧轮次完成前发起。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | data_sample | 本地 canonical SQLite：chat_conversations、chat_turns；同会话 explore 查询，bug-generate 再次只读核对 | 2026-10-19 北京时间：sprint-propose 10:23:29 开始、10:25:46 完成；新会话 10:25:40 创建，bug-opsx 10:25:45 开始 | 新建发生在前轮结束前 6 秒，后续轮次与前轮重叠 |
| E2 | screenshot | 用户本会话附件与 explore 的 Chrome /chat 历史观察 | 新会话包含 bug-opsx，历史中存在两个同主对象会话；Chat 刷新后显示新轮次 failed | 会话分裂是真实产品事实；失败不等于产物不存在 |
| E3 | code_path | src/backend/app/services/requirement_center.py：_issue_status、_map_stage | 根据 trace/registry、Change 和文档映射卡片阶段，不将当前 Chat 轮次终态作为统一完成门禁 | 文件先更新可使阶段提前变化 |
| E4 | code_path | src/backend/app/governance/preparation.py：_latest_object_conversation、prepare、prepare_object_session | 排除 active_turn_id 非空会话，无可复用候选即新建 | 活动会话被当作不可复用而非当前执行入口 |
| E5 | code_path | src/web/src/pages/catalog/RequirementCenterPage.tsx：openIssueActionDialog | 命令按钮请求对象会话准备，按返回 ID 跳转；未把忙碌原会话作为查看执行入口 | 前端没有弥补阶段状态与会话状态之间的缺口 |
| E6 | code_path | src/backend/app/chat/worker.py：终态处理；src/backend/tests/test_governance_candidates.py：test_prepare_skips_archived_and_active_object_conversations | 终态才清除活动轮次；现有测试明确期望跳过活动会话并新建 | 这是既有策略与完成门禁缺失的组合，而非单次偶发随机行为 |

运行数据仅保存业务命令及时间摘要，不保存真实个人标识、会话标识、凭证或原始日志。浏览器证据承接此前已完成的观察，本次未重复发起会写入治理事实的命令。

复核入口：在有权限的本地只读连接中，以完整 BUG-0028 业务标题限定 chat_conversations，关联 chat_turns，筛选 2026-10-19 的 sprint-propose 和 bug-opsx；比较创建与终态更新时间。将 UTC 转为 Asia/Shanghai，不导出 prompt 全文或用户字段。原数据若被清理，以这里的历史摘要为历史证据，不伪造当前复现。

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 仅 bug-opsx 强制创建新会话 | E4：与 sprint-propose 共用选择函数 |
| 前一轮完成后仍随机新建 | E1：新建早于旧轮次完成 |
| “部分输出”提示导致新建 | E4、E5：新建由对象会话准备控制，消息渲染不参与 |
| 关闭浏览器或结束整条会话后才能续用 | E4：判断活动轮次而非页面是否关闭 |

## 已确认根因

卡片的业务阶段投影、动作准入与 Chat 执行状态没有统一的完成契约。治理文件在命令执行中途就可更新，使卡片开放下一步；对象会话准备又将忙碌会话排除，并以新建代替等待或查看执行。两者组合造成同对象前后轮次重叠与上下文分裂。

不能仅删除 active_turn_id 过滤就直接允许发送，也不能把所有阶段迁移推迟到结束；前者仍可能并发执行，后者会破坏研发启动展示。

## 修复方向

- 明确执行型与完成型阶段事件：开始开发/返修及时显示研发中；完成型迁移等待当前轮次成功、业务校验及状态同步通过。
- 对象级治理执行互斥与前端状态协同，覆盖不同会话、双标签页和直接 API。互斥键至少包含项目与规范化对象身份，不泄漏其他用户会话内容。
- 默认沿用当前用户可访问的原会话；忙碌时提供查看执行和保留草稿，不静默新建；明确多会话、归档及删除的安全选择策略。
- 失败或未知状态下先核验已写成果和执行终态，再恢复阶段与按钮；幂等恢复不得重复执行或盲目回滚。
- 外部 Codex/CLI 以治理事实与校验收敛；未建立可观测关联时不得声称可以互斥任意外部进程。

## 验证闭环

现象由 E1/E2 支撑，E3—E6 解释完整触发机制。此前隔离测试后端 77 项通过，前端 132 项通过、1 项旧卡片宽度断言失败；这些验证描述现有行为，不等于修复验收。

修复后按 acceptance.md 逐项补充合成回归与真实产品证据，尤其慢收尾窗口、跨会话并发及异常恢复。本次根因门禁只检查证据结构，不替代产品验收。

## 数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: Web 行为、对象会话 API、请求日志、Task Trace、Chat 轮次及阶段投影。

validation: 后续验证同对象动作的请求/任务/轮次关联、拒绝原因、复用结果及阶段生效依据，支持无行为事件的直接 API；不采集原始 Prompt、凭证或真实用户标识。本次仅文档完善，schema、索引、保留周期、对象存储和客户端生成变更均 N/A，具体实现影响留给 Change 评估。
