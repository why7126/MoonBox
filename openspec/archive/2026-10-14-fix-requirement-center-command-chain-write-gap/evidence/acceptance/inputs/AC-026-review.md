---
title: 标准部署轮次复核
created_at: 2026-10-14 17:20:00
updated_at: 2026-10-14 17:20:00
---

# 标准部署轮次复核

结论：已按标准部署路径完成配对重启并复核现状。

- `verification.md` 标准部署补证段记录：确认无活跃 Chat 轮次后依次执行 `docker-down.sh self-storage-sqlite --chat-platform` 与 `docker-up.sh self-storage-sqlite --chat-platform`，两者退出码为 0；后端和 Web 重建，服务健康，历史 unknown 未被误写为完成。
- 2026-10-14 17:20 本机只读 `docker ps`：共享 `moonbox-backend`、`moonbox-chat-worker`、`moonbox-governance-controller` 和 MinIO 为 healthy，Web 为 Up；隔离环境对应服务亦健康。
- 当前前端测试使用项目入口及 Node localStorage 参数，126 项通过；标准部署有效性另由 AC-020/024 的运行态构建取证支持。
- product_data_collection_observability: N/A，无采集逻辑变更；affected_layers: 部署、Web、Backend、Chat worker；validation: 标准脚本历史运行记录、现状健康检查、前端测试。
