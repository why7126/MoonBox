## 背景

REQ-0017 要求在 MoonBox 后台管理中新增空间管理模块。空间是产品研发协作与资源隔离容器，并执行“一空间对应一个产品”的强绑定规则。当前已有后台用户管理、后台 CRUD 列表模板和原型驱动 UI Gate，可作为空间管理实现的结构基线。

关联事实源：

- REQ：`issues/requirements/review/REQ-0017-admin-space-management/`
- Prototype HTML：`issues/requirements/review/REQ-0017-admin-space-management/prototype/web/prototype.html`
- Prototype Context：`issues/requirements/review/REQ-0017-admin-space-management/prototype/web/prototype-context.md`
- Interaction：`issues/requirements/review/REQ-0017-admin-space-management/prototype/web/interaction.md`
- Visual Reference：`issues/requirements/review/REQ-0017-admin-space-management/prototype/web/prototype.png`
- Knowledge Base：`docs/knowledge-base/best-practices/admin-list-page-consistency.md`
- Knowledge Base：`docs/knowledge-base/best-practices/admin-modal-width-css-cascade.md`
- UI Gate：`docs/standards/prototype-ui-acceptance.md`

## 目标与非目标

**Goals:**

- 建立后台空间管理导航入口、列表、申请审批、回收站和详情页。
- 建立空间、产品绑定、成员、配额、申请、生命周期和审计的数据/API 契约。
- 保证空间创建与审批通过时原子创建同名产品，并保持不可解绑的一对一绑定。
- 以 prototype 为输入完成 UI Contract、UI Skeleton、1440px 视觉验收和 computed style 验收。
- 复用后台 CRUD 列表页模板、fixed toast、设计系统确认弹窗和后台用户管理横切经验。

**Non-Goals:**

- 不实现用户侧空间申请页面和空间负责人扩容申请页面。
- 不支持一空间多产品、产品迁移或解绑。
- 不支持自定义角色权限、计费套餐、安全策略和数据区域配置。
- 不提供跨空间成员或资源批量迁移。
- 不在 `/req-opsx` 阶段写业务代码；实现由 `/opsx-apply REQ-0017-admin-space-management` 执行。

## 冲突处理

事实源优先级：

```text
prototype.html > prototype.png > prototype-context.md / interaction.md > acceptance.md > ui-design.md > openspec/specs
```

- 原型早期 token 使用浅色后台蓝色主色；`prototype-context.md` v1.0.1 之后明确以 `MoonBox-Platform-Operations-v1.0.5` 为视觉基线，默认暗色、金色主色、2px 圆角、224px 侧边栏和右侧无顶部导航容器。实现以最新 context 增量为准。
- 原型 HTML 中存在旧 `.top` 样式定义；v1.0.4 明确 `.main` 内直接挂载 `.content`，不渲染空白顶部栏。实现必须遵循 v1.0.4。
- 空间详情曾出现“最近操作”与“配额与用量”嵌套风险；v1.0.5 明确二者必须是独立 `.card` 节点。实现和验收以 v1.0.5 为准，详情页还必须保留原型中的详情头、负责人摘要/变更入口和概览、成员、产品、配额与用量、操作记录五个详情分区；详情头必须贴近原型的信息层级，面包屑为无边框文本路径，空间名称与状态同行，编码/来源和负责人摘要同组，右侧使用实体操作按钮；详情页局部字体、按钮、头像、卡片 padding 和间距必须按原型紧凑尺度收敛，不得继承后台页面标题级大字号或大按钮尺度。
- 原型 API 路径为 `/admin/spaces` 风格；项目 REST API 现有前缀为 `/api/v1/**`，后端实际路由 SHOULD 落在 `/api/v1/admin/spaces*` 能力域，前端服务层封装时隐藏基址差异。

## UI 契约

### 页面与入口

