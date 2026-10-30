---
title: 治理脚本执行说明
created_at: 2026-10-25 22:20:00
updated_at: 2026-10-29 06:53:30
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

## 临时 Docker 验证资源

`scripts/temporary_docker.py` 提供 register、check、cleanup、reap，统一通过 `bash scripts/project-python.sh` 调用。cleanup/reap 默认预览；显式 --apply 执行，check 有残留返回非零。reap 到期仍运行项返回 blocked，继续处理其他 run。详见 [生命周期契约](../docs/standards/temporary-docker-lifecycle.md)。回归：`bash scripts/project-python.sh scripts/test_temporary_docker.py`。仅登记资源进入清理范围，历史容器不自动补标签、不自动删除。

真实 Docker 回归：`bash scripts/project-python.sh scripts/smoke_temporary_docker.py --image moonbox-chat-executor:0.153.4-test`。镜像必须已存在，不拉取；样本无挂载、不访问业务服务，finally 精确清理。到期使用模拟时钟，Docker 创建与删除为真实操作。

## 探索改进契约验证

`bash scripts/project-python.sh scripts/validate-agent-context-budget.py` 包含 explore 反馈交接与评测入口静态检查。`bash scripts/project-python.sh scripts/test_explore_feedback_contract.py` 验证缺失契约、分类、版本及案例入口时会失败。两者不执行模型任务，不证明真实探索质量提升。

## 归档 Shell 解释器继承

`archive-change.sh` 在写入前调用现有 `project-python.sh -c` 获取经选择与预检的 `PYTHON_BIN`，随后导出并使用带引号的该变量运行全部 Python 命令；不再要求调用者临时调整 PATH。入口新增 `-c CODE` 与 `-` 标准输入执行，保留参数、stdin及退出码；解释器选择仍只有一处。预检只保证公共依赖，归档额外依赖失败仍由门禁阻断。

验证：`bash scripts/project-python.sh scripts/test_project_python.py`、`bash scripts/project-python.sh scripts/test_archive_python_entry.py`。后者使用真实 wrapper 与临时门禁/CLI替身，验证解释器选择、失败前无迁移、命令替换、heredoc及管道，不重放真实项目归档。中央上下文预算校验覆盖纳管归档 shell 的裸调用回退；词法检查不是任意 shell 的完整语法分析。

## Issue 生命周期阶段同步

`workflow_sync/issue_stage.py` 提供目录阶段与已有 Frontmatter 镜像的共享投影，供 `promote-issue-stage.py`、子文档同步和残留扫描使用。仅覆盖 trace、主文档、capture；不处理历史正文和其他语义状态。合法漂移可同步，非法字段先阻断。

定向归档漂移修复复用 `sync-workflow-status.py --reconcile-issue-status-residuals`：先带 `--dry-run --output detail` 检查路径、字段、目标与更新时间，再于授权范围内 `--apply-reconcile`。该分支不重放归档，不自动移动目录。规则见 `rules/issues-lifecycle.md` 第9节，回归见 `tests/unit/test_issue_lifecycle_stage.py`。

## Issue 迁移原型引用检查

`workflow_sync/prototype_references.py` 为 `promote-issue-stage.py` 和 `promote-issues-for-archive.py` 提供只读预检与实际迁移后复核。`--dry-run` 输出同一门禁诊断而不改写文件；`--check` 保持原有待迁移退出码语义。错误包含来源、行号、目标及 `existing-missing` / `migration-break` 分类。历史章节、示例、远程和动态引用为单独提示。有效引用失败返回非零，不自动修链接；后检失败保留目标目录，修复后重跑原命令复核。

检查限定当前 Issue、其关联 Change、所属 Sprint 及原型引用的仓库内 HTML/CSS 依赖。语法边界、历史标题和根路径提示见 [Issue 生命周期规则](../rules/issues-lifecycle.md#10-迁移原型引用门禁)。单元测试只用临时文件树，不迁移真实 Issue。

回归入口：`bash scripts/project-python.sh scripts/test_prototype_references.py`。
