---
title: 需求中心文档抽屉移除 Change 属性模块 - 规格变更
created_at: 2026-09-15 23:32:00
updated_at: 2026-09-16 08:45:49
---

# 需求中心文档抽屉移除 Change 属性模块 - 规格变更

## MODIFIED Requirements

### Requirement: 卡片文档查看与详情跳转

系统 MUST 支持从需求中心卡片安全查看关联 Markdown/HTML 文档，并支持卡片标题和归档入口新 Tab 打开对象详情。Markdown 文档抽屉 MUST 只承载当前文档阅读、文档属性和既有编辑能力，不得在正文前渲染 Change 追溯属性模块。

#### Scenario: Markdown 文档从右侧抽屉打开

- **WHEN** 卡片关联文档包含 `.md` 文件
- **THEN** 文件名必须展示为可点击入口
- **AND** 点击后必须从右侧打开 Markdown 文档抽屉
- **AND** 抽屉必须展示当前对象 ID、文件名和文档内容
- **AND** 抽屉打开后必须显示背景蒙层
- **AND** 桌面端抽屉必须支持 420px-760px 范围内拖拽调整宽度，移动端必须使用全屏宽度
- **AND** 文件点击不得冒泡触发卡片详情或阶段动作

#### Scenario: Markdown 文档抽屉不展示 Change 属性模块

- **GIVEN** 用户打开 REQ、BUG 或独立 Change 的 Markdown 文档抽屉
- **WHEN** 文档抽屉完成加载
- **THEN** 抽屉正文前必须只保留文档属性区和当前文档正文
- **AND** 抽屉不得渲染“Change 追溯属性”标题、模块边框、左侧色条、任务进度文案、告警分隔符、关联 Change 列表或模块内 Change 文档按钮
- **AND** 文档属性区必须继续使用面向用户的“文档属性”标题，并保留展开/收起能力
- **AND** 删除模块后不得保留空白占位、残留分隔线、贴边文本或正文顶部断层

#### Scenario: 抽屉外 Change 文档入口保持可达

- **GIVEN** REQ 或 BUG 关联一个或多个 Change
- **WHEN** 用户需要查看关联 Change 的 proposal、design、tasks 或 Change trace
- **THEN** 系统必须通过抽屉外的卡片、详情或既有文档分组入口提供可达路径
- **AND** 卡片侧关联 Change 文档入口必须保持紧凑，使用直接紧凑文档入口承接，不得在卡片上展开完整 Change ID
- **AND** Issue 自身文档与关联 Change 文档合并展示时，`proposal.md`、`spec.md`、`design.md`、`tasks.md`、`sprint.md` 等非 trace 同名文档必须按文件名和语义去重
- **AND** 多 Change 场景不得默认选择第一个 Change
- **AND** 系统不得把多个 Change 的任务进度汇总成单个 Change 的进度
- **AND** Issue trace 与 Change trace 的入口标签或上下文必须可区分

#### Scenario: 采集池 capture.md 受控编辑保存

- **GIVEN** 用户打开采集池阶段对象的 `capture.md`
- **WHEN** 文档抽屉完成加载
- **THEN** 系统必须默认展示 `capture.md` 预览内容和“编辑”按钮，不得直接进入编辑器
- **WHEN** 用户点击“编辑”后修改内容并保存
- **THEN** 系统必须通过受控 API 保存 `capture.md`
- **AND** 保存成功后必须展示成功反馈，回到预览态，并用服务端返回内容更新抽屉预览
- **AND** 再次打开该文档必须回显最新内容
- **AND** 用户关闭存在未保存修改的抽屉前必须出现确认提示
- **AND** `trace.md`、非采集池阶段 Markdown 或非 `capture.md` 文件必须保持只读且保存请求必须被阻断

#### Scenario: HTML 文档从新 Tab 打开

- **WHEN** 卡片关联文档包含 `.html` 文件
- **THEN** 文件名必须展示为可点击入口
- **AND** 点击后必须在新 Tab 打开受控 HTML 预览或详情页面

#### Scenario: 文档抽屉视觉与权限回归

- **WHEN** 文档抽屉在 1440px、窄视口、深色主题或浅色主题下展示
- **THEN** 文档属性、正文、关闭、全屏或恢复、滚动和长标题/长 ID/长正文不得重叠或溢出
- **AND** 实现必须提供 1440px 与窄视口视觉证据，以及文档属性区和滚动容器的 computed style 或等价检查
- **AND** 无权对象、只读成员、冻结空间、跨项目同 ID 和直接文档 URL 不得因模块删除暴露受限内容
