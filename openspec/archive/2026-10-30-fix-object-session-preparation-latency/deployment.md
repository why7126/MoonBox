---
title: BUG-0057 本地服务部署与实际导航核对
created_at: '2026-10-30 19:18:00'
updated_at: '2026-10-30 23:40:00'
---

# 本地服务部署与实际导航核对

## 当前结果（快速打开返修）

当前本地运行“快速打开，发送时最终检查”版本。真实10次导航观察上界中位数868.5ms、最大1311ms；发送前检查仍需约5.45–8.81s（3个受控副本样本），二者分别报告。8/8增量验收通过，归档预演与共享准入ready；未执行正式归档或发布。

后端以更新前运行文件为基础加入准备分流和发送最终检查；前端使用本次7个相关模块覆盖的隔离构建，保留原镜像/应用文件/静态产物。构建与部署沿用标准受控流程，无DB迁移、端口、真实env或凭据修改。后端、worker、控制器、签名器healthy，Web实际HTTP200且静态manifest一致。执行器沿用原候选镜像，不覆盖运行版本选择；没有成功发送模型轮次。

回滚：`bash logs/bug0057-fast-open/deploy.sh rollback`，仍执行活动轮次预检及标准受控编排，不恢复数据库。采样临时数据库与冻结树已清理，无新增临时Docker容器/网络。证据：[当前摘要](evidence/fast-open/health.json)、[导航](evidence/fast-open/navigation-result.json)、[分阶段诊断](evidence/fast-open/diagnostic.json)、[验收](evidence/acceptance/20261030233606383318-49df5430/summary.md)。

## 19:18 部署历史（已被上述版本替代）

用户明确授权构建并更新当前本地服务。修复已在当前服务生效并保持运行，没有还原旧版；这与此前临时诊断恢复原件的历史记录不同。API健康200，worker、治理控制器和签名服务healthy；Web实际登录与目标Chat导航正常，静态资源摘要匹配新构建。没有正式版本发布、归档或数据库迁移。

部署后的自然导航未满足原绝对性能目标，不能继续沿用此前ready结论。10次有效样本：服务端中位数5231ms、最大8369ms；点击至路由观察上界中位数5360.5ms、最大8528ms。所有12次准备均HTTP200，原有2个会话/4条历史轮次保持，没有发送模型任务。前两次等待工具未取得有效导航时刻，审计分别4171ms、3288ms，全部保留；另一次看板未就绪发生在点击前，不算请求失败。

证据：[运行摘要](evidence/deployment/result.json)、[浏览器样本](evidence/deployment/browser.json)、[审计](evidence/deployment/audit.json)、[页面](evidence/deployment/chat-deployed.png)。请求关联按唯一有序请求和点击时间窗完成，未宣称捕获浏览器响应头ID；计时为观察上界。对象为既有隔离BUG-0036-bug，动作bug-complete；不冒充历史BUG-0057 bug-opsx。旧固定基线及通过样本保持原样。

## 构建与部署范围

使用标准scripts/docker-up.sh self-storage-sqlite --chat-platform --controlled-replacement进行预检、构建与完整编排。局部Shell适配仅追加本次构建上下文覆盖，以及将executor构建指向同样六文件覆盖的上下文，不绕过启动与健康门禁。未改真实env、端口、凭据、业务数据或权限配置。

后端以当前运行镜像和应用文件为基底，仅覆盖已验收的六个governance模块；worker使用其原有运行基底，controller/signer使用同一API镜像，executor同样加入六文件修复。前端由HEAD加唯一RequirementCenterPage覆盖重新类型检查与构建。其他工作区未交付代码不进入镜像。API、worker、controller和signer运行文件摘要均与已验收候选一致，Web全产物清单一致。

启动前无queued/connecting/running/stopping/recovering任务；已有1条历史unknown保持。首次启动自动快照曾记录copy_deferred，未把延后说成备份成功；随后worker正常完成启动预检并healthy。维护中第一次登录失败，健康恢复后登录成功。没有新增任务自建临时容器/网络；入口临时资源扫描38项clean，产品自身执行器启动预检沿既有生命周期处理。

## 剩余未知与门禁

当前治理树6880文件/20354729字节，原固定样本6851文件/20308926字节；CPU亲和10、cpu.max无限额、暖2/冷4读取线程，与原预算一致。一次只读完整扫描1620.7ms是独立观测，不是同请求分段归因。观察到后台资源占用，但没有足够证据将波动归因为CPU、数据库、后台轮询或扫描缓存。限定机制confirmed保持，历史21.27秒精确归因仍未知；当前运行态性能差异需要继续同请求补证或返修。

AC-02追加当前部署观察与数值校验；其他正确性证据按精确指纹复用。部署成功不等于性能验收通过，未自动扩大到代码返修或归档。

## 回滚

旧镜像保留bug0057-rollback-20261030标签，原运行应用和Web文件、范围构建上下文保存在Git忽略的logs/bug0057-deploy。回滚入口：`bash logs/bug0057-deploy/deploy.sh rollback`。脚本先核对无活动执行，再用原应用/静态资源重建并通过同一标准启动流程恢复；数据库和卷保持原样，不恢复旧数据库、不清空unknown。配置预检通过，未实际回滚。镜像身份见[回滚记录](evidence/deployment/rollback.json)。

回滚材料是当前本地服务的保留交付，不按临时测试目录自动删除；后续再次更新前重新核对基底与运行任务。

## 观测边界

product_data_collection_observability: applicable；affected_layers: 本地API/Web/worker部署核验和现有request_logs。validation: 当前代码与产物摘要、健康、12请求审计、10导航有效样本、会话/轮次数、回滚预检。永久观测字段、数据库schema、API及生成客户端N/A：本轮仅部署已实现代码，未新增契约。临时诊断钩子不存在，无新增秘密或原始数据库证据。


## 收尾复核

[最新完整验收](evidence/acceptance/20261030191839740009-d63f6432/summary.md)：7项passed、AC-02失败，无阻塞或待采集；执行4组、去重3组、复用1项。Workflow Sync已将Issue验收同步为pending，Change保留applied；共享归档准入blocked。实际AI Usage已记录1条并刷新Sprint快照、warning 0；治理计时单独记录，不虚构token收益。
