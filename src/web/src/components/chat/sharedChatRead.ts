import { readValidFrontendSession } from '../../pages/home/frontendSession';
import { chatRequest, type TurnRead } from './chatApi';

type Entry = { controller: AbortController; promise: Promise<unknown>; users: number };
const pending = new Map<string, Entry>();
let identity: string | undefined;
/** Share only in-flight reads. Never reuse an authorization decision from a completed request. */
export function sharedChatRead<T>(key: string, load: (signal: AbortSignal) => Promise<T>, signal?: AbortSignal): Promise<T> {
  const token = readValidFrontendSession()?.access_token;
  if (token !== identity) {
    for (const entry of pending.values()) entry.controller.abort();
    pending.clear(); identity = token;
  }
  if (signal?.aborted) return Promise.reject(new DOMException('Aborted', 'AbortError'));
  let entry = pending.get(key);
  if (!entry) {
    const controller = new AbortController();
    entry = { controller, users: 0, promise: Promise.resolve().then(() => load(controller.signal)) };
    const current = entry;
    pending.set(key, entry);
    const cleanup = () => { if (pending.get(key) === current) pending.delete(key); };
    entry.promise.then(cleanup, cleanup);
  }
  const current = entry;
  current.users++;
  return new Promise<T>((resolve, reject) => {
    let finished = false;
    const release = () => {
      if (finished) return false;
      finished = true; signal?.removeEventListener('abort', abort);
      if (--current.users === 0) {
        current.controller.abort();
        if (pending.get(key) === current) pending.delete(key);
      }
      return true;
    };
    const abort = () => { if (release()) reject(new DOMException('Aborted', 'AbortError')); };
    signal?.addEventListener('abort', abort, { once: true });
    current.promise.then(value => {
      if (release()) {
        if (readValidFrontendSession()?.access_token !== token) reject(new DOMException('Aborted', 'AbortError'));
        else resolve(value as T);
      }
    }, error => { if (release()) reject(error); });
  });
}
export type TurnSummary = TurnRead & { tool_count: number; event_sequence: number; usage: Record<string, number> };
export const readTurnSummary = (id: string, signal?: AbortSignal) => sharedChatRead(
  `summary:${id}`, inner => chatRequest<TurnSummary>(`/turns/${encodeURIComponent(id)}/summary`, { signal: inner }), signal);
