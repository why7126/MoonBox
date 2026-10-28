---
title: Chat 中断后独立后继证明验证记录
created_at: '2026-10-27 17:06:00'
updated_at: '2026-10-27 17:40:00'
---

# Chat 中断后独立后继证明验证记录

## 交付范围

无旧成功同步证明的终态 apply/modify，可凭原操作及可信启动基线核验独立后继交付。身份、权限、绑定、时间、正式收据、当前验收和全量差异全部验证。界面差异展示最多30条，授权判断不截断。旧步骤、事件及停止状态不被改写。

现场发现原执行后 rules/issues-lifecycle.md 合法变化，用户明确授权补充设计及评审。新增 successor_dependencies.py：原操作、基线、规则前后摘要、唯一归档来源及完整当前验收共同绑定，正式收据对计划和报告签名。只允许已有规则修改，不允许新增/删除、未覆盖输入、正式规格/Sprint变化或未知来源。用户此前批准的任务3.3验收调整以原操作、基线和前后任务摘要单独承接，任务数量/顺序/编号不变且完整设计规格纳入验收。原依赖拒绝和事务围栏保留。

## 回归结果

- SQLite：interrupted/successor/direct/verification_transaction/archive_proof五组171项通过；interrupted组49项包含14项规则承接和10项任务承接正反例。
- MySQL 8.2：interrupted/successor/verification_transaction三组83项通过，任务承接增量10项通过；使用登记的隔离无持久卷容器，结束check为0容器/0网络。
- 前端：核验入口、自动跟进和恢复面板22项通过；TypeScript构建检查通过。补测卡片无专用operation时惰性请求原turn，以及旧自动失败原因不覆盖新核验资格。
- 真实执行器链路：HTTP排队后中断→标准CLI完成及验收→HTTP核验→后续动作实际发送→真实Codex completed，更新实现后再次通过。原轮排队时中断，未启动模型；后续轮真实运行，SQLite样本。MySQL亦增量执行相同真实链路并completed，独立报告为samples/live-mysql.json。临时授权已删除。详见 samples/ac-007.json。
- 视觉：真实HTTP接口、合成身份/停止轮次；卡片OperationVerification与TurnActivity在1440×1000和390×1000覆盖可核验、忙碌、失败、成功。旧状态仍已停止，后续报告路径可展开，长路径换行，无横向溢出。8张截图及styles.json位于evidence/acceptance/samples。Chrome视口覆盖未实际生效，已改用侧边浏览器并核对实际innerWidth，错误尺寸截图已替换。

## 现场核验

用户已授权更新本地服务并完成BUG-0056现场核验，不归档。部署前确认没有queued/connecting/running/stopping执行，保留一条无执行容器的历史unknown记录。通过标准docker-up更新self-storage-sqlite，并保留更新前镜像。

第一次现场显式核验正确拒绝规则依赖差异，未解除保护。差异为生命周期阶段镜像规则，来源为已归档fix-issue-lifecycle-stage-sync。补充AC-009后，BUG-0056完整验收9/9、正式opsx.accept收据与当前readiness有效；随后部署受控承接实现并复核实际准入。后续发现任务3.3对应用户此前批准的上限验收调整，已加入精确任务承接声明并重新取得9/9与正式收据。数据库读取连续锁等待时停止后台核验进程后立即读取成功且无活动执行，更新流程已恢复服务。最终现场POST返回200；guard为recovered_valid、can_send=true、执行平台ready。旧轮保持stopped，27个步骤SHA256完全一致，旧成功同步仍为0；新记录单独保存规则与任务承接证明。页面显示已由后续执行完成，结果待核对消失、当前阻塞0，恢复完成/归档入口；没有执行归档。已核对原事件导出的ensure_ascii=true序列化口径，167条全字段事件摘要与维护前完全一致；旧停止、步骤及事件均保留。现场证据见ac-008.json与site-card-success.png。

## 界面与横切边界

修改DirectCompletion、OperationVerification及原因映射，复用局部详情；没有新modal或参考稿复刻。selector：requirement-operation-status、direct-completion-verify、direct-successor-evidence、turn-status-trigger。后端新增可选successor_evidence映射，仅返回确认后的安全Change/run标识；OpenAPI及Orval已同步。admin-list/admin-form/admin-modal/media-upload为N/A。

API、数据库与部署说明已同步；无数据库schema迁移、对象存储或管理端改动。product_data_collection_observability: affected。affected_layers: governance workflow、completion proof、API admission、Web UI、recovery audit。复用请求/Task Trace及direct_revalidated，追加独立依赖证明，不伪造usage事件；不泄漏私有日志正文。

## 门禁及边界

根因门禁、当前中文标题、当前OpenSpec中文及全仓残留分离检查通过。全仓Design System检查存在204条既有问题，本次无新增颜色或样式体系，局部视觉证据单独通过；不将全仓遗留宣称通过。现场恢复已通过，11/11任务已完成，opsx.apply与opsx.accept已同步，8/8验收通过，归档预演ready，未执行归档。本地后台与页面轮询发生数据库锁争用，worker曾因OperationalError重启。关闭本次验收页后，停止相关服务释放锁，按后端→worker→后台核验顺序恢复；初次复查worker健康、重启计数0；后续锁争用仍复发，worker计数1、controller计数4，不能据此认定持续稳定。未改数据库或删除历史；未将该维护动作宣称为并发性能根治。Workflow Sync唯一warning是root-cause.status=confirmed语义未声明，按根因语义保留，不改为空。

最后只读复查：后台正常外部同步后对象保护为idle、can_send=true，原stopped、27步骤与167事件摘要仍一致，后继证明仍可查询。该轮平台心跳为worker_starting（此前成功现场为ready）；后台核验暂停取证后已恢复。该环境锁争用属于未消除限制，实际后续执行的双数据库隔离证据与现场发送准入证据分别报告，不宣称现场后续任务已发送。
