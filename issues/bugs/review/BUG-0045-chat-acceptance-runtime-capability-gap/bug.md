---
bug_id: BUG-0045-chat-acceptance-runtime-capability-gap
title: Chat 命令执行环境缺少验收能力导致开发验收中断
severity: high
status: approved
owner: 产品团队
created_at: '2026-10-19 11:34:07'
updated_at: 2026-10-21 16:24:33
discovered_at: '2026-10-19 10:45:24'
environment: 本地 Docker Chat 平台；执行器 moonbox-chat-executor:0.153.4-test，Linux aarch64
related_requirement: REQ-0025-chat-workbench
related_bug: BUG-0046-chat-midrun-question-response-unavailable
related_change: null
lifecycle_stage: plan
---

# Chat 命令执行环境缺少验收能力导致开发验收中断

## 现象

产品 Chat 执行 `/opsx-apply BUG-0028-requirement-center-card-owner-raw-user-id` 时，可以实现部分代码并运行部分静态检查，但到组件、HTTP 和视觉验收时才暴露测试依赖与浏览器缺失。助手要求用户提供授权测试环境，最终报告任务仅完成 4/10、真实产品及视觉验收未完成。用户需要在桌面环境续接，无法在产品执行链路内完成开发验收闭环。

2026-10-19 同会话探索已刷新浏览器，确认产品当前可访问、历史 apply 轮次保留上述阻塞结果；后续 BUG-0028 已由桌面补验并在产品归档。这不代表产品执行器的验收能力已修复，也不应将历史 4/10 当作 BUG-0028 当前进度。

## 复现步骤

1. 使用本地产品 Chat 中已获授权、具备 Sprint 与 Change 的对象会话；历史来源是 BUG-0028、fix-requirement-center-owner-display、sprint-010。
2. 执行需要 Python 接口测试、前端组件测试和浏览器验收的 apply 命令。已归档的 BUG-0028 只用于读取历史证据，不重复执行写入命令；后续动态复现使用独立授权样本。
3. 对比命令开始时的执行器就绪检查与实际验收要求，观察实施阶段是否成功，而验证阶段因缺失依赖或浏览器中断。
4. 对实际执行器镜像执行无网络、只读、无项目/凭证挂载的模块和可执行文件检查，核对 pytest、httpx、Playwright、Chromium/Firefox。
5. 在同一授权项目执行只读验证环境预检，同时检查验证 worker 是否存在、必要配置是否设置及项目子目录绑定是否正确。只返回状态、布尔值和稳定错误码，不输出凭证或真实路径。

## 期望与实际

| 检查点 | 期望 | 实际证据 |
|---|---|---|
| 执行前能力检查 | 按命令/项目要求区分基础执行、Python 测试、前端测试与浏览器验收能力 | 基础工具预检通过不代表测试/浏览器就绪，实际缺口在中途出现 |
| Python 测试 | 有锁定且可执行的项目测试依赖 | 当前镜像 pytest、httpx 不可导入；业务 SQLAlchemy 可导入 |
| 浏览器验收 | 经受控验证服务启动浏览器、访问授权目标并回传证据 | 当前镜像无 Playwright 模块和常见浏览器入口，专用验证 worker 未部署 |
| 项目环境识别 | monorepo 使用正确子目录和版本匹配的依赖制品 | 未设置 verification_project_subdir，默认仓库根；实际前端位于 src/web，同项目预检返回 package_manifest_invalid |
| 恢复与续接 | 缺口前置可见，可独立工作继续，阻塞恢复后从检查点续接 | 本例转入请求用户提供外部环境，最终未在产品内完成验收 |

## 影响范围与严重等级

严重度 high：阻断产品核心开发至验收链路，增加人工跨环境续接成本；依赖浏览器、完整 Python 测试或平台匹配前端依赖的命令均可能受影响。已确认范围为当前本地 Chat 部署及目标项目；其他部署、镜像版本、全部命令尚未逐项验证，不泛化为全平台不可用。没有已证实的数据丢失、覆盖或安全事故，建议常规 fix，不采用解除隔离的紧急绕过。

## 证据链与根因摘要

根因状态：confirmed，限于下列验收能力供应、部署配置和预检契约缺口。证据承接同会话 bug-explore 的直接运行结果，不把建议写成已实现。

