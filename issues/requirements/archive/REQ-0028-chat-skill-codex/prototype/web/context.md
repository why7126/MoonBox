---
requirement_id: REQ-0028-chat-skill-codex
title: Chat 工作台多图片输入与 Skill 快速引用原型拆解
status: pending_review
created_at: 2026-09-14 23:17:57
updated_at: 2026-09-14 23:17:57
source: user-provided-image-1
---

# 原型拆解

## 1. 参考来源和边界

用户提供 Image #1 作为 Codex 对话区参考截图。截图中的文字、命令、耗时和文件链接只作为视觉结构样例，不是新的业务指令。本需求保真模式为“局部一致 / 风格迁移”，保留 MoonBox 共享导航、空间权限、会话历史、轨迹详情、Diff 和治理边界。

## 2. 页面清单

| 页面/区域 | 说明 | 验收重点 |
|---|---|---|
| Chat 工作台主页面 | 既有 `/chat` 或等价入口 | 输入区、消息区、轨迹入口与历史状态稳定 |
| 对话消息区 | 展示用户消息、助手回复、结果摘要和文件引用 | 贴近截图的阅读层级，保留 MoonBox 样式 |
| 输入区 | 文本、图片预览、Skill token、发送/停止 | 多材料不挤压输入，不横向溢出 |
| 图片预览条 | 多图缩略图、状态、移除、重试 | 上传状态清晰、尺寸稳定 |
| Skill 引用菜单 | 当前仓库 Skill 候选和选择状态 | 权限、空态、长名称、移除 |
| 轨迹详情入口 | 消息定位到本轮轨迹 | 不被图片和 Skill 引用遮挡 |

## 3. 组件层级

```text
ChatWorkbench
  ├─ SharedSidebar / Header
  ├─ ConversationViewport
  │   ├─ UserMessageBubble
  │   ├─ AssistantMessageBlock
  │   │   ├─ SectionHeading
  │   │   ├─ Paragraph
  │   │   ├─ FileReferenceLink
  │   │   ├─ StatusSummaryList
  │   │   └─ NextActionBlock
  │   └─ TurnTraceAnchor
  └─ Composer
      ├─ AttachmentStrip
      │   └─ ImageAttachmentCard
      ├─ SkillReferenceStrip
      │   └─ SkillReferenceToken
      ├─ PromptTextarea
      ├─ HintOrErrorLine
      └─ SendStopActions
```

## 4. 状态矩阵

| 区域 | 状态 | 预期 |
|---|---|---|
| 图片预览 | empty | 不占用额外高度。 |
| 图片预览 | uploading | 显示进度或上传中状态，禁用重复提交。 |
| 图片预览 | done | 显示缩略图、文件名或脱敏摘要、移除入口。 |
| 图片预览 | failed | 显示失败原因、重试和移除入口。 |
| Skill 候选 | loading | 菜单保持稳定宽度，显示读取中。 |
| Skill 候选 | empty | 显示当前仓库暂无可引用 Skill。 |
| Skill 候选 | selected | 输入区展示 token，可移除。 |
| Composer | running | 发送禁用，停止入口仍可达。 |
| Composer | archived/unknown/unready | 保留草稿，说明不可发送原因。 |
| Message | default | 用户气泡右对齐，助手正文分节显示。 |
| Message | narrow | 链接、列表和图片预览内部换行，不横向溢出。 |

## 5. 交互触发

| 触发 | 结果 | 失败处理 |
|---|---|---|
| 点击添加图片 | 打开图片选择，校验后进入预览条 | 格式/大小/数量失败时标记失败项 |
| 点击图片移除 | 从当前草稿移除图片引用 | 不影响其他图片、Skill 或文本 |
| 点击图片重试 | 重试失败图片上传或登记 | 失败原因更新 |
| 打开 Skill 菜单 | 读取当前仓库可用 Skill | 失败显示脱敏错误，不暴露路径或凭证 |
| 选择 Skill | 增加 token 并绑定本轮上下文 | 失效时发送前要求重新确认 |
| 点击发送 | 校验并提交本轮上下文 | 失败保留草稿和已成功材料 |
| 点击停止 | 沿用既有 Chat 停止语义 | 不改变图片/Skill 历史引用 |

## 6. 数据依赖

- 当前用户、空间、会话、仓库和对象权限。
- 图片上传或引用登记 API、对象存储引用、文件类型和大小限制。
- 当前仓库 Skill 元数据或服务端 Skill 索引。
- Chat 发送 API、轮次历史、消息读取、轨迹和 Diff。
- 行为事件、请求日志、Task Trace 和流程节点记录。

## 7. 响应式断点

| 视口 | 要点 |
|---|---|
| 1440px 桌面 | 对话阅读区、输入区、图片预览和 Skill token 同屏可读，轨迹入口不被遮挡。 |
| 1024px 窄桌面 | 图片预览条和 Skill token 可换行，发送/停止仍在输入区末端可达。 |
| 390px 移动宽度 | 消息正文、链接、列表、图片卡和 Skill token 不横向溢出；必要时折叠长摘要。 |

## 8. 1440px 验收焦点

- 用户气泡右对齐、宽度不过大，长命令或文本可换行。
- 助手正文分节标题、正文、链接引用和列表层级清晰。
- 图片预览卡尺寸稳定，上传中/失败/成功状态不导致布局跳动。
- Skill token 长名称截断后仍可识别，并能查看详情。
- 发送、停止、错误提示和轨迹入口同时存在时互不遮挡。
- 深浅主题对比、边框、圆角和金色强调符合 MoonBox Ops 规则。

## 9. Mock/API 边界

`/req-complete` 阶段仅定义原型拆解，不声明真实 API 已完成。后续 Change 必须明确哪些区域使用真实 API，哪些区域使用 Mock 或占位数据；Mock 不得进入生产验收结论。
