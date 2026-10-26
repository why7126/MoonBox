# governance-python-entry Specification

## Purpose
TBD - created by archiving change unify-governance-python-entry. Update Purpose after archive.
## Requirements
### Requirement: 治理解释器选择与预检
入口 MUST 优先使用显式 PYTHON_BIN，否则使用项目虚拟环境，检查 Python >=3.12 和 PyYAML，不隐式回退或自动安装。

#### Scenario: 环境不满足要求
- **WHEN** 环境缺失、版本不足或依赖缺失
- **THEN** 在目标写入前明确诊断并失败

#### Scenario: 环境满足要求
- **WHEN** 预检成功
- **THEN** 参数原样传递，子进程继承解释器并保留退出码

### Requirement: 技能入口一致性
技能 MUST 使用统一入口运行治理脚本，Python 子命令使用 sys.executable。

#### Scenario: 示例回退
- **WHEN** 技能出现裸 python 调用治理脚本
- **THEN** 校验报告失败

