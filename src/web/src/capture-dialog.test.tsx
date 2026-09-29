import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CaptureDialog } from "./components/requirement-center/capture/CaptureDialog";
import type { Project } from "./components/workbench/governanceApi";

const apiState = vi.hoisted(() => ({
  revision: 1,
  content: { text: "", media_ids: [] as string[], candidates: [] as Array<Record<string, unknown>> },
  onCreated: vi.fn(),
  saveDelayMs: 0,
  organizeRevision: 0,
}));

vi.mock("./components/requirement-center/capture/captureApi", () => ({
  captureApi: vi.fn(() => ({
    capabilities: vi.fn(async () => ({
      limits: {
        max_images: 10, max_image_bytes: 10485760, max_total_image_bytes: 52428800, max_pixels: 20000000,
        max_text_codepoints: 20000, max_candidates: 50, max_title_codepoints: 60, max_description_codepoints: 10000,
        max_drafts: 50, max_material_bytes: 1073741824, image_types: ["image/png", "image/jpeg", "image/webp"],
      },
      organize_ready: true, organize_reason: "ready", write_ready: true, write_reason: "ready",
    })),
    list: vi.fn(async () => ({ items: [], total: 0, page: 1, page_size: 20 })),
    create: vi.fn(async () => ({ id: "draft-1", revision: apiState.revision, state: "editing", content: apiState.content, updated_at: "2026-09-15T00:00:00Z" })),
    save: vi.fn(async (_id: string, _version: number, content: typeof apiState.content) => {
      if (apiState.saveDelayMs) await new Promise(resolve => setTimeout(resolve, apiState.saveDelayMs));
      apiState.revision += 1;
      apiState.content = {
        ...content,
        candidates: (content.candidates || []).map((candidate, index) => ({ id: String(candidate.id || `candidate-${index + 1}`), ...candidate })),
      };
      return { id: "draft-1", revision: apiState.revision, state: "editing", content: apiState.content, updated_at: "2026-09-15T00:00:01Z" };
    }),
    remove: vi.fn(async () => ({ id: "draft-1", state: "deleted", cleanup: "queued" })),
    upload: vi.fn(async () => ({ media_id: "media-1", mime_type: "image/png", size: 10, width: 1, height: 1, state: "ready", preview_url: "/preview/media-1" })),
    image: vi.fn(async () => new Blob(["png"], { type: "image/png" })),
    organize: vi.fn(async (_id: string, revision: number) => {
      apiState.organizeRevision = revision;
      return { id: "organize-1", revision: apiState.revision, state: "ready", error_code: null, result: {
        rules_version: "capture-organize-v1",
        candidates: [{ type: "requirement", title: "支持统一材料编辑器", description: "用户在一个 MD 编辑器中输入文字、图片和文本文件。", priority: "P1", severity: null, source_refs: ["text"], classification_reason: "新增输入能力，属于需求。" }],
      } };
    }),
    organized: vi.fn(),
    confirm: vi.fn(async () => ({ id: "task-1", revision: apiState.revision, state: "completed", phase: "applied", issue_links: [{ candidate_id: "candidate-1", issue_id: "REQ-0042-unified-capture-editor" }] })),
    status: vi.fn(),
    retry: vi.fn(),
    source: vi.fn(),
  })),
}));

const project: Project = { space_id: "space", repository_id: "repo", status: "connected", readonly: false };

afterEach(() => {
  cleanup();
  apiState.revision = 1;
  apiState.content = { text: "", media_ids: [], candidates: [] };
  apiState.onCreated.mockReset();
  apiState.saveDelayMs = 0;
  apiState.organizeRevision = 0;
});

