## MODIFIED Requirements

### Requirement: 卡片文档查看与详情跳转

系统 MUST 支持从需求中心卡片安全查看关联 Markdown/HTML 文档，并支持卡片标题和归档入口新 Tab 打开对象详情。

#### Scenario: Markdown 文档从右侧抽屉打开

- **WHEN** 卡片关联文档包含 `.md` 文件
- **THEN** 文件名必须展示为可点击入口
- **AND** 点击后必须从右侧打开 Markdown 文档抽屉
- **AND** 抽屉必须展示当前对象 ID、文件名和文档内容
- **AND** 抽屉打开后必须显示背景蒙层
- **AND** 桌面端抽屉必须支持 420px-760px 范围内拖拽调整宽度，移动端必须使用全屏宽度
- **AND** 文件点击不得冒泡触发卡片详情或阶段动作

#### Scenario: 采集池 capture.md 受控编辑保存

- **GIVEN** 用户打开采集池阶段对象的 `capture.md`
- **WHEN** 文档抽屉完成加载
- **THEN** 系统必须默认展示 `capture.md` 预览内容和“编辑”按钮，不得直接进入编辑器
- **WHEN** 用户点击“编辑”后修改内容并保存
- **THEN** 系统必须通过受控 API 保存 `capture.md`
- **AND** 保存成功后必须展示成功反馈，回到预览态，并用服务端返回内容更新抽屉预览
- **AND** 再次打开该文档必须回显最新内容
- **AND** 用户关闭存在未保存修改的抽屉前必须出现确认提示
- **AND** `trace.md`、非采集池阶段 Markdown 或非 `capture.md` 文件必须保持只读且保存请求必须被阻断

#### Scenario: HTML 文档从新 Tab 打开

- **WHEN** 卡片关联文档包含 `.html` 文件
- **THEN** 文件名必须展示为可点击入口
- **AND** 点击后必须在新 Tab 打开受控 HTML 预览或详情页面
- **AND** HTML 预览请求必须使用当前登录态和项目作用域发起受控认证请求
- **AND** 前端不得直接使用裸 `/api/v1/requirement-center/.../preview` API URL 调用 `window.open`
- **AND** 成功读取 HTML 后必须以 `text/html` Blob URL 打开新 Tab，并在合理时间内释放对象 URL
- **AND** 认证失败、权限失败、文档不存在、缺少 URL、网络失败或浏览器拦截弹窗时，系统必须在原页面给出可理解的脱敏失败反馈，不得误报打开成功
- **AND** 系统不得向浏览器暴露 Bearer、Cookie、本机绝对路径或内部文件系统结构

#### Scenario: 卡片标题和查看归档打开详情

- **WHEN** 用户点击任意卡片标题
- **THEN** 系统必须在新 Tab 打开当前对象的详情或编辑页面
- **WHEN** 用户点击已归档对象的“查看归档”
- **THEN** 系统必须在新 Tab 打开归档后的对象详情页面
- **AND** 新 Tab URL 必须指向前端受控路由或可安全访问的详情入口
