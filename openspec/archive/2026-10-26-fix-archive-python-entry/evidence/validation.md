---
title: 归档解释器隔离回归证据
created_at: 2026-10-26 12:57:16
updated_at: 2026-10-26 12:59:09
---

# 归档解释器隔离回归证据

## 运行与边界
10项统一入口测试通过，7项归档隔离测试通过。归档测试执行真实 archive-change.sh，门禁脚本和 OpenSpec CLI 使用临时替身；不代表真实产品权限、正式规格合并或生产端到端验收。

## 覆盖
- 默认项目解释器及显式 PYTHON_BIN；PATH 中 python/python3 故意失败但归档成功。
- 路径含空格、变量继承、参数/退出码、stdin、-c。
- 缺默认环境、无效显式环境、缺 PyYAML 时无门禁运行和目录迁移；门禁失败保留 active Change。
- 真正执行 safe_move heredoc、Sprint解析命令替换和 Usage管道，临时旧目录迁入规范目录。
- 7种裸 Python 注入、注释/文案/heredoc正文排除，以及统一导出缺失检查。

## 首轮差异
默认路径断言首次因 macOS 临时目录别名不等失败。两路径解析到同一文件；断言改为比较 resolve 后的路径身份，未放宽环境选择规则，复验7项通过。

## 数据与影响
本次不改业务 API、DB、UI、Docker、安全权限和客户端生成。product_data_collection_observability: N/A；affected_layers: []；临时夹具不进入长期证据，未复制原始会话。精确 Token 不可归因，不宣称效率收益。


## 原有恢复链路回归
15项 test_change_identity.py 全部通过，覆盖重复身份阻断、串行收尾、合并后中断续接、外部修改拒绝、跨文件系统迁移与Sprint用量归属。更新测试夹具以包含统一入口；两项旧夹具缺少恢复门禁要求的delta，已补全有效MODIFIED规格并保留原有断言。未修改恢复门禁实现。总计32项相关回归通过。
