---
title: Chat 数据库锁竞争修复验证记录
created_at: '2026-10-27 09:03:09'
updated_at: '2026-10-27 09:03:09'
---

# Chat 数据库锁竞争修复验证记录

## 验证结果

| 证据 | 结果与边界 |
|---|---|
| SQLite聚焦回归 | 155通过，6个子测试；覆盖实际零行更新、2秒扫描屏障、20轮双读取/单写入、真实锁等待、有限重试、权限撤销、版本/代次围栏和提交后响应丢失 |
| 独立MySQL 8.2.0 | 82通过，真实数据库并发及同一事务矩阵；3次登记运行均清理并check为clean |
| 真实执行器新样本 | native codex-cli 0.153.4，独立测试身份/DB/工作区；90次并发核验，零核验失败，轮次completed，最终结果保存及再次读取一致，临时认证副本已删除 |
| 隔离浏览器 | 1440×900，合成业务身份与真实HTTP/Chromium；needs_review→validated，2次GET、0次POST，回答显示1份；目视确认成果已核验且原历史保留 |

长期证据为evidence/verification.json、live.json、concurrency.json、browser.json和browser.png。verification_evidence.py核对代码指纹与结果；原始日志、临时DB、认证和正文不入证据包。并发写入时延仅针对该隔离小样本，不是生产SLA或BUG-0056整体首屏性能结论。

## 失败诊断与处置

初轮测试启动使用stdin导致multiprocessing无法重入，且macOS临时目录别名被安全门禁拒绝；改用项目pytest入口与物理临时目录后通过。新事务授权复查要求旧mock补齐scope字段，已保持原行为断言并新增真实撤权用例。真实执行器首次因本机0.162.1不匹配、第二次因npm启动器隔离PATH缺Node而启动失败；临时安装固定版本并直接调用原生二进制后通过，不修改版本门禁。浏览器端口沙箱限制通过已授权独立临时HTTP验证解决。

扩展运行发现test_governance_board的两项既有文案断言失败：验收来源提示及待验证数量提示。对应requirement_center.py及该测试文件在本次和Git工作区均无改动，测试直接调用解析服务，不经过本次事务模块；保留为基线warning，未降低断言或修改无关业务。本次相关事务/恢复/权限回归全部通过。

## 交付范围与限制

仅修改核验事务、终态无效写入、短事务重试及脱敏诊断。无schema迁移、API响应结构、前端、部署拓扑或权限放宽；客户端生成N/A。数据库、API诊断、兼容矩阵和知识库已同步。现有业务服务未重启、未部署此源码，BUG-0056原轮次未重跑也未改写终态。原06:53失败SQL/线程仍不可恢复。

## 复现入口

使用项目Python入口运行src/backend/.venv/bin/pytest，目标test_verification_transaction.py及相关核验回归。MySQL仅显式独立测试库；真实执行器需CHAT_LIVE_ISOLATED_PROBE=1与固定版本可执行文件，使用项目local_probe临时认证工具；临时资源按登记流程清理。证据检查命令：bash scripts/project-python.sh src/backend/tests/verification_evidence.py。