- 后台导航在 `OPERATIONS` 或等价运营分组中新增“空间管理”入口。
- 默认落点为“空间列表”；模块内页签为“空间列表”“申请审批”“回收站”。
- 模块内主页签必须位于页面标题区下方、筛选栏上方；不得放在右侧内容区最顶部，避免形成额外顶部导航条。
- 点击空间名称或“查看”进入空间详情；详情页包含概览、成员、产品、配额与用量、操作记录分区。
- 空间详情为独立详情视图，不作为“空间列表 / 申请审批 / 回收站”同级主页签展示。
- 空间详情页必须与空间列表页复用同一个后台 `AdminSidebar`，侧边栏 active、折叠态、用户菜单、个人资料、修改密码、返回前台、主题切换和退出登录入口保持一致；侧边栏自身以视口高度稳定布局，主内容滚动或详情内容变长不得撑高侧边栏，底部用户触发区需保持贴近视口底部可见。
- 空间详情页的编辑、调整配额、续期、移交负责人、冻结和删除入口必须复用对应真实操作弹窗与 API；操作成功后详情态应重新拉取当前空间详情和审计事件，概览最近操作同步刷新为真实审计最新 6 条；删除进入回收站后退出详情并回到空间列表；弹窗标题需展示具体操作名称。概览基础信息字段顺序为空间名称、唯一标识、创建来源、创建时间、有效期；有效期为固定日期时显示完整到秒，到长期有效时显示“长期有效”；最近操作动作文本不得过度加粗，应使用普通或中等字重，仅卡片标题保持强调。有效期固定日期输入使用后台统一轻量 `AdminDateTimePicker`，输入框展示 `yyyy-mm-dd hh:mm:ss`，展开面板同时支持日历日期选择、时/分/秒选择和快捷项；面板使用 body 级 fixed 浮层并适配暗色/浅色主题，不得被弹窗滚动容器裁剪。成员分区展示真实成员表格，字段为用户、角色、加入时间、状态和操作；负责人不进入成员表格，负责人变更仍走详情头变更负责人流程；成员角色仅包含管理员、编辑者和查看者，按管理员、编辑者、查看者排序，同角色按加入时间倒序；成员表格不得通过放大字号解决可读性，需通过适度行高、垂直 padding 和垂直居中缓解行间拥挤；添加成员候选仅来自用户管理中状态正常且非负责人、非既有成员的用户。操作记录分区接入真实分页 `/api/v1/admin/spaces/{space_id}/audit-events?page=&page_size=`，列表列为时间、操作人、操作动作、变更摘要、结果、操作；操作动作和结果使用差异化轻量标签与中文文案；操作记录分页使用轻量无边框样式，但必须保留 hover、focus-visible 和 active 状态。行内“查看”打开右侧详情抽屉，展示来源、对象、request_id、完整变更前后值、原因和结果；变更前和变更后存在 JSON 或原始文本内容时使用主题适配的 JSON code block 格式化展示，解析失败时降级为原始文本，长内容在 code 区域内滚动；当变更前或变更后为空、null、空字符串或“无”时，使用轻量空态文本“无”，不得使用大块 code block 或撑高抽屉。审批通过创建空间时，新空间详情必须可追溯审批来源；编辑空间、添加成员和编辑成员角色不按高风险操作处理，不强制填写操作原因，但仍需写入审计记录。产品分区顶部展示绑定关系 notice，下方按产品卡片列表展示，一张 Card 对应一个产品；当前阶段仅展示一个绑定产品卡片，卡片不显示“绑定产品”标题，字段为产品名称、产品 ID、绑定状态和研发状态，不展示产品数字段，不提供解绑、迁移或新增产品等未实现操作。
- 详情页“返回空间列表”是无边框文字链接，不使用实体按钮边框；hover/focus 仅通过文字颜色和下划线反馈。
- 访问必须要求后台登录态；操作入口根据服务端 `allowedActions` 和当前角色展示。

### 信息架构

- 空间列表：统计卡、全宽筛选栏、数据表格、分页、状态化行内操作；表格列按“空间名称/编码、负责人、成员数、产品数、AI 用量、有效期、状态、创建来源、更新时间、操作”展示。
- 空间列表中长期有效空间的有效期列展示“长期有效”，不得简写为“长期”。
- 申请审批：待办角标、后台统一紧凑审批表格、审批弹窗、通过/拒绝分支；表格字段为空间名称/编码、申请人、负责人、资源申请、有效期、申请时间和操作，空间名称/编码两行展示，资源申请用成员、存储和 AI Tokens 三个独立紧凑资源项展示，不使用分隔符伪元素；AI Tokens 使用中文短量级格式，如 `90万 Tokens`、`150万 Tokens`，避免长数字挤压有效期；操作使用用户管理同款轻量文字操作；本轮补真实分页，不新增搜索/筛选，避免在后端查询交互未确认前只筛当前页。
- 回收站：必须独立请求 `GET /api/v1/admin/spaces?status=RECYCLE&page=&page_size=` 的真实分页数据，不得从默认空间列表本地过滤；分页 total 使用回收站接口返回值；表格展示删除时间、删除人、删除原因、剩余天数和查看/恢复/永久删除操作；删除空间进入回收站后需刷新默认列表与回收站列表，并确保管理员切换到回收站时可看到该空间；回收站行内“更多”菜单必须复用普通空间列表 body 级 fixed 浮层能力，锚定当前回收站行按钮下方、左对齐并保留小间隙，不得向上漂移，菜单面板和菜单项文字必须完整可见，且不得被表格、分页、sticky 操作列或回收站容器遮罩或裁剪；当当前行无更多收敛操作时不得展示“更多”按钮或空菜单面板。
- 空间详情：详情头、负责人摘要、状态化操作、详情 Tab、基础信息、最近操作、配额与用量、审计时间线。

