---
bug_id: BUG-0047-review-recovery-operation-record-missing
title: 评审恢复记录缺失导致成果未应用与卡片未流转根因分析
created_at: '2026-10-19 14:28:26'
updated_at: '2026-10-19 14:28:26'
root_cause_status: confirmed
---

# 评审恢复记录缺失导致成果未应用与卡片未流转根因分析

## 根因状态

status: confirmed

## 现象

产品 req-review 已生成评审成果，但轮次被收尾检查改判 failed / direct_command_recovery_blocked；无成功应用记录，REQ-0046 卡片仍为待评审。前期仅确认缺失记录的阻断机制，本次已取得实际部署模块及真实函数隔离复现，确认缺失产生原因。

## 证据链

| id | type | source | 摘要 | 支持的判断 |
|---|---|---|---|---|
| E1 | screenshot | 本会话用户附件与 Chrome /chat | 助手成功措辞与产品失败状态并存。 | 模型输出不能代表后端完成。 |
| E2 | data_sample | canonical SQLite 对目标轮次和候选的聚焦只读查询 | 轮次 failed / direct_command_recovery_blocked，候选 rejected / executor_unavailable，无成功应用记录。 | 状态应用未完成。 |
| E3 | data_sample | 对应私有命令记录目录 | baseline.json 存在且 action=req-review，operation.json 不存在。 | 准备与收尾记录不完整。 |
| E4 | code_path | app/governance/preparation.py::prepare_command_snapshot | 先写 baseline，再调用 prepare_direct_journal；评审继续创建候选。 | baseline 与 operation 不是同一成功条件。 |
| E5 | code_path | 已部署 backend/chat-worker 的 direct_command_journal.DIRECT_ACTIONS、prepare | 两服务名单均仅 sprint-propose、req-opsx、opsx-apply、opsx-archive；req-review 不在名单，prepare 直接返回。 | 评审合法执行但 operation 未创建。 |
| E6 | config_diff | 两服务实际模块 SHA-256 与工作区差异 | 部署模块均为 000b94105100d6e7302736084f2b39d885b6bb1a6a0fa437f14e6625d7db2f14；工作区已扩展 req-review 等动作，当前部署未包含该改动。 | 不能以工作区改动认定线上能力已生效。 |
| E7 | reproduction | 本轮 docker exec 隔离临时目录，调用部署模块 store.write / prepare / completion_block_reason | 虚构 req-review baseline；prepare 后 operation_exists=False；completion_block_reason=direct_command_recovery_blocked。退出自动清理，无业务库连接。 | 使用真实部署函数稳定复现原因与同错误，不依赖 AST 模拟。 |
| E8 | code_path | direct_command_journal.py::completion_block_reason、chat/execution.py | 目录存在即尝试 operation；缺失返回阻断码，收尾将 completed 改 failed。 | 创建名单与消费门禁契约不一致。 |
| E9 | reproduction | 前轮 Chrome /requirements 刷新完成 | REQ-0046 保持待评审并提供发起评审入口。 | UI 反映未完成事实，刷新不能解决。 |
| E10 | config_diff | 容器启动时间只读核对 | backend/worker 当日 08:59 启动，故障轮次 13:57；部署名单一致且缺少评审。 | 并非必须假设两服务名单不一致才能解释故障。 |

## 已确认根因

恢复记录的生产与消费采用不一致的动作契约：prepare_command_snapshot 为 req-review 写 baseline，但部署版 prepare 受旧 DIRECT_ACTIONS 名单限制而静默跳过 operation；completion_block_reason 不先判断此动作是否按该契约初始化，只要目录存在便强制读取 operation。结果是正常候选评审路径也被视为恢复记录损坏，模型完成后遭到收尾失败判定。

仓库工作区已扩展名单是相关改动，不等于修复已发布或全链路验证完成。需检查同模式的 bug-review、req/bug-complete 等动作；本次只证实 req-review 实例，不宣称其他动作都已发生事故。

## 已排除假设

| 假设 | 证据与结论 |
|---|---|
| 仅看板缓存未刷新 | 刷新、事实源与应用记录一致，排除。 |
| Agent 完全未生成成果 | 会话输出与 Diff 有迁移成果，排除“完全无产物”，不据此保证完整成果可恢复。 |
| 两服务必须运行不同名单才会失败 | 两服务名单及模块摘要相同，隔离复现仍失败，排除该必要条件。 |
| 必须发生文件删除或磁盘写失败 | 部署 prepare 按名单主动跳过即可复现，解释本次缺失无需该假设；未进行全盘删除审计。 |
| 当前工作区已有初始化调用，因此部署不会缺失 | 部署 prepare 的动作名单仍是旧值，调用存在但无写入，排除。 |

## 修复方向

统一支持动作的记录初始化、启动预检与收尾校验契约，显式区分未接入动作、旧版 baseline-only、损坏/丢失记录；不以无条件跳过检查或写空 operation 修复。核对工作区已有改动的覆盖与正式交付，不重复创建无关联修复。

保留准确阻断码与阶段；历史成果恢复必须校验归属、基线、当前版本、权限及既有应用记录。失败轮次事实不可伪改成功。多命令通用持久化阶段与幂等恢复能力留在 REQ-0047，展示契约留在 REQ-0046。

## 验证闭环

本次部署函数隔离复现完成，旧名单下 operation 缺失与阻断码均符合预测；前轮工作区函数探针在包含评审名单时不触发该阻断。两者是根因与修复方向证据，不代表正式修复验收。真实评审成功应用、历史成果恢复、并发/权限边界及部署版本一致性需按 acceptance.md 执行。

## 证据与隐私边界

本次未重启服务、修改镜像、改真实恢复文件或业务数据库；只读容器检查和隔离临时目录探针不等于部署。未保存凭证、原始日志、会话标识或本机路径。剩余验证属于修复验收，不再阻塞根因确认。
