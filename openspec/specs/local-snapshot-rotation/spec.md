# local-snapshot-rotation Specification

## Purpose
TBD - created by archiving change add-local-data-mount-and-snapshot-rotation. Update Purpose after archive.
## Requirements
### Requirement: 自动快照数量配置

Chat 本地自动快照 MUST 由 `MOONBOX_CHAT_LOCAL_SNAPSHOT_LIMIT` 控制，缺省值为 `2`；正整数限定未受保护自动快照的数量，`0` 停止自动创建且不得删除已有副本或独立删除日志。配置仅接受非负十进制整数，API 与 Worker MUST 使用一致值。

#### Scenario: 缺省和正整数配置

- **WHEN** 环境变量缺失或配置为正整数 `N`
- **THEN** 自动快照上限 MUST 分别为 `2` 或 `N`
- **AND** 启动及约 24 小时周期的未受保护自动快照 MUST 在轮转后不超过该上限

#### Scenario: 关闭自动快照

- **WHEN** 配置为 `0`
- **THEN** 启动和周期任务 MUST 跳过自动快照创建
- **AND** 已有副本、手动备份和独立删除日志 MUST 保留可用

#### Scenario: 非法配置与进程不一致

- **WHEN** 配置为空、负数、小数、非数字或 API 与 Worker 的解析值不同
- **THEN** 系统 MUST 明确报告配置或就绪错误
- **AND** MUST NOT 静默采用默认值继续生成快照

### Requirement: 受保护的自动轮转

系统 MUST 在新快照通过完整性、摘要和账本登记校验后，按创建顺序通过受控接口过期超额的未受保护自动副本。手动副本和治理成套备份 manifest 引用的副本 MUST NOT 被自动过期；来源不明的旧副本 MUST 在核对前保留。

#### Scenario: 有效新副本完成轮转

- **WHEN** 创建并验证的新自动快照使未受保护自动库存超过上限
- **THEN** 系统 MUST 按创建顺序逐份受控过期超额副本并更新账本
- **AND** MUST 记录数量、占用与逐次过期结果的脱敏摘要

#### Scenario: 治理引用和手动副本保护

- **WHEN** 自动副本被治理 manifest 引用，或库存条目为手动副本
- **THEN** 该副本 MUST 不因自动上限而过期
- **AND** 被引用的自动副本 MUST 作为受保护例外记录

#### Scenario: 创建校验或过期失败

- **WHEN** 新副本完整性、摘要、登记或旧副本过期失败
- **THEN** 系统 MUST 保留此前有效恢复点与账本一致性
- **AND** MUST 给出脱敏失败摘要，不得用未验证副本替换最后有效副本

### Requirement: 删除意图与历史快照恢复

会话删除意图 MUST 独立持久保存，不受自动快照配置和轮转影响。历史快照离线恢复 MUST 重放删除意图，治理成套备份引用 MUST 可验证。

#### Scenario: 旧快照恢复已删除会话

- **WHEN** 使用删除发生前的历史快照进行离线恢复
- **THEN** 系统 MUST 重放独立删除意图
- **AND** 已删除会话 MUST NOT 复活

#### Scenario: 关闭自动快照后恢复

- **WHEN** 上限为 `0` 且已有快照或治理 manifest 仍在
- **THEN** 系统 MUST 继续支持库存登记、引用校验和离线恢复
