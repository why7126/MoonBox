---
title: Chat 验收运行能力验证记录
created_at: '2026-10-31 13:20:00'
updated_at: '2026-10-31 14:02:00'
---

# Chat 验收运行能力验证记录

用户已授权本机 MoonBox 测试部署和独立合成样本，并确认能力卡片布局。当前实现已在真实产品 Chat 完成一次原生验收调用：四项检查通过、结果返回原轮次、临时验收资源释放。自动验收及归档准入以 evidence/acceptance/ 的最新 manifest 为准；未执行正式归档或生产部署。

## 逐项证据

| 验收项 | 结果与证据 |
|---|---|
| AC-001 执行前能力 | 会话授权预检与实现轮次诊断；缺失能力独立报告。manual/regression.json、preflight-trace.json、browser/product-preflight-style.json。启动时项目验证不可用与隔离工具可用可以并存，不伪报通过。 |
| AC-002 Python | Linux arm64 固定镜像 pytest/httpx/AnyIO 导入及真实线程探针通过；隔离运行中的 HTTP 项目测试通过。manual/python-runtime.json、product-matrix.json。 |
| AC-003 前端平台 | Linux arm64 Node 22.23.3、pnpm 11.2.2、锁文件一致制品，11 项组件/消息回归通过；只读根目录、有限临时目录，不复用宿主 node_modules。 |
| AC-004 服务与绑定 | 心跳、过期探针、版本、src/web 子目录与批准模板校验回归通过；真实页面重新检查显示 Python/服务探针就绪。 |
| AC-005 调用与回传 | 原生工具在真实模型轮次调用一次，四项结果通过并在原会话展示；manual/chat-result.json 和 browser/product-completed.png。 |
| AC-006 浏览器 | Chromium 151.0.7922.34 / Firefox 153.0 对真实产品目标执行成员/只读角色断言，1440/390 共16幅截图；能力组件4状态×2视口合成截图另列。真实Chat卡片1440/390样式无横向溢出，窄屏上下滚动可读。 |
| AC-007 恢复 | 176项后端集中回归覆盖局部失败、输入指纹、检查点、恢复竞争与取消后不自动续接；独立MySQL并发状态测试通过。恢复负向测试属合成回归，不宣称本次产品轮次发生恢复。 |
| AC-008 异常 | 浏览器失败、不可达目标、依赖/版本/平台、网络及清理失败具有稳定错误码；禁止无限重试。见回归与manual/browser-limit-diagnosis.json。 |
| AC-009 安全 | 跨空间、撤权、任意命令/路径/目标和配额取消回归通过；网络隔离、只读、固定镜像/入口、资源回收保持。观测仅保留状态/原因/引用。 |
| AC-010 当前部署 | 当前源码指纹匹配；turn 277c9b68-d03d-4443-a607-44023d172029，operation 84c76ca1-d6d8-4033-8407-0e5bdb5afa54；completed/passed/released，resume_count=0，工具等待结果delivered，原生只读证明verified=true。 |

## 验证分层与修复事实

- 后端集中回归176项通过；浏览器文件限制修复后24项相关增量回归通过，范围重叠，不累加为200项唯一用例。
- 前端Linux回归11项通过，类型检查及生产构建通过。历史消息测试样本补充问答接口空结果和持久化用量，匹配已落地接口。宿主Node25内置localStorage不适用该测试，正式结果使用批准Linux Node22制品。
- 实际产品隔离矩阵四项通过并回收；真实模型Chat再次执行同一当前模板，四项通过、结果回传和资源回收均独立核实。截图不替代产品状态证明。
- 浏览器探针通过但真实页面初次关闭，单变量对照确认10MiB单文件上限不足；调整为128MiB后双浏览器通过。截图证据仍限制10MiB，网络/只读/内存/进程边界不变。该发现不用于反推历史AnyIO异常的唯一根因。
- 能力卡片原先在消息滚动区域外，自动跟随影响查看；移入消息列表footer后复验刷新、结果展开及滚动查看，卡片保持可达。
- 现有大包及Starlette弃用提示不影响结果。私有控制器矩阵缺Chat Trace表不作为Chat证据；真实Chat存在chat.verification_preflight及acceptance链路，脱敏记录另存。

## 影响与文档

新增只读Chat verification-preflight API，已同步OpenAPI/Orval、API索引、Web卡片及README；Python/前端固定测试镜像和worker独立探针已同步部署与容器文档。沿用现有acceptance权限/取消/恢复/证据，数据库无新增表或迁移；对象存储和保留周期无变化。正式环境凭证未修改，当前只验证授权本机部署。

product_data_collection_observability: applicable；affected_layers: API、Chat执行、Web、Task Trace、验证服务；validation: 预检及原生验收关联、权限负向测试和脱敏证据通过。DB schema、对象存储和保留周期N/A：复用现有机制。未落盘Prompt、凭证或宿主路径。

## 执行链路复盘

BUG已评审并纳入sprint-017，Change实施及产品取证完成，随后运行自动验收；最终状态由共享门禁给出。环境缺失与业务失败、配置与真实通过、模型结束与任务完成分别记录。建议后续镜像例行冒烟同时覆盖浏览器启动和真实页面加载，避免只验证可执行文件；未自动创建后续Issue。

自动验收结果：10/10通过，当前证据ready，归档临时副本预演通过；只执行1次共享证据验证，7项去重，其余2项读取原生产品轮次证明。Workflow Sync无错误，根因文档confirmed字段保留其根因语义，不改为交付状态。临时Docker run检查容器0、网络0；测试服务已停止。
