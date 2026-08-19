---
req_id: REQ-0020-requirement-center-card-document-actions-ai-chat
status: captured
created_at: 2026-08-18 09:34:10
updated_at: 2026-08-18 09:34:10
recorded_by: product
source: 用户输入
priority_hint: P1
parent_requirement: REQ-0012-frontend-requirement-center
---

# 一句话

增强需求中心卡片的新建、文档查看、阶段流转、全局 AI 聊天和异常反馈交互，补齐从采集到受限验收与归档的前台操作闭环。

# 原始描述

新增需求中心卡片的文档(markdown，html)查看、按钮交互，卡片流转、全局AI聊天悬浮。具体内容如下：

- 新增 Capture 新建表单、标题必填校验、创建反馈及采集池卡片插入。
- 将卡片关联文档中的 Markdown 文件转换为可点击入口，Markdown 文档展示容器由居中弹窗调整为右侧抽屉
- 将卡片关联文档中的 Html 文件转换为可点击入口，Html 文档实现新Tab点击打开
- 新增全局 AI 聊天悬浮按钮、右侧聊天抽屉与消息发送交互。
- 建立卡片阶段动作与 req/bug/opsx/sprint Slash Command 的完整映射。
- 新增统一 Loading、按钮锁定、AI 反馈、成功流转及文件异常分支。
- 新增生成/完善方式选择、文件导入校验和迭代选择。
- 新增 tasks.md 只读进度抽屉、受限验收及归档流转。
- “已通过”更名“已评审”，卡片标题与查看归档支持新 Tab 详情。

# 待澄清

- [ ] 需求中心卡片阶段动作是否覆盖 REQ、BUG、Sprint、OpenSpec Change 的全部状态，还是先聚焦 REQ 主链路。
- [ ] Markdown/HTML 文档入口的数据来源、权限边界和文件不存在/解析失败时的统一提示文案。
- [ ] 全局 AI 聊天是否需要接入真实 Agent 会话与历史记录，还是先实现前台交互壳和消息发送反馈。
- [ ] 迭代选择的数据源和可选范围，是否允许选择 planning / in_progress 以外的 Sprint。
- [ ] 受限验收与归档流转的门禁规则、失败态文案和可重试动作。

# 探索结论

（/req-explore 后人工确认写入）
