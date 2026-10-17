---
title: 纯治理 Change 的受控归档执行规范
---

# 纯治理 Change 的受控归档执行规范

## ADDED Requirements

### Requirement: 纯治理 Change 的受控归档执行

系统 SHALL 仅对已授权且已应用的纯治理 Change 归档命令授予最小归档写权限，并保证同一执行沙箱可以调用固定镜像内的治理工具。

#### Scenario: 合法纯治理 Change 归档

- **WHEN** 有写权限成员在对应主对象会话发送完整归档命令，Change 已应用且位于当前 Sprint 正式范围
- **THEN** 系统 SHALL 授予归档专用权限，使规格合并、归档移动和工作流同步可以在受控工作区完成

#### Scenario: 归档条件不足

- **WHEN** 命令、主对象、来源类型、Change 状态、Sprint 范围或成员权限任一条件不匹配
- **THEN** 系统 MUST NOT 授予归档专用写权限
- **AND** 普通治理写权限 MUST NOT 扩展到生效规格或归档目录

#### Scenario: 归档命令工具可用

- **WHEN** 执行器镜像通过工具链预检并启动治理命令沙箱
- **THEN** 命令环境 SHALL 使用固定的镜像内工具路径解析 Python、Node 与 OpenSpec
- **AND** 不得继承宿主可写工具目录或开放执行网络
