---
bug_id: BUG-0064-chat-unknown-recovery-container-churn
title: Chat 未知轮次无界恢复缺陷修复评审
review_status: approved
created_at: '2026-10-26 13:35:26'
updated_at: '2026-10-26 13:35:26'
reviewer: 用户明确批准，Agent完成门禁核对
decision: approve
---

# Chat 未知轮次无界恢复缺陷修复评审

## 评审结论

批准修复，严重等级保留high。用户明确执行bug-review --approve；本结论确认修复范围及后续规划准入，不表示修复完成、验收通过或立即部署。

## 评审清单

- [x] 根因充分：8项脱敏证据通过根因门禁，确认unknown无界恢复导致执行容器重复创建。
- [x] 严重等级合理：持续后台资源消耗与恢复不收敛，有调度干扰风险；没有全站不可用证据，不提升到critical/blocker。
- [x] 回归明确：AC-01至AC-08覆盖有界调度、瞬态恢复、重启与持久化、多轮次公平性、预检缓存安全、保护语义、观测和真实Docker收尾。
- [x] 无需hotfix路径：走正常Sprint与OpenSpec流程；本命令不停止worker或修改真实历史轮次。

## 批准范围

先实现持久化退避、重试预算、暂停和并发幂等，再降低无变化检查与重复预检成本，补充恢复观测。保留原业务unknown、写入/并发/账务保护；不得重放业务命令或凭超时伪造终态。预检缓存需绑定镜像、策略、工作区身份与有效期，失效后重新验证。

## 设计阶段需收敛

明确有限默认重试次数、间隔上限、总时间预算、公平调度预算、暂停恢复触发语义、双库迁移和预检缓存失效条件。API/UI仅在必要恢复状态和受控操作范围内设计，并同步文档与客户端；不得扩大为新的通用任务平台。原始执行进入unknown的具体历史原因仍未知，单次RPC错误未截获；不影响本无界调度缺陷的修复批准，但不得冒充已诊断该历史异常。

product_data_collection_observability: applicable；affected_layers: task_traces、task_trace_spans；validation: 文档与根因门禁通过，产品修复验收not_started。后台无HTTP来源时request_logs为N/A，usage_events为N/A；新增人工恢复API时补权限与请求日志验证。

## 证据与交付边界

依据[root-cause.md](root-cause.md)、[bug.md](bug.md)、[acceptance.md](acceptance.md)及[workaround.md](workaround.md)。本次不创建Change、不纳入Sprint、不改业务代码或运行配置；评审通过后先完成Sprint范围与容量门禁，再转OpenSpec。

## 下一步

`/sprint-propose --bug BUG-0064-chat-unknown-recovery-container-churn`
