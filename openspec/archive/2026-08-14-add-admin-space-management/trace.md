---
change_id: add-admin-space-management
source_requirement: REQ-0017-admin-space-management
status: applied
created_at: 2026-08-12 21:26:00
updated_at: 2026-08-14 16:11:09
sprint: sprint-002
change_type: add
prototype_refs:
  - issues/requirements/review/REQ-0017-admin-space-management/prototype/web/prototype.html
  - issues/requirements/review/REQ-0017-admin-space-management/prototype/web/prototype-context.md
  - issues/requirements/review/REQ-0017-admin-space-management/prototype/web/interaction.md
  - issues/requirements/review/REQ-0017-admin-space-management/prototype/web/prototype.png
knowledge_base_refs:
  - docs/knowledge-base/best-practices/admin-list-page-consistency.md
  - docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md
ui_contract: done
ui_skeleton: done
visual_acceptance_1440: done
computed_style_acceptance: done
mock_api_boundary: real_api_connected
req_final_consistency: done
---

# Trace

## Requirement Readiness Report

| 项 | 结论 |
|---|---|
| status | in_sprint |
| requirement.md | ready |
| user-stories.md | ready |
| business-flow.md | ready |
| acceptance.md | ready |
| prototype_refs | ready |
| prototype_gate | decomposition done；skeleton/visual/final consistency pending |
| readiness | ready |

## Impact Analysis

```yaml
impact:
  backend: true
  web: true
  admin: true
  database: true
  storage: false
  api: true
capabilities:
  new:
    - web-admin-space-management
  modified:
    - web-admin-crud-list-template: reuse only
    - web-admin-user-management: reference only
change_type: add
```

## Conflict Resolution

事实源优先级：`prototype.html > prototype.png > prototype-context.md / interaction.md > acceptance.md > ui-design.md > openspec/specs`。

- 视觉 token 以 prototype-context 最新增量和 `rules/ui-design.md` 为准。
- 右侧内容区不得保留旧 `.top` 空白容器。
- 空间详情概览中基础信息、配额与用量、最近操作必须是独立卡片。
- API 路径以项目 `/api/v1/admin/**` 前缀落地，前端封装隐藏基址。

## 变更记录

| 时间 | 事件 | 说明 |
|---|---|---|
| 2026-08-12 21:26:00 | req.opsx | 从 REQ-0017 创建 OpenSpec Change，状态 proposed。 |
| 2026-08-12 21:50:00 | opsx.apply | 新增后台空间管理后端 API、数据库初始化、后台页面、测试和长期文档，待补 1440px 视觉证据。 |
| 2026-08-12 21:55:00 | visual.acceptance | 完成 1440px 空间列表、申请审批、回收站、详情和冻结弹窗截图；完成 modal computed style 记录。 |
| 2026-08-12 22:16:00 | opsx.modify | 返修主页签层级：Tab 下移到页面标题下方，并移除主 Tab 中的“详情”入口。 |
| 2026-08-12 22:31:00 | opsx.modify | 返修侧边栏一致性：空间管理页复用用户管理页同款后台侧边栏交互。 |
| 2026-08-12 22:55:31 | opsx.modify | 返修空间创建/编辑/负责人移交弹窗：负责人选择、产品派生、必填提示、有效期控件与编辑边界。 |
| 2026-08-12 23:27:43 | opsx.modify | 返修空间新增/编辑弹窗 UI 细节：标题图标、红色星号、字段顺序、负责人下拉和帮助文案。 |
| 2026-08-12 23:40:20 | opsx.modify | 返修空间新增/编辑弹窗帮助文案：空间名称即产品名称、空间编码系统唯一与不可修改。 |
| 2026-08-13 08:43:00 | opsx.modify | 返修空间列表原型对齐：统计卡、九列表头、AI 用量进度条、行内更多操作和下划线主页签。 |
| 2026-08-13 08:53:00 | opsx.modify | 返修空间列表 UI 细节：空间名称无边框文字链接，1440px 下操作列可见。 |
| 2026-08-13 09:01:00 | opsx.modify | 返修空间列表与用户管理列表样式一致性：操作列文字链接、状态圆点文本。 |
| 2026-08-13 09:17:00 | opsx.modify | 返修空间列表字段与密度：字段命名、更新时间、来源标签、nowrap 和更多菜单可见性。 |
| 2026-08-13 19:56:00 | opsx.modify | 返修空间列表列宽、详情产品提示位置、成员头像、成员弹窗纵向布局和移除原因必填标签单行显示。 |
| 2026-08-13 21:29:00 | opsx.modify | 返修添加成员和编辑成员弹窗用户/角色下拉被弹窗滚动容器裁剪或遮罩。 |
| 2026-08-13 21:40:00 | opsx.modify | 返修成员 Tab 空态文案，精简负责人不在列表说明。 |
| 2026-08-13 22:02:08 | opsx.modify | 返修空间详情成员头像旧路由 404，空间读模型统一规范化负责人和成员头像 URL。 |
| 2026-08-13 22:21:06 | opsx.modify | 返修空间详情产品 Tab 原型与扩展性，改为 notice + 产品卡片列表结构。 |
| 2026-08-14 10:48:00 | opsx.modify | 返修空间详情成员 Tab 行距与概览最近操作动作字重。 |
| 2026-08-14 13:08:00 | opsx.modify | 返修空间有效期到期时间控件，替换原生 datetime-local 为自研轻量日期时间选择器。 |
| 2026-08-14 13:20:00 | opsx.modify | 返修空间详情操作记录抽屉空值展示，空值不再使用大块 JSON code block。 |
| 2026-08-14 14:20:00 | opsx.modify | 返修创建空间申请后台演示数据：新增开发/演示后端 seed 与手动脚本，走真实申请审批链路且生产禁用自动播种。 |
| 2026-08-14 15:42:00 | opsx.modify | 返修空间申请演示数据 seed 目标库：脚本加载 `.env` 并映射 Docker SQLite 运行库，避免播种到页面未连接的默认开发库。 |
| 2026-08-14 16:00:07 | opsx.modify | 返修申请审批 Tab 视觉与信息架构：横向大卡片改为后台统一紧凑审批表格，补真实分页和 1440px 证据。 |
| 2026-08-14 16:11:09 | opsx.modify | 返修申请审批表格资源申请列：移除乱码分隔符，Tokens 短量级展示并避免与有效期列重叠。 |

## 验收返修记录

