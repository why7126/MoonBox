import { useCallback, useEffect, useMemo, useRef, useState, type ChangeEvent } from "react";
import { ImagePlus, Loader2, Paperclip, Pencil, Split, Trash2, X } from "lucide-react";
import { GovernanceError, type Project } from "../../workbench/governanceApi";
import { captureApi, type Candidate, type CapabilitiesResult, type ConfirmationResult, type DraftContent, type DraftResult, type MaterialResult, type OrganizeResult } from "./captureApi";
import { CaptureWorkspace, type CaptureSaveState, type CaptureStep } from "./CaptureWorkspace";

type CaptureImage = { id: string; name: string; size: number; status: "uploading" | "ready" | "failed"; url?: string; error?: string };
type SourceFileBlock = { name: string; start: number; end: number };
export type CaptureExistingIssue = { id: string; title: string; type: "requirement" | "bug" | string; stage?: string; source?: string; documents?: string[] };
type SimilarIssue = CaptureExistingIssue & { score: number; reason: string };
type CandidateResolution = { mode: "create" } | { mode: "merge" | "supplement"; issue: CaptureExistingIssue };
type CaptureDialogState = "loading" | "input" | "organizing" | "review" | "confirming" | "result";
type CaptureModal =
  | { type: "none" }
  | { type: "edit"; candidate: Candidate }
  | { type: "split"; candidate: Candidate }
  | { type: "delete"; candidate: Candidate }
  | { type: "source"; candidate: Candidate }
  | { type: "confirm" }
  | { type: "delete-draft" };

const emptyContent: DraftContent = { text: "", media_ids: [], candidates: [] };
const priorityLevels = ["P0", "P1", "P2", "P3"] as const;
const severityLevels = ["blocker", "critical", "high", "medium", "low"] as const;

function codepoints(value: string) {
  return Array.from(value).length;
}

function message(error: unknown, fallback: string) {
  return error instanceof Error ? error.message : fallback;
}

function defaultGrade(type: Candidate["type"]) {
  return type === "bug" ? { severity: "medium" as const, priority: null } : { priority: "P1" as const, severity: null };
}

function normalizeCandidate(candidate: Candidate): Candidate {
  const grade = defaultGrade(candidate.type);
  return {
    ...candidate,
    title: candidate.title.trim(),
    description: candidate.description.trim(),
    priority: candidate.type === "requirement" ? (candidate.priority || grade.priority) : null,
    severity: candidate.type === "bug" ? (candidate.severity || grade.severity) : null,
    source_refs: candidate.source_refs?.length ? candidate.source_refs : ["text"],
  };
}

function sourceFileBlock(fileName: string, text: string) {
  const clipped = text.length > 12000 ? `${text.slice(0, 12000)}\n\n[文件内容已截断展示，请按需拆分输入]` : text;
  return `\n\n### 来源文件：${fileName}\n\n\`\`\`text\n${clipped.replace(/```/g, "`\u200b``")}\n\`\`\`\n`;
}

function sourceFileBlocks(text: string): SourceFileBlock[] {
  const blocks: SourceFileBlock[] = [];
  const pattern = /\n{0,2}### 来源文件：([^\n]+)\n\n```text\n[\s\S]*?\n```/g;
  for (const match of text.matchAll(pattern)) {
    blocks.push({ name: match[1].trim(), start: match.index || 0, end: (match.index || 0) + match[0].length });
  }
  return blocks;
}


function issueKind(issueId: string) {
  return issueId.startsWith("BUG-") ? "bug" : "requirement";
}

function issueDirectory(issueId: string) {
  const prefix = issueKind(issueId) === "bug" ? "BUG" : "REQ";
  return `/issues/${prefix}-${issueId.split("-")[1] || issueId}/`;
}

function sourceSummary(candidate?: Candidate) {
  if (!candidate) return "来源依据已写入 trace.md";
  const refs = candidate.source_refs?.length ? candidate.source_refs.join("、") : "原始材料";
  const reason = candidate.classification_reason?.trim();
  return reason ? `${refs} · ${reason}` : refs;
}

function terms(value: string) {
  return Array.from(new Set((value.toLowerCase().match(/[a-z0-9]+|[一-龥]{1,2}/g) || [])
    .filter(item => item.length > 1 && !["需求", "问题", "支持", "希望", "当前", "用户", "一个", "这个", "可以", "需要"].includes(item))));
}

function similarity(candidate: Candidate, issue: CaptureExistingIssue) {
  const candidateText = `${candidate.title} ${candidate.description} ${candidate.classification_reason || ""}`;
  const issueText = `${issue.id} ${issue.title} ${issue.stage || ""} ${issue.source || ""} ${(issue.documents || []).join(" ")}`;
  const candidateTerms = terms(candidateText);
  const issueTerms = new Set(terms(issueText));
  if (!candidateTerms.length || !issueTerms.size) return 0;
  const overlap = candidateTerms.filter(term => issueTerms.has(term)).length;
  const titleBoost = issue.title && (candidate.title.includes(issue.title) || issue.title.includes(candidate.title)) ? 0.35 : 0;
  const typeBoost = issue.type === candidate.type ? 0.12 : 0;
  return Math.min(1, overlap / Math.max(candidateTerms.length, 4) + titleBoost + typeBoost);
}

