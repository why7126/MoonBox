---
title: 治理 Python 统一入口优化记录
created_at: 2026-10-25 22:19:31
updated_at: 2026-10-25 22:19:31
---

# 治理 Python 统一入口优化记录

## 目标与变更

通过统一解释器选择与写入前检查，减少环境缺依赖导致的治理流程中断。新增 shell 入口与标准库预检，选择显式 PYTHON_BIN 或项目虚拟环境；无有效环境明确失败，不安装包、不回退。子进程沿用 sys.executable 与 PYTHON_BIN。

## 更新文件与影响范围

- scripts/project-python.sh、project_python_preflight.py、test_project_python.py、README.md：入口、检查、测试与帮助。
- scripts/validate-agent-context-budget.py：禁止技能示例回退裸 Python。
- 41 个已有 Python 示例的技能、AGENTS.md、rules/agent-context-budget.md、docs/08-command-execution-order.md、docs/standards/governance-feedback-loop.md、docs/README.md：统一执行入口和预检契约。
- openspec/changes/unify-governance-python-entry 与 sprint-013：交付追踪、范围与验收。

## 验证结果

隔离回归验证解释器选择、版本、依赖、失败前无写入、空格路径、参数/退出码、子进程继承、非根工作目录和示例回退。Change 内自动验收保存完整记录。中文、上下文预算、目录、规格、标题和 Sprint 范围校验通过；目录既有 SQLite legacy 警告保留。临时副本归档预演通过，不执行正式归档。

## 边界与后续

API/DB/Web/客户端/管理端/Orval/Docker Compose 无影响。容器及 CI 的真实镜像运行未执行，不把隔离测试说成部署验证。新增1人天，Sprint 达31/30人天，保留容量并提示无缓冲；建议低优先级增强延后。执行中范围工具追加缩进不兼容，已修正本次生成条目；建议后续单独完善该工具的列表缩进兼容测试，未自动创建后续 Issue/Change。收益处于待观察，未宣称 Token 或耗时节省。
