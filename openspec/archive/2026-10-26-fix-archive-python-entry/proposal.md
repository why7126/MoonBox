---
title: 归档脚本统一解释器接入修复
created_at: 2026-10-26 12:55:09
updated_at: 2026-10-26 12:55:09
---

# 归档脚本统一解释器接入修复

## 背景
承接已归档 unify-governance-python-entry。归档入口内部仍调用 PATH 中的 python，曾在验收门禁导入 sqlalchemy 时失败；临时 PATH 修正仅解决当次运行。现有校验只覆盖技能示例。
## 变更内容
复用 project-python.sh 选择与预检解释器，支持内联 -c/- 执行；归档入口在副作用前调用统一入口取得已验证解释器，导出 PYTHON_BIN，所有脚本、命令替换、管道、heredoc 使用该解释器。增加隔离归档执行与裸调用回退检查。
## 能力
### 修改能力
- governance-python-entry：补齐治理 shell 接入及检查。
## 影响
scripts、规则、说明和测试，无业务 API/DB/UI/安全权限/部署变化，不修改正式规格或重做统一入口。

