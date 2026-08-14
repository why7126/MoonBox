---
change_id: fix-docker-media-upload-acceptance-gate
status: applied
acceptance_status: pending
created_at: 2026-08-12 12:56:35
updated_at: 2026-08-12 13:04:04
---

# 验收

- AC-001：Docker media-upload 验收不再要求固定 `:3000`。
- AC-002：验收脚本不依赖 `ADMIN_INITIAL_PASSWORD` 或默认管理员密码。
- AC-003：脚本准备测试身份并完成登录、头像上传、受保护读取和回显。
- AC-004：对象存储策略、最佳实践和 Sprint 横切验收口径同步。
- AC-005：OpenSpec、测试和相关文档校验通过。

## 验收证据

```yaml
acceptance_status: pending
source_event: opsx.apply
evidence:
  - command: uv run pytest tests/unit/test_verify_docker_media_upload.py
    result: passed
  - command: scripts/verify-docker-media-upload.py --file <tmp-image>
    result: passed
    web_port: 18102
    test_identity: script-prepared-front-user
    checks:
      login: passed
      upload: passed
      protected_read: passed
      profile_echo: passed
  - command: openspec validate fix-docker-media-upload-acceptance-gate --strict
    result: passed
notes: 验收输出已脱敏，未记录密码、Authorization header、Cookie、真实 .env 原文或本机绝对路径。
```
