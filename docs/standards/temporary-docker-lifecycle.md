---
title: 临时 Docker 验证资源生命周期
created_at: 2026-10-26 12:09:45
updated_at: 2026-10-26 12:09:45
---

# 临时 Docker 验证资源生命周期

## 范围与默认策略

本契约约束 Agent 在测试、返修、验收中临时创建的 Docker 容器与专属网络。正式 MoonBox 服务、Chat 运行时容器、数据库、对象存储、历史未登记环境不自动纳入。默认4小时，最长24小时；正常完成立即清理，不以未到期为理由保留。

任务入口运行 `bash scripts/project-python.sh scripts/temporary_docker.py reap` 预览；确认属于过期且停止的登记资源后运行同命令加 `--apply`。运行中到期项、跨 daemon、标签不符、损坏台账、卷或外部网络连接返回阻断，继续独立项。没有后台守护或系统定时器，回收由任务入口、结束或人工显式运行触发；无人调用时不承诺按时删除。需要常驻调度应另行明确执行环境及授权。

## 创建前登记

使用 `register --change` 传当前 active Change ID，`--purpose` 取 test、acceptance、repair、smoke，必要时传 `--ttl-hours`。只登记受当前任务授权的独立验证环境。输出 JSON 包含 run、expires、labels，保留 run 供清理使用，不复制真实环境文件或凭据。

每个容器和专属网络必须带全部三标签：`moonbox.temp.managed=true`、`moonbox.temp.run`、`moonbox.temp.expires`，值使用登记结果，不自行猜测。登记先于 docker create/run 或 compose up，创建失败仍须对原 run 收尾。容器建议 --rm，临时 Compose 使用独占 project 和 restart: no；services 与 networks 各自配置 labels。不得复用正式项目名；不得创建匿名或命名卷，使用受控临时 bind 目录或 tmpfs，宿主目录单独保留与管理。镜像、构建缓存、卷不在本脚本回收范围。

## 正常结束、失败与取消

1. 停止创建资源；完成仍依赖该环境的验证，保存必要脱敏证据。
2. 执行 cleanup --run 指定 run 预览，确认范围后追加 --apply。该动作可以停止本 run 的运行容器，不能与仍在执行的验证并行。
3. 执行 check --run 指定 run；返回 clean 且退出0才可报告零残留。网络在容器之后删除，失败保留台账便于重试。
4. 容器进程退出、docker stop、Compose stop 和任务显示完成均不等于资源删除。禁止全局 prune、按 moonbox 前缀删除、down -v 或自动删除 bind 路径。

在可控 shell 中用 trap/finally 调用同 run 清理，并在 Agent 最终回复前复核；SIGKILL、断电、宿主崩溃不能依赖 trap，后续入口 reap 兜底。不承诺工具本身能拦截所有任意 shell 创建动作；Agent 必须遵守先登记加标签契约。

## 异常保留与到期

排障现场确需保留时，在 Change trace 写入脱敏 run、理由、责任任务、到期时间及精确 cleanup/check 命令，报告“保留待回收”；期限不可无限延长。保留不等同清理通过，未清理项在完成报告单列。到期已停止资源可 reap --apply；到期仍运行项先核查任务是否结束，确认后对明确 run 执行 cleanup --apply。不能仅凭时间或名称强杀。

原任务中断后先查台账与现有资源，再决定复用或回收；若缺登记/标签，人工确认归属与数据保护后另行清理，脚本不自动补登记或接管。跨 Docker daemon 不同环境分别处理，不修改 daemon 哈希绕过门禁。

## 完成与验收证据

记录创建前登记、创建时标签、结束清理结果及 check 状态；只保留计数与脱敏结论。回归覆盖预览不删除、正常与取消清理、重复清理、到期停止回收、到期运行拒绝、跨 daemon、错标签、卷、外部网络、Docker 故障和损坏台账。真实 Docker 样本必须自身登记并最终 check 为 clean；模拟回归不能替代真实清理证据。
