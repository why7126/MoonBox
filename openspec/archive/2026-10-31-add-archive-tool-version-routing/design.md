---
title: 归档工具独立版本路由设计
---
# 归档工具独立版本路由设计

## 背景
ArchiveDriver当前从project.root/scripts取工具；ContainerAppServer由Docker守护进程直接绑定宿主workspace为/work，父容器挂载不会自动传播。改变source_root会影响历史操作绑定，故保持业务根不变。
## 目标与非目标
独立固定归档工具版本，完整保留工作区。排除隔离验收、数据库策略、部分交付新状态、历史unknown恢复及当前环境部署。
## 决策
部署配置指定工具包根、预期摘要及兼容版本；未配置保持原模式，显式配置无效即阻断。工具包包含必要scripts、Python模块和规则，具有逐文件manifest，拒绝可写目录、符号链接、路径逃逸和摘要漂移。配置只来自运维受控入口，Agent参数不得选择任意宿主目录。
事实目录继续作为cwd与业务root；工具目录只用于命令定位和受控Python导入。逐项拆分脚本中根据__file__推导业务根的行为，禁止把工具包当作事实仓库。产品驱动的authority上下文与原operation传递保持原链路；不得另起无授权子进程绕过现有fence。
Worker显式传递同一工具包宿主目录到子容器固定只读挂载点；映射来自部署白名单，启动核对digest，不能只验证父容器。CLI、服务和执行器缺包或版本不同均拒绝写入。
恢复及重放重新校验工具版本；没有可证明的原版本绑定时阻断并回读原操作，禁止猜测新版本兼容。优先复用已有tool_hash/script_hash与操作证据；实施前确认持久绑定可用性，不新增数据库字段作为默认方案。
## 风险与权衡
全量工作区发布会扩大范围，拒绝；只覆父容器会使子容器漂移，拒绝；修改绑定路径会破坏历史身份，拒绝。独立包引入路由复杂度，以默认兼容、显式失败关闭及真实子容器测试约束。
## 迁移与回滚
先构建独立包、隔离验证，再形成只读挂载配置。真实部署另行授权。回滚恢复工具digest与镜像组合；旧执行器缺失保持领取冻结，不清unknown、会话占用或恢复账本。
## 待验证事项
现有恢复记录能否完整绑定工具版本；Shell/Python入口闭包；Docker宿主路径映射。Web漂移属于独立发布兼容评估，本Change不宣称已解决。


## 实施契约细化

固定配置入口为仓库外 `/etc/moonbox/archive-tools.json`，schema_version为1；root、host_root与digest来自受控只读配置，不接受Agent环境变量或请求参数选根。manifest为schema_version与files的精确清单；构建仅包含脚本源码、后端Python模块和规则白名单扩展名，避免复制真实env、运行时数据或前端产物。子容器挂载点固定，启动先验证再运行原app-server。

普通归档和Sprint关闭复用操作manifest字段绑定digest；受控归档的原input_hash绑定私有sidecar（operation_id、original指纹、digest），不新增数据库字段。无原绑定的历史操作在启用独立路由时拒绝恢复；禁用路由也不能重放已绑定操作。CLI恢复日志同样绑定digest。全部路径保留原权限和fence校验。

product_data_collection_observability:
  status: applicable
  affected_layers: [agent_workflow, task_traces, task_trace_spans]
  reason: 归档工具路由与Worker领取门禁影响执行链；沿用原操作身份和既有任务观测，不新增HTTP接口、DB字段、usage_events或Web请求封装，不改变request_logs和保留周期。
  validation: 定向回归覆盖旧模式、拒绝、恢复及重放；真实隔离容器核对CLI、服务驱动与生产子容器启动，固定错误码不包含宿主路径。不存在UI变更，OpenAPI及客户端无需生成。