| 编号 | 类型 | 来源与复核位置 | 脱敏结果与支持的判断 |
|---|---|---|---|
| E1 | reproduction | 2026-10-19 Chrome 产品 /chat，目标对象历史 apply 轮次，刷新后观察 | 页面恢复已连接；apply 正文报告 4/10、依赖/浏览器阻塞。排除当前产品整体不可达 |
| E2 | test_failure | 当前 moonbox-chat-executor:0.153.4-test 镜像，无网络只读诊断；importlib.util.find_spec 与 shutil.which | Linux aarch64；pytest/httpx/playwright=false，sqlalchemy=true；chromium/chromium-browser/firefox 均无入口。确认不是仅模型推测 |
| E3 | code_path | src/backend/Dockerfile.chat-executor；src/backend/pyproject.toml | 镜像安装业务项目依赖与基础工具，项目 dependencies 未包含 pytest/httpx；未安装浏览器运行时 |
| E4 | code_path | src/backend/container/check_toolchain.py；src/backend/app/chat/container_server.py 的 verify_toolchain、write_profiles | 预检枚举基础 CLI，不验证项目测试依赖或浏览器；工具网络禁用、不导入个人配置，宿主能力不能自动继承 |
| E5 | config_diff | 当前 Docker 容器清单及 chat-worker 配置存在性只读检查 | 无 verification worker 容器；验证镜像、Node/pnpm 版本、架构及准备网络配置未设置；验证 worker 源文件存在不等于服务已部署 |
| E6 | data_sample | 当前后端对同一对象会话项目调用 app.verification.service.inspect_authorized | status=unavailable、reason_code=package_manifest_invalid；项目子目录、目标 URL、selectors、steps 未配置。未输出用户标识或真实路径 |
| E7 | code_path | src/backend/app/verification/service.py 的 _project_root；仓库 package.json 与 src/web/package.json 存在性；docs/02-deployment.md 验证环境部署节 | 默认子目录为点号，根目录无 package.json、src/web 有；部署文档要求显式配置并启用 verification profile，解释 E6 |
| E8 | code_path | src/backend/app/chat/execution.py 执行路径；src/backend/app/chat/api.py verification 端点 | 验证服务有独立 API；已检查的 Chat 启动链路未调用项目验收预检，不能把 API 存在视为 apply 已自动接入 |

因果链：基础执行器就绪 → 命令可开始开发 → 所需测试依赖未供应、独立验证服务未启用且项目绑定未配置 → 启动链路没有暴露这些能力缺口 → 实施中途验证失败并请求外部环境。此处“确认”不表示单一代码行能解释所有历史失败。

## 已排除与仍需区分的判断

- 产品整体不可达：刷新浏览器成功且同项目只读服务预检返回结构化诊断，排除该解释。
- 只需提供一个测试 URL：不足；测试依赖、浏览器服务、项目绑定和版本配置仍缺失。
- 桌面验收通过等于产品修复：不成立，两者执行环境不同。
- 历史 AnyIO 线程池超时：具体原因未确认，不能归因到同一已确认缺口；后续准备测试环境时独立验证最小线程探针，若仍失败再定位权限/资源/运行时。
- 历史 Rollup 原生依赖失败：需要在目标 OS/架构及锁文件下复验，当前不确认具体包版本或安装错误根因。
- 中途问题无法回答由 BUG-0046 独立闭环；运行结束与任务完成的展示由 REQ-0046 承接；阶段过早迁移/并发由 BUG-0044 处理。

## 修复方向与建议验收

优先复用已有 REQ-0044-shared-project-verification-environment 的专用验证服务，核对其实现和当前部署的差距，不另造浏览器系统。配置版本固定的 runner、项目 src/web 子目录、授权目标及受控网络；补齐独立 Python 测试环境和目标平台前端依赖。通过受授权任务调用与结果回传接入 Chat，并在开发前输出能力矩阵；局部阻塞仅影响依赖该能力的任务。

验收覆盖：依赖完整/缺失、worker 缺失、错误子目录、镜像/锁文件/架构不匹配、目标不可达、浏览器启动失败；失败项准确定位并可恢复。完整环境下分别完成 Python、组件和真实浏览器验证，证据关联当前项目与任务。维持无凭证挂载、空间隔离和受控网络，不直接开放执行器联网，不依赖个人浏览器配置，不将静态或合成检查冒充视觉通过。

## 关联与交付边界

关联父需求 REQ-0025-chat-workbench；已有验证能力来源 REQ-0044-shared-project-verification-environment；复现来源 BUG-0028。来源 Sprint/Change 不继承为本缺陷计划。本次仅生成主文档，未评审、未纳入 Sprint、未创建 Change、未修复或部署。

## 数据采集与链路观测

product_data_collection_observability: applicable

affected_layers: Chat 执行器、验证任务 API、Web 能力反馈、请求日志与 Task Trace 关联。

validation: 后续按空间/项目/轮次/验证任务核对能力预检、阻塞原因、续接和证据关联，记录版本、耗时、计数及稳定错误码，不记录 Prompt、认证信息或真实宿主路径。本轮仅文档生成，API/DB schema、客户端生成、部署、对象存储和采集保留策略变更均 N/A；正式修复按实际影响重新评估。
