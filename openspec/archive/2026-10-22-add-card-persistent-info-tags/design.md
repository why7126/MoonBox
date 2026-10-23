---
title: 卡片常驻信息标签设计
created_at: "2026-10-22 13:56:36"
updated_at: 2026-10-22 19:20:00
---

# 卡片常驻信息标签设计

## 背景与现状

来源 REQ-0051-card-persistent-info-tags，状态 in_sprint，归属 sprint-013。现有 RequirementCenterPage.tsx 的 rc-card-tags 显示等级及负责人；服务 requirement_center.py 读取 Sprint Scope 并支持授权文档查看。现有根因样本兼有 status 与 root_cause_status，不能只读单字段。

## 目标与非目标

落实来源 PRD FR-001—006 和18项AC；有数据后持续展示至已完成。无实际工时统计、人天编辑、新权限、数据库迁移或阶段门禁变更。

## 设计决策

D1 采用现有设计系统 Token 与局部 CSS 扩展（DS策略），保留页面和文档抽屉。原型仅作为标签结构输入；不整页移植原型 CSS，避免重写现有看板和抽屉。

D2 后端在同一授权治理快照中聚合标签元数据，不让前端逐卡请求完整根因正文。复用快照失效机制；授权撤销与项目切换不得保留越权数据。缓存不能仅靠TTL掩盖同尺寸修改。

D3 人天来自对象有效归属的 Sprint scope_estimates：完整 Issue ID 总估算优先，Issue/Change 同行只计一次；相同身份与数值重复去重，冲突返回未知。不跨Sprint累加。没有总量时仅完整唯一的关联Change分项可求和；无法证明完整不显示。合法有限非负数包含0，小数无多余尾零，字符串/布尔/负数/非有限数拒绝。有效归属含 archive，顶层容量和story_points不替代人天。

D4 有效根因正文必须在分析或证据章节包含非空非模板内容；状态、标题、注释和空表格不算。专用 root_cause_status 优先，兼容合法根因 status，均缺失时兼容根因状态章节。普通生命周期status不参与比较；多个明确根因声明冲突或专用字段非法时只显示待确认。unknown/hypothesis/probable映射待确认，一致confirmed映射已确认；该读取不改根因确认规则。

## 数据与 API

卡片响应拟增可空 estimated_person_days、estimate_status（available/missing/conflict/invalid）、root_cause_state（absent/pending/confirmed）、root_cause_reason 和可复用的根因文档能力引用。root_cause_reason 为安全枚举或简短诊断，不能含正文与绝对路径。沿用现有命名和模型约定，字段最终在OpenAPI与客户端映射中统一，旧字段语义不变，旧响应缺失新字段时前端隐藏新增标签。

API契约变更同步后端响应模型、OpenAPI、Orval/客户端类型、docs/03-api-index.md与接口测试。不新增DB表、SQLite/MySQL迁移或对象存储写入。请求保持现有登录、项目与文档读取权限。

## UI Contract：界面契约

页面 /requirements；仅新增标签与根因按钮。顺序：等级、负责人、根因、人天；flex换行，不删除第二标签。新旧标签共用字体、10px字号、1.2行高、3px 8px内边距、20px圆角且无描边；根因保留状态色、点击与focus-visible提示。标签间距6px；人天只读并有预估提示。深浅主题均保留文字状态及可见焦点。

前后台一致性：复用现有品牌、字体、颜色和图标习惯，无管理端改动；页面壳、筛选、主动作不变。根因按钮Enter/Space与鼠标等价，打开对应文档，阻止触发卡片动作；关闭/Esc/外部点击及焦点返回复用文档抽屉。内部stopPropagation不影响外部退出。

Mock/API边界：REQ原型数据全部为Mock；实现接真实聚合接口与授权文档读取，禁止生产用原型值兜底。已完成仅保留读取能力，编辑权限不扩大。

## 冲突处理

事实源优先级：原型HTML、PNG（本次无）、原型context、验收、UI规则、既有spec；冲突明确决策后以本设计及同步后的REQ为准。

