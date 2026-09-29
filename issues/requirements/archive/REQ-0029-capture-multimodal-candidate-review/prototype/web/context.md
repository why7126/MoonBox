---
requirement_id: REQ-0029-capture-multimodal-candidate-review
title: Capture 原型拆解与交互约束
created_at: '2026-09-14 11:17:44'
updated_at: '2026-09-14 11:17:44'
---
# 原型拆解与交互契约种子

## 页面清单与用途

单个 `prototype.html` 演示三个状态：原始材料（步骤 1）、审阅候选（步骤 2，默认落点）、创建结果（步骤 3）。真实入口来自需求中心“新建 Capture”，打开宽幅分步工作区；不新增正式路由承诺。

原型使用离线演示项目与合成反馈。所有 AI 整理和编号均为模拟，上传仅浏览器 object URL 预览，保存仅 localStorage 演示；图片不跨刷新保留且页面提示该限制。产品需要服务端自动保存完整材料与候选，并满足 `requirement.md` 的全部边界。原型不包含账号、真实客户图文或 API 连接，不写 Issue。

## 关键区域与组件层级

```text
页面壳：顶栏 / 面包屑 / 原型说明
  工作区 .workspace：标题 / 三步导航
    .layout
      aside：来源标签 / 原文 / 图片缩略预览 / 返回材料
      .content：输入表单 或 候选列表 或 批次结果
        .candidate：勾选 / 序号 / 类型 / 分级 / 标题 / 描述 / 来源 / 动作
    .footer：保存状态 / 次动作 / 唯一主操作
  dialog#modal：编辑 / 合并 / 拆分 / 删除 / 确认 / 来源
  #toast：固定反馈，不参与布局
```

## 状态矩阵与触发

| 组件 | 状态 | 触发与响应 |
|---|---|---|
| 输入 | empty/filled/invalid | 空材料不可整理，字数和图片限制提示 |
| 上传 | idle/uploading/done/failed | 原型仅模拟选择预览，产品需完整上传状态；上传失败保留其他图片 |
| 草稿 | saving/saved/failed/conflict | 原型 1 秒本地保存；产品最长 5 秒保存和版本冲突门禁由 API 实现 |
| 整理 | idle/loading/failed/ready | 原型显式说明固定候选，产品执行真实模型并校验结果 |
| 候选 | default/selected/empty/edited | 勾选至少 2 条才可合并；删除全部禁用确认 |
| 编辑 | open/invalid/saved/cancelled | 显式保存与取消，改类型重置目标分级建议；保留原内部 ID |
| 合并/拆分 | open/invalid/saved | 新 ID 保存父来源；产品补齐图片证据分配与完整来源边 |
| 来源 | open/closed | 可点击外部或关闭，内部点击不关闭 |
| 确认 | summary/accepted/conflict | 原型演示固定集合，产品保存版本未完成或冲突时禁止受理 |
| 创建 | creating/failed/done | 原型勾选模拟中断后可重试原任务；产品还有 recovery_blocked、权限失败 |
| 主题/视口 | dark/light/desktop/mobile | 主题按钮切换，窄屏单列布局 |

产品需要补齐的状态不以原型未模拟为删减依据。读写权限、草稿列表/主动删除、服务端保存失败、50 条候选、仅图片理解及多文件恢复按 PRD 和 AC 实现。

## 动作按钮 → modal 类型 → selector → 状态 → 验收证据

| 动作 | 类型 | 触发器 → 容器/主操作 | 状态 | 证据计划 |
|---|---|---|---|---|
| 新建 Capture | 分步工作区 | 既有新建入口 → `[data-testid=capture-workspace]` | 开/关/只读/恢复 | 实施 Skeleton + 入口截图 |
| 查看/编辑材料 | N/A 步骤切换 | `#back-input` → `#raw` | default/disabled | 原型交互检查，产品权限 AC |
| 图片选择/移除 | 系统选择器/inline | `#files`、`[data-image]` → `.thumbs` | 空/预览/失败 | 上传实链证据 AC-XCUT |
| 编辑/改类型 | dialog | `[data-edit]` → `#modal`、`#etype`、`#modal-ok` | open/invalid/saved/cancel | 原型改类型检查 + 实施截图 |
| 合并所选 | dialog | `#merge` → `#merge-title`、`#modal-ok` | disabled/open/saved | 原型合并检查 + 来源断言 |
| 拆分 | dialog | `[data-split]` → `#split-a`、`#split-b`、`#modal-ok` | open/invalid/saved | 原型拆分检查 + 来源断言 |
| 删除候选 | confirm | `[data-remove]` → `#modal-ok` | open/cancel/deleted/empty | 产品空态、无共享图片误删 |
| 查看来源 | dialog preview | `[data-source]` → `#modal`、`#modal-cancel` | open/closed | 原型捕获阶段外部退出检查 |
| 确认创建 | confirm | `#confirm` → `#modal-ok` | disabled/summary/creating | 原型确认 + 产品版本并发 AC |
| 重试原任务 | inline | `#retry` → `.result` | failed/creating/done | 原型演示 + 实际恢复证据 |
| 关闭保留 | N/A 退出工作区 | `#close` | saving/saved/failed | 原型保存演示；产品恢复入口 |
| 恢复/删除草稿 | 选择器/confirm | 产品待分配 selector，不在当前演示中 | 有草稿/空/确认/被任务占用 | 实施前补齐组件族，AC-008/017 |

