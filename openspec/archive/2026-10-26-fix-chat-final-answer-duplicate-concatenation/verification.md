---
title: Chat 修复交付验证记录
created_at: '2026-10-26 19:11:33'
updated_at: '2026-10-26 19:11:33'
---

# Chat 修复交付验证记录

## 已执行验证
- SQLite：回答去重、内容存储、assistant投影首批27项通过；核验与可扩展结果67项通过；恢复与最终答案30项通过。随后最终追加保护的6项增量回归通过。
- MySQL 8.0.40：隔离容器67项通过，最终答案追加保护6项增量通过。使用临时内存数据，无生产连接。
- Web：自动核验10项、手动核验4项、结果分页1项，共15项通过；TypeScript编译通过。
- 真实Chromium 1440×900：隔离HTTP API、原DirectCompletion、真实completion_handoff.tick控制器，以合成终态/治理证明为样本；两次GET、零POST，观察待核验→validated，queue最终confirmed，合法重复措辞保留。见evidence/browser/browser.json与browser.png。
- 不声称执行过新的真实模型命令。test_chat_local_execution真实模型探针未启用而跳过；本次不为验证重放用户治理命令。
- Starlette弃用警告保留；Node默认实验webstorage造成现有分页测试环境错误，以NODE_OPTIONS=--no-experimental-webstorage运行通过，未改产品逻辑规避断言。

## 证据签认
已目视检查隔离浏览器截图：只展示一份答案，合法重复句保留，已核验状态与时间显示正确。截图是测试夹具布局，不是产品全页视觉验收；此修复不改布局/主题/弹窗，computed style专项N/A。现有产品会话观察单独追加。

## 组合回归修正与现有产品观察
组合验收发现test_projection_bounds_and_final_snapshot失败：受限事件读投影覆盖旧完整消息。已收紧为仅具备可信完整来源选择时覆盖旧消息，28项组合测试通过。
本地Chrome原BUG-0056会话更新后刷新，完整答案从两份变为一份，成果已核验标签正常；未重新发送原命令。点击复制按钮显示“已复制”，工具读取剪贴板为空，不能据此确认复制字节；复制载荷由前端回归独立核验，不伪造人工剪贴板结果。
