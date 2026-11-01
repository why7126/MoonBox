---
title: 归档收尾恢复设计
---
# 归档收尾恢复设计

## 边界
仅唯一已归档且完整验收与恢复证明ready的Change可生成恢复记录。允许proposal.md的status: proposed投影为archived；仅已关闭、双向归属、全部关联Change归档的来源Issue顶层文档，将指向自身Change活动目录的旧路径映射为唯一归档中同一文件。其他正文冲突、失败状态、未知对象、外部路径、符号链接与歧义不豁免。

## 证明与写入
记录位于归档恢复目录finalization子目录，绑定原始恢复日志、交付指纹、通过清单、源文档和目标文档字节。预检只读，apply采用排他原子发布，重复运行只验证；输入或记录失配拒绝且不覆盖。共享inspect_document使用同一校验，不修改历史文件、正式规格或旧恢复记录。

## 验证
合成测试覆盖真实归档证明、初始状态、导航映射、幂等、篡改、失败验收、未归档/双重身份、无关Issue、未完成兄弟、路径逃逸及符号链接。真实REQ-0056记录前后完整文件哈希保持一致，运行wrapper恢复且不再次合并。

## 数据采集边界
product_data_collection_observability: N/A
affected_layers: governance
原因：仅本地证明记录与只读收尾校验，无新增请求、Task Trace、用户日志、DB或UI。
validation：共享校验与恢复安全回归，不扩展授权。

## 重放幂等性
验收块除accepted_at外完全相同时保留原块，不触发updated_at变更；真实结论或来源变化仍写入。事故时间仅通过原始完整哈希匹配恢复，不刷新或覆盖恢复记录。