| 项 | 说明 |
|---|---|
| 验收反馈 | 3 个主 Tab 位置过高，视觉上像额外顶部导航；“详情”不应作为主 Tab 同级入口 |
| 调整内容 | `AdminCrudListTemplate` 新增 `headerAddon` 插槽；空间管理主 Tab 放入标题区下方；详情页改为独立视图并提供“返回空间列表”按钮 |
| 文档更新 | `design.md` 明确主 Tab 位于页面标题下方、筛选栏上方；`tasks.md` 追加验收返修记录；本 trace 回填返修证据 |
| 未更新项 | API、DB、部署、安全、长期 API/DB 文档未变化，本次仅调整 UI 层级与视觉验收证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 空间管理页侧边栏与用户管理页侧边栏不一致 |
| 调整内容 | 新增共享 `AdminSidebar`，抽出认证头像、导航、折叠、用户菜单、主题切换与退出登录；用户管理页与空间管理页均复用该组件；空间页复用 `ProfileModal` 与 `ChangePasswordModal` |
| 文档更新 | `design.md` 明确空间管理页和用户管理页必须复用同一套后台侧边栏交互；`tasks.md` 追加返修记录；本 trace 回填返修证据 |
| 未更新项 | API、DB、部署、安全、长期 API/DB 文档未变化，本次仅调整 UI 组件复用与侧边栏交互一致性 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 空间创建/编辑弹窗字段表达不清，负责人不应输入 ID；当前一空间一产品不应单独填写产品信息；长期有效时不应存在到期时间 |
| 调整内容 | 创建与负责人移交弹窗改为从 `/api/v1/admin/users?status=正常` 读取状态正常用户并下拉选择负责人；编辑弹窗移除负责人字段；创建时由空间名称派生产品名称、空间编码派生产品 ID；补齐必填标记、输入说明、长度/数值约束和 `datetime-local` 到期时间控件，长期有效时隐藏到期时间 |
| 文档更新 | `design.md` 补充负责人选择器、编辑不改负责人、产品信息派生和有效期控件规则；`tasks.md` 追加返修记录；本 trace 回填返修证据 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化，本次复用既有用户管理列表 API 与空间接口字段，仅调整后台 UI 表单语义 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 空间新增/编辑弹窗标题不应有图标；必填星号需红色；创建弹窗字段顺序、负责人占位符/下拉文案和空间名称/编码帮助文案需调整 |
| 调整内容 | 移除空间弹窗标题图标；新增统一 `FieldLabel` 渲染红色必填星号；创建弹窗字段顺序调整为“空间名称/空间编码、负责人/成员上限、存储空间/AI Tokens、有效期类型/到期时间、描述整行”；编辑弹窗不包含负责人和配额字段，描述整行；负责人占位符改为“请选择”，选项仅显示昵称或用户名，不展示角色；更新空间名称/编码 placeholder 与帮助文案 |
| 文档更新 | `design.md` 补充弹窗标题、必填星号、字段顺序、负责人下拉与文案规则；`acceptance.md` 补充横切验收项；`tasks.md` 追加返修记录；本 trace 回填返修证据 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化，本次仅调整后台 UI 展示和测试证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 空间新增/编辑弹窗中空间名称与空间编码帮助文案需进一步精简和明确 |
| 调整内容 | 将空间名称帮助文案调整为“一空间仅绑定一款产品，空间名称即产品名称，2-80个字符”；将空间编码帮助文案调整为“系统唯一，3-48 位；仅允许小写字母/数字/短横线，且必须以字母开头；创建后不可修改。” |
| 文档更新 | `tasks.md` 追加文案微调返修记录；本 trace 回填返修证据 |
| 未更新项 | `design.md` 与 REQ `acceptance.md` 的规则语义未变化；API、DB、部署、安全和长期文档未变化 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 空间管理页空间列表与原型效果差异太大，当前实现过度继承通用用户管理列表样式 |
| 调整内容 | 补回空间总数、正常运行、已冻结、资源预警 4 张统计卡；表格列改为“空间、负责人、成员、产品、AI 用量、有效期、状态、创建来源、操作”；AI 用量改为进度条；主页签改为原型下划线样式；行内操作收敛为查看、编辑、冻结/恢复、更多 |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、`tasks.md` 与本 trace 均已同步空间列表原型对齐规则和证据 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化；本次仅调整后台 UI 展示、测试和视觉证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 空间列表中空间名称不应显示边框；1440px 下操作列没有显示出来 |
| 调整内容 | 提升 `.admin-link-button` 样式优先级，使空间名称为无边框、透明背景文字链接；为空间表格补 `colgroup` 和列宽，调整 `min-width`，确保 1440px 视口下操作列可见 |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、`tasks.md` 与本 trace 已同步空间名称链接和 1440px 操作列可见规则 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化；本次仅调整后台 UI 展示、测试和视觉证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 空间管理列表样式与用户管理列表样式不一致 |
| 调整内容 | 保留空间列表字段结构、统计卡、AI 用量进度条和下划线 Tab；空间列表操作列复用后台用户管理同款 `.admin-operation-set` 无边框金色文字链接；状态展示从描边标签改为圆点加文本风格 |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、`tasks.md` 与本 trace 已同步后台列表视觉基准和验证证据 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化；本次仅调整后台 UI 展示、测试和视觉证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 空间列表字段名、创建来源、字段换行、更新时间、冻结/恢复图标和更多菜单遮挡需继续打磨 |
| 调整内容 | 表头调整为空间名称/编码、成员数、产品数；新增更新时间列，格式 `yyyy-mm-dd hh:mm:ss`；创建来源改为轻量标签；除首列外表头和内容不换行；冻结/恢复移除图标；空间表格容器改为不裁剪更多菜单 |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、`tasks.md` 与本 trace 已同步字段密度规则和视觉证据 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化；本次仅使用已有 `updated_at` 字段调整后台列表展示、测试和视觉证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 空间列表字段间距过紧、AI 用量进度条不够直观、不同状态需要不同图标、操作列宽度偏小，更多菜单仍被遮罩 |
| 调整内容 | 参照用户管理列表恢复空间表更舒展列宽，操作列宽度对齐 `220px` 基准；AI 用量改为“已用 / 上限 · 百分比”文本并用颜色表达预警/超限；状态列改为不同语义图标/颜色加文本；更多菜单改为 body 级 fixed 浮层并支持点击外部和 Escape 关闭 |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、`tasks.md` 与本 trace 已同步列表密度、用量文本、状态图标和更多浮层规则 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化；本次仅调整后台列表 UI 展示、前端交互、测试和视觉证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | AI 用量应恢复为原型一致的两行进度条样式且颜色正确；更多菜单仍被分页区域遮罩 |
| 调整内容 | AI 用量改为上行进度条、下行百分比与状态，正常/预警/超限分别使用绿色、金色、红色；更多菜单保留 body 级 fixed 浮层，并增加分页/视口底部边界判断，靠近分页或视口底部时向上展开 |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、`tasks.md` 与本 trace 已同步 AI 用量两行进度条和更多菜单向上展开规则 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化；本次仅调整后台列表 UI 展示、前端交互、测试和视觉证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | AI 用量列第二行不应显示状态文字，进度条轨道和状态颜色需要更贴近原型；更多菜单文字过大、面板可读性不足且覆盖感较强 |
| 调整内容 | AI 用量第二行仅显示百分比，进度条宽度、条高、间距和轨道对比度微调；更多菜单缩小为 `108px` 宽、`12px` 字体、`26px` 行高，面板不透明、z-index `900`，普通项使用金色，危险项红色 |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、`tasks.md` 与本 trace 已同步 AI 用量仅百分比和更多菜单紧凑可读规则 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化；本次仅调整后台列表视觉细节、测试和视觉证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 更多菜单面板位置仍偏离当前行“更多”按钮，hover/focus 状态不明显 |
| 调整内容 | 更多菜单 fixed/portal 保持不变，横向定位改为锚定当前行按钮并与按钮右边缘对齐，优先向下，空间不足时向上且不遮挡分页；普通菜单项 hover/focus-visible 使用金色透明高亮和更亮金色文字，危险项使用红色语义高亮 |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、Sprint 验收报告、`tasks.md` 与本 trace 已同步更多菜单按钮锚定、右边缘对齐和 hover/focus-visible 规则 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化；本次仅调整后台列表更多菜单视觉细节、测试和视觉证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 更多菜单应优先出现在当前行“更多”按钮所在操作列附近，不能漂移到筛选栏或表格中部；空间操作原因缺少必填标记，空原因点击确认没有可见反馈，应参照 BUG-0010 |
| 调整内容 | 更多菜单横向定位改为从当前按钮左边缘展开并限制在视口内，底部空间不足时仍向上且不遮挡分页；空间操作弹窗新增 `hasTriedConfirm` 本地状态，操作原因使用 `label.required`、字段提示、`aria-invalid` 和 `aria-live` 错误，空值或不足 4 字点击确认不发起 API 请求 |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、Sprint 验收报告、`tasks.md` 与本 trace 已同步更多菜单贴近操作列和 BUG-0010 同款原因校验规则 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化；本次仅调整后台空间管理前端交互、测试和视觉证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 空间管理列表更多菜单应显示在“更多”按钮下方，紧贴按钮但保留少量缝隙，面板与按钮左对齐；菜单背景与页面背景过近，边界不清晰 |
| 调整内容 | 更多菜单固定使用 bottom placement，top 为按钮底部加 `6px`，left 为按钮左边缘并限制在视口内；菜单面板背景调整为 `rgb(31, 34, 61)`，增强金色边框、阴影和内描边，提升与页面背景的分层 |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、Sprint 验收报告、`tasks.md` 与本 trace 已同步更多菜单下方显示、左对齐、留缝和背景对比规则 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化；本次仅调整后台空间管理列表更多菜单视觉细节、测试和视觉证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 空间管理列表更多菜单面板背景和边框颜色需要适配暗色/浅色两种主题，面板内菜单项需要靠左对齐 |
| 调整内容 | 更多菜单 portal 浮层自身携带 `dark/light` class，避免依赖 `.admin-shell.light` 祖先选择器；分别定义暗色与浅色面板背景、边框、hover 和危险项颜色；菜单按钮使用 `display:flex`、`justify-content:flex-start` 和 `text-align:left` |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、Sprint 验收报告、`tasks.md` 与本 trace 已同步更多菜单双主题适配和菜单项左对齐规则 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化；本次仅调整后台空间管理列表更多菜单主题样式、测试和视觉证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 空间详情页实现与 REQ-0017 原型图差异较大，缺少详情头、负责人摘要/变更入口、状态化操作和详情内五个分区 Tab |
| 调整内容 | 详情页重构为原型结构：补齐面包屑、详情头、空间状态、编码/来源、负责人摘要和变更入口、续期/冻结/恢复/删除/返回入口；新增概览、成员、产品、配额与用量、操作记录五个分区 Tab；概览按基础信息左上、配额与用量左下、最近操作右侧的三卡片布局展示；成员/产品/配额/操作记录分区补齐 UI 骨架和数据展示 |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、Sprint 验收报告、`tasks.md` 与本 trace 已同步详情页原型结构和分区切换规则 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化；本次仅调整后台空间管理详情页 UI、测试和视觉证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 空间列表成员数、产品数、AI 用量字段仍偏宽；详情概览中的产品绑定提示更适合放到产品 Tab；成员头像未正常显示；添加/编辑成员弹窗横向布局不够清晰；移除成员弹窗操作原因必填标签不应换行 |
| 调整内容 | 收窄空间列表成员数、产品数和 AI 用量列，AI 用量保留原型两行进度条表达；概览 Tab 移除产品绑定提示并移动到产品 Tab 顶部；成员列表用户列复用统一 `AuthenticatedAvatar`；添加成员和编辑成员弹窗改为 `.admin-form-stack` 纵向布局；移除成员操作原因标签补充 `admin-space-reason-label` 单行样式 |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、Sprint 验收报告、`tasks.md` 与本 trace 已同步列表列宽、产品提示位置、成员头像、成员弹窗纵向布局和原因标签单行规则 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化；本次仅调整后台空间管理 UI、前端测试、视觉证据和 OpenSpec/验收文档 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 前台创建空间申请入口尚未实现，需要先在后台 Mock/Seed 待审批申请数据，了解后台审批功能闭环 |
| 调整内容 | 新增 `ADMIN_SPACE_APPLICATION_DEMO_SEED` 开发/演示环境开关、后端 `seed_demo_space_applications` 真实申请数据播种函数和 `scripts/seed-admin-space-applications.py` 手动脚本；演示数据创建正常状态申请人/负责人用户，并通过既有 `create_application` 逻辑生成待审批申请；生产环境不自动播种，前端不硬编码生产 Mock |
| 文档更新 | `design.md`、spec delta、`docs/02-deployment.md`、`.env.example`、`tasks.md` 与本 trace 已同步开发/演示 seed 边界和验证证据 |
| 未更新项 | 空间申请正式 API 与数据库表结构未变化，`docs/03-api-index.md` 和 `docs/04-database-design.md` 无需更新；本次仅新增开发/演示数据入口和脚本 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 直接运行 `python scripts/seed-admin-space-applications.py` 后，空间管理页申请审批 Tab 仍无数据；排查确认脚本写入 `data/sqlite/moonbox.db`，而 Docker 后台实际读取 `data/runtime/backend/sqlite/moonbox.db` |
| 调整内容 | 脚本改为先加载本地 `.env`，把 `sqlite:////app/data/sqlite/moonbox.db` 映射为宿主机 `data/runtime/backend/sqlite/moonbox.db`；无 `.env` 时自动识别 Docker 本地运行库；输出目标数据库路径和播种数量；保留生产环境拒绝演示播种 |
| 文档更新 | `design.md`、spec delta、`docs/02-deployment.md`、`tasks.md` 与本 trace 已同步 seed 目标库解析规则和验证证据 |
| 未更新项 | 空间申请正式 API、DB schema、权限和前端 UI 无变化，`docs/03-api-index.md`、`docs/04-database-design.md`、REQ 验收标准无需新增条目 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 申请审批 Tab 横向大卡片过于稀疏，名称、编码和产品信息容易连在一起，整体与后台列表视觉基准不一致 |
| 调整内容 | 申请审批页改为后台统一紧凑表格，字段为空间名称/编码、申请人、负责人、资源申请、有效期、申请时间和操作；空间名称/编码两行展示，资源申请格式化展示成员、存储和 AI Tokens；操作改为无边框轻量文字按钮，通过为金色，拒绝为危险色；补真实分页，搜索/筛选本轮暂不新增 |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、Sprint 验收报告、`tasks.md` 与本 trace 已同步审批表格信息架构和分页边界 |
| 未更新项 | API、DB schema、权限、部署、安全和长期 API/DB 文档未变化；本次仅调整后台申请审批 Tab UI、前端测试和视觉证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 申请审批表格资源申请列出现 `Â·` 乱码分隔符，长 Tokens 数字挤压有效期列并发生视觉重叠 |
| 调整内容 | 资源申请改为成员、存储、AI Tokens 三个独立紧凑资源项，不再使用分隔符伪元素；AI Tokens 改为中文短量级格式，如 `90万 Tokens`、`150万 Tokens`；审批表格采用固定布局并调整资源、有效期和申请时间列宽 |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、Sprint 验收报告、`tasks.md` 与本 trace 已同步资源列展示规则和 1440px 不重叠验收要求 |
| 未更新项 | API、DB schema、权限、部署、安全和长期 API/DB 文档未变化；本次仅调整后台申请审批 Tab UI 展示、前端测试和视觉证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 添加成员和编辑成员弹窗中的用户下拉框、角色下拉框展开列表被弹窗滚动容器裁剪或遮罩 |
| 调整内容 | `AdminSelect` 新增可选 body 级 fixed portal 菜单能力，点击外部关闭同时识别 root 和 portal 菜单；成员添加/编辑弹窗中的用户与角色下拉启用 portal；portal 菜单同步触发器所在后台主题变量，避免离开 `.admin-shell` 后背景透明 |
| 文档更新 | `design.md`、spec delta、REQ `acceptance.md`、Sprint 验收报告、`tasks.md` 与本 trace 已同步成员弹窗下拉不被裁剪或遮罩的规则和证据 |
| 未更新项 | API、DB、部署、安全和长期 API/DB 文档未变化；本次仅调整后台空间管理成员弹窗下拉 UI、前端测试和视觉证据 |

