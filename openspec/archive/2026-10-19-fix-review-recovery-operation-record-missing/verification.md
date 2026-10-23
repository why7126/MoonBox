---
title: 评审恢复记录完整性验收映射
created_at: "2026-10-19 14:41:56"
updated_at: "2026-10-19 15:32:05"
---

# 评审恢复记录完整性验收映射

## 交付结论

实现及修复验证完成。统一准备、启动预检与收尾的操作记录契约；缺失、损坏、身份冲突明确阻断并保留基线。已有 prepared 候选不再跳过新请求记录，重试不覆盖原记录。治理错误码沿现有轮次和候选链路保留。

最终源码的 244 项组合回归及 6 项子测试通过，正式自动验收见 evidence/acceptance 的最新完整清单；此前 diagnostic 清单只表示当时尚未采集产品证据。实际运行验证使用独立本地项目、数据库、测试身份及 backend/worker/controller；原业务部署未升级。没有把工作区修改当作线上修复。

## 逐项证据

| AC | 证据及结论 | 类型 |
|---|---|---|
| AC-001 | 12 个支持动作参数化验证；准备、worker 预检与收尾共用完整性判断 | 合成回归 |
| AC-002 | BUG 正常完成并应用；REQ 评审成果在轮次中断后恢复应用；分别 6→7、8→9 个文件，均 approved/review，索引正确，受保护文档完整 | 真实产品与文件回读 |
| AC-003 | baseline-only、整个记录缺失、非法 JSON、非法 schema/steps、身份冲突在执行器前阻断 | 合成回归 |
| AC-004 | 写入中断保留基线；REQ 原 stopped 终态保留且成果核验成功；三个服务重启后哈希和状态一致 | 合成回归与真实恢复 |
| AC-005 | 响应丢失/重复恢复回归；两个真实候选均只有一条 applied 应用，重启未重复迁移 | 合成回归与真实恢复 |
| AC-006 | 同对象互斥、版本、权限撤回与绑定变化回归通过，未放宽既有门禁 | 合成回归 |
| AC-007 | 六类记录准备错误保留原码与 preparation 阶段；业务拒绝样本未被模型 completed 掩盖；真实中断会话显示已停止/部分输出，已应用卡片独立显示已评审 | 合成回归、负向与正向产品观察 |
| AC-008 | deployment.json 的三个模块哈希与最终源码一致；同源码全新隔离 backend/worker/controller 完成评审并重启回读 | 实际运行版本 |
| AC-009 | BUG-0044 互斥、候选、执行门禁与会话连续性回归通过；真实评审复用对象会话并显示下一阶段动作 | 合成回归与真实观察 |

## 正常完成与恢复事实

- BUG-9096：模型轮次 completed，候选及唯一应用均 applied，phase verified，操作记录 terminal。见 [缺陷结果](evidence/acceptance/bug-review-result.json)。
- REQ-9095：模型轮次 stopped / execution_access_or_workspace_error，候选及唯一应用均 applied，phase verified。恢复没有篡改原轮次；没有把该轮次报成 completed。错误底层原因本轮没有足够证据确认，保留诊断，且不属于 operation 缺失。见 [需求恢复结果](evidence/acceptance/req-review-result.json)。
- 自动验收的正常完成同轮检查绑定 BUG 轮次；REQ 作为单独真实恢复证据附加，未放宽 product_turn 对 completed 的校验。
- 重启三个隔离服务后，源文档与结果哈希一致，各一条应用，负向拒绝与 stopped 事实未改变。见 [重启证据](evidence/acceptance/restart-verification.json)。

## 视觉与数据边界

两张已评审卡片分别完成页面刷新/重连、1440×900 截图及 computed style 检查。截图显示目标卡片完整、review.md 入口及加入迭代动作，待评审列计数为 0。页面使用真实隔离后端数据，没有 Mock 替代。未修改前端布局、原型或按钮族，因此 UI Skeleton 与参考稿复刻门禁不适用；本次只验收状态流转。

