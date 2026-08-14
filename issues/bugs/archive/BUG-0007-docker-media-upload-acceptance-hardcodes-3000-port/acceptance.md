---
bug_id: BUG-0007-docker-media-upload-acceptance-hardcodes-3000-port
acceptance_status: passed
created_at: 2026-08-12 12:48:13
updated_at: 2026-08-14 16:29:34
---

# 验收标准

## AC-001 端口口径不再固定为 3000

- GIVEN MoonBox 本地 Docker 端口规范为 `18101-18199`
- WHEN 生成或执行 `media-upload` 横切验收
- THEN 验收说明和脚本 MUST 从 `.env`、Docker Compose 或启动脚本解析实际宿主机端口
- AND 默认 Web 入口 SHOULD 使用 `HOST_PORT_WEB=18102`
- AND 不得要求 Docker Web 固定运行在 `:3000`

## AC-002 验收身份不依赖默认管理员密码

- GIVEN Docker 本地数据库挂载在 `data/runtime/backend`
- WHEN 本地库已有持久状态、管理员密码被修改或历史 seed 使用过不同初始值
- THEN media-upload 验收 MUST 仍可稳定准备测试身份
- AND 不得把 `ADMIN_INITIAL_PASSWORD` 或项目示例默认密码视为当前账号密码

## AC-003 脚本准备一次性测试用户或测试会话

- GIVEN 需要验证当前登录用户头像上传链路
- WHEN 执行 Docker media-upload 验收
- THEN 验收脚本 SHOULD 创建或准备一次性测试用户、测试会话或可回收 fixture
- AND 使用该测试身份完成 `/api/v1/auth/login`
- AND 使用该测试身份完成 `POST /api/v1/auth/avatar`
- AND 使用该测试身份完成受保护头像读取和同会话回显校验

## AC-004 治理文档和最佳实践同步

- GIVEN 修复该缺陷
- WHEN 更新对象存储策略、媒体上传最佳实践、Sprint 横切验收口径或命令提示
- THEN 相关文档 MUST 删除或替换 Docker `:3000` 固定入口要求
- AND MUST 明确本地持久库不保证默认管理员密码可用
- AND MUST 明确 media-upload 验收应使用环境解析端口和脚本准备的测试身份

## AC-005 回归验证覆盖

- GIVEN `HOST_PORT_WEB` 为 `18102`
- WHEN Docker Web 通过 `18102` 提供服务，且本地管理员密码不等于项目默认值
- THEN media-upload 验收仍能通过脚本准备的测试身份完成上传、读取和回显
- AND `/opsx-apply` 不应因为 `:3000` 不可用或默认管理员密码不可用而阻塞

## 验收结果回填

```yaml
acceptance_status: passed
accepted_at: 2026-08-14 16:29:34
accepted_by: workflow-sync
source_change: fix-docker-media-upload-acceptance-gate
source_sprint: sprint-002
evidence: []
failed_items: []
source_event: sprint.archive
notes: 由 Workflow Sync 根据 Change/Sprint 状态回填。
```