唯一已发现差异：HTML抽屉宽560px为示意，而已生效规格支持桌面420—760px可拖拽及移动全宽。本需求非抽屉重构，选择保留既有能力；在REQ原型说明同步例外。没有删除或修改旧条文，delta使用ADDED追加要求。PNG不要求当前导出，不能用其缺失声称验收通过。

## UI Skeleton：结构与首轮门禁

保留现有页面壳与rc-card，标签行增加可空根因/人天插槽；根因触发共享文档抽屉。先以隔离样本构建无值、仅人天、仅根因、两者都有的状态容器，在1440px核验布局及选择器后再做细节。数据层与视觉样本明确分离，最终接入API并移除Mock兜底。

## UI Reference Replication Contract：局部一致契约

| 组件 | 参考与目标selector | 批次 | 验证 |
|---|---|---|---|
| 既有卡片与标签 | .rc-card / .rc-card-tags | 1 | 四组合与原有层级 |
| 根因按钮 | [data-testid="root-cause-tag"] | 1/2 | pending/confirmed/冲突、键盘焦点 |
| 人天标签 | [data-testid="person-days-tag"] | 1/2 | 0/小数/缺失、顺序 |
| 文档抽屉 | 现有drawer，新增可测根因锚点 | 2 | loading/正文/无权限/缺失/读取失败 |

动作矩阵：根因按钮→共享Markdown抽屉→root-cause-tag/root-cause-document→上述全部状态→AC-007截图及交互证据；人天无modal。一次完成按钮与抽屉状态族，不逐按钮拆分返修。页面壳、品牌、指标、筛选、列头、空列、滚动保留现状，无新增FAB或footer动作。

computed style采样：1440×900及390×844，深浅主题；标签字号10px与gap6px为当前基准，其余沿用现有Token，产品首次采样记录当前值和最终期望值。几何容差1px，颜色按Token精确值；记录font-size/line-height/padding/gap/border/background/color/overflow；抽屉另查width/position/z-index。当前产品尚未实现，当前值标待采集，不伪造。

验收分批：1结构与四组合首轮1440px；2真实数据和整个根因交互族；3全阶段×视口×主题及最终文档一致性。证据保存evidence/acceptance，按AC与状态命名；返修后受影响证据失效重采。

## 产品数据采集与链路观测

product_data_collection_observability: applicable；affected_layers: web、api、usage_events、request_logs。依据docs/standards/product-data-collection-observability.md。文档点击沿用行为与request关联，直接API不伪造用户事件。validation：AC-007/009/011验证权限、隔离、事件失败不阻断、OpenAPI/Orval契约；诊断日志不写根因正文、凭证或本机路径。N/A：只读聚合不新增长任务、task_traces/task_trace_spans、DB结构、存储写入、保留周期或部署变更。

## 验收与知识库承接

18项AC逐项引用来源REQ acceptance.md；其中11功能、3横切、4原型。引用prototype-driven-ui-gate.md、20260912-requirement-center-read-performance.md、sprint-011-retrospective.md，覆盖快照/权限失效、避免重复读取、当前事实与历史证据区分。具体执行先生成逐AC验收计划，再按opsx-accept当前指纹与队列采证。

## 风险与回滚

历史字段冲突→保守待确认；估算重复→去重与完整性校验；每卡读文档→后端同快照聚合并比较请求数；视觉密度→窄列换行证据。回滚前后端增量即可，无数据迁移；旧客户端忽略新增字段，新客户端容忍字段缺失。

## 待决事项

无阻断设计决策。部署端实际样本、当前computed style和性能基线在apply预检获取，不宣称已完成产品验收。

## 验收返修决议

人天按有效非负值d分档：S为0≤d≤1，M为1<d≤3，L为3<d≤5，XL为5<d≤10，XXL为d>10；显示“档位·数值人天”（如“M·3人天”），不含“开发”前缀。S青、M蓝、L紫、XL橙、XXL玫红，保留精确值和“档位 · 预估开发数值人天”提示；缺失/非法值隐藏。

用户最新要求覆盖原型12px及描边，统一共享标签规则。反馈对照及验证见acceptance-fixes.md。

分隔点展示细则：去除两侧普通空格，使用独立分隔点左右各2px固定间距；其余标签样式及根因交互保持不变。
