---
bug_id: BUG-0017-compose-container-name-suffix-one
title: 容器名不应自动追加 -1 后缀
status: done
created_at: '2026-09-14 09:05:04'
updated_at: 2026-09-17 08:12:08
owner: 产品团队
source: 用户反馈
lifecycle_stage: plan
environment: docker
related_requirement: null
related_bug: null
captured_via: capture
classification_rationale: 用户描述“容器名不要加 -1”，属于现有 Docker/Compose 命名表现与期望不一致，按缺陷采集。
severity: medium
---

# 现象

Docker/Compose 启动后的容器名出现自动追加 `-1` 后缀的情况；期望容器名不要包含该后缀。

# 复现步骤

1. 使用项目 Docker/Compose 启动本地或部署环境。
2. 查看生成的容器名称。
3. 观察容器名是否被追加 `-1`。

# 期望 vs 实际

- 期望：容器名符合项目约定，不自动追加 `-1` 后缀。
- 实际：用户反馈当前容器名存在追加 `-1` 的表现。

# 待澄清与补证

- [ ] 具体环境：本地 Docker Compose、生产 Compose、CI 或其他部署方式。
- [ ] 受影响容器清单及当前实际容器名。
- [ ] 期望容器名格式是否要求固定 `container_name`，以及是否允许多副本扩展。

# 后续补证步骤

在目标环境执行容器列表查看命令，记录服务名、容器名和启动方式摘要；去除本机路径、密钥、镜像仓库凭据和环境变量内容。
