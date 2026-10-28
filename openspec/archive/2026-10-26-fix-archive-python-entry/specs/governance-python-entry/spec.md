---
title: 治理 Shell 统一解释器补充规格
created_at: 2026-10-26 12:55:09
updated_at: 2026-10-26 12:55:09
---

# 治理 Shell 统一解释器补充规格

## ADDED Requirements

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

