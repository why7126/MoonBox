# Chat独立执行容器

本目录用于REQ-0025受控测试，不是正式多租户发布配置。Dockerfile入口为src/backend/Dockerfile.chat-executor；从官方npm分发下载codex-cli 0.153.4对应Linux架构包，校验SHA-512，保留资源相对布局。镜像不包含凭证或用户工作区。

控制worker在宿主机以非root身份调用Docker；每次适配器创建独立容器，挂载单个/work和/runtime，.git二次只读挂载。容器使用控制用户UID/GID以兼容私有bind目录，无端口发布、无业务DB或Docker socket挂载；根只读、cap-drop ALL、no-new-privileges、1CPU/1GiB/128进程测试限制、禁用Docker协议日志副本。控制进程可连接模型服务，模型工具另由Codex权限禁止网络和/runtime、/proc读取。两层网络权限不同，不能把控制端联网描述为整个容器network=none。

seccomp-codex.json派生自Moby官方默认配置（https://github.com/moby/profiles/blob/main/seccomp/default.json），源码快照摘要见Change evidence/recommended-deployment/sandbox-profile.json，许可证见LICENSE.moby。保留默认拒绝动作和其余规则，额外允许clone/unshare/setns/mount/umount/umount2/pivot_root/chroot，使非特权用户命名空间中的bubblewrap能够建立沙箱。容器没有外层CAP_SYS_ADMIN或privileged权限；额外系统调用增加内核攻击面，不能据此声称达到虚拟机隔离强度。不同内核/运行时必须重新通过合成预检，不能改用seccomp=unconfined绕过失败。

persistent_container_server先以合成认证文件校验读写与严格只读配置，成功后才复制授权认证文件；已有运行目录仍重新预检。认证文件只在独立0700运行目录，模型工具不可读；原始登录文件不修改。容器销毁后运行目录保留以恢复同线程，整个隔离启动器结束后清除。宿主机崩溃后的目录回收和生产凭证轮换仍是独立未完成项。

启动和恢复备份命令见docs/02-deployment.md。正式共享平台认证、S3备份上传/异地保留和自动调度尚未启用。

Chat 持续保存不扩大执行容器权限。容器使用 `--memory 1g --memory-swap 1g --pids-limit 128 --cpus 1`，临时目录64MiB；超出保护时保留数据库已提交结果，运行状态按执行端证据确认，不能仅凭连接关闭宣布成功。容量测试与真实执行测试使用独立临时工作区，不能连接生产数据库。


BUG-0064恢复路径增加有限退避、独立槽及成功预检短缓存；普通执行仍执行原预检。控制器只转交受信Unix Docker endpoint，执行容器仍无socket。配置、运维续接和回滚见[部署说明](../../../docs/02-deployment.md#chat-未知轮次有界恢复bug-0064)。

## 专用 Python 验收镜像

`Dockerfile.verification-python`通过uv锁文件安装`verification`额外依赖，构建和运行探针均实际调用AnyIO线程池。该镜像用于受控验证，不向Chat执行器开放网络。Node依赖必须由项目锁文件和平台匹配的制品供应；组件测试需同时携带项目Vitest配置，不能把配置缺失误判为Rollup依赖故障。部署用实际镜像摘要固定身份。


`Dockerfile.verification-frontend`从已批准且固定摘要的Linux项目依赖镜像构建，要求`/app/src/web`包含目标平台node_modules及pnpm-lock.yaml。构建上下文为仓库根，`FRONTEND_DEPENDENCY_IMAGE`显式提供已校验摘要；依赖可来自现有Web构建阶段，不能复制宿主依赖。受控模板只声明`node /opt/moonbox/frontend-check.cjs`和批准的测试相对路径。入口逐字比对候选与制品锁文件，复制候选源码及Vitest配置到有限tmpfs，关闭Vitest缓存，根文件系统及依赖保持只读。Node版本、OS/架构和镜像摘要由验收模板及运行器检查；运行阶段不安装依赖。


浏览器进程文件上限与输出截图上限分别控制：进程使用128MiB文件上限及128MiB临时盘，截图仍逐个核验不超过10MiB。不能把10MiB截图配额套到浏览器全部文件，否则启动探针虽通过，实际页面加载仍可能关闭浏览器。此次单变量隔离复验证实调整该限制后同一页面及双浏览器检查通过；只读根、内部网络、内存和进程限制保持原约束。
