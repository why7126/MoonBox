---
bug_id: BUG-0058-chat-history-status-replay-request-amplification
title: 聊天历史状态重建与重复读取修复评审
review_result: approved
reviewed_at: '2026-10-21 09:15:16'
created_at: '2026-10-21 09:15:16'
updated_at: '2026-10-21 09:15:16'
review_basis: 用户明确执行 bug-review --approve，结合缺陷包与根因证据门禁
---

# 聊天历史状态重建与重复读取修复评审

## 评审结论

批准修复。维持 high 严重等级，采用常规 fix，不走 hotfix。批准范围为历史状态重建、跨组件重复读取、隐藏详情取数和相关轮询生命周期；不扩大为整体后端性能重构，不认定所有等待具有共同根因。

本结论表示允许进入 Sprint 规划，不表示修复完成或验收通过。尚无 Sprint、OpenSpec Change；先纳入 Sprint 并同步为 in_sprint，再转换修复 Change。

## 评审清单

| 项目 | 结论 | 依据 |
|---|---|---|
| 可复现或根因充分 | 通过 | 同会话完成态历史刷新后重读状态，同轮事件首页三次成功响应；三个独立读取方与隐藏挂载代码对应。根因校验 confirmed，9条证据。 |
| 严重等级合理 | 通过，high | 核心研发入口加载等待与重复请求；未见数据丢失、安全事故或全站不可用。 |
| 回归验收明确 | 通过 | acceptance.md 的 AC-001—AC-010 覆盖状态展示、请求共享、隐藏详情、分页、活跃状态、慢响应、切换、权限、性能对照和页脚摘要。全部待执行。 |
| 是否需要 hotfix | 否 | 无 P0 紧急事故依据，常规评审后排期。 |
| 规避方案 | 无已验证的完整方案 | 仅减少非必要刷新与切换；收起详情不作为修复，不重复发送历史命令。 |

## 证据边界与实施约束

证据来源见 [根因分析](root-cause.md) 和 [缺陷说明](bug.md)。浏览器事实为本会话既有真实观测，本次评审未重新计时；无 HAR/截图附件，源码与部署包未做严格版本映射。

confirmed 仅覆盖已复现的读取机制。整体延迟贡献、Stalled 具体原因、恢复慢响应实际重叠规模仍待实施阶段受控量化；这些不阻断已确认机制的修复评审，也不能作为已量化收益。修复前保留基准，修复后按采样契约对照。

共享缓存和请求不能跨权限边界；未知状态不伪装终态，不绕过成果核验和写入保护。保留活跃任务更新、故障恢复与权限失效清理。API摘要是否新增由 Change 设计决定；若涉及 API、数据库、UI、安全或客户端生成，按实际边界同步契约、文档与测试。

## 观测声明与验证

product_data_collection_observability: applicable；affected_layers: Web、API、request_logs、Task Trace。validation: 根因证据门禁、中文标题和状态一致性校验；验收未执行。本次只记录批准，不改变采集字段或运行行为；数据库、部署、对象存储、安全及客户端生成变更为 N/A。

## 后续入口

`/sprint-propose --bug BUG-0058-chat-history-status-replay-request-amplification`
