import { act, cleanup, fireEvent, render, renderHook, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { useChatWorkbench } from "./components/chat/useChatWorkbench";
import { chatRequest, listSessions } from "./components/chat/chatApi";
import { Composer } from "./components/chat/Composer";

vi.mock("./components/chat/chatApi", async importOriginal => ({
  ...await importOriginal<typeof import("./components/chat/chatApi")>(),
  chatRequest: vi.fn(), listSessions: vi.fn(),
}));
afterEach(() => { cleanup(); vi.useRealTimers(); vi.resetAllMocks(); window.history.replaceState(null, "", "/"); });

it("automatically recovers capabilities without clearing the selected conversation or history", async () => {
  vi.useFakeTimers();
  let ready = false;
  vi.mocked(listSessions).mockResolvedValue({ items: [], total: 0 } as never);
  vi.mocked(chatRequest).mockImplementation(async path => {
    if (path === "/spaces") return [{ id: "space", name: "Space" }] as never;
    if (path.startsWith("/capabilities")) return { execution_ready: ready, reason: "worker unavailable", repositories: [] } as never;
    return { items: [{ id: "turn", status: "completed" }] } as never;
  });
  const { result, unmount } = renderHook(() => useChatWorkbench());
  await act(async () => {});
  expect(result.current.capabilities?.execution_ready).toBe(false);
  await act(async () => { result.current.setSelected({ id: "conversation", space_id: "space" } as never); });
  ready = true;
  await act(async () => { await vi.advanceTimersByTimeAsync(3000); });
  expect(result.current.capabilities?.execution_ready).toBe(true);
  expect(result.current.selected?.id).toBe("conversation");
  expect(result.current.turns[0].id).toBe("turn");
  unmount();
  const calls = vi.mocked(chatRequest).mock.calls.length;
  await vi.advanceTimersByTimeAsync(30000);
  expect(vi.mocked(chatRequest).mock.calls.length).toBe(calls);
});

it("preserves an edited draft across a network failure and automatically enables sending after recovery", async () => {
  vi.useFakeTimers();
  let probes = 0;
  vi.mocked(listSessions).mockResolvedValue({ items: [], total: 0 } as never);
  vi.mocked(chatRequest).mockImplementation(async path => {
    if (path === "/spaces") return [{ id: "space", name: "Space" }] as never;
    if (path.startsWith("/capabilities")) {
      if (++probes === 2) throw new TypeError("Failed to fetch");
      return { execution_ready: probes >= 3, reason: "心跳暂时中断", repositories: [] } as never;
    }
    return { id: "turn" } as never;
  });
  function Harness() {
    const model = useChatWorkbench();
    return <Composer conversation={{ id: "conversation" } as never} capabilities={model.capabilities} initialDraft="草稿" onDraft={() => {}} onSubmitted={() => {}} />;
  }
  render(<Harness />);
  await act(async () => {});
  const input = screen.getByTestId("chat-prompt");
  input.textContent = "/req-complete REQ-0027-requirement-center-command-chain-realization";
  fireEvent.input(input);
  expect((screen.getByTestId("chat-send") as HTMLButtonElement).disabled).toBe(true);
  await act(async () => { await vi.advanceTimersByTimeAsync(3000); });
  expect(input.textContent).toContain("/req-complete");
  expect(screen.queryByText("Failed to fetch")).toBeNull();
  await act(async () => { await vi.advanceTimersByTimeAsync(3000); });
  expect((screen.getByTestId("chat-send") as HTMLButtonElement).disabled).toBe(false);
  expect(input.textContent).toContain("/req-complete");
  await act(async () => { fireEvent.click(screen.getByTestId("chat-send")); });
  const sent = vi.mocked(chatRequest).mock.calls.find(([path, options]) => path.endsWith("/turns") && options?.method === "POST");
  expect(JSON.parse(String(sent?.[1]?.body)).prompt).toContain("/req-complete REQ-0027");
});
