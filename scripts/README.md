---
title: 治理脚本执行说明
created_at: 2026-10-25 22:20:00
updated_at: '2026-11-01 00:11:44'
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

## Git 隐私扫描

运行 `bash scripts/project-python.sh scripts/git-check.py` 检查 staged 与 tracked 工作区内容。完整占位值及有限哈希、JSON 小数上下文见 `rules/security.md`；URL 同行内容仍检查，不使用目录豁免。环境变量允许完整变量引用、change-me 默认值或 Compose 必填提示；其他默认值仍检测。默认扫描保留现有 1 MiB 文本读取上限，并非 Git 历史审计或完整密钥识别器。

回归：`bash scripts/project-python.sh -c 'import pytest; raise SystemExit(pytest.main(["tests/unit/test_git_check.py", "tests/unit/test_verify_docker_media_upload.py", "-q"]))'`。新增例外时同时增加可排除样本和邻接真实值反例。

## 归档收尾判定

`bash scripts/project-python.sh scripts/check-archive-finalization.py --change change-id` 只读检查唯一归档目录、关联 Issue 与 Sprint 文档的普通导航及明确当前正文。历史字面路径和代码示例保留，历史章节里的真实链接仍检查；矛盾的当前事实阻断，历史与当前混杂列为 review，均不自动改文档。

CLI --finalize 在 sync/promote 后调用；产品协调器在 synced 后、completed 前调用，completed 重放也复核。driver.finalize 不重复执行此检查。中断保留原目录和 journal，已 synced 的重试仅验证，不重复合并或收尾写入。非 finalize 只报告 moved，检查失败不报告 finalized。历史 applied trace 的兼容事实沿用原恢复判定，不要求改写首次执行证据。

## 归档元数据恢复与跨迭代同步

已迁移归档的设计阶段 `acceptance.md` 若保留 `acceptance_status: not_started`，先运行 `bash scripts/project-python.sh scripts/restore-archive-metadata.py --change add-chat-isolated-acceptance-orchestration` 只读预检，再加 `--apply` 追加恢复记录。命令只在唯一归档、原恢复证明和完整验收证据通过时允许 `not_started` → `passed`，不覆盖失败/部分验收，不改原文或原恢复日志。

记录位于 `openspec/archive/.archive-recovery/metadata/`，绑定原文、原日志、交付输入投影、完整验收清单。重复运行无变化；绑定漂移须调查，禁止删记录后重试绕过检查。收尾检查每次验证记录和原证据，缺失记录不会豁免旧状态。此辅助命令不授予归档权限；已授权的归档继续使用 `archive-change.sh --finalize`，跳过已完成规格合并。

Workflow Sync 对当前 Sprint 和目标 Change 关联的 Issue 加载全部兄弟 Change，包括历史 Sprint；关联状态用于读取推导，不把兄弟纳入当前 Sprint。归档事件按关联成员同步子文档，不能因历史主 Change 不等于本次 Change 而跳过。收尾引用检查仅对裸路径按中文顿号断词，显式 Markdown 链接按原值验证。

归档文档保留的 Issue 旧阶段引用仅在唯一同名 Issue、完成状态、双向 Change 归属、全部关联已归档及原归档恢复证明通过时解析至 archive 目录。迁移预检按同一源文件模拟，迁移后按唯一归档文件校验；活动文档和可变 Issue 仍须修正旧链接。缺文件、符号链接、重复身份或证明失配均阻断。原型裸路径不包含紧接的中文说明，也不将 prototype 开头的普通文档名截成原型目录。

## 独立 Change 初始状态门禁

新建或复用活动 Change 后、进入实施前，运行 Workflow Sync 的 opsx.propose 事件并传入实际 Change ID。共享初始化器建立缺失的 trace.md，写入 proposed、execution.schema_version: 1、空 started_at/completed_at 和 last_event: opsx.propose。登记时间不冒充原始创建或执行时间。

