import { beforeEach, expect, it, vi } from 'vitest';
import { sharedChatRead } from './sharedChatRead';
let token = 'a';
vi.mock('../../pages/home/frontendSession', () => ({ readValidFrontendSession: () => ({access_token: token}) }));
beforeEach(() => { token += 'x'; });
it('shares a request while cancelling only the departing subscriber', async () => {
 let finish!: (v: number) => void;
 const load = vi.fn(() => new Promise<number>(r => { finish = r; }));
 const a = new AbortController(), b = new AbortController();
 const first = sharedChatRead('turn', load, a.signal);
 const failed = expect(first).rejects.toMatchObject({name:'AbortError'});
 const second = sharedChatRead('turn', load, b.signal);
 await Promise.resolve(); a.abort(); finish(7);
 await failed; expect(await second).toBe(7); expect(load).toHaveBeenCalledTimes(1);
});
it('does not reuse a completed authorization decision', async () => {
 const load = vi.fn(async () => 3);
 await sharedChatRead('turn', load); await sharedChatRead('turn', load);
 expect(load).toHaveBeenCalledTimes(2);
});
it('rejects an old identity result even when transport ignores abort', async () => {
 let finish!: (v: number) => void;
 const old = sharedChatRead('turn', () => new Promise<number>(r => {finish=r;}));
 const failed = expect(old).rejects.toMatchObject({name:'AbortError'});
 await Promise.resolve(); token='new-user';
 expect(await sharedChatRead('turn', async () => 9)).toBe(9);
 finish(1); await failed;
});

it('rejects every subscriber after logout even without a subsequent read', async () => {
 let finish!: (v: number) => void;
 const first=sharedChatRead('logout',()=>new Promise<number>(r=>{finish=r;}));
 const second=sharedChatRead('logout',async()=>99);
 const a=expect(first).rejects.toMatchObject({name:'AbortError'});
 const b=expect(second).rejects.toMatchObject({name:'AbortError'});
 await Promise.resolve();token='logged-out';finish(1);await a;await b;
});
