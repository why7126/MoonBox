import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { RelationsDialog } from "./components/chat/RelationsBar";
let rejectSave = false;
const objects = [{ id: "REQ-9001-synthetic", title: "合成对象一" }, { id: "REQ-9002-synthetic", title: "合成对象二" }];
beforeEach(() => {
  rejectSave = false;
  localStorage.setItem("moonbox.session", JSON.stringify({ access_token: "synthetic-token" }));
  vi.stubGlobal("fetch", vi.fn(async (_url: string, options: RequestInit = {}) => ({ ok: !(rejectSave && options.method === "PUT"), status: rejectSave ? 403 : 200, json: async () => ({ code: rejectSave && options.method === "PUT" ? 2509 : 0, message: "对象权限已变化", data: options.method === "PUT" ? { primary: objects[0], references: [objects[1]] } : { items: objects } }) })));
});
afterEach(() => { cleanup(); vi.unstubAllGlobals(); localStorage.clear(); });
it("saves one primary and references explicitly, preserving draft on permission failure", async () => {
  const save = vi.fn(); render(<RelationsDialog conversationId="c" initial={{ primary: null, references: [] }} onClose={vi.fn()} onSave={save} />);
  await screen.findByText("合成对象二", { selector: "small" });
  fireEvent.change(screen.getByLabelText("主对象"), { target: { value: objects[0].id } });
  expect((screen.getByLabelText(`引用 ${objects[0].id}`) as HTMLInputElement).disabled).toBe(true);
  fireEvent.click(screen.getByLabelText(`引用 ${objects[1].id}`));
  rejectSave = true; fireEvent.click(screen.getByTestId("chat-modal-submit"));
  await screen.findByRole("alert"); expect(save).not.toHaveBeenCalled();
  expect((screen.getByLabelText("主对象") as HTMLSelectElement).value).toBe(objects[0].id);
  rejectSave = false; fireEvent.click(screen.getByTestId("chat-modal-submit"));
  await waitFor(() => expect(save).toHaveBeenCalledOnce());
  const request = vi.mocked(fetch).mock.calls.find(([, options]) => options?.method === "PUT");
  expect(JSON.parse(String(request?.[1]?.body))).toEqual({ primary: objects[0].id, references: [objects[1].id] });
});
it("cancels without persisting the draft", async () => {
  const close = vi.fn(); render(<RelationsDialog conversationId="c" initial={{ primary: null, references: [] }} onClose={close} onSave={vi.fn()} />);
  await screen.findByText("合成对象一", { selector: "small" });
  fireEvent.click(screen.getByLabelText(`引用 ${objects[0].id}`)); fireEvent.click(screen.getByTestId("chat-modal-cancel"));
  expect(close).toHaveBeenCalledOnce(); expect(vi.mocked(fetch).mock.calls.some(([, opts]) => opts?.method === "PUT")).toBe(false);
});
