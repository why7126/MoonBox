import { GovernanceError } from "./governanceApi";

export function governanceActionError(error: unknown): string {
    if (error instanceof GovernanceError && (error.status === 403 || error.code === 2601)) return "你没有执行此操作的权限";
    if (error instanceof GovernanceError && error.code === 2606 && error.kind !== "workspace_fact_source_stale") return "对象已更新，请刷新后重试";
    if (error instanceof GovernanceError && error.code === 2604) {
      return /缺少|缺失|空文件/.test(error.message) ? "缺少必备文档，请先补齐" : "当前阶段不支持此操作";
    }
    if (error instanceof GovernanceError && error.kind === "workspace_fact_source_stale") {
      const categories = (error.details?.categories?.length ? error.details.categories : error.details?.roots || []).join("、");
      const scopeText = categories ? `阻断范围：${categories}。` : "";
      if (error.details?.reason === "manifest_mismatch") {
        return `${scopeText}治理目录与源工作区内容不一致，请同步对应事实源后重试；无需提交 Git。`;
      }
      if (error.details?.reason === "local_governance_dirty") {
        return `${scopeText}本地治理事实源有未提交或未同步变更，执行器暂看不到这些文件。请先提交或同步对应事实源，再按标准部署脚本重启后重试。`;
      }
      if (error.details?.reason === "git_snapshot_unreadable") {
        return `${scopeText}Git 快照不可读，系统无法确认执行器 /work 是否为最新事实源。请先检查仓库 Git 状态和服务日志，恢复后再重试。`;
      }
      if (error.details?.reason === "standard_deployment_outdated" || !error.details?.reason) {
        return `${scopeText}运行服务未更新到最新治理门禁。请使用项目标准部署脚本重启 Web、backend、chat-worker 与 governance-controller 后重试。`;
      }
      return `${scopeText}执行器工作区与当前事实源可能不是同一快照。请确认事实源已提交/同步，并使用项目标准部署脚本重启后重试。`;
    }
    return "项目请求失败，请稍后重试";
}
