---
title: 临时 Docker 资源登记与回收设计
created_at: 2026-10-26 12:06:37
updated_at: 2026-10-26 12:06:37
---

# 临时 Docker 资源登记与回收设计

## 设计
台账写入 Git 忽略的 logs/temporary-docker/，仅记录随机 run ID、Change ID、用途分类、daemon ID 哈希、期限和关闭事实，不写真实路径或凭据。先登记再创建，容器和网络都携带 moonbox.temp.managed=true、moonbox.temp.run、moonbox.temp.expires 标签。默认4小时，最长24小时；延期必须重新明确范围，不自动无限续期。
脚本提供 register、check、cleanup、reap；cleanup/reap 默认预览，显式 --apply 执行。删除前核对 daemon、三标签与完整资源 ID；容器先于网络删除，删除后重扫。仅任务所属 run 的 cleanup 可以终止运行容器；到期 reap 遇到运行容器阻断该 run，继续处理其他可回收 run。网络存在任何连接、发现带卷的容器或台账损坏均失败关闭；不删除卷、镜像、bind 文件或未登记资源。不使用全局 prune 或名称前缀删除。
## 执行门禁
入口只读扫描到期项；本任务登记资源退出前 cleanup --apply 后 check。正常结束零残留；排障保留须在证据中说明原因、期限、责任与清理命令，不能报已清理。异常强杀无法依赖 finally，下一治理任务入口执行 reap；不是常驻定时服务，不承诺无人执行时准时回收。
## 风险与验证
标签是本地受信任治理约定，不是对恶意 Docker 管理员的安全隔离。任务必须停止创建资源后清理，不能同时继续创建。并发脚本通过文件锁串行；Docker 不可用不能当作零残留。验证跨 daemon、错标签、到期运行容器、卷保护、网络占用、重复清理及错误路径。