describe("CaptureDialog", () => {
  it("uses one markdown editor for raw text and text file material", async () => {
    render(<CaptureDialog project={project} contextFailure={false} onClose={vi.fn()} onCreated={apiState.onCreated} />);

    const editor = await screen.findByLabelText("原始材料");
    expect(screen.queryByText("写下需求或问题")).toBeNull();
    expect(screen.queryByText(/附上截图/)).toBeNull();
    expect(screen.queryByLabelText("Capture 标题")).toBeNull();
    expect(screen.queryByRole("group", { name: "Capture 类型" })).toBeNull();
    expect(screen.queryByText("确认前仅保存草稿")).toBeNull();
    expect(screen.queryByText(/\d+\/20000/)).toBeNull();
    expect(screen.queryByText("原始材料")).toBeNull();
    expect(editor.getAttribute("placeholder")).toContain("写下需求、问题或补充背景");

    expect(screen.queryByTestId("capture-md-text-card")).toBeNull();
    expect(screen.getByText("来源材料 · 0 项")).toBeTruthy();

    fireEvent.change(editor, { target: { value: "1. xxx问题\n2. xxx需求" } });
    expect(screen.queryByTestId("capture-md-text-card")).toBeNull();
    expect(screen.getByText("来源材料 · 0 项")).toBeTruthy();

    const file = new File(["文件里的补充背景"], "notes.md", { type: "text/markdown" });
    fireEvent.change(screen.getByTestId("capture-file-input"), { target: { files: [file] } });

    await waitFor(() => expect((editor as HTMLTextAreaElement).value).toContain("来源文件：notes.md"));
    expect((editor as HTMLTextAreaElement).value).toContain("文件里的补充背景");
    expect(screen.getByTestId("capture-text-file-card").textContent).toContain("notes.md");
    expect(screen.getByText("来源材料 · 1 项")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "移除文本文件 notes.md" }));
    await waitFor(() => expect((editor as HTMLTextAreaElement).value).not.toContain("来源文件：notes.md"));
    expect((editor as HTMLTextAreaElement).value).not.toContain("文件里的补充背景");
    expect((editor as HTMLTextAreaElement).value).toContain("1. xxx问题");
    expect(screen.getByText("来源材料 · 0 项")).toBeTruthy();
  });


  it("waits for pending draft saves before organizing", async () => {
    apiState.saveDelayMs = 25;
    render(<CaptureDialog project={project} contextFailure={false} onClose={vi.fn()} onCreated={apiState.onCreated} />);

    const editor = await screen.findByLabelText("原始材料");
    fireEvent.change(editor, { target: { value: "第一段材料" } });
    fireEvent.change(editor, { target: { value: "第一段材料\n第二段材料" } });
    fireEvent.click(screen.getByRole("button", { name: "AI 整理候选" }));

    const review = await screen.findByTestId("capture-review-list");
    expect(within(review).queryByText("可能相关")).toBeNull();
    expect(within(review).queryByText("未发现高相似的现有 REQ/BUG，可继续创建。")).toBeNull();
    expect(apiState.organizeRevision).toBe(apiState.revision - 1);
    expect(apiState.content.text).toContain("第二段材料");
  });


  it("keeps in-flight capture requests alive when parent refreshes the same project", async () => {
    const { rerender } = render(<CaptureDialog project={{ ...project }} contextFailure={false} onClose={vi.fn()} onCreated={apiState.onCreated} />);

    fireEvent.change(await screen.findByLabelText("原始材料"), { target: { value: "父页面刷新项目对象时不要取消整理请求。" } });
    rerender(<CaptureDialog project={{ ...project }} contextFailure={false} onClose={vi.fn()} onCreated={apiState.onCreated} />);
    fireEvent.click(screen.getByRole("button", { name: "AI 整理候选" }));

    expect(await screen.findByTestId("capture-review-list")).toBeTruthy();
  });

  it("keeps candidates unnumbered until final confirmation", async () => {
    render(<CaptureDialog
      project={project}
      contextFailure={false}
      existingIssues={[{
        id: "REQ-0029-capture-multimodal-candidate-review",
        title: "支持统一材料编辑器",
        type: "requirement",
        stage: "验收中",
        source: "trace",
        documents: ["capture.md", "trace.md"],
      }]}
      onClose={vi.fn()}
      onCreated={apiState.onCreated}
    />);

    fireEvent.change(await screen.findByLabelText("原始材料"), { target: { value: "希望 Capture 输入支持图片和文本文件。" } });
    fireEvent.click(screen.getByRole("button", { name: "AI 整理候选" }));

    const review = await screen.findByTestId("capture-review-list");
    expect(within(review).queryByText("AI 审阅结果")).toBeNull();
    expect(within(review).getByText("1 条候选 · 1 条待创建需求 / 0 条待创建缺陷")).toBeTruthy();
    const candidate = within(review).getByTestId("capture-candidate");
    const checkbox = within(candidate).getByRole("checkbox", { name: "选择条目 1" });
    expect(checkbox.closest("label")?.className).toContain("capture-candidate-title");
    expect(checkbox.closest("label")?.textContent).toContain("支持统一材料编辑器");
    expect(within(review).getByText("需求")).toBeTruthy();
    expect(within(review).getByText("P1")).toBeTruthy();
    expect(within(review).getAllByText("支持统一材料编辑器").length).toBeGreaterThan(0);
    expect(within(review).queryByText("REQ-0042-unified-capture-editor")).toBeNull();
    expect(within(review).queryByText(/BUG-\d+/)).toBeNull();
    expect(within(review).queryByText(/这些仍是候选/)).toBeNull();
    expect(within(candidate).getByText("来源依据")).toBeTruthy();
    expect(within(candidate).getByText("新增输入能力，属于需求。")).toBeTruthy();
    expect(within(candidate).getByText("可能相关")).toBeTruthy();
    expect(within(candidate).getByText("REQ-0029-capture-multimodal-candidate-review")).toBeTruthy();
    expect(within(candidate).queryByRole("button", { name: "继续创建新记录" })).toBeNull();
    fireEvent.click(within(candidate).getByRole("button", { name: "补充材料" }));
    expect(within(candidate).getByText("作为 REQ-0029-capture-multimodal-candidate-review 的补充材料")).toBeTruthy();
    expect(within(review).getByText("1 条候选 · 0 条待创建需求 / 0 条待创建缺陷 · 1 条已标记为已有项")).toBeTruthy();
    expect((screen.getByRole("button", { name: "确认创建 0 条" }) as HTMLButtonElement).disabled).toBe(true);
    expect(within(candidate).queryByRole("button", { name: "继续创建新记录" })).toBeNull();
    fireEvent.click(within(candidate).getByRole("button", { name: "恢复创建" }));
    expect(within(review).getByText("1 条候选 · 1 条待创建需求 / 0 条待创建缺陷")).toBeTruthy();
    const actions = within(candidate).getByText("编辑").closest("div");
    expect(within(review).queryByText("编辑 / 改类型")).toBeNull();
    fireEvent.click(within(review).getByRole("button", { name: /^编辑$/ }));
    const editPanel = within(candidate).getByTestId("capture-inline-edit");
    expect(editPanel.compareDocumentPosition(actions as Node) & Node.DOCUMENT_POSITION_PRECEDING).toBeTruthy();
    fireEvent.click(within(editPanel).getByRole("button", { name: "取消" }));
    fireEvent.click(within(review).getByRole("button", { name: /拆分/ }));
    const splitPanel = within(candidate).getByTestId("capture-split-panel");
    expect(splitPanel.compareDocumentPosition(actions as Node) & Node.DOCUMENT_POSITION_PRECEDING).toBeTruthy();
    expect(within(splitPanel).getByRole("region", { name: "拆分条目 A" })).toBeTruthy();
    expect(within(splitPanel).getByRole("region", { name: "拆分条目 B" })).toBeTruthy();
    expect(within(splitPanel).getAllByText("类目")).toHaveLength(2);
    expect(within(splitPanel).getAllByText("标题")).toHaveLength(2);
    expect(within(splitPanel).getAllByText("描述")).toHaveLength(2);
    fireEvent.click(within(splitPanel).getByRole("button", { name: "取消" }));
    expect(within(candidate).queryByTestId("capture-split-panel")).toBeNull();
    expect(within(review).getByRole("button", { name: "删除" }).className).toContain(
      "capture-danger-action",
    );
    fireEvent.click(within(review).getByRole("button", { name: "删除" }));
    const deletePanel = within(candidate).getByTestId("capture-delete-panel");
    expect(deletePanel.compareDocumentPosition(actions as Node) & Node.DOCUMENT_POSITION_PRECEDING).toBeTruthy();
    fireEvent.click(within(deletePanel).getByRole("button", { name: "取消" }));
    expect(screen.queryByRole("dialog", { name: "确认创建这批记录" })).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "确认创建 1 条" }));

    const result = await screen.findByTestId("capture-result-body");
    expect(within(result).getByText("已生成 1 条采集记录")).toBeTruthy();
    expect(result.querySelector(".capture-doneicon")).toBeNull();
    expect(within(result).getByText("已按最终类型分配编号，注册表与索引已同步。")).toBeTruthy();
    expect(within(result).getByTestId("capture-result-card")).toBeTruthy();
    expect(within(result).getByText("REQ-0042-unified-capture-editor")).toBeTruthy();
    expect(within(result).getByText("支持统一材料编辑器")).toBeTruthy();
    expect(within(result).getByText("/issues/REQ-0042/")).toBeTruthy();
    expect(within(result).getByText("capture.md")).toBeTruthy();
    expect(within(result).getByText("trace.md")).toBeTruthy();
    expect(within(result).queryByText("candidate-1")).toBeNull();
    expect(within(result).getByText(/幂等保护/)).toBeTruthy();
    expect(within(result).getByText(/产物边界/)).toBeTruthy();
    await waitFor(() => expect(apiState.onCreated).toHaveBeenCalledOnce());
  });
});
