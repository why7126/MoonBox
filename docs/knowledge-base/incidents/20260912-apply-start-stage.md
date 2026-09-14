---
created_at: 2026-09-12 21:28:51
updated_at: 2026-09-12 21:28:51
source_bug: BUG-0015-requirement-center-apply-start-stage-not-synced
source_change: fix-requirement-center-apply-lifecycle-sync
---

# 启动事实与任务进度分离

任务完成数不能证明研发是否启动。启动事件记录生命周期事实，任务计数表达实际完成进度，完成事件表达门禁通过；三个信号分别建模，避免0/N停留待开发或全勾选提前完成。

CLI和看板采用同一纯函数，保留旧终态，不为历史数据编造启动时间。先写事实再生成投影；项目锁与逐文件原子替换支持失败重跑，但不承诺跨文件事务或与任意外部编辑器互斥。

回归同时覆盖合成中断与真实CLI/API/浏览器链路，证据见Change verification.md。截图和快照证明刷新后的事实源状态，不能用前端本地移动替代服务端持久化。