### 视觉 Token

- 遵循 `rules/ui-design.md` 与 prototype-context 最新增量：默认暗色后台、金色主操作、2px 圆角、224px 侧边栏、近直角和细线基调。
- 右侧内容区不得渲染空白顶部导航容器；页面内容从 `.content` 顶部开始。
- 筛选栏搜索框弹性占满剩余宽度，筛选控件保持稳定宽度。
- 空间列表主页签使用原型式下划线 Tab；统计卡展示空间总数、正常运行、已冻结、资源预警；AI 用量在列表中按原型使用两行展示，上行展示进度条，下行仅展示百分比数值，正常、预警和超限通过进度条和百分比颜色表达。
- 空间列中的空间名称必须是无边框文字链接；操作列宽度以用户管理列表为基准，1440px 桌面视口下操作列必须可见且不拥挤。
- 空间列表成员数和产品数字段为短数值列，AI 用量列按内容适度收敛但仍保留两行进度条表达，不得挤压操作列。
- 空间列表仍以用户管理列表作为后台列表视觉基准：行内操作使用无边框金色文字链接；状态展示使用低视觉重量的语义图标加文本，正常、冻结、回收站必须有不同图标或颜色区分。
- 除空间名称/编码列和 AI 用量列按原型两行展示外，空间列表其他表头和单元格内容不得换行；创建来源使用轻量标签；更新时间使用 `yyyy-mm-dd hh:mm:ss` 格式。更多菜单必须使用不受表格 overflow 或 sticky 操作列裁剪的浮层方式展示，并支持点击外部和 Escape 关闭；菜单定位必须锚定当前行“更多”按钮，显示在按钮正下方并从按钮左边缘展开，面板与按钮之间保留小间隙且不得重叠，不得横向漂移到筛选栏或表格中部；菜单面板必须不透明、紧凑，背景与边框颜色需适配暗色和浅色主题并与对应页面背景有清晰区分，菜单项内容靠左对齐，普通项高对比可读、危险项红色，并提供清晰 hover 与 focus-visible 高亮状态。
- 详情概览中“基础信息”位于左上，“配额与用量”位于左下，“最近操作”位于右侧，三者互不嵌套。
- 详情概览不展示空间与产品绑定提示；产品分区顶部展示“绑定关系不可解除或迁移，产品名称始终与空间名称一致。”提示，提示位于产品卡片列表上方。
- 产品分区按产品卡片列表建模，一张 Card 对应一个产品；当前一空间一产品阶段仅渲染一个产品卡片，产品卡片不显示“绑定产品”标题，字段使用详情页统一两列字段网格，展示产品名称、产品 ID、绑定状态和研发状态，为未来一空间多产品保留扩展结构。
- 空间详情概览必须保持左宽右窄的原型比例；基础信息卡使用两列字段网格，字段 label 与 value 均从各自网格起点对齐，不得呈现表单式缩进；最近操作使用清晰时间线圆点和竖线。
- 空间详情视觉尺度按原型 14px 基准验收：详情头 padding 约 18px，空间标题约 24px，负责人头像约 26px，普通操作按钮高度约 36px 且 padding 约 `8px 13px`，详情卡片 padding 约 16px，基础信息 label/value 分别约 12px/14px。
- 空间详情负责人摘要必须复用后台统一头像组件，优先展示真实负责人头像，缺失时 fallback 首字；负责人姓名与“变更”入口之间不再展示额外“负责人”文案；除空间标题和卡片标题外，面包屑、负责人、按钮、notice 和字段值不应使用明显加粗。
- 空间详情成员列表用户列必须复用后台统一头像组件，优先展示真实用户头像，缺失时 fallback 首字。
- 管理后台金色主按钮必须适配暗色/浅色主题：浅色主题下文字使用主题深棕或深文本色，避免突兀纯黑，字重使用中等；暗色主题下保持金色底与深色文字的可读对比。主按钮 hover 与 focus-visible 必须有清晰可见反馈。

