---
title: Chat 验收运行能力缺口修复提案
created_at: "2026-10-31 12:44:24"
updated_at: "2026-10-31 12:44:24"
source_bug: BUG-0045-chat-acceptance-runtime-capability-gap
---

# Chat 验收运行能力缺口修复提案

## 背景

[BUG-0045-chat-acceptance-runtime-capability-gap](../../../issues/bugs/review/BUG-0045-chat-acceptance-runtime-capability-gap/bug.md)已评审并纳入sprint-017。执行器基础工具就绪不代表测试依赖、验证worker及浏览器可用，缺少项目绑定和启动预检导致开发后才暴露验收阻塞。E1—E8支持该链路；历史AnyIO超时的独立原因仍未确认。

## 变更内容

复用REQ-0044验证服务，补齐固定版本依赖、正确项目子目录、验证worker配置、按项目能力预检、Chat受控验证调用和证据回传。局部失败仅阻塞相关验证，恢复时按输入指纹续接。

## 能力影响

### 修改能力
- project-verification-environment：扩展项目预检到Python测试、worker部署及Chat启动；增加Chat操作关联和局部续接要求。

### 新增能力
无独立新能力；在既有验证服务内修复。

## 影响范围

Chat执行链路、verification服务与worker、锁定依赖和Docker部署配置、Web能力反馈、API/OpenAPI/Orval、观测及对应文档。DB按现有验证任务字段优先复用，若需要新增持久化须在实施前设计迁移。暂估8人天；Sprint总35/30人天，超额但未达120%硬阻断，不扩大范围。

## 范围与回滚

只验证授权且版本可核对的预配置目标。REQ-0048负责独立数据库、测试应用、短期身份和生命周期编排；BUG-0046问答、REQ-0046结果文案不重复实现。不开放任意网络/Docker socket，不复制个人凭证。回滚关闭新增准入、停止领取新验证任务、保留运行事实及证据，恢复已验证镜像；未知结果不自动重放。正式部署需明确目标与授权，本命令不执行部署。

