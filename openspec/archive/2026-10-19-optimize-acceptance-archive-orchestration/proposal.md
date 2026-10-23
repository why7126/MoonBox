---
title: 自动验收与归档连续执行优化
created_at: 2026-10-19 09:00:30
updated_at: 2026-10-19 09:00:30
---

# 自动验收与归档连续执行优化

## 背景

REQ-0027 与 BUG-0033/0034/0035 的验收暴露全局阻塞、宽泛指纹、重复命令及环境准备成本。

## 变更内容

逐 AC 连续调度、局部预检、待采集状态、检查点、精确输入、命令去重、环境与样本契约、浏览器能力、状态统一、归档预演与恢复、最小耗时指标。

## 能力影响

### 新增能力
- `acceptance-orchestration`：治理验收连续执行与归档就绪预检。

## 影响范围

仅 scripts、tests/unit、skills、rules、docs、AGENTS 和当前 Change/Sprint；不修改 src、API、DB、UI、Orval 或部署。
