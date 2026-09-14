## MODIFIED Requirements

### Requirement: 需求中心上下文聚合

系统 SHALL 基于服务端授权的 space_id 与 repository_id 提供前台需求中心上下文聚合接口，返回当前用户、可访问空间、当前空间、权限态、统计、筛选选项、治理对象列表、卡片文档入口、动作映射和进度摘要。

#### Scenario: 首屏获取真实上下文

- **WHEN** 用户进入 `/requirements` 且请求需求中心上下文接口
- **THEN** 系统返回可驱动页面首屏的用户、空间、权限、统计、筛选和治理对象数据
- **AND** 每个治理对象必须包含可展示的文档入口摘要
- **AND** 每个治理对象必须包含当前阶段允许动作及禁用原因
- **AND** 待开发、研发中、验收中或已完成对象可以包含可展示的任务进度摘要
- **AND** 采集池、规划中、待评审和已评审对象即使历史字段中存在任务进度，前端也不得展示为研发进度入口

#### Scenario: 未登录访问需求中心

- **WHEN** 未登录用户进入 `/requirements`
- **THEN** 系统先展示登录页，不渲染需求中心看板或发起需求中心上下文请求

#### Scenario: 接口使用统一响应结构

- **WHEN** 前端调用 `/api/v1/requirement-center/context`
- **THEN** 请求必须携带有效 Bearer 会话，响应使用项目统一 API 响应结构和受控错误码

### Requirement: 治理文件事实源聚合

系统 SHALL 从当前授权项目的治理文档、REQ/BUG registry、Issue trace、Sprint 四件套和 OpenSpec Change 元信息聚合首版真实数据。

#### Scenario: 聚合 REQ 与 BUG registry

- **WHEN** 后端构建需求中心治理对象列表
- **THEN** 系统读取 `issues/requirements/_registry.yaml` 与 `issues/bugs/_registry.yaml` 的白名单字段

#### Scenario: trace 优先于 registry

- **WHEN** Issue `trace.md` 与 registry 摘要状态不一致
- **THEN** 系统以 `trace.md` 为优先事实源，并返回对象级漂移提示

#### Scenario: Docker 环境读取治理事实源

- **WHEN** 后端运行在 Docker Compose 中
- **THEN** 系统通过已授权项目绑定解析治理目录，以只读方式聚合 `issues/`、`iterations/`、`openspec/`、`docs/` 和 `rules/`，不得依赖容器源码或无作用域全局目录
- **AND** 受控文档写入与治理成果应用由可信写入通道统一协调，普通聚合接口不获取任意主机写权限

#### Scenario: 完整仓库归档事实

- **WHEN** registry 中的 Issue 已完成且关联 Change 或 Sprint 已迁入归档目录
- **THEN** 聚合保留 Issue 已完成阶段并读取归档事实，不因活动目录缺项回退为待开发
- **AND** 已完成事项的历史漂移作为诊断信息，不计入当前阻塞
- **AND** 对象计数仅覆盖 registry 注册项，不自动纳入未注册基础建设目录

#### Scenario: 验收文档与卡片展示分离

- **WHEN** applied Change 的卡片展示精简 Change 文档入口
- **THEN** 系统将对象映射验收中，使用真实 Issue 文档检查 acceptance.md 存在性与非空内容
- **AND** 卡片未显示该文件不等于文档缺失

## ADDED Requirements

### Requirement: 项目作用域及版本校验

系统 SHALL 在所有需求中心数据、文档与保存入口重新验证项目权限和版本，拒绝隐式跨项目回退。

#### Scenario: 缺少或无权项目身份
- **WHEN** 请求缺少空间仓库身份或用户无权访问
- **THEN** 系统拒绝请求，不返回全局治理数据或其他项目缓存

#### Scenario: 保存旧文档基准
- **WHEN** 文档内容已被外部更新而用户携带旧版本保存
- **THEN** 系统返回冲突并保留外部文件，页面保留用户草稿

### Requirement: 项目快照自动刷新

系统 SHALL 在服务正常、前台可见及文件稳定可读条件下于5秒内反映治理变化，异常保留最后完整快照。

#### Scenario: 正常轮询与页面恢复
- **WHEN** 本地治理文件稳定落盘或页面恢复可见
- **THEN** 前台主动刷新当前项目，保留筛选和草稿，在工具栏刷新按钮提示中显示成功同步时间，需求中心不显示独立项目连接栏

#### Scenario: 解析失败与迟到响应
- **WHEN** 文件写入中、解析失败或响应属于已离开的项目
- **THEN** 系统不呈现部分快照或旧项目内容，失败显示状态并可手动重试


#### Scenario: 首屏加载与后台刷新分离