### 交互状态

- `.tab[data-page]` 切换列表、审批、回收站。
- `.detail-link` 进入详情；`.detail-tab` 切换详情分区。
- 创建、编辑、审批、冻结、恢复、配额调整、续期、负责人移交、删除、永久删除均使用设计系统弹窗。
- 空间新增/编辑弹窗标题不展示图标；必填项 `*` 必须使用红色。
- 创建空间弹窗必须展示必填标记、输入要求和长度限制；字段顺序为：空间名称/空间编码、负责人/成员上限、存储空间/AI Tokens、有效期类型/到期时间、描述整行；空间名称等同当前绑定产品名称，空间编码等同当前绑定产品 ID，产品信息由这两个字段派生，不再让管理员单独填写产品 ID/产品名称。
- 创建空间和负责人移交弹窗中的负责人字段必须使用来自用户管理列表的“负责人”下拉/搜索选择器，候选仅限定状态为“正常”的用户；占位符为“请选择”，下拉项仅展示昵称或用户名，不展示角色；UI 不暴露 `owner_id`，提交时再映射为接口字段。
- 编辑空间弹窗不包含负责人和配额字段；负责人变更必须走独立“负责人移交/变更负责人”操作，配额变更走独立“配额调整”操作；描述字段独占一整行。
- 添加成员和编辑成员弹窗字段采用纵向布局；移除成员弹窗中的操作原因必填标签保持单行紧凑显示，红色星号不得单独换行。
- 添加成员和编辑成员弹窗中的用户与角色下拉展开列表必须脱离弹窗滚动容器裁剪，使用 body 级 fixed/portal 浮层或等价方案；菜单宽度与触发器一致，优先显示在触发器下方，空间不足时向上展开，背景不透明且层级高于弹窗内容。
- 有效期选择“长期有效”时不得展示或提交到期时间；选择“固定日期”时使用后台统一日期时间控件填写到期时间，日期和时分秒均可通过控件选择。
- 高风险动作必须二次确认、原因填写、防重复提交和 fixed toast 反馈；操作原因需参照 BUG-0010 的后台确认弹窗校验模式，展示红色必填标记、字段提示、`aria-invalid` 和 `aria-live` 错误反馈，空值或不足 4 字点击确认时不得静默无响应且不得发起写请求。
- 空间列表行内操作按原型收敛为查看、编辑、冻结/恢复和“更多”；配额、续期、负责人移交、删除和永久删除等低频或高风险操作进入更多入口，不在列表行内平铺。
- 低视口下弹窗 body 必须滚动，底部主操作和取消操作必须可访问。
- 后台管理下拉框必须统一使用 `AdminSelect` 或等价共享组件；用户管理、空间管理和后台分页条数下拉不得直接使用原生 `select`。展开列表必须位于触发器下方，不覆盖原下拉组件，并支持键盘选择、`Escape` 关闭和点击外部关闭。

### 图标与文案

- 用户可见文案中文优先，保持“空间管理”“创建空间”“申请审批”“回收站”“配额与用量”“操作记录”等产品化表达。
- 危险操作使用危险色和明确确认文案，不暴露内部命令名、脚本名或数据库字段名。

### Mock/API 边界

- UI Skeleton 阶段 MAY 使用 Mock 数据验证布局、状态矩阵和交互容器，但必须在 trace 中声明 Mock 区域。
- 业务完成态必须接入真实后台 API：空间列表、空间详情、创建/编辑、申请审批、冻结恢复、配额、删除回收、永久删除和审计记录。
- 生产实现不得把原型静态数据作为业务事实源。
- 前台空间申请入口未实现前，开发/演示环境可通过后端环境开关或 `scripts/seed-admin-space-applications.py` 生成待审批空间申请演示数据；该数据必须走真实后端申请数据结构与创建逻辑，生产环境不自动播种，前端不得硬编码生产 Mock。手动脚本必须加载本地 `.env` 并将 Docker 容器内 SQLite 路径 `/app/data/sqlite/moonbox.db` 映射为宿主机 `data/runtime/backend/sqlite/moonbox.db`，同时输出目标数据库路径和播种数量，避免播种到前端页面未连接的默认开发库。

