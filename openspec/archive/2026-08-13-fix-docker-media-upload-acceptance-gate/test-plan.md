---
change_id: fix-docker-media-upload-acceptance-gate
created_at: 2026-08-12 12:56:35
updated_at: 2026-08-12 12:56:35
---

# 测试计划

## 必跑

- `openspec validate fix-docker-media-upload-acceptance-gate --strict`
- 相关后端 pytest 或脚本测试，覆盖测试身份准备、登录、头像上传和受保护读取。
- Docker media-upload 验收脚本，使用实际 `HOST_PORT_WEB`，默认 `18102`。

## 证据要求

- 记录解析出的 Web/API 入口，不记录本机绝对路径。
- 记录测试身份来源，不记录真实密码。
- 记录上传、读取和回显结果。
- 若 Docker 环境不可用，记录不可用原因，并不得退回 `:3000` 或默认管理员密码假设。
