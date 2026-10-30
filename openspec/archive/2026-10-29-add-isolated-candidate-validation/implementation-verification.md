---
title: 实施验证与样本边界
created_at: 2026-10-29 12:50:00
updated_at: 2026-10-29 12:50:00
---

## 最终实施与验收依据

本次以统一主目录 → 工作区恢复点 → 固定候选隔离验收 → 迭代权限确认合入的依赖顺序完成实现。仍保留 Web 入口，模块职责使用 moonbox- 前缀，moonbox-tui 仅保留职责名，不新增终端产品。

| 证据层 | 实测结果 | 本 Change 入口 |
|---|---|---|
| 后端稳定回归 | 248 项通过、21 项子测试；3 项显式环境样本跳过，真实模型与 Docker 另列 | evidence/implementation/stable-backend.json |
| MySQL 8.4 | 69 项通过、1 项环境样本跳过；真实双库候选另列 | evidence/implementation/stable-mysql.json |
| 前端与类型 | 5 项通过，TypeScript 检查通过；OpenAPI 与源码一致，Orval 已生成 | evidence/implementation/ui-regression.json |
| 真实模型隔离轮次 | Codex CLI 0.153.4 完成文件修改、两恢复点、执行器退出及占用释放；合成身份，非生产部署 | evidence/implementation/isolated-live-round.json |
| 独立候选供应 | SQLite 3.46.1 / MySQL 8.4.13，迁移、种子、检查、固定版本与 Chromium 156 通过，环境清理 clean | evidence/implementation/live-candidate.json |
| 真实 HTTP / Git | 权限撤销403、源提交变化409、合法确认完成合入和治理同步；回执中断注入后两次续接均未增加提交 | evidence/implementation/live-api-flow.json |
| UI 视觉 | 1440×900、1024×600、390×844 深浅主题、正常/拒绝/错误/完整动作族；低高度正文滚动、footer可达、无横向溢出，键盘焦点与Esc通过 | evidence/ui/visual-review.json、workspace-keyboard.json 与 verified-*.jpg |
| 性能样本 | 100个文件、409600字节、单次扫描/采集/恢复实测，完整恢复100个文件；无SLA声明 | evidence/implementation/performance-sample.json |

真实浏览器使用当前 WorkspacePanel 和真实 API，登录身份、业务仓库和数据为一次性合成样本；静态 Skeleton 只用于结构确认，未冒充产品执行。浏览器镜像是固定摘要的临时 Chromium 验收镜像，未宣称 Firefox 或生产部署已验证。所有临时容器与专属网络已检查零残留，API和Web临时服务已停止。

product_data_collection_observability：applicable；affected_layers=web,api,db,agent_workflow,usage_events,request_logs,task_traces,task_trace_spans；validation=服务端请求ID关联任务/行为，伪造字段不参与鉴权；跨空间/仓库、撤权和对象拒绝回归通过；业务授权/恢复依据强一致，通用遥测失败不制造通过。移动/桌面客户端与新对象存储后端为N/A，本期未启用或新增。

## 本轮问题与修复证据

- SQLite 的 SAVEPOINT 在尚无真实事务时释放会提交预留占用。已先建立外层事务，双队列及回滚回归通过。
- 固定候选控制器 server.py 遮蔽项目同名入口，真实容器首次失败且清理成功；移除控制目录的模块搜索优先级后，双库浏览器通过，新增同名应用回归。
- 连续替换 MySQL 连接池时，事件注册表可报告存在而实际回调为空，锁预算残留为5秒；最小复现第8个池失败。改用稳定 Pool 类回调后300个池验证通过，整组MySQL回归通过。
- 部分依赖交付必须具有独立 AC 清单、Issue映射与范围说明；Workflow Sync 保留 partial，不覆盖完整 Issue AC 勾选。183项治理回归通过（包括子Change准入、父Issue保留与晋级阻断）。

## 实现与文档一致性

API索引、OpenAPI/Orval、数据库设计、增量迁移、部署挂载、安全及观测文档已同步。主目录治理记录只新增合入事实，不提前归档或改变正式规格。未提交治理修改保留给受控提交流程；不会自动提交其他人工修改。旧copy目录保留为历史工作区，未知范围的旧快照仅允许已证明的逐文件恢复。

实现任务完成后自动续接逐AC验收；最终准入以 evidence/acceptance 最新报告和共享归档门禁为准。未执行正式归档、远程推送或生产发布。
