# Chat独立执行容器

本目录用于REQ-0025受控测试，不是正式多租户发布配置。Dockerfile入口为src/backend/Dockerfile.chat-executor；从官方npm分发下载codex-cli 0.153.4对应Linux架构包，校验SHA-512，保留资源相对布局。镜像不包含凭证或用户工作区。

控制worker在宿主机以非root身份调用Docker；每次适配器创建独立容器，挂载单个/work和/runtime，.git二次只读挂载。容器使用控制用户UID/GID以兼容私有bind目录，无端口发布、无业务DB或Docker socket挂载；根只读、cap-drop ALL、no-new-privileges、1CPU/1GiB/128进程测试限制、禁用Docker协议日志副本。控制进程可连接模型服务，模型工具另由Codex权限禁止网络和/runtime、/proc读取。两层网络权限不同，不能把控制端联网描述为整个容器network=none。

seccomp-codex.json派生自Moby官方默认配置（https://github.com/moby/profiles/blob/main/seccomp/default.json），源码快照摘要见Change evidence/recommended-deployment/sandbox-profile.json，许可证见LICENSE.moby。保留默认拒绝动作和其余规则，额外允许clone/unshare/setns/mount/umount/umount2/pivot_root/chroot，使非特权用户命名空间中的bubblewrap能够建立沙箱。容器没有外层CAP_SYS_ADMIN或privileged权限；额外系统调用增加内核攻击面，不能据此声称达到虚拟机隔离强度。不同内核/运行时必须重新通过合成预检，不能改用seccomp=unconfined绕过失败。

persistent_container_server先以合成认证文件校验读写与严格只读配置，成功后才复制授权认证文件；已有运行目录仍重新预检。认证文件只在独立0700运行目录，模型工具不可读；原始登录文件不修改。容器销毁后运行目录保留以恢复同线程，整个隔离启动器结束后清除。宿主机崩溃后的目录回收和生产凭证轮换仍是独立未完成项。

启动和恢复备份命令见docs/02-deployment.md。正式共享平台认证、S3备份上传/异地保留和自动调度尚未启用。
