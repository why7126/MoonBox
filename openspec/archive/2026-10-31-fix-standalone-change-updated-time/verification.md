---
title: 独立 Change 可信时间实施验证记录
created_at: "2026-10-31 22:52:19"
updated_at: "2026-10-31 22:52:19"
---

# 独立 Change 可信时间实施验证记录

## 实施结果

时间解析按有效来源优先级只读投影；CardTime 使用生成类型并按上海时区显示来源。执行同步补缺 updated_at；共享 Change 文档写入无变化不写，保留缺失创建事实及首次完成时间。初始化已有真实时间维护，6项回归通过。归档后不追写历史时间。

## 验证记录

- 后端与治理：111项通过，含 execution、patch、change_time、change_visibility、requirement_summary、change_priority；随后补充摘要/完整直接API时间一致性用例通过，最终验收计划将形成完整机器记录。
- 前端：CardTime、优先级编辑、交付动作及卡片来源13项通过；Node 25 默认 webstorage 干扰测试，使用 NODE_OPTIONS=--no-experimental-webstorage 后复验通过，未修改产品行为或降低断言。
- tsc 与 Vite 构建通过；OpenAPI 导出及本地 Orval 生成成功。生成入口的缓存/包管理目录写权限不可用，改用临时 uv 缓存与已安装 Orval，无依赖下载。
- 真实产品：本地 /requirements 刷新后，sprint-016 原样本 fix-archive-finalization-consistency 显示“执行完成于 26/10/30 09:04”；来源 trace 仍无顶层时间，不修改归档样本。截图 product-* 与合成 synthetic-* 严格分开。
- 视觉签认：2026-10-31，AI 通过浏览器目视检查深浅主题×1440×900/390×844。来源文本、优先级、验收检查与禁用动作可读，窄屏时间单行，动作换行，无时间文本越出卡片。现有横向看板通过滚动查看，不将横向看板本身误报为时间溢出。
- 样式：.rc-updated 字号9px、行高10.8px、nowrap，继承主题 muted 色；footer gap与wrap及元素边界见 evidence/visual/computed-style.json。没有新增CSS。

## 运行环境与边界

本地已有 moonbox-backend 加载3份当前后端源码并重启，moonbox-web 加载本次 dist；没有创建临时容器、修改数据库、权限、真实环境配置或生产环境。API新增可选字段，无DB迁移。请求封装、请求日志、链路ID及90天保留语义保持，无新行为事件或Task Trace。客户端已同步。合成预览仅绑定本机临时端口，验收后停止，不进入生产构建。

全仓 Design System 存在既存原生控件/硬编码颜色违规；本次组件及页面聚焦扫描单独检查。历史SQLite目录为既存目录警告。不修无关规范，不创建后续Issue。

## 经验沉淀判断

本次规则已记录于 rules/document-governance.md 的“Change 业务时间与历史兼容”，根因与实现保留在 BUG 和本 Change。没有新的独立事故机制需要复制到 docs/knowledge-base/incidents/，因此不另建重复事故记录。

