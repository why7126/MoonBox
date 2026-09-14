---
created_at: '2026-09-12 22:42:37'
updated_at: '2026-09-14 00:04:31'
---

## 1. 先行契约与 UI Skeleton

- [x] 1.1 复核REQ/Sprint双向追溯、最新REQ-0022实现与当前卡片源码；完成参考稿反向工程、selector映射、动作按钮/modal矩阵与样式采样基线。
- [x] 1.2 以现有renderIssueCard建立最小UI Skeleton及测试数据边界，仅新增ID行与替换标题；在1440px深浅主题完成首轮截图确认并记录computed style，确认后再开展细节任务。

## 2. 关系、授权与接口

- [x] 2.1 在稳定项目快照构建完整Issue/Change索引，覆盖双向结构化关联、短ID歧义、缺来源与冲突，保证关联识别先于授权过滤。
- [x] 2.2 增加独立Change对象授权，复用项目/对象读取及路径限制；统一卡片和直接文档API授权，回归隐藏Issue及多来源权限。
- [x] 2.3 实现活动/唯一归档/同ID冲突解析、未知状态集合及tasks未知处理；归档迁移不回退旧文档，不以全勾选判完成。
- [x] 2.4 扩展schema/current_change/related_changes及standalone_changes统计，保持原Issue身份与只读边界；明确多关联当前项选择证据，禁止循环末项推断。
- [x] 2.5 接入Change主文档、规格、trace与Sprint受控读取，校验归属和缺失反馈，不增加写权限。

## 3. 当前卡片增量接入

- [x] 3.1 使用真实响应驱动当前卡片两项修改，新增ID字体与原ID相同，标题来自同一Change；补齐无关联、缺中文标题、歧义、长ID和独立对象。
- [x] 3.2 扩展现有类型筛选/搜索与统计，关联ID命中原卡片、独立类型不重复计数；保留九阶段及项目切换刷新行为。
- [x] 3.3 按族回归原文档、tasks定位及footer动作与浮层退出，新增ID保持文本；无新增关联面板或抽屉。

## 4. 验证与文档同步

- [x] 4.1 后端单元/接口合成回归覆盖AC-001至007、009/010，包含权限越界、冻结空间、registry失败、归档歧义与无默认数据回退。
- [x] 4.2 Vitest覆盖卡片身份/标题与筛选归属；真实浏览器完成1440px深浅、390px、长ID、同字号computed style及旧交互回归，保留evidence/ui证据。
- [x] 4.3 使用专用授权项目和多成员账号真实观察新增关联、状态变化、归档与刷新；分别记录合成回归和真实观察结果，不能互相替代。
- [x] 4.4 同步OpenAPI、Orval、API索引及测试；验证Web/API观测字段、直接API拒绝日志、脱敏和采集失败降级，确认DB/部署/存储/Task Trace无新增变化。
- [x] 4.5 回填REQ主文档、故事、流程、acceptance、trace及prototype的一致性，更新Change验收与trace；运行中文、OpenSpec、Sprint scope及观测校验，执行Workflow Sync与AI Usage Hook后进入人工验收。

## 验收返修记录

- [x] 5.1 按附件对照修复独立卡片颜色与九阶段布局，核对重复归档身份并保留受控诊断
- [x] 5.2 回归筛选、统计、文档及1440/390深浅主题布局，补充computed style证据
- [x] 5.3 同步REQ子文档、原型意图、Change规格和Sprint验收，完成Workflow Sync及AI Usage

## 2026-09-13 返修验证

独立Change已使用info蓝框；unknown不再渲染九阶段之外的卡片，保留默认收起的只读数据异常入口，页面统计只计算真实阶段卡片。修正rc-content固定四行网格，改纵向flex，避免可选诊断行及窄屏标题动作遮挡。

证据：用户附件与源码路径已在design.md逐项对照；09-01/09-02同ID归档分别为建立契约/扩展动作矩阵，不是等价副本，保留历史冲突，不自动删除或按日期选版本。核对完成，不宣称历史ID冲突已被修复。

验证：Vitest需求中心与错误回归86项通过；TypeScript通过；后端既有Change身份/归档/权限8项通过。浏览器 `src/web/tests/requirement-center-change-layout.cjs` 四组1440/390深浅主题通过，styles.json和layout/diagnostics截图在logs/req0026-modify/。验证三类边框不同、九阶段DOM、无待核实卡片区、统计一致、仅unknown搜索、诊断折叠键盘与标题统计无重叠。视觉检查已查看1440深色和390浅色截图。首轮夹具缺项目目录上下文导致0卡片已修正；后续视觉发现固定网格重叠，留在本轮自修后重验。

