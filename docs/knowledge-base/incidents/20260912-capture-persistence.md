---
created_at: 2026-09-12 17:25:00
updated_at: 2026-09-12 17:25:00
source_bug: BUG-0014-requirement-center-capture-not-persisted
source_change: fix-requirement-center-capture-persistence
---

# Capture 假成功与多文件持久化

需求中心原submitCapture只生成前端卡片，描述未进入后端，刷新后丢失。根因证据见BUG root-cause；修复通过真实API、可信controller和四类治理文件闭环。

异步接口202只是接收。页面等待applied后重新读取事实源；未知结果的超时复用幂等键，确定未写入的conflict才允许新键。完整ID由服务端锁内分配，不能用前端列表最大值分配。

跨目录、注册表和索引不是文件系统原子事务。协调锁、私有前后镜像、目录fd安全创建、逐文件替换与读取屏障共同保证可恢复性；未知外部编辑或权限失败时保留recovery_blocked，不以删锁或强改状态掩盖半成品。controller中止后的已知前后镜像可向前续写。

回归分别覆盖合成故障注入与真实观察。SQLite/MySQL测试证明操作记账；真实Chromium、独立账号及临时项目证明刷新与文档恢复；临时Compose证明API只读而controller可写。测试环境通过不代表生产已部署。
