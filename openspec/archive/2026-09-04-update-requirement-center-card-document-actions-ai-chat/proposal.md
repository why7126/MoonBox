---
change_id: update-requirement-center-card-document-actions-ai-chat
source_requirement: REQ-0020-requirement-center-card-document-actions-ai-chat
change_type: update
status: proposed
created_at: 2026-08-18 09:58:34
updated_at: 2026-08-18 09:58:34
---

# Proposal: 需求中心卡片文档查看、动作流转与 AI 聊天增强

## 背景

REQ-0012 已提供前台需求中心 9 阶段看板和卡片骨架，REQ-0013 已接入真实治理数据。当前需求中心仍缺少日常治理闭环所需的卡片行为：Capture 新建、Markdown/HTML 文档入口、阶段动作与 Slash Command 映射、AI 聊天反馈、生成/完善导入校验、Sprint 选择、`tasks.md` 进度查看、受限验收和归档详情跳转。

REQ-0020 已完成评审并纳入 `sprint-003`。本 Change 将该需求转换为 OpenSpec 实现合同，后续由 `/opsx-apply REQ-0020-requirement-center-card-document-actions-ai-chat` 实现。

## 目标

- 在前台需求中心补齐卡片级文档查看与阶段动作交互。
- 通过全局 AI 聊天抽屉承载命令发送、执行反馈和异常分支。
- 让 Requirement 与 Bug 卡片动作严格映射到 `req-*`、`bug-*`、`sprint-*` 和 `opsx-*` 流程。
- 建立 Markdown/HTML 文档入口、文件导入校验、按钮 Loading/锁定和失败不流转规则。
- 补齐 `tasks.md` 只读/受限验收抽屉和归档流转门禁。
- 将“已通过”展示文案统一为“已评审”，不改变底层 `approved` 状态语义。
- 承接 prototype-driven UI gate，保证 UI Contract、UI Skeleton、1440px 验收、Mock/API 边界和最终一致性检查可执行。

## 非目标

- 不改变 REQ、BUG、Sprint 或 OpenSpec 的底层状态机事实源。
- 不绕过 REQ/BUG 评审、Sprint 纳入、OpenSpec apply/archive 等治理门禁。
- 不建设完整 AI Agent 编排系统、长期聊天历史、多人协同聊天或通知中心。
- 不新增移动端、桌面端、微信小程序或管理后台需求中心页面。
- 不暴露本机绝对路径、系统用户名、密钥、token、`.env` 内容、未脱敏日志或内部异常堆栈。

## 影响范围

```yaml
impact:
  backend: true
  web: true
  miniapp: false
  admin: false
  database: false
  storage: false
  api: true
capabilities:
  new:
    - 需求中心全局 AI 聊天抽屉
    - Markdown 文档右侧抽屉
    - HTML 文档新 Tab 预览入口
    - Capture 新建表单
    - 生成/完善方式选择与文件导入校验
    - Sprint 选择弹窗
    - tasks.md 进度抽屉与受限验收
  modified:
    - 前台需求中心 9 阶段展示文案
    - 卡片阶段动作与命令映射
    - 需求中心真实数据对象字段与文档预览安全边界
```

## 估算

- 规模：M
- Story Points：3
- 人天：3
- Sprint：`sprint-003`

## 风险

- 卡片动作涉及多个治理命令，前端必须展示产品化动作文案，同时保留可追溯命令映射，避免将内部命令直接变成唯一用户交互。
- 文档预览和文件导入存在安全边界，必须由后端或安全客户端路径控制，不能直接透传本机路径。
- UI 抽屉、弹窗、toast 与看板横向滚动并存，容易出现遮挡、冒泡、布局跳动和文本溢出，必须先完成 UI Skeleton 与 1440px 验收。

## 交付物

- `design.md`：UI Contract、UI Skeleton、冲突处理、Mock/API 边界和测试策略。
- `tasks.md`：先 UI Skeleton 后实现细节，覆盖后端、前端、测试、文档和验收。
- `specs/web-catalog-requirement-center/spec.md`：修改前台需求中心卡片行为与阶段动作要求。
- `specs/web-catalog-requirement-center-real-data/spec.md`：修改真实数据接口字段、安全读取和任务进度支持。
