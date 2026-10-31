---
title: Chat 原轮次问答修复验证记录
created_at: "2026-10-31 12:07:00"
updated_at: "2026-10-31 12:07:00"
---

# Chat 原轮次问答修复验证记录

## 交付结果

实现原轮次结构化问题、专用回答API、持久状态与安全回传；维持普通新命令互斥。新增客户端能力声明默认关闭旧客户端交互，实际Web显式启用。问题/答案、取消、过期、进程失联及撤权分别处理；不确定投递不自动重放。已同步API、DB、部署、生成客户端及模块文档。本轮没有部署生产或归档。

## 验证记录

- 根因门禁：8条证据通过，保留历史单次是否发出原生请求未知的边界。
- 相关后端集中回归：82 passed、6 skipped（原有显式环境测试）；随后新增边界按影响面增量验证。问答专项最终22例覆盖并发、鉴权、终止、队列双阶段、丢失句柄、写后异常、历史删除和客户端能力。
- MySQL 8.2.0独立tmpfs容器：结果及输入指纹见[evidence/acceptance/manual/mysql.json](evidence/acceptance/manual/mysql.json)。SQLite和MySQL不互相替代。
- TypeScript构建、2项卡片测试、Vite生产构建通过；产物分块大于500kB提示不影响本次构建，未扩大为全站拆包。
- 用户已确认Skeleton。1440px/390px共16项状态截图、computed style、键盘路径通过：无水平溢出，卡片边框/间距/主题符合现有Chat token；错误保留输入，刷新恢复已收到状态。样本控件是测试壳，不属于生产界面。
- 最终真实模型轮次使用固定0.153.4镜像、真实worker、API、实际ConversationMessages和QuestionPanel：浏览器选择BETA，原轮次消费答案、写出choice.txt=BETA并正常completed，error_code为空。见[同轮结果](evidence/acceptance/browser/live-result.json)、[卡片](evidence/acceptance/browser/live-completed.png)、[结果区域](evidence/acceptance/browser/live-consumed.png)。全部业务账号、空间、仓库和文件均为一次性合成数据；非生产部署验证。

## 逐项验收映射

| AC | 证据与结论 |
|---|---|
| AC-001 | 真实模型结构化问题与卡片、选项/补充输入；通过 |
| AC-002 | 专用API与唯一turn断言、原enqueue互斥回归、真实同轮消费；通过 |
| AC-003 | 实际ByteQueue的RPC等待和event两阶段测试；通过 |
| AC-004 | 非法选项/长度、重复键、并发不同答案仅一方成功；通过 |
| AC-005 | 真实浏览器刷新、服务端问题身份复用、迟到响应隔离；通过 |
| AC-006 | 过期、停止/unknown/终态迟到答案拒绝；合成状态和浏览器终态卡片通过 |
| AC-007 | bridge断开、句柄/投递不确定、终态通知与worker围栏；合成故障测试通过，不宣称生产worker重启已验证 |
| AC-008 | 跨用户、错误会话问题ID、空间停用、账号撤权及执行权限降级；通过 |
| AC-009 | 旧客户端能力默认关闭、未知交互请求拒绝、固定版本功能开关及降级指引；通过 |
| AC-010 | 8状态×2视口截图与computed style、键盘radio/textarea/submit；通过 |
| AC-011 | 独立授权真实模型同轮提问→浏览器答案→消费→BETA效果与completed；通过 |
| AC-012 | 直接API/页面动作区分、可信request关联、span无答案原文、业务历史删除；通过 |

## 自检修复与证据边界

首次RPC测试发现待答期间缓存ACK未被rpc重新消费，已修正；首次真实模型验证发现ByteQueue不支持get_nowait，改为产品队列get(timeout=0)并让回归使用同类型。无支持能力的测试Peer曾因无条件提示追加而失败，现按适配器和客户端能力接入，原集中回归已通过。所有修复在当前apply内完成，未要求用户发送“继续”。这些失败不能改写成首轮即通过。

视觉error/submitting通过受控网络故障/延迟采样；delivered/expired/cancelled/unrecoverable矩阵使用隔离持久状态，真实模型效果另列，合成状态不冒充模型运行。未观察平台强制终止；无未解决业务阻塞。

product_data_collection_observability: applicable；affected_layers: Web/API/问答表/执行器/usage_events/request_logs/Task Trace；validation: 关联身份、状态、授权、幂等、删除与日志脱敏验证通过。对象存储、管理端、小程序及移动端N/A：未新增附件或页面。

## 回滚与发布边界

先关闭新问答准入，核实/终止待答原轮次，保留数据库新增结构；不对unknown重新执行写命令。真实服务升级及发布不在本命令内，执行器能力与新Web须随部署一起启用。
