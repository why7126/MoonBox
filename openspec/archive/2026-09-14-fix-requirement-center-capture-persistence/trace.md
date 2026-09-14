---
status: applied
iteration: sprint-005
change_id: fix-requirement-center-capture-persistence
bug_id: BUG-0014-requirement-center-capture-not-persisted
created_at: 2026-09-12 16:40:10
updated_at: 2026-09-12 22:17:09
---

## 链路

- 来源BUG：BUG-0014-requirement-center-capture-not-persisted
- 父需求：REQ-0012-frontend-requirement-center
- Sprint：sprint-005
- 根因：confirmed，5条证据门禁通过。
- Readiness：Ready；实现和验收已执行，工作流已同步为applied，待归档。
- product_data_collection_observability：applicable；affected_layers、N/A原因与validation见design.md D5。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-09-12 16:40:10 | bug.opsx | 创建修复提案、设计、MODIFIED规格与16项任务，尚未实施。 |

## 实施与证据映射

核验现有writer后采用项目锁内生成新建计划、目录fd安全创建、私有前后镜像和向前恢复；读取屏障保护半成品。与REQ-0022共享reader/writer/ChatRoute和页面，以增量接入保留已有文档写入及导入回归。终态实际名称applied；context卡片展示短编号，operation与文档地址保留完整ID。

| 验收 | 实现与验证入口 |
|---|---|
| AC-001、002、008、010 | test_governance_capture.py：真实API/字段/项目权限/路径；capture.py生成四文件，schema拒绝额外字段；OpenAPI与Orval |
| AC-004、005、006 | 同测试文件：两请求编号、锁竞争、幂等、逐文件中止重启、目录拒写保护与外部冲突；既有writer回归；MySQL矩阵 |
| AC-005、007 | capture-persistence.test.tsx：终态等待、失败输入、超时复用键、确定冲突新键、关闭与切换项目隔离；requirement-center.test.tsx保留导入/文档行为 |
| AC-003 | capture_live_harness.py与capture_browser_probe.py；evidence/browser-observed.json、capture-1440.png、capture-390.png、document-req.png、document-bug.png |
| AC-009 | ChatRoute请求审计、governance.capture白名单与Task Trace；evidence/observability-observed.json；Compose实际挂载evidence/compose-permissions.json |

真实与合成边界：浏览器未mock网络，真实登录、API、controller、SQLite与项目文件；账号/内容均为合成，未部署到生产。Vitest与故障注入为合成回归，不替代浏览器观察。无新增DB schema、对象存储、安全授权模型或容器拓扑；API/生成客户端、数据库语义、部署说明和观测映射已同步。

UI验收：复用既有Capture布局，无新原型或参考稿。1440px弹窗560px，390px弹窗342px；overflow-y:auto，标题初始焦点通过；窄屏错误输入保留、按钮滚动与聚焦可达。截图由真实Chromium获得，已检查；无需改CSS。

知识沉淀：Capture假成功与跨文件恢复经验记录于docs/knowledge-base/incidents/20260912-capture-persistence.md。

## 最终验证摘要

SQLite Capture/writer 21 passed；共享ChatRoute 31 passed/1 skipped；MySQL 8.2.0矩阵34 passed；Vitest79 passed；TypeScript与Vite构建通过；真实浏览器REQ/BUG创建、刷新、文档及1440/390焦点通过；临时Compose权限通过。

OpenSpec严格/中文、API标准、目录、上下文预算、Sprint Scope及观测校验通过。全库Design System有106项非本次Capture文件违规；定向扫描页面与两份测试及Ops token合约为0违规，见evidence/design-system-scope.json。该全库问题未自动扩展范围或创建Issue。

OpenAPI导出完成；生成脚本因本机pnpm版本不一致退出2，随后调用已安装Orval 8.29.0成功生成governance/chat客户端，无锁文件或包管理配置调整。

共享Chat测试跳过项为需显式开启的真实Codex模型探针；Capture不调用模型，已用真实无模型controller验收，未把skip计为通过。暂无生产发布或用户最终签收声明。

工作流复核：BUG trace关联Change状态applied并记录/opsx-apply，Sprint包含本Change，BUG当前态索引下一步为带完整ID的opsx-archive。acceptance_status由同步器保持pending，表示归档前最终签收；AC逐项自动/真实观察结果已pass。

完成门禁：OpenSpec CLI返回all_done（16/16）；Workflow Sync复跑Updated=0、Errors=0；BUG关联applied和索引归档命令已核对。AI Usage Hook为warning/unavailable（无可归因会话，0条命令记录），不伪造用量。隔离服务已停止。


## 部署返修检查点

反馈：当前环境创建报治理存储未配置，confirmed，容器配置与store.root直接对应。已补常驻Capture配置、30秒心跳、授权就绪查询、禁用/刷新提示及部署自动接入；其他治理写操作继续限时维护，项目锁/版本检查/恢复屏障保留。API/Orval、部署说明、BUG根因与验收、规格delta已同步。

验证：Capture/writer后端22项、部署预检4项、部署生命周期9项，前端80项，MySQL矩阵35项通过；TypeScript/Vite、OpenSpec严格、目录、环境ignore及API/观测门禁通过。当前服务已更新并Healthy，授权项目状态ready=true/continuous，API源挂载只读；controller重启后心跳恢复。真实独立浏览器REQ/BUG创建、刷新及文档通过；1440/390新截图和按钮可达性记录于evidence/browser-observed.json及capture-*，最终就绪提示中性色已目视确认。

