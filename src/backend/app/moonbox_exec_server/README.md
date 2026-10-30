# moonbox-exec-server

执行资源适配边界，当前继续使用既有 Chat 容器执行器。

`runtime.py` 在模型开始前保存实际不可变镜像 digest、工具版本及权限配置摘要；恢复复核原版本，默认镜像更新不改变活动轮次。`scope.py` 共用采集范围和权限边界；`git_view.py` 为 linked worktree 构建只读、仅含当前 HEAD 可达对象的私有 Git 视图，不挂载共享 Git 管理目录或其他分支对象。工具进程没有凭证 HOME，网络继续受原沙箱限制。

`validation.py` 是固定候选组合环境的可信供应接口。已接入 verification.candidate 供应器；只有部署批准的不可变模板才可启用。供应器验证精确候选的独立 SQLite/MySQL 8.4、应用与浏览器，清理确认后返回受信证据；未配置时仍失败关闭。测试注入的 SyntheticValidator 仅用于回归，不进入生产配置。

本机 probe 仅供既有隔离测试；新托管工作区要求不可变容器运行版本，不能用本机进程绕过该检查。
