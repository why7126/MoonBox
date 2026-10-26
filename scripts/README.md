---
title: 治理脚本执行说明
created_at: 2026-10-25 22:20:00
updated_at: 2026-10-25 22:20:00
---

# 治理脚本执行说明

运行治理命令及 Agent 写入治理文档前，先执行：

```bash
bash scripts/project-python.sh --check
bash scripts/project-python.sh scripts/validate-sprint-selection.py
```

显式 `PYTHON_BIN` 优先，否则使用仓库 `src/backend/.venv/bin/python`。CI 或容器可设置 `PYTHON_BIN=python3`，前提是该环境已安装项目依赖。变量只接受可执行文件名或路径，不接受带参数的 shell 命令。无效配置、缺失环境、Python 低于3.12或缺 PyYAML 时退出2，不自动安装、不回退。依赖安装沿用后端项目环境准备流程，不向系统 Python 安装包。

`--check` 不执行目标、不修改文件；`--help` 查看入口说明。统一预检覆盖治理公共依赖，特定验证器的额外依赖仍由该命令负责。入口保留调用者工作目录，相对脚本路径按仓库根解析，脚本参数不改写。不要将需要相对仓库路径的参数误认为会自动转换。

Python 子命令使用 `[sys.executable, script, ...]`，shell 子命令使用导出的 `PYTHON_BIN`，禁止重新选择裸 `python`。从同一入口派生的子命令不重复选择环境。

回归：`bash scripts/project-python.sh scripts/test_project_python.py`。这验证本地入口与隔离环境，不代表已完成容器镜像或 CI 真实执行。
