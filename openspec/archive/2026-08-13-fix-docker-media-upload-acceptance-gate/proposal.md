## 背景

BUG-0007 证明 Docker media-upload 横切验收存在两个不稳定前置条件：验收资料仍硬编码 Docker Web `:3000`，并隐含依赖 `admin / 默认密码` 可登录本地持久库。MoonBox 当前本地宿主机端口规范为 `18101-18199`，Docker Web 默认 `HOST_PORT_WEB=18102`；同时 `data/runtime/backend` 是持久状态，`ADMIN_INITIAL_PASSWORD` 只代表首次 seed 输入，不保证代表当前管理员密码。

该缺陷会让 `/opsx-apply` 在媒体上传、受保护读取和同会话回显验收中被错误阻塞，尤其影响头像上传和统一账号认证链路的后续回归。

## 变更内容

- 修正 Docker media-upload 验收治理口径：不得固定使用 `:3000`，必须从 `.env`、Docker Compose 或启动脚本解析实际宿主机端口。
- 修正测试身份策略：验收脚本应创建或准备一次性测试用户、测试会话或可回收 fixture，不依赖本地持久库中的管理员密码等于 `ADMIN_INITIAL_PASSWORD`。
- 同步对象存储策略、media-upload 最佳实践、Sprint 横切验收描述、相关命令提示和回归证据口径。
- 增加回归验证：在 Docker Web 使用 `18102` 且默认管理员密码不可用时，仍可通过脚本准备的测试身份完成 `/api/v1/auth/login`、`POST /api/v1/auth/avatar`、受保护读取和回显校验。

## 能力范围

### 新增能力

- None. This change corrects existing deployment and testing governance.

### 修改能力

- `deployment-governance`: Docker media-upload 验收入口必须遵守 MoonBox 宿主机端口矩阵，不得硬编码 `:3000`。
- `testing`: Docker media-upload 验收必须使用可控测试身份或 fixture，不得依赖本地持久库中的默认管理员密码。

## 影响范围

- `docs/07-object-storage-strategy.md`
- `docs/knowledge-base/best-practices/admin-media-upload-chain.md`
- `iterations/archive/sprint-002/` 中 media-upload 横切验收口径
- 相关验收脚本、测试 fixture、命令提示和回归证据
- 不修改业务上传接口语义；若实现阶段发现必须补充测试辅助接口或 fixture，应同步 API/测试文档并记录原因。

## 回滚计划

- 若修复后的脚本化测试身份策略不可用，回滚到只更新文档口径但保留人工验收说明。
- 不回滚到 Docker `:3000` 固定入口，也不恢复 `admin / 默认密码` 作为验收前置条件。
- 回滚后必须在 BUG trace 和 Change trace 中记录仍需人工验收的剩余风险。