| 项 | 说明 |
|---|---|
| 验收反馈 | 成员 Tab 空态文案需从“暂无普通成员；负责人不在成员列表中展示，请通过详情头变更负责人。”调整为“暂无成员，负责人不在成员列表。” |
| 调整内容 | 成员列表空态文案已精简为“暂无成员，负责人不在成员列表。” |
| 文档更新 | `tasks.md` 与本 trace 已同步文案返修记录 |
| 未更新项 | spec delta、REQ acceptance、Sprint 验收报告、API、DB、部署、安全和长期文档未变化；本次仅为等价空态文案精简，不改变验收标准或产品能力边界 |

## Implementation Evidence

| 类别 | 证据 |
|---|---|
| Backend API | `src/backend/app/api/v1/admin_spaces.py` 暴露 `/api/v1/admin/spaces` 与 `/api/v1/admin/space-applications` |
| Backend Service | `src/backend/app/repositories/admin_spaces.py` 实现空间列表、创建、详情、编辑、冻结、恢复、回收、彻删、配额、续期、负责人转移、申请审批和审计 |
| Database | `src/backend/app/db/session.py` 与 `src/backend/app/db/schema.sql` 新增空间、产品绑定、成员、申请和审计表 |
| Web | `src/web/src/pages/admin/AdminSpaceManagementPage.tsx` 新增空间管理页；`src/web/src/App.tsx` 接入 `/admin/spaces`；用户管理侧边栏接入空间管理导航 |
| UI Style | `src/web/src/styles/globals.css` 新增空间管理 tabs、列表动作、详情 grid 和 modal 样式 |
| Tests | `tests/integration/api/test_admin_spaces.py`、`src/web/src/admin-space-management.test.tsx` |
| Docs | `docs/03-api-index.md`、`docs/04-database-design.md` |
| Visual | `openspec/archive/2026-08-14-add-admin-space-management/implementation/space-list-1440.png`、`space-approvals-1440.png`、`space-recycle-1440.png`、`space-detail-1440.png`、`space-freeze-modal-1440.png` |
| Computed Style | `openspec/archive/2026-08-14-add-admin-space-management/implementation/computed-style.json` |

## Mock/API Boundary

当前实现已接入真实后端 API：

- 空间列表、搜索、筛选、分页、详情和状态化行内操作使用 `/api/v1/admin/spaces`。
- 申请审批使用 `/api/v1/admin/space-applications`。
- 前端测试仅在 Vitest 中 mock `fetch`，运行时代码不使用页面内静态空间数据。
- 删除前运行中 Agent/任务阻塞检查保留服务层入口 `list_runtime_blockers()`；当前基线尚无 Agent 运行表，返回无阻塞。

## Validation Evidence

