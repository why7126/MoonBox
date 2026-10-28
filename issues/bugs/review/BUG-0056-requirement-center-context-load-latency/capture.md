---
bug_id: BUG-0056-requirement-center-context-load-latency
title: 需求中心首屏聚合请求耗时约二十七秒缺陷记录
status: captured
created_at: '2026-10-21 08:50:06'
updated_at: 2026-10-27 10:09:18
severity: high
environment: local
owner: 产品团队
source: 用户授权与同会话 explore 证据
related_requirement: null
related_bug: BUG-0016-capture
root_cause_status: probable
lifecycle_stage: review
---

# 需求中心首屏聚合请求耗时约二十七秒缺陷记录

用户第 1 项：从进入需求中心到卡片数据出现等待过长。2026-10-21 同会话在本地 Web、Chrome 已登录会话的 /requirements 刷新复现；页面约 20 个治理对象。环境具体部署版本与负载尚未锁定。

## 已确认的证据

| 编号 | 类型 | 来源 | 事实及确认边界 |
|---|---|---|---|
| E1 | network_request | 同会话 Chrome 原生 DevTools Network / Timing | GET /api/v1/requirement-center/projects 返回 200，约 813 ms；随后 context 返回 200，总耗时约 26.86 s，Waiting 26.77 s，下载 74.72 ms；响应约 1,793 kB。确认本次等待主要发生在响应首字节前，不是下载传输。 |
| E2 | network_request | 同次 context 的 Server-Timing | snapshot_and_fences 7.48 s、materialize 0.58 ms、object_authorization 0 μs、parse 8.02 s、cleanup 9.84 ms、total 24.98 s。未覆盖的内部阶段约 9.47 s，不能归因为某一函数。 |
| E3 | code_path | src/web/src/pages/catalog/RequirementCenterPage.tsx，loadContext 与轮询 effect | 项目目录与 context 串行；可见页面每轮完成后约 3 s 再轮询，完整响应后更新卡片。 |
| E4 | code_path | src/backend/app/governance/reader.py，ProjectReader._call；snapshot.py，stable/read_once | context 获取一致性快照后解析并逐卡投影执行状态；stable 对 issues、iterations、openspec、docs、rules 连续读取两遍。缓存物化不免除快照扫描。 |

## 根因判断

已确认当前样本的服务端聚合瓶颈及串行加载机制。完整根因保持 probable：全量快照、解析及后处理为主要调查方向；尚无隔离对照证明各函数成本与本次回归的直接因果。27 秒是单次样本，不是 P95，也不是纯服务端函数耗时。

## 判重与拆分

BUG-0016-capture 已 done/archive，曾修复刷新与抽屉加载问题。用户明确选择新建关联 BUG，独立跟踪当前首屏复发；旧 BUG 的交付与归档事实不变。本条不扩展为文档抽屉故障。

## 复现与期望

1. 在相同项目登录后打开 /requirements，Network 保留记录，刷新一次。
2. 记录项目目录、context 请求和首张卡片出现时刻。
3. 期望首屏及时可用，未变更时不重复昂贵聚合；实际本次 context 等待约 27 秒。

## 待补证与验收建议

补齐部署提交/镜像、治理文件数与体积、缓存冷暖状态、同期负载；在相同数据与权限下采集多次冷暖加载，分别报告样本数、中位数、P95及首卡可见时间。追加后处理、权限查询、执行状态核对的细分计时，覆盖现有约 9.47 s 空白，再比较优化前后。验收同时覆盖权限隔离、写入版本变化和错误恢复，不以减少安全校验换性能。

## 证据归属与边界

证据复用同会话 2026-10-21 浏览器工具结果与源码只读检查；本次 capture 未重新计时。运行态样本未保存 HAR/截图文件，以上为脱敏观察摘要，不伪称已有附件。代码行号可能变化，按文件与函数定位。浏览器 DOM 只读接口不支持 performance，已改用 Chrome 原生 DevTools 取证；未因单工具失败判定服务不可用。

后续补证优先自主浏览器与服务端可用观测；涉及创建会话或执行命令的采样使用明确测试对象或用户自然操作。返回格式：环境/版本、动作、脱敏路径、状态码、总耗时、Waiting、阶段计时、样本规模；禁止凭证、原始消息/文档、个人标识及本机路径。

## 严重等级与观测声明

初判 high：核心研发入口出现明显长等待，影响日常连续操作；无数据丢失、安全事故或全站不可用证据，不提升为 critical/blocker。

product_data_collection_observability:
- status: applicable
- affected_layers: Web、API、request_logs、Task Trace
- reason: 性能定位涉及请求等待及治理步骤计时；本次只记录 BUG，不改变埋点或日志契约。DB 索引/结构、对象存储和部署变更尚无证据支持，暂不提出修改。
- validation: 同会话浏览器观察与聚焦代码路径；未执行修复或性能回归，剩余计时见待补证。

