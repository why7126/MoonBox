---
title: 治理命令统一 Python 环境入口
created_at: 2026-10-25 22:20:00
updated_at: 2026-10-25 22:20:00
---

# 治理命令统一 Python 环境入口

## 背景
系统 Python 缺少 PyYAML 导致治理命令失败，项目环境可以执行。
## 变更内容
增加统一入口、写入前环境预检、继承契约和回归验证。
## 能力影响
### 新增能力
- governance-python-entry：治理 Python 环境选择与预检。
## 影响范围
仅治理脚本、技能和文档，不涉及业务 src。

