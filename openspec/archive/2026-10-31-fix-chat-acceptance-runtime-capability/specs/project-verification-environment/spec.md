---
title: Chat 项目验收运行能力增量规格
created_at: "2026-10-31 12:44:24"
updated_at: "2026-10-31 12:44:24"
---

# Chat 项目验收运行能力增量规格

## MODIFIED Requirements

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

## ADDED Requirements

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

