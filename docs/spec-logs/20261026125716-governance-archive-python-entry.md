---
title: 归档脚本统一解释器接入补齐记录
created_at: 2026-10-26 12:57:16
updated_at: 2026-10-26 12:59:09
---

# 归档脚本统一解释器接入补齐记录

## 目标与原因
承接已归档 unify-governance-python-entry，补齐 archive-change.sh 内部裸 Python 遗漏；不重建统一入口。
## 修改范围
scripts/project-python.sh 增加内联执行转发；archive-change.sh 通过入口初始化并继承解释器；中央上下文校验增加纳管 shell 检查；test_project_python.py 与 test_archive_python_entry.py 及 tests/unit/test_change_identity.py 共提供32项回归。同步 AGENTS、规则、执行顺序、scripts README及文档索引。
## 验证
32项测试通过，覆盖真实 wrapper 在隔离替身环境下的成功、失败及内部调用。治理检查与自动验收结果以 openspec/changes/fix-archive-python-entry/trace.md 为入口。未执行真实项目归档；不将隔离执行冒充生产验证。
## 影响
API/DB/Web/客户端/管理端/Orval/Docker Compose/权限均无变更，无需迁移或生成。复用原入口与治理流程，保留工作区其他修改。
## 后续
本次只覆盖归档 wrapper；其他 shell 不宣称已迁移。真实后续归档按现有流程观察，未自动创建额外 Issue/Change。

