const { chromium, expect } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');

(async () => {
  const browser = await chromium.launch();
  const out = path.resolve('../../logs/chat-capabilities-recovery');
  fs.mkdirSync(out, { recursive: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    let probes = 0;
    const requests = [], errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const conversation = { id: 'recovery', space_id: 'space', repository_id: 'repo', title: '恢复发送验证', archived: false, pinned: false, active_turn_id: null, write_scope: 'governance_write' };
    await page.addInitScript(() => {
      localStorage.setItem('moonbox.session', JSON.stringify({ username: 'synthetic', access_token: 'synthetic' }));
      localStorage.setItem('moonbox.ui.preferences', JSON.stringify({ theme: 'dark' }));
    });
    await page.route('**/api/**', async route => {
      const req = route.request(), url = new URL(req.url());
      const endpoint = url.pathname;
      let data = {};
      if (endpoint.endsWith('/spaces')) data = [{ id: 'space', name: '验证空间' }];
      else if (endpoint.endsWith('/capabilities')) {
        probes++;
        requests.push({ endpoint, probe: probes });
        if (probes === 2) return route.abort('failed');
        data = { execution_ready: probes >= 3, reason: '执行服务心跳暂时中断，正在自动重试；草稿已保留', reason_code: probes >= 3 ? 'ready' : 'worker_heartbeat_expired', repositories: [{ id: 'repo', space_id: 'space' }] };
      } else if (endpoint.endsWith('/conversations')) data = { items: [conversation], total: 1 };
      else if (endpoint.endsWith('/conversations/recovery')) data = conversation;
      else if (endpoint.endsWith('/messages')) data = { items: [{ id: 'message', role: 'assistant', content: '之前已完成的回复', materials: [], created_at: '2026-09-30T00:00:00Z' }] };
      else if (endpoint.endsWith('/turns') && req.method() === 'POST') {
        requests.push({ endpoint, method: 'POST', prompt: req.postDataJSON().prompt });
        data = { id: 'sent', status: 'queued' };
      } else if (endpoint.endsWith('/turns') || endpoint.endsWith('/objects') || endpoint.endsWith('/governance-candidates')) data = { items: [] };
      else if (endpoint.endsWith('/relations')) data = { primary: null, references: [] };
      else if (endpoint.endsWith('/projects')) data = { current_user: { name: 'synthetic' }, workspaces: [], projects: [{ space_id: 'space', repository_id: 'repo', readonly: false, status: 'connected' }] };
      await route.fulfill({ json: { code: 0, data } });
    });
    await page.goto((process.env.CHAT_BASE_URL || 'http://localhost:39002') + '/chat?space_id=space&conversation_id=recovery');
    await expect(page.getByTestId('chat-title-edit')).toContainText('恢复发送验证');
    const input = page.getByTestId('chat-prompt'), send = page.getByTestId('chat-send');
    const draft = '/req-complete REQ-0027-requirement-center-command-chain-realization';
    await input.fill(draft);
    await expect(send).toBeDisabled();
    await page.screenshot({ path: path.join(out, 'unavailable.png') });
    await expect(send).toBeEnabled({ timeout: 15000 });
    await expect(input).toHaveText(draft);
    await expect(page.getByTestId('chat-conversation')).toContainText('之前已完成的回复');
    await page.screenshot({ path: path.join(out, 'recovered.png') });
    const dom = await send.evaluate(el => ({ disabled: el.disabled, width: getComputedStyle(el).width }));
    await send.click();
    await expect.poll(() => requests.filter(row => row.method === 'POST').length).toBe(1);
    if (requests.find(row => row.method === 'POST').prompt !== draft) throw Error('draft changed');
    if (errors.length) throw Error(errors.join('\n'));
    fs.writeFileSync(path.join(out, 'evidence.json'), JSON.stringify({ mode: 'deployed-web-synthetic-api', probes, requests, dom, draftPreserved: true, historyPreserved: true, errors }, null, 2));
    console.log('DOM/Network recovery passed: draft retained, send enabled, one POST');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