function similarIssues(candidate: Candidate, issues: CaptureExistingIssue[]): SimilarIssue[] {
  return issues
    .filter(issue => issue.type === "requirement" || issue.type === "bug")
    .map(issue => ({ ...issue, score: similarity(candidate, issue), reason: `${issue.stage || "未知阶段"} · ${issue.source || "trace"}` }))
    .filter(issue => issue.score >= 0.22)
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);
}

function resolutionLabel(resolution?: CandidateResolution) {
  if (!resolution || resolution.mode === "create") return "";
  return resolution.mode === "merge" ? `合并到 ${resolution.issue.id}` : `作为 ${resolution.issue.id} 的补充材料`;
}

export function CaptureDialog({ project, contextFailure, existingIssues = [], onClose, onCreated }: {
  project: Project | null;
  contextFailure: boolean;
  existingIssues?: CaptureExistingIssue[];
  onClose: () => void;
  onCreated: () => Promise<void>;
}) {
  const projectKey = `${project?.space_id || ""}:${project?.repository_id || ""}`;
  const request = useMemo(() => new AbortController(), [projectKey]);
  const api = useMemo(() => project ? captureApi(project, request.signal) : null, [projectKey, request.signal]);
  const [draft, setDraft] = useState<DraftResult | null>(null);
  const [content, setContent] = useState<DraftContent>(emptyContent);
  const [images, setImages] = useState<CaptureImage[]>([]);
  const [capabilities, setCapabilities] = useState<CapabilitiesResult | null>(null);
  const [state, setState] = useState<CaptureDialogState>("loading");
  const [saveState, setSaveState] = useState<CaptureSaveState>("saved");
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [inlineEdit, setInlineEdit] = useState<Candidate | null>(null);
  const [candidatePanel, setCandidatePanel] = useState<{ type: "split" | "delete"; candidateId: string | null } | null>(null);
  const [candidateResolutions, setCandidateResolutions] = useState<Record<string, CandidateResolution>>({});
  const [splitDraft, setSplitDraft] = useState({ typeA: "requirement" as Candidate["type"], titleA: "", descriptionA: "", typeB: "bug" as Candidate["type"], titleB: "", descriptionB: "" });
  const [modal, setModal] = useState<CaptureModal>({ type: "none" });
  const [task, setTask] = useState<ConfirmationResult | null>(null);
  const [organizeTask, setOrganizeTask] = useState<OrganizeResult | null>(null);
  const saveTimer = useRef<number | null>(null);
  const maxSaveTimer = useRef<number | null>(null);
  const saving = useRef(false);
  const pendingSave = useRef(false);
  const activeSave = useRef<Promise<DraftResult | null> | null>(null);
  const lastVersion = useRef(0);
  const latestContent = useRef(content);
  const latestDraft = useRef(draft);
  latestContent.current = content;
  latestDraft.current = draft;

  const canWrite = Boolean(project && !project.readonly && project.status === "connected" && !contextFailure);
  const candidates = content.candidates || [];
  const createCandidates = candidates.filter(candidate => !candidate.id || (candidateResolutions[candidate.id]?.mode || "create") === "create");
  const skippedCount = candidates.length - createCandidates.length;
  const hasMaterial = Boolean((content.text || "").trim() || (content.media_ids || []).length);
  const imageIds = images.filter(image => image.status === "ready").map(image => image.id);
  const busy = state === "loading" || state === "organizing" || state === "confirming";

  const clearSaveTimers = () => {
    if (saveTimer.current) window.clearTimeout(saveTimer.current);
    if (maxSaveTimer.current) window.clearTimeout(maxSaveTimer.current);
    saveTimer.current = null; maxSaveTimer.current = null;
  };

  const replaceContent = useCallback((next: DraftContent, nextDraft = latestDraft.current) => {
    const normalized = { text: next.text || "", media_ids: next.media_ids || [], candidates: next.candidates || [] };
    setContent(normalized);
    latestContent.current = normalized;
    if (nextDraft) setDraft({ ...nextDraft, content: normalized });
  }, []);

  const saveNow = useCallback(async (): Promise<DraftResult | null> => {
    const current = latestDraft.current;
    if (!api || !current || current.state !== "editing") return current;
    if (saving.current) {
      pendingSave.current = true;
      await activeSave.current;
      return saveNow();
    }
    saving.current = true;
    const run = (async () => {
      clearSaveTimers();
      setSaveState("saving");
      try {
        const saved = await api.save(current.id, lastVersion.current || current.revision, latestContent.current);
        lastVersion.current = saved.revision;
        latestDraft.current = saved;
        setDraft(saved);
        setSaveState("saved");
        return saved;
      } catch (err) {
        setSaveState(err instanceof GovernanceError && err.status === 409 ? "conflict" : "failed");
        setError(message(err, "草稿保存失败"));
        throw err;
      } finally {
        saving.current = false;
        activeSave.current = null;
      }
    })();
    activeSave.current = run;
    const saved = await run;
    if (pendingSave.current) {
      pendingSave.current = false;
      return saveNow();
    }
    return saved;
  }, [api]);

  const scheduleSave = useCallback(() => {
    if (!latestDraft.current || latestDraft.current.state !== "editing") return;
    setSaveState("saving");
    if (saveTimer.current) window.clearTimeout(saveTimer.current);
    saveTimer.current = window.setTimeout(() => { void saveNow(); }, 1000);
    if (!maxSaveTimer.current) maxSaveTimer.current = window.setTimeout(() => { void saveNow(); }, 5000);
  }, [saveNow]);

  const mutateContent = useCallback((updater: (current: DraftContent) => DraftContent) => {
    replaceContent(updater(latestContent.current));
    setError("");
    scheduleSave();
  }, [replaceContent, scheduleSave]);

  const loadImage = useCallback(async (id: string, name = "图片") => {
    if (!api) return;
    try {
      const blob = await api.image(id);
      if (request.signal.aborted) return;
      setImages(current => current.some(item => item.id === id)
        ? current.map(item => item.id === id ? { ...item, status: "ready", url: URL.createObjectURL(blob), error: "" } : item)
        : [...current, { id, name, size: blob.size, status: "ready", url: URL.createObjectURL(blob) }]);
    } catch {
      setImages(current => current.some(item => item.id === id) ? current : [...current, { id, name, size: 0, status: "failed", error: "图片暂不可读" }]);
    }
  }, [api, request.signal]);

  useEffect(() => {
    let mounted = true;
    const init = async () => {
      if (!api || !project) {
        setError("当前项目未连接");
        setState("input");
        return;
      }
      try {
        const [caps, list] = await Promise.all([api.capabilities(), api.list()]);
        if (!mounted || request.signal.aborted) return;
        setCapabilities(caps);
        const reusable = list.items.find(item => item.state === "editing") || null;
        const loaded = reusable ? await api.get(reusable.id) : await api.create();
        if (!mounted || request.signal.aborted) return;
        lastVersion.current = loaded.revision;
        latestDraft.current = loaded;
        setDraft(loaded);
        replaceContent(loaded.content || emptyContent, loaded);
        setState((loaded.content?.candidates || []).length ? "review" : "input");
        await Promise.all((loaded.content?.media_ids || []).map(id => loadImage(id)));
      } catch (err) {
        if (!mounted || request.signal.aborted) return;
        setError(message(err, "Capture 草稿初始化失败"));
        setState("input");
      }
    };
    void init();
    return () => {
      mounted = false;
      request.abort();
      clearSaveTimers();
      setImages(current => {
        current.forEach(image => { if (image.url) URL.revokeObjectURL(image.url); });
        return current;
      });
    };
  }, [api, loadImage, project?.space_id, project?.repository_id, replaceContent, request]);

  const handleFiles = async (event: ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    event.target.value = "";
    if (!api || !draft || !files.length) return;
    const imageFiles = files.filter(file => file.type.startsWith("image/"));
    const textFiles = files.filter(file => !file.type.startsWith("image/"));
    if (imageFiles.length + imageIds.length > (capabilities?.limits.max_images || 10)) {
      setError("图片数量超过限制，请先移除部分图片");
      return;
    }
    for (const file of textFiles) {
      const text = await file.text();
      mutateContent(current => ({ ...current, text: `${current.text || ""}${sourceFileBlock(file.name, text)}` }));
    }
    for (const file of imageFiles) {
      const localUrl = URL.createObjectURL(file);
      const tempId = `uploading-${crypto.randomUUID()}`;
      setImages(current => [...current, { id: tempId, name: file.name, size: file.size, status: "uploading", url: localUrl }]);
      try {
        const material: MaterialResult = await api.upload(draft.id, file);
        setImages(current => current.map(image => image.id === tempId ? { id: material.media_id, name: file.name, size: material.size, status: "ready", url: localUrl } : image));
        mutateContent(current => ({ ...current, media_ids: [...(current.media_ids || []), material.media_id] }));
      } catch (err) {
        setImages(current => current.map(image => image.id === tempId ? { ...image, status: "failed", error: message(err, "上传失败") } : image));
        setError(message(err, "图片上传失败"));
      }
    }
  };

  const removeImage = (id: string) => {
    setImages(current => current.filter(image => {
      if (image.id === id && image.url) URL.revokeObjectURL(image.url);
      return image.id !== id;
    }));
    mutateContent(current => ({ ...current, media_ids: (current.media_ids || []).filter(mediaId => mediaId !== id) }));
  };

  const removeSourceFile = (block: SourceFileBlock) => {
    mutateContent(current => ({ ...current, text: `${(current.text || "").slice(0, block.start)}${(current.text || "").slice(block.end)}` }));
  };

  const organize = async () => {
    if (!api || !draft || !hasMaterial || saveState === "failed" || saveState === "conflict") return;
    setState("organizing");
    setError("");
    try {
      if (skippedCount) {
        const nextContent = { ...latestContent.current, candidates: createCandidates };
        replaceContent(nextContent);
      }
      const saved = await saveNow();
      if (!saved) throw new Error("草稿不可保存");
      const started = await api.organize(saved.id, saved.revision);
      setOrganizeTask(started);
      let current = started;
      for (let i = 0; i < 120 && current.state !== "ready"; i++) {
        await new Promise(resolve => window.setTimeout(resolve, 1000));
        current = await api.organized(saved.id, started.id);
        setOrganizeTask(current);
        if (current.state === "failed") throw new Error(current.error_code || "AI 整理失败");
      }
      if (!current.result?.candidates?.length) throw new Error("AI 未返回可审阅候选");
      const updated = await api.save(saved.id, saved.revision, { ...latestContent.current, candidates: current.result.candidates.map(normalizeCandidate) });
      lastVersion.current = updated.revision;
      latestDraft.current = updated;
      setDraft(updated);
      replaceContent(updated.content || emptyContent, updated);
      setState("review");
    } catch (err) {
      setError(message(err, "AI 整理失败，草稿已保留"));
      setState("input");
    }
  };

  const updateCandidate = (id: string | null | undefined, next: Candidate) => {
    mutateContent(current => ({ ...current, candidates: (current.candidates || []).map(candidate => candidate.id === id ? normalizeCandidate(next) : candidate) }));
  };

  const deleteCandidate = (candidate: Candidate) => {
    mutateContent(current => ({ ...current, candidates: (current.candidates || []).filter(item => item.id !== candidate.id) }));
    setSelected(current => { const next = new Set(current); if (candidate.id) next.delete(candidate.id); return next; });
    setCandidateResolutions(current => { const next = { ...current }; if (candidate.id) delete next[candidate.id]; return next; });
    setCandidatePanel(null);
    setModal({ type: "none" });
  };

  const openSplitPanel = (candidate: Candidate) => {
    setInlineEdit(null);
    setCandidatePanel({ type: "split", candidateId: candidate.id || null });
    setSplitDraft({ typeA: candidate.type, titleA: candidate.title, descriptionA: candidate.description, typeB: candidate.type === "bug" ? "requirement" : "bug", titleB: "", descriptionB: "" });
  };

  const splitCandidate = (candidate: Candidate, titleA: string, titleB: string, descriptionA = candidate.description, descriptionB = candidate.description, typeA: Candidate["type"] = candidate.type, typeB: Candidate["type"] = candidate.type) => {
    const first = normalizeCandidate({ ...candidate, type: typeA, ...defaultGrade(typeA), id: crypto.randomUUID(), title: titleA, description: descriptionA, parents: [candidate.id || ""].filter(Boolean) });
    const second = normalizeCandidate({ ...candidate, type: typeB, ...defaultGrade(typeB), id: crypto.randomUUID(), title: titleB, description: descriptionB, parents: [candidate.id || ""].filter(Boolean) });
    mutateContent(current => ({ ...current, candidates: (current.candidates || []).flatMap(item => item.id === candidate.id ? [first, second] : [item]) }));
    setSelected(new Set());
    setCandidateResolutions(current => { const next = { ...current }; if (candidate.id) delete next[candidate.id]; return next; });
    setCandidatePanel(null);
    setModal({ type: "none" });
  };

  const mergeSelected = () => {
    const rows = candidates.filter(candidate => candidate.id && selected.has(candidate.id));
    if (rows.length < 2) return;
    const merged = normalizeCandidate({
      ...rows[0],
      id: crypto.randomUUID(),
      title: rows[0].title,
      description: rows.map(row => row.description).join("\n\n"),
      source_refs: Array.from(new Set(rows.flatMap(row => row.source_refs || []))),
      parents: rows.map(row => row.id || "").filter(Boolean),
      classification_reason: "由用户合并，请核对最终类型与分级。",
    });
    mutateContent(current => ({ ...current, candidates: [...(current.candidates || []).filter(candidate => !candidate.id || !selected.has(candidate.id)), merged] }));
    setCandidateResolutions(current => { const next = { ...current }; selected.forEach(id => delete next[id]); return next; });
    setSelected(new Set());
  };

  const setResolution = (candidate: Candidate, resolution: CandidateResolution) => {
    if (!candidate.id) return;
    setCandidateResolutions(current => ({ ...current, [candidate.id as string]: resolution }));
    setSelected(current => { const next = new Set(current); next.delete(candidate.id as string); return next; });
  };

  const confirm = async () => {
    if (!api || !draft || !createCandidates.length || saveState === "failed" || saveState === "conflict") return;
    setModal({ type: "none" });
    setState("confirming");
    setError("");
    try {
      if (skippedCount) {
        const nextContent = { ...latestContent.current, candidates: createCandidates };
        replaceContent(nextContent);
      }
      const saved = await saveNow();
      if (!saved) throw new Error("草稿不可保存");
      let result = await api.confirm(saved.id, saved.revision, `capture-${saved.id}-${saved.revision}`);
      setTask(result);
      for (let i = 0; i < 60 && !["completed", "failed", "conflict", "recovery_blocked"].includes(result.state); i++) {
        await new Promise(resolve => window.setTimeout(resolve, 1000));
        result = await api.status(result.id);
        setTask(result);
      }
      if (result.state !== "completed") throw new Error(result.state === "recovery_blocked" ? "创建恢复被阻止，请重试原任务或联系管理员" : "创建尚未完成");
      setState("result");
      await onCreated();
    } catch (err) {
      setError(message(err, "确认创建失败，已保留原任务"));
      setState("result");
    }
  };

  const retry = async () => {
    if (!api || !task) return;
    setState("confirming");
    setError("");
    try {
      let result = await api.retry(task.id);
      setTask(result);
      for (let i = 0; i < 60 && !["completed", "failed", "conflict", "recovery_blocked"].includes(result.state); i++) {
        await new Promise(resolve => window.setTimeout(resolve, 1000));
        result = await api.status(result.id);
        setTask(result);
      }
      setState("result");
      if (result.state === "completed") await onCreated();
    } catch (err) {
      setError(message(err, "重试失败"));
      setState("result");
    }
  };

  const deleteDraft = async () => {
    if (!api || !draft) return;
    try {
      await api.remove(draft.id, lastVersion.current || draft.revision);
      setModal({ type: "none" });
      onClose();
    } catch (err) {
      setError(message(err, "删除草稿失败"));
    }
  };

  const step: CaptureStep = state === "result" || state === "confirming" ? "result" : state === "review" ? "review" : "input";
  const reqCount = createCandidates.filter(candidate => candidate.type === "requirement").length;
  const bugCount = createCandidates.filter(candidate => candidate.type === "bug").length;
  const sourceFiles = sourceFileBlocks(content.text || "");
  const materialCount = sourceFiles.length + images.length;
  const saveLabels: Record<CaptureSaveState, string> = {
    saving: "正在保存…", saved: "草稿已保存", failed: "保存失败，请重试", conflict: "草稿已更新，请核对后保存",
  };
  const commitInlineEdit = () => {
    if (!inlineEdit?.id) return;
    updateCandidate(inlineEdit.id, inlineEdit);
    setInlineEdit(null);
  };
  const sourceEvidence = (candidate: Candidate) => candidate.classification_reason || candidate.source_refs?.join("、") || "来源依据来自原始材料与模型整理结果。";
  const materialNodes = <details className="capture-material-drawer" data-testid="capture-materials-summary" open>
    <summary><span>来源材料 · {materialCount} 项</span></summary>
    <div className="capture-chiprow" aria-label="来源材料列表">
      {sourceFiles.map(file => <div className="capture-source capture-material-card capture-material-chip text" key={`${file.start}-${file.name}`} data-testid="capture-text-file-card">
        <Paperclip size={18} aria-hidden="true" />
        <div><strong>{file.name}</strong></div>
        <button type="button" aria-label={`移除文本文件 ${file.name}`} onClick={() => removeSourceFile(file)} disabled={busy}><X size={14} /></button>
      </div>)}
      {images.map((image, index) => <div className={`capture-material-card capture-material-chip ${image.status}`} key={image.id} data-testid="capture-image-card">
        {image.url ? <img src={image.url} alt={image.name} /> : <Paperclip size={18} aria-hidden="true" />}
        <div><strong>图片 {index + 1}</strong></div>
        <button type="button" aria-label={`移除图片 ${index + 1}`} onClick={() => removeImage(image.id)} disabled={busy}><X size={14} /></button>
      </div>)}
      <label className="capture-material-add" htmlFor="capture-file-input">
        <input id="capture-file-input" data-testid="capture-file-input" type="file" multiple accept="image/png,image/jpeg,image/webp,text/plain,text/markdown,.txt,.md" onChange={handleFiles} disabled={!canWrite || busy} />
        <ImagePlus size={18} aria-hidden="true" />
        <span>+ 添加图片或文本文件</span>
      </label>
    </div>
  </details>;

  const inputView = <>
    <div className="capture-editor-panel" data-testid="capture-md-editor">
      {materialNodes}
      <textarea id="capture-raw-editor" aria-label="原始材料" value={content.text || ""} maxLength={capabilities?.limits.max_text_codepoints || 20000}
        placeholder="写下需求、问题或补充背景；也可以粘贴长文本，或用上方材料块加入图片、.txt、.md 文件。

示例：
1. xxx问题
2. xxx需求"
        onChange={event => mutateContent(current => ({ ...current, text: event.target.value }))} disabled={!canWrite || busy} />
      <div className="capture-rowfoot">
        <span className={`capture-save capture-save-${saveState}`} data-testid="capture-save-state" role="status">{saveLabels[saveState]}</span>
        <button type="button" className="capture-input-delete" onClick={() => setModal({ type: "delete-draft" })} disabled={!draft || busy}>删除草稿</button>
      </div>
      {error && <p className="capture-alert" role="alert">{error}</p>}
      {!canWrite && <p className="capture-alert" role="status">当前项目未连接或没有写入权限。</p>}
    </div>
    <button type="button" className="capture-primary capture-input-submit" aria-label="AI 整理候选" onClick={organize} disabled={!canWrite || !hasMaterial || busy || saveState === "failed" || saveState === "conflict"}>AI 整理候选 →</button>
  </>;

  const reviewView = <div data-testid="capture-review-list">
    <div className="capture-reviewhead">
      <p className="capture-muted">{candidates.length} 条候选 · {reqCount} 条待创建需求 / {bugCount} 条待创建缺陷{skippedCount ? ` · ${skippedCount} 条已标记为已有项` : ""}</p>
      <button type="button" onClick={mergeSelected} disabled={selected.size < 2}>合并所选（{selected.size}）</button>
    </div>
    <div className="capture-board">
      {candidates.length ? candidates.map((candidate, index) => {
        const editing = inlineEdit?.id && inlineEdit.id === candidate.id;
        const draftCandidate = editing ? inlineEdit : candidate;
        const matches = similarIssues(candidate, existingIssues);
        const resolution = candidate.id ? candidateResolutions[candidate.id] : undefined;
        const resolutionText = resolutionLabel(resolution);
        const showSimilar = Boolean(candidate.id && matches.length);
        return <article className="capture-candidate" key={candidate.id || index} data-testid="capture-candidate" data-candidate-id={candidate.id || ""}>
          <div className="capture-candidate-number" aria-hidden="true">{index + 1}</div>
          <div className="capture-candidate-main">
            <div className="capture-candidate-top">
              <label className="capture-candidate-title"><input type="checkbox" aria-label={`选择条目 ${index + 1}`} checked={Boolean(candidate.id && selected.has(candidate.id))} onChange={event => setSelected(current => {
                const next = new Set(current); if (candidate.id) event.target.checked ? next.add(candidate.id) : next.delete(candidate.id); return next;
              })} /><span>{candidate.title}</span></label>
              <span className="capture-candidate-tags">
                <span className={`capture-badge ${candidate.type}`}>{candidate.type === "bug" ? "BUG" : "需求"}</span>
                <span className={`capture-badge grade ${candidate.type}`}>{candidate.type === "bug" ? candidate.severity : candidate.priority}</span>
              </span>
            </div>
            <p>{candidate.description}</p>
            {!!candidate.clarifications?.length && <ul className="capture-clarifications">{candidate.clarifications.map(item => <li key={item}>{item}</li>)}</ul>}
            <div className="capture-source-evidence"><span>来源依据</span><p>{sourceEvidence(candidate)}</p></div>
            {showSimilar && candidate.id && <div className="capture-similar" data-testid="capture-similar-panel">
              <div className="capture-similar-head"><strong>可能相关</strong>{resolutionText && <span>{resolutionText}</span>}</div>
              {matches.map(issue => <div className="capture-similar-row" key={issue.id}>
                <div className="capture-similar-meta"><strong>{issue.id}</strong><span>{issue.title}</span><small>{issue.reason}</small></div>
                <span className="capture-similar-actions">
                  <button type="button" onClick={() => setResolution(candidate, { mode: "merge", issue })}>合并</button>
                  <button type="button" onClick={() => setResolution(candidate, { mode: "supplement", issue })}>补充材料</button>
                </span>
              </div>)}
              {resolution && resolution.mode !== "create" && <button type="button" className="capture-similar-reset" onClick={() => setResolution(candidate, { mode: "create" })}>恢复创建</button>}
            </div>}
            <div className="capture-card-actions">
              <span>
                <button type="button" onClick={() => { setCandidatePanel(null); setInlineEdit(normalizeCandidate(candidate)); }}><Pencil size={14} aria-hidden="true" /> 编辑</button>
                <button type="button" onClick={() => openSplitPanel(candidate)}><Split size={14} aria-hidden="true" /> 拆分</button>
                <button type="button" className="capture-danger-action" onClick={() => { setInlineEdit(null); setCandidatePanel({ type: "delete", candidateId: candidate.id || null }); }}><Trash2 size={14} aria-hidden="true" /> 删除</button>
              </span>
            </div>
            {editing && draftCandidate && <div className="capture-fieldpanel" data-testid="capture-inline-edit">
              <div className="capture-edit-grid">
                <label>类型<select value={draftCandidate.type} onChange={event => setInlineEdit(normalizeCandidate({ ...draftCandidate, type: event.target.value as Candidate["type"] }))}>
                  <option value="requirement">需求</option><option value="bug">缺陷</option>
                </select></label>
                <label>{draftCandidate.type === "bug" ? "缺陷严重度" : "需求优先级"}<select value={(draftCandidate.type === "bug" ? draftCandidate.severity : draftCandidate.priority) || ""} onChange={event => setInlineEdit(normalizeCandidate({ ...draftCandidate, ...(draftCandidate.type === "bug" ? { severity: event.target.value as Candidate["severity"] } : { priority: event.target.value as Candidate["priority"] }) }))}>
                  {(draftCandidate.type === "bug" ? severityLevels : priorityLevels).map(level => <option key={level} value={level}>{level}</option>)}
                </select></label>
              </div>
              <label>标题<input value={draftCandidate.title} maxLength={60} onChange={event => setInlineEdit({ ...draftCandidate, title: event.target.value })} /></label>
              <label>描述<textarea value={draftCandidate.description} maxLength={10000} onChange={event => setInlineEdit({ ...draftCandidate, description: event.target.value })} /></label>
              <div className="capture-idnote">内部候选 ID 保持不变；改类型不会丢失来源和图片关联。</div>
              <div className="capture-field-actions"><button type="button" onClick={() => setInlineEdit(null)}>取消</button><button className="capture-primary" type="button" onClick={commitInlineEdit} disabled={!draftCandidate.title.trim() || !draftCandidate.description.trim()}>保存调整</button></div>
            </div>}
            {candidatePanel?.type === "split" && candidatePanel.candidateId === candidate.id && <div className="capture-fieldpanel capture-split-panel" data-testid="capture-split-panel">
              <div className="capture-split-grid">
                <section className="capture-split-item" aria-label="拆分条目 A">
                  <strong>条目 A</strong>
                  <label>类目<select value={splitDraft.typeA} onChange={event => setSplitDraft(current => ({ ...current, typeA: event.target.value as Candidate["type"] }))}>
                    <option value="requirement">需求</option><option value="bug">BUG</option>
                  </select></label>
                  <label>标题<input value={splitDraft.titleA} maxLength={60} onChange={event => setSplitDraft(current => ({ ...current, titleA: event.target.value }))} /></label>
                  <label>描述<textarea value={splitDraft.descriptionA} maxLength={10000} onChange={event => setSplitDraft(current => ({ ...current, descriptionA: event.target.value }))} /></label>
                </section>
                <section className="capture-split-item" aria-label="拆分条目 B">
                  <strong>条目 B</strong>
                  <label>类目<select value={splitDraft.typeB} onChange={event => setSplitDraft(current => ({ ...current, typeB: event.target.value as Candidate["type"] }))}>
                    <option value="requirement">需求</option><option value="bug">BUG</option>
                  </select></label>
                  <label>标题<input value={splitDraft.titleB} maxLength={60} placeholder="第二个独立诉求" onChange={event => setSplitDraft(current => ({ ...current, titleB: event.target.value }))} /></label>
                  <label>描述<textarea value={splitDraft.descriptionB} maxLength={10000} placeholder="补充第二个条目的描述" onChange={event => setSplitDraft(current => ({ ...current, descriptionB: event.target.value }))} /></label>
                </section>
              </div>
              <div className="capture-field-actions"><button type="button" onClick={() => setCandidatePanel(null)}>取消</button><button className="capture-primary" type="button" onClick={() => splitCandidate(candidate, splitDraft.titleA.trim(), splitDraft.titleB.trim(), splitDraft.descriptionA.trim(), splitDraft.descriptionB.trim(), splitDraft.typeA, splitDraft.typeB)} disabled={!splitDraft.titleA.trim() || !splitDraft.titleB.trim() || !splitDraft.descriptionA.trim() || !splitDraft.descriptionB.trim()}>确认拆分</button></div>
            </div>}
            {candidatePanel?.type === "delete" && candidatePanel.candidateId === candidate.id && <div className="capture-fieldpanel capture-delete-panel" data-testid="capture-delete-panel">
              <p>仅从当前候选草稿中删除这条内容，不会删除共享来源材料，也不会影响已正式创建的记录。</p>
              <div className="capture-field-actions"><button type="button" onClick={() => setCandidatePanel(null)}>取消</button><button type="button" className="capture-danger" onClick={() => deleteCandidate(candidate)}><Trash2 size={15} /> 删除候选</button></div>
            </div>}
          </div>
        </article>;
      }) : <div className="capture-empty">暂无候选，可返回输入态重新整理。</div>}
    </div>
    {error && <p className="capture-alert" role="alert">{error}</p>}
  </div>;

  const resultLinks = task?.issue_links || [];
  const resultView = <div className="capture-result" data-testid="capture-result-body">
    <div className="capture-result-hero">
      {state === "confirming" && <Loader2 className="capture-spin" size={30} aria-hidden="true" />}
      <h2>{task?.state === "completed" ? `已生成 ${resultLinks.length} 条采集记录` : state === "confirming" ? "正在创建这批记录" : "创建中断，可重试原任务"}</h2>
      <p className="capture-muted">已按最终类型分配编号，注册表与索引已同步。</p>
    </div>
    <div className="capture-result-list">
      {resultLinks.map(link => {
        const candidate = candidates.find(item => item.id === link.candidate_id);
        const kind = issueKind(link.issue_id);
        return <article className="capture-resultcard" key={`${link.issue_id}-${link.candidate_id}`} data-testid="capture-result-card">
          <span className={`capture-result-badge ${kind}`}>{link.issue_id}</span>
          <div className="capture-result-detail">
            <strong>{candidate?.title || link.issue_id}</strong>
            <p>目录 <code>{issueDirectory(link.issue_id)}</code></p>
            <p>文件 <code>capture.md</code> · <code>trace.md</code></p>
            <p>来源 {sourceSummary(candidate)}</p>
          </div>
        </article>;
      })}
    </div>
    <div className="capture-idempotent">
      <p><strong>幂等保护：</strong>本次确认已绑定候选版本，编号仅分配一次。重复点击「确认创建」或失败重试都会返回同一批记录，不会重复创建。</p>
      <p><strong>产物边界：</strong>这一步只生成采集记录（capture.md / trace.md），正式的 requirement.md / bug.md 留到后续生成阶段。</p>
    </div>
    {error && <p className="capture-alert" role="alert">{error}</p>}
  </div>;

  const actions = state === "input" ? null : state === "review" ? <>
    <button type="button" onClick={() => setState("input")} disabled={busy}>返回编辑材料</button>
    <button type="button" className="capture-primary" onClick={confirm} disabled={!createCandidates.length || busy || saveState === "failed" || saveState === "conflict"}>确认创建 {createCandidates.length} 条</button>
  </> : <>
    {task && task.state !== "completed" && <button type="button" className="capture-primary" onClick={retry} disabled={state === "confirming"}>重试原任务</button>}
    {task?.state === "completed" && <button type="button" className="capture-primary" onClick={onClose}>完成</button>}
  </>;

  return <div className="rc-settings-mask rc-capture-mask" role="presentation" onMouseDown={onClose}>
    <div className="capture-dialog-shell" role="dialog" aria-modal="true" aria-label="新建 Capture" onMouseDown={event => event.stopPropagation()}>
      <CaptureWorkspace step={step} materials={null} saveState={saveState} onClose={onClose} actions={actions}>
        {state === "loading" ? <div className="capture-empty"><Loader2 className="capture-spin" aria-hidden="true" /> 正在恢复 Capture 草稿…</div>
          : state === "organizing" ? <div className="capture-empty"><Loader2 className="capture-spin" aria-hidden="true" /> AI 正在整理候选…<p className="capture-muted">{organizeTask?.state || capabilities?.organize_reason}</p></div>
          : state === "input" ? inputView : state === "review" ? reviewView : resultView}
      </CaptureWorkspace>
      <CaptureModalView modal={modal} text={content.text || ""} onClose={() => setModal({ type: "none" })} onDeleteDraft={deleteDraft}
        onDelete={deleteCandidate} onSplit={splitCandidate} onSave={updateCandidate} onConfirm={confirm} />
    </div>
  </div>;
}

