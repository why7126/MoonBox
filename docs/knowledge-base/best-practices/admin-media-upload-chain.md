---
title: Admin Media Upload Chain
purpose: 管理后台媒体上传链路治理，预防上传状态、即时回显和 Docker 边界文件访问缺陷
source: REQ-0004-admin-user-management
status: active
created_at: 2026-08-07 22:21:34
updated_at: 2026-08-07 22:21:34
---

# 管理后台媒体上传链路

## 适用范围

适用于管理后台头像、Logo、图片、视频等上传与回显场景，覆盖前端状态机、后端存储、对象访问和本地 Docker 验收。

## 验收 gate

- 上传组件必须具备 `idle -> uploading -> done/failed` 状态机。
- 上传中必须禁用重复提交和重复选择触发，失败后必须允许重试。
- 上传成功后必须在同一会话立即回显到当前表单或列表，不依赖刷新页面。
- 上传成功后的 URL 或对象引用不得写入日志中的敏感上下文，且不得泄露临时凭据。
- Docker 本地环境必须从 `.env`、Docker Compose 或启动脚本解析实际 `HOST_PORT_WEB`，默认使用 `18102` 完成文件上传、读取和回显验收；不得硬编码 `:3000`。
- Docker media-upload 验收脚本必须自行准备一次性测试用户、测试会话或可回收 fixture，不得依赖 `data/runtime/backend` 持久库中的管理员密码等于 `ADMIN_INITIAL_PASSWORD`。
- 后端上传接口和静态/对象访问路径必须在容器网络、浏览器访问和反向代理路径下保持一致。

## 落地要求

- `/req-complete` 命中 `media-upload` 时，必须将上传状态机、同会话即时回显、Docker 实际 Web 端口上传读取回显和脚本准备测试身份转化为横切 AC。
- `/opsx-apply` 需要覆盖上传成功、上传失败、重复提交、刷新前回显、Docker 本地文件访问和默认管理员密码不可用时的测试身份准备。
