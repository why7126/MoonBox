# moonbox-core

统一工作区领域服务，Python 导入名为 `moonbox_core`。空间和仓库身份先经服务端鉴权，客户端不传物理路径或角色。

- `workspaces.py` / `schema.py`：唯一主目录、交付根链路唯一活动开发树、不可变会话绑定、持久占用与创建续接。
- `authority.py`：从主目录解析 Change、REQ/BUG 和 Sprint；确认和执行时重新检查当前空间角色、对象可见性与迭代范围。
- `migration.py` / `sessions.py`：source 原位登记，旧 copy 保留为历史目录；迁移保留基线摘要，不把旧会话搬入新目录。
- `service.py` / `delivery_policy.py`：开发树申请、子 Change 串行复用、后继会话、当前交付范围限制。正式治理文件仍由主工作区维护。
- `integration.py` / `integration_worker.py`：固定双父候选、验证指纹、人工确认、主目录串行队列、实际 Git 结果与持久操作对账。Git 已成功但数据库未记录时可仅修复结果，不重新合并或获得新写权限。
- `completion.py`：执行器确认退出且文件采集完成后释放原操作占用；失联、超时或未知结果保持占用。单项失败不阻止同批其他工作区收尾。
- `lifecycle.py`：显式清理独立目录；主目录、脏目录、未合入提交、活动操作和保护引用保持保护。

Web 传输层在 `moonbox_app_server`，非交互服务适配在 `moonbox_exec`，共同调用此领域层。Git 经 `moonbox_worktree`，恢复内容经 `moonbox_rollout` 和既有分块存储。

当前正式开放门禁仍受 REQ-0048 的固定候选独立验收能力约束。供应器已接入 verification.candidate；部署未批准模板时仍返回 `isolated_candidate_validation_unavailable`，不接受客户端上传的“通过”证明。真实 Git/数据库回归、容器沙箱与浏览器合成样本不替代真实模型轮次和组合环境验收。

`governance_projection.py` 将已证明的 Git 合入结果写入主线共享注册表和 Sprint 合入记录。它使用主工作区占用及既有治理文件锁，逐文件比较、原子写入并读回，独立记录 pending/applying/blocked/completed。失败只影响治理同步，不抹去已发生的 Git 结果；重试不重放合并。写入形成主目录未提交治理修改，正式归档及提交由各自受控流程执行。

`moonbox-tui` 为保留的终端交互职责名，首期不新增终端产品入口；Web 使用 `moonbox-app-server`，自动执行使用 `moonbox-exec`，两者复用 `moonbox-core`，执行隔离由 `moonbox-exec-server`，恢复点由 `moonbox-rollout`，Git 工作树由 `moonbox-worktree` 承担。Python 包使用下划线映射同名模块。