目标环境真实观察：用户登录后在当前部署真实创建REQ-0027-capture与BUG-0016-capture；整页刷新后均保留在采集池，两份capture.md可从页面打开且描述完整。文件系统交叉核对两套capture.md、trace.md、注册表与CHANGELOG均已持久化，status=captured且未进入Sprint/开发。两条明确标记的部署验收记录保留。证据见evidence/modify-deployment.json。M4实际行为验证完成。

REQ子文档一致性扫尾：本次为BUG来源，父REQ-0012已归档；无新增原型布局或业务流程，父REQ正文/原型无需更新，反向修复入口沿用现有trace。API、DB和对象存储无新增表/存储域；部署增加的是既有controller的启动接入。

全局中文扫描曾命中另一Change fix-requirement-center-apply-lifecycle-sync的英文脚手架标题，本Change定向扫描无违规；不修改并行工作。未自动创建follow-up Issue/Change。建议后续规范把目标部署就绪、登录态和真实创建分开列验收证据。

最终补验：所有Capture模式均检查controller，后端合并26项通过；部署预检非法模式拒绝通过。当前backend/controller最终镜像已健康，Web最终提示样式已部署。独立测试服务已停止，仅保留当前用户服务。本轮目标账号验证已完成。Workflow Sync opsx.modify：Updated=2、Errors=0、子文档blockers=0；AI Usage Hook：warning/unavailable，无可归因token事件、0条记录，未伪造用量。20/20任务完成，可进入归档；acceptance_status=pending仍表示归档前最终签收。

## 分级返修记录

表单按类型选择REQ三档priority与BUG五档severity，切换保留各自值；API拒绝非法、缺失和混用字段，writer将所选正式分级写入capture/trace/registry/index，移除BUG priority与hint。既有看板context的priority兼容投影未在本次表单返修中迁移；历史Issue不批量改写。

验证：后端29项通过；Capture前端8项通过；完整前端81项通过。TypeScript/Vite/OpenAPI/Orval通过。真实隔离浏览器REQ P1和BUG critical创建、刷新、文档及1440/390通过；窄屏五档自动换行，computed style显示按钮92/142px，scrollWidth不超过clientWidth，截图已目视核对，证据evidence/grading-browser-observed.json及grading-*.png。当前本地Web/API/controller已更新健康；本轮未在目标项目新增验收Issue。

REQ子文档一致性：BUG来源，父REQ已归档，本轮无新业务流程/页面原型；无需修改父REQ子文档。API索引、生成客户端、Change规格与设计、BUG验收及Sprint报告/发布说明已同步；DB schema、对象存储和权限无变化，部署拓扑无变化。

## 弹窗与说明返修记录

Capture桌面宽度840px，REQ支持P0-P3；BUG中文标签致命/严重/高/中/低映射blocker/critical/high/medium/low。共用说明支持Hover、键盘聚焦、Escape及触屏选择后持续说明。API、工作流分级校验与规范一致支持P3。

后端29项、前端82项通过；第一次完整前端回归一项既有文档测试超时，复跑82项全通过。TypeScript/Vite、OpenAPI/Orval通过。真实隔离浏览器REQ P3与BUG critical创建、刷新、文档，1440桌面840px与390窄屏，Hover/焦点/Escape/触屏说明证据见evidence/help-browser-observed.json及help-*.png。无新增真实项目测试条目。

product_data_collection_observability: applicable；affected_layers: Web/API/治理分级；沿用既有事件与关联，未新增日志字段。DB/对象存储/权限N/A，无对应边界变化。REQ子文档：本BUG来源父REQ已归档，无新增业务流程，父REQ无需回写。

P3分级同步幂等回归5项通过；需求四档390px无横向溢出，BUG触屏tap后持续说明通过。提示采用Hover优先于焦点，避免两条说明重叠；该路径纳入定向回归。部署首次系统包下载停滞，停止本次构建后按原Dockerfile重试，不修改运行中的服务或部署拓扑。

最终定向Capture回归9项通过，TypeScript/Vite通过。标准部署重试成功，backend/controller健康；Web最终提示逻辑更新后检查健康。无需修改真实env、DB schema或对象存储。

## 提示去重返修记录

移除分级Hover/焦点浮层，只保留下方当前选中说明和原生键盘选择；ready成功状态不渲染文案及容器，检查中/异常提示、刷新和提交二次校验保留。

前端82项、TypeScript与Vite通过。本轮仅Web展示调整，API/生成客户端、DB、对象存储、权限和部署拓扑无变化，无需重跑后端或重新生成客户端。product_data_collection_observability: N/A；affected_layers: Web展示；未改变请求或事件链路。BUG来源父REQ已归档，未改变业务流程，父REQ子文档无需回写。

真实隔离浏览器1440/390验收通过：宽度840/342px，tooltip与ready容器均不存在，选中说明单份；Enter及触屏选择、异常提示和真实创建后刷新/文档通过。截图及computed style证据见evidence/quiet-browser-observed.json、quiet-*.png，已目视检查。当前Web已更新Healthy，临时服务已停止，未新增目标项目测试Issue。
