## 背景

BUG-0007 的根因不是上传接口本身，而是 media-upload 验收治理把临时本机假设写成了正式门禁。Docker Web 端口应从环境解析，测试身份应由脚本准备，而不是依赖历史持久库中的默认管理员密码。

## 根因

- 端口根因：旧最佳实践要求 Docker 本地 `:3000` 上传读取回显，但 MoonBox 当前宿主机端口统一使用 `18101-18199`，Web 默认 `18102`。
- 身份根因：Docker 后端数据挂载在 `data/runtime/backend`，已有数据库会跨启动保留。`ADMIN_INITIAL_PASSWORD` 只在首次 seed 时生效，不能代表当前管理员密码。
- 治理根因：`media-upload` 横切验收缺少“环境解析端口 + 可控测试身份”的稳定模式。

## 修复方案

1. 文档治理
   - 将所有 Docker media-upload 固定 `:3000` 验收表述改为“解析 `HOST_PORT_WEB`，默认 `18102`”。
   - 明确本地持久库不保证默认管理员密码可用。
   - 在 best-practice 中要求验收脚本准备测试身份。

2. 验收脚本策略
   - 脚本读取 `.env` 或 Compose 默认值获得 Web/API 入口。
   - 脚本创建一次性用户、测试会话或可回收 fixture。
   - 脚本使用该身份完成 `/api/v1/auth/login`、`POST /api/v1/auth/avatar`、受保护读取和前端/接口回显校验。

3. 回归证据
   - 记录实际端口、测试身份来源、是否使用持久库、上传结果、受保护读取结果和回显结果。
   - 不记录真实密码、Authorization header、Cookie、`.env` 原文或本机绝对路径。

## 测试计划

- 后端/脚本测试：覆盖测试身份准备、登录、头像上传、受保护读取。
- Docker 验收：在 `HOST_PORT_WEB=18102` 下运行；默认管理员密码不可用时仍应通过。
- 文档校验：搜索并替换 `media-upload` 相关 `:3000` 固定验收口径。
- OpenSpec 校验：运行 `openspec validate fix-docker-media-upload-acceptance-gate --strict`。

## 风险

- 若现有 API 不支持安全创建一次性测试用户，可能需要通过测试 fixture 或管理端测试准备路径实现。
- 若 Docker 环境未启动，验收脚本应给出可诊断跳过/失败信息，不得把端口或默认密码假设重新写入文档。
