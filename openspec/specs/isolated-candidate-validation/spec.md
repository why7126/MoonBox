# isolated-candidate-validation Specification

## Purpose
TBD - created by archiving change add-isolated-candidate-validation. Update Purpose after archive.
## Requirements
### Requirement: 受控不可变候选供应
系统 SHALL 仅按服务端批准模板为固定候选准备隔离环境，固定镜像、平台、依赖锁、计划及 Git 版本。

#### Scenario: 请求无法替换模板
- **WHEN** 客户端请求验证候选
- **THEN** 服务端从批准配置取得命令与镜像，不接受客户端声明通过或任意宿主路径

#### Scenario: 双库实际验证
- **WHEN** 供应器执行批准的 moonbox-web-python-v1 模板
- **THEN** SQLite 与 MySQL 8.4 linux/arm64 分别使用独立数据，真实执行迁移、种子、应用健康/版本探针和适用检查，必需项均通过才形成证据

### Requirement: 持久生命周期和受限资源
系统 SHALL 在创建资源前持久记录归属与租约，限制容量、超时与网络，并确认清理后才交付通过证明。

#### Scenario: 中断恢复
- **WHEN** 原进程中断或留下未知状态
- **THEN** 重入核对精确标签并清理所属资源，不盲目重放未知副作用，不清理其他环境

#### Scenario: 清理失败
- **WHEN** 无法证明容器和专属网络已消失
- **THEN** 保留恢复记录并阻断候选通过，重试清理不重复执行已完成检查

### Requirement: 验收证据与合入身份关联
系统 SHALL 将服务端证据绑定候选、环境和计划，并复用既有验证执行器；源码单独通过不得替代组合验证。

#### Scenario: 版本发生变化
- **WHEN** 源、主线、候选、治理或模板发生变化
- **THEN** 原通过证明不得授权新候选合入

### Requirement: 依赖子交付不冒充整体需求完成
系统 SHALL 区分当前 Change 验收与来源需求的完整验收范围。

#### Scenario: 必要依赖完成
- **WHEN** 带有 issue_acceptance_scope partial 的子交付计划取得 ready
- **THEN** 当前 Change 保留通过证据，来源需求验收投影为 partial，完整需求剩余 AC 不被自动勾选

#### Scenario: 子交付归档准入与父需求保留
- **WHEN** 子交付当前证据完整并取得partial签认
- **THEN** 当前Change独立核验恢复和规格合并门禁，父Issue完整验收仍阻断；父需求不得仅因该Change归档而变为done或迁入archive