- **WHEN** 首屏快照尚未返回
- **THEN** 指标、阶段计数和卡片位置显示骨架，不呈现假零值、空态或独立加载面板
- **AND** 标题、工具栏与阶段列在加载完成前后保持位置稳定
- **WHEN** 已有快照时手动刷新或轮询
- **THEN** 保留已有数据与筛选，只显示刷新按钮忙碌状态


#### Scenario: 卡片追踪文档固定所属Issue

- **WHEN** 用户在任一阶段查看REQ或BUG卡片
- **THEN** 卡片仅提供一个标签为trace.md的入口，读取所属Issue目录的trace.md
- **AND** 不提供Change trace入口，文件缺失时明确不可用且不回退Change trace
- **AND** Change仍用于内部阶段计算，其他文档入口和原授权边界保持


#### Scenario: 卡片进度入口定位任务文档

- **WHEN** 用户点击 REQ 或 BUG 卡片的研发、测试或人工验收入口
- **THEN** 系统 SHALL 通过当前卡片关联文档入口读取完整 tasks.md，在加载后优先定位对应章节、其次定位匹配任务并高亮，不打开独立进度面板，不改变文档权限
- **AND** 关联或文件缺失时 SHALL 明确提示；目标章节或任务缺失时 SHALL 展示完整文档并说明未找到目标，不回退其他文档或历史返修任务


#### Scenario: 卡片读取关联 Sprint 计划

- **WHEN** 用户查看已关联 Sprint 的 REQ 或 BUG 卡片并打开 sprint.md
- **THEN** 系统 SHALL 在授权项目内根据关联和成员关系解析 Sprint 文档，卡片展示、文档读取和缺失校验共用该解析，提供完整只读正文
- **AND** 系统 SHALL 兼容同 ID 的活动和归档目录，仅活动目录不存在时查归档目录；关联或文件缺失时明确提示，不回退 Issue、Change、其他 Sprint 或活动目录缺文件时的旧归档副本


#### Scenario: 主动作阻塞提示与禁用一致

- **WHEN** 卡片存在接口阻塞、Issue阻塞或缺少当前阶段前置文档
- **THEN** 系统 SHALL 使用同一原因显示阻塞提示并禁用主动作，执行前再次检查，不打开动作弹窗或提交操作；已有文档仍可阅读
- **AND** 前置条件补齐并刷新后 SHALL 根据新结果恢复主动作

#### Scenario: Tips 避让 Agent 助手

- **WHEN** Tips与Agent助手同时显示，包含窄屏及长文案场景
- **THEN** 系统 SHALL 在助手上方显示Tips并保留间距，保证可读层级、边界内宽度及长词换行，超长内容允许容器内滚动


#### Scenario: Issue 主文档生成后持续展示

- **WHEN** REQ的requirement.md或BUG的bug.md已在所属Issue目录生成
- **THEN** 系统 SHALL 在所有阶段卡片保留该主文档并优先显示，包括已完成阶段；读取所属Issue当前或归档目录的实际正文，保留既有编辑权限
- **AND** 系统 SHALL 不使用Change同名文件补齐；未生成不伪造入口，后续删除按快照反映，读取缺失时明确提示


#### Scenario: Sprint 文档跨阶段持续展示

- **WHEN** 卡片已具备关联Sprint的sprint.md文档入口
- **THEN** 系统 SHALL 在后续全部阶段持续展示该入口，包括已完成；主文档requirement.md或bug.md仍优先
- **AND** 系统 SHALL 保留关联来源、只读权限、归档兼容与缺失不回退，不因展示范围扩大而新增其他阶段必需文档校验


#### Scenario: 卡片文档按用途分组
- **WHEN** 卡片存在常驻文档或阶段文档
- **THEN** 常驻文档按主文档、Sprint、trace排序，阶段文档按当前任务优先排序
- **AND** 双组以4px紧凑换行区分，无分隔线，单组无占位，来源、权限、必需文档校验不变


#### Scenario: 完整卡片更新时间
- **WHEN** 展示任一阶段REQ或BUG卡片
- **THEN** 有效更新时间显示YY/MM/DD HH:mm，缺失或无效显示更新时间未知，不补造日期或时分
- **AND** 窄屏时间不拆分，必要时footer动作换行


#### Scenario: 所属需求原型持续展示
- **WHEN** 所属REQ存在安全可读的原型HTML
- **THEN** 所有阶段主文档之后展示原型入口，多端标识区分，兼容归档
- **AND** 缺失不占位、不新增必需文档，保留项目授权和HTML预览安全策略


#### Scenario: 原型标签仅保留相对路径
- **WHEN** 卡片显示原型HTML入口
- **THEN** 标签为区分多端所需相对路径，不附加“原型 · ”前缀，排序与预览行为不变
