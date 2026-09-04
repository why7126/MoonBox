---
requirement_id: REQ-0020-requirement-center-card-document-actions-ai-chat
title: 需求中心卡片文档查看、动作流转与 AI 聊天增强
owner: product
created_at: 2026-08-18 09:44:53
updated_at: 2026-08-18 09:44:53
---

# 业务流程

## 总流程

```text
用户进入需求中心
  |
  +-- 新建 Capture
  |     |
  |     +-- 标题校验失败 -> 表单内提示 -> 留在表单
  |     |
  |     +-- 创建成功 -> 采集池新增卡片 -> 展示成功反馈
  |
  +-- 点击卡片标题 / 查看归档
  |     |
  |     +-- 新 Tab 打开对象详情
  |
  +-- 点击关联文档
  |     |
  |     +-- .md -> Markdown 右侧抽屉
  |     +-- .html -> 新 Tab 预览
  |     +-- 异常 -> AI 聊天或抽屉展示错误，不流转
  |
  +-- 点击阶段动作
        |
        +-- 选择生成/完善方式或迭代
        |
        +-- 校验失败 -> AI 聊天展示异常 -> 卡片不移动
        |
        +-- 执行 Slash Command
              |
              +-- 成功 -> 刷新数据 -> 卡片按状态机流转
              +-- 失败 -> 保持原阶段 -> AI 聊天展示失败原因
```

## 阶段流转

```text
采集池
  -> 规划中       req-generate / bug-generate 或合法导入
  -> 待评审       req-complete / bug-complete 或合法文档包导入
  -> 已评审       req-review / bug-review approve
  -> 迭代规划     sprint-propose + Sprint 选择
  -> 待开发       req-opsx / bug-opsx
  -> 研发中       opsx-apply
  -> 验收中       任务执行完成并进入验收
  -> 已完成       opsx-archive
```

分析类动作 `/req-explore` 和 `/bug-explore` 不改变卡片阶段。

## 与父 REQ 差异

| 项 | REQ-0012 基线 | REQ-0020 增强 |
|---|---|---|
| 卡片动作 | 原型级主动作 | 完整 Slash Command 映射、Loading、锁定和失败分支 |
| 文档查看 | 基础关联文档展示 | Markdown 抽屉、HTML 新 Tab、文件异常处理 |
| AI 交互 | 无全局聊天入口 | 全局 AI 悬浮按钮与右侧聊天抽屉 |
| 导入 | 未明确 | 生成/完善方式选择与文件导入校验 |
| 进度 | 展示任务摘要 | `tasks.md` 只读/受限验收抽屉 |
| 阶段文案 | 已通过 | 已评审 |

## 数据依赖

- Requirement / Bug 卡片基础字段来自需求中心真实数据聚合接口。
- 文档列表来自治理对象关联文档白名单。
- Markdown/HTML 内容通过安全文档读取或预览接口获取。
- 阶段动作结果来自 AI 命令执行反馈和刷新后的治理事实源。
- Sprint 选择来自未关闭迭代列表。
- `tasks.md` 进度来自关联 OpenSpec Change 的任务文件解析结果。

## 异常分支

- 标题缺失：阻止 Capture 创建。
- 文件类型不符：阻止导入或打开，并显示校验异常。
- 文件缺失/读取失败：不流转状态，展示可恢复错误。
- 命令执行失败：按钮解除锁定，卡片保持原阶段。
- Sprint 不合法：阻止加入迭代。
- `tasks.md` 缺失：展示不可查看原因。
- 验收门禁未满足：不展示或禁用归档动作，并说明阻塞项。
