const { chromium, expect } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');
(async () => {
  const browser = await chromium.launch();
  const out = path.resolve('../../logs/chat-live-output-width');
  fs.mkdirSync(out, { recursive: true });
  const samples = [];
  try {
    for (const width of [1440, 1920, 390]) {
      const page = await browser.newPage({ viewport: { width, height: 1000 } });
      let saved = false;
      const text = '目标目录和需求文档已经同步，接下来补充验收标准与失败恢复矩阵。'.repeat(16);
      const conversation = { id: 'width', space_id: 'space', repository_id: 'repo', title: '真实组件宽度验证', archived: false, active_turn_id: null };
      await page.addInitScript(() => localStorage.setItem('moonbox.session', JSON.stringify({ username: 'synthetic', access_token: 'synthetic' })));
      await page.route('**/api/**', async route => {
        const url = new URL(route.request().url()), endpoint = url.pathname;
        let data = {};
        if (endpoint.endsWith('/events')) return route.fulfill({ contentType: 'text/event-stream', body: Number(url.searchParams.get('after')) ? '' : `id: 1\nevent: execution.output\ndata: ${JSON.stringify({ text })}\n\n` });
        if (endpoint.endsWith('/spaces')) data = [{ id: 'space', name: '验证空间' }];
        else if (endpoint.endsWith('/capabilities')) data = { execution_ready: true, reason: '', repositories: [{ id: 'repo', space_id: 'space' }] };
        else if (endpoint.endsWith('/conversations')) data = { items: [conversation], total: 1 };
        else if (endpoint.endsWith('/conversations/width')) data = conversation;
        else if (endpoint.endsWith('/messages')) data = { items: [{ id: 'user', role: 'user', turn_id: 'turn', content: '/req-complete REQ-0027-example', materials: [], created_at: '2026-09-30T00:00:00Z' }, ...(saved ? [{ id: 'assistant', role: 'assistant', turn_id: 'turn', content: text, materials: [], created_at: '2026-09-30T00:01:00Z' }] : [])] };
        else if (endpoint.endsWith('/turns/turn')) data = { id: 'turn', status: saved ? 'completed' : 'running' };
        else if (endpoint.endsWith('/turns') || endpoint.endsWith('/objects') || endpoint.endsWith('/governance-candidates')) data = { items: [] };
        else if (endpoint.endsWith('/relations')) data = { primary: null, references: [] };
        else if (endpoint.endsWith('/projects')) data = { current_user: { name: 'synthetic' }, workspaces: [], projects: [{ space_id: 'space', repository_id: 'repo', readonly: false, status: 'connected' }] };
        await route.fulfill({ json: { code: 0, data } });
      });
      await page.goto((process.env.CHAT_BASE_URL || 'http://localhost:39002') + '/chat?space_id=space&conversation_id=width');
      for (const phase of ['running', 'saved', 'history']) {
        if (phase === 'saved') saved = true;
        if (phase === 'history') await page.reload();
        const selector = phase === 'running' ? '.turn-assistant p[role="status"]' : '.turn-assistant .chat-markdown';
        await expect(page.locator(selector)).toContainText('目标目录', { timeout: 15000 });
        await expect(page.locator('.turn-assistant .chat-turn-activity')).toHaveCount(1);
        await expect(page.locator('.turn-user .chat-turn-activity')).toHaveCount(0);
        if (phase !== 'running') await expect(page.getByTestId('chat-pending-assistant')).toHaveCount(0);
        const result = await page.evaluate(selector => {
          const widthOf = el => el.getBoundingClientRect().width;
          const body = document.querySelector(selector), col = body.closest('.chat-assistant-col'), block = body.closest('.chat-message-block');
          const history = document.querySelector('.chat-message-history');
          const style = getComputedStyle(history);
          return { history: history.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight), block: widthOf(block), article: widthOf(block.querySelector('article')), col: widthOf(col), body: widthOf(body), activity: widthOf(col.querySelector('.chat-turn-activity')), maxWidth: getComputedStyle(body).maxWidth, user: widthOf(document.querySelector('.chat-message-user')) };
        }, selector);
        for (const [a, b] of [['history','block'], ['block','article'], ['col','body'], ['col','activity']]) if (Math.abs(result[a] - result[b]) > 2) throw Error(`${phase}/${width}: ${a} != ${b}: ${JSON.stringify(result)}`);
        if (width >= 1440 && result.user >= result.block) throw Error('user bubble lost its limit');
        samples.push({ width, phase, ...result });
        await page.screenshot({ path: path.join(out, `${width}-${phase}.png`) });
      }
      await page.close();
    }
    fs.writeFileSync(path.join(out, 'computed-width.json'), JSON.stringify({ mode: 'real-app-components-synthetic-api', samples }, null, 2));
    console.log('9 real-component DOM/computed-width states passed');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
