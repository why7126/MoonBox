---
bug_id: BUG-0007-docker-media-upload-acceptance-hardcodes-3000-port
review_result: approved
reviewed_at: 2026-08-12 12:50:28
reviewer: user
decision: approve
---

# 评审结论

## 结论

批准修复。

## 评审清单

- [x] 可复现或根因充分：已确认 `media-upload` 横切验收同时依赖固定 Docker `:3000` 入口和本地持久库中的默认管理员密码，均属于不稳定验收前置条件。
- [x] 严重等级合理：`high / P1` 合理；该问题会阻塞 `/opsx-apply` 交付验收，且容易跨需求重复触发。
- [x] 回归验收明确：AC 已覆盖端口解析、测试身份准备、治理文档同步和 Docker media-upload 回归验证。
- [x] hotfix 路径判断：不需要 hotfix；建议作为当前 Sprint 内治理修复尽快纳入。

## 修复方向

修复应统一调整 Docker media-upload 验收口径：

1. 从 `.env`、Docker Compose 或启动脚本解析实际宿主机端口，默认使用 `HOST_PORT_WEB=18102`。
2. 验收脚本自行准备一次性测试用户或测试会话，不依赖 `data/runtime/backend` 持久库中的管理员密码等于项目默认值。
3. 同步对象存储策略、媒体上传最佳实践、Sprint 横切验收描述和后续命令提示，删除 Docker `:3000` 与 `admin / 默认密码` 的隐式前置条件。

## 下一步

`/sprint-propose --bug BUG-0007-docker-media-upload-acceptance-hardcodes-3000-port`
