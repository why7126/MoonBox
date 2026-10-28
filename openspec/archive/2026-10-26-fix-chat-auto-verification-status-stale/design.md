---
title: Chat 自动核验状态持续更新修复设计
created_at: '2026-10-26 18:50:07'
updated_at: '2026-10-26 18:50:07'
---

# Chat 自动核验状态持续更新修复设计

## 背景与现状
子组件首次GET后不再跟进，父组件执行终态停轮询。当前响应仅有 state/reason_code/can_verify，不能由 needs_review 单独判断自动队列是否仍运行。

## 修复方案
1. completion-verification GET/POST 响应新增可选 auto_verification 对象：state 为 pending/checking/confirmed/blocked/unavailable，reason_code 为受限原因或null。只投影当前 actor、scope、object、turn及guard_version匹配的既有handoff；无匹配为unavailable，不创建作业或修改保护。保留原state/version与现有客户端兼容。
2. 权威成果状态为 validated/recovered_valid 时展示已核验并停止自动跟进；队列pending/checking显示“正在自动核验”，blocked展示原因和已有合法手动入口；confirmed但保护未确认不伪造成功，继续有限查询并暴露不一致。旧服务未提供字段时显示中性“核验状态更新中”，不能宣称队列运行。
3. 仅当前会话最新治理轮次自动跟进；历史已成功或blocked不轮询，历史未决轮次只在用户展开或显式刷新时读取。首次读取若队列尚未登记，给最新轮次短期查询窗口，不把未登记永久视为失败。
4. 单个轮次/URL同一时刻只允许一个GET；使用完成后setTimeout，间隔2、4、8、10秒，之后10秒，最多18次且最多180秒，含失败请求。成功/终态/401/403/404/卸载/切换即停止；页面隐藏暂停且不重置总时间预算，网络或5xx按上述退避。超预算显示“自动跟进已暂停，可刷新状态”，不标为业务失败。手动刷新开启一次受控读取，不自动重放命令。
5. 每次轮次/URL切换增加generation并取消AbortController；GET和POST都检查generation，丢弃旧响应、旧finally和过时版本。手动核验与GET互斥，使用最新expected_version；POST结束只接受本轮响应，必要时重新读取，仍不调用模型。
6. onState及父级状态标签使用同一事实映射；完成业务状态不能由前端completed推断。保持现有样式和展开行为，无新增modal/布局复刻。

## 取舍与风险
采用有界GET而非新增长连接，复用现有权限与请求审计；单靠needs_review轮询全部历史会放大BUG-0058，因此引入最新轮次准入、硬预算和后端队列事实。可选字段对旧后端降级；不把网络错误当作核验失败。仅UI刷新不能解除后端保护。

## 测试策略
真实组件fake timers覆盖首次待核验后成功、延迟登记、blocked、隐藏、预算、请求去重、切换及GET/POST竞态。API集成验证队列归属和跨版本隔离。真实浏览器采集执行终态、后台确认和页面更新的脱敏时间线，且证明无点击核验/无模型重跑。

## 回滚方案
响应新增字段可选，先部署API再部署Web；回退Web或API不会改作业和保护状态。旧Web忽略新字段，新Web缺字段走有限兼容查询。回退后可能恢复状态滞留，不清理业务记录、不自动POST。

## 数据采集与链路观测
product_data_collection_observability:
- status: applicable
- affected_layers: Web、API、DB、request_logs、task_traces、task_trace_spans
- reason: 结果持久化或自动核验读取行为变化，沿用可信request_id与现有请求封装。
- validation: 计划核对请求计数、脱敏状态/来源摘要、权限、直接API无伪造行为、观测失败降级；尚未执行修复验收。
自动GET不伪造用户点击，不把正文、令牌、本机路径写入日志；后台无HTTP不伪造request_id。沿用既有保留清理策略；未新增usage_events事件。对象存储、移动端/管理端、密钥和环境变量N/A。API字段变化同步OpenAPI/Orval；持久化变化同步DB文档及双库验证。

## 实施细化
自动状态由授权operation_context之后读取同版本handoff；无队列或旧接口时使用中性更新文案。180秒硬截止可取消挂起请求；请求本身的AbortController与组件generation同时防止迟到响应覆盖。历史折叠轮次不发核验请求，展开可单次读取。