function CaptureModalView({ modal, text, onClose, onDeleteDraft, onDelete, onSplit, onSave, onConfirm }: {
  modal: CaptureModal;
  text: string;
  onClose: () => void;
  onDeleteDraft: () => void;
  onDelete: (candidate: Candidate) => void;
  onSplit: (candidate: Candidate, a: string, b: string) => void;
  onSave: (id: string | null | undefined, candidate: Candidate) => void;
  onConfirm: () => void;
}) {
  const [draft, setDraft] = useState<Candidate | null>(null);
  const [splitA, setSplitA] = useState("");
  const [splitB, setSplitB] = useState("");

  useEffect(() => {
    if (modal.type === "edit") setDraft(modal.candidate);
    if (modal.type === "split") {
      setSplitA(modal.candidate.title);
      setSplitB("");
    }
  }, [modal]);

  if (modal.type === "none") return null;
  const title = modal.type === "edit" ? "编辑候选" : modal.type === "split" ? "拆分候选" : modal.type === "source" ? "来源依据" : modal.type === "confirm" ? "确认创建这批记录" : modal.type === "delete-draft" ? "删除当前草稿？" : "删除这条候选？";
  return <div className="capture-modal-backdrop" role="presentation" onMouseDown={onClose}>
    <section className="capture-modal" role="dialog" aria-modal="true" aria-label={title} onMouseDown={event => event.stopPropagation()}>
      <header><h2>{title}</h2><button type="button" aria-label="关闭" onClick={onClose}><X size={16} /></button></header>
      {modal.type === "edit" && draft && <div className="capture-modal-body">
        <div className="capture-edit-grid">
          <label>类型<select value={draft.type} onChange={event => setDraft(normalizeCandidate({ ...draft, type: event.target.value as Candidate["type"] }))}>
            <option value="requirement">需求</option><option value="bug">缺陷</option>
          </select></label>
          <label>{draft.type === "bug" ? "缺陷严重度" : "需求优先级"}<select value={(draft.type === "bug" ? draft.severity : draft.priority) || ""} onChange={event => setDraft(normalizeCandidate({ ...draft, ...(draft.type === "bug" ? { severity: event.target.value as Candidate["severity"] } : { priority: event.target.value as Candidate["priority"] }) }))}>
            {(draft.type === "bug" ? severityLevels : priorityLevels).map(level => <option key={level} value={level}>{level}</option>)}
          </select></label>
        </div>
        <label>标题<input value={draft.title} maxLength={60} onChange={event => setDraft({ ...draft, title: event.target.value })} /></label>
        <label>描述<textarea value={draft.description} maxLength={10000} onChange={event => setDraft({ ...draft, description: event.target.value })} /></label>
      </div>}
      {modal.type === "split" && <div className="capture-modal-body">
        <label><Split size={15} aria-hidden="true" /> 条目 A<input value={splitA} maxLength={60} onChange={event => setSplitA(event.target.value)} /></label>
        <label>条目 B<input value={splitB} maxLength={60} placeholder="第二个独立诉求" onChange={event => setSplitB(event.target.value)} /></label>
      </div>}
      {modal.type === "source" && <div className="capture-modal-body">
        <p>{modal.candidate.classification_reason || "来源依据来自原始材料与模型整理结果。"}</p>
        <pre>{text}</pre>
      </div>}
      {modal.type === "delete" && <p>仅从当前确认集合移除，其他条目的来源材料不受影响。</p>}
      {modal.type === "delete-draft" && <p>草稿和未确认候选会被删除，已正式创建的采集记录不受影响。</p>}
      {modal.type === "confirm" && <p>系统会冻结当前候选版本，并按最终类型分配 REQ/BUG 编号。</p>}
      <footer>
        <button type="button" onClick={onClose}>取消</button>
        {modal.type === "edit" && draft && <button className="capture-primary" type="button" onClick={() => { onSave(draft.id, draft); onClose(); }} disabled={!draft.title.trim() || !draft.description.trim()}>保存调整</button>}
        {modal.type === "split" && <button className="capture-primary" type="button" onClick={() => onSplit(modal.candidate, splitA.trim(), splitB.trim())} disabled={!splitA.trim() || !splitB.trim()}>确认拆分</button>}
        {modal.type === "delete" && <button className="capture-danger" type="button" onClick={() => onDelete(modal.candidate)}><Trash2 size={15} /> 删除候选</button>}
        {modal.type === "delete-draft" && <button className="capture-danger" type="button" onClick={onDeleteDraft}><Trash2 size={15} /> 删除草稿</button>}
        {modal.type === "confirm" && <button className="capture-primary" type="button" onClick={onConfirm}>确认创建</button>}
      </footer>
    </section>
  </div>;
}
