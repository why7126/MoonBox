---
title: 归档用量归属与桌面会话解析修复
created_at: "2026-10-20 19:40:57"
updated_at: "2026-10-20 19:40:57"
---

# 归档用量归属与桌面会话解析修复

## 背景
归档钩子仅读取 sprint，而事实使用 iteration；桌面用户消息 content 数组未识别，已有 Token 事件却无命令记录。

## 变更内容
复用 Workflow Sync 的 Sprint 解析，支持文本内容块，增加脱敏诊断和回归。

## 能力
更新治理用量采集。

## 影响
仅治理脚本、测试与文档；不涉及业务实现、API、DB、Web、客户端、Orval 或 Docker Compose。