# 设计

识别当前 Sprint Issue 的完整标题，仅当行内同时存在该 Issue 完整或短编号时剥离标题用于状态检查。原行保留用于路径检查和诊断；不忽略整行，不以 done 覆盖后续待实现语句。

product_data_collection_observability: N/A
affected_layers: 治理文档扫描
原因：不修改产品日志、API、数据库、执行链路或数据采集。
validation: 标题误报正例及标题外待实现反例。
