## ADDED Requirements

### Requirement: Harness 学习同步技能

MoonBox MUST 提供 `/spec-study` 技能，用于学习其他项目的 Harness 工程，并在用户确认后将可复用治理经验应用到本项目。

#### Scenario: 默认自动学习

- **WHEN** 用户执行 `/spec-study <学习对象>` 且未指定学习模式
- **THEN** 系统 MUST 默认使用自动学习模式
- **AND** 系统 MUST 综合分析项目入口、全局规范、Agent 能力目录、脚本、部署与环境示例
- **AND** 系统 MUST 输出候选学习内容，等待用户确认后才能应用

#### Scenario: 指定学习内容

- **WHEN** 用户执行 `/spec-study <学习对象> --focus <内容>`
- **THEN** 系统 MUST 以指定主题为主线学习
- **AND** 系统 MUST 仍横向检查 `AGENTS.md`、`project.yaml`、`DOCUMENT_METADATA_INDEX.md`、`rules/`、`docs/`、Agent 目录、`scripts/`、部署与环境模块中的相关内容
- **AND** 系统 MUST NOT 只读取单一目录后得出迁移结论

#### Scenario: 学习对象只读保护

- **WHEN** 系统学习任何本地项目、临时克隆目录或远端快照
- **THEN** 系统 MUST 把学习对象作为外部只读输入
- **AND** 系统 MUST NOT 在学习对象路径下运行安装依赖、格式化、迁移、生成、测试修复、提交、分支、清理或重置命令
- **AND** 学习报告 MUST 说明学习对象只读保护结果

#### Scenario: 应用前用户确认

- **WHEN** 系统完成学习阶段
- **THEN** 系统 MUST 告知用户学习到了哪些内容建议应用到本项目
- **AND** 系统 MUST 列出每项内容的理由、风险、拟更新目标文件和是否需要 OpenSpec/Sprint 承载
- **AND** 系统 MUST 等待用户确认学习内容，不得默认直接应用

#### Scenario: 确认后应用到本项目治理资产

- **WHEN** 用户确认应用某些学习内容
- **THEN** 系统 MUST 通过当前项目的 OpenSpec Change 和 Sprint Inclusion Gate 承载变更
- **AND** 系统 MAY 更新 `.agents/skills/`、`AGENTS.md`、`rules/`、`docs/`、`scripts/`、部署治理文件和 active Change 文档
- **AND** 系统 MUST NOT 修改 `src/` 目录下任何业务运行时代码

#### Scenario: 输出学习报告

- **WHEN** 系统完成应用阶段
- **THEN** 系统 MUST 输出学习报告
- **AND** 学习报告 MUST 写入 `docs/spec-logs/YYYYMMDDhhmmss-study-xxx.md`
- **AND** `YYYYMMDDhhmmss` MUST 使用报告生成时刻的 `Asia/Shanghai` 日期时间，精确到秒
- **AND** `xxx` MUST 使用小写 kebab-case 表达学习对象或主题
- **AND** 学习报告 MUST 包含学习对象、学习模式、采纳内容、未采纳内容、更新文件、验证结果和后续建议
