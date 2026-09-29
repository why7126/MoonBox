---
title: Capture 图文候选审阅与确认采集提案
created_at: '2026-09-15 00:11:27'
updated_at: '2026-09-15 00:11:27'
---
# Capture 图文候选审阅与确认采集

## 变更动机

现有 Capture 要求用户预先填写类型、标题与分级，每次创建一条记录。REQ-0029 要求沿用 Codex `/capture` 的分类、拆分与整理效果，增加用户审阅，并将正式编号延后到最终版本确认后，避免误分类改号和重试重复创建。

## 变更内容

- 原始图文经无正式写入权限的 AI 整理形成未编号候选，保留来源依据。
- 增加服务端草稿保存与恢复、候选改类型、编辑、合并、拆分、删除和来源预览。
- 确认固定完整候选版本，服务端锁内分配最终类型编号，批量写入采集记录、注册表与索引。
- 保障业务确认唯一性、持久化写计划、向前恢复、完整快照读取屏障和授权来源保留。
- **BREAKING**：产品入口改为宽幅分步审阅，替换原有预填短表单和 840px 规格。授权单条兼容 API 可保留，候选整理不能调用该写入入口。
- 确认后只生成 capture.md、trace.md，正式 requirement.md / bug.md 继续留在 generate 阶段。

## 能力范围

### 新增能力

- `capture-candidate-review`：图文整理隔离、稳定候选与版本、确认幂等、批次恢复及来源追溯。

### 修改能力

- `web-catalog-requirement-center`：修改“Capture 新建与导入选择”，更新输入、尺寸、分级和反馈，保留文件导入与受控写入约束。

## 影响范围

来源为 `issues/requirements/review/REQ-0029-capture-multimodal-candidate-review/`，所属 sprint-007，分类 add。

```yaml
impact: { backend: true, web: true, miniapp: false, admin: false, database: true, storage: true, api: true }
```

涉及需求中心 Web、governance capture/writer、Codex 受限多模态执行、业务草稿/确认表、私有图片、OpenAPI/Orval、SQLite/MySQL 迁移及四层观测。复用 REQ-0028 图片传递基础前先验证当前代码，不将 Chat 整体交付设为前置。沿用项目 Bucket 和部署拓扑，补齐材料传递、清理及恢复配置文档。管理后台、小程序和移动端页面不在本期范围。

本次仅生成设计与任务，产品实现和 36 条验收仍待后续执行。
