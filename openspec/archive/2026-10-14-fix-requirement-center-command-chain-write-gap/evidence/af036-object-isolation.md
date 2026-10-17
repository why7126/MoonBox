---
title: AF-036 对象读取隔离验证
created_at: 2026-10-06 10:35:00
updated_at: 2026-10-06 10:35:00
---

# AF-036 对象读取隔离验证

## 根因与保留范围

BUG-0029 所有者空间鉴权通过，关联文件存在；未完成 Change 仅含 .openspec.yaml。旧全量扫描读取其缺失文档时抛出 403，污染原会话授权。修复按对象定向读取，列表逐项隔离；缺失文档返回 503，ACL、符号链接及路径越界保持 403。

未删除准备态文件、历史、快照或 unknown 轮次；未新建会话、未发送模型请求。

## 自动回归

- 后端 test_chat_incomplete_objects.py、test_chat.py、test_governance_candidates.py：90 passed、1 skipped，跳过项为需显式启用的真实模型测试。
- 前端 chat-events.test.ts：7 passed，覆盖空间拒绝、对象拒绝、未就绪与网络异常。
- 覆盖原会话消息/关联/候选读取、准备态目录保留、文档恢复、ACL 撤销、危险符号链接与活动轮次修改门禁。

## 真实运行态观察

- 标准 scripts/docker-down.sh self-storage-sqlite 与 scripts/docker-up.sh self-storage-sqlite 串行执行，退出码均为 0；Web、backend、chat-worker、governance-controller 已更新。
- 运行态只读数据库和服务核验：两个原 BUG-0029 会话历史授权通过，主对象正确，候选列表均有 77 项；准备态 Change 仍仅含 .openspec.yaml。
- Firefox 原页面刷新前复现空间权限错误；标准部署后刷新同一地址，实际截图及可访问性树确认错误消失、moonbox 已连接、主对象恢复。
- 原 bug-opsx 草稿保留，权限显示治理可写，发送按钮可用。该页面自身为空会话，不将空态描述为历史正文恢复；已有消息历史由 API 回归和原会话授权读取验证。
- 本批无布局或 CSS 修改；浏览器取证为真实产品，不以构造 DOM 替代。

## 边界

product_data_collection_observability: applicable；affected_layers: web、api、request_logs。沿用既有日志及业务码，无 DB schema/API 字段/客户端生成变化。未持久化会话标识、凭证或原始日志。未执行新业务命令，不宣称业务文档生成或状态流转已复验。