证据：[需求卡片](evidence/acceptance/req-review-board.png)、[缺陷卡片](evidence/acceptance/bug-review-board.png)、对应 req-review-style.json / bug-review-style.json。样式采样包括真实视口、卡片尺寸、字体、前景与背景色。

## 动作适用矩阵

| 动作族 | 记录与前置核验 | 本次验证 |
|---|---|---|
| req/bug-generate | 支持 | 参数化初始化及既有门禁；无需重跑模型生成 |
| req/bug-complete | 支持 | 参数化初始化、候选及恢复回归 |
| req/bug-review | 支持 | 全链路真实评审、完整迁移与恢复 |
| req/bug-opsx | 支持 | 参数化初始化及执行/权限门禁；不扩大至新 Change |
| sprint-propose | 支持 | 参数化与原 Sprint 完成门禁 |
| opsx-apply/modify/archive | 支持 | 参数化与原完成/归档门禁；不执行真实归档 |
| 普通对话、只读动作、未接入命令 | 无写操作记录要求 | 普通对话跳过记录预检回归；不增加模型或外部副作用 |

## 失败样本与自修过程

此前 REQ-9097 因模型越界修改子文档被 review_unrelated_document_edit 拒绝；BUG-9097 继承了实施阶段验收来源，被 review_acceptance_scope 拒绝；REQ-9096 缺少初始 CHANGELOG 行，被 review_index 拒绝。三者均不计正向通过，未产生应用，摘要保留在 negative-product-observations.json。最终样本在实际模型执行前通过真实评审校验器预检，预检本身不作为产品成功证据。

临时测试配额不足暴露已准备候选跳过新请求记录的边界，已在当前 apply 内修复并回归。仅调整隔离测试账本，不改原业务配额或购买额度。最初 macOS 临时路径别名导致互斥测试失败，使用实际临时路径后通过，符号链接安全校验保持不变。

## 影响与观测声明

product_data_collection_observability: applicable。affected_layers: API、Task Trace、轮次/候选/应用与 Web 状态反馈。validation: 准备阶段错误原码测试、真实轮次到候选及应用的脱敏身份关联、源状态与页面回读、重启后幂等回读。

修改 direct_command_journal.py、preparation.py、chat/preparation_failure.py 及聚焦测试；API 文档同步具体错误码，沿用现有字符串错误字段，无新路由或响应字段，OpenAPI/Orval 生成不适用。DB schema、usage_events、对象存储、保留周期和 UI 布局无变化；请求封装和链路字段未改变，沿用原有采集。权限、绑定、源版本与互斥仍执行原校验。临时部署只用于本轮验证，正式业务部署仍需后续发布。

长期证据仅保存最小脱敏结果、截图及指纹；不包含凭证、完整 Prompt、原始事件、数据库或原始业务日志。终态异常的进一步原因分析与展示增强继续归关联需求范围，不自动创建新 Issue。

## 正式验收与签认

2026-10-19 完整验收运行 20261019153058472542-5b217550：9/9 passed，failed 0、blocked 0、pending_collection 0，复用 7 项，当前无重复命令执行。先前组合回归一条执行覆盖六项检查，去重 5 次。归档临时副本预演 passed，readiness ready；opsx.apply 与 opsx.accept 均零错误，Issue acceptance_status 已回填 passed。

已目视核对两张 1440×900 截图的完整目标卡片、已评审列和下一阶段动作，并核对对应 computed style；视觉签认仅覆盖状态与内容完整性，不宣称做过 UI 重设计。第一次正式检查因沙箱本机端口限制局部 preflight 失败，取得本机隔离预检权限后通过，未删改诊断记录。

正式报告：[逐 AC 结果](evidence/acceptance/20261019153058472542-5b217550/summary.md)。自动验收完成后仅关闭本轮隔离测试服务，保留脱敏证据与私有测试现场；未执行真实归档或升级原业务部署。AI Usage 自动发现无可归因运行，usage_mode unavailable，不作为交付阻塞。
