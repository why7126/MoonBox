---
bug_id: BUG-0045-chat-acceptance-runtime-capability-gap
title: Chat 验收运行能力缺口根因分析
created_at: '2026-10-19 11:38:11'
updated_at: '2026-10-19 11:38:11'
owner: 产品团队
status: confirmed
---

# Chat 验收运行能力缺口根因分析

## 根因状态

status: confirmed

确认范围为当前本地部署的能力供应、验证服务配置及 Chat 启动预检缺口，不覆盖历史 AnyIO 超时和全部部署版本。证据复用 2026-10-19 同会话 bug-explore 的实际只读检查；本次文档完善未重新发起业务命令。

## 现象

产品 Chat 可以开始开发，但 apply 到测试与视觉验收时发现依赖/浏览器不可用，最终停在4/10并要求外部测试环境。后续桌面补验与 BUG-0028 归档属于不同执行环境，不构成本缺陷修复。

## 证据链

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

## 已确认根因

1. 执行器镜像安装基础 CLI 和业务 Python 依赖，未提供本项目所需 pytest/httpx 及浏览器。其可执行开发命令与可完成验收是两种能力。
2. 已有专用验证服务在当前部署未启用：没有验证 worker，必要镜像/版本/架构配置缺失，目标项目没有验证子目录和测试入口配置。预检默认查仓库根，返回 package_manifest_invalid。
3. Chat 启动路径检查权限和基础工具，未调用独立项目验证预检，因此这些缺口没有作为任务能力限制在开始前暴露；独立 API 存在不代表命令已接入它。
4. 工具网络禁用、个人配置不继承是既有隔离边界，导致宿主浏览器和联网补装无法作为默认补救。这些安全边界本身不应因本缺陷被撤销。

## 已排除假设

| 假设 | 排除证据 |
|---|---|
| 整个产品无法访问导致验收中断 | E1 刷新后正常加载；E6 服务端同项目返回结构化诊断 |
| 助手凭空声称缺少能力 | E2 镜像直接探测与 E3 构建声明一致 |
| 只提供测试 URL 即可解决 | E2/E5 缺少测试依赖、worker与版本配置，URL 不补齐这些能力 |
| 桌面验证成功已经修复产品执行器 | E2/E5/E6 当前产品能力缺口仍存在，环境不同 |

## 未确认的附随问题

历史 AnyIO 线程池超时、Rollup 原生依赖失败的具体机制未确认。它们不作为上述根因成立的前提；环境准备后纳入验收探针，若仍失败继续最小化定位，禁止将它们伪报为已解决。执行中问答由 BUG-0046、结果状态展示由 REQ-0046、阶段/并发门禁由 BUG-0044 独立闭环。

## 修复方向

复用 REQ-0044-shared-project-verification-environment 的专用 runner/worker，补齐部署配置和 monorepo 项目绑定，分别供应目标平台前端依赖与 Python 测试环境。通过受控任务调用和证据回传接入 Chat，开始前按任务声明区分所需能力；缺失能力只阻断依赖任务，保留可独立工作与续接检查点。不要挂载个人配置、认证信息或开放任意网络来规避。

## 验证闭环

现有闭环是历史失败 → 镜像直接缺失探测 → 同项目预检失败 → 构建/部署/启动路径对应；足以确认当前缺口。修复后的成功闭环尚未执行，以 acceptance.md 的完整/缺失能力矩阵、真实命令轮次与浏览器证据为准。

## 数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: Chat、验证 API、请求日志、Task Trace。validation：将能力预检、验证任务与对应轮次关联，证据仅保留状态、稳定错误码、版本和脱敏摘要。本次文档不修改 API/DB/部署/客户端/采集保留策略，以上变更 N/A。
