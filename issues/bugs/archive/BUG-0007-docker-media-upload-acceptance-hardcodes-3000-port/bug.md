---
bug_id: BUG-0007-docker-media-upload-acceptance-hardcodes-3000-port
title: Docker 媒体上传横切验收依赖固定端口和默认管理员密码
severity: high
status: done
owner:
discovered_at: 2026-08-12 12:08:14
environment: docker
related_requirement:
related_change:
created_at: 2026-08-12 12:58:04
updated_at: 2026-08-13 22:50:17
---

# Docker 媒体上传横切验收依赖固定端口和默认管理员密码

## 现象

媒体上传横切验收资料仍要求 Docker 本地 `:3000` 完成上传、读取和回显验收，但 MoonBox 当前端口规范要求本地宿主机端口统一落在 `18101-18199` 区间。Docker Compose 默认后端宿主机端口为 `18101`，Web 宿主机端口为 `18102`，因此 `:3000` 不属于当前 MoonBox Docker 端口矩阵。

即使端口改为 `18102`，当前验收方法仍隐含依赖“本地运行时库中的管理员账号密码刚好等于项目默认值”。Docker 本地库挂载在 `data/runtime/backend`，属于持久状态；只要之前启动过服务、改过管理员密码，或用不同 `ADMIN_INITIAL_PASSWORD` seed 过，后续 `ADMIN_INITIAL_PASSWORD` 就不能稳定代表当前账号密码。

因此，“用 `admin / 默认密码` 登录后再做媒体上传验收”本身就是不可靠的验收方法。该问题会导致涉及 `media-upload` 的 `/opsx-apply` 在验收阶段被错误阻塞，尤其是头像上传、受保护媒体读取、同会话回显等横切验收场景。

## 复现

1. 执行涉及 `media-upload` 横切验收的 `/opsx-apply`。
2. 按当前验收资料要求，尝试使用 Docker 本地 `:3000` 完成文件上传、读取和回显验收。
3. 对照端口规范确认 MoonBox 本地宿主机端口应使用 `18101-18199`，默认 Web 端口为 `18102`。
4. 当 `:3000` 被其他服务占用，或 Docker Web 未映射到 `:3000` 时，验收被判定为阻塞。
5. 即使改用 `18102`，继续使用 `admin / 默认密码` 登录做验收。
6. 当 `data/runtime/backend` 已存在持久库，且管理员密码曾被修改或由不同初始值 seed，登录前置条件失败，媒体上传验收再次被错误阻塞。

## 期望 / 实际

期望：

- Docker 媒体上传横切验收应从 `.env`、Docker Compose 或启动脚本解析实际宿主机端口。
- 默认验收应使用 `HOST_PORT_WEB=18102` 的 Web 同源入口和 `HOST_PORT_BACKEND=18101` 的后端直连接口证据。
- 验收脚本应自行准备一次性测试用户或测试会话，完成 `/api/v1/auth/login`、`/api/v1/auth/avatar` 上传、受保护读取和回显校验。
- 长期治理文档、知识库最佳实践、Sprint 横切验收描述不得硬编码 `:3000`。
- 验收不得依赖本地持久库中管理员账号的当前密码等于 `ADMIN_INITIAL_PASSWORD` 或项目示例默认值。

实际：

- 对象存储策略、媒体上传最佳实践和部分 Sprint 验收描述仍残留 Docker `:3000` 上传读取回显要求。
- 部分验收证据仍使用 `admin / 默认密码` 作为登录前置条件，忽略 `data/runtime/backend` 是持久状态。
- `/opsx-apply` 容易把非 MoonBox 端口冲突或本地持久账号密码漂移误判为功能未通过，造成错误阻塞。

## 影响范围

- 影响命令：`/req-complete`、`/req-opsx`、`/opsx-apply` 中涉及 `media-upload` 的横切验收。
- 影响文档：对象存储策略、媒体上传链路最佳实践、已纳入 Sprint 的头像/媒体上传验收口径。
- 影响测试身份：依赖本地持久库中的默认管理员密码，会让同一仓库在不同机器、不同历史运行状态下得到不同验收结果。
- 影响交付：会让已可通过实际 Compose 端口和稳定测试身份完成的上传读取回显，被 `:3000` 口径或默认密码假设错误阻断。

## 严重等级说明

严重等级为 `high`。该问题不直接破坏运行时代码，但会阻断正式交付流程中的 `/opsx-apply` 验收，且属于跨需求复用的横切治理口径错误。一旦后续需求复用 `media-upload` 验收模板，就可能因为固定宿主端口或默认管理员密码假设重复触发同类阻塞。
