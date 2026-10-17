---
title: 本地部署端口治理规格增量
created_at: 2026-10-08 15:19:34
updated_at: 2026-10-08 18:29:53
---
# 本地部署端口治理规格增量

## MODIFIED Requirements

### Requirement: Docker media-upload 验收入口

MoonBox Docker 本地 media-upload 验收 MUST 使用环境解析得到的宿主机端口，不得硬编码 Docker Web `:3000`。

#### Scenario: 使用实际 Web 宿主机端口验收

- **GIVEN** Docker Compose 暴露 `HOST_PORT_WEB`
- **WHEN** 执行头像、Logo、图片或其他 media-upload 横切验收
- **THEN** 验收脚本或验收说明 MUST 解析实际 Web 宿主机端口
- **AND** 默认值 SHOULD 为 `39002`
- **AND** 验收不得要求 Docker Web 固定运行在 `:3000`

#### Scenario: 端口冲突不得误判上传失败

- **GIVEN** 本机 `:3000` 被其他服务占用
- **WHEN** MoonBox Docker Web 通过 `39002` 或其他 `39001-39050` 范围内端口可访问
- **THEN** media-upload 验收 MUST 使用 MoonBox 实际端口继续验证
- **AND** 不得因为 `:3000` 不可用阻塞 `/opsx-apply`

## ADDED Requirements

### Requirement: 本地宿主机端口范围

MoonBox 本地部署的宿主机端口 MUST 位于 `39001-39050`；容器内部监听端口保持服务默认值。

#### Scenario: 校验本地部署配置

- **WHEN** 本地部署环境配置宿主机映射端口
- **THEN** 配置校验 MUST 拒绝范围外端口
- **AND** Compose 默认值 MUST 使用 390xx 端口段
