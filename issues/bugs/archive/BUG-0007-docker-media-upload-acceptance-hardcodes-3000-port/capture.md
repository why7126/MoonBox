---
bug_id: BUG-0007-docker-media-upload-acceptance-hardcodes-3000-port
status: done
created_at: 2026-08-12 12:08:14
updated_at: 2026-08-13 22:50:42
severity_hint: high
environment: docker
related_requirement:
related_bug:
---

# 现象

Docker 媒体上传横切验收仍硬编码使用宿主机 `:3000`，与 MoonBox 本地宿主机端口统一使用 `18101-18199` 的端口规范冲突，导致 `/opsx-apply` 在媒体上传验收时多次被错误阻塞。

# 复现步骤

1. 执行涉及 `media-upload` 横切验收的 `/opsx-apply`。
2. 按当前验收要求尝试使用 Docker 本地 `:3000` 完成上传、读取和回显验收。
3. 对照 `rules/port-management.md` 与 `docs/02-deployment.md` 中 MoonBox 本地端口范围要求。
4. 观察验收是否因 `:3000` 与端口规范冲突而被判定为阻塞。

# 期望 vs 实际

- 期望：Docker 媒体上传横切验收应使用 MoonBox 规范端口，例如 Web 宿主机端口 `18102` 与后端宿主机端口 `18101`，或从环境/Compose 配置解析实际端口；不得要求使用 `:3000`。
- 实际：部分横切验收描述仍要求 Docker 本地 `:3000` 上传读取回显，和 `18101-18199` 端口规范不一致，导致 `:3000` 被其他服务占用或不属于 MoonBox 端口矩阵时，`/opsx-apply` 被错误阻塞。

# 附件

无
