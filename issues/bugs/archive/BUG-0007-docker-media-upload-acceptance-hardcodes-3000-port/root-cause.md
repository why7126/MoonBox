---
bug_id: BUG-0007-docker-media-upload-acceptance-hardcodes-3000-port
created_at: 2026-08-12 12:48:13
updated_at: 2026-08-12 12:48:13
category: governance
---

# 根因分析

## 直接原因

Docker 媒体上传横切验收口径把两个本应动态解析或由脚本准备的前置条件写成了隐式固定值：

1. 宿主机访问入口固定为 Docker 本地 `:3000`。
2. 登录身份固定依赖 `admin / 默认密码`。

这与 MoonBox 当前 Docker 端口矩阵和本地运行时数据持久化策略不匹配。项目默认 Web 宿主机端口为 `18102`，后端宿主机端口为 `18101`；Docker 本地数据库挂载在 `data/runtime/backend`，已有数据会跨启动保留。

## 根本原因

`media-upload` 验收最佳实践和 Sprint 横切验收描述把“演示时可用的本机假设”沉淀成了正式验收门禁，没有把验收依赖抽象为可解析的环境输入和可控测试身份。

正确的验收边界应是：

- 从 `.env`、Docker Compose 或启动脚本解析实际 `HOST_PORT_WEB` / `HOST_PORT_BACKEND`。
- 由验收脚本创建或准备一次性测试用户、测试会话或可回收 fixture。
- 使用脚本持有的测试身份完成登录、头像上传、受保护读取和回显校验。
- 不依赖本地历史状态中管理员密码是否仍等于 `ADMIN_INITIAL_PASSWORD`。

## 触发条件

- 本机 `:3000` 被其他服务占用，或 MoonBox Docker Web 未映射到 `:3000`。
- 本地 `data/runtime/backend` 已存在持久数据库。
- 管理员密码曾被用户修改，或历史启动时使用过不同的 `ADMIN_INITIAL_PASSWORD`。
- `/opsx-apply` 复用旧的 `media-upload` 验收口径，要求固定端口或默认管理员密码。

## 分类

- 类型：governance / test-design / documentation
- 影响阶段：`/req-complete`、`/req-opsx`、`/opsx-apply`
- 影响能力：Docker 媒体上传横切验收、头像上传、受保护媒体读取、同会话回显

## 结论

这是治理和验收设计缺陷，不是单个上传接口的运行时代码缺陷。修复应优先改正验收口径和脚本策略：端口从环境解析，测试身份由脚本准备，避免依赖固定宿主端口和持久本地库中的默认管理员密码。
