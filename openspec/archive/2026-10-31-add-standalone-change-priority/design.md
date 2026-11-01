---
title: 独立 Change 优先级维护与展示设计
created_at: '2026-10-31 21:27:39'
updated_at: '2026-10-31 21:27:39'
---

# 独立 Change 优先级维护与展示设计

## 背景与现状
源码 change_index.py 的独立卡片构造将 priority 置空；关联对象沿用来源字段。现有 Issue 分级规范不承载独立 Change。复用 REQ-0056 的对象身份、来源解析及授权，不重新判断隐藏来源为独立。

## 目标与非目标
实现需求 FR-001至005、AC-001至012及全部原型/横切AC。不改变卡片数量、默认排序、BUG严重度、验收及归档条件，不执行生产发布。

## 设计方案
D1 采用现有 Design System token/组件加局部样式迁移；HTML仅作为卡片内编辑输入，不搬运演示页壳。相比完整CSS移植可保持需求中心密度和主题。
D2 trace Frontmatter priority 为唯一事实源，合法枚举四档；返回 valid/missing/invalid 状态，非法原文不直接泄漏到UI。来源转换后保留字段但只读、展示来源Issue分级。读取摘要不运行全量验收检查。
D3 写入绑定项目、完整Change ID、来源关系及当前文档版本。复用服务端对象写权限；每次保存重新解析活动目录、唯一身份、来源与授权，禁止路径注入、符号链接越界及归档写入。保存采用内容版本比较与项目写锁；外部文件写入竞争纳入回归，不用前端锁替代服务端保护。
D4 必要审计与priority在同一trace原子提交：审计记录旧值、新值、服务端不透明操作者ID、时间；同值无操作，不改业务更新时间。复用现有受控写入/恢复设施；先核实其跨进程并发能力，若不足先补实现设计，不能直接无锁覆盖。写入失败保持原文件，原子替换后失联通过回读恢复；可选遥测与必要审计分开。

## 数据与 API
在既有需求中心对象路由增加分级更新能力，实施阶段按当前路由规范确定准确路径并写入OpenAPI。请求为priority、expected_version与idempotency_key，项目及对象身份使用受控路由参数；返回202及操作标识，等待applied后回读摘要。错误区分非法枚举、无权限、版本冲突、来源变化、归档只读，沿统一错误封装。GET摘要新增必要字段和can_edit能力，后端再次授权。
更新OpenAPI、Orval生成客户端、docs/03-api-index.md及契约测试。默认无新增数据库表：审计随文件原子提交；不修改SQLite/MySQL schema、对象存储或部署配置。若现有writer依赖数据库操作记录，复用现有schema并测试两库兼容。

product_data_collection_observability:
- status: applicable
- affected_layers: web、api、governance、usage_events、request_logs、task_traces、task_trace_spans
- reason: 界面保存与请求需关联；必要业务审计随trace提交。复用异步控制器既有Task Trace及节点，不新增数据库表。
- validation: 行为保存事件与可信request_id关联、直接API不伪造行为、脱敏及遥测故障回归；沿用行为180天和请求90天，不改变保留策略。禁止正文、凭证及本机路径。

## 冲突处理（Conflict Resolution）
HTML、PNG、context、AC、UI规则、既有spec依次用于视觉参考；无PNG。HTML演示壳和Mock不进入产品，现有业务权限与验收不可被演示代码覆盖。HTML卡片最大560px为局部参考，生产看板列宽随现有布局；浅色panel使用对应组件token，避免覆盖全局。没有现有规格要求独立对象必须永远为空，新增合法分级不违反缺值不伪造默认原则。

## UI Contract 与局部一致契约
入口 /requirements。保留页面壳、导航、阶段列及其他动作，新增卡片标签、设置按钮、内联编辑、状态反馈。负责人缺失为“负责人未分配”，优先级缺失/非法分别“优先级未设置/待核实”。正文Inter/Noto Sans SC 14px/1.45，ID等宽；按钮半径2px，卡片不超过8px；桌面局部padding24px、窄屏16px，动作gap12px；以现有token实现深浅金色强调。长ID换行，低高度自然滚动，不能仅用颜色表达分级。
权限差异仅隐藏写入口，服务端重验。显式保存/取消，Esc取消并返焦；外部点击不关闭，因为存在异步校验和审计。保存中禁重复；失败保留草稿和旧标签；冲突先重载再选择。切项目清理编辑与请求身份，迟到响应忽略；取消不能撤销已提交的服务端请求，重读真实值。
前后台一致性检查：品牌、导航、用户菜单、折叠保持现状；字体、图标尺寸、hover/focus/disabled、toast层级复用组件。未新增浮层，外部关闭capture场景不适用。
原型全部内存Mock；Skeleton可用显式测试数据，完成验收必须真实API保存回读，生产不得保留演示选择器及模拟延时。

## UI Skeleton
现有页面 → 交付卡 → metadata优先级/负责人 → priority editor插槽 → select/feedback/actions。先建立default/open/saving/error/conflict/readonly状态容器及稳定选择器，1440×900首轮截图确认后再实现细节与接口联调。

| 原型动作/元素 | 类型 | 目标data-testid | 状态与证据 |
|---|---|---|---|
| #badge | 标签 | change-priority-badge | 四档/缺失/非法；截图与筛选 |
| #edit/#editor | 内联组件族 | change-priority-edit/editor | open/readonly；键盘与权限 |
| #save/#level | 同一内联组件族 | change-priority-save/level | saving/error/success；回读 |
| #cancel | 同一内联组件族 | change-priority-cancel | Esc/cancel；无新增提交和返焦 |
| #reload | 同一内联组件族 | change-priority-reload | conflict；重载与版本 |
| #filter | 筛选 | change-priority-filter | all/P0-P3/missing/invalid/empty |

## 视觉采样与分批验收
批1卡片标签筛选，批2完整编辑动作族，批3只读/窄屏/主题与真实API。每批记录非目标区域未改。
对card、badge、editor、save、toast在1440×900和390×844、深浅主题、默认/展开/错误/只读采样font-family/size/line-height、width、padding、gap、border、background/color、overflow、position/z-index。期望为上述设计值与生成token；像素容差1px，颜色按token，实际样式见evidence/visual/computed-style.json与state-computed-style.json，逐项验收位于evidence/acceptance。Skeleton已获确认，视觉、样式和REQ最终一致性已完成，样本边界见verification.md。

## 风险与回滚方案
并发文件写入及审计一致性是主要风险，覆盖多writer和中断恢复；隐藏来源不降级为独立。回滚应用版本保留已写priority与审计，旧版本忽略新字段；不删除历史值。新增字段不作为归档门禁。


## 已确认的异步保存契约
用户已确认保留维护窗口与异步控制器。PUT /api/v1/requirement-center/changes/{change_id}/priority 接受 priority、expected_version、idempotency_key，返回202及操作标识；沿既有操作查询等待 applied，随后回读摘要。未建立维护窗口返回503，界面提示暂不可保存。冲突保留草稿，重载后重新提交。取消关闭界面不能撤销已入队操作，回读以服务端事实为准。
仅新增change-priority受控操作，不开放独立Change通用文档编辑。必要审计写在同一trace priority_history，控制器重新授权并核对完整快照及计划写集。沿用异步governance_application Task Trace及节点，因此 affected_layers 包含task_traces/task_trace_spans；无新增表或迁移。写锁只协调已登记writer，维护窗口声明外部写入暂停；不宣称任意外部编辑器可无锁并发。
