## ADDED Requirements

### Requirement: 逐项自动验收与证据包

系统 MUST 按 Change 的 AC 计划执行可自动化检查，并在 Change 证据目录保存每条 AC 的结论、输入指纹和可复核来源。未观察或环境受阻不得记为通过。

#### Scenario: 所有 AC 通过

- **WHEN** 预检通过且每条 AC 均取得计划要求的证据
- **THEN** 系统生成 passed 清单和归档就绪报告，Issue 验收结论可同步为 passed。

#### Scenario: 产品轮次停止或证据缺失

- **WHEN** 轮次未完成、目标命令没有同轮成功事件或文件效果不足
- **THEN** 该 AC 保持 failed 或 blocked，保留安全的轮次标识与原因，不生成可归档结论。

### Requirement: 增量复验与安全样本

系统 MUST 对输入或计划已变化的 AC 重新取证；仅在证据未过期且来源可复核时复用旧结果。带副作用的首次归档样本 MUST 遵守授权、评审和 Sprint 门禁。

#### Scenario: 返修仅影响部分 AC

- **WHEN** 返修只改变某些 AC 声明的输入
- **THEN** 未改变且仍可核对的 AC 复用旧证据，受影响 AC 重跑。

#### Scenario: 样本首次归档中断

- **WHEN** 产品轮次在归档途中停止
- **THEN** 系统保留失败事实，并仅在符合既有授权及治理门禁时恢复或准备独立样本；宿主恢复不替代产品成功。
