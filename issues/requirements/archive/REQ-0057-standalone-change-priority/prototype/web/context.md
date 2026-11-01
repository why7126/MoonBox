---
title: 独立 Change 优先级原型拆解与交互契约
created_at: '2026-10-30 09:48:10'
updated_at: '2026-10-31 21:45:00'
---

# 独立 Change 优先级原型拆解与交互契约

## 定位与事实源

局部一致模式：复用 MoonBox Ops token、卡片信息层级；用户截图仅为现象证据，不要求整页一对一复刻。事实源顺序为本 REQ 业务要求及验收、本文交互契约、prototype.html、项目 token、现有页面；冲突先校核业务边界。原型是卡片区域示意，页面壳/侧栏/其他列均不重设计。

## 页面、组件和数据

生产入口 /requirements；原型只有本地 HTML。主区域含说明、演示状态/主题/筛选控件、独立卡片、优先级标签、负责人、设置按钮、内联编辑区及固定反馈区。演示控件不进入正式产品。

组件树：main → toolbar → article → header / metadata / details / inline-editor → select + feedback + actions；全局 toast 为 fixed。生产复用 src/web/src/components/ui/Button.tsx 和 tokens.generated.css；原型不导入应用运行时。

依赖：项目身份、Change ID、来源关系、priority、owner、可见/写权限、归档状态与版本。所有原型值为内存 Mock；无网络、无本地持久化，不证明 API 已接入。

## 动作矩阵与 selector 种子

| 动作 | 类型 | selector | 状态 | 后续证据 |
|---|---|---|---|---|
| 设置优先级 | inline-expanded | #edit / #editor | default/open/readonly | 截图、键盘、权限断言 |
| 保存 | inline-expanded | #save / #level | idle/saving/error/conflict/success | API回读、重复提交、样式 |
| 取消、Esc | 关闭内联区 | #cancel / #editor | open/error | 无保存、焦点回设置按钮 |
| 冲突后重载 | inline-expanded | #reload | conflict | 最新版本替换草稿，重新选择 |
| 分级筛选 | select | #filter | all/P0-P3/missing/invalid/empty | 筛选与刷新一致 |

生产 selector 候选使用 data-testid=change-priority-edit/editor/save/cancel/reload，卡片沿用 data-issue-id；实施建立最终映射。其他阶段按钮非本次动作族，不在原型假装已接通。

## 状态矩阵

正常四档、缺失、非法、只读、归档、保存中、网络失败、冲突及筛选空态。内联编辑由显式保存提交，因为存在异步校验、冲突和必要变更记录；不是临时筛选。取消/Esc 不写数据；外部点击不关闭，因此不声明 click-outside；键盘可达、焦点返回。切换项目后忽略旧对象迟到回包。

## 响应式与视觉采样

1440×900：主内容最大1120px，卡片最大560px，24px间距，近直角8px上限，金色主动作；390×844：外边距16px，卡片宽度自适应，长 ID 换行，操作换行。低高度编辑区保留自然滚动，toast不挤布局。

采样候选：#card、#badge、#editor、#save、#toast；属性 font-family/font-size/line-height/padding/gap/border/background/color/width/overflow/position。深浅 token 沿 rules/ui-design.md，按钮半径取生成 token 的2px；所有期望为设计值，未声称实际样式采样。

## 分批验收与门禁

第一批：卡片/标签/缺值及筛选；第二批：编辑/保存/错误/冲突/取消；第三批：只读/归档/窄屏/深浅主题及真实 API。每批包含 selector、状态、截图及样式证据。原型拆解完成；UI Skeleton 未实现、1440px 产品视觉待验证、REQ最终实现一致性待验证。PNG 本阶段暂不要求，后续 UI 实现必须采集截图，不以本 HTML 替代。



## 异步保存实施约定
已确认保留服务端维护窗口和异步控制器。未就绪提示暂不可保存；入队后显示保存中，完成后回读卡片。关闭编辑区不撤销已提交操作，重新读取以服务端事实为准。必要审计随trace原子提交，异步链路复用Task Trace；不新增数据库表。UI Skeleton首轮结构已获用户确认。