### 权限规则

- 后台管理员可创建、审批、编辑、冻结、恢复、续期、调整配额和删除空间，具体操作以 `allowedActions` 为准。
- 超级管理员可提前永久删除回收期空间；普通后台管理员不得看到或使用永久删除入口。
- 系统保留空间和受保护空间不得删除。
- 前端隐藏或禁用无权操作，后端必须再次校验权限、状态和阻塞条件。

### 前后台一致性清单

- 侧边栏品牌区、分组、active 态、用户菜单和主题切换对齐现有后台。
- 空间管理页和用户管理页必须复用同一套后台侧边栏交互：折叠、底部用户菜单、个人资料、修改密码、返回前台、主题切换和退出登录行为保持一致，仅 active 项随当前模块变化。
- 空间管理页、用户管理页和后台分页必须复用统一下拉交互，保留各自原有选项、筛选、负责人选择、有效期选择和分页条数行为。
- 列表分页 DOM 对齐用户管理基准。
- fixed toast 不挤压布局。
- 设计系统确认弹窗替代 `window.confirm`。
- 弹窗宽度、低视口滚动和遮罩行为通过 computed style/浏览器检查。

## UI 骨架

### 页面结构

```text
AdminShell
  Sidebar
    OPERATIONS / SpaceManagementNavItem
    UserMenu / ThemeToggle
  Content
    SpaceManagementPage
      Header(title, subtitle, createButton)
      Tabs(spaces, approvals, recycle)
      SpaceListPanel
      ApplicationApprovalPanel
      RecycleBinPanel
    SpaceDetailPage
      DetailHeader(ownerSummary, statusActions)
      DetailTabs(overview, members, product, quota, audit)
      OverviewGrid(baseInfo, quotaUsage, recentActions)
  ModalLayer(create/edit/approve/freeze/restore/quota/renew/transfer/delete/purge)
  FixedToastLayer
```

### 区域边界与状态容器

- `SpaceManagementPage` 负责页签、筛选条件和列表刷新。
- `SpaceDetailPage` 负责详情数据、详情 Tab 和状态化操作刷新。
- `SpaceModalProvider` 或等价状态容器集中管理弹窗打开、提交、loading 和错误。
- `useAdminSpaces`、`useAdminSpaceDetail`、`useAdminSpaceApplications` 或等价请求封装隔离 API。

### 数据依赖

- `GET /api/v1/admin/spaces`
- `POST /api/v1/admin/spaces`
- `GET /api/v1/admin/spaces/{id}`
- `PATCH /api/v1/admin/spaces/{id}`
- `POST /api/v1/admin/spaces/{id}/freeze`
- `POST /api/v1/admin/spaces/{id}/restore`
- `POST /api/v1/admin/spaces/{id}/renew`
- `POST /api/v1/admin/spaces/{id}/transfer-owner`
- `GET /api/v1/admin/spaces/{id}/members`
- `POST /api/v1/admin/spaces/{id}/members`
- `PUT /api/v1/admin/spaces/{id}/members/{member_id}`
- `DELETE /api/v1/admin/spaces/{id}/members/{member_id}`
- `PATCH /api/v1/admin/spaces/{id}/quota`
- `DELETE /api/v1/admin/spaces/{id}`
- `DELETE /api/v1/admin/spaces/{id}/purge`
- `GET /api/v1/admin/space-applications`
- `POST /api/v1/admin/space-applications/{id}/approve`
- `POST /api/v1/admin/space-applications/{id}/reject`
- `GET /api/v1/admin/spaces/{id}/audit-logs`
- `GET /api/v1/admin/users?status=正常`，用于创建空间与负责人移交时选择状态正常的负责人。

### 可测选择器

- `data-testid="admin-space-page"`
- `data-testid="admin-space-tabs"`
- `data-testid="admin-space-filterbar"`
- `data-testid="admin-space-table"`
- `data-testid="admin-space-pagination"`
- `data-testid="admin-space-detail"`
- `data-testid="admin-space-modal-create"`
- `data-testid="admin-space-modal-edit"`
- `data-testid="admin-space-modal-approve"`
- `data-testid="admin-space-modal-freeze"`
- `data-testid="admin-space-modal-quota"`
- `data-testid="admin-space-toast"`

