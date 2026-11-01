# standalone-change-priority Specification

## Purpose
TBD - created by archiving change add-standalone-change-priority. Update Purpose after archive.
## Requirements
### Requirement: 分级事实源与兼容
系统 SHALL 按独立 Change 类型读取 trace.severity 或 trace.priority；fix 使用严重性，其余使用P0/P1/P2/P3。缺失待评估、非法或类型冲突待核实，来源受限不能当作独立。保留历史且不机械映射，不批量回填。

#### Scenario: 读取旧对象
- **WHEN** 读取缺字段的旧fix或非fix对象
- **THEN** fix旧priority仅供追溯，非fix合法priority继续显示；负责人独立，不新增历史开发归档门禁。

### Requirement: 授权保存与并发审计
系统 SHALL 只允许授权活动独立对象按正确维度维护，校验项目、来源、类型和版本，原子记录等级与必要审计，同值不刷新业务时间。旧priority API对fix拒绝入队，排队执行再次复核。

#### Scenario: 保存时版本变化、来源受限或归档
- **WHEN** 版本变化、来源受限、归档或fix调用priority接口
- **THEN** 拒绝覆盖、越权或错维度写入，保留旧数据；合法成功返回版本及可信主体记录。

### Requirement: 编辑反馈与筛选
系统 SHALL 将独立Change卡片分级改为只读，移除设置入口、编辑区、保存取消及替代入口；按维度筛选四档优先级或五档严重性与异常状态，保持原排序与Issue分级。

#### Scenario: 查看卡片
- **WHEN** 用户查看、刷新、搜索或切换交付阶段
- **THEN** 正确展示严重性或优先级，缺失和非法状态明确，无鼠标键盘分级编辑入口，无卡片保存请求。

### Requirement: 来源转换与观测
系统 SHALL 在建立Issue关联后停止独立分级写入，保留旧值并展示来源分级；可信请求与治理审计可追溯，非必要遥测故障不阻断业务。

#### Scenario: 直接API调用或遥测故障
- **WHEN** 直接调用或遥测故障
- **THEN** 不伪造点击事件，不记录凭证全文，必要审计不能跳过，保留可信请求关联。

### Requirement: 原型与真实验收
系统 SHALL 将原型作为设计输入，完成UI Contract、Skeleton确认、双视口关键交互视觉、computed style、Mock/API声明及REQ一致性后交付。

#### Scenario: 提交完成与归档验收
- **WHEN** 提交完成或归档
- **THEN** 提供全部AC映射、1440及390深浅主题与各阶段证据；保留原交付动作，缺证不宣称通过。

### Requirement: 创建时自动评估分级
系统 SHALL 在独立Change创建完成前识别来源及类型、基于材料评估等级并持久化理由和证据引用；新建明确类型，历史类型可按fix-前缀兼容，冲突待核实。

#### Scenario: 创建材料充分的独立对象
- **WHEN** 无来源且材料充分
- **THEN** fix生成合法severity，其他生成priority及评估记录；重试保留有效结果不重复写入。

#### Scenario: 评估材料不足
- **WHEN** 自主补证后仍不足
- **THEN** 标记pending和具体缺口，可保留proposed草稿但不得报告创建完整成功，不伪造默认等级。

