## 背景与动机

需求中心现有 Markdown 抽屉已支持 `capture.md` 预览、编辑和保存，但原始 textarea 对表格、图片、代码块和数学公式不友好，增加产品和非工程用户在采集阶段整理需求材料的成本。

本变更在不扩大文档编辑权限的前提下，为采集阶段 `capture.md` 引入 Vditor 增强编辑体验，使早期需求素材更结构化、更可读，并为后续 PRD、验收和 OpenSpec 转化提供更完整上下文。

## 变更内容

- 在前台需求中心 Markdown 抽屉中，仅对采集阶段、文档名为 `capture.md` 且可编辑的文档启用 Vditor。
- 支持图片上传入口、表格工具、代码高亮和数学公式输入/预览。
- 保持服务端持久化内容为 Markdown 字符串，不引入富文本私有格式。
- 继承现有 `capture.md` 保存、未保存关闭确认、保存回显和错误提示行为。
- 增加 Vditor 初始化失败时的原始 Markdown textarea 降级路径。
- 建立图片上传、Markdown/HTML 渲染、对象存储 URL、深浅主题、抽屉宽度和移动端布局的安全与验收边界。

## 能力影响

### 新增能力

- 无。

### 修改能力

- `web-catalog-requirement-center`: 增强需求中心 Markdown 抽屉中 `capture.md` 的采集阶段编辑能力。

## 影响范围

- 前端：`src/web/src/pages/catalog/RequirementCenterPage.tsx`、需求中心相关测试、全局样式和 Vditor 依赖。
- 后端/API：若复用或新增图片上传接口，影响需求中心文档保存接口、上传鉴权、对象存储访问路径和相关测试。
- 对象存储：图片上传应复用项目认可的 MinIO/S3 兼容对象存储策略，不得写入本机路径或私有临时地址。
- 安全：Markdown 渲染、HTML 白名单或禁用策略、危险链接、脚本注入和上传 URL 泄露需要验收。
- UI 验收：需要 1440px 截图、关键交互截图、computed style 和深浅主题验证。
