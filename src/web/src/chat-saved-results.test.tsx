import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, expect, it, vi } from "vitest";
import { SavedResults } from "./components/chat/SavedResults";

afterEach(() => { cleanup(); vi.unstubAllGlobals(); localStorage.clear(); });
it("keeps four pages, separates final output, and retains saved pages after a read failure", async () => {
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic" }));
  let sequence = 0, fail = false;
  vi.stubGlobal("fetch", vi.fn(async () => {
    if (fail) throw new Error("Failed to fetch");
    sequence++;
    return new Response(JSON.stringify({ code: 0, data: { items: [{ sequence, text: `saved-${sequence}` }], next_cursor: `cursor-${sequence}`, resume_cursor: `cursor-${sequence}`, committed_sequence: sequence, completeness: "unknown_tail", has_final: false } }));
  }));
  render(<SavedResults turnId="one" status="unknown" />);
  fireEvent.click(screen.getByTestId("chat-saved-result"));
  await screen.findByText("saved-1");
  for (let page = 2; page <= 5; page++) {
    fireEvent.click(screen.getByTestId("chat-result-load-more"));
    await screen.findByText(`saved-${page}`);
  }
  expect(screen.queryByText("saved-1")).toBeNull();
  expect(screen.getByText("saved-2")).toBeTruthy();
  fail = true; fireEvent.click(screen.getByTestId("chat-result-load-more"));
  await screen.findByRole("alert"); expect(screen.getByText("saved-5")).toBeTruthy();
  fireEvent.change(screen.getByLabelText("读取内容"), { target: { value: "final" } });
  expect(screen.queryByText("saved-5")).toBeNull();
  fail = false; fireEvent.click(screen.getByTestId("chat-saved-result"));
  await screen.findByText("saved-6");
  const calls = vi.mocked(fetch).mock.calls;
  expect(String(calls[calls.length - 1]?.[0])).toContain("stream_id=final");
});