已有合法状态和来源关联保持不变，包括旧版执行记录；非法状态、身份冲突、执行状态不一致及已有任务进度却缺失 trace 时阻断，先核实历史。dry-run 不写入，重复执行不回退状态。提案可暂未纳入 Sprint，但实施仍执行 Sprint 门禁。创建完成以有效状态记录为准，不能仅以 CLI 产物齐全或同步退出码为准。回归入口为 `bash scripts/project-python.sh scripts/test_change_initialization.py`。

## 独立归档工具包

`build-archive-tools.py --output` 生成新只读制品及 manifest 摘要，不安装或覆盖现有部署；`archive-tool-route.py --check` 只读核验固定部署配置。`archive_runtime.py` 分开工具导入目录与业务事实根，未启用路由保留原默认值。Shell 归档入口的 Python 脚本及内联导入均来自同一工具目录，原业务 cwd 保持不变。

回归入口：`src/backend/tests/test_archive_tools.py`、`scripts/test_archive_python_entry.py`。真实子容器验证入口 `verify-archive-tool-container.py` 要求先登记临时 Docker run，再提供 run、expires 和当前 Change 内输出路径；使用合成事实与已有镜像，不发送模型请求、不修改运行服务。验收结束按 temporary_docker cleanup/check 收尾。

关闭扫描仅在同一行识别到 Issue 编号时排除其完整原始标题中的状态词；标题之外的待实现、待归档和中间态仍阻断，不得因同行出现 done 而跳过整行。


## 证明绑定的归档收尾恢复

仅唯一已迁移归档、原恢复证明和完整验收有效时，可用 `scripts/restore-archive-finalization.py --change` 加目标Change ID预检；显式 `--apply` 排他追加恢复记录，随后续跑原 `archive-change.sh --finalize`。此入口仅投影proposal的初始proposed状态，以及已关闭且双向归属的来源Issue指向自身Change活动目录的旧导航。目标必须是唯一归档中的同一文件，未完成兄弟、未知路径、符号链接与失败状态不豁免。

记录保存在 `openspec/archive/.archive-recovery/finalization/`，绑定原始恢复日志、交付输入、完整通过清单、来源与目标字节。共享产品/CLI收尾检查每次重新验证，不改写原文、正式规格或原恢复日志；记录失配、并发变化及重复身份继续阻断，不删除或覆盖记录后重试。普通正文矛盾仍须处理，恢复记录不是新增验收或归档授权。历史导航的有效目的地可在恢复记录的projections查看，原文保留为历史输入。

归档前声明恢复：唯一归档trace的“验收结论”若包含完整句子“无正式归档授权，本次未归档”，同一恢复入口可追加绑定全文哈希、段落行号及完整验收的历史投影。仅消除此句冲突，同段失败、未知措辞、非目标文件/章节仍保留原门禁；原文与恢复证明不改写。

提案历史引用恢复：同一入口也支持proposal背景中的固定完整句式：Issue编号、归档同步后的验收声明引用及共享收尾误判说明。匹配限定整句并绑定全文，不豁免同句新增内容或相邻当前断言，未知措辞继续阻断。

### 独立 Change 分级回归

`bash scripts/project-python.sh scripts/test_change_classification_workflow.py` 在自动回收的临时仓库执行真实 OpenSpec CLI 与 opsx.propose，验证 fix/非 fix 分级完成、重试不改写和 pending 拒绝。评估由样本 Agent 材料给出，不调用产品 Chat、不创建正式业务样本。

## 来源追溯补充证明

原恢复证明绑定的来源trace因追加已关闭缺陷索引变化时，使用restore-archive-finalization.py的--original-trace提供原证明哈希匹配的原文，预检后加--apply。独立记录位于.archive-recovery/finalization/trace-supplements，保留原证明和当前文档。仅允许末尾关联缺陷表及updated_at变化，BUG需已关闭、反向关联且Change唯一归档；其他绑定、正文、证据或补证变化继续阻断。补证不能覆盖，不能代替验收或归档授权。
