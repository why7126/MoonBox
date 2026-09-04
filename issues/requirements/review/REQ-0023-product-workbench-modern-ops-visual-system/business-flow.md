---
requirement_id: REQ-0023-product-workbench-modern-ops-visual-system
title: MoonBox 产品工作台全面升级为现代 Ops 视觉系统 - 业务流程
created_at: 2026-08-30 23:24:18
updated_at: 2026-08-30 23:24:30
owner: product
---

# 业务流程

## 总体流程

```text
品牌方向确认
  -> 现代 Ops 视觉系统定义
  -> 设计 token 与组件规范调整
  -> 需求中心 / 工作台 Shell 试点
  -> 1440px 与关键交互视觉验收
  -> 管理后台与其他登录后页面迁移
  -> UI 规则、设计系统文档和验收标准同步
```

## 品牌分层流程

```text
识别页面类型
  -> 公开品牌叙事页
      -> 保留 MoonBox 宝盒感、品牌插画、克制叙事
  -> 登录后产品工作台
      -> 使用现代 Ops token、密集导航、状态卡、看板和工具型组件
  -> 管理后台
      -> 与工作台共享 Shell、列表、弹窗、toast 和状态组件规范
  -> 产品手册
      -> 仅同步必要品牌识别，不强制承载高密度工作台组件
```

## 设计系统迁移流程

```text
现有 token 盘点
  -> 定义现代 Ops token 分层
  -> 组件映射
      -> Sidebar / Header / Stats / Toolbar / Kanban / Card
      -> Popover / Drawer / Modal / Toast / Empty / Loading
  -> 试点页面落地
  -> 深浅主题与 computed style 验收
  -> 旧 token 下线或保留范围声明
```

## 与既有需求差异

| 关联需求 | 已有能力 | 本需求差异 |
|---|---|---|
| REQ-0000-build-design-system | 建立基础设计系统 | 本需求可能重定义品牌定位、token、组件规范和验收标准 |
| REQ-0012-frontend-requirement-center | 9 阶段需求研发流转看板 | 本需求将需求中心作为现代 Ops 试点，但目标超出单页看板 |
| REQ-0020-requirement-center-card-document-actions-ai-chat | 卡片动作、文档查看、AI 聊天增强 | 本需求统一这些工作台组件的视觉系统和交互层级 |
| REQ-0021-markdown-editor-vditor-enhancement | Markdown 编辑体验增强 | 本需求要求编辑器外壳、抽屉和工具栏纳入现代 Ops 视觉一致性 |

## 关键决策点

| 决策点 | 推荐 | 说明 |
|---|---|---|
| 品牌范围 | 双品牌分层 | 公开页保留品牌叙事，登录后工作台全面现代 Ops 化 |
| 试点范围 | 需求中心 + 工作台 Shell | 信息密度最高，最能验证附件风格价值 |
| 迁移节奏 | 分阶段 | 先 token 与核心组件，再扩展页面，降低全站一次性返工 |
| 回退策略 | 保留旧主题映射一轮迭代 | 便于视觉验收失败时快速降级 |