| 命令 | 结果 |
|---|---|
| `python -m compileall src/backend/app/api/v1/admin_spaces.py src/backend/app/repositories/admin_spaces.py src/backend/app/schemas/admin_spaces.py` | passed |
| `uv run pytest tests/integration/api/test_admin_spaces.py` | passed，3 tests |
| `pnpm --dir src/web test -- admin-space-management.test.tsx --run` | passed，6 files / 72 tests |
| `pnpm --dir src/web test -- admin-space-management.test.tsx admin-user-management.test.tsx --run` | passed，6 files / 72 tests |
| `pnpm --dir src/web build` | passed |
| `node scripts/capture-admin-space-evidence.mjs` | passed，生成 1440px 截图和 computed style JSON |
| `openspec validate add-admin-space-management --strict` | passed |
| `python scripts/validate-directory-structure.py` | passed |
| `python scripts/validate-openspec-language.py` | 本变更不再报错；全仓库仍因其他既有 Change 的英文标题/任务失败 |
| `pnpm --dir src/web test -- admin-space-management.test.tsx --run` | 返修后 passed，6 files / 72 tests |
| `pnpm --dir src/web build` | 返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 返修后 passed，主 Tab 已位于标题下方，详情不再显示主 Tab |
| `pnpm --dir src/web test -- admin-space-management.test.tsx admin-user-management.test.tsx --run` | 侧边栏返修后 passed，6 files / 73 tests |
| `pnpm --dir src/web build` | 侧边栏返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 侧边栏返修后 passed，空间页侧边栏与用户管理页同款交互基础视觉已刷新 |
| `pnpm --dir src/web test -- src/admin-space-management.test.tsx --run --testTimeout=30000` | 空间弹窗返修后空间页 passed，6 tests；同命令因 Vitest 匹配到既有 `admin-auth.test.tsx` 慢用例仍按默认 5s 超时失败，空间页用例全部通过 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx --testTimeout=30000` | 空间弹窗返修后 passed，1 file / 6 tests |
| `pnpm --dir src/web build` | 空间弹窗返修后 passed |
| `openspec validate add-admin-space-management --strict` | 空间弹窗返修后 passed |
| `git diff --check -- <touched files>` | 空间弹窗返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间弹窗返修后 passed，刷新 1440px 截图和 computed style JSON；沙箱内 Chromium Mach port 权限受限，已按权限规则非沙箱执行 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx --testTimeout=30000` | 空间弹窗 UI 细节返修后 passed，1 file / 6 tests |
| `pnpm --dir src/web build` | 空间弹窗 UI 细节返修后 passed |
| `openspec validate add-admin-space-management --strict` | 空间弹窗 UI 细节返修后 passed |
| `python scripts/validate-openspec-language.py --root openspec/changes/add-admin-space-management` | 空间弹窗 UI 细节返修后 passed |
| `git diff --check -- <touched files>` | 空间弹窗 UI 细节返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间弹窗 UI 细节返修后 passed，刷新 `space-create-modal-1440.png`；computed style 记录标题图标数量 0、必填星号 `rgb(224, 82, 82)`、描述字段 `grid-column: 1 / -1`、负责人占位符“请选择” |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx --testTimeout=30000` | 空间弹窗文案返修后 passed，1 file / 6 tests |
| `pnpm --dir src/web build` | 空间弹窗文案返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间弹窗文案返修后 passed，刷新 `space-create-modal-1440.png` 与 `computed-style.json`，证据已包含新的空间名称/空间编码帮助文案 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 后台下拉框统一返修后 passed，2 files / 31 tests；覆盖空间管理、用户管理、后台分页、键盘选择和点击外部关闭 |
| `pnpm --dir src/web build` | 后台下拉框统一返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 后台下拉框统一返修后 passed，刷新 `space-create-modal-select-1440.png` 与 `computed-style.json`；证据记录下拉菜单位于触发器下方且不覆盖触发器 |
| `openspec validate add-admin-space-management --strict` | 后台下拉框统一返修后 passed |
| `python scripts/validate-openspec-language.py --root openspec/changes/add-admin-space-management` | 后台下拉框统一返修后 passed |
| `python scripts/validate-directory-structure.py` | 后台下拉框统一返修后 passed |
| `git diff --check -- <touched files>` | 后台下拉框统一返修后 passed |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx --testTimeout=30000` | 空间列表原型对齐返修后 passed，1 file / 6 tests；覆盖统计卡、九列表头、AI 用量进度条、创建来源和更多入口 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间列表原型对齐返修后 passed，2 files / 31 tests；确认通用列表模板变更未影响用户管理 |
| `pnpm --dir src/web build` | 空间列表原型对齐返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间列表原型对齐返修后 passed，刷新 `space-list-1440.png` 与 `computed-style.json`；沙箱内 Chromium Mach port 权限受限，已按权限规则非沙箱执行 |
| `openspec validate add-admin-space-management --strict` | 空间列表原型对齐返修后 passed |
| `python scripts/validate-openspec-language.py --root openspec/changes/add-admin-space-management` | 空间列表原型对齐返修后 passed |
| `python scripts/validate-directory-structure.py` | 空间列表原型对齐返修后 passed |
| `git diff --check -- <touched files>` | 空间列表原型对齐返修后 passed |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx --testTimeout=30000` | 空间列表 UI 细节返修后 passed，1 file / 6 tests；覆盖空间名称链接、colgroup 和操作入口 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间列表 UI 细节返修后 passed，2 files / 31 tests；确认用户管理未受通用样式调整影响 |
| `pnpm --dir src/web build` | 空间列表 UI 细节返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间列表 UI 细节返修后 passed，刷新 `space-list-1440.png` 与 `computed-style.json`；证据记录空间名称无边框、背景透明、操作列可见 |
| `openspec validate add-admin-space-management --strict` | 空间列表 UI 细节返修后 passed |
| `python scripts/validate-openspec-language.py --root openspec/changes/add-admin-space-management` | 空间列表 UI 细节返修后 passed |
| `python scripts/validate-directory-structure.py` | 空间列表 UI 细节返修后 passed |
| `git diff --check -- <touched files>` | 空间列表 UI 细节返修后 passed |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间列表与用户管理列表样式一致性返修后 passed，2 files / 31 tests；覆盖空间操作区复用 `admin-operation-set`、状态样式和用户管理回归 |
| `pnpm --dir src/web build` | 空间列表与用户管理列表样式一致性返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间列表与用户管理列表样式一致性返修后 passed，刷新 `space-list-1440.png` 与 `computed-style.json`；证据记录操作按钮无边框、金色文字，状态无边框、圆点加文本 |
| `openspec validate add-admin-space-management --strict` | 空间列表与用户管理列表样式一致性返修后 passed |
| `python scripts/validate-openspec-language.py --root openspec/changes/add-admin-space-management` | 空间列表与用户管理列表样式一致性返修后 passed |
| `python scripts/validate-directory-structure.py` | 空间列表与用户管理列表样式一致性返修后 passed |
| `git diff --check -- <touched files>` | 空间列表与用户管理列表样式一致性返修后 passed |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间列表字段与密度返修后 passed，2 files / 31 tests；覆盖字段名、更新时间、来源标签、冻结无图标和用户管理回归 |
| `pnpm --dir src/web build` | 空间列表字段与密度返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间列表字段与密度返修后 passed，刷新 `space-list-1440.png`、`space-list-more-1440.png` 与 `computed-style.json`；证据记录 nowrap、来源标签和更多菜单可见 |
| `openspec validate add-admin-space-management --strict` | 空间列表字段与密度返修后 passed |
| `python scripts/validate-openspec-language.py --root openspec/changes/add-admin-space-management` | 空间列表字段与密度返修后 passed |
| `python scripts/validate-directory-structure.py` | 空间列表字段与密度返修后 passed |
| `git diff --check -- <touched files>` | 空间列表字段与密度返修后 passed |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间列表字段间距与操作菜单返修后 passed，2 files / 32 tests；覆盖 AI 用量数值、状态图标、portal 更多菜单、点击外部关闭、Escape 关闭和用户管理回归 |
| `pnpm --dir src/web build` | 空间列表字段间距与操作菜单返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间列表字段间距与操作菜单返修后 passed，刷新 `space-list-1440.png`、`space-list-more-1440.png` 与 `computed-style.json`；证据记录 AI 用量无进度条、操作列 `220px`、状态图标和 body 级 fixed 更多菜单 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间列表 AI 用量与更多菜单返修后 passed，2 files / 33 tests；覆盖 AI 用量进度条、预警文案、更多菜单点击外部/Escape 关闭、向上展开和用户管理回归 |
| `pnpm --dir src/web build` | 空间列表 AI 用量与更多菜单返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间列表 AI 用量与更多菜单返修后 passed，刷新 `space-list-1440.png`、`space-list-more-1440.png` 与 `computed-style.json`；证据记录 `hasUsageProgressBar=true`、`usageText=86% · 预警`、`moreMenuPlacement=top`、`moreMenuDoesNotCoverPagination=true` |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间列表 AI 用量与更多菜单视觉细节返修后 passed，2 files / 34 tests；覆盖 AI 用量第二行仅百分比、更多菜单 portal/关闭/向上展开和用户管理回归 |
| `pnpm --dir src/web build` | 空间列表 AI 用量与更多菜单视觉细节返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间列表 AI 用量与更多菜单视觉细节返修后 passed，刷新 `space-list-1440.png`、`space-list-more-1440.png` 与 `computed-style.json`；证据记录 `usageText=86%`、`usageBarWidth=104px`、`moreMenuWidth=108px`、`moreMenuButtonFontSize=12px`、`moreMenuButtonColor=rgb(203, 163, 92)` |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间列表更多菜单位置与 hover 状态返修后 passed，2 files / 34 tests；覆盖更多菜单按钮锚点定位、向上展开、portal/关闭和用户管理回归 |
| `pnpm --dir src/web build` | 空间列表更多菜单位置与 hover 状态返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间列表更多菜单位置与 hover 状态返修后 passed，刷新 `space-list-more-1440.png` 与 `computed-style.json`；证据记录 `moreMenuRightAlignedToTrigger=true`、`moreMenuButtonHoverBackground=rgba(203, 163, 92, 0.16)`、`moreMenuButtonColor=rgb(228, 190, 118)` |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间列表更多菜单定位与操作原因校验返修后 passed，2 files / 34 tests；覆盖更多菜单贴近当前按钮、向上展开、操作原因空值/短值阻断、无效原因不请求、有效原因提交和用户管理回归 |
| `pnpm --dir src/web build` | 空间列表更多菜单定位与操作原因校验返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间列表更多菜单定位与操作原因校验返修后 passed，刷新 `space-list-more-1440.png`、`space-freeze-modal-1440.png` 与 `computed-style.json`；证据记录 `moreMenuLeftAlignedToTrigger=true`、`moreMenuHorizontalGapFromTrigger=0`、`reasonAriaInvalid=true`、`reasonErrorText=操作原因至少需要 4 个字。` |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间列表更多菜单下方定位与背景对比返修后 passed，2 files / 34 tests；覆盖更多菜单下方展开、左对齐、6px 间隙和用户管理回归 |
| `pnpm --dir src/web build` | 空间列表更多菜单下方定位与背景对比返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间列表更多菜单下方定位与背景对比返修后 passed，刷新 `space-list-more-1440.png` 与 `computed-style.json`；证据记录 `moreMenuPlacement=bottom`、`moreMenuLeftAlignedToTrigger=true`、`moreMenuVerticalGapFromTrigger=6`、`moreMenuBackgroundColor=rgb(31, 34, 61)` |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间列表更多菜单双主题与菜单项对齐返修后 passed，2 files / 34 tests；覆盖更多菜单 portal、定位/关闭和用户管理回归 |
| `pnpm --dir src/web build` | 空间列表更多菜单双主题与菜单项对齐返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间列表更多菜单双主题与菜单项对齐返修后 passed，刷新 `space-list-more-1440.png` 与 `computed-style.json`；证据记录暗色 `className=admin-space-more-menu dark`、`buttonJustifyContent=flex-start`，浅色 `className=admin-space-more-menu light`、`backgroundColor=rgb(255, 252, 244)`、`borderColor=rgba(142, 105, 45, 0.36)`、`buttonJustifyContent=flex-start` |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情页原型对齐返修后 passed，2 files / 34 tests；覆盖详情头、负责人变更入口、5 个详情分区 Tab、概览三卡片和分区切换 |
| `pnpm --dir src/web build` | 空间详情页原型对齐返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情页原型对齐返修后 passed，刷新 `space-detail-1440.png` 与 `computed-style.json`；证据记录 `hasDetailHead=true`、`hasOwnerTransfer=true`、5 个详情分区 Tab、概览三卡片布局和成员/产品/配额/操作记录分区可见 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情页继续对齐原型返修后 passed，2 files / 34 tests；覆盖无边框面包屑、标题状态同行、实体操作按钮、危险删除按钮和基础信息两列字段网格 |
| `pnpm --dir src/web build` | 空间详情页继续对齐原型返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情页继续对齐原型返修后 passed，刷新 `space-detail-1440.png` 与 `computed-style.json`；证据记录 `crumbBorderWidth=0px`、`titleRowDisplay=flex`、`actionButtonBackground=rgb(14, 16, 35)`、`dangerButtonBackground=rgb(212, 116, 118)`、`overviewGridTemplateColumns=754.656px 377.344px`、`fieldGridTemplateColumns=324.328px 324.328px` |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情页视觉尺度返修后 passed，2 files / 34 tests；确认局部尺度调整未影响空间列表、详情分区切换和用户管理回归 |
| `pnpm --dir src/web build` | 空间详情页视觉尺度返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情页视觉尺度返修后 passed，刷新 `space-detail-1440.png` 与 `computed-style.json`；证据记录 `detailHeadHeight=140px`、`detailHeadPaddingTop=18px`、`titleFontSize=24px`、`ownerAvatarWidth=26px`、`ownerAvatarHeight=26px`、`actionButtonHeight=36px`、`actionButtonPaddingTop=8px`、`actionButtonPaddingRight=13px`、`baseCardPaddingTop=16px`、`fieldLabelFontSize=12px`、`fieldValueFontSize=14px` |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情页侧边栏、头像和字重返修后 passed，2 files / 34 tests；覆盖负责人真实头像、删除“负责人”文案、空间详情/列表/用户管理回归 |
| `python -m compileall src/backend/app/schemas/admin_spaces.py src/backend/app/repositories/admin_spaces.py` | 空间负责人头像 URL 响应字段返修后 passed |
| `uv run pytest tests/integration/api/test_admin_spaces.py` | 空间负责人头像 URL 响应字段返修后 passed，3 tests；首次沙箱内因 uv 用户缓存权限失败，已按权限规则提升后通过 |
| `pnpm --dir src/web build` | 空间详情页侧边栏、头像和字重返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情页侧边栏、头像和字重返修后 passed，刷新 `space-detail-1440.png` 与 `computed-style.json`；证据记录 `sidebarReusedWithList=true`、列表/详情用户菜单项一致、`ownerAvatarHasImage=true`、`ownerTextContent=空间负责人变更`、除标题外详情关键文本字重均为 `400` |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情页侧边栏用户菜单栏贴底返修后 passed，2 files / 34 tests；覆盖详情页仍复用 `.admin-sidebar-user` 与 `.admin-user-trigger`，并确认用户管理回归 |
| `pnpm --dir src/web build` | 空间详情页侧边栏用户菜单栏贴底返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情页侧边栏用户菜单栏贴底返修后 passed，刷新 `space-list-1440.png`、`space-detail-1440.png` 与 `computed-style.json`；证据记录列表/详情侧边栏均为 `position=sticky`、`height=1000px`、`sidebarBottomGap=0`、`.admin-sidebar-user` 到视口底部均为 `12px`、`.admin-user-trigger` 到视口底部均为 `12px`，且均可见 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情页操作功能返修后 passed，2 files / 35 tests；覆盖详情页编辑、调整配额、续期、移交负责人、冻结、删除的弹窗标题、提交 API、成功 toast、详情态字段刷新与删除后跳转，并确认用户管理回归 |
| `pnpm --dir src/web build` | 空间详情页操作功能返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情页操作功能返修后 passed，刷新 `space-detail-1440.png`、`space-freeze-modal-1440.png` 与 `computed-style.json`；证据记录 `freezeModalTitle=冻结空间`、`hasMemberAddButton=false` |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情页分区真实性与操作闭环返修后 passed，2 files / 35 tests；覆盖成员/产品/配额与用量/操作记录分区切换、成员与操作记录明确空态、产品无未实现操作、配额分区调整入口可用和用户管理回归 |
| `pnpm --dir src/web build` | 空间详情页分区真实性与操作闭环返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情页分区真实性与操作闭环返修后 passed，刷新 `space-detail-1440.png` 与 `computed-style.json`；证据记录成员无添加入口、无“成员占位”、产品无未实现按钮、配额分区有“调整配额”、操作记录无静态时间线 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情页成员分区与返回按钮视觉返修后 passed，2 files / 35 tests；覆盖成员分区标题移除、字段网格复用和用户管理回归 |
| `pnpm --dir src/web build` | 空间详情页成员分区与返回按钮视觉返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情页成员分区与返回按钮视觉返修后 passed，刷新 `space-detail-1440.png` 与 `computed-style.json`；证据记录 `returnButtonBorderWidth=0px`、成员 `hasSectionTitle=false`、`fieldGridClassName=admin-space-detail-field-grid`、字段 label/value 字号 `12px/14px` 且字重均为 `400` |
| `python -m compileall src/backend/app/api/v1/admin_spaces.py src/backend/app/repositories/admin_spaces.py src/backend/app/schemas/admin_spaces.py` | 空间详情页成员 Tab 返修后 passed |
| `uv run pytest tests/integration/api/test_admin_spaces.py` | 空间详情页成员 Tab 返修后 passed，4 tests；覆盖成员 API 负责人排除、正常用户限制、角色排序、角色编辑、移除和成员计数更新 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情页成员 Tab 返修后 passed，2 files / 35 tests；覆盖成员表格字段、负责人不在成员表、添加成员、编辑角色、移除成员和用户管理回归 |
| `pnpm --dir src/web build` | 空间详情页成员 Tab 返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情页成员 Tab 返修后 passed，刷新 `space-detail-1440.png` 与 `computed-style.json`；证据记录成员表头 `[用户, 角色, 加入时间, 状态, 操作]`、`rowCount=2`、`hasOwnerInRows=false`、`firstRoleText=管理员`、表头/单元格字号 `12px/14px` 且字重均为 `400` |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间管理 UI 细节返修后 passed，2 files / 35 tests；覆盖产品提示迁移、成员真实头像、成员弹窗纵向布局、移除原因标签和用户管理回归 |
| `pnpm --dir src/web build` | 空间管理 UI 细节返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间管理 UI 细节返修后 passed，刷新 `space-list-1440.png`、`space-detail-1440.png`、`space-member-add-modal-1440.png`、`space-member-edit-modal-1440.png` 与 `computed-style.json`；沙箱内 Chromium Mach port 权限受限，已按权限规则非沙箱执行 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情成员弹窗下拉遮罩返修后 passed，2 files / 35 tests；覆盖成员弹窗用户/角色下拉使用 body 级 portal 且不在 modal 内渲染，并确认用户管理回归 |
| `pnpm --dir src/web build` | 空间详情成员弹窗下拉遮罩返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情成员弹窗下拉遮罩返修后 passed，刷新 `space-member-add-modal-user-select-1440.png`、`space-member-add-modal-role-select-1440.png`、`space-member-edit-modal-role-select-1440.png` 与 `computed-style.json`；沙箱内 Chromium Mach port 权限受限，已按权限规则非沙箱执行 |
| `python -m compileall src/backend/app/repositories/admin_spaces.py src/backend/app/repositories/admin_users.py` | 空间详情成员头像旧路由 404 返修后 passed |
| `uv run pytest tests/integration/api/test_admin_spaces.py` | 空间详情成员头像旧路由 404 返修后 passed，4 tests；覆盖历史头像 URL 规范化、成员列表、详情负责人头像、成员添加/编辑/移除返回对象；首次沙箱内因 uv 用户缓存权限失败，已按权限规则提升后通过 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情成员头像旧路由 404 返修后 passed，2 files / 37 tests；覆盖详情负责人/成员头像只请求 `/api/v1/auth/avatar/*` 且不请求旧 `/api/v1/admin/users/avatar/*` |
| `pnpm --dir src/web build` | 空间详情成员头像旧路由 404 返修后 passed |
| `openspec validate add-admin-space-management --strict` | 空间详情成员头像旧路由 404 返修后 passed |
| `python scripts/validate-openspec-language.py --root openspec/changes/add-admin-space-management` | 空间详情成员头像旧路由 404 返修后 passed |
| `python scripts/validate-directory-structure.py` | 空间详情成员头像旧路由 404 返修后 passed |
| `git diff --check -- <touched files>` | 空间详情成员头像旧路由 404 返修后 passed |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情产品 Tab 原型与扩展性返修后 passed，2 files / 37 tests；覆盖 notice、产品卡片列表、无“绑定产品”标题、无产品数字段、统一字段网格和用户管理回归 |
| `pnpm --dir src/web build` | 空间详情产品 Tab 原型与扩展性返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情产品 Tab 原型与扩展性返修后 passed；首次沙箱内因 Chromium Mach port 权限失败、非沙箱首次因 4317 预览服务未启动失败，启动 `vite preview` 后重跑通过并刷新 1440px 空间详情视觉证据和 computed style |
| `python -m compileall src/backend/app/repositories/admin_spaces.py src/backend/app/api/v1/admin_spaces.py src/backend/app/schemas/admin_spaces.py` | 空间管理操作记录返修后 passed |
| `uv run pytest tests/integration/api/test_admin_spaces.py` | 空间管理操作记录返修后 passed，4 tests；覆盖成员添加/编辑角色/移除审计、审批通过创建空间后新空间详情可追溯 `application_approved_create_space` 审批来源、原因、前后值和结果；首次沙箱内因 uv 用户缓存权限失败，已按权限规则提升后通过 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间管理操作记录返修后 passed，2 files / 37 tests；覆盖操作记录 Tab 调用真实 `/api/v1/admin/spaces/{space_id}/audit-events`、展示操作人/来源/变更前后值/原因/结果并移除旧静态占位 |
| `pnpm --dir src/web build` | 空间管理操作记录返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间管理操作记录返修后 passed，刷新 1440px 空间管理视觉证据和 `computed-style.json`；证据记录操作记录表头 `[操作, 操作人, 时间, 来源, 对象, 变更前后值, 原因, 结果]`、`rowCount=2`、`firstActionText=审批通过创建空间`、`hasAuditApiPlaceholder=false`、`hasApprovalReason=true` |
| `python -m compileall src/backend/app/repositories/admin_spaces.py src/backend/app/api/v1/admin_spaces.py src/backend/app/schemas/admin_spaces.py` | 空间详情刷新与操作记录表格返修后 passed |
| `uv run pytest tests/integration/api/test_admin_spaces.py` | 空间详情刷新与操作记录表格返修后 passed，4 tests；覆盖审计事件返回 `actor_display_name` 且不是裸 actor/user_id；首次沙箱内因 uv 用户缓存权限失败，已按权限规则提升后通过 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情刷新与操作记录表格返修后 passed，2 files / 37 tests；覆盖详情操作成功后重新拉取详情与审计事件、概览最近操作基于真实审计、操作记录无内层标题、标签化枚举和变更摘要 |
| `pnpm --dir src/web build` | 空间详情刷新与操作记录表格返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情刷新与操作记录表格返修后 passed，刷新 1440px 空间管理视觉证据和 `computed-style.json`；证据记录操作记录表头 `[操作, 操作人, 时间, 来源, 对象, 变更摘要, 原因, 结果]`、`hasInnerTitle=false`、`tagCount=6`、`actorDisplayText=平台超级管理员`、`sourceTagText=申请审批`、`resultTagText=成功`、`firstChangeSummary=状态：待审批 → 无`、`hasAuditApiPlaceholder=false` |
| `python -m compileall src/backend/app/repositories/admin_spaces.py src/backend/app/api/v1/admin_spaces.py src/backend/app/schemas/admin_spaces.py` | 空间详情有效期与审计记录交互返修后 passed |
| `uv run pytest tests/integration/api/test_admin_spaces.py` | 空间详情有效期与审计记录交互返修后 passed，4 tests；覆盖固定日期必须晚于当前时间、长期有效不保存到期时间、审计事件分页响应与操作人展示名 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx` | 空间详情有效期与审计记录交互返修后 passed，10 tests；覆盖到期时间秒级控件默认季度末 23:59:59、最小时间、概览基础信息字段顺序、最近 6 条审计、操作记录分页、标签化列和右侧详情抽屉 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情有效期与审计记录交互返修后 passed，2 files / 37 tests；覆盖空间管理与用户管理列表/下拉/侧边栏回归 |
| `pnpm --dir src/web build` | 空间详情有效期与审计记录交互返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情有效期与审计记录交互返修后 passed，刷新 1440px 视觉证据和 `computed-style.json`；证据记录基础信息顺序、最近 6 条、操作记录分页、行内查看抽屉和到期时间秒级默认值 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情操作记录视觉返修后 passed，2 files / 38 tests；覆盖操作记录分页轻量无边框样式、操作详情抽屉变更前/后 JSON 格式化展示、空间列表长期有效文案和用户管理回归 |
| `pnpm --dir src/web build` | 空间详情操作记录视觉返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情操作记录视觉返修后 passed，刷新 1440px 视觉证据和 `computed-style.json`；证据记录操作记录分页 `border-width=0px`、背景透明、active 页无边框，抽屉内两个 JSON code block 使用等宽字体并在区域内滚动 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情成员 Tab 与最近操作视觉返修后 passed，2 files / 38 tests；覆盖空间详情成员/最近操作结构和用户管理回归 |
| `pnpm --dir src/web build` | 空间详情成员 Tab 与最近操作视觉返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情成员 Tab 与最近操作视觉返修后 passed，刷新 1440px 视觉证据和 `computed-style.json`；首次沙箱内因 Chromium Mach port 权限失败，已按权限规则非沙箱执行；证据记录成员表格行高、单元格 padding、垂直居中和最近操作动作字重 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx` | 空间有效期到期时间控件返修后 passed，11 tests；覆盖自研日期时间控件展示格式、展开面板、时分秒选择与创建空间表单回归 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间有效期到期时间控件返修后 passed，2 files / 38 tests；覆盖空间管理与用户管理回归 |
| `pnpm --dir src/web build` | 空间有效期到期时间控件返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间有效期到期时间控件返修后 passed，刷新 `space-create-modal-1440.png`、新增 `space-create-modal-datetime-1440.png` 与 `computed-style.json`；沙箱内因 Chromium Mach port 权限失败，已按权限规则非沙箱执行；证据记录日期时间控件输入格式、秒级默认值、日历、时分秒选择、快捷项、fixed portal 面板和不透明主题背景 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx` | 空间详情操作记录抽屉空值展示返修后 passed，11 tests；覆盖 JSON 值继续使用 code block、空值使用轻量空态文本“无” |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间详情操作记录抽屉空值展示返修后 passed，2 files / 38 tests；覆盖空间管理和用户管理回归 |
| `pnpm --dir src/web build` | 空间详情操作记录抽屉空值展示返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间详情操作记录抽屉空值展示返修后 passed，新增 `space-audit-empty-drawer-1440.png` 并刷新 `computed-style.json`；证据记录空值抽屉轻量空态高度、padding、背景和 JSON block 数量 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 后台亮主题主按钮文字颜色返修后 passed，2 files / 38 tests；覆盖空间管理和用户管理回归 |
| `pnpm --dir src/web build` | 后台亮主题主按钮文字颜色返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 后台亮主题主按钮文字颜色返修后 passed，新增 `space-detail-members-light-1440.png` 并刷新 `computed-style.json`；证据记录亮/暗主题主按钮文字颜色、背景、边框、字重和 focus outline |
| `uv run pytest tests/integration/api/test_admin_spaces.py` | 空间回收站功能返修后 passed，4 tests；覆盖 `status=RECYCLE` 回收站分页和删除人、删除原因等回收站读模型字段；首次沙箱内因 uv 用户缓存权限失败，已按权限规则提升后通过 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 空间回收站功能返修后 passed，2 files / 40 tests；覆盖回收站独立请求 `status=RECYCLE` 接口、回收站分页 total、删除字段展示、恢复/彻底删除操作，以及删除空间后进入回收站并刷新数据 |
| `pnpm --dir src/web build` | 空间回收站功能返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 空间回收站功能返修后 passed，刷新 `space-recycle-1440.png` 与 `computed-style.json`；证据记录回收站标题、删除字段、回收站分页、查看/恢复/更多操作和无常规编辑入口 |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 回收站 Tab 更多菜单遮罩返修后 passed，2 files / 40 tests；覆盖回收站更多菜单 body 级 portal、`data-scope=recycle`、按钮下方左对齐、6px 间隙和彻底删除菜单项 |
| `pnpm --dir src/web build` | 回收站 Tab 更多菜单遮罩返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 回收站 Tab 更多菜单遮罩返修后 passed；沙箱内因 Chromium Mach port 权限失败，已按权限规则非沙箱执行；新增 `space-recycle-more-1440.png` 并刷新 `space-recycle-1440.png` 与 `computed-style.json` |
| `pnpm --dir src/web exec vitest run src/admin-space-management.test.tsx src/admin-user-management.test.tsx --testTimeout=30000` | 回收站 Tab 更多菜单位置回退与层级返修后 passed，2 files / 41 tests；覆盖回收站更多菜单回到按钮下方、左对齐、6px 间隙，以及无更多收敛操作时不展示“更多”按钮或空菜单面板 |
| `pnpm --dir src/web build` | 回收站 Tab 更多菜单位置回退与层级返修后 passed |
| `node scripts/capture-admin-space-evidence.mjs` | 回收站 Tab 更多菜单位置回退与层级返修后 passed；沙箱内因 Chromium Mach port 权限失败，已按权限规则非沙箱执行；刷新 `space-recycle-more-1440.png` 与 `computed-style.json`，确认菜单在按钮下方且菜单项位于最上层可见 |

## Visual Acceptance

| 场景 | 证据 |
|---|---|
| 空间列表 | `implementation/space-list-1440.png` |
| 空间列表更多菜单展开 | `implementation/space-list-more-1440.png` |
| 申请审批 | `implementation/space-approvals-1440.png` |
| 回收站 | `implementation/space-recycle-1440.png` |
| 回收站更多菜单展开 | `implementation/space-recycle-more-1440.png` |
| 空间详情 | `implementation/space-detail-1440.png` |
| 高风险弹窗 | `implementation/space-freeze-modal-1440.png` |
| 新增空间弹窗 | `implementation/space-create-modal-1440.png` |
| 新增空间弹窗日期时间控件 | `implementation/space-create-modal-datetime-1440.png` |
| 新增空间弹窗负责人下拉展开 | `implementation/space-create-modal-select-1440.png` |
| 操作记录空值抽屉 | `implementation/space-audit-empty-drawer-1440.png` |
| 亮主题成员 Tab 主按钮 | `implementation/space-detail-members-light-1440.png` |
| 添加成员用户下拉 | `implementation/space-member-add-modal-user-select-1440.png` |
| 添加成员角色下拉 | `implementation/space-member-add-modal-role-select-1440.png` |
| 编辑成员角色下拉 | `implementation/space-member-edit-modal-role-select-1440.png` |

`computed-style.json` 记录：1440x1000 视口下 `.admin-space-modal` 宽度 `720px`、`max-height: 760px`、`overflow: auto`、圆角 `2px`；负责人下拉展开时 `triggerBottom=439`、`menuTop=443`、`gap=4`、`doesNotCoverTrigger=true`；空间列表证据包含 4 张统计卡、空间名称/编码等十列表头、active Tab `2px` 金色下划线、AI 用量 `usageText=86%`、`usageLabelColor=rgb(213, 168, 91)`、`usageBarWidth=104px`、`usageBarFillWidth=89px`、`hasUsageProgressBar=true` 和“更多”入口；空间名称 `border-width: 0px`、背景透明，1440px 下操作列 `actionColumnVisibleAt1440=true`、宽度 `220px`；操作按钮 `border-width: 0px`、金色文字，状态 `border-width: 0px`、状态图标为 `svg`；来源标签 `border-width: 1px`，非首列 `white-space: nowrap`；空间详情记录 `sidebarReusedWithList=true`、`sidebarUserBottomGapEqual=true`、`userTriggerBottomGapEqual=true`，列表态与详情态 `shellClassName=admin-shell admin-space-shell`、`sidebarClassName=admin-sidebar`、`sidebarPosition=sticky`、`sidebarTop=0px`、`sidebarAlignSelf=start`、`sidebarHeight=1000px`、`sidebarBottomGap=0`、`sidebarUserBottomGap=12`、`userTriggerBottomGap=12`、`sidebarUserVisible=true`、`userTriggerVisible=true`、active 均为“空间管理”，用户菜单均包含“个人资料/修改密码/返回前台/界面主题/退出登录”；`hasCrumb=true`、`crumbBorderWidth=0px`、`hasDetailHead=true`、`detailHeadMinHeight=0px`、`detailHeadHeight=140px`、`detailHeadPaddingTop=18px`、`detailHeadPaddingRight=18px`、`titleFontSize=24px`、`titleFontWeight=700`、`titleRowDisplay=flex`、`titleRowAlignItems=center`、`ownerAvatarWidth=26px`、`ownerAvatarHeight=26px`、`ownerAvatarHasImage=true`、`ownerAvatarImageAlt=空间负责人头像`、`ownerTextContent=空间负责人变更`、`hasOwnerTransfer=true`、普通实体操作按钮高度 `36px`、padding `8px 13px`、圆角 `7px`、背景 `rgb(14, 16, 35)`、删除危险按钮背景 `rgb(212, 116, 118)`、面包屑当前项/负责人姓名/操作按钮/notice/字段 label/value 字重均为 `400`、`detailTabs=[概览,成员,产品,配额与用量,操作记录]`、`overviewGridTemplateColumns=761.328px 380.672px`、`overviewGridTemplateAreas=\"base recent\" \"quota recent\"`、`overviewCardCount=3`、基础信息卡片 padding `16px`、`fieldGridTemplateColumns=349.656px 349.672px`、字段 label/value 字号 `12px/14px`、成员/产品/配额/操作记录分区均可见、`hasMemberAddButton=true`、成员表头为 `[用户, 角色, 加入时间, 状态, 操作]`、`rowCount=2`、`hasOwnerInRows=false`；暗色更多菜单 `moreMenuClassName=admin-space-more-menu dark`、`moreMenuVisible=true`、`position=fixed`、`background=rgb(31, 34, 61)`、`borderColor=rgba(203, 163, 92, 0.34)`、`z-index=900`、`width=108px`、`buttonFontSize=12px`、`buttonMinHeight=26px`、hover 后普通项颜色 `rgb(228, 190, 118)`、hover 背景 `rgba(203, 163, 92, 0.16)`、`buttonJustifyContent=flex-start`、`buttonTextAlign=left`、`moreMenuParentIsBody=true`、`moreMenuPlacement=bottom`、`moreMenuLeftAlignedToTrigger=true`、`moreMenuHorizontalGapFromTrigger=0`、`moreMenuVerticalGapFromTrigger=6`；浅色更多菜单记录 `className=admin-space-more-menu light`、`backgroundColor=rgb(255, 252, 244)`、`borderColor=rgba(142, 105, 45, 0.36)`、`buttonColor=rgb(111, 77, 28)`、`buttonHoverBackground=rgba(184, 134, 62, 0.14)`、`buttonJustifyContent=flex-start`、`buttonTextAlign=left`；冻结弹窗错误态记录 `title=冻结空间`、`reasonLabelText=操作原因`、`reasonAriaInvalid=true`、`reasonErrorText=操作原因至少需要 4 个字。`、`reasonErrorColor=rgb(212, 116, 118)`。

分区真实性补充证据：成员 Tab 已升级为真实成员表格；产品 Tab `detailProductState.productNoticeText=绑定关系不可解除或迁移，产品名称始终与空间名称一致。`、`productCardCount=1`、`hasProductCardTitle=false`、`hasProductCountField=false`、`productIdText=moonbox-platform`、`researchStatusText=进行中`、`fieldGridClassName=admin-space-detail-field-grid`、字段 label/value 字号 `12px/14px` 且字重均为 `400`、`hasUnsupportedActionButton=false`；`detailQuotaState.hasAdjustQuotaButton=true`；操作记录 Tab 已接入真实审计数据，`detailLogsState.hasStaticTimeline=false`、`emptyStateText=null`、`headers=[操作, 操作人, 时间, 来源, 对象, 变更摘要, 原因, 结果]`、`rowCount=2`、`firstActionText=审批通过创建空间`、`hasInnerTitle=false`、`tagCount=6`、`actorDisplayText=平台超级管理员`、`sourceTagText=申请审批`、`resultTagText=成功`、`firstChangeSummary=状态：待审批 → 无`、`hasAuditApiPlaceholder=false`、`hasApprovalReason=true`。

成员分区与返回按钮视觉补充证据：`returnButtonBorderWidth=0px`、`returnButtonBackground=rgba(0, 0, 0, 0)`、`returnButtonColor=rgb(203, 163, 92)`；成员 `hasSectionTitle=false`、`fieldGridClassName=admin-space-detail-field-grid`、`fieldLabelFontSize=12px`、`fieldLabelFontWeight=400`、`fieldValueFontSize=14px`、`fieldValueFontWeight=400`。

成员 Tab 表格补充证据：`detailMembersState.hasAddMemberButton=true`、`detailMembersState.tableHeaders=[用户, 角色, 加入时间, 状态, 操作]`、`detailMembersState.rowCount=2`、`detailMembersState.hasOwnerInRows=false`、`detailMembersState.firstRoleText=管理员`、`detailMembersState.tableHeaderFontSize=12px`、`detailMembersState.tableHeaderFontWeight=400`、`detailMembersState.tableCellFontSize=14px`、`detailMembersState.tableCellFontWeight=400`。

空间管理 UI 细节补充证据：列表 `tableMinWidth=1368px`、`membersColumnWidth=76px`、`productColumnWidth=68px`、`usageColumnWidth=172px`，AI 用量仍保留 `hasUsageProgressBar=true`；详情概览 `overviewHasProductNotice=false`；成员列表 `memberAvatarHasImage=true`、`memberAvatarAlt=后台负责人头像`；冻结/移除类原因标签 `reasonLabelDisplay=inline-flex`、`reasonLabelWhiteSpace=nowrap`；添加成员和编辑成员弹窗均记录 `hasStackLayout=true`、`stackDisplay=grid`、单列 `stackGridTemplateColumns=674px`。

成员弹窗下拉遮罩补充证据：添加成员用户下拉记录 `userMenuParentIsBody=true`、`userMenuInsideModal=false`、`userMenuPosition=fixed`、`userMenuZIndex=120`、`userMenuBackgroundColor=rgb(18, 20, 43)`、`userMenuWidthMatchesTrigger=true`、`userMenuVerticalGapFromTrigger=4`；添加成员角色下拉记录 `menuParentIsBody=true`、`menuInsideModal=false`、`menuPosition=fixed`、`menuBackgroundColor=rgb(18, 20, 43)`、`menuWidthMatchesTrigger=true`、`menuDoesNotClipByModal=true`、`menuVerticalGapFromTrigger=4`；编辑成员角色下拉记录 `roleMenuParentIsBody=true`、`roleMenuInsideModal=false`、`roleMenuPosition=fixed`、`roleMenuBackgroundColor=rgb(18, 20, 43)`、`roleMenuWidthMatchesTrigger=true`、`roleMenuDoesNotClipByModal=true`、`roleMenuVerticalGapFromTrigger=4`。

空间详情有效期与审计记录交互补充证据：`detailPrototypeAlignment.baseFieldLabels=[空间名称, 唯一标识, 创建来源, 创建时间, 有效期]`、`baseFieldValues` 中固定日期有效期为 `2027-12-31 23:59:59`、`recentOperationCount=6`；操作记录 Tab `headers=[时间, 操作人, 操作动作, 变更摘要, 结果, 操作]`、`rowCount=7`、`firstActionText=审批通过创建空间`、`paginationText=共 7 条记录‹1›每页显示10 条`、`viewButtonCount=7`、`hasInnerTitle=false`、`resultTagText=成功`；右侧抽屉 `auditDrawerState.visible=true`、`title=审批通过创建空间`、`hasRequestId=true`、`hasBeforeAfter=true`、`sourceTagText=申请审批`、`resultTagText=成功`；新增空间弹窗到期时间 `expiryInputType=datetime-local`、`expiryInputStep=1`、`expiryInputValue=2026-09-30T23:59:59`、`expiryInputHasSeconds=true`、`expiryInputDefaultsToQuarterEnd=true`。

空间详情操作记录视觉返修补充证据：`detailLogsState.paginationBorderWidth=0px`、`paginationBackground=rgba(0, 0, 0, 0)`、`activePageBorderWidth=0px`、`activePageBackground=color(srgb 0.796078 0.639216 0.360784 / 0.14)`；操作详情抽屉 `auditDrawerState.jsonBlockCount=2`、`beforeJsonText` 和 `afterJsonText` 为带换行与 2 空格缩进的格式化 JSON，`jsonFontFamily=SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace`、`jsonMaxHeight=340px`、`jsonOverflow=auto`、`jsonWhiteSpace=pre-wrap`；空间列表长期有效文案由回归测试覆盖，长期有效空间的有效期列显示“长期有效”而非“长期”。

空间详情成员 Tab 与最近操作视觉返修补充证据：`detailMembersState.tableRowHeight=52.7812px`、`tableCellHeight=52.7812px`、`tableCellPaddingTop=8px`、`tableCellPaddingBottom=8px`、`tableCellVerticalAlign=middle`，且 `tableCellFontSize=14px`、`tableCellFontWeight=400` 保持不变；`detailPrototypeAlignment.recentOperationFontWeight=400`，仅卡片标题保持强调。

空间有效期到期时间控件返修补充证据：创建空间弹窗 `createModal.expiryInputType=text`、`expiryInputPlaceholder=yyyy-mm-dd hh:mm:ss`、`expiryInputValue=2026-09-30 23:59:59`、`expiryInputHasSeconds=true`、`expiryInputDefaultsToQuarterEnd=true`；日期时间面板 `dateTimePanelPlacement.gap=4`、`doesNotCoverTrigger=true`、`widthMatchesTrigger=true`，`dateTimePanelState.parentIsBody=true`、`position=fixed`、`zIndex=120`、`backgroundColor=rgb(18, 20, 43)`、`borderColor=rgba(234, 242, 255, 0.16)`、`activeDayText=30`、`activeDayBackground=rgb(203, 163, 92)`、`timeInputCount=3`、`timeInputValues=[23, 59, 59]`、`shortcutTexts=[今天 23:59:59, 本季度末, 一年后]`。

空间详情操作记录抽屉空值展示返修补充证据：JSON 场景 `auditDrawerState.jsonBlockCount=2`、`jsonMaxHeight=340px`、`jsonOverflow=auto`、`jsonWhiteSpace=pre-wrap` 保持不变；空值场景 `auditEmptyDrawerState.title=添加成员`、`emptyCount=1`、`jsonBlockCount=1`、`emptyText=无`、`emptyMinHeight=34px`、`emptyPaddingTop=8px`、`emptyOverflow=visible`，确认变更前为空时展示轻量空态且不撑高抽屉。

后台亮主题主按钮文字颜色返修补充证据：`primaryButtonThemeState.light.color=rgb(62, 43, 18)`、`backgroundColor=rgb(184, 134, 62)`、`borderColor=rgb(184, 134, 62)`、`fontWeight=500`、`outlineStyle=solid`、`outlineWidth=2px`；暗主题 `primaryButtonThemeState.dark.color=rgb(9, 11, 22)`、`backgroundColor=rgb(203, 163, 92)`、`borderColor=rgb(203, 163, 92)`、`fontWeight=500`，确认空间详情成员 Tab“添加成员”等后台主按钮在亮/暗主题下均可读。

空间回收站功能返修补充证据：`recycleState.title=空间回收站`、`headers=[空间名称/编码, 负责人, 删除时间, 删除人, 删除原因, 剩余天数, 创建来源, 操作]`、`firstRowCells=[历史空间old-space, 空间负责人, 2026-08-12 10:00:00, 平台超级管理员, 空间生命周期结束, 29 天, 后台创建, 查看恢复更多]`、`paginationLabel=回收站分页`、`paginationText=共 1 个空间‹1›每页显示10 条`、`hasRestoreButton=true`、`hasEditButton=false`、`hasDeletedAt=true`、`hasDeletedByName=true`、`hasDeleteReason=true`、`hasRemainingDays=true`，确认回收站 Tab 使用独立真实分页数据展示回收站字段和专属操作。

回收站 Tab 更多菜单遮罩返修补充证据：`recycleState.moreMenuScope=recycle`、`moreMenuParentIsBody=true`、`moreMenuPosition=fixed`、`moreMenuZIndex=1100`、`moreMenuBackgroundColor=rgb(31, 34, 61)`、`moreMenuBorderColor=rgba(203, 163, 92, 0.34)`、`moreMenuVisible=true`、`moreMenuHeight=34`、`moreMenuItemTexts=[彻删]`、`moreMenuFirstItemVisible=true`、`moreMenuFirstItemOnTop=true`、`moreMenuLeftAlignedToTrigger=true`、`moreMenuPlacement=bottom`、`moreMenuVerticalGapFromTrigger=6`、`moreMenuZIndexAbovePagination=true`，确认回收站行内“更多”菜单位于按钮下方，菜单项文字完整可见，且不被表格、分页、sticky 操作列或回收站容器遮罩/裁剪；无更多收敛操作时由回归测试确认不展示“更多”按钮或空菜单面板。
