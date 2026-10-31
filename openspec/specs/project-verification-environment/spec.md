# project-verification-environment Specification

## Purpose
TBD - created by archiving change add-shared-project-verification-environment. Update Purpose after archive.
## Requirements
### Requirement: 项目验证声明与环境预检

MoonBox SHALL 为授权空间的 Web 项目识别 Node 锁文件、运行版本、Firefox/Chromium 浏览器与目标系统架构，分别报告基础工具、项目依赖和浏览器就绪情况。

#### Scenario: 环境完整可运行
- **WHEN** 授权项目的声明、锁文件、依赖制品、浏览器和系统库均通过探针
- **THEN** 平台 SHALL 返回 ready 和可追溯的环境身份
- **AND** 不把合成 DOM 检查充作浏览器就绪证据

#### Scenario: 缺失依赖或浏览器
- **WHEN** 依赖制品、浏览器文件或系统库缺失
- **THEN** 平台 SHALL 返回 preparable 或 unavailable 及稳定原因码
- **AND** 未就绪时不得声称验证任务通过

#### Scenario: Chat验收能力预检
- **WHEN** 授权Chat操作需要Python、组件或浏览器验收
- **THEN** 平台 SHALL 在执行前分别探测测试依赖、worker部署、项目子目录、目标与环境身份，返回稳定缺失原因
- **AND** 基础CLI通过不得替代验收能力就绪，缺失项只阻塞依赖它的任务

### Requirement: 版本化制品准备与跨架构隔离

MoonBox SHALL 依据锁文件、运行时、包管理器、Playwright、OS/架构和镜像摘要准备并校验不可变验证制品；仅可跨项目共享无凭证的只读制品。

#### Scenario: 相同环境复用制品
- **WHEN** 两个授权项目具有相同环境身份且制品摘要校验通过
- **THEN** 平台 SHALL 复用只读制品并为每个项目建立独立可写任务目录

#### Scenario: 环境版本或架构改变
- **WHEN** 锁文件、Node、Playwright、OS 或架构任一身份字段变化
- **THEN** 平台 SHALL 产生不同环境身份，不复用旧 `node_modules` 或不匹配浏览器

### Requirement: 授权的隔离浏览器验证任务

MoonBox SHALL 只为有权限的空间和项目创建、查询或取消验证任务，使用隔离工作副本与受限运行容器，不允许请求扩大命令、宿主路径、网络或 Docker 权限。

#### Scenario: 同仓库跨空间验证
- **WHEN** 两个空间分别绑定同一仓库并运行验证
- **THEN** 平台 SHALL 分离工作副本、凭证、运行状态和证据读取权限
- **AND** 可共享的仅是已校验不可变只读制品

#### Scenario: 无权或恶意请求
- **WHEN** 请求者无权访问目标空间/项目或提交宿主路径、任意命令、未授权网络目标
- **THEN** 平台 SHALL 在启动容器前拒绝请求并保留脱敏错误类别

### Requirement: 真实浏览器证据与验收语义

MoonBox SHALL 区分环境失败、测试失败和测试通过，只有真实浏览器执行产生完整证据时才能声明浏览器验收通过。

#### Scenario: 真实浏览器通过
- **WHEN** Firefox 或 Chromium 在规定视口完成交互与断言
- **THEN** 结果 SHALL 关联环境身份、浏览器版本、视口、截图和 computed style 摘要
- **AND** 结果读取 SHALL 再次校验空间与项目授权

#### Scenario: 环境缺失或合成测试通过
- **WHEN** 浏览器无法启动或仅有合成 DOM 测试通过
- **THEN** 真实浏览器验收 SHALL 保持未通过，结果 SHALL 明确证据类别和缺口

### Requirement: 验证任务生命周期与脱敏观测

MoonBox SHALL 为任务提供可查询的状态、超时、取消、幂等和制品清理语义，并在请求日志与 Task Trace 中只保留脱敏元数据。

#### Scenario: 超时与失败恢复
- **WHEN** 任务超时、平台重启或制品准备失败
- **THEN** 平台 SHALL 保留可复核终态或恢复状态，不丢失活跃制品引用、不自动报通过

#### Scenario: 跨空间观测边界
- **WHEN** 任务记录请求、链路和结果摘要
- **THEN** 记录 SHALL 包含不透明身份、版本、状态、耗时、计数和稳定错误码
- **AND** 不包含凭证、完整路径、页面正文或完整工具输出

### Requirement: Python与前端测试运行能力

平台 SHALL 使用锁定测试依赖与目标平台一致的运行环境。

#### Scenario: 目标环境测试
- **WHEN** 授权项目执行测试
- **THEN** 平台 SHALL 实际通过pytest/httpx导入、AnyIO最小线程探针和组件测试；环境身份变化不得复用旧制品

### Requirement: Chat受控验证与证据回传

平台 SHALL 从可信授权上下文将验证任务绑定空间、项目、操作、轮次及输入指纹。

#### Scenario: 同操作完成验证
- **WHEN** Chat请求已声明验证种类
- **THEN** 平台 SHALL 受控提交并查询结果，返回可授权访问的证据；拒绝任意命令、宿主路径和未授权目标

### Requirement: 按输入指纹恢复局部验收

平台 SHALL 持久保存检查点并限制重复副作用。

#### Scenario: 能力恢复后续接
- **WHEN** 某项能力缺失后恢复且请求仍获授权
- **THEN** 平台 SHALL 核对输入指纹，仅执行受阻或已失效检查，保持原轮次终态；用户主动停止后不得自动启动模型

### Requirement: 产品验收闭环与故障边界

平台 SHALL 分别保留命令、真实浏览器与产品轮次证据，准确区分环境和业务失败。

#### Scenario: 正式目标独立样本
- **WHEN** 授权正式目标完成同一操作的Python、组件及视觉检查
- **THEN** 平台 SHALL 核对源码和环境指纹、真实浏览器1440px交互截图及样式，再据可信证据判定结果；超时或缺证不得报通过