### 1440px 验收焦点

- 空间列表首屏：侧边栏、标题区、页签、统计卡、筛选栏、表格和分页完整可见。
- 申请审批页：待办角标、审批弹窗、拒绝原因必填。
- 回收站：剩余天数、恢复、永久删除入口权限差异。
- 空间详情概览：基础信息、配额与用量、最近操作独立卡片布局。
- 空间详情分区：详情头、负责人变更入口、详情内五个分区 Tab 和成员表格、产品/配额/操作记录分区可见并可切换。
- 弹窗：创建/编辑/审批/冻结/恢复/配额/删除/永久删除的宽度、滚动、遮罩、底部操作。
- fixed toast：成功/失败反馈不挤压布局。

## 决策

### D1 使用原型承接 + 后台 CRUD/DS 组件化落地

选择：以 prototype 作为结构与交互输入，使用现有后台 Shell、CRUD 列表模板、设计系统弹窗和 fixed toast 落地。

原因：直接复制静态 HTML 会绕开现有组件、权限、API 和测试体系；从零设计会丢失用户确认过的页面结构。组合策略能保留原型意图，同时符合项目后台一致性。

### D2 后端以空间领域模型为事实源，前端只消费 `allowedActions`

选择：空间状态、权限、阻塞条件和高风险动作校验由后端负责，前端根据 `allowedActions` 展示入口。

原因：冻结、回收、永久删除和配额限制属于安全边界，不能只靠前端隐藏按钮实现。

### D3 空间与产品绑定在服务层原子创建

选择：创建空间和审批通过时由服务层在同一事务中创建空间、同名产品和绑定关系。

原因：REQ 明确“一空间对应一个产品”永久绑定；拆成两个非事务调用会导致空间存在但产品缺失或产品名不同步。

### D4 有效期使用互斥类型模型

选择：使用 `fixed_date` / `long_term` 两种互斥类型，`long_term` 不保存结束日期。

原因：可以避免空日期占位、误触发到期提醒或自动冻结。

### D5 负责人由用户管理列表选择

选择：创建空间与负责人移交时复用后台用户管理列表作为候选来源，仅展示状态正常的用户；UI 展示负责人昵称或用户名，不展示角色，提交时映射为 `owner_id`。

原因：`owner_id` 是内部接口字段，管理员应选择具体用户而不是手输 ID；复用用户管理列表可以保证候选来源、状态语义和用户管理事实源一致。

### D6 当前一空间一产品下产品信息由空间字段派生

选择：当前版本不再在创建/编辑弹窗中单独填写产品信息，空间名称同步作为产品名称，空间编码同步作为产品 ID；后端仍保持空间与产品分表存储，为未来一空间多产品保留演进空间。

原因：REQ 当前明确一空间一产品，单独填写产品信息会制造重复输入和不一致风险。

## 风险与取舍

- [Risk] Sprint 容量已达到 113.3%，空间管理又是后台主能力 → [Mitigation] `/opsx-apply` 必须先完成 Skeleton 和数据模型/API 边界，避免边做边扩范围；超出范围拆后续 REQ。
- [Risk] 原型与最新 UI token 存在历史差异 → [Mitigation] 以 prototype-context 最新增量和 `rules/ui-design.md` 为准，Change trace 记录冲突处理。
- [Risk] 只实现静态页面会漏掉权限、状态机和审计 → [Mitigation] tasks 将后端模型/API/权限审计列为独立任务，验收要求真实 API。
- [Risk] 弹窗数量多，容易出现宽度、滚动或遮罩回归 → [Mitigation] 强制 admin-modal 横切 AC、computed style 和低视口验收。

## 迁移计划

1. 新增数据库迁移和后端模型/Repository/Service/API。
2. 新增前端 API client 封装和后台空间管理页面 Skeleton。
3. 接入真实 API，补齐列表、审批、回收站、详情和弹窗交互。
4. 补齐测试、OpenAPI/API 文档、数据库文档和 UI 验收证据。
5. 通过 `/opsx-apply` 完成实现后，由 Workflow Sync 更新 REQ/Sprint/Change 状态。

## 待确认问题

- 空间成员与现有用户/未来组织权限模型的长期关系是否需要在后续独立 REQ 扩展。
- 通知实际发送渠道首版是否仅记录通知事件，还是需要真实站内通知/邮件通道；本 Change 以通知事件契约和可测试触发为主。
