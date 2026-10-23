# acceptance-validation-orchestration Specification

## Purpose
TBD - created by archiving change optimize-acceptance-stable-validation. Update Purpose after archive.
## Requirements
### Requirement: 前置完整入口与稳定验证
Agent MUST 在高成本验证前建立入口矩阵并稳定本批输入，修改后按实际依赖复验，保留正确性门禁。

#### Scenario: 多入口存在数据形态差异
- **WHEN** 产品与 CLI 共用流程但存在字段别名或工作区投影
- **THEN** 前置检查覆盖这些入口与样本差异，不以隔离成功替代正式入口核验

#### Scenario: 验证中输入改变
- **WHEN** 验证期间输入变化
- **THEN** 受影响结果失效，完成修复后复验依赖闭包，不发布虚假通过

### Requirement: 有效证据复用与克制反馈
Agent MUST 仅复用指纹、效果、环境和附件有效的成功证据，按里程碑反馈并保留真实失败。

#### Scenario: 未受影响项仍有效
- **WHEN** 仅部分依赖发生变化
- **THEN** 保留其他有效证据，完整 readiness 仍要求所有验收项有效

#### Scenario: 长任务尚在等待
- **WHEN** 没有新的结果或阻塞
- **THEN** 合并重复日志轮询，不提前宣称最终完成，不遗漏必要进度反馈

### Requirement: 部署态验收输入来源与指纹一致性

系统 SHALL 按明确的输入来源契约读取治理投影及绑定源码中的验收输入，在相同合法输入下保持本地与部署态指纹一致，并保留真实性与路径安全门禁。

#### Scenario: 投影缺少源码与根级输入
- **WHEN** 验收计划引用 src、scripts、tests、AGENTS.md、.gitignore 或合法目录，治理投影不包含相应源码输入且可信绑定可用
- **THEN** 系统 SHALL 从明确授权的来源读取，计算与本地相同的指纹，不将实际存在的输入误判缺失

#### Scenario: 治理事实与工作副本不同
- **WHEN** 治理事实只应由投影提供而另一个工作副本存在不同内容
- **THEN** 系统 SHALL 保持权威来源，不以无条件回退掩盖缺失或覆盖治理事实

#### Scenario: 输入真实变化或不安全
- **WHEN** 输入缺失、内容变化、不可访问或路径越界及符号链接逃逸
- **THEN** 系统 SHALL 阻断受影响验收，拒绝未授权读取，不改写既有证据使其通过

#### Scenario: 修复部署后复核
- **WHEN** 当前输入与有效验收证据一致且其他归档条件满足
- **THEN** 部署态 readiness SHALL 为 ready，刷新后的卡片可完成或归档，并留有运行版本和浏览器证据