Mock/API边界：本轮视觉采用真实浏览器组件与合成API，不冒称真实数据验收；本地Web服务更新另记。API/schema/权限/后端统计无修改，不需要OpenAPI或客户端重生成；DB、存储、安全策略及Task Trace无新增变更。product_data_collection_observability：applicable，affected_layers：web；复用既有读取请求，无新增埋点或日志字段。

REQ子文档一致性扫尾：已更新requirement、business-flow、user-stories、acceptance、prototype/context及prototype.html意图说明；trace由Workflow Sync更新。capture/review保持历史输入和原评审，不改写历史结论。Change design/spec/acceptance/verification与Sprint验收及release-note同步；Sprint容量、范围、API索引无需更新，原因是原Change内UI返修且接口不变。历史视觉证据不替代本轮截图。

## 验收返修记录：已完成独立 Change 的 Sprint 标签

- [x] 6.1 证据确认并拆分 Sprint 身份解析与文档可读性，支持唯一成员关系反查。
- [x] 6.2 补充成员歧义、显式关联、活动优先、缺文档和权限回归，1440px 深浅主题样式验收。
- [x] 6.3 同步 REQ、Change 增量规格、API 行为说明和 Sprint 验收记录。

REQ 子文档一致性扫尾检查：已同步 requirement.md、business-flow.md、user-stories.md、acceptance.md、prototype/web/context.md；trace 由 Workflow Sync 同步。无需更新 prototype.html 与既有原型图片，原因：既有 Sprint 标签位置、样式、动作均不变，本次修复 API 归属数据。review/capture 保留历史决策。无 API schema、DB、部署、安全或客户端生成变化。


## 7. 已评审阶段按钮增补（待实施）

- [x] 7.1 核对REQ/BUG参考组件，完善动作/弹窗selector与样式基线，完成1440px UI Skeleton首轮确认。
- [x] 7.2 复用阶段动作元数据与完整Change身份，接入权限、Sprint、验收证据和执行能力门禁，不新增执行器。
- [x] 7.3 一次实现开始开发、查看进度、完成/归档的按钮及既有modal/drawer族，覆盖禁用、加载、取消、失败、防重入和刷新。
- [x] 7.4 回归真实API权限/拒绝、缺tasks、只读/冻结、能力未接入及Demo无写入；验证观测与接口文档。
- [x] 7.5 完成1440/390深浅主题截图、computed style、关键交互与REQ子文档一致性，更新验收证据和工作流。

本轮停止前核对：已确认Skeleton，任务7.1至7.5自验完成；写执行服务缺失是范围内能力禁用分支，不宣称执行成功。REQ主文档、故事、流程、验收、trace和prototype已扫尾；capture/review保留历史，无需修改。

## 验收返修记录：固定禁用提示

- [x] 8.1 核对固定文案根因，复用阶段必需文档和实际权限原因，删除前后端固定禁用。
- [x] 8.2 独立Change复用REQ/BUG动作入口与验收条件，回归齐备/缺失/空文档、只读与进度。
- [x] 8.3 更新REQ六件套、原型说明、增量规格、API行为与Sprint验收；浏览器4组和后端94/前端79项通过。

REQ子文档一致性扫尾：主文档、故事、流程、验收、trace、context及HTML已同步新结论；capture/review保留历史，无需重写。旧固定禁用证据为历史，不代表当前效果。

## 验收返修记录：独立交付契约

- [x] 9.1 按acceptance_refs、实际验收报告或trace验证记录解析来源，取消固定acceptance.md要求，保留路径和空源保护。
- [x] 9.2 两个真实Change差异复核、95项后端回归与四组浏览器验证，同步REQ和增量规格。
- [x] 9.3 只读核对18102运行前端与后端镜像：旧固定提示未出现在当前代码，后端尚未包含本次来源修复；未部署，未声称旧提示的运行响应已复现。

## 验收返修记录：中文标题回退

- [x] 10.1 附件与文档证据确认：trace正文存在业务标题，原解析遗漏该来源。
- [x] 10.2 增加末级来源回退和通用章节过滤，覆盖优先级与空标题降级。
- [x] 10.3 四组浏览器标题与阶段交互、computed style验证通过；后端回归结果见verification。

REQ 子文档一致性扫尾检查：已同步requirement.md与acceptance.md，trace由Workflow Sync更新。无需更新business-flow.md、user-stories.md、prototype/web/context.md与prototype.html及历史原型图片：仍是“显示Change中文标题”的原流程和意图，本次补齐后端来源兼容，不改变布局、交互或角色；capture/review保留历史。API结构、DB、部署、安全、客户端生成无需更新；product_data_collection_observability：N/A，affected_layers：backend，原因是现有文档标题读取兼容，无新增采集或链路字段；validation：后端回归和合成API浏览器验证。
