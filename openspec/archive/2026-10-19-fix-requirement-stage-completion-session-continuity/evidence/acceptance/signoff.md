---
title: 需求中心执行门禁逐项证据与验收签认
created_at: "2026-10-19 13:37:00"
updated_at: "2026-10-19 13:37:00"
---

# 需求中心执行门禁逐项证据与验收签认

## 环境与边界

2026-10-19，当前工作区实现；隔离 API 和前端构建、独立 SQLite、独立 MySQL 8.2 容器。真实模型仅访问一次性项目副本，正式业务对象未重跑。原产品执行按用户授权停止后接管；用户已确认沿用卡片布局、增加执行状态和查看原执行。截图使用 Chrome 后备入口；1440px 来自真实产品 iframe 内视口（1440×900），宿主完整截图宽1470px，未裁切冒充视口。真实轮次页面宿主1470px，作为行为补充。

## 验收矩阵

| AC | 观察与断言 | 证据性质及入口 |
|---|---|---|
| AC-001 | 文档draft但轮次running，卡片仍capture、下一动作禁用；REQ生成completed、同步命令exit0且成果应用后进入planning | 两次BUG真实45秒慢收尾：live-slow-tail.json、live-retry-slow-tail.json及截图；真实REQ成功：live-generation-result.json、live-generation-validated.png；核心组合回归 |
| AC-002 | 忙碌查看和后续完善均回原cid，草稿跨页面保存；重试前草稿不被建议命令覆盖 | live-original-conversation-header.png、live-retained-draft.png；REQ连续轮次同cid；前端持久草稿与候选选择测试 |
| AC-003 | 活动对象10个真实准备请求均不新建/不发送；跨会话直接发送409/2607；SQLite/MySQL并发只接受一个 | live-entry-requests.json、observability-sample.json；连接/进程/事务测试 |
| AC-004 | 不同项目隔离；他人执行只给忙碌摘要；归档/删除不可复用；最新可用会话稳定选择 | 守卫、候选、权限回归；不是每种权限独立模型轮次 |
| AC-005 | 外部opsx.start返回0，保持首次started_at且无需模型轮次，页面研发中且进度可读；apply/modify不覆盖首次完成事实 | external-sync.json、external-start-development.png、external-start-read-progress.png；REQ/BUG生命周期回归 |
| AC-006 | failed/stopped的合法成果进入应用核验，保留原终态；无写入或拒绝后精确恢复基线可同阶段重试，未知不能解锁，未知或陈旧终态通知不进入源文件回滚，后续权威终态可接续收集；候选版本变化且缺少稳定现场快照时保留成果并阻断回滚 | 候选源模式16组终态/校验组合及隔离模式恢复、守卫恢复测试；execution-states-1440.png为合成failed状态；两次真实BUG校验拒绝均无提前迁移 |
| AC-007 | API重启后持久守卫恢复；刷新仍锁住unknown；旧回调不能释放新执行；项目切换旧请求被丢弃 | execution-unknown-1440.png为故障注入；真实隔离API重启后恢复响应；持久/前端竞争测试 |
| AC-008 | completed不等于业务成功；REQ完善无有效写入保留planning；BUG生成范围校验拒绝保留capture；成功指纹和同步联合确认 | live-generation-result.json、两次BUG慢收尾及终态；验证器/候选测试 |
| AC-009 | REQ/BUG各10种对象入口共享准入；卡片和助手共享服务；直接已识别命令同事务抢占 | 全入口HTTP集成测试20种+真实BUG请求10种；前端卡片/助手测试。未声称每种命令独立完成模型轮次 |
| AC-010 | 外部CLI可收敛且不伪造turn；172个历史对象合法事实校验零失败；归档目录兼容历史trace | external-sync.json、历史规格/归档验证器回归 |
| AC-011 | 执行中bug.md抽屉、研发中tasks抽屉可读；任务/人工验收入口不加写锁 | execution-read-document-1440.png、external-start-read-progress.png；前端只读入口回归 |
| AC-012 | Web行为→服务端请求→任务→guard span关联成功；直接API409无行为事件；未保留原始正文 | observability-sample.json；请求ID伪造、metadata白名单、日志降级/保留周期回归 |

