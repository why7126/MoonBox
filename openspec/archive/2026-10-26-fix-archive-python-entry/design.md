---
title: 归档解释器复用与隔离验证设计
created_at: 2026-10-26 12:55:09
updated_at: 2026-10-26 12:55:09
---

# 归档解释器复用与隔离验证设计

## 方案
project-python.sh 保留单一解释器选择、版本和依赖检查，新增 -c 与 - 的原样转发。archive-change.sh 参数检查后、任何治理命令或目录写入前，调用统一入口 -c 取得 PYTHON_BIN；导出给子进程，不修改全局 PATH、不安装包、不回退系统解释器。全部 Python 调用包括内联代码使用带引号的 PYTHON_BIN。
## 检查边界
中央校验对显式纳管的 archive-change.sh 检查统一启动和裸 python/python3 命令；注释与 heredoc 正文排除。词法检查不声称完整解析任意 shell，真实脚本隔离执行回归补足行为证明。其他 shell 不在本次迁移范围。
## 入口矩阵与验证
| 入口 | 正向与拒绝 | 证据 |
|---|---|---|
| 统一入口 | -c/- 参数、stdin、退出码、空格路径及无效环境 | test_project_python |
| 归档 wrapper | PATH 中坏 python 不被调用，默认/显式选择、子进程继承、迁移、管道 | test_archive_python_entry |
| 拒绝路径 | 缺失解释器/依赖或门禁失败，在迁移前停止 | 隔离目录断言 |
| 静态回退 | 普通调用、命令替换、管道、heredoc 启动行裸调用 | 负向夹具 |
## 数据采集声明
product_data_collection_observability: N/A

affected_layers: []

原因：只修复本地治理解释器选择，不改变产品采集或 Task Trace；validation：隔离测试只写临时夹具，长期证据仅保存摘要。
## 授权与范围
用户明确单次 spec-opt 授权。保留工作区既有修改；不执行本 Change 正式归档，不重复归档原 Change。历史生产归档路径已验证，当前验收用真实 wrapper 配合隔离门禁替身，不冒称生产端到端归档。

