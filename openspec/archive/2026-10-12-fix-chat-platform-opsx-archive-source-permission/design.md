---
title: Chat 平台 source 工作区归档权限与状态诊断修复
created_at: '2026-10-04 11:17:53'
updated_at: 2026-10-10 07:21:24
---

# Chat 平台 source 工作区归档权限与状态诊断修复

## 设计概述

修复分为三层：部署层让 trusted source root 对 worker 可写；权限层把 archive 写入从普通治理写入中拆成单独 write scope；执行层把未启动外部 turn 的 setup 失败终结为 failed，并保留可诊断错误码。

## 权限模型

新增 `archive_write` 写入范围，仅在当前对象满足可写治理事实、用户发送的是 `/opsx-archive <完整 REQ 或 BUG ID>` 且对象关联 Change 可归档时使用。执行容器映射到 `moonbox-archive` permission profile：

- `/work/issues` 可写，用于 Issue archive promote 与 trace 同步。
- `/work/iterations` 可写，用于 Sprint/iteration 投影同步。
- `/work/openspec/changes` 可写，用于 active Change 移除和残留校验。
- `/work/openspec/specs` 可写，用于 OpenSpec archive 合并生效规格。
- `/work/openspec/archive` 可写，用于 canonical archive 目录。
- `/work/docs/spec-logs` 可写，用于治理日志。
- `.git` 继续只读，网络继续禁用。

普通 `governance_write` 不增加 `openspec/specs` 或 `openspec/archive` 写入权限。

## source 工作区部署

`chat-worker` 在本地 source 模式中负责启动执行容器并把 source root 绑定到 `/work`。因此 worker 宿主挂载必须可写；backend 保持只读读取事实源与投影。执行容器是否能写入仍由 Codex sandbox profile 决定，避免把 Docker volume 可写等同于无限制写权限。

## 状态诊断

`run_claim` 在外部 executor turn 创建前发生的 `WorkspaceError`、`ExecutorError` 或受控 `ChatError` 应更新 turn 为 `failed`，写入脱敏错误码并释放会话占用。只有外部 turn 已创建但终态不可确认时，才保留 `unknown` 以便后续 `reconcile_unknown` 读取执行器权威状态。

`platform_worker` 外层 setup 兜底也应优先使用 failed 语义，确保没有 executor turn id 的失败不会永久占用会话。

## Change 身份校验

`scripts/change_identity.py` 继续校验 active 与 archive Change ID 唯一性，但忽略 `openspec/changes` 与 `openspec/archive` 下一层隐藏系统目录，例如 `.git`、`.agents`、`.codex` 和 `.DS_Store`。隐藏目录不是 Change 身份，不参与 ID 格式校验或重复判断。

## 验证策略

### 执行环境目录校验

Chat executor 的私有配置给命令沙箱注入 `MOONBOX_CHAT_TOOL_SANDBOX=1`。目录校验只在该标记、根为 `/work`、已知写入根目录下的 `.agents`、`.codex` 精确路径为空且非符号链接时给出警告。`shell_environment_policy.inherit="none"` 会移除 `CODEX_HOME`，不能依赖它；真实执行曾在宿主留下空目录，设备号和挂载点状态不稳定。worker 在写入型轮次前后递归检查仓库自有目录并清理空残留，非空目录、文件、符号链接继续阻断；不进入 Git 元数据、虚拟环境、依赖、构建缓存和运行数据目录。标准脚本保留移动前预校验、移动后校验和唯一 archive 续跑门禁。除根目录 `.agents` 外，全仓目录校验拒绝其他工具路径。本次新发现的八个目录具有直接文件系统证据，具体创建轮次仍待隔离复现。

### 归档迁移与恢复

产品仍从需求中心跳转对象 Chat 并填入归档 prompt。执行 prompt 追加标准脚本约束，优先 `bash scripts/archive-change.sh CHANGE_ID --finalize`。跨挂载目录迁移使用 `shutil.move`，不使用 `Path.rename`；CLI 不可用时仅允许技能定义的 delta 自检与合并后安全移动，再进入同一脚本收尾。

运行中权限重检允许从 active trace 切换到唯一同身份 archive trace，要求关联原 REQ/BUG 且状态为 applied/archived；空间权限、对象 ACL 和命令身份仍每轮校验。移动本身不会撤销归档写权限，避免执行器在 Workflow Sync 前被关闭。身份重复、关联错误和权限撤销继续阻断。

纯治理 Change 使用同一归档命令与 Sprint 绑定校验。`shutil.move` 跨挂载复制时，标准目录可能先于 `trace.md` 出现；旧目录中的完整 trace 尚在，权限重检应在唯一同名旧源与最多一个同名标准目标并存期间继续授权。目标名称冲突、符号链接、源失效或命令改变立即撤销。旧源删除后，改由完整的标准目录 trace 授权。这一中间态不得被误判为两个独立 Change。

执行循环的历史引用再授权早于写权限重检；当主对象快照处于同一合法旧目录过渡期时，沿用上述严格门禁保持可访问。该例外只覆盖精确归档 prompt、当前主对象、唯一完整旧源和有效 Sprint 绑定，其他快照对象或目录冲突仍拒绝。未知轮次对账保留原始安全原因码，便于区分历史引用拒绝、写权限撤销与执行器中断。

Issue promote 的目录迁移和 registry 刷新存在短暂间隙。既有对象 ACL 校验通过后，旧 review 路径缺失时允许读取同身份 archive 文档；不得借此跨对象或绕过访问控制。执行容器无 HOME 时，AI Usage hook 的本机会话发现明确返回 unavailable，不抛异常或填造用量；产品账单仍依据执行器最终收据。

脚本在 active 缺失且唯一 canonical archive 已存在时恢复验证，不再次合并规格；验证成功后串行执行 Workflow Sync、Issue promote、AI Usage hook。验证失败保留目录并退出，不推进状态。该入口不替代验收门禁，恢复前须检查已有 delta 合并和交付证据。

终态后的有界 grace window 同时读取命令完成事件和用量。unknown 对账只补录执行器读取结果中已确认完成的命令，不虚构未完成命令；已有可信 accounting 收据立即幂等补结算，缺少收据保留预留和待对账语义，不推断零用量。

App Server 流式通知使用有界队列背压：消费者写入数据库期间可短暂落后于文字突发，队列满时等待，不以一秒排队超时判定执行异常；关闭信号解除等待。帧大小和 RPC pending 边界不变，不放开无界内存。

- 单元测试覆盖 `/opsx-archive` prompt 获得 `archive_write`，普通治理对象仍为 `governance_write`。
- 容器 profile 测试覆盖 `moonbox-archive` 包含 archive 所需路径，`moonbox-governance` 不包含 `openspec/specs` 和 `openspec/archive`。
- 执行测试覆盖外部 turn 启动前失败为 `failed`，启动后未确认错误仍为 `unknown`。
- 脚本测试覆盖隐藏目录不阻断 Change 身份校验。
- 至少运行相关后端测试、Change 中文校验和 Workflow Sync。