## 逐入口分类

| REQ入口 | BUG入口 | 卡片/助手/API行为 | 证据 |
|---|---|---|---|
| req-explore | bug-explore | 只读分析准备，忙碌时返回原执行 | 20种合成HTTP与10种真实BUG请求 |
| req-generate | bug-generate | 生成成果的完成迁移受三重门禁 | 同上；REQ真实成功、BUG真实慢收尾及负向校验 |
| req-complete | bug-complete | 原会话继续，成果验证未通过不迁移 | 同上；REQ真实负向完善 |
| req-review | bug-review | 同对象互斥，评审业务门禁不绕过 | 同上及评审候选回归 |
| sprint-propose --req | sprint-propose --bug | 同对象互斥，项目范围校验 | 同上及Sprint双向归属验证 |
| req-opsx | bug-opsx | 同对象互斥，不跳过旧活动会话 | 同上及验证器 |
| opsx-apply | opsx-apply | 启动开发即时投影，完成验收受门禁 | 同上及生命周期/CLI页面 |
| opsx-modify | opsx-modify | 返修投影和首次完成事实保留 | 同上及生命周期/前端回归 |
| opsx-archive | opsx-archive | 归档身份/来源和完成事实验证 | 同上及归档兼容回归；本BUG未归档 |
| open-chat/Agent助手 | open-chat/Agent助手 | 使用同一对象会话准备入口 | HTTP与前端助手测试 |

文档、进度、验收是只读入口，不占写锁。未接入的动作维持服务端422。未绑定对象的普通对话和自由文本工具写入不能被识别成任意治理命令，明确不承诺跨外部进程互斥；外部并发写入通过指纹变化保守阻断。

## 视觉签认

Agent已目视核对用户批准的增量骨架与实际产品。execution-states-1440.png覆盖执行中/失败待核对，execution-ready-1440.png覆盖可继续，execution-unknown-1440.png覆盖未知态，view-original-execution-1440.png覆盖查看执行，execution-read-document-1440.png覆盖只读抽屉。computed-styles-1440.json记录真实iframe视口、360px卡宽、15px/16px/18px内边距、左3px状态边框及按钮cursor/disabled；与既有token一致，无新增modal、无卡片布局改版。合成API夹具只注入状态，不伪造模型成功。真实模型截图补充阶段与会话行为。

## 样本异常说明

两次BUG生成均completed但成果被既有严格边界校验拒绝：第二次模型将注册表path由无尾斜杠规范化为有尾斜杠，违反生成命令不改变path的现有约束；不作为生成成功。拒绝成果的diff保留在私有产品库，事实源精确回到基线后可同会话重试。未修改此既有校验，也未无限重试。正向业务完成证据来自REQ生成同轮exit0与已应用成果，负向证据来自BUG和REQ完善；不同轮次没有拼接为同轮成功。

## 文档一致性

父需求REQ-0012、REQ-0020、REQ-0025的卡片、文档抽屉、Chat和原型相关章节已复核。保持既有布局、权限、只读drawer与手动发送语义；此次新增执行门禁以BUG及Change增量契约记录，不重写已归档原型或历史验收。REQ-0046过程输出提示和BUG-0046运行中问答入口不在本次实现范围。

product_data_collection_observability: applicable

affected_layers: Web、API、SQLite/MySQL、usage_events、request_logs、task_traces、task_trace_spans、agent_workflow。

validation: 脱敏四层关联、服务端请求ID、直接API无Web事件、guard原因码、日志失败降级及既有保留周期。新增两张守卫表；API/OpenAPI/客户端字段已同步。部署拓扑、管理端、对象存储及认证授权机制N/A：未新增服务、存储调用或权限授予。
