---
title: Change 来源估算修复验证记录
created_at: '2026-10-31 23:48:00'
updated_at: '2026-10-31 23:48:00'
---

# Change 来源估算修复验证记录

## 修改范围
card_metadata.py 增加仅由完整关系索引授权的来源回退；change_index.py 验证完整唯一关系、Sprint双方成员；schema增加estimate_source_issue_id，CardInfoTags保留标签布局并增加来源提示。OpenAPI/Orval及API索引同步。无DB迁移、权限放宽、容量计算变更或源文档写入。测试覆盖前后端、完整/摘要API。

## 机制与测试证据
真实仓库BUG-0070与归档Change的当前只读索引投影为3/available，来源ID正确；这是真实输入的函数验证，不冒称浏览器。来源自身优先、非法/冲突不掩盖、零值小数、重复、隐藏/归档/缺目录兄弟、多个来源、权限拒绝与只读性均有回归。测试夹具曾因未导入chat、将审计DB混入源文件哈希及重复status参数失败，已修复测试设置，不修改业务门禁。全量索引验证曾触发无关历史验收计算，已改用目标摘要读取。

## 横切与UI边界
AC-XCUT为n/a（非管理端列表/表单/modal/上传）；知识库partial-delivery-sprint-handoff已读并用于防止总量复制。无prototype、无新骨架、无参考稿复刻；原截图只作为数据缺失证据。原有person-days-tag标签与样式不变，真实浏览器验证来源提示、刷新及窄屏另见evidence/acceptance/visual-review.md。

## 数据采集与链路观测
product_data_collection_observability: applicable；affected_layers: api、web、request_logs。现有请求仍经过原路由、权限及请求日志，完整与摘要响应契约一致。API回归检查可信X-Request-ID；既有交付观测测试覆盖直接API不伪造行为、事件关联及脱敏降级。新投影只返回已授权Issue ID与数值，不记录正文、凭据或原始响应。未改请求封装、行为字典、日志保留周期；纯同步只读计算不新增Task Trace。DB、对象存储、客户端请求头及部署拓扑不变；仅按用户授权重建现有本地测试服务，无正式发布。

## 门禁与待完成
根因5证据、Sprint范围、标题、中文、OpenSpec严格、观测声明、上下文预算及目录结构通过。新增后端20项、相关前端23项、TypeScript与生产构建通过；自动验收首轮8/8，2次命令执行、6次去重。补入完整delta及生效规格输入后重新验证归档准入。真实观察详见视觉记录。

全仓Design System检查存在243项既有违规，集中在未由本次修改的样式、原生控件及预览；本次未新增样式或控件，仅复用既有标签。目录检查提示legacy SQLite目录，保留原数据；未自动迁移。首次Docker reap受沙箱连接限制，本次更新为既有常驻服务，未创建临时环境。

## 最终结果
完整验收8/8通过，证据包evidence/acceptance/20261031235345727111-7cd273ef/；归档预演与最终准入ready。实现applied，BUG验收passed，未执行正式归档。
