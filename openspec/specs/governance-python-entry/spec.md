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

### Requirement: 归档 Shell 复用统一解释器
归档 Shell MUST 在副作用前经统一入口选择并预检解释器，将其通过 PYTHON_BIN 导出；脚本、命令替换、管道和内联代码均使用该解释器，不依赖 PATH 的裸 python。统一入口 MUST 保持 -c 与标准输入执行的参数、输入与退出码语义。
#### Scenario: PATH 中 Python 缺少项目依赖
- **WHEN** 项目解释器有效而 PATH 中的 python 不可用
- **THEN** 归档仍使用项目解释器，所有 Python 子调用继承选择
#### Scenario: 显式环境不可用
- **WHEN** PYTHON_BIN 无效或预检失败
- **THEN** 归档在门禁和目录写入前失败，不回退

### Requirement: 归档 Shell 解释器回退检查
治理校验 MUST 覆盖归档 Shell 的裸 python/python3 调用，并通过隔离执行验证命令替换、heredoc 与管道路径；不把静态扫描宣称为完整 Shell 解析。
#### Scenario: 内部调用回退
- **WHEN** 纳管归档脚本恢复裸 Python 调用
- **THEN** 校验失败，负向回归确认该失败可复现

