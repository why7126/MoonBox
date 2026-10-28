---
bug_id: BUG-0065-chat-final-answer-duplicate-concatenation
title: 最终回答重复拼接根因分析
created_at: '2026-10-26 18:19:35'
updated_at: '2026-10-26 18:19:35'
root_cause_status: confirmed
---

# 最终回答重复拼接根因分析

## 根因状态

status: confirmed

## 现象

详见 [正式缺陷说明](bug.md)。

## 证据链

| id | type | source | 摘要 |
|---|---|---|---|
| E1 | screenshot | 同会话用户截图及 Chrome /chat | 正文完整重复，核验成功后仍重复 |
| E2 | data_sample | capture.md 与 bug.md 的只读统计 | 两片各354字、676字节、摘要相同，最终708字且两半相同 |
| E3 | runtime_log | bug.md 的片段时间及事件查询 | 第二片段与 reconcile:terminal 均为17:50:59 |
| E4 | code_path | execution.py 正常完成与 reconcile_unknown；content_store.py::result；assistant_output.py::saved_output | 来源前缀不同，来源去重失效，最终流全量拼接 |
| E5 | reproduction | 本次隔离 pytest，合成内容 answer、同一item身份 | 正常保存返回序号1，相同正常重放仍为1，恢复前缀返回2，saved_output为answeranswer；1 passed |
| E6 | config_diff | bug.md 三文件部署摘要核对 | 部署 API 与本地源码内容一致 |

## 已确认根因

正常完成使用 `final:item-id`，恢复使用 `recovered-final:item-id`；content_store.result 的去重键包含来源哈希，故同一逻辑答案两条路径无法命中同一片段。assistant_output.saved_output 将 final 流所有片段顺序拼接，形成重复正文。确认范围是上述跨路径重放机制；原真实事件的 item ID 未完整留存，不能断言两份真实事件原始 ID 相同。

## 已排除假设

仅前端重复渲染：存储消息已重复。相同来源键未去重：合成对照显示同键返回原序号。不能排除不同上游事件重复送达，但消费端仍需正确处理恢复重放。

## 修复方向

统一正常与恢复逻辑答案身份，定义最终版本替换与合法多片段边界，兼容历史投影。

## 验证闭环

1. 使用 test_chat.chat 临时 SQLite 夹具及 create/queued 创建合成轮次。
2. 调用 content_store.result(db,cid,tid,'final','final:same-item',0,b'answer') 两次，均返回1。
3. 再以 recovered-final:same-item 写入同一字节，返回2。
4. 调用 saved_output，断言当前结果为 answeranswer。

本次 pytest 1 passed，证明缺陷可复现，不是修复通过。夹具仅用临时数据库，未操作业务记录。存在一条第三方 Starlette 弃用警告，不影响断言。复现脚本运行于系统临时目录，未改 src/tests；后续 Change 应纳入正式回归测试。

## 剩余边界

机制已确认，历史原始时序缺口不伪造；修复后仍需合成回归及真实产品复验。
