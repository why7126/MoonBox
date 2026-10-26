# 范围外既有校验残留

2026-10-26 全仓 API 标准校验报告 `src/backend/app/api/v1/capture_drafts.py` 的图片二进制路由没有 response_model。通过 `git show HEAD:src/backend/app/api/v1/capture_drafts.py` 核对，提交基线已存在同一声明，本次未修改该文件。Chat 新增路由另按同一校验器聚焦检查。

`tests/unit/test_chat_platform_script.py::test_chat_overlay_container_name_defaults_do_not_use_compose_suffixes` 要求 `.env.example` 包含 `CHAT_WORKER_CONTAINER_NAME` 等内部字段；HEAD 的示例文件也不含该字段，本次未改动示例与此测试。该文件其余4项通过，Docker 生命周期与启动脚本11项通过。未为消除范围外失败降低测试断言或改写环境示例。

两项均记录为既有 warning，不代替本需求功能、接口和容量门禁。未自动创建跟进 Issue。

聚焦Chat文件时，同一校验器还对已有二进制/流式 material_content、stream、verification_evidence 报 response_model 缺失，HEAD已存在，未修改其返回协议。新增5个分页/恢复路由的响应模型、summary及tags检查通过。