编辑、拆分、合并、删除和最终确认涉及数据调整或批量副作用，故保留显式主操作与取消；不使用原生 window.confirm。来源预览无数据提交，可以轻量退出。来源弹窗内部点击 stopPropagation，document pointerdown 使用捕获阶段及坐标边界判断外部退出；编辑类不以点击遮罩丢弃输入。原生 dialog 负责焦点约束与 Esc，实施使用项目 Dialog 组件保持焦点恢复。

## 数据依赖与事实源

输入能力、项目/用户授权、材料 ID、候选稳定 ID/父来源、revision、确认任务、最终映射及保存时间来自服务端。UI 不生成正式编号，不把演示列表写入正式看板。关闭后的任务继续由服务端管理；同批同版本唯一确认保障不依赖前端禁用。

## 响应式与 1440px 焦点

- 1440px：工作区最大 1200px、材料列 320px，内容列自适应；工作区头/脚与内容滚动分离，阅读密度稳定。
- 1024px：保留双列并缩减外侧边距，长正文折行；超过内容高度内部滚动。
- 900px 以下：材料与候选单列，来源区限高滚动；500px 以下操作栏纵向、按钮换行。
- 390px：标题、选择框、卡片动作和确认栏无横向溢出；确保来源和编辑弹窗可读。
- 矮视口：dialog 最大 85vh 且内部滚动；固定主操作不得遮住正文或阻止关闭。
- 1440px 重点：金色仅强调主动作/步骤，深浅主题对比、输入面区别、候选密度、两个并列区域与底栏对齐、toast 不引发布局偏移。

## UI Reference Replication Contract 种子

保真模式为局部一致：复用现有 MoonBox Ops 的颜色、字体、近直角、细边框及按钮层级；本需求未提供附件截图，不声明一对一复刻。

事实源优先级：用户确认业务边界 → requirement/acceptance → 本 context 交互约束 → prototype 结构 → rules/ui-design.md 与当前设计 token；样式冲突遵循项目 token，先更新原型说明。既有页面只作为风格基线，不复刻看板布局。

| 对照组件 | 参考入口/selector | 原型 selector | 后续实现 |
|---|---|---|---|
| 工作区与动作 | 当前 `.rc-capture-dialog`、`.rc-dialog-actions` | `.workspace`、`.footer` | 在 Change 中映射实际组件与 test selector |
| 主题/按钮 | `rules/ui-design.md`、`Button.tsx` | CSS 变量、`.primary` | 复用项目 token 和 Button |
| 来源/候选 | 本原型新增语义 | `aside`、`.candidate`、`.source-link` | 建立新组件 selector 映射 |
| 编辑与确认 | 项目浮层交互规范 | `#modal` | 统一 Dialog/Confirm 组件族 |

非目标：不重建共享导航，不修改其他需求中心阶段，不改 Chat 视觉，不牺牲版本/权限/真实写入边界。

## Computed style 采样清单与分批验收

| 批次 | selector | 属性与期望 | 当前证据/后续门禁 |
|---|---|---|---|
| 工作区 | `.workspace`、`.layout` | width ≤1200px、两列 320px/自适应、字体 14px、细边框 | 原型 QA 可采样；真实 Skeleton pending |
| 候选与动作 | `.candidate`、`.primary`、`.footer` | padding 17px/18px、圆角2px、金色、行高1.45、底栏不漂移 | 真实截图/computed style pending |
| 浮层 | `#modal` | 宽≤610px、高≤85vh、overflow auto、焦点和捕获退出 | 原型交互核验；真实实现 pending |
| 响应式 | `.layout`、`.card-foot` | 390px无横向溢出，深浅主题可读 | 原型截图不替代真实验收 |

## 原型验证与 Readiness

本次离线原型 QA 已通过 10 项检查，见 `prototype-qa.json`。已导出 `review-1440.png`、`review-light-1440.png`、`result-1440.png`、`review-390.png`；桌面深色和移动端浅色截图已人工查看，无横向溢出，区域层级与操作可读。PNG 仅为原型审阅辅助，不是产品视觉验收。

原型拆解 done。真实 UI Skeleton、1440px 视觉与 REQ 最终实现一致性均 pending；Readiness 为 Partially Ready，不阻塞进入需求评审。验收清单中的产品 AC 全部保持未勾选。
