---
title: 独立交付卡片验收返修台账
---
# 独立交付卡片验收返修台账

## 2026-10-31 卡片顶部布局

返修执行中展示为研发中；保留applied及首次完成事实。用户已通过opsx-modify授权此两项局部调整，无需重做骨架确认。

### 附件截图逐项视觉对照表

| 附件/截图编号 | 页面/状态 | 对照对象 | 期望表现 | 实际表现 | 偏差项 | 检查方式 | 处置结论 | 证据入口 |
|---|---|---|---|---|---|---|---|---|
| 用户附件60446d41；before-1440 | /requirements，附件浅色/实际深色，验收中，实际视口1440×900；附件为卡片裁图 | REQ-0056标题与完整Change ID | 标题下方显示完整Change ID | ID位于标题上方 | 信息层级顺序 | 截图、DOM子元素及bounding rect | 本次修复 | evidence/acceptance/layout-repair/before-1440.png；DeliveryCardIdentity.tsx |
| 同上 | 同上，无浮层 | P1、产品团队、人力估算 | 同一标签容器，同排；窄屏不足时自然换行 | 待估算在标签容器外另占一行 | 排列与文案 | 截图、.rc-card-tags与rc-estimate-pending父子关系 | 本次修复 | 同上；RequirementCenterPage.tsx |

根因confirmed：渲染顺序与容器归属直接对应截图。修改范围仅Web呈现；product_data_collection_observability: N/A，affected_layers: [web]，原因：不变更请求、遥测、权限或数据契约。validation：前端定向测试2/2、TypeScript及Vite构建通过；真实产品标题打开当前Change proposal抽屉且关闭焦点回归正常；两主题×两视口截图及样式顺序/同排断言通过。

### 本批视觉契约

顺序为来源编号/Sprint → 中文标题 → 完整Change ID → 标签行 → 三组文档。标题交互不变，Change ID保持等宽次要文字与任意长词换行。估算缺失显示“人力待估算”，冲突/无效保持“估算待核实”；全部置于rc-card-tags，与已有工期标签互斥。复用现有tag样式与flex-wrap。采样标题/ID bounding rect、font-size、line-height、margin；标签display/gap/flex-wrap及子元素坐标。1440px及390px深浅主题验证；既有动作族矩阵不变，抽屉以标题及任务入口回归。

### REQ子文档一致性扫尾检查

已检查并更新requirement、business-flow、user-stories、acceptance、prototype/web/prototype.html及context的布局/文案；原PNG保留历史参考，由context明确本批反馈优先。Issue trace通过Workflow Sync更新。无需更新capture/review，原因：原始记录和评审历史不变。无需更新API、DB、部署、安全与生成客户端，原因：本批仅DOM顺序和展示文案调整。

### 本批验证与证据

附件两项均已修复。新版Web容器已健康运行；真实产品截图product-after-dark-1440.png与product-title-drawer-1440.png，样式product-styles.json；合成只读组件截图preview-{light,dark}-{1440,390}.png及preview-styles.json。全部位于evidence/acceptance/layout-repair/。DOM实测标题在ID前、估算标签与优先级/负责人同排，flex-wrap为wrap。没有变更业务数据、动作族或服务端权限。原evidence/acceptance/ui仅复用未修改的角色授权、任务/文档/动作浮层、筛选及历史语义；不作为当前顶部排版证明，新布局证据覆盖该部分。历史归档门禁阻塞仍独立处理。

### 最终结论
返修与自动复验完成：30/30通过，失败/受阻/待采集均0；执行2组命令，同轮去重28项，证据ready。运行20261031192129096768-f204b061；归档临时副本预演通过，最终共享门禁仍因既有历史记录返回acceptance_source_invalid，未实际归档。opsx.modify与opsx.accept同步成功，REQ验收passed，卡片回到验收中。
修改及验收AI Usage hook均成功；目录校验仅提示既有legacy SQLite目录，不属本次调整。上下文预算、中文标题/语言、Sprint范围、OpenSpec严格校验及diff检查通过。

## 归档前当前结论
历史段落中的归档阻塞为当时结论；两份历史状态核实修正与完整规格输入补齐后，20261031193424806046-3530fd99验收30/30通过，最终共享归档准入ready。上述问题已闭环，历史记录保留。
