import { governanceRequest, type Application } from "../workbench/governanceApi";
import { useEffect, useRef, useState } from "react";
export type GovernanceCandidate = { recovery_operation_id?: string; id: string; object_id: string; action?: string; current?: boolean; state: string; turn_id?: string | null; prepared_turn_id?: string | null; files: {path: string; diff: string}[]; manifest_hash: string; revision: string | number; error_code?: string; application?: Application };
export const activeGovernanceCandidate = (items: GovernanceCandidate[]) =>
  items.find(item => item.current) || items[0];
const reviewReasons: Record<string, string> = {
  outcome_conflict: "评审文档 status 与 result 结论冲突",
  outcome: "评审结论缺失或无效",
  identity: "对象标识或路径不一致", scope: "成果超出授权文件范围",
  review: "评审记录或前置状态不满足要求", migration_set: "目录迁移文件不完整",
  destination_exists: "评审目标目录已存在", document_size: "文档为空或超出大小限制",
  document_title: "文档标题校验未通过", acceptance_scope: "验收文档存在超出评审范围的修改",
  unrelated_document_edit: "子文档存在超出目录迁移范围的修改",
  state: "主文档、trace 与评审结论不一致", stage: "目录阶段与状态不一致",
  trace_scope: "trace 存在超出评审范围的修改", lifecycle_scope: "既有生命周期记录被改动",
  lifecycle: "缺少评审或批准时间", approval: "非通过结论修改了批准时间",
  primary_scope: "主文档元数据存在越界修改", root_cause: "缺陷根因尚未确认",
  registry: "注册表头部被改动", registry_ids: "注册表对象集合被改动",
  other_object: "其他对象被改动", registry_target: "注册表与评审目标不一致",
  registry_scope: "注册表目标条目存在越界修改", index: "索引与评审结果不一致",
  document_format: "评审文档格式不符合约定",
};
export function GovernanceResult({ candidate, previewOnly = false, onApplied, onNotice }: { candidate?: GovernanceCandidate; previewOnly?: boolean; onApplied?: () => void; onNotice?: (message: string) => void }) {
  const [operation, setOperation] = useState<Application | null>(null);
  const [error, setError] = useState("");
  const autoRequested = useRef("");
  const noticed = useRef("");
  const candidateId = candidate?.id;
  useEffect(() => { setOperation(candidate?.application || null); setError(""); autoRequested.current = ""; noticed.current = ""; }, [candidateId, candidate?.application?.id]);
  useEffect(() => {
    if (!candidateId || previewOnly) return;
    const stored = candidate?.application?.id || sessionStorage.getItem(`moonbox.governance.operation:${candidateId}`);
    if (!stored) return;
    const controller = new AbortController(); let timer: ReturnType<typeof setTimeout>;
    const poll = async () => {
      try {
        const row = await governanceRequest<Application>(`/api/v1/chat/governance-applications/${encodeURIComponent(stored)}`, { signal: controller.signal });
        if (controller.signal.aborted) return;
        setOperation(row);
        if (["pending", "applying", "recovering"].includes(row.state)) timer = setTimeout(poll, 1000);
      } catch (e) { if (!controller.signal.aborted) { setError(e instanceof Error ? e.message : "应用状态读取失败"); timer = setTimeout(poll, 3000); } }
    };
    void poll(); return () => { controller.abort(); clearTimeout(timer); };
  }, [candidateId, candidate?.application?.id, previewOnly]);
  const state = operation?.state || candidate?.state || "";
  useEffect(() => {
    if (!candidate || previewOnly || operation || error || autoRequested.current === candidate.id) return;
    if (candidate.state !== "pending" || !candidate.files.length || !candidate.manifest_hash) return;
    autoRequested.current = candidate.id;
    onNotice?.("治理结果已交由后端自动应用，需求中心将随事实源刷新。");
  }, [candidateId, candidate?.state, previewOnly, operation, error, onNotice]);
  useEffect(() => {
    if (!candidate || previewOnly) return;
    const message = error
      || (["pending", "applying", "recovering"].includes(state) && operation ? "模型执行已结束，治理成果正在自动应用，尚未确认事实源同步完成。" : "")
      || (state === "applied" ? "治理成果已写入事实源，文档和状态已同步。" : "")
      || (state === "unchanged" ? "已核验，事实源一致，无需更新。" : "")
      || (state === "conflict" ? "治理结果未应用：源文件已变化，请查看轨迹后重新准备。" : "")
      || (state === "recovery_blocked" && operation?.error_code === "workflow_sync_failed" ? "文件已写入，状态同步失败，待恢复" : "")
      || (state === "recovery_blocked" ? "治理结果恢复已暂停，请查看轨迹并联系管理员核对恢复记录。" : "")
      || (state === "failed" ? "治理结果应用失败，请查看轨迹后重试。" : "")
      || (state === "rejected" && candidate.error_code === "executor_unavailable" ? "生成未开始：执行器 sandbox/dry-run 预检失败，请稍后重试。" : "")
      || (state === "rejected" && reviewReasons[(candidate.error_code || "").replace(/^review_/, "")] ? `评审成果未应用：${reviewReasons[(candidate.error_code || "").replace(/^review_/, "")]}。原成果已保留。` : "")
      || (state === "rejected" && candidate.error_code === "governance_validation_failed" ? "治理结果未通过校验，未写入事实源。" : "")
      || (state === "rejected" ? "治理结果未通过校验，请查看轨迹。" : "");
    if (!message || noticed.current === `${candidate.id}:${message}`) return;
    noticed.current = `${candidate.id}:${message}`;
    onNotice?.(message);
  }, [candidateId, candidate?.error_code, state, operation?.state, error, previewOnly, onNotice]);
  useEffect(() => {
    if (operation?.state === "applied") onApplied?.();
  }, [operation?.state, onApplied]);
  return null;
}
