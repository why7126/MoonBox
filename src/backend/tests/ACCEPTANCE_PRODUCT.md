---
title: 本机 MoonBox 隔离产品验收
created_at: 2026-10-30 10:30:00
updated_at: 2026-10-30 11:00:00
---

# 本机 MoonBox 隔离产品验收

此入口用于 REQ-0048 的本机验收，明确禁止连接生产。当前仅验证 Linux arm64。使用全新 SQLite、专属 MySQL 8.4 容器、短期随机账号、真实 MoonBox 登录与空间权限；对象存储指向不可达本机端点，不复制业务数据库或真实账号。测试启动器在仓库外创建权限 0700 的独立目录，批准模板为 0600。

## 环境准备

先按 `docs/standards/temporary-docker-lifecycle.md` 登记 run，将登记返回值设置为 `MOONBOX_TEMP_RUN`、`MOONBOX_TEMP_EXPIRES`。核对 Docker 网络后设置未占用的 `MOONBOX_ACCEPTANCE_SUBNET`，仅接受 RFC1918 的 /24 至 /28 网段；不要删除其他任务网络。

需要本机已有镜像 `moonbox-backend:local`、`moonbox-verification:req0048-synthetic`、`mysql:8.4`、`node:24-trixie-slim`。双浏览器基础镜像需要 Chromium 和 Firefox；缺镜像或版本不符直接阻断，不静默下载或改用宿主浏览器。先在 `src/web` 执行 `npm run build`，再从仓库根执行：

```bash
export MOONBOX_PRODUCT_ACCEPTANCE_LIVE=1
PYTHONPATH=src/backend:src/backend/tests bash scripts/project-python.sh src/backend/tests/acceptance_product_images.py
PYTHONPATH=src/backend:src/backend/tests bash scripts/project-python.sh src/backend/tests/acceptance_product_live.py
```

镜像覆盖层仅复制当前 Web 制品和浏览器适配器；构建禁止网络及拉取。运行器将实际镜像 ID 写入批准模板，并核对 Python 3.12.15、Node 24.22.0、MySQL 8.4.13、Chromium 156.0.8078.73、Firefox 153.0。版本升级需要重验，不能只修改预期字符串绕过核对。

启动器输出本次独立目录和结果。目录内 `template.json` 即当前 MoonBox 的本机验收配置，`activate.sh` 指定模板、独立运行目录与子网。不要将它加载进生产服务；同一验收服务的 API 和 worker 使用同一份配置。模板包含实际源码摘要、迁移、种子、角色签发/撤销、登录和逐项命令。

## 真实 Chat 与模型

将刚输出的独立目录设置为 `MOONBOX_PRODUCT_PREPARED`，选择另一个无冲突子网，然后执行：

```bash
PYTHONPATH=src/backend:src/backend/tests bash scripts/project-python.sh src/backend/tests/acceptance_chat_live.py
```

此入口创建全新控制数据库、仓库副本、工作区和 Chat，并监听 `127.0.0.1:39048`。它使用当前已登录 Codex 的授权运行真实模型，临时复制认证文件到私有目录，并在退出时删除；凭证不进入产品源码、验收容器或公开证据。浏览器登录信息仅在本次目录的 `browser.json` 中，不能提交或复制进报告。

输入 `restart` 重启本次 worker，输入 `cleanup` 停止本次 API/worker 并删除临时模型认证。测试调度调用真实领取、回收扫描、恢复、一次结果投递和长期摘要接口。`observe-stages` 文件可启用最长 90 秒的阶段观察屏障，删除对应 `observing-*` 标记继续；屏障只延迟调度，不改写产品状态或检查结果。

`acceptance_chat_scenario.py` 提供 `executor-loss`、`application-loss`、`cleanup-failure`、`visual-stages`、`failed-source` 故障/观察入口，需要设置本次 `MOONBOX_CHAT_TEST_ROOT`。容器故障仅操作经 run 标签确认的本次资源。`failed-source` 只损坏新建测试轮次的私有执行记录，由真实完成守卫生成失败终态，再经 API 发起验收并观察关联模型续接；不直接修改终态或用量。清理失败场景的临时 peer 移除后，通过页面“重试清理”验证同一尝试回收，不重新验收。`pause-reconcile` 文件最长延迟回收扫描 90 秒，仅供观察真实回收中状态。

正式逐项验收支持 `isolated_acceptance_v1` 证据类型，从显式授权的本机控制数据库只读核对原生工具确认、尝试身份、原轮次终态、文件归集、结果及回收，关联续接还核对同会话、一次计数和原预算。它不再要求原生工具调用产生 shell 命令。未知或缺失事实仍拒绝签认。

最后对登记的精确 run 执行 cleanup 与 check，保留脱敏报告。不要执行全局容器删除。原始数据库、认证、账号文件和私有诊断日志不得进入仓库；只转存白名单字段、必要截图与哈希。

## 证据限制

产品矩阵的控制请求由测试入口创建，不能替代真实 Chat 轮次。Chat 样本使用真实工具协议与产品状态；阶段观察屏障是测试调度条件，应随证据声明。执行器被终止后若权威记录为 interrupted，产品标记 stopped 且拒绝自动续接；不能把它算作 failed 轮次自动续接通过。源轮次失败、执行关闭、文件归集、用量、权限和剩余预算均确认后，才允许最多一次关联续接。


## 账号与数据库补充检查

适配器在私有状态目录记录临时账号截止时间，每次实际应用请求前撤销到期会话并冻结到期账号。矩阵使用独立短期账号验证到期后重新登录401，另验证普通会话过期401、后台越权403、只读写入与跨空间拒绝。数据库检查包括JSON、排序/分页、保存点回滚；MySQL追加字符集/排序规则/UTC。SQLite探针在HTTP登录之前释放自己的事务，避免验收脚本锁住登录会话写入。

`MOONBOX_PRODUCT_SPACE=space-2` 可选择另一个独立空间绑定；每次运行新建控制器，不能据此宣称同一共享账本的并发测试。共享账本竞争由登记MySQL测试和集中事务回归覆盖。`acceptance_chat_scenario.py revocation` 仅冻结一次性测试用户作为真实撤权输入，不注入执行终态；随后检查资源释放和无关联续接。


## BUG-0045 运行能力复验

`MOONBOX_PRODUCT_TEST_IMAGES`和`MOONBOX_PRODUCT_TEST_VERSIONS`接受测试专用JSON映射，显式选择本机已检查的Python、MySQL、浏览器和Node镜像及实际版本；运行器仍核验不可变摘要和真实版本。`MOONBOX_PRODUCT_TEST_FRONTEND=1`额外复制当前Web源码、锁文件与Vitest配置，并添加受控组件测试入口。Python锁文件固定为uv.lock。覆盖参数仅用于本机合成验收，不更改正式配置。

`MOONBOX_PRODUCT_RUNTIME_PREFLIGHT=1`让Chat样本启动真实verification worker，使用正确src/web绑定及实际浏览器探针版本；原测试循环不再自行调度验收。该模式的worker心跳、Python探针和验收结果均来自产品实现。旧验证通道未准备制品或绑定外部目标时仍显示未就绪，不能因此伪报隔离模板不可用；隔离模板的实际结果单独记录。
