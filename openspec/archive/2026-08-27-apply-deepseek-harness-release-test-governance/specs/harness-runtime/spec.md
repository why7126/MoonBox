## ADDED Requirements

### Requirement: Harness 治理资产学习应用

系统 MUST 在通过 `/spec-study apply` 应用外部 Harness 学习成果时，以 MoonBox 当前 OpenSpec、REQ/BUG、Sprint、Workflow Sync 和 `.agents/skills/` 体系为事实源，转写可迁移治理能力，不得照搬外部目录结构或与本项目事实源冲突的自动化。

#### Scenario: 发布与测试治理学习应用

- **WHEN** Agent 采纳外部 Harness 的发布产物、构建记录或测试调度治理经验
- **THEN** Agent MUST 将其转写到 MoonBox 现有发布对象、镜像计划、测试规则、治理校验或 active Change 中
- **AND** Agent MUST NOT 照搬外部 npm 发布、CI workflow、包结构或技术栈特定脚本
- **AND** Agent MUST 在学习报告中说明未采纳内容和不适用原因

### Requirement: 发布产物可复核记录

系统 MUST 在发布、镜像或公开站点构建证据中保留可复核记录，使发布确认能够追溯到明确输入、产物和校验结果。

#### Scenario: 发布确认基于已验证产物

- **WHEN** 发布流程使用构建产物、镜像包、公开文档站投影或外部构建证据作为发布依据
- **THEN** 发布对象或关联 manifest MUST 记录版本、来源范围、输入摘要、产物位置或摘要、生成时间、校验命令和校验结果
- **AND** 发布写入动作 MUST 基于已验证产物或经批准的外部证据
- **AND** 输入漂移、manifest 过期或校验缺失时 MUST 阻断发布确认

### Requirement: 慢测试分区与调度治理

系统 MUST 允许慢测试、覆盖率或浏览器验收按稳定分区调度，但调度方式必须可复核、可复现并能保留失败摘要。

#### Scenario: 慢测试使用分区或并行池

- **WHEN** 测试命令为了降低耗时而使用分区、worker 池或串并行混合调度
- **THEN** 测试规则 MUST 说明分区数量、worker 来源、串行前置用例、失败停止策略和输出摘要要求
- **AND** 高风险互斥用例 SHOULD 串行运行后再进入并行池
- **AND** 失败输出 MUST 保留失败分区、命令、用例和关键错误摘要
