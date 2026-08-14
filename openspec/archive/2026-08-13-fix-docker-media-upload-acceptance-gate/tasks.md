## 1. 治理文档与最佳实践

- [x] 1.1 更新 `docs/07-object-storage-strategy.md`，删除 Docker `:3000` 固定 media-upload 验收口径，改为解析 `HOST_PORT_WEB` 默认 `18102`。
- [x] 1.2 更新 `docs/knowledge-base/best-practices/admin-media-upload-chain.md`，明确端口解析和脚本准备测试身份要求。
- [x] 1.3 更新 `iterations/archive/sprint-002/` 中残留的 media-upload 横切验收描述，避免继续阻塞当前 Sprint。
- [x] 1.4 如命令 Skill 或规则中存在 `media-upload` 固定 `:3000` 或默认管理员密码假设，同步修正并记录治理日志。

## 2. 验收脚本与测试身份

- [x] 2.1 实现或调整 Docker media-upload 验收脚本，使其解析 `.env` / Compose 默认端口。
- [x] 2.2 让验收脚本创建或准备一次性测试用户、测试会话或可回收 fixture。
- [x] 2.3 使用脚本准备的测试身份完成 `/api/v1/auth/login`、`POST /api/v1/auth/avatar`、受保护读取和回显校验。
- [x] 2.4 确保验收输出不包含真实密码、Authorization header、Cookie、真实 `.env` 原文或本机绝对路径。

## 3. 回归验证

- [x] 3.1 在 Docker Web 默认 `18102` 下验证 media-upload 上传、读取和回显。
- [x] 3.2 验证本地管理员密码不等于项目默认值时，验收脚本仍可通过测试身份完成验证。
- [x] 3.3 运行相关后端 pytest / 脚本测试。
- [x] 3.4 运行 OpenSpec 校验。

## 4. 追溯与沉淀

- [x] 4.1 更新 BUG-0007 trace、Sprint scope 和 Change trace。
- [x] 4.2 若修复过程发现可复用事故经验，补充 `docs/knowledge-base/incidents/` 或记录不适用原因。
