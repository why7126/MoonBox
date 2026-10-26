---
title: 治理 Python 入口设计
created_at: 2026-10-25 22:20:00
updated_at: 2026-10-25 22:20:00
---

# 治理 Python 入口设计

## 方案
显式 PYTHON_BIN 优先，否则使用 src/backend/.venv/bin/python，不隐式回退系统环境。CI 和容器显式选择自身 Python。版本至少3.12，统一治理依赖基线为 PyYAML；专用命令仍负责额外依赖检查。
## 执行边界
bash 启动器计算仓库路径，保留调用工作目录，参数原样传递。--check 仅预检；Agent 直接写文档前也先执行预检。导出 PYTHON_BIN，Python 子命令沿用 sys.executable。exec 保留目标退出码，不安装依赖。
## 验证
隔离临时仓库覆盖缺失/错误环境、版本、缺依赖、含空格路径、参数、退出码、子进程和非根工作目录。

