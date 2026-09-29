import { afterEach, describe, expect, it, vi } from 'vitest';
import { captureApi } from './components/requirement-center/capture/captureApi';
vi.mock('./components/workbench/workbenchAccount', () => ({ readAccessToken: () => 'synthetic-test-token' }));
const project = { space_id: 'space-one', repository_id: 'repo-one', status: 'connected' as const, readonly: false };
afterEach(() => vi.unstubAllGlobals());
const reply = (data: unknown, status = 200) => new Response(JSON.stringify({ data, message: status === 409 ? '版本冲突' : '' }), { status, headers: { 'content-type': 'application/json', 'X-Request-ID': 'trusted-request' } });
describe('Capture scoped requests', () => {
  it('keeps explicit scope, cancellation and action identity on writes', async () => {
    const fetch = vi.fn().mockResolvedValue(reply({ id: 'draft', revision: 2 }));vi.stubGlobal('fetch', fetch);
    const signal = new AbortController().signal;
    await captureApi(project, signal).save('draft', 1, { text: '合成材料', media_ids: [], candidates: [] });
    const [url, options] = fetch.mock.calls[0];
    expect(url).toContain('space_id=space-one');expect(url).toContain('repository_id=repo-one');expect(options.signal).toBe(signal);
    const headers = new Headers(options.headers);
    expect(headers.get('Authorization')).toBe('Bearer synthetic-test-token');expect(headers.get('X-Behavior-Event-ID')).toBeTruthy();
    expect(JSON.parse(options.body).expected_revision).toBe(1);
  });
  it('does not retry a conflict against an unscoped endpoint', async () => {
    const fetch = vi.fn().mockResolvedValue(reply(null, 409));vi.stubGlobal('fetch', fetch);
    await expect(captureApi(project, new AbortController().signal).get('draft')).rejects.toMatchObject({ status: 409, requestId: 'trusted-request' });
    expect(fetch).toHaveBeenCalledTimes(1);
  });
  it('uploads multipart and reads private images with authorization', async () => {
    const fetch = vi.fn().mockResolvedValueOnce(reply({ media_id: 'image' })).mockResolvedValueOnce(new Response('synthetic', { headers: { 'content-type': 'image/png' } }));
    vi.stubGlobal('fetch', fetch);const api = captureApi(project, new AbortController().signal);
    await api.upload('draft', new File(['synthetic'], 'image.png', { type: 'image/png' }));
    expect(fetch.mock.calls[0][1].body).toBeInstanceOf(FormData);
    expect(new Headers(fetch.mock.calls[0][1].headers).get('content-type')).toBeNull();
    expect(await (await api.image('image')).text()).toBe('synthetic');
    expect(new Headers(fetch.mock.calls[1][1].headers).get('Authorization')).toBe('Bearer synthetic-test-token');
    expect(new Headers(fetch.mock.calls[1][1].headers).get('X-Behavior-Event-ID')).toBeNull();
  });
});
