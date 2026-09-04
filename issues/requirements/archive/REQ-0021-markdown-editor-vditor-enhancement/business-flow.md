---
requirement_id: REQ-0021-markdown-editor-vditor-enhancement
created_at: 2026-08-19 11:36:10
updated_at: 2026-08-19 11:36:10
owner: product
source: requirement.md
---

# 业务流程

## 主流程

```text
用户进入需求中心
  -> 打开采集池对象卡片
  -> 点击 capture.md
  -> 右侧 Markdown 抽屉打开
  -> 判断对象阶段、文档名、权限
      -> 可编辑：初始化 Vditor 增强编辑器
      -> 不可编辑：展示只读 Markdown
  -> 用户编辑文本/表格/代码/公式/图片
  -> 系统维护未保存状态
  -> 用户点击保存
  -> 前端提交 Markdown 文本
  -> 服务端校验权限与内容边界
  -> 保存成功后回显最新 capture.md
```

## 图片上传流程

```text
用户在 Vditor 中选择图片
  -> 前端进入 uploading
  -> 校验文件大小、类型、权限和鉴权
  -> 调用项目认可的上传接口
      -> 成功：返回可访问 URL，写入 Markdown 图片语法，同会话回显
      -> 失败：进入 failed，展示原因，保留当前编辑内容，允许重试
```

## 异常与降级流程

```text
Vditor 初始化失败 / 资源加载失败 / 浏览器能力不足
  -> 抽屉展示降级提示
  -> 切换到原始 Markdown 文本编辑
  -> 保持权限校验、保存、脏状态确认和安全边界
```

## 与父 REQ 差异

REQ-0020 解决“Markdown 抽屉可打开、`capture.md` 可编辑保存、未保存关闭确认”等基础闭环。本需求不改变文档入口和状态流转，而是在同一抽屉中增强 `capture.md` 的编辑能力，重点新增 Vditor 编辑器、图片上传、表格工具、代码高亮、数学公式、主题适配和安全降级。
